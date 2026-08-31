import json
from unittest.mock import patch

from chat.agent.graph import (
    _fan_out_catalog,
    _route_after_classify,
    _should_continue_gathering,
    build_graph,
)
from chat.agent.nodes import catalog_worker, consolidate_catalog, gather_needs
from chat.observability import clear_metrics, execution_context, metrics_snapshot


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


def test_build_graph_compiles():
    compiled = build_graph().compile()

    assert compiled is not None


def test_routes_classified_intents():
    assert _route_after_classify({"classified_intent": "saudacao"}) == "greet"
    assert _route_after_classify({"classified_intent": "recomendacao"}) == "recommend"
    assert _route_after_classify({"classified_intent": "dados"}) == "gather_needs"
    assert _route_after_classify({"classified_intent": "desconhecida"}) == "gather_needs"


@patch("chat.agent.nodes._call_llm", side_effect=["dados", '{"proposito": "estudos", "orcamento": 3000}', "Recomendação", "Resposta"])
@patch("chat.agent.nodes.buscar_produtos")
def test_compiled_graph_runs_complete_flow(mock_buscar_produtos, mock_call_llm):
    mock_buscar_produtos.invoke.return_value = json.dumps({"produtos": PRODUCTS})

    result = build_graph().compile().invoke({"messages": [{"role": "user", "content": "Quero estudar"}]})

    assert result["stage"] == "respond"
    assert result["products_found"]
    assert result["report"]
    assert result["messages"][-1].content == "Resposta"
    assert mock_call_llm.call_count == 4


def test_complete_flow_records_correlated_stages():
    clear_metrics()
    with execution_context("trace-graph", "run-graph"):
        with patch("chat.agent.nodes._call_llm", side_effect=["dados", '{"proposito": "estudos", "orcamento": 3000}', "Recomendação", "Resposta"]), patch("chat.agent.nodes.buscar_produtos") as buscar_produtos:
            buscar_produtos.invoke.return_value = json.dumps({"produtos": PRODUCTS})
            build_graph().compile().invoke({"messages": [{"role": "user", "content": "Quero estudar"}]})

    records = metrics_snapshot()
    assert {record["event"] for record in records} >= {"start", "complete"}
    assert {record["trace_id"] for record in records} == {"trace-graph"}
    assert {record["run_id"] for record in records} == {"run-graph"}
    assert all(record["count"] > 0 for record in records)
    clear_metrics()


def test_routes_gathering_by_required_needs():
    assert _should_continue_gathering({"user_needs": {"proposito": "estudos", "orcamento": 3000}}) == "recommend"
    assert _should_continue_gathering({"user_needs": {"proposito": "estudos"}}) == "respond"


def test_fan_out_creates_catalog_branches():
    jobs = [
        {"branch": "notebook", "categoria": "notebook", "orcamento_max": 3000},
        {"branch": "desktop", "categoria": "desktop", "orcamento_max": 3000},
    ]

    sends = _fan_out_catalog({"catalog_jobs": jobs})

    assert len(sends) == 2
    assert [send.node for send in sends] == ["catalog_worker", "catalog_worker"]
    assert [send.arg["branch_job"] for send in sends] == jobs


def test_fan_in_consolidates_products_and_errors():
    result = consolidate_catalog(
        {
            "catalog_results": [
                {"branch": "notebook", "status": "ok", "products": [{"nome": "N"}]},
                {"branch": "desktop", "status": "error", "products": [], "error": "indisponível"},
            ]
        }
    )

    assert result == {
        "products_found": [{"nome": "N"}],
        "errors": ["desktop: indisponível"],
        "stage": "catalog_consolidate",
    }


@patch("chat.agent.nodes.buscar_produtos")
def test_catalog_worker_keeps_partial_failure_as_result(mock_buscar_produtos):
    mock_buscar_produtos.invoke.side_effect = RuntimeError("catálogo indisponível")

    result = catalog_worker(
        {"branch_job": {"branch": "desktop", "categoria": "desktop", "orcamento_max": 3000}}
    )

    assert result["catalog_results"][0]["status"] == "error"
    assert result["catalog_results"][0]["products"] == []
    assert result["catalog_results"][0]["error"] == "falha ao consultar catálogo"


@patch("chat.agent.nodes._call_llm", return_value='{"orcamento": 3000}')
def test_gather_needs_preserves_existing_user_needs(mock_call_llm):
    result = gather_needs(
        {
            "messages": [{"role": "user", "content": "Meu orçamento é 3000"}],
            "user_needs": {"proposito": "estudos", "mobilidade": "alta"},
        }
    )

    assert result["user_needs"] == {
        "proposito": "estudos",
        "mobilidade": "alta",
        "orcamento": 3000,
    }
    mock_call_llm.assert_called_once()


@patch("chat.agent.nodes._call_llm", return_value='{"orcamento": 3000}')
def test_gather_needs_consumes_recovered_context(mock_call_llm):
    result = gather_needs(
        {
            "messages": [{"role": "user", "content": "Continuar"}],
            "recovered_context": {"user_needs": {"proposito": "estudos"}},
            "user_needs": {},
        }
    )

    assert result["user_needs"] == {"proposito": "estudos", "orcamento": 3000}
    prompt = mock_call_llm.call_args.args[0][0]["content"]
    assert "estudos" in prompt
