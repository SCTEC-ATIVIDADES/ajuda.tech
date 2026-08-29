"""
Tools integradas ao agente LangGraph.

Ferramentas que o Herbert pode usar durante o fluxo de recomendação.
"""

import html
import json
import math
from pathlib import Path

from django.conf import settings
from langchain_core.tools import tool

from chat.observability import emit_event, stage
from chat.services import fetch_external_catalog


_PRODUTOS_PATH = Path(__file__).resolve().parent.parent.parent / "produtos.json"
_REQUIRED_PRODUCT_FIELDS = {"id", "nome", "tipo", "preco", "especificacoes", "indicado_para", "mobilidade"}
_VALID_TYPES = {"notebook", "desktop"}
_MAX_PRODUCTS = 1000
_MAX_TEXT = 500
_MAX_SPECS = 50


def _validar_catalogo(produtos) -> list[dict]:
    if not isinstance(produtos, list) or len(produtos) > _MAX_PRODUCTS:
        raise ValueError("Catálogo inválido.")
    for product in produtos:
        if not isinstance(product, dict) or not _REQUIRED_PRODUCT_FIELDS.issubset(product):
            raise ValueError("Catálogo contém produto malformado.")
        if (
            not isinstance(product["id"], int)
            or isinstance(product["id"], bool)
            or not isinstance(product["nome"], str)
            or len(product["nome"]) > _MAX_TEXT
            or product["tipo"] not in _VALID_TYPES
            or not isinstance(product["especificacoes"], dict)
            or isinstance(product["preco"], bool)
            or not isinstance(product["preco"], (int, float))
            or not math.isfinite(product["preco"])
            or product["preco"] < 0
            or not isinstance(product["mobilidade"], str)
        ):
            raise ValueError("Catálogo contém produto inválido.")
        if (
            not isinstance(product["especificacoes"], dict)
            or len(product["especificacoes"]) > _MAX_SPECS
            or not all(isinstance(key, str) and len(key) <= _MAX_TEXT for key in product["especificacoes"])
            or not all(isinstance(value, (str, int, float, bool)) for value in product["especificacoes"].values())
            or not isinstance(product["indicado_para"], list)
            or len(product["indicado_para"]) > _MAX_SPECS
            or not all(isinstance(item, str) and len(item) <= _MAX_TEXT for item in product["indicado_para"])
        ):
            raise ValueError("Catálogo contém produto malformado.")
    return produtos


def _carregar_produtos() -> list[dict]:
    """Carrega e valida catálogo local."""
    if not _PRODUTOS_PATH.exists():
        return []
    with open(_PRODUTOS_PATH, "r", encoding="utf-8") as f:
        return _validar_catalogo(json.load(f))


def _obter_catalogo() -> tuple[list[dict], str]:
    if not getattr(settings, "CATALOG_API_URL", ""):
        return _validar_catalogo(_carregar_produtos()), "local"
    try:
        return _validar_catalogo(fetch_external_catalog()), "externo"
    except Exception as exc:
        emit_event("catalog", "fallback", "fallback", error=exc)
        try:
            return _validar_catalogo(_carregar_produtos()), "local_fallback"
        except Exception as exc:
            raise ValueError("Catálogo indisponível.") from exc


def _erro(message: str, code: str = "invalid_argument") -> str:
    return json.dumps({"ok": False, "erro": message, "codigo": code, "produtos": []}, ensure_ascii=False)


def _escapar(value) -> str:
    return html.escape(str(value), quote=True)


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
    if not isinstance(categoria, str) or categoria.lower().strip() not in _VALID_TYPES:
        return _erro("Parâmetro 'categoria' inválido ou ausente.")

    if isinstance(orcamento_max, str):
        cleaned = orcamento_max.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            orcamento_max = float(cleaned)
        except (TypeError, ValueError):
            orcamento_max = None

    if orcamento_max is None or isinstance(orcamento_max, bool) or not isinstance(orcamento_max, (int, float)):
        return _erro("Parâmetro 'orcamento_max' inválido ou ausente.")

    orcamento_max = float(orcamento_max)
    if orcamento_max < 0 or not math.isfinite(orcamento_max):
        return _erro("Parâmetro 'orcamento_max' inválido ou ausente.")
    with stage("tool.buscar_produtos"):
        produtos, origem = _obter_catalogo()

    resultados = [
        p for p in produtos
        if p["tipo"].lower() == categoria.lower().strip()
        and p["preco"] <= orcamento_max
    ]

    if not resultados:
        return json.dumps(
            {"ok": True, "origem": origem, "mensagem": "Nenhum produto encontrado para esses critérios.", "produtos": []},
            ensure_ascii=False,
        )

    return json.dumps(
        {"ok": True, "origem": origem, "mensagem": f"{len(resultados)} produto(s) encontrado(s).", "produtos": resultados},
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
    if isinstance(produto_a_id, bool) or not isinstance(produto_a_id, int):
        return _erro("Parâmetro 'produto_a_id' inválido.")
    if isinstance(produto_b_id, bool) or not isinstance(produto_b_id, int):
        return _erro("Parâmetro 'produto_b_id' inválido.")
    if produto_a_id == produto_b_id:
        return _erro("Produtos para comparação devem ser diferentes.")
    with stage("tool.comparar_produtos"):
        produtos, _origem = _obter_catalogo()
    mapa = {p["id"]: p for p in produtos}

    a = mapa.get(produto_a_id)
    b = mapa.get(produto_b_id)

    if not a or not b:
        ids_disponiveis = sorted(mapa.keys())
        return json.dumps(
            {
                "ok": False,
                "erro": "Produto(s) não encontrado(s).",
                "codigo": "not_found",
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
    if (
        not isinstance(nome, str)
        or not isinstance(tipo, str)
        or tipo.lower().strip() not in _VALID_TYPES
        or isinstance(preco, bool)
        or not isinstance(preco, (int, float))
        or not math.isfinite(preco)
        or preco < 0
        or not isinstance(especificacoes, dict)
        or not isinstance(justificativa, str)
        or len(nome) > _MAX_TEXT
        or len(especificacoes) > _MAX_SPECS
        or any(
            not isinstance(key, str)
            or len(key) > _MAX_TEXT
            or not isinstance(value, (str, int, float, bool))
            for key, value in especificacoes.items()
        )
    ):
        return _erro("Parâmetros do relatório inválidos.", "invalid_report")

    with stage("tool.gerar_relatorio"):
        specs_formatadas = "\n".join(
            f"  - **{_escapar(k).replace('_', ' ').title()}:** {_escapar(v)}"
            for k, v in especificacoes.items()
        )

    relatorio = f"""## Relatório de Recomendação — Ajuda Tech

### Computador Recomendado

| Campo | Valor |
|-------|-------|
| **Nome** | {_escapar(nome)} |
| **Tipo** | {_escapar(tipo.title())} |
| **Preço** | R$ {preco:,.2f} |

### Especificações Técnicas

{specs_formatadas}

### Por que este produto?

{_escapar(justificativa)}

---
*Relatório gerado automaticamente pelo Herbert — Ajuda Tech*
"""
    return relatorio


TOOLS = [buscar_produtos, comparar_produtos, gerar_relatorio]
