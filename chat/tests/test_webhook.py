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
