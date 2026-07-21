"""Testes dos nós do agente LangGraph."""

from unittest.mock import patch

from django.conf import settings

settings.LLM_API_KEY = "test-key"

from chat.agent.nodes import _call_llm, report


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


@patch("chat.agent.nodes.OpenRouterClient")
def test_call_llm_returns_fallback_for_safety_response(mock_client):
    mock_client.return_value.chat_completion.return_value = "content filtered"

    result = _call_llm([{"role": "user", "content": "teste"}])

    assert result == "Desculpe, não consegui processar sua mensagem. Pode reformular?"


@patch("chat.agent.nodes.OpenRouterClient")
def test_call_llm_returns_fallback_for_short_response(mock_client):
    mock_client.return_value.chat_completion.return_value = "ok"

    result = _call_llm([{"role": "user", "content": "teste"}])

    assert result == "Desculpe, não consegui processar sua mensagem. Pode reformular?"
