import json
from unittest.mock import patch

import pytest
from django.urls import reverse

import chat.agent.nodes


PRODUCTS = [
    {
        "id": 1,
        "nome": "Notebook Estudo",
        "tipo": "notebook",
        "preco": 3000.0,
        "especificacoes": {"ram": "8GB"},
        "indicado_para": ["estudos"],
        "mobilidade": "alta",
    }
]


def post_agent(client, message):
    return client.post(
        reverse("chat:agent_send_message"),
        data=json.dumps({"message": message}),
        content_type="application/json",
    )


@pytest.mark.django_db
def test_agent_recommendation_persists_session_across_requests(client):
    catalog_response = json.dumps({"produtos": PRODUCTS})
    with (
        patch(
            "chat.services.OpenRouterClient.chat_completion",
            side_effect=[
                "dados",
                '{"proposito": "estudos", "orcamento": 3000, "mobilidade": "alta"}',
                "Recomendação baseada no catálogo.",
                "Resposta simples.",
                "recomendacao",
                "Outra recomendação baseada no catálogo.",
                "Outra resposta simples.",
            ],
        ) as chat_completion,
        patch("chat.agent.nodes.buscar_produtos") as buscar_produtos,
    ):
        buscar_produtos.invoke.return_value = catalog_response

        first = post_agent(client, "Quero computador para estudar")
        second = post_agent(client, "Também quero mobilidade")

    assert first.status_code == 200
    assert second.status_code == 200
    assert json.loads(first.content)["reply"] == "Resposta simples."
    assert json.loads(second.content)["reply"] == "Outra resposta simples."
    assert chat_completion.call_count == 7
    assert buscar_produtos.invoke.call_count == 4

    history = client.session["chat_history"]
    assert [item["role"] for item in history] == ["user", "assistant", "user", "assistant"]
    assert [item["content"] for item in history] == [
        "Quero computador para estudar",
        "Resposta simples.",
        "Também quero mobilidade",
        "Outra resposta simples.",
    ]
    assert client.session["thread_id"]
    assert client.session["run_id"]


@pytest.mark.django_db
def test_agent_catalog_failure_returns_safe_response_and_persists_session(client):
    with (
        patch(
            "chat.services.OpenRouterClient.chat_completion",
            side_effect=[
                "dados",
                '{"proposito": "estudos", "orcamento": 3000, "mobilidade": "alta"}',
                "Recomendação segura sem catálogo.",
                "Resposta segura sem catálogo.",
            ],
        ) as chat_completion,
        patch("chat.agent.nodes.buscar_produtos") as buscar_produtos,
    ):
        buscar_produtos.invoke.side_effect = RuntimeError("catalog unavailable")

        response = post_agent(client, "Quero notebook para estudar por até 3000")

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "reply": "Recomendação segura sem catálogo.",
        "report": "Nenhum produto encontrado para gerar relatório.",
    }
    assert chat_completion.call_count == 3
    assert buscar_produtos.invoke.call_count == 2
    assert client.session["chat_history"] == [
        {"role": "user", "content": "Quero notebook para estudar por até 3000"},
        {"role": "assistant", "content": "Recomendação segura sem catálogo."},
    ]
