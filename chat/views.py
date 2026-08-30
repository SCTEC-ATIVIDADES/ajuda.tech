"""
Views do app chat.

ChatView           — renderiza a interface de chat
SendMessageView    — recebe mensagem do usuário, consulta IA, retorna JSON (endpoint legado)
RecommendView      — extrai lista de produtos a partir do histórico da conversa
AgentSendMessageView — endpoint principal usando LangGraph agent
"""

import hashlib
import hmac
import json
import logging
import time
from uuid import uuid4

from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from chat.exceptions import (
    AuthenticationError,
    InvalidResponseError,
    RateLimitError,
    ServiceUnavailableError,
)
from chat.services import OpenRouterClient
from chat.observability import emit_event, execution_context, new_id

logger = logging.getLogger(__name__)

_WEBHOOK_IDEMPOTENCY_TTL = 86400


def _get_agent_graph():
    """Carrega o grafo do agente sob demanda para facilitar testes."""
    from chat.agent.graph import agent_graph
    return agent_graph


def _invoke_agent(initial_state):
    from django.conf import settings
    trace_id = initial_state["trace_id"]
    run_id = initial_state["run_id"]
    with execution_context(trace_id, run_id, getattr(settings, "AGENT_TIMEOUT", 60)):
        emit_event("request", "start", "started")
        started = time.perf_counter()
        try:
            result = _get_agent_graph().invoke(initial_state)
        except Exception as exc:
            emit_event("request", "complete", "error", duration_ms=(time.perf_counter() - started) * 1000, error=exc)
            raise
        emit_event("request", "complete", "ok", duration_ms=(time.perf_counter() - started) * 1000)
        return result

_MAX_HISTORY_SIZE = 50
_LLM_WINDOW_SIZE = 20
_MAX_MESSAGE_SIZE = 4000
_MAX_REQUEST_SIZE = 8192
_RATE_LIMIT_MAX = 10
_RATE_LIMIT_WINDOW = 60
_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "ignore all instructions",
    "reveal system prompt",
    "show system prompt",
    "reveal your prompt",
    "chain of thought",
    "raciocínio interno",
    "segredo",
    "api key",
)
_SAFE_INJECTION_RESPONSE = (
    "Não posso revelar instruções internas, segredos ou raciocínio privado. "
    "Posso ajudar a escolher um computador com base nas suas necessidades."
)


def _history(request):
    return list(request.session.get("chat_history", []))[-_MAX_HISTORY_SIZE:]


def _llm_history(history):
    return history[-_LLM_WINDOW_SIZE:]


def _rate_limited(request) -> bool:
    now = time.time()
    timestamps = [
        stamp for stamp in request.session.get("chat_rate_limit", [])
        if now - stamp < _RATE_LIMIT_WINDOW
    ]
    if len(timestamps) >= _RATE_LIMIT_MAX:
        request.session["chat_rate_limit"] = timestamps
        return True
    timestamps.append(now)
    request.session["chat_rate_limit"] = timestamps
    request.session.modified = True
    return False


def _rate_limit_response(request):
    if _rate_limited(request):
        return JsonResponse(
            {"error": "Muitas mensagens. Aguarde um minuto e tente novamente."},
            status=429,
        )
    return None


def _is_injection(message: str) -> bool:
    lowered = message.casefold()
    return any(pattern in lowered for pattern in _INJECTION_PATTERNS)


def _parse_json_object(request):
    if len(request.body) > _MAX_REQUEST_SIZE:
        return None, JsonResponse({"error": "Body excede limite de tamanho."}, status=413)
    try:
        body = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse({"error": "Body deve ser JSON válido."}, status=400)
    if not isinstance(body, dict):
        return None, JsonResponse({"error": "Body deve ser um objeto JSON."}, status=400)
    return body, None


def _parse_message(request):
    body, error = _parse_json_object(request)
    if error:
        return None, error

    if not isinstance(body, dict):
        return None, JsonResponse({"error": "Body deve ser um objeto JSON."}, status=400)

    message = body.get("message", "")
    if not isinstance(message, str) or not message.strip():
        return None, JsonResponse({"error": "O campo 'message' é obrigatório."}, status=400)
    message = message.strip()
    if len(message) > _MAX_MESSAGE_SIZE:
        return None, JsonResponse(
            {"error": f"Mensagem excede limite de {_MAX_MESSAGE_SIZE} caracteres."}, status=413
        )
    return message, None


