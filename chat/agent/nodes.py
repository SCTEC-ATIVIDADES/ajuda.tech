"""
Nós do grafo LangGraph do assistente Herbert.

Cada nó é uma função que recebe o estado atual e retorna um dicionário
com as atualizações a serem aplicadas ao estado.
"""

import json
import logging

from chat.services import OpenRouterClient
from chat.agent.state import AgentState
from chat.agent.tools import buscar_produtos, comparar_produtos, gerar_relatorio

logger = logging.getLogger(__name__)

_client = OpenRouterClient()


def _call_llm(messages: list[dict]) -> str:
    """Chama o LLM via OpenRouterClient e retorna a resposta."""
    return _client.chat_completion(messages)


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

    prompt = f"""Classifique a mensagem do usuário em UMA das categorias abaixo:
- saudacao: cumprimentos, "oi", "olá", "bom dia", etc.
- dados: o usuário está fornecendo informações (propósito, orçamento, mobilidade)
- pergunta: o usuário quer saber algo sobre computadores, especificações, diferenças
- recomendacao: o usuário pede uma recomendação ou sugestão de produto

Mensagem do usuário: "{user_text}"

Responda APENAS com a categoria (uma palavra)."""

    response = _call_llm([{"role": "user", "content": prompt}])
    intent = response.strip().lower()

    valid_intents = {"saudacao", "dados", "pergunta", "recomendacao"}
    if intent not in valid_intents:
        intent = "dados"

    return {
        "classified_intent": intent,
        "stage": "classify",
    }


def greet(state: AgentState) -> dict:
    """Nó de saudação — responde ao cumprimento do usuário."""
    prompt = """Você é Herbert, assistente da Ajuda Tech.
O usuário acabou de cumprimentar. Responda de forma breve e amigável (1-2 frases),
diga que você ajuda a escolher computadores e pergunte como pode ajudar."""

    response = _call_llm([{"role": "user", "content": prompt}])

    return {
        "messages": [{"role": "assistant", "content": response}],
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

    prompt = f"""Você é Herbert, assistente da Ajuda Tech.

Analise a conversa abaixo e extraia as necessidades do usuário.
Necessidades conhecidas até agora: {json.dumps(current_needs, ensure_ascii=False)}

Conversa:
{json.dumps(history, ensure_ascii=False, indent=2)}

Extraia e retorne um JSON com as seguintes chaves (preencha o que conseguir):
{{
  "proposito": "para que o computador será usado (ex: estudos, games, escritório)",
  "orcamento": valor numérico máximo em reais (ou null se não informado),
  "mobilidade": "alta", "media" ou "baixa" (ou null se não informado),
  "prioridades": ["lista", "de", "prioridades"]
}}

Se o usuário não forneceu uma informação ainda, deixe null.
Retorne APENAS o JSON, sem texto adicional."""

    response = _call_llm([{"role": "user", "content": prompt}])

    try:
        clean_response = response.strip()
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

    prompt = f"""Você é Herbert, assistente da Ajuda Tech.

Analise as necessidades coletadas do usuário e confirme se estão suficientes
para fazer uma recomendação:

{json.dumps(needs, ensure_ascii=False, indent=2)}

Necessidades mínimas para recomendar:
- propósito de uso (obrigatório)
- orçamento ou faixa de preço (obrigatório)

Responda um JSON:
{{
  "suficiente": true/false,
  "mensagem_confirmacao": "resumo do que entendeu do usuário",
  "faltando": ["lista de informações faltantes"]
}}

Retorne APENAS o JSON."""

    response = _call_llm([{"role": "user", "content": prompt}])

    try:
        clean_response = response.strip()
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

    prompt = f"""Você é Herbert, assistente da Ajuda Tech.

Necessidades do usuário:
- Propósito: {proposito}
- Orçamento: R$ {orcamento}
- Mobilidade: {mobilidade}

Produtos disponíveis no catálogo:
{json.dumps(produtos, ensure_ascii=False, indent=2)}

Com base nas necessidades e produtos disponíveis, gere uma recomendação clara
e objetiva em linguagem simples (máximo 3 frases).
Explique por que o produto recomendado atende as necessidades.

Se nenhum produto se encaixar, diga que não encontrou algo adequado e sugira
aumentar o orçamento ou mudar os critérios.

Retorne apenas o texto da recomendação."""

    response = _call_llm([{"role": "user", "content": prompt}])

    return {
        "products_found": produtos,
        "recommendation": response,
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

    melhor_produto = min(produtos, key=lambda p: abs(p["preco"] - needs.get("orcamento", 5000)))

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


def respond(state: AgentState) -> dict:
    """Nó de resposta final — monta a resposta completa para o usuário."""
    needs = state.get("user_needs", {})
    recommendation = state.get("recommendation", "")
    report_text = state.get("report", "")

    if not needs.get("proposito") or not needs.get("orcamento"):
        faltando = []
        if not needs.get("proposito"):
            faltando.append("para que você vai usar o computador (ex: estudos, trabalho, jogos)")
        if not needs.get("orcamento"):
            faltando.append("qual é o seu orçamento aproximado (em reais)")

        prompt = (
            "Você é Herbert, assistente da Ajuda Tech.\n\n"
            f"Ainda faltam informações para recomendar: {', '.join(faltando)}.\n"
            "Faça UMA pergunta por vez, em linguagem simples, para obter a próxima informação.\n"
            "Retorne apenas a pergunta."
        )
        response = _call_llm([{"role": "user", "content": prompt}])
        return {"messages": [{"role": "assistant", "content": response}], "stage": "respond"}
    prompt = f"""Você é Herbert, assistente da Ajuda Tech.

Monte a resposta final para o usuário com base na recomendação e relatório:

Recomendação:
{recommendation}

Relatório:
{report_text}

Instruções:
- Responda de forma amigável e simples (máximo 4 frases)
- Destaque o produto recomendado e o preço
- Ofereça gerar o relatório completo se o usuário quiser
- Não use jargões técnicos

Retorne apenas a mensagem final para o usuário."""

    response = _call_llm([{"role": "user", "content": prompt}])

    return {
        "messages": [{"role": "assistant", "content": response}],
        "stage": "respond",
    }
