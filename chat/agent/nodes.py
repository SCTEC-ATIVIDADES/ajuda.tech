"""
Nós do grafo LangGraph do assistente Herbert.

Cada nó é uma função que recebe o estado atual e retorna um dicionário
com as atualizações a serem aplicadas ao estado.
"""

import json
import logging
import math
import re
import time

from chat.services import OpenRouterClient
from chat.agent.state import AgentState, CatalogBranchResult, CatalogJob
from chat.agent.tools import buscar_produtos, comparar_produtos, gerar_relatorio
from chat.observability import ExecutionTimeout, current_context, emit_event, execution_context, stage
from chat.prompts import (
    build_agent_classification_prompt,
    build_agent_greeting_prompt,
    build_agent_needs_prompt,
    build_agent_recommendation_prompt,
    build_agent_response_prompt,
)

logger = logging.getLogger(__name__)

_COT_TAG_RE = re.compile(
    r"<(?:thinking|reasoning|scratchpad|thought|analysis)>.*?"
    r"</(?:thinking|reasoning|scratchpad|thought|analysis)>",
    re.DOTALL | re.IGNORECASE,
)
_PT_PARA_RE = re.compile(
    r"^(?:Olá|Oi|Claro|Sim|Não|Para |Você |Qual |Como |O que |Pois "
    r"|Agora |Então |Com base|De acordo|Como posso|Vou |Gostaria "
    r"|Bom dia|Boa tarde|Boa noite|Poderia |Podemos |Vamos )",
    re.IGNORECASE,
)


def _strip_cot(text: str) -> str:
    """Remove chain-of-thought antes da resposta ao usuário.

    Detecta o padrão CoT (em inglês) seguido de resposta (em português)
    e retorna apenas o bloco em português.
    """
    cleaned = _COT_TAG_RE.sub("", text).strip()

    blocks = [b.strip() for b in re.split(r"\n\s*\n", cleaned) if b.strip()]
    if not blocks:
        return text.strip()

    for block in blocks:
        if _PT_PARA_RE.search(block[:80]):
            return block

    single_lines = [b for b in blocks if "\n" not in b]
    if single_lines:
        return single_lines[-1]

    return blocks[-1] if blocks else text.strip()


_SAFETY_RESPONSES = {
    "user safety: safe",
    "user safety: unsafe",
    "safety",
    "content filtered",
    "blocked",
}
_MAX_TEXT = 1000
_ALLOWED_NEEDS = {"proposito", "orcamento", "mobilidade", "prioridades"}
_INJECTION_RE = re.compile(
    r"\b(?:ignore|disregard|forget|reveal|show|system prompt|instruções? anteriores?|ignore as instruções)\b",
    re.IGNORECASE,
)


def _sanitize_text(value, limit: int = _MAX_TEXT) -> str:
    if not isinstance(value, str):
        return ""
    text = value.strip()[:limit]
    return "[conteúdo removido]" if _INJECTION_RE.search(text) else text


def _sanitize_needs(needs) -> dict:
    if not isinstance(needs, dict):
        return {}
    clean = {}
    for key, value in needs.items():
        if key not in _ALLOWED_NEEDS or value is None:
            continue
        if key == "orcamento":
            parsed = _parse_orcamento(value, -1)
            if math.isfinite(parsed) and parsed >= 0:
                clean[key] = parsed
        elif key == "prioridades" and isinstance(value, list):
            clean[key] = [_sanitize_text(item, 120) for item in value if isinstance(item, str)][:10]
        elif isinstance(value, str):
            clean[key] = _sanitize_text(value)
    return clean


def _safe_history(messages: list[dict]) -> list[dict]:
    return [
        {"role": "user" if item["role"] == "user" else "assistant", "content": _sanitize_text(item["content"])}
        for item in messages[-20:]
    ]


def _call_llm(messages: list[dict]) -> str:
    """Chama o LLM via OpenRouterClient e retorna a resposta."""
    logger.debug("LLM call metadata: messages=%d", len(messages))
    with stage("llm"):
        response = OpenRouterClient().chat_completion(messages)
    logger.debug("LLM response metadata: chars=%d", len(response))

    if response.strip().lower() in _SAFETY_RESPONSES or len(response.strip()) < 5:
        logger.warning("Fallback aplicado para resposta do LLM: chars=%d", len(response.strip()))
        emit_event("llm", "fallback", "fallback")
        return "Desculpe, não consegui processar sua mensagem. Pode reformular?"

    return response


def _message_text(message) -> str:
    """Extrai o texto de uma mensagem, aceitando dict ou objeto BaseMessage."""
    if isinstance(message, dict):
        return message.get("content", "")
    return getattr(message, "content", "")


