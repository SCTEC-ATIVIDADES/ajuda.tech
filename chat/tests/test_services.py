"""
Testes unitários para chat.services.OpenRouterClient
Metodologia: TDD — estes testes foram escritos ANTES da implementação.

Cobertura:
  - Inicialização e leitura de configurações
  - Construção de cabeçalhos HTTP
  - Chamada à API OpenRouter e processamento de resposta
  - Tratamento de erros HTTP (401, 429, 5xx)
  - Lógica de retry com backoff exponencial
  - Extração e parsing de recomendações de produtos
"""

import json
import pytest
from unittest.mock import patch, MagicMock, call

import requests as req_module

from chat.observability import clear_metrics, execution_context, metrics_snapshot

from chat.exceptions import (
    AuthenticationError,
    InvalidResponseError,
    RateLimitError,
    ServiceUnavailableError,
)
from chat.services import OpenRouterClient

# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_mock_response(status_code=200, json_data=None):
    """Cria um mock de requests.Response com status_code e corpo JSON."""
    mock = MagicMock()
    mock.status_code = status_code
    if json_data is not None:
        mock.json.return_value = json_data
    else:
        mock.json.side_effect = ValueError("No JSON")
    return mock


def make_chat_response(content="resposta de teste"):
    """Cria o payload JSON padrão de uma resposta bem-sucedida do OpenRouter."""
    return {
        "choices": [
            {"message": {"role": "assistant", "content": content}}
        ]
    }


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Cliente com chave explícita — não lê settings."""
    return OpenRouterClient(api_key="test-api-key")


# ─── TestOpenRouterClientInit ──────────────────────────────────────────────────

class TestOpenRouterClientInit:
    def test_init_stores_explicit_api_key(self, client):
        assert client.api_key == "test-api-key"

    def test_init_reads_api_key_from_django_settings(self, settings):
        settings.LLM_API_KEY = "chave-via-settings"
        c = OpenRouterClient()
        assert c.api_key == "chave-via-settings"

    def test_init_raises_improperly_configured_when_key_missing(self, settings):
        settings.LLM_API_KEY = ""
        from django.core.exceptions import ImproperlyConfigured
        with pytest.raises(ImproperlyConfigured):
            OpenRouterClient()

    def test_explicit_key_takes_precedence_over_settings(self, settings):
        settings.LLM_API_KEY = "chave-settings"
        c = OpenRouterClient(api_key="chave-explicita")
        assert c.api_key == "chave-explicita"

    def test_reads_model_from_settings(self, settings):
        settings.LLM_MODEL = "anthropic/claude-3-haiku"
        c = OpenRouterClient(api_key="test-key")
        assert c.model == "anthropic/claude-3-haiku"

    def test_reads_timeout_from_settings(self, settings):
        settings.LLM_TIMEOUT = 60
        c = OpenRouterClient(api_key="test-key")
        assert c.timeout == 60

    def test_default_model_is_set(self):
        c = OpenRouterClient(api_key="test-key")
        assert c.model is not None
        assert isinstance(c.model, str)

    def test_default_timeout_is_positive(self):
        c = OpenRouterClient(api_key="test-key")
        assert c.timeout > 0


# ─── TestBuildHeaders ─────────────────────────────────────────────────────────

class TestBuildHeaders:
    def test_authorization_uses_bearer_scheme(self, client):
        headers = client._build_headers()
        assert headers["Authorization"] == "Bearer test-api-key"

    def test_content_type_is_application_json(self, client):
        headers = client._build_headers()
        assert headers["Content-Type"] == "application/json"

    def test_http_referer_header_is_present(self, client):
        headers = client._build_headers()
        assert "HTTP-Referer" in headers

    def test_x_title_header_is_present(self, client):
        headers = client._build_headers()
        assert "X-Title" in headers


# ─── TestChatCompletion ───────────────────────────────────────────────────────

class TestChatCompletion:
    @patch("chat.services.requests.post")
    def test_returns_assistant_content_string(self, mock_post, client):
        mock_post.return_value = make_mock_response(
            200, make_chat_response("Olá! Como posso ajudar?")
        )
        result = client.chat_completion([{"role": "user", "content": "Oi"}])
        assert result == "Olá! Como posso ajudar?"

    @patch("chat.services.requests.post")
    def test_first_message_is_system_prompt(self, mock_post, client):
        mock_post.return_value = make_mock_response(200, make_chat_response())
        client.chat_completion([{"role": "user", "content": "Oi"}])
        payload = json.loads(mock_post.call_args.kwargs["data"])
        assert payload["messages"][0]["role"] == "system"

    @patch("chat.services.requests.post")
    def test_system_prompt_mentions_herbert(self, mock_post, client):
        mock_post.return_value = make_mock_response(200, make_chat_response())
        client.chat_completion([{"role": "user", "content": "Oi"}])
        payload = json.loads(mock_post.call_args.kwargs["data"])
        assert "Herbert" in payload["messages"][0]["content"]

    @patch("chat.services.requests.post")
    def test_conversation_history_follows_system_message(self, mock_post, client):
        mock_post.return_value = make_mock_response(200, make_chat_response())
        history = [{"role": "user", "content": "Preciso de um notebook"}]
        client.chat_completion(history)
        payload = json.loads(mock_post.call_args.kwargs["data"])
        assert payload["messages"][1:] == history

    @patch("chat.services.requests.post")
    def test_uses_model_from_client_attribute(self, mock_post, client):
        mock_post.return_value = make_mock_response(200, make_chat_response())
        client.model = "custom/model"
        client.chat_completion([{"role": "user", "content": "test"}])
        payload = json.loads(mock_post.call_args.kwargs["data"])
        assert payload["model"] == "custom/model"

    @patch("chat.services.requests.post")
    def test_passes_timeout_to_requests(self, mock_post, client):
        mock_post.return_value = make_mock_response(200, make_chat_response())
        client.timeout = 45
        client.chat_completion([{"role": "user", "content": "test"}])
        assert mock_post.call_args.kwargs["timeout"] == 45

    @patch("chat.services.requests.post")
    def test_posts_to_correct_endpoint(self, mock_post, client):
        mock_post.return_value = make_mock_response(200, make_chat_response())
        client.chat_completion([{"role": "user", "content": "test"}])
        url = mock_post.call_args.args[0]
        assert "openrouter.ai" in url
        assert "chat/completions" in url


# ─── TestHttpErrorHandling ────────────────────────────────────────────────────

class TestHttpErrorHandling:
    @patch("chat.services.requests.post")
    def test_401_raises_authentication_error(self, mock_post, client):
        mock_post.return_value = make_mock_response(401)
        with pytest.raises(AuthenticationError):
            client.chat_completion([{"role": "user", "content": "test"}])

    @patch("chat.services.requests.post")
    def test_429_raises_rate_limit_error(self, mock_post, client):
        mock_post.return_value = make_mock_response(429)
        with pytest.raises(RateLimitError):
            client.chat_completion([{"role": "user", "content": "test"}])

    @patch("chat.services.requests.post")
    def test_500_raises_service_unavailable(self, mock_post, client):
        mock_post.return_value = make_mock_response(500)
        with pytest.raises(ServiceUnavailableError):
            client.chat_completion([{"role": "user", "content": "test"}])

    @patch("chat.services.requests.post")
    def test_503_raises_service_unavailable(self, mock_post, client):
        mock_post.return_value = make_mock_response(503)
        with pytest.raises(ServiceUnavailableError):
            client.chat_completion([{"role": "user", "content": "test"}])

    @patch("chat.services.requests.post")
    def test_unexpected_4xx_raises_invalid_response(self, mock_post, client):
        mock_post.return_value = make_mock_response(422)
        with pytest.raises(InvalidResponseError):
            client.chat_completion([{"role": "user", "content": "test"}])

    @patch("chat.services.requests.post")
    def test_non_json_body_raises_invalid_response(self, mock_post, client):
        mock = MagicMock()
        mock.status_code = 200
        mock.json.side_effect = ValueError("não é JSON")
        mock_post.return_value = mock
        with pytest.raises(InvalidResponseError):
            client.chat_completion([{"role": "user", "content": "test"}])

    @patch("chat.services.requests.post")
    def test_empty_choices_raises_invalid_response(self, mock_post, client):
        mock_post.return_value = make_mock_response(200, {"choices": []})
        with pytest.raises(InvalidResponseError):
            client.chat_completion([{"role": "user", "content": "test"}])

    @patch("chat.services.requests.post")
    def test_missing_choices_key_raises_invalid_response(self, mock_post, client):
        mock_post.return_value = make_mock_response(200, {"result": "sem choices"})
        with pytest.raises(InvalidResponseError):
            client.chat_completion([{"role": "user", "content": "test"}])

    @patch("chat.services.requests.post")
    def test_requests_timeout_raises_service_unavailable(self, mock_post, client):
        mock_post.side_effect = req_module.exceptions.Timeout()
        with pytest.raises(ServiceUnavailableError):
            client.chat_completion([{"role": "user", "content": "test"}])

    @patch("chat.services.requests.post")
    def test_connection_error_raises_service_unavailable(self, mock_post, client):
        mock_post.side_effect = req_module.exceptions.ConnectionError()
        with pytest.raises(ServiceUnavailableError):
            client.chat_completion([{"role": "user", "content": "test"}])

    @patch("chat.services.requests.post")
    def test_401_does_not_retry(self, mock_post, client):
        mock_post.return_value = make_mock_response(401)
        with pytest.raises(AuthenticationError):
            client.chat_completion([{"role": "user", "content": "test"}])
        assert mock_post.call_count == 1


# ─── TestRetryLogic ───────────────────────────────────────────────────────────

class TestRetryLogic:
    @patch("chat.services.time.sleep")
    @patch("chat.services.requests.post")
    def test_retries_up_to_max_retries_on_timeout(self, mock_post, mock_sleep, client):
        mock_post.side_effect = req_module.exceptions.Timeout()
        with pytest.raises(ServiceUnavailableError):
            client.chat_completion([{"role": "user", "content": "test"}])
        assert mock_post.call_count == client.max_retries + 1

    @patch("chat.services.time.sleep")
    @patch("chat.services.requests.post")
    def test_succeeds_on_second_attempt(self, mock_post, mock_sleep, client):
        mock_post.side_effect = [
            req_module.exceptions.Timeout(),
            make_mock_response(200, make_chat_response("funcionou")),
        ]
        result = client.chat_completion([{"role": "user", "content": "test"}])
        assert result == "funcionou"
        assert mock_post.call_count == 2

    @patch("chat.services.time.sleep")
    @patch("chat.services.requests.post")
    def test_exponential_backoff_between_retries(self, mock_post, mock_sleep, client):
        mock_post.side_effect = req_module.exceptions.Timeout()
        with pytest.raises(ServiceUnavailableError):
            client.chat_completion([{"role": "user", "content": "test"}])
        sleep_calls = [c.args[0] for c in mock_sleep.call_args_list]
        # Cada espera deve ser maior que a anterior (backoff exponencial)
        for i in range(1, len(sleep_calls)):
            assert sleep_calls[i] >= sleep_calls[i - 1]

    @patch("chat.services.emit_event")
    @patch("chat.services.time.sleep")
    @patch("chat.services.requests.post")
    def test_timeout_emits_timeout_and_retry_events(self, mock_post, mock_sleep, emit, client):
        mock_post.side_effect = req_module.exceptions.Timeout()
        with pytest.raises(ServiceUnavailableError):
            with execution_context("trace-retry", "run-retry"):
                client.chat_completion([{"role": "user", "content": "test"}])
        events = [call.args[1] for call in emit.call_args_list]
        assert "timeout" in events
        assert "retry" in events

    @patch("chat.services.emit_event")
    @patch("chat.services.requests.post")
    def test_429_emits_failure_without_retry(self, mock_post, emit, client):
        mock_post.return_value = make_mock_response(429)
        with pytest.raises(RateLimitError):
            client.chat_completion([{"role": "user", "content": "test"}])
        assert mock_post.call_count == 1
        assert [call.args[1] for call in emit.call_args_list] == ["failure"]

    @patch("chat.services.time.sleep")
    @patch("chat.services.requests.post")
    def test_retries_on_500_server_error(self, mock_post, mock_sleep, client):
        mock_post.side_effect = [
            make_mock_response(500),
            make_mock_response(200, make_chat_response("recuperou")),
        ]
        result = client.chat_completion([{"role": "user", "content": "test"}])
        assert result == "recuperou"
        assert mock_post.call_count == 2


# ─── TestProductRecommendations ───────────────────────────────────────────────

# Produtos de exemplo que a IA retornaria em JSON
_SAMPLE_PRODUCTS = [
    {
        "name": "Dell Inspiron 15",
        "price": "R$ 2.499",
        "type": "Notebook",
        "specs": "Intel Core i5, 8GB RAM, 256GB SSD",
        "justification": "Ótimo custo-benefício para uso básico",
        "option": "budget",
    },
    {
        "name": "Lenovo IdeaPad 5",
        "price": "R$ 3.299",
        "type": "Notebook",
        "specs": "Intel Core i7, 16GB RAM, 512GB SSD",
        "justification": "Equilíbrio perfeito de desempenho e preço",
        "option": "ideal",
    },
    {
        "name": "ASUS ZenBook Pro",
        "price": "R$ 5.999",
        "type": "Notebook",
        "specs": "Intel Core i9, 32GB RAM, 1TB SSD",
        "justification": "Desempenho máximo para demandas intensas",
        "option": "premium",
    },
]


class TestProductRecommendations:
    @patch("chat.services.requests.post")
    def test_returns_a_list(self, mock_post, client):
        mock_post.return_value = make_mock_response(
            200, make_chat_response(json.dumps(_SAMPLE_PRODUCTS))
        )
        result = client.get_product_recommendations([])
        assert isinstance(result, list)

    @patch("chat.services.requests.post")
    def test_returns_three_products(self, mock_post, client):
        mock_post.return_value = make_mock_response(
            200, make_chat_response(json.dumps(_SAMPLE_PRODUCTS))
        )
        result = client.get_product_recommendations([])
        assert len(result) == 3

    @patch("chat.services.requests.post")
    def test_each_product_has_required_keys(self, mock_post, client):
        mock_post.return_value = make_mock_response(
            200, make_chat_response(json.dumps(_SAMPLE_PRODUCTS))
        )
        products = client.get_product_recommendations([])
        required_keys = {"name", "price", "type", "specs", "justification", "option"}
        for product in products:
            assert required_keys.issubset(product.keys())

    @patch("chat.services.requests.post")
    def test_products_cover_ideal_budget_and_premium_options(self, mock_post, client):
        mock_post.return_value = make_mock_response(
            200, make_chat_response(json.dumps(_SAMPLE_PRODUCTS))
        )
        products = client.get_product_recommendations([])
        options = {p["option"] for p in products}
        assert options == {"ideal", "budget", "premium"}

    @patch("chat.services.requests.post")
    def test_raises_invalid_response_when_no_json_array_found(self, mock_post, client):
        mock_post.return_value = make_mock_response(
            200, make_chat_response("Não tenho produtos para sugerir agora.")
        )
        with pytest.raises(InvalidResponseError):
            client.get_product_recommendations([])

    @patch("chat.services.requests.post")
    def test_raises_invalid_response_when_json_is_object_not_list(self, mock_post, client):
        mock_post.return_value = make_mock_response(
            200, make_chat_response('{"name": "só um objeto"}')
        )
        with pytest.raises(InvalidResponseError):
            client.get_product_recommendations([])

    @patch("chat.services.requests.post")
    def test_parses_json_wrapped_in_markdown_code_block(self, mock_post, client):
        wrapped = f"```json\n{json.dumps(_SAMPLE_PRODUCTS)}\n```"
        mock_post.return_value = make_mock_response(
            200, make_chat_response(wrapped)
        )
        products = client.get_product_recommendations([])
        assert len(products) == 3

    @patch("chat.services.requests.post")
    def test_parses_json_with_leading_text(self, mock_post, client):
        with_prefix = f"Aqui estão as opções:\n\n{json.dumps(_SAMPLE_PRODUCTS)}"
        mock_post.return_value = make_mock_response(
            200, make_chat_response(with_prefix)
        )
        products = client.get_product_recommendations([])
        assert len(products) == 3

    @patch("chat.services.requests.post")
    def test_sends_extraction_prompt_as_last_user_message(self, mock_post, client):
        mock_post.return_value = make_mock_response(
            200, make_chat_response(json.dumps(_SAMPLE_PRODUCTS))
        )
        client.get_product_recommendations([])
        payload = json.loads(mock_post.call_args.kwargs["data"])
        last_message = payload["messages"][-1]
        assert last_message["role"] == "user"

    @patch("chat.services.requests.post")
    def test_includes_conversation_history_in_payload(self, mock_post, client):
        history = [
            {"role": "user", "content": "Preciso de um notebook para estudar"},
            {"role": "assistant", "content": "Qual é o seu orçamento?"},
            {"role": "user", "content": "Até R$ 3.000"},
        ]
        mock_post.return_value = make_mock_response(
            200, make_chat_response(json.dumps(_SAMPLE_PRODUCTS))
        )
        client.get_product_recommendations(history)
        payload = json.loads(mock_post.call_args.kwargs["data"])
        messages = payload["messages"]
        # sistema + histórico + prompt de extração
        assert len(messages) >= len(history) + 2