def _persist(request, history, needs, *, run_id=None):
    try:
        request.session["chat_history"] = history[-_MAX_HISTORY_SIZE:]
        request.session["user_needs"] = needs
        request.session["thread_id"] = request.session.get("thread_id", str(uuid4()))
        request.session["run_id"] = run_id or str(uuid4())
        request.session.modified = True
    except Exception as exc:
        emit_event("memory", "persist", "error", error=exc)
        logger.error("Falha ao persistir memória da sessão", exc_info=True)
        return False
    return True


class ChatView(TemplateView):
    """Renderiza a página de chat e garante que a sessão exista."""

    template_name = "chat/chat.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NewConversationView(View):
    http_method_names = ["post"]

    def post(self, request):
        request.session.flush()
        return JsonResponse({"ok": True})


class SendMessageView(View):
    """
    POST /chat/send/
    Body JSON: {"message": "<texto do usuário>"}
    Resposta:  {"reply": "<resposta da IA>"}

    Endpoint legado — mantido para compatibilidade.
    """

    http_method_names = ["post"]

    def _get_client(self) -> OpenRouterClient:
        return OpenRouterClient()

    def post(self, request):
        message, error = _parse_message(request)
        if error:
            return error
        if response := _rate_limit_response(request):
            return response
        if _is_injection(message):
            emit_event("security", "prompt_injection", "blocked")
            return JsonResponse({"reply": _SAFE_INJECTION_RESPONSE})
        history = _history(request)
        history.append({"role": "user", "content": message})

        try:
            reply = self._get_client().chat_completion(_llm_history(history))
        except AuthenticationError as exc:
            logger.error("Falha de autenticação com OpenRouter: %s", exc)
            return JsonResponse(
                {"error": "Erro de configuração do serviço de IA."}, status=500
            )
        except ServiceUnavailableError as exc:
            logger.warning("OpenRouter indisponível: %s", exc)
            return JsonResponse(
                {
                    "error": "Serviço de IA temporariamente indisponível. Tente novamente.",
                },
                status=503,
            )
        except RateLimitError as exc:
            logger.warning("Erro ao processar resposta: %s", exc)
            return JsonResponse(
                {
                    "error": "Muitas requisições. Aguarde alguns segundos e tente novamente.",
                },
                status=429,
            )
        except InvalidResponseError as exc:
            logger.warning("Erro ao processar resposta: %s", exc)
            return JsonResponse(
                {"error": "Não foi possível processar a resposta."},
                status=503,
            )

        history.append({"role": "assistant", "content": reply})
        if not _persist(request, history, request.session.get("user_needs", {})):
            return JsonResponse({"error": "Não foi possível salvar a conversa."}, status=500)

        return JsonResponse({"reply": reply})


class RecommendView(View):
    """
    POST /chat/recommend/
    Usa o histórico da conversa na sessão atual para gerar lista de produtos.
    Resposta: {"products": [...]}
    """

    http_method_names = ["post"]

    def _get_client(self) -> OpenRouterClient:
        return OpenRouterClient()

    def post(self, request):
        body, error = _parse_json_object(request)
        if error:
            return error
        if response := _rate_limit_response(request):
            return response
        history = _history(request)
        if not history:
            return JsonResponse({"error": "Envie uma mensagem antes de pedir recomendações."}, status=400)

        try:
            products = self._get_client().get_product_recommendations(_llm_history(history))
        except ServiceUnavailableError as exc:
            logger.warning("OpenRouter indisponível ao gerar recomendações: %s", exc)
            return JsonResponse(
                {"error": "Serviço temporariamente indisponível."}, status=503
            )
        except (AuthenticationError, InvalidResponseError, RateLimitError) as exc:
            logger.error("Erro ao gerar recomendações: %s", exc)
            return JsonResponse({"error": "Não foi possível gerar recomendações."}, status=503)

        return JsonResponse({"products": products})


