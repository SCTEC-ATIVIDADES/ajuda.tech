import hashlib
import hmac
import json

import pytest

from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch


@pytest.fixture(autouse=True)
def clear_webhook_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def webhook_settings(settings):
    settings.AUTOMATION_WEBHOOK_SECRET = "test-secret"


def _post(client, payload, secret="test-secret"):
    body = json.dumps(payload).encode()
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return client.post(
        reverse("chat:automation_webhook"),
        data=body,
        content_type="application/json",
        HTTP_X_AUTOMATION_SIGNATURE=signature,
    )


@pytest.mark.django_db
class TestWebAutomationProxy:
    @patch("chat.views.requests.post")
    def test_forwards_message_to_n8n(self, post, client, webhook_settings, settings):
        post.return_value.status_code = 200
        post.return_value.json.return_value = {"reply": "Resposta", "trace_id": "trace"}
        settings.N8N_WEBHOOK_URL = "http://n8n.test/webhook/ajuda-tech"

        response = client.post(
            reverse("chat:web_automation_proxy"),
            data=json.dumps({"message": "Preciso estudar"}),
            content_type="application/json",
            HTTP_COOKIE="sessionid=session; csrftoken=token",
        )

        assert response.status_code == 200
        assert response.json()["reply"] == "Resposta"
        payload = post.call_args.kwargs["json"]
        assert payload["message"] == "Preciso estudar"
        assert payload["event_id"]
        assert post.call_args.kwargs["headers"]["Cookie"] == "sessionid=session; csrftoken=token"

    @patch("chat.views.requests.post")
    def test_returns_502_for_invalid_n8n_response(self, post, client, webhook_settings):
        post.return_value.status_code = 200
        post.return_value.json.side_effect = ValueError
        response = client.post(
            reverse("chat:web_automation_proxy"),
            data=json.dumps({"message": "teste"}),
            content_type="application/json",
        )
        assert response.status_code == 502

    def test_requires_csrf(self, client, webhook_settings):
        from django.test import Client

        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(
            reverse("chat:web_automation_proxy"),
            data=json.dumps({"message": "teste"}),
            content_type="application/json",
        )
        assert response.status_code == 403

    @patch("chat.views.requests.post", side_effect=__import__("requests").RequestException)
    def test_returns_503_when_n8n_unavailable(self, post, client, webhook_settings):
        response = client.post(
            reverse("chat:web_automation_proxy"),
            data=json.dumps({"message": "teste"}),
            content_type="application/json",
        )
        assert response.status_code == 503


class TestAutomationWebhook:
    @patch("chat.views._get_agent_graph")
    def test_processes_normal_payload(self, mock_graph, client, webhook_settings):
        mock_graph.return_value.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Resposta"}],
            "user_needs": {},
        }
        response = _post(client, {"event_id": "evt-1", "message": "Preciso estudar"})
        assert response.status_code == 200
        assert response.json()["reply"] == "Resposta"
        mock_graph.return_value.invoke.assert_called_once()

    def test_rejects_invalid_signature(self, client, webhook_settings):
        response = _post(client, {"event_id": "evt-1", "message": "teste"}, "wrong")
        assert response.status_code == 401

    def test_rejects_invalid_payload(self, client, webhook_settings):
        response = _post(client, {"event_id": "evt-1"})
        assert response.status_code == 400

    @patch("chat.views._get_agent_graph")
    def test_duplicate_is_idempotent(self, mock_graph, client, webhook_settings):
        mock_graph.return_value.invoke.return_value = {
            "messages": [{"role": "assistant", "content": "Resposta"}],
            "user_needs": {},
        }
        payload = {"event_id": "evt-1", "message": "teste"}
        first = _post(client, payload)
        second = _post(client, payload)
        assert first.status_code == 200
        assert second.json() == {"ok": True, "duplicate": True}
        mock_graph.return_value.invoke.assert_called_once()

    @patch("chat.views._get_agent_graph")
    def test_failure_releases_idempotency_key(self, mock_graph, client, webhook_settings):
        mock_graph.return_value.invoke.side_effect = RuntimeError("falha")
        payload = {"event_id": "evt-1", "message": "teste"}
        response = _post(client, payload)
        assert response.status_code == 500
        assert not cache.get("automation-webhook:evt-1")
