"""
Grafo LangGraph do assistente Herbert.

Define o fluxo completo do agente com nós, edges e roteamento condicional.
"""

from langgraph.graph import END, START, StateGraph

from chat.agent.nodes import (
    classify_msg,
    greet,
    gather_needs,
    recommend,
    report,
    respond,
)
from chat.agent.state import AgentState


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


def build_graph() -> StateGraph:
    """
    Monta o grafo LangGraph com todos os nós e conexões.

    Fluxo otimizado (mínimo de chamadas LLM):
        START → classify_msg → [greet | gather_needs | recommend]
        gather_needs → [recommend | respond]
        recommend → report → respond → END
    """
    graph = StateGraph(AgentState)

    graph.add_node("classify_msg", classify_msg)
    graph.add_node("greet", greet)
    graph.add_node("gather_needs", gather_needs)
    graph.add_node("recommend", recommend)
    graph.add_node("report", report)
    graph.add_node("respond", respond)

    graph.set_entry_point("classify_msg")

    graph.add_conditional_edges(
        "classify_msg",
        _route_after_classify,
        {
            "greet": "greet",
            "gather_needs": "gather_needs",
            "recommend": "recommend",
        },
    )

    graph.add_edge("greet", END)

    graph.add_conditional_edges(
        "gather_needs",
        _should_continue_gathering,
        {
            "recommend": "recommend",
            "respond": "respond",
        },
    )

    graph.add_edge("recommend", "report")
    graph.add_edge("report", "respond")
    graph.add_edge("respond", END)

    return graph


agent_graph = build_graph().compile()
