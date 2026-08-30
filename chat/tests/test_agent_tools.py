"""Testes das tools do agente LangGraph."""

import json
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from chat.agent.tools import (
    buscar_produtos,
    comparar_produtos,
    gerar_relatorio,
    _carregar_produtos,
)

PRODUTOS_FIXTURE = [
    {
        "id": 1,
        "nome": "Notebook Básico",
        "tipo": "notebook",
        "preco": 3500.0,
        "especificacoes": {"ram": "8GB", "ssd": "256GB"},
        "indicado_para": ["estudos", "escritório"],
        "mobilidade": "alta",
    },
    {
        "id": 2,
        "nome": "Desktop Gamer",
        "tipo": "desktop",
        "preco": 7000.0,
        "especificacoes": {"ram": "16GB", "ssd": "512GB"},
        "indicado_para": ["games"],
        "mobilidade": "baixa",
    },
]


def test_buscar_produtos_catalogo_vazio():
    with patch("chat.agent.tools._carregar_produtos", return_value=[]):
        result = json.loads(buscar_produtos.invoke({"categoria": "notebook", "orcamento_max": 5000.0}))
    assert result["produtos"] == []
    assert result["origem"] == "local"


def test_buscar_produtos_orcamento_invalido():
    result = json.loads(buscar_produtos.invoke({"categoria": "notebook", "orcamento_max": float("nan")}))
    assert result["codigo"] == "invalid_argument"


def test_buscar_produtos_catalogo_malformado():
    with patch("chat.agent.tools._carregar_produtos", return_value=[{}]):
        result = json.loads(buscar_produtos.invoke({"categoria": "notebook", "orcamento_max": 5000.0}))
    assert result["codigo"] == "catalog_unavailable"


def test_buscar_produtos_fallback_malformado():
    with patch("chat.agent.tools.fetch_external_catalog", side_effect=RuntimeError("timeout")), patch(
        "chat.agent.tools._carregar_produtos", return_value=[{}]
    ):
        result = json.loads(buscar_produtos.invoke({"categoria": "notebook", "orcamento_max": 5000.0}))
    assert result["codigo"] == "catalog_unavailable"


def test_buscar_produtos_categoria_valida():
    with patch("chat.agent.tools._carregar_produtos", return_value=PRODUTOS_FIXTURE):
        result = json.loads(buscar_produtos.invoke({"categoria": "notebook", "orcamento_max": 5000.0}))
    assert len(result["produtos"]) == 1
    assert result["produtos"][0]["nome"] == "Notebook Básico"


def test_buscar_produtos_sem_resultado():
    with patch("chat.agent.tools._carregar_produtos", return_value=PRODUTOS_FIXTURE):
        result = json.loads(buscar_produtos.invoke({"categoria": "notebook", "orcamento_max": 1000.0}))
    assert result["produtos"] == []
    assert "Nenhum" in result["mensagem"]


def test_buscar_produtos_categoria_invalida():
    result = json.loads(buscar_produtos.invoke({"categoria": "", "orcamento_max": 5000.0}))
    assert result["codigo"] == "invalid_argument"


def test_tools_reject_out_of_scope_operations():
    result = json.loads(buscar_produtos.invoke({"categoria": "delete", "orcamento_max": 5000.0}))
    assert result == {"ok": False, "erro": "Parâmetro 'categoria' inválido ou ausente.", "codigo": "invalid_argument", "produtos": []}


def test_report_escapes_untrusted_content():
    result = gerar_relatorio.invoke({
        "nome": "<script>alert(1)</script>",
        "preco": 3500.0,
        "tipo": "notebook",
        "especificacoes": {"ram": "<b>8GB</b>"},
        "justificativa": "<img src=x>",
    })
    assert "<script>" not in result
    assert "&lt;script&gt;" in result
    assert "&lt;img src=x&gt;" in result


def test_buscar_produtos_orcamento_string_direto():
    from chat.agent.tools import buscar_produtos as fn
    with patch("chat.agent.tools._carregar_produtos", return_value=PRODUTOS_FIXTURE):
        raw = fn.func(categoria="notebook", orcamento_max="R$ 5.000,00")
    result = json.loads(raw)
    assert len(result["produtos"]) == 1


def test_comparar_produtos_usa_fallback_local():
    from django.test import override_settings

    with override_settings(CATALOG_API_URL="https://catalog.test"), patch(
        "chat.agent.tools.fetch_external_catalog", side_effect=RuntimeError("timeout")
    ), patch("chat.agent.tools._carregar_produtos", return_value=PRODUTOS_FIXTURE):
        result = json.loads(comparar_produtos.invoke({"produto_a_id": 1, "produto_b_id": 2}))
    assert result["origem"] == "local_fallback"
    assert result["comparacao"]["diferenca_preco"] == 3500.0


def test_comparar_produtos_encontrados():
    with patch("chat.agent.tools._carregar_produtos", return_value=PRODUTOS_FIXTURE):
        result = json.loads(comparar_produtos.invoke({"produto_a_id": 1, "produto_b_id": 2}))
    assert result["ok"] is True
    assert result["codigo"] == "ok"
    assert result["origem"] == "local"
    assert result["comparacao"]["diferenca_preco"] == 3500.0


def test_comparar_produtos_argumentos_invalidos():
    result = comparar_produtos.func(produto_a_id="1", produto_b_id=2)
    assert json.loads(result)["codigo"] == "invalid_argument"


def test_comparar_produtos_nao_encontrado():
    with patch("chat.agent.tools._carregar_produtos", return_value=PRODUTOS_FIXTURE):
        result = json.loads(comparar_produtos.invoke({"produto_a_id": 99, "produto_b_id": 1}))
    assert "erro" in result


@pytest.mark.parametrize("field", ["nome", "justificativa"])
def test_gerar_relatorio_rejeita_texto_vazio(field):
    values = {
        "nome": "Notebook Básico",
        "preco": 3500.0,
        "tipo": "notebook",
        "especificacoes": {"ram": "8GB"},
        "justificativa": "Ideal para estudos.",
    }
    values[field] = "   "
    result = json.loads(gerar_relatorio.invoke(values))
    assert result["codigo"] == "invalid_report"


def test_gerar_relatorio_formatacao():
    result = gerar_relatorio.invoke({
        "nome": "Notebook Básico",
        "preco": 3500.0,
        "tipo": "notebook",
        "especificacoes": {"ram": "8GB"},
        "justificativa": "Ideal para estudos.",
    })
    assert "Notebook Básico" in result
    assert "3,500" in result
    assert "Ajuda Tech" in result
