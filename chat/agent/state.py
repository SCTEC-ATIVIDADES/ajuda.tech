"""Contratos tipados do estado compartilhado pelo agente LangGraph."""

from operator import add
from typing import Annotated, TypedDict

from langgraph.graph import add_messages


class Product(TypedDict, total=False):
    id: int
    nome: str
    tipo: str
    preco: float
    especificacoes: dict[str, str]
    indicado_para: list[str]
    mobilidade: str


class CatalogJob(TypedDict, total=False):
    branch: str
    categoria: str
    orcamento_max: float
    trace_id: str
    run_id: str
    deadline: float


class CatalogBranchResult(TypedDict, total=False):
    branch: str
    categoria: str
    status: str
    products: list[Product]
    error: str
    duration_ms: float


class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    thread_id: str
    run_id: str
    trace_id: str
    deadline: float
    recovered_context: dict[str, object]
    user_needs: dict[str, object]
    products_found: list[Product]
    catalog_jobs: list[CatalogJob]
    branch_job: CatalogJob
    catalog_results: Annotated[list[CatalogBranchResult], add]
    errors: Annotated[list[str], add]
    stage: str
    recommendation: str
    report: str
    comparison: str
    classified_intent: str
