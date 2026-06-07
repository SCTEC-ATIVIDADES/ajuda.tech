"""
Views do app chat.

ChatView        — renderiza a interface de chat
SendMessageView — recebe mensagem do usuário, consulta IA, retorna JSON
RecommendView   — extrai lista de produtos a partir do histórico da conversa
"""

import json
import logging

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

logger = logging.getLogger(__name__)

_MAX_HISTORY_SIZE = 50


class ChatView(TemplateView):
    """Renderiza a página de chat e garante que a sessão exista."""

    template_name = "chat/chat.html"

    def get(self, request, *args, **kwargs):
        # Reinicia a sessão a cada carregamento da página — nova conversa no F5
        request.session.flush()
        return super().get(request, *args, **kwargs)


class SendMessageView(View):
    """
    POST /chat/send/
    Body JSON: {"message": "<texto do usuário>"}
    Resposta:  {"reply": "<resposta da IA>"}
    """

    http_method_names = ["post"]

    def _get_client(self) -> OpenRouterClient:
        return OpenRouterClient()

    def _parse_message_body(self, request) -> tuple[str | None, JsonResponse | None]:
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None, JsonResponse({"error": "Body deve ser JSON válido."}, status=400)

        message = body.get("message", "").strip()
        if not message:
            return None, JsonResponse({"error": "O campo 'message' é obrigatório."}, status=400)

        return message, None

    def post(self, request):
        message, error = self._parse_message_body(request)
        if error:
            return error

        history = request.session.get("chat_history", [])
        history.append({"role": "user", "content": message})

        try:
            reply = self._get_client().chat_completion(history)
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
                    "failed_message": message,
                },
                status=503,
            )
        except RateLimitError as exc:
            logger.warning("Erro ao processar resposta: %s", exc)
            return JsonResponse(
                {
                    "error": "Muitas requisições. Aguarde alguns segundos e tente novamente.",
                    "failed_message": message,
                },
                status=429,
            )
        except InvalidResponseError as exc:
            logger.warning("Erro ao processar resposta: %s", exc)
            return JsonResponse(
                {"error": "Não foi possível processar a resposta.", "failed_message": message},
                status=503,
            )

        history.append({"role": "assistant", "content": reply})
        request.session["chat_history"] = history[-_MAX_HISTORY_SIZE:]

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
        history = request.session.get("chat_history", [])

        try:
            products = self._get_client().get_product_recommendations(history)
        except ServiceUnavailableError as exc:
            logger.warning("OpenRouter indisponível ao gerar recomendações: %s", exc)
            return JsonResponse(
                {"error": "Serviço temporariamente indisponível."}, status=503
            )
        except (AuthenticationError, InvalidResponseError, RateLimitError) as exc:
            logger.error("Erro ao gerar recomendações: %s", exc)
            return JsonResponse({"error": "Não foi possível gerar recomendações."}, status=503)

        return JsonResponse({"products": products})