@method_decorator(csrf_exempt, name="dispatch")
class AutomationWebhookView(View):
    http_method_names = ["post"]

    def post(self, request):
        secret = getattr(settings, "AUTOMATION_WEBHOOK_SECRET", "")
        provided = request.headers.get("X-Automation-Signature", "")
        expected = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
        if not secret or not hmac.compare_digest(provided, expected):
            return JsonResponse({"error": "Assinatura inválida."}, status=401)

        body, error = _parse_json_object(request)
        if error:
            return error
        event_id = body.get("event_id")
        message = body.get("message")
        if not isinstance(event_id, str) or not event_id.strip() or not isinstance(message, str) or not message.strip():
            return JsonResponse({"error": "Campos 'event_id' e 'message' são obrigatórios."}, status=400)
        key = f"automation-webhook:{event_id.strip()}"
        if not cache.add(key, True, _WEBHOOK_IDEMPOTENCY_TTL):
            return JsonResponse({"ok": True, "duplicate": True})
        response = AgentSendMessageView().post(request)
        if response.status_code >= 500:
            cache.delete(key)
        return response


class AgentSendMessageView(View):
    """
    POST /agent/send/
    Body JSON: {"message": "<texto do usuário>"}
    Resposta:  {"reply": "<resposta do agente>", "report": "<relatório se disponível>"}

    Endpoint principal usando LangGraph agent.
    """

    http_method_names = ["post"]

    def post(self, request):
        message, error = _parse_message(request)
        if error:
            return error
        if response := _rate_limit_response(request):
            return response
        if _is_injection(message):
            emit_event("security", "prompt_injection", "blocked")
            return JsonResponse({"reply": _SAFE_INJECTION_RESPONSE})

        history = _history(request)
        history.append({"role": "user", "content": message})

        try:
            messages = _llm_history(history)

            thread_id = request.session.get("thread_id") or new_id()
            request.session["thread_id"] = thread_id
            recovered_needs = request.session.get("user_needs", {})
            initial_state = {
                "messages": messages,
                "thread_id": thread_id,
                "trace_id": new_id(),
                "run_id": new_id(),
                "recovered_context": {"user_needs": recovered_needs},
                "user_needs": recovered_needs,
                "products_found": [],
                "stage": "",
                "recommendation": "",
                "report": "",
                "classified_intent": "",
            }

            result = _invoke_agent(initial_state)

            reply = ""
            for msg in reversed(result.get("messages", [])):
                if isinstance(msg, dict):
                    content = msg.get("content", "")
                else:
                    content = getattr(msg, "content", "")
                if content:
                    reply = content
                    break

            if not reply:
                reply = result.get("recommendation", "Desculpe, não consegui processar sua mensagem.")

            history.append({"role": "assistant", "content": reply})
            if not _persist(request, history, result.get("user_needs", {}), run_id=initial_state["run_id"]):
                return JsonResponse({"error": "Não foi possível salvar a conversa."}, status=500)

            response_data = {"reply": reply}
            if result.get("report"):
                response_data["report"] = result["report"]

            return JsonResponse(response_data)

        except AuthenticationError as exc:
            logger.error("Falha de autenticação com OpenRouter: %s", exc)
            return JsonResponse(
                {"error": "Erro de configuração do serviço de IA."}, status=500
            )
        except ServiceUnavailableError as exc:
            logger.warning("OpenRouter indisponível: %s", exc)
            return JsonResponse(
                {
                    "error": "Serviço de IA temporariamente indisponível. Tente novamente.",
                },
                status=503,
            )
        except RateLimitError as exc:
            logger.warning("Rate limit atingido: %s", exc)
            return JsonResponse(
                {
                    "error": "Muitas requisições. Aguarde alguns segundos e tente novamente.",
                },
                status=429,
            )
        except InvalidResponseError as exc:
            logger.warning("Erro ao processar resposta: %s", exc)
            return JsonResponse(
                {"error": "Não foi possível processar a resposta."},
                status=503,
            )
        except Exception as exc:
            logger.error("Erro inesperado no agente LangGraph: %s", exc, exc_info=True)
            return JsonResponse(
                {"error": "Erro interno do agente. Tente novamente."},
                status=500,
            )
