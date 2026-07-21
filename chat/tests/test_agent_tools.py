"""Testes das tools do agente LangGraph."""

import json
from pathlib import Path
from unittest.mock import patch, mock_open

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
    assert "erro" in result


def test_buscar_produtos_orcamento_string_direto():
    from chat.agent.tools import buscar_produtos as fn
    with patch("chat.agent.tools._carregar_produtos", return_value=PRODUTOS_FIXTURE):
        raw = fn.func(categoria="notebook", orcamento_max="R$ 5.000,00")
    result = json.loads(raw)
    assert len(result["produtos"]) == 1


def test_comparar_produtos_encontrados():
    with patch("chat.agent.tools._carregar_produtos", return_value=PRODUTOS_FIXTURE):
        result = json.loads(comparar_produtos.invoke({"produto_a_id": 1, "produto_b_id": 2}))
    assert "diferenca_preco" in result
    assert result["diferenca_preco"] == 3500.0


def test_comparar_produtos_nao_encontrado():
    with patch("chat.agent.tools._carregar_produtos", return_value=PRODUTOS_FIXTURE):
        result = json.loads(comparar_produtos.invoke({"produto_a_id": 99, "produto_b_id": 1}))
    assert "erro" in result


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