def classify_msg(state: AgentState) -> dict:
    """
    Classifica a intenção da última mensagem do usuário.

    Determina se é: saudacao, pergunta, dados, recomendacao.
    """
    user_text = _message_text(state["messages"][-1])

    prompt = build_agent_classification_prompt(user_text)

    response = _call_llm([{"role": "user", "content": prompt}])
    intent = _strip_cot(response).strip().lower()

    valid_intents = {"saudacao", "dados", "pergunta", "recomendacao"}
    if intent not in valid_intents:
        intent = "dados"

    return {
        "classified_intent": intent,
        "stage": "classify",
    }


def greet(state: AgentState) -> dict:
    """Nó de saudação — responde ao cumprimento do usuário."""
    prompt = build_agent_greeting_prompt()

    response = _call_llm([{"role": "user", "content": prompt}])

    return {
        "messages": [{"role": "assistant", "content": _strip_cot(response)}],
        "stage": "greet",
    }


def _message_role(message) -> str:
    """Extrai o papel de uma mensagem, aceitando dict ou objeto BaseMessage."""
    if isinstance(message, dict):
        return message.get("role", "assistant")
    msg_type = getattr(message, "type", "")
    if msg_type in {"human", "user"}:
        return "user"
    return "assistant"


def gather_needs(state: AgentState) -> dict:
    """Nó de coleta — extrai necessidades do usuário a partir da conversa."""
    history = _safe_history([
        {"role": _message_role(msg), "content": _message_text(msg)}
        for msg in state["messages"]
    ])

    recovered_context = state.get("recovered_context", {})
    recovered_needs = recovered_context.get("user_needs", {}) if isinstance(recovered_context, dict) else {}
    current_needs = _sanitize_needs(recovered_needs)
    current_needs.update(_sanitize_needs(state.get("user_needs", {})))

    prompt = build_agent_needs_prompt(current_needs, history)

    response = _call_llm([{"role": "user", "content": prompt}])

    try:
        clean_response = _strip_cot(response).strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        needs = _sanitize_needs(json.loads(clean_response))
    except (json.JSONDecodeError, ValueError):
        needs = current_needs

    merged = {**current_needs, **needs}

    return {
        "user_needs": merged,
        "stage": "gather",
    }



