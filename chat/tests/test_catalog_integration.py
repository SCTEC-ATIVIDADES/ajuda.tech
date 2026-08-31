import json
from unittest.mock import patch

import pytest

from chat.agent.tools import buscar_produtos


PRODUTOS_FIXTURE = [
    {
        "id": 1,
        "nome": "Notebook Básico",
        "tipo": "notebook",
        "preco": 3500.0,
        "especificacoes": {"ram": "8GB"},
        "indicado_para": ["estudos"],
        "mobilidade": "alta",
    }
]


def test_external_catalog_success():
    from chat.services import ExternalCatalogClient
    response = type("Response", (), {"status_code": 200, "json": lambda self: {"produtos": PRODUTOS_FIXTURE}})()
    with patch("chat.services.requests.get", return_value=response):
        assert ExternalCatalogClient(url="https://catalog.test").fetch_products() == PRODUTOS_FIXTURE


def test_external_catalog_timeout_retries():
    from chat.services import ExternalCatalogClient
    with patch("chat.services.requests.get", side_effect=__import__("requests").exceptions.Timeout()), patch("chat.services.time.sleep") as sleep:
        from chat.services import CatalogIntegrationError
        with pytest.raises(CatalogIntegrationError, match="Timeout"):
            ExternalCatalogClient(url="https://catalog.test", max_retries=2).fetch_products()
    assert sleep.call_count == 2


def test_external_catalog_4xx_no_retry():
    from chat.services import CatalogIntegrationError, ExternalCatalogClient
    response = type("Response", (), {"status_code": 404})()
    with patch("chat.services.requests.get", return_value=response) as get:
        with pytest.raises(CatalogIntegrationError, match="HTTP 404"):
            ExternalCatalogClient(url="https://catalog.test").fetch_products()
    get.assert_called_once()


def test_external_catalog_5xx_retries():
    from chat.services import CatalogIntegrationError, ExternalCatalogClient
    response = type("Response", (), {"status_code": 503})()
    with patch("chat.services.requests.get", return_value=response) as get, patch("chat.services.time.sleep") as sleep:
        with pytest.raises(CatalogIntegrationError, match="HTTP 503"):
            ExternalCatalogClient(url="https://catalog.test", max_retries=2).fetch_products()
    assert get.call_count == 3
    assert sleep.call_count == 2


def test_external_catalog_invalid_response():
    from chat.services import CatalogIntegrationError, ExternalCatalogClient
    response = type("Response", (), {"status_code": 200, "json": lambda self: {"produtos": {}}})()
    with patch("chat.services.requests.get", return_value=response):
        with pytest.raises(CatalogIntegrationError):
            ExternalCatalogClient(url="https://catalog.test").fetch_products()


def test_configured_catalog_success_marks_external_origin():
    from django.test import override_settings

    with override_settings(CATALOG_API_URL="https://catalog.test"), patch(
        "chat.agent.tools.fetch_external_catalog", return_value=PRODUTOS_FIXTURE
    ):
        payload = json.loads(buscar_produtos.invoke({"categoria": "notebook", "orcamento_max": 5000}))

    assert payload["ok"] is True
    assert payload["origem"] == "externo"
    assert payload["produtos"] == PRODUTOS_FIXTURE


def test_configured_catalog_falls_back_to_local():
    from django.test import override_settings
    from chat.agent.tools import _carregar_produtos

    with override_settings(CATALOG_API_URL="https://catalog.test"), patch(
        "chat.agent.tools.fetch_external_catalog", side_effect=RuntimeError("timeout")
    ), patch("chat.agent.tools._carregar_produtos", return_value=PRODUTOS_FIXTURE):
        result = buscar_produtos.invoke({"categoria": "notebook", "orcamento_max": 5000})

    payload = __import__("json").loads(result)
    assert payload["origem"] == "local_fallback"
    assert payload["produtos"] == PRODUTOS_FIXTURE
