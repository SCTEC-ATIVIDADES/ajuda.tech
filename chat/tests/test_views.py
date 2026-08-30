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

    @patch("chat.views.OpenRouterClient")
    def test_get_preserves_session(self, MockClient, django_client):
        MockClient.return_value.chat_completion.return_value = "ok"
        django_client.post(
            reverse("chat:send_message"),
            data=json.dumps({"message": "continuidade"}),
            content_type="application/json",
        )

        response = django_client.get(reverse("chat:chat"))

        assert response.status_code == 200
        assert django_client.session["chat_history"][0]["content"] == "continuidade"

    def test_get_uses_correct_template(self, django_client):
        response = django_client.get(reverse("chat:chat"))
        assert any(t.name == "chat/chat.html" for t in response.templates)

    def test_response_includes_csrf_token(self, django_client):
        response = django_client.get(reverse("chat:chat"))
        content = response.content.decode()
        assert "csrfmiddlewaretoken" in content or "csrf" in content.lower()


# ─── TestNewConversationView ───────────────────────────────────────────────────

@pytest.mark.django_db
class TestNewConversationView:
    def test_post_clears_session(self, django_client):
        session = django_client.session
        session["chat_history"] = [{"role": "user", "content": "antiga"}]
        session["user_needs"] = {"proposito": "estudos"}
        session.save()

        response = django_client.post(reverse("chat:new_conversation"))

        assert response.status_code == 200
        assert django_client.session.get("chat_history") is None
        assert django_client.session.get("user_needs") is None

    def test_get_is_not_allowed(self, django_client):
        assert django_client.get(reverse("chat:new_conversation")).status_code == 405

    def test_expired_session_starts_without_old_context(self, django_client):
        session = django_client.session
        session["chat_history"] = [{"role": "user", "content": "antiga"}]
        session["user_needs"] = {"proposito": "estudos"}
        session.set_expiry(-1)
        session.save()

        with patch("chat.views._get_agent_graph") as get_graph:
            get_graph.return_value.invoke.return_value = {
                "messages": [{"role": "assistant", "content": "nova conversa"}],
                "user_needs": {},
            }
            response = django_client.post(
                reverse("chat:agent_send_message"),
                data=json.dumps({"message": "começar"}),
                content_type="application/json",
            )

        assert response.status_code == 200
        initial_state = get_graph.return_value.invoke.call_args.args[0]
        assert initial_state["messages"] == [{"role": "user", "content": "começar"}]
        assert initial_state["user_needs"] == {}


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
    def test_returns_200_on_success(self, MockClient, django_client):
        MockClient.return_value.chat_completion.return_value = "Ótima escolha!"
        response = self._post(django_client, {"message": "Preciso de um notebook"})
        assert response.status_code == 200

    @patch("chat.views.OpenRouterClient")
    def test_response_is_json(self, MockClient, django_client):
        MockClient.return_value.chat_completion.return_value = "Ok!"
        response = self._post(django_client, {"message": "teste"})
        assert response["Content-Type"] == "application/json"
        data = json.loads(response.content)
        assert isinstance(data, dict)

    @patch("chat.views.OpenRouterClient")
    def test_response_contains_reply_key(self, MockClient, django_client):
        MockClient.return_value.chat_completion.return_value = "Resposta aqui"
        response = self._post(django_client, {"message": "teste"})
        data = json.loads(response.content)
        assert "reply" in data

    @patch("chat.views.OpenRouterClient")
    def test_reply_matches_service_return_value(self, MockClient, django_client):
        expected = "Recomendo um notebook Dell"
        MockClient.return_value.chat_completion.return_value = expected
        response = self._post(django_client, {"message": "teste"})
        data = json.loads(response.content)
        assert data["reply"] == expected

    @patch("chat.views.OpenRouterClient")
    def test_saves_user_message_to_session(self, MockClient, django_client):
        MockClient.return_value.chat_completion.return_value = "ok"
        self._post(django_client, {"message": "mensagem do usuário"})
        history = django_client.session.get("chat_history", [])
        assert any(m["role"] == "user" and m["content"] == "mensagem do usuário" for m in history)

    @patch("chat.views.OpenRouterClient")
    def test_saves_assistant_reply_to_session(self, MockClient, django_client):
        ai_reply = "Resposta da IA salva"
        MockClient.return_value.chat_completion.return_value = ai_reply
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
    def test_returns_503_when_service_unavailable(self, MockClient, django_client):
        MockClient.return_value.chat_completion.side_effect = ServiceUnavailableError(
            "serviço indisponível"
        )
        response = self._post(django_client, {"message": "teste"})
        assert response.status_code == 503

    @patch("chat.views.OpenRouterClient")
    def test_continues_session_history(self, MockClient, django_client):
        MockClient.return_value.chat_completion.side_effect = ["primeira", "segunda"]

        self._post(django_client, {"message": "contexto"})
        self._post(django_client, {"message": "continua"})

        history = django_client.session["chat_history"]
        assert [item["content"] for item in history] == [
            "contexto", "primeira", "continua", "segunda"
        ]

    def test_rejects_oversized_message(self, django_client):
        response = self._post(django_client, {"message": "x" * 4001})
        assert response.status_code == 413

    def test_rejects_oversized_request_body(self, django_client):
        response = django_client.post(
            reverse("chat:send_message"),
            data=json.dumps({"message": "ok", "padding": "x" * 8200}),
            content_type="application/json",
        )
        assert response.status_code == 413

    @patch("chat.views._persist", return_value=False)
    @patch("chat.views.OpenRouterClient")
    def test_returns_500_when_session_persistence_fails(self, MockClient, _persist, django_client):
        MockClient.return_value.chat_completion.return_value = "resposta"

        response = self._post(django_client, {"message": "teste"})

        assert response.status_code == 500

    def test_persistence_failure_emits_structured_memory_event(self):
        from types import SimpleNamespace
        from chat.views import _persist

        class BrokenSession:
            def __setitem__(self, key, value):
                raise RuntimeError("session unavailable")

        with patch("chat.views.emit_event") as emit:
            assert not _persist(SimpleNamespace(session=BrokenSession()), [], {})

        emit.assert_called_once()
        assert emit.call_args.args[:3] == ("memory", "persist", "error")
        assert isinstance(emit.call_args.kwargs["error"], RuntimeError)


    @patch("chat.views.OpenRouterClient")
    def test_returns_500_when_authentication_fails(self, MockClient, django_client):
        MockClient.return_value.chat_completion.side_effect = AuthenticationError(
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

    def _seed_history(self, django_client):
        session = django_client.session
        session["chat_history"] = [{"role": "user", "content": "preciso estudar"}]
        session.save()
        django_client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key

    @patch("chat.views.OpenRouterClient")
    def test_returns_200_on_success(self, MockClient, django_client):
        MockClient.return_value.get_product_recommendations.return_value = _SAMPLE_PRODUCTS
        self._seed_history(django_client)
        response = self._post(django_client, {})
        assert response.status_code == 200

    @patch("chat.views.OpenRouterClient")
    def test_response_contains_products_key(self, MockClient, django_client):
        MockClient.return_value.get_product_recommendations.return_value = _SAMPLE_PRODUCTS
        self._seed_history(django_client)
        response = self._post(django_client, {})
        data = json.loads(response.content)
        assert "products" in data

    @patch("chat.views.OpenRouterClient")
    def test_products_list_has_three_items(self, MockClient, django_client):
        MockClient.return_value.get_product_recommendations.return_value = _SAMPLE_PRODUCTS
        self._seed_history(django_client)
        response = self._post(django_client, {})
        data = json.loads(response.content)
        assert len(data["products"]) == 3

    def test_rejects_empty_history(self, django_client):
        response = self._post(django_client, {})
        assert response.status_code == 400

    @patch("chat.views.OpenRouterClient")
    def test_returns_503_when_service_unavailable(self, MockClient, django_client):
        MockClient.return_value.get_product_recommendations.side_effect = (
            ServiceUnavailableError("fora do ar")
        )
        session = django_client.session
        session["chat_history"] = [{"role": "user", "content": "preciso de um computador"}]
        session.save()
        django_client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key
        response = self._post(django_client, {})
        assert response.status_code == 503

    def test_returns_405_for_get_request(self, django_client):
        response = django_client.get(reverse("chat:recommend"))
        assert response.status_code == 405


# ─── TestAgentSendMessageView ─────────────────────────────────────────────────


@pytest.mark.django_db
class TestAgentSendMessageView:
    def _post(self, django_client, payload):
        return django_client.post(
            reverse("chat:agent_send_message"),
            data=json.dumps(payload),
            content_type="application/json",
        )

    @patch("chat.views._get_agent_graph")
    def test_returns_200_on_success(self, mock_get_graph, django_client):
        mock_get_graph.return_value.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Resposta do agente"}],
            "user_needs": {"proposito": "estudos"},
        }
        response = self._post(django_client, {"message": "Preciso de um notebook"})
        assert response.status_code == 200

    @patch("chat.views._get_agent_graph")
    def test_response_contains_reply_key(self, mock_get_graph, django_client):
        mock_get_graph.return_value.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Resposta do agente"}],
            "user_needs": {},
        }
        response = self._post(django_client, {"message": "teste"})
        data = json.loads(response.content)
        assert data["reply"] == "Resposta do agente"

    @patch("chat.views._get_agent_graph")
    def test_extracts_reply_from_base_message_object(self, mock_get_graph, django_client):
        class FakeMessage:
            content = "Resposta objeto"

        mock_get_graph.return_value.invoke.return_value = {"messages": [FakeMessage()], "user_needs": {}}
        response = self._post(django_client, {"message": "teste"})
        data = json.loads(response.content)
        assert data["reply"] == "Resposta objeto"

    @patch("chat.views._get_agent_graph")
    def test_saves_user_message_to_session(self, mock_get_graph, django_client):
        mock_get_graph.return_value.invoke.return_value = {"messages": [], "user_needs": {}}
        self._post(django_client, {"message": "mensagem do usuário"})
        history = django_client.session.get("chat_history", [])
        assert any(m["role"] == "user" and m["content"] == "mensagem do usuário" for m in history)

    @patch("chat.views._get_agent_graph")
    def test_saves_assistant_reply_to_session(self, mock_get_graph, django_client):
        mock_get_graph.return_value.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Resposta do agente"}],
            "user_needs": {},
        }
        self._post(django_client, {"message": "teste"})
        history = django_client.session.get("chat_history", [])
        assert any(m["role"] == "assistant" and m["content"] == "Resposta do agente" for m in history)

    @patch("chat.views._get_agent_graph")
    def test_persists_user_needs_in_session(self, mock_get_graph, django_client):
        mock_get_graph.return_value.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Ok"}],
            "user_needs": {"proposito": "estudos", "orcamento": 3000},
        }
        self._post(django_client, {"message": "teste"})
        assert django_client.session.get("user_needs") == {
            "proposito": "estudos",
            "orcamento": 3000,
        }

    def test_returns_400_when_message_is_missing(self, django_client):
        response = self._post(django_client, {})
        assert response.status_code == 400

    def test_returns_400_when_message_is_empty_string(self, django_client):
        response = self._post(django_client, {"message": ""})
        assert response.status_code == 400

    def test_returns_400_for_invalid_json(self, django_client):
        response = django_client.post(
            reverse("chat:agent_send_message"),
            data="não é json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_returns_405_for_get_request(self, django_client):
        response = django_client.get(reverse("chat:agent_send_message"))
        assert response.status_code == 405

    def test_rejects_invalid_json(self, django_client):
        response = django_client.post(
            reverse("chat:send_message"), data="not-json", content_type="application/json"
        )
        assert response.status_code == 400

    def test_rejects_wrong_json_type(self, django_client):
        response = django_client.post(
            reverse("chat:send_message"), data="[]", content_type="application/json"
        )
        assert response.status_code == 400

    def test_rejects_request_without_csrf(self):
        from django.test import Client
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(
            reverse("chat:send_message"),
            data=json.dumps({"message": "teste"}),
            content_type="application/json",
        )
        assert response.status_code == 403

    @patch("chat.views._get_agent_graph")
    def test_returns_500_on_unexpected_agent_error(self, mock_get_graph, django_client):
        mock_get_graph.return_value.invoke.side_effect = RuntimeError("erro inesperado")
        response = self._post(django_client, {"message": "teste"})
        assert response.status_code == 500

    @patch("chat.views._get_agent_graph")
    def test_includes_report_when_available(self, mock_get_graph, django_client):
        mock_get_graph.return_value.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Recomendo este"}],
            "user_needs": {},
            "report": "## Relatório",
        }
        response = self._post(django_client, {"message": "teste"})
        data = json.loads(response.content)
        assert data["report"] == "## Relatório"
