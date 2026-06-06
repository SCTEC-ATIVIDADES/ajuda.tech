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

    def post(self, request):
        # 1. Parse e validação do body
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Body deve ser JSON válido."}, status=400)

        message = body.get("message", "").strip()
        if not message:
            return JsonResponse({"error": "O campo 'message' é obrigatório."}, status=400)

        # 2. Recupera histórico da sessão
        history = request.session.get("chat_history", [])

        # 3. Adiciona mensagem do usuário ao histórico (em memória/sessão)
        history.append({"role": "user", "content": message})

        # 4. Chama o serviço de IA
        try:
            client = OpenRouterClient()
            reply = client.chat_completion(history)
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

        # 5. Adiciona resposta do assistente e salva na sessão (limite 50 msgs)
        history.append({"role": "assistant", "content": reply})
        request.session["chat_history"] = history[-50:]

        return JsonResponse({"reply": reply})


class RecommendView(View):
    """
    POST /chat/recommend/
    Usa o histórico da conversa na sessão atual para gerar lista de produtos.
    Resposta: {"products": [...]}
    """

    http_method_names = ["post"]

    def post(self, request):
        # Recupera histórico da conversa da sessão atual
        history = request.session.get("chat_history", [])

        try:
            client = OpenRouterClient()
            products = client.get_product_recommendations(history)
        except ServiceUnavailableError as exc:
            logger.warning("OpenRouter indisponível ao gerar recomendações: %s", exc)
            return JsonResponse(
                {"error": "Serviço temporariamente indisponível."}, status=503
            )
        except (AuthenticationError, InvalidResponseError, RateLimitError) as exc:
            logger.error("Erro ao gerar recomendações: %s", exc)
            return JsonResponse({"error": "Não foi possível gerar recomendações."}, status=503)

        return JsonResponse({"products": products})
