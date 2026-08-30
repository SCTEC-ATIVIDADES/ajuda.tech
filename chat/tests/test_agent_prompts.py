"""Testes dos builders de prompt do agente."""

from chat.prompts import (
    build_agent_classification_prompt,
    build_agent_followup_prompt,
    build_agent_greeting_prompt,
    build_agent_needs_prompt,
    build_agent_recommendation_prompt,
    build_agent_response_prompt,
)


def test_build_agent_classification_prompt_returns_string():
    result = build_agent_classification_prompt("oi")
    assert isinstance(result, str)
    assert "oi" in result


def test_build_agent_greeting_prompt_returns_string():
    result = build_agent_greeting_prompt()
    assert isinstance(result, str)
    assert len(result) > 0


def test_build_agent_needs_prompt_returns_string():
    result = build_agent_needs_prompt({}, [{"role": "user", "content": "oi"}])
    assert isinstance(result, str)
    assert len(result) > 0



def test_build_agent_recommendation_prompt_returns_string():
    result = build_agent_recommendation_prompt("estudos", 5000.0, "alta", [])
    assert isinstance(result, str)
    assert "5000" in result


def test_build_agent_followup_prompt_returns_string():
    result = build_agent_followup_prompt("Qual seu orçamento?")
    assert isinstance(result, str)
    assert "orçamento" in result


def test_build_agent_response_prompt_returns_string():
    result = build_agent_response_prompt(" recomendação", " relatório")
    assert isinstance(result, str)
    assert "recomendação" in result
