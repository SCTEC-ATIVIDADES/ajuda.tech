"""
Nós do grafo LangGraph do assistente Herbert.

Cada nó é uma função que recebe o estado atual e retorna um dicionário
com as atualizações a serem aplicadas ao estado.
"""

import json
import logging
import re

from chat.services import OpenRouterClient
from chat.agent.state import AgentState
from chat.agent.tools import buscar_produtos, comparar_produtos, gerar_relatorio
from chat.prompts import (
    build_agent_classification_prompt,
    build_agent_context_prompt,
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


def _call_llm(messages: list[dict]) -> str:
    """Chama o LLM via OpenRouterClient e retorna a resposta."""
    logger.debug("LLM call: %s", messages[-1]["content"][:200])
    response = OpenRouterClient().chat_completion(messages)
    logger.debug("LLM response (first 200): %s", response[:200])

    if response.strip().lower() in _SAFETY_RESPONSES or len(response.strip()) < 5:
        logger.warning("Resposta de safety filter detectada: %s", response[:100])
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
    history = []
    for msg in state["messages"]:
        role = _message_role(msg)
        content = _message_text(msg)
        history.append({"role": role, "content": content})

    current_needs = state.get("user_needs", {})

    prompt = build_agent_needs_prompt(current_needs, history)

    response = _call_llm([{"role": "user", "content": prompt}])

    try:
        clean_response = _strip_cot(response).strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        needs = json.loads(clean_response)
    except (json.JSONDecodeError, ValueError):
        needs = current_needs

    merged = {**current_needs, **{k: v for k, v in needs.items() if v is not None}}

    return {
        "user_needs": merged,
        "stage": "gather",
    }


def extract_context(state: AgentState) -> dict:
    """Nó de extração — valida e organiza os dados coletados."""
    needs = state.get("user_needs", {})

    prompt = build_agent_context_prompt(needs)

    response = _call_llm([{"role": "user", "content": prompt}])

    try:
        clean_response = _strip_cot(response).strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        result = json.loads(clean_response)
    except (json.JSONDecodeError, ValueError):
        result = {"suficiente": bool(needs.get("proposito") and needs.get("orcamento")),
                  "mensagem_confirmacao": "", "faltando": []}

    return {
        "stage": "extract",
        "recommendation": result.get("mensagem_confirmacao", ""),
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


def recommend(state: AgentState) -> dict:
    """Nó de recomendação — busca produtos e gera recomendação."""
    needs = state.get("user_needs", {})
    proposito = needs.get("proposito", "uso geral")
    orcamento = _parse_orcamento(needs.get("orcamento"), 5000.0)
    mobilidade = _parse_mobilidade(needs.get("mobilidade"), "media")
    if mobilidade == "alta":
        categoria = "notebook"
    elif mobilidade == "baixa":
        categoria = "desktop"
    else:
        categoria = "notebook"

    produtos_result = buscar_produtos.invoke({"categoria": categoria, "orcamento_max": orcamento})
    produtos_data = json.loads(produtos_result)
    produtos = produtos_data.get("produtos", [])

    if not produtos and categoria == "notebook":
        produtos_result = buscar_produtos.invoke({"categoria": "desktop", "orcamento_max": orcamento})
        produtos_data = json.loads(produtos_result)
        produtos = produtos_data.get("produtos", [])

    logger.info("RECOMMEND: cat=%s orc=%.0f prods=%d", categoria, orcamento, len(produtos))
    for p in produtos:
        logger.info("  -> %s R$%.2f", p["nome"], p["preco"])

    if not produtos:
        return {
            "products_found": [],
            "recommendation": "No momento não temos um produto ideal para o seu perfil no nosso catálogo. Posso buscar uma opção com orçamento um pouco maior ou outro tipo de computador.",
            "stage": "recommend",
        }

    prompt = build_agent_recommendation_prompt(proposito, orcamento, mobilidade, produtos)
    response = _call_llm([{"role": "user", "content": prompt}])

    return {
        "products_found": produtos,
        "recommendation": _strip_cot(response),
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

    relatorio = gerar_relatorio.invoke({
        "nome": melhor_produto["nome"],
        "preco": melhor_produto["preco"],
        "tipo": melhor_produto["tipo"],
        "especificacoes": melhor_produto["especificacoes"],
        "justificativa": f"Indicado para {', '.join(melhor_produto['indicado_para'])}. "
                         f"Mobilidade: {melhor_produto['mobilidade']}.",
    })

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
