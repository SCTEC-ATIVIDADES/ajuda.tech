"""
Estado compartilhado do agente LangGraph.

Define o TypedDict que representa o estado que flui entre os nós do grafo.
"""

from typing import TypedDict

from langgraph.graph import add_messages
from typing import Annotated


class AgentState(TypedDict):
    """
    Estado compartilhado entre todos os nós do grafo LangGraph.

    Attributes
    ----------
    messages : list
        Histórico de mensagens da conversa (user + assistant).
    user_needs : dict
        Necessidades extraídas do usuário:
        - proposito: str (ex: "estudos", "games", "escritorio")
        - orcamento: float (valor máximo em reais)
        - mobilidade: str ("alta", "media", "baixa")
        - prioridades: list[str] (ex: ["desempenho", "preco", "portabilidade"])
    products_found : list
        Produtos encontrados pela tool buscar_produtos.
    stage : str
        Etapa atual do fluxo: classify | greet | gather | extract | recommend | report | respond
    recommendation : str
        Texto da recomendação gerada pelo agente.
    report : str
        Relatório estruturado em Markdown da recomendação.
    classified_intent : str
        Intenção classificada: saudacao | pergunta | dados | recomendacao
    """
    messages: Annotated[list, add_messages]
    user_needs: dict
    products_found: list
    stage: str
    recommendation: str
    report: str
    classified_intent: str
