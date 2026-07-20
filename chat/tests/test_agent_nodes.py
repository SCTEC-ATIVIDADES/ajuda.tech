"""Testes dos nós do agente LangGraph."""

from unittest.mock import patch

from django.conf import settings

settings.LLM_API_KEY = "test-key"

from chat.agent.nodes import report


@patch("chat.agent.nodes.gerar_relatorio")
def test_report_accepts_string_budget(mock_gerar_relatorio):
    mock_gerar_relatorio.invoke.return_value = "Relatório gerado"

    state = {
        "products_found": [
            {
                "nome": "Notebook Ideal",
                "preco": 4900.0,
                "tipo": "notebook",
                "especificacoes": {"ram": "16GB"},
                "indicado_para": ["estudos"],
                "mobilidade": "alta",
            },
            {
                "nome": "Notebook Premium",
                "preco": 6200.0,
                "tipo": "notebook",
                "especificacoes": {"ram": "32GB"},
                "indicado_para": ["edição"],
                "mobilidade": "alta",
            },
        ],
        "user_needs": {"orcamento": "R$ 5.000,00"},
    }

    result = report(state)

    assert result == {"report": "Relatório gerado", "stage": "report"}
    assert mock_gerar_relatorio.invoke.call_args.args[0]["nome"] == "Notebook Ideal"
