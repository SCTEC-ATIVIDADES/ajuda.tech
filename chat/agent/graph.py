"""
Grafo LangGraph do assistente Herbert.

Define o fluxo completo do agente com nós, edges e roteamento condicional.
"""

from langgraph.graph import END, StateGraph
from langgraph.types import Send

from chat.agent.nodes import (
    classify_msg,
    greet,
    gather_needs,
    prepare_catalog,
    catalog_worker,
    consolidate_catalog,
    compare_catalog_products,
    recommend,
    report,
    respond,
)
from chat.agent.state import AgentState
from chat.observability import stage


def _route_after_classify(state: AgentState) -> str:
    """Roteamento condicional após classificação da mensagem."""
    intent = state.get("classified_intent", "dados")

    if intent == "saudacao":
        return "greet"
    elif intent == "recomendacao":
        return "recommend"
    else:
        return "gather_needs"


def _should_continue_gathering(state: AgentState) -> str:
    """Decide se continua coletando dados ou vai direto para recomendação."""
    needs = state.get("user_needs", {})
    has_purpose = bool(needs.get("proposito"))
    has_budget = bool(needs.get("orcamento"))

    if has_purpose and has_budget:
        return "recommend"
    return "respond"


def _fan_out_catalog(state: AgentState) -> list[Send]:
    context = {key: state[key] for key in ("trace_id", "run_id", "deadline") if key in state}
    return [Send("catalog_worker", {"branch_job": {**job, **context}}) for job in state.get("catalog_jobs", [])]


def _instrument(name, node):
    def wrapped(state):
        with stage(name):
            return node(state)
    return wrapped


def build_graph() -> StateGraph:
    """Monta fluxo com roteamento, fan-out/fan-in e parada segura."""
    graph = StateGraph(AgentState)
    for name, node in {
        "classify_msg": classify_msg,
        "greet": greet,
        "gather_needs": gather_needs,
        "prepare_catalog": prepare_catalog,
        "catalog_worker": catalog_worker,
        "consolidate_catalog": consolidate_catalog,
        "compare_catalog_products": compare_catalog_products,
        "recommend": recommend,
        "report": report,
        "respond": respond,
    }.items():
        graph.add_node(name, _instrument(name, node))

    graph.set_entry_point("classify_msg")
    graph.add_conditional_edges("classify_msg", _route_after_classify, {
        "greet": "greet", "gather_needs": "gather_needs", "recommend": "prepare_catalog",
    })
    graph.add_edge("greet", END)
    graph.add_conditional_edges("gather_needs", _should_continue_gathering, {
        "recommend": "prepare_catalog", "respond": "respond",
    })
    graph.add_conditional_edges("prepare_catalog", _fan_out_catalog)
    graph.add_edge("catalog_worker", "consolidate_catalog")
    graph.add_edge("consolidate_catalog", "compare_catalog_products")
    graph.add_edge("compare_catalog_products", "recommend")
    graph.add_edge("recommend", "report")
    graph.add_edge("report", "respond")
    graph.add_edge("respond", END)
    return graph


agent_graph = build_graph().compile()
