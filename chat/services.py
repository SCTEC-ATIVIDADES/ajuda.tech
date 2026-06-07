"""
Cliente OpenRouter para o assistente Herbert.

Responsabilidades:
- Autenticação via Bearer token lido do settings.LLM_API_KEY
- Envio de mensagens à API /chat/completions do OpenRouter
- Retry com backoff exponencial em falhas transitórias (timeout, 5xx)
- Sem retry para erros permanentes (401, 429, 4xx inesperado)
- Parsing de recomendações de produtos a partir da resposta da IA

Uso:
    from chat.services import OpenRouterClient
    client = OpenRouterClient()
    reply = client.chat_completion(history)
    products = client.get_product_recommendations(history)
"""

import json
import logging
import re
import time

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from chat.exceptions import (
    AuthenticationError,
    InvalidResponseError,
    OpenRouterError,
    RateLimitError,
    ServiceUnavailableError,
)
from chat.prompts import PRODUCT_EXTRACTION_PROMPT, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_DEFAULT_MODEL = "deepseek/deepseek-v4-flash:free"
_DEFAULT_TIMEOUT = 60
_DEFAULT_MAX_RETRIES = 2
_DEFAULT_MAX_RATE_LIMIT_RETRIES = 10
_RETRYABLE_STATUS_CODES = frozenset({500, 502, 503, 504})
_MAX_CHAT_TOKENS = 800
_MAX_EXTRACTION_TOKENS = 1500


