"""Testes para limites de sessão e janela de contexto."""

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


def _clear_rate_limit(django_client):
    session = django_client.session
    session["chat_rate_limit"] = []
    session.save()


# ─── Limite de mensagens por sessão ──────────────────────────────────────────

@pytest.mark.django_db
class TestSessionMessageLimit:
    @patch("chat.views._rate_limit_response", return_value=None)
    @patch("chat.views.OpenRouterClient")
    def test_history_is_truncated_to_50_entries(self, MockClient, _rate_limit, django_client):
        MockClient.return_value.chat_completion.return_value = "resposta"

        for i in range(26):
            _clear_rate_limit(django_client)
            response = _post_message(django_client, f"mensagem {i}")
            assert response.status_code == 200

        history = django_client.session["chat_history"]
        assert len(history) == 50
        assert history[0]["content"] == "mensagem 1"
        assert history[-1]["content"] == "resposta"


# ─── Janela de histórico enviado à LLM ───────────────────────────────────────

@pytest.mark.django_db
class TestHistoryWindowLimit:
    """LLM deve receber no máximo 20 mensagens por chamada (CLAUDE.md: services.py)."""

    @patch("chat.views.OpenRouterClient")
    def test_sends_at_most_20_messages_to_llm(self, MockClient, django_client):
        mock_instance = MockClient.return_value
        mock_instance.chat_completion.return_value = "resposta"

        for i in range(25):
            _clear_rate_limit(django_client)
            _post_message(django_client, f"mensagem {i+1}")

        last_call_history = mock_instance.chat_completion.call_args[0][0]
        assert len(last_call_history) <= 20

    @patch("chat.views._rate_limit_response", return_value=None)
    @patch("chat.views.OpenRouterClient")
    def test_history_window_excludes_oldest_messages(self, MockClient, _rate_limit, django_client):
        mock_instance = MockClient.return_value
        mock_instance.chat_completion.return_value = "resposta"

        for i in range(25):
            _clear_rate_limit(django_client)
            _post_message(django_client, f"mensagem {i+1}")

        last_call_history = mock_instance.chat_completion.call_args[0][0]
        contents = [m["content"] for m in last_call_history]
        assert not any("mensagem 1" == c for c in contents)


# ─── Rate limiting por sessão ─────────────────────────────────────────────────

@pytest.mark.django_db
class TestRateLimiting:
    """No máximo 10 mensagens por minuto por sessão (CLAUDE.md: services.py)."""

    @patch("chat.views.OpenRouterClient")
    def test_rejects_11th_message_within_one_minute(self, MockClient, django_client):
        MockClient.return_value.chat_completion.return_value = "resposta"

        for _ in range(10):
            _post_message(django_client)

        response = _post_message(django_client, "mensagem 11")
        assert response.status_code == 429
        assert MockClient.return_value.chat_completion.call_count == 10

    @patch("chat.views.OpenRouterClient")
    def test_rate_limit_error_body_is_informative(self, MockClient, django_client):
        MockClient.return_value.chat_completion.return_value = "resposta"

        for _ in range(10):
            _post_message(django_client)

        response = _post_message(django_client, "mensagem 11")
        data = response.json()
        assert "error" in data


@pytest.mark.django_db
def test_agent_sends_at_most_20_messages_to_graph(client):
    with patch("chat.views._get_agent_graph") as get_graph, patch(
        "chat.views._rate_limit_response", return_value=None
    ):
        get_graph.return_value.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "resposta"}],
            "user_needs": {},
        }
        for i in range(11):
            session = client.session
            session["chat_rate_limit"] = []
            session.save()
            client.post(
                reverse("chat:agent_send_message"),
                data=json.dumps({"message": f"mensagem {i}"}),
                content_type="application/json",
            )

    messages = get_graph.return_value.invoke.call_args.args[0]["messages"]
    assert len(messages) == 20
    assert messages[0]["content"] == "resposta"
    assert messages[-1]["content"] == "mensagem 10"
