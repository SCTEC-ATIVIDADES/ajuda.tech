"""
Testes para limites de sessão e rate limiting.

Estes testes cobrem requisitos documentados no CLAUDE.md que ainda NÃO foram
implementados no código. Estão marcados como xfail para que:
  - O CI continue passando (sem regressão)
  - Os requisitos fiquem rastreados como especificações pendentes
  - Ao implementar a feature, basta remover o @pytest.mark.xfail

Requisitos documentados (CLAUDE.md):
  - views.py: limite de 50 mensagens por sessão
  - services.py: janela de histórico de 20 mensagens enviadas à LLM
  - services.py: rate limiting de 10 mensagens por minuto por sessão
"""

import json
import pytest
from django.urls import reverse
from unittest.mock import patch


@pytest.fixture
def django_client(client):
    client.get("/")
    return client


def _post_message(django_client, message="Olá"):
    return django_client.post(
        reverse("chat:send_message"),
        data=json.dumps({"message": message}),
        content_type="application/json",
    )


# ─── Limite de mensagens por sessão ──────────────────────────────────────────

@pytest.mark.django_db
class TestSessionMessageLimit:
    """Sessão deve rejeitar mensagens após atingir 50 trocas (CLAUDE.md: views.py)."""

    @pytest.mark.xfail(reason="limite de 50 msgs/sessão não implementado em views.py")
    @patch("chat.views.OpenRouterClient")
    def test_rejects_message_after_50_exchanges(self, MockClient, django_client):
        MockClient.return_value.chat_completion.return_value = "resposta"

        for _ in range(50):
            _post_message(django_client)

        response = _post_message(django_client, "mensagem 51")
        assert response.status_code == 429

    @pytest.mark.xfail(reason="limite de 50 msgs/sessão não implementado em views.py")
    @patch("chat.views.OpenRouterClient")
    def test_error_message_is_user_friendly_on_limit(self, MockClient, django_client):
        MockClient.return_value.chat_completion.return_value = "resposta"

        for _ in range(50):
            _post_message(django_client)

        response = _post_message(django_client, "mensagem 51")
        data = response.json()
        assert "error" in data
        assert len(data["error"]) > 0

    @patch("chat.views.OpenRouterClient")
    def test_accepts_exactly_50_messages(self, MockClient, django_client):
        # Comportamento positivo já implementado: 50 mensagens devem ser aceitas.
        # Não é xfail — testa o limite superior permitido, não a rejeição.
        MockClient.return_value.chat_completion.return_value = "resposta"

        for i in range(50):
            response = _post_message(django_client, f"mensagem {i+1}")
            assert response.status_code == 200, f"falhou na mensagem {i+1}"


# ─── Janela de histórico enviado à LLM ───────────────────────────────────────

@pytest.mark.django_db
class TestHistoryWindowLimit:
    """LLM deve receber no máximo 20 mensagens por chamada (CLAUDE.md: services.py)."""

    @pytest.mark.xfail(reason="janela de 20 msgs para LLM não implementada em services.py")
    @patch("chat.views.OpenRouterClient")
    def test_sends_at_most_20_messages_to_llm(self, MockClient, django_client):
        mock_instance = MockClient.return_value
        mock_instance.chat_completion.return_value = "resposta"

        for i in range(25):
            _post_message(django_client, f"mensagem {i+1}")

        last_call_history = mock_instance.chat_completion.call_args[0][0]
        assert len(last_call_history) <= 20

    @pytest.mark.xfail(reason="janela de 20 msgs para LLM não implementada em services.py")
    @patch("chat.views.OpenRouterClient")
    def test_history_window_excludes_oldest_messages(self, MockClient, django_client):
        # Com janela de 20: ao enviar 25 mensagens, as primeiras 5 devem ser excluídas.
        # Sem a janela implementada, todas as 25 chegam à LLM — o teste falha (xfail correto).
        mock_instance = MockClient.return_value
        mock_instance.chat_completion.return_value = "resposta"

        for i in range(25):
            _post_message(django_client, f"mensagem {i+1}")

        last_call_history = mock_instance.chat_completion.call_args[0][0]
        contents = [m["content"] for m in last_call_history]
        # A primeira mensagem ("mensagem 1") deve ter sido descartada pela janela
        assert not any("mensagem 1" == c for c in contents)


# ─── Rate limiting por sessão ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestRateLimiting:
    """No máximo 10 mensagens por minuto por sessão (CLAUDE.md: services.py)."""

    @pytest.mark.xfail(reason="rate limiting de 10 msgs/min não implementado")
    @patch("chat.views.OpenRouterClient")
    def test_rejects_11th_message_within_one_minute(self, MockClient, django_client):
        MockClient.return_value.chat_completion.return_value = "resposta"

        for _ in range(10):
            _post_message(django_client)

        response = _post_message(django_client, "mensagem 11")
        assert response.status_code == 429

    @pytest.mark.xfail(reason="rate limiting de 10 msgs/min não implementado")
    @patch("chat.views.OpenRouterClient")
    def test_rate_limit_error_body_is_informative(self, MockClient, django_client):
        MockClient.return_value.chat_completion.return_value = "resposta"

        for _ in range(10):
            _post_message(django_client)

        response = _post_message(django_client, "mensagem 11")
        data = response.json()
        assert "error" in data