class OpenRouterClient:
    """
    Encapsula toda a comunicação com a API OpenRouter.

    Parâmetros
    ----------
    api_key : str | None
        Chave de API explícita. Se None, usa settings.LLM_API_KEY.
    max_retries : int
        Número máximo de tentativas após a primeira falha.
    """

    def __init__(
        self,
        api_key: str | None = None,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        max_rate_limit_retries: int = _DEFAULT_MAX_RATE_LIMIT_RETRIES,
    ):
        if api_key:
            self.api_key = api_key
        else:
            key = getattr(settings, "LLM_API_KEY", "")
            if not key:
                raise ImproperlyConfigured(
                    "LLM_API_KEY não configurada. "
                    "Defina a variável de ambiente LLM_API_KEY ou settings.LLM_API_KEY."
                )
            self.api_key = key

        self.model: str = getattr(settings, "LLM_MODEL", _DEFAULT_MODEL)
        self.timeout: int = getattr(settings, "LLM_TIMEOUT", _DEFAULT_TIMEOUT)
        self.max_retries: int = max_retries
        self.max_rate_limit_retries: int = max_rate_limit_retries

    # ─── Public API ───────────────────────────────────────────────────────────

    def chat_completion(self, messages: list[dict]) -> str:
        """
        Envia o histórico de mensagens e retorna a resposta do assistente.

        Parameters
        ----------
        messages : list[dict]
            Lista de dicts com keys ``role`` e ``content``.

        Returns
        -------
        str
            Conteúdo textual da resposta do assistente.

        Raises
        ------
        AuthenticationError
            Chave inválida (HTTP 401).
        RateLimitError
            Limite de requisições atingido (HTTP 429).
        ServiceUnavailableError
            Falha de rede ou API indisponível.
        InvalidResponseError
            Resposta com estrutura inesperada.
        """
        full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
        return self._chat_completion(full_messages)

    def get_product_recommendations(self, history: list[dict]) -> list[dict]:
        """
        Gera uma lista de 3 produtos recomendados com base no histórico.

        Parameters
        ----------
        history : list[dict]
            Histórico da conversa (role + content).

        Returns
        -------
        list[dict]
            Lista com 3 dicts: chaves ``name``, ``price``, ``type``,
            ``specs``, ``justification`` e ``option``.

        Raises
        ------
        InvalidResponseError
            Se a IA não retornar um array JSON válido.
        """
        messages = self._build_extraction_messages(history)
        content = self._chat_completion(messages, is_extraction=True)
        return self._parse_products(content)

    # ─── Private helpers ──────────────────────────────────────────────────────

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": getattr(settings, "SITE_URL", "http://localhost:8000"),
            "X-Title": getattr(settings, "SITE_NAME", "Ajuda Tech"),
        }

    def _build_extraction_messages(self, history: list[dict]) -> list[dict]:
        return (
            [{"role": "system", "content": SYSTEM_PROMPT}]
            + history
            + [{"role": "user", "content": PRODUCT_EXTRACTION_PROMPT}]
        )

    def _build_payload(self, messages: list[dict], max_tokens: int) -> dict:
        return {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "include_reasoning": False,
        }

    def _backoff_sleep(self, attempt: int) -> None:
        time.sleep(2 ** attempt)

    def _chat_completion(self, messages: list[dict], *, is_extraction: bool = False) -> str:
        """Monta o payload e delega a execução com retry."""
        max_tokens = _MAX_EXTRACTION_TOKENS if is_extraction else _MAX_CHAT_TOKENS
        payload = self._build_payload(messages, max_tokens)
        return self._execute_with_rate_limit_retry(payload)

    def _execute_with_rate_limit_retry(self, payload: dict) -> str:
        """Envolve a chamada com retry específico para 429 (contador separado)."""
        for attempt in range(self.max_rate_limit_retries + 1):
            try:
                return self._execute_with_backoff_retry(payload)
            except RateLimitError as exc:
                if attempt == self.max_rate_limit_retries:
                    raise
                logger.warning(
                    "Rate limit atingido (429) — tentativa %d/%d. Aguardando %ds.",
                    attempt + 1,
                    self.max_rate_limit_retries,
                    exc.retry_after,
                )
                time.sleep(exc.retry_after)
        raise ServiceUnavailableError("Rate limit excedido após todas as tentativas.")  # pragma: no cover

    def _execute_with_backoff_retry(self, payload: dict) -> str:
        """Executa a chamada HTTP com retry exponencial para falhas transitórias (5xx, timeout, conexão)."""
        last_exc: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    _OPENROUTER_URL,
                    headers=self._build_headers(),
                    data=json.dumps(payload),
                    timeout=self.timeout,
                )
                return self._handle_response(response)

            except (AuthenticationError, InvalidResponseError, RateLimitError):
                raise  # sem retry para erros permanentes

            except ServiceUnavailableError as exc:
                last_exc = exc

            except requests.exceptions.Timeout as exc:
                last_exc = ServiceUnavailableError(f"Timeout após {self.timeout}s: {exc}")

            except requests.exceptions.ConnectionError as exc:
                last_exc = ServiceUnavailableError(f"Erro de conexão: {exc}")

            if attempt < self.max_retries:
                logger.warning(
                    "Falha transitória (tentativa %d/%d). Aguardando %ds.",
                    attempt + 1,
                    self.max_retries + 1,
                    2 ** attempt,
                )
                self._backoff_sleep(attempt)

        raise last_exc  # type: ignore[misc]

    def _handle_response(self, response: requests.Response) -> str:
        """
        Valida o status HTTP e extrai o conteúdo da resposta.

        Raises
        ------
        AuthenticationError  para 401
        RateLimitError       para 429
        ServiceUnavailableError  para 5xx
        InvalidResponseError para demais 4xx ou payload inválido
        """
        status = response.status_code

        if status == 401:
            raise AuthenticationError("Chave de API inválida ou sem permissão (HTTP 401).")
        if status == 402:
            try:
                detail = response.json().get("error", {}).get("message", "")
            except ValueError:
                detail = response.text[:200]
            raise InvalidResponseError(
                f"Modelo indisponível ou sem créditos (HTTP 402): {detail}"
            )
        if status == 429:
            retry_after = int(response.headers.get("Retry-After", 10))
            raise RateLimitError("Limite de requisições excedido (HTTP 429).", retry_after=retry_after)
        if status in _RETRYABLE_STATUS_CODES:
            raise ServiceUnavailableError(f"OpenRouter indisponível (HTTP {status}).")
        if status >= 400:
            try:
                detail = response.json().get("error", {}).get("message", "")
            except ValueError:
                detail = response.text[:200]
            logger.error("Resposta inesperada da API (HTTP %d): %s", status, detail)
            raise InvalidResponseError(
                f"Resposta inesperada da API (HTTP {status}): {detail}"
            )

        try:
            body = response.json()
        except ValueError as exc:
            raise InvalidResponseError(f"Resposta não é JSON válido: {exc}") from exc

        try:
            choices = body["choices"]
            if not choices:
                raise InvalidResponseError("'choices' está vazio na resposta.")
            choice = choices[0]
            content = choice["message"]["content"]
            if content is None:
                finish_reason = choice.get("finish_reason", "unknown")
                if finish_reason == "length":
                    raise InvalidResponseError(
                        f"Modelo esgotou tokens antes de gerar resposta "
                        f"(finish_reason={finish_reason}). Tente novamente."
                    )
                raise ServiceUnavailableError(
                    f"Modelo retornou content=None (finish_reason={finish_reason})."
                )
            # Remove blocos de raciocínio interno (<think>...</think>) que
            # alguns modelos (ex: DeepSeek) incluem no campo content.
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            return content
        except (KeyError, IndexError, TypeError) as exc:
            raise InvalidResponseError(
                f"Estrutura de resposta inesperada: {exc}. Corpo: {body}"
            ) from exc

    def _parse_products(self, content: str) -> list[dict]:
        """
        Extrai e valida o array JSON de produtos do texto retornado pela IA.

        Aceita:
        - JSON puro: ``[...]``
        - JSON em bloco Markdown: `` ```json\\n[...]\\n``` ``
        - JSON precedido de texto livre

        Raises
        ------
        InvalidResponseError
            Se nenhum array JSON válido for encontrado.
        """
        markdown_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", content, re.DOTALL)
        if markdown_match:
            candidate = markdown_match.group(1)
        else:
            bracket_pos = content.find("[")
            if bracket_pos == -1:
                raise InvalidResponseError(
                    "Nenhum array JSON encontrado na resposta da IA."
                )
            candidate = content[bracket_pos:]

        try:
            products = json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise InvalidResponseError(
                f"Falha ao parsear JSON dos produtos: {exc}"
            ) from exc

        if not isinstance(products, list):
            raise InvalidResponseError(
                "A resposta da IA deve ser um array JSON, não um objeto."
            )

        logger.debug("Produtos parseados com sucesso: %d itens.", len(products))
        return products
