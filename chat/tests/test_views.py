"""
Testes de integração para as views do chat (ChatView, SendMessageView, RecommendView).
Metodologia: TDD — escritos antes da implementação das views.
Refatorado para utilizar Django Sessions em vez de Models (Tarefa #12).
"""

import json
import pytest
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch

from chat.exceptions import AuthenticationError, ServiceUnavailableError


@pytest.fixture
def django_client(client):
    """Cliente Django com sessão ativa."""
    client.get("/")  # inicia sessão
    return client


# ─── TestChatView ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestChatView:
    def test_get_returns_200(self, django_client):
        response = django_client.get(reverse("chat:chat"))
        assert response.status_code == 200

    def test_get_uses_correct_template(self, django_client):
        response = django_client.get(reverse("chat:chat"))
        assert any(t.name == "chat/chat.html" for t in response.templates)

    def test_response_includes_csrf_token(self, django_client):
        response = django_client.get(reverse("chat:chat"))
        content = response.content.decode()
        assert "csrfmiddlewaretoken" in content or "csrf" in content.lower()


# ─── TestSendMessageView ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSendMessageView:
    def _post(self, django_client, payload):
        return django_client.post(
            reverse("chat:send_message"),
            data=json.dumps(payload),
            content_type="application/json",
        )

    @patch("chat.views.OpenRouterClient")
    def test_returns_200_on_success(self, mock_client, django_client):
        mock_client.return_value.chat_completion.return_value = "Ótima escolha!"
        response = self._post(django_client, {"message": "Preciso de um notebook"})
        assert response.status_code == 200

    @patch("chat.views.OpenRouterClient")
    def test_response_is_json(self, mock_client, django_client):
        mock_client.return_value.chat_completion.return_value = "Ok!"
        response = self._post(django_client, {"message": "teste"})
        assert response["Content-Type"] == "application/json"
        data = json.loads(response.content)
        assert isinstance(data, dict)

    @patch("chat.views.OpenRouterClient")
    def test_response_contains_reply_key(self, mock_client, django_client):
        mock_client.return_value.chat_completion.return_value = "Resposta aqui"
        response = self._post(django_client, {"message": "teste"})
        data = json.loads(response.content)
        assert "reply" in data

    @patch("chat.views.OpenRouterClient")
    def test_reply_matches_service_return_value(self, mock_client, django_client):
        expected = "Recomendo um notebook Dell"
        mock_client.return_value.chat_completion.return_value = expected
        response = self._post(django_client, {"message": "teste"})
        data = json.loads(response.content)
        assert data["reply"] == expected

    @patch("chat.views.OpenRouterClient")
    def test_saves_user_message_to_session(self, mock_client, django_client):
        mock_client.return_value.chat_completion.return_value = "ok"
        self._post(django_client, {"message": "mensagem do usuário"})
        history = django_client.session.get("chat_history", [])
        assert any(m["role"] == "user" and m["content"] == "mensagem do usuário" for m in history)

    @patch("chat.views.OpenRouterClient")
    def test_saves_assistant_reply_to_session(self, mock_client, django_client):
        ai_reply = "Resposta da IA salva"
        mock_client.return_value.chat_completion.return_value = ai_reply
        self._post(django_client, {"message": "pergunta"})
        history = django_client.session.get("chat_history", [])
        assert any(m["role"] == "assistant" and m["content"] == ai_reply for m in history)

    def test_returns_400_when_message_is_missing(self, django_client):
        response = self._post(django_client, {})
        assert response.status_code == 400

    def test_returns_400_when_message_is_empty_string(self, django_client):
        response = self._post(django_client, {"message": ""})
        assert response.status_code == 400

    def test_returns_405_for_get_request(self, django_client):
        response = django_client.get(reverse("chat:send_message"))
        assert response.status_code == 405

    @patch("chat.views.OpenRouterClient")
    def test_returns_503_when_service_unavailable(self, mock_client, django_client):
        mock_client.return_value.chat_completion.side_effect = ServiceUnavailableError(
            "serviço indisponível"
        )
        response = self._post(django_client, {"message": "teste"})
        assert response.status_code == 503

    @patch("chat.views.OpenRouterClient")
    def test_returns_500_when_authentication_fails(self, mock_client, django_client):
        mock_client.return_value.chat_completion.side_effect = AuthenticationError(
            "chave inválida"
        )
        response = self._post(django_client, {"message": "teste"})
        assert response.status_code == 500


# ─── TestRecommendView ────────────────────────────────────────────────────────

_SAMPLE_PRODUCTS = [
    {
        "name": "Dell Inspiron",
        "price": "R$ 2.499",
        "type": "Notebook",
        "specs": "i5, 8GB, 256GB SSD",
        "justification": "Custo-benefício",
        "option": "budget",
    },
    {
        "name": "Lenovo IdeaPad",
        "price": "R$ 3.299",
        "type": "Notebook",
        "specs": "i7, 16GB, 512GB SSD",
        "justification": "Equilíbrio",
        "option": "ideal",
    },
    {
        "name": "ASUS ZenBook",
        "price": "R$ 5.999",
        "type": "Notebook",
        "specs": "i9, 32GB, 1TB SSD",
        "justification": "Máximo desempenho",
        "option": "premium",
    },
]


@pytest.mark.django_db
class TestRecommendView:
    def _post(self, django_client, payload):
        return django_client.post(
            reverse("chat:recommend"),
            data=json.dumps(payload),
            content_type="application/json",
        )

    @patch("chat.views.OpenRouterClient")
    def test_returns_200_on_success(self, mock_client, django_client):
        mock_client.return_value.get_product_recommendations.return_value = _SAMPLE_PRODUCTS
        response = self._post(django_client, {})
        assert response.status_code == 200

    @patch("chat.views.OpenRouterClient")
    def test_response_contains_products_key(self, mock_client, django_client):
        mock_client.return_value.get_product_recommendations.return_value = _SAMPLE_PRODUCTS
        response = self._post(django_client, {})
        data = json.loads(response.content)
        assert "products" in data

    @patch("chat.views.OpenRouterClient")
    def test_products_list_has_three_items(self, mock_client, django_client):
        mock_client.return_value.get_product_recommendations.return_value = _SAMPLE_PRODUCTS
        response = self._post(django_client, {})
        data = json.loads(response.content)
        assert len(data["products"]) == 3

    @patch("chat.views.OpenRouterClient")
    def test_returns_200_even_with_empty_history(self, MockClient, django_client):
        MockClient.return_value.get_product_recommendations.return_value = _SAMPLE_PRODUCTS
        response = self._post(django_client, {})
        assert response.status_code == 200

    @patch("chat.views.OpenRouterClient")
    def test_returns_503_when_service_unavailable(self, mock_client, django_client):
        mock_client.return_value.get_product_recommendations.side_effect = (
            ServiceUnavailableError("fora do ar")
        )
        response = self._post(django_client, {})
        assert response.status_code == 503

    def test_returns_405_for_get_request(self, django_client):
        response = django_client.get(reverse("chat:recommend"))
        assert response.status_code == 405