def _parse_orcamento(value, default: float = 5000.0) -> float:
    """Converte orçamento para float, limpando strings como 'R$ 5.000,00'."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(cleaned)
        except (TypeError, ValueError):
            return default
    return default


def _parse_mobilidade(value, default: str = "media") -> str:
    """Normaliza mobilidade para 'alta', 'media' ou 'baixa'."""
    if not value:
        return default
    text = str(value).lower().strip()
    if text in {"alta", "máxima", "muita", "total"}:
        return "alta"
    if text in {"baixa", "mínima", "pouca", "nenhuma"}:
        return "baixa"
    if text in {"media", "média", "moderada"}:
        return "media"
    return default


def prepare_catalog(state: AgentState) -> dict:
    """Cria dois trabalhos independentes de catálogo."""
    needs = state.get("user_needs", {})
    budget = _parse_orcamento(needs.get("orcamento"), 5000.0)
    mobility = _parse_mobilidade(needs.get("mobilidade"), "media")
    primary = "desktop" if mobility == "baixa" else "notebook"
    categories = [primary, "desktop" if primary == "notebook" else "notebook"]
    return {
        "catalog_jobs": [
            {"branch": category, "categoria": category, "orcamento_max": budget}
            for category in categories
        ],
        "stage": "catalog_prepare",
    }


def catalog_worker(state: AgentState) -> dict:
    """Executa um trabalho de catálogo sem derrubar outros ramos."""
    job: CatalogJob = state["branch_job"]
    started = time.perf_counter()
    parent = current_context()
    trace_id = job.get("trace_id") or parent.get("trace_id")
    run_id = job.get("run_id") or parent.get("run_id")
    deadline = job.get("deadline") or parent.get("deadline")
    timeout = None
    if deadline:
        timeout = max(deadline - time.monotonic(), 0.001)
    with execution_context(trace_id, run_id, timeout):
        emit_event(f"catalog.{job['branch']}", "start", "started")
        try:
            data = json.loads(buscar_produtos.invoke({
                "categoria": job["categoria"],
                "orcamento_max": job["orcamento_max"],
            }))
            products = data.get("produtos", [])
            result: CatalogBranchResult = {
                "branch": job["branch"],
                "categoria": job["categoria"],
                "status": "ok",
                "products": products,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            }
            emit_event(f"catalog.{job['branch']}", "complete", "ok", duration_ms=result["duration_ms"])
        except ExecutionTimeout:
            raise
        except Exception as exc:
            result = {
                "branch": job["branch"],
                "categoria": job["categoria"],
                "status": "error",
                "products": [],
                "error": "falha ao consultar catálogo",
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            }
            emit_event(f"catalog.{job['branch']}", "complete", "error", duration_ms=result["duration_ms"], error=exc)
        logger.info("CATALOG branch=%s status=%s duration_ms=%.2f count=%d",
                    result["branch"], result["status"], result["duration_ms"],
                    len(result.get("products", [])))
        return {"catalog_results": [result]}


def consolidate_catalog(state: AgentState) -> dict:
    """Consolida resultados saudáveis e registra falhas parciais."""
    products = []
    errors = []
    for result in state.get("catalog_results", []):
        products.extend(result.get("products", []))
        if result.get("status") == "error":
            errors.append(f"{result['branch']}: {result.get('error', 'falha controlada')}"[:200])
    emit_event(
        "catalog.consolidate",
        "complete",
        "partial" if errors and products else "error" if errors else "ok",
        duration_ms=0,
        error=RuntimeError("falha parcial") if errors else None,
    )
    return {"products_found": products, "errors": errors, "stage": "catalog_consolidate"}


def compare_catalog_products(state: AgentState) -> dict:
    """Demonstra comparação quando catálogo oferece pelo menos dois produtos."""
    products = state.get("products_found", [])
    if len(products) < 2 or "id" not in products[0] or "id" not in products[1]:
        emit_event("catalog.compare", "complete", "skipped")
        return {"comparison": "", "stage": "compare"}
    try:
        comparison = comparar_produtos.invoke({"produto_a_id": products[0]["id"], "produto_b_id": products[1]["id"]})
        emit_event("catalog.compare", "complete", "ok")
    except Exception as exc:
        logger.warning("CATALOG comparison failed")
        emit_event("catalog.compare", "complete", "error", error=exc)
        comparison = ""
    return {"comparison": comparison, "stage": "compare"}


def recommend(state: AgentState) -> dict:
    """Gera recomendação usando catálogo já consolidado."""
    needs = state.get("user_needs", {})
    products = state.get("products_found", [])
    budget = _parse_orcamento(needs.get("orcamento"), 5000.0)
    mobility = _parse_mobilidade(needs.get("mobilidade"), "media")
    if not products:
        return {
            "recommendation": "No momento não temos um produto ideal para o seu perfil no nosso catálogo. Posso buscar uma opção com orçamento um pouco maior ou outro tipo de computador.",
            "stage": "recommend",
        }
    prompt = build_agent_recommendation_prompt(
        needs.get("proposito", "uso geral"), budget, mobility, products
    )
    comparison = state.get("comparison", "")
    if comparison:
        prompt += f"\n\nComparação validada do catálogo:\n{comparison}"
    return {
        "recommendation": _strip_cot(_call_llm([{"role": "user", "content": prompt}])),
        "stage": "recommend",
    }


def report(state: AgentState) -> dict:
    """Nó de relatório — gera relatório estruturado da recomendação."""
    produtos = state.get("products_found", [])
    needs = state.get("user_needs", {})

    if not produtos:
        return {
            "report": "Nenhum produto encontrado para gerar relatório.",
            "stage": "report",
        }

    orcamento = _parse_orcamento(needs.get("orcamento"), 5000.0)
    melhor_produto = min(produtos, key=lambda p: abs(p["preco"] - orcamento))

    try:
        relatorio = gerar_relatorio.invoke({
        "nome": melhor_produto["nome"],
        "preco": melhor_produto["preco"],
        "tipo": melhor_produto["tipo"],
        "especificacoes": melhor_produto["especificacoes"],
            "justificativa": f"Indicado para {', '.join(melhor_produto['indicado_para'])}. "
                             f"Mobilidade: {melhor_produto['mobilidade']}.",
        })
        emit_event("report", "complete", "ok")
    except Exception as exc:
        emit_event("report", "complete", "error", error=exc)
        relatorio = "Relatório técnico indisponível no momento."

    return {
        "report": relatorio,
        "stage": "report",
    }


def _next_missing_question(needs: dict) -> str:
    """Retorna a próxima pergunta a fazer quando faltam dados obrigatórios."""
    if not needs.get("proposito"):
        return (
            "Para que você vai usar o computador? Pode ser estudos, trabalho, "
            "jogos, edição de fotos/vídeos ou uso básico como navegar na internet."
        )
    if not needs.get("orcamento"):
        return "Qual é o seu orçamento aproximado?"
    if not needs.get("mobilidade"):
        return "Você precisa levar o computador para fora de casa com frequência?"
    return "Tem alguma prioridade especial, como tela grande, bateria longa ou durabilidade?"


def respond(state: AgentState) -> dict:
    """Nó de resposta final — monta a resposta completa para o usuário."""
    needs = state.get("user_needs", {})
    recommendation = state.get("recommendation", "")
    report_text = state.get("report", "")

    if not needs.get("proposito") or not needs.get("orcamento"):
        question = _next_missing_question(needs)
        return {"messages": [{"role": "assistant", "content": question}], "stage": "respond"}
    prompt = build_agent_response_prompt(recommendation, report_text)

    response = _call_llm([{"role": "user", "content": prompt}])

    return {
        "messages": [{"role": "assistant", "content": _strip_cot(response)}],
        "stage": "respond",
    }
