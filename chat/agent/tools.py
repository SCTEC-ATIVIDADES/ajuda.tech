"""
Tools integradas ao agente LangGraph.

Ferramentas que o Herbert pode usar durante o fluxo de recomendação.
"""

import json
import os
from pathlib import Path

from langchain_core.tools import tool


_PRODUTOS_PATH = Path(__file__).resolve().parent.parent.parent / "produtos.json"


def _carregar_produtos() -> list[dict]:
    """Carrega a base de dados de produtos do arquivo JSON."""
    if not _PRODUTOS_PATH.exists():
        return []
    with open(_PRODUTOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@tool
def buscar_produtos(categoria: str, orcamento_max: float) -> str:
    """Busca computadores disponíveis por tipo e orçamento máximo.

    Parameters
    ----------
    categoria : str
        Tipo de computador: "notebook" ou "desktop".
    orcamento_max : float
        Valor máximo em reais.

    Returns
    -------
    str
        JSON com a lista de produtos encontrados.
    """
    produtos = _carregar_produtos()

    resultados = [
        p for p in produtos
        if p["tipo"].lower() == categoria.lower()
        and p["preco"] <= orcamento_max
    ]

    if not resultados:
        return json.dumps(
            {"mensagem": "Nenhum produto encontrado para esses critérios.", "produtos": []},
            ensure_ascii=False,
        )

    return json.dumps(
        {"mensagem": f"{len(resultados)} produto(s) encontrado(s).", "produtos": resultados},
        ensure_ascii=False,
        indent=2,
    )


@tool
def comparar_produtos(produto_a_id: int, produto_b_id: int) -> str:
    """Compara especificações de dois produtos pelo ID.

    Parameters
    ----------
    produto_a_id : int
        ID do primeiro produto.
    produto_b_id : int
        ID do segundo produto.

    Returns
    -------
    str
        JSON com a comparação lado a lado.
    """
    produtos = _carregar_produtos()
    mapa = {p["id"]: p for p in produtos}

    a = mapa.get(produto_a_id)
    b = mapa.get(produto_b_id)

    if not a or not b:
        ids_disponiveis = sorted(mapa.keys())
        return json.dumps(
            {
                "erro": "Produto(s) não encontrado(s).",
                "ids_disponiveis": ids_disponiveis,
            },
            ensure_ascii=False,
        )

    comparacao = {
        "produto_a": {
            "nome": a["nome"],
            "tipo": a["tipo"],
            "preco": a["preco"],
            "especificacoes": a["especificacoes"],
            "indicado_para": a["indicado_para"],
        },
        "produto_b": {
            "nome": b["nome"],
            "tipo": b["tipo"],
            "preco": b["preco"],
            "especificacoes": b["especificacoes"],
            "indicado_para": b["indicado_para"],
        },
        "diferenca_preco": round(abs(a["preco"] - b["preco"]), 2),
    }

    return json.dumps(comparacao, ensure_ascii=False, indent=2)


@tool
def gerar_relatorio(nome: str, preco: float, tipo: str, especificacoes: dict, justificativa: str) -> str:
    """Gera um relatório em Markdown com a recomendação do computador.

    Parameters
    ----------
    nome : str
        Nome do produto recomendado.
    preco : float
        Preço do produto em reais.
    tipo : str
        Tipo do produto (notebook ou desktop).
    especificacoes : dict
        Especificações técnicas do produto.
    justificativa : str
        Por que este produto atende as necessidades do usuário.

    Returns
    -------
    str
        Relatório formatado em Markdown.
    """
    specs_formatadas = "\n".join(
        f"  - **{k.replace('_', ' ').title()}:** {v}"
        for k, v in especificacoes.items()
    )

    relatorio = f"""## Relatório de Recomendação — Ajuda Tech

### Computador Recomendado

| Campo | Valor |
|-------|-------|
| **Nome** | {nome} |
| **Tipo** | {tipo.title()} |
| **Preço** | R$ {preco:,.2f} |

### Especificações Técnicas

{specs_formatadas}

### Por que este produto?

{justificativa}

---
*Relatório gerado automaticamente pelo Herbert — Ajuda Tech*
"""
    return relatorio


TOOLS = [buscar_produtos, comparar_produtos, gerar_relatorio]
