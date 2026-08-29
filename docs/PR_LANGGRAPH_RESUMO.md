# PR: Implementação do Agente LangGraph — Módulo 2

## Resumo

Agente **Herbert** implementado com **LangGraph**, estado tipado (`AgentState`) e fluxo de catálogo com fan-out/fan-in. O grafo cobre classificação, coleta de necessidades, busca paralela de produtos, recomendação, relatório e resposta.

## Mudanças Principais

### Módulo `chat/agent/`

| Arquivo | Descrição |
|---------|-----------|
| `state.py` | Contratos tipados (`TypedDict`) para estado, trabalhos, produtos, resultados e erros |
| `tools.py` | Tools de consulta de produtos, comparação e relatório Markdown |
| `nodes.py` | Nós `classify_msg`, `gather_needs`, `prepare_catalog`, `catalog_worker`, `consolidate_catalog`, `recommend`, `report` e `respond`, além de `greet` |
| `graph.py` | `StateGraph` compilado com roteamento condicional, `Send` e reducers |

`extract_context` permanece disponível em `nodes.py`, mas não pertence ao grafo atual.

### Fluxo do Agente

```text
START → classify_msg → [greet → END | gather_needs → respond | prepare_catalog]
                                      prepare_catalog → Send → catalog_worker (ramos)
                                      catalog_worker → consolidate_catalog
                                      consolidate_catalog → recommend → report → respond → END
```

`gather_needs` vai para `prepare_catalog` quando propósito e orçamento estão disponíveis; caso contrário, vai para `respond` para solicitar dados faltantes. `prepare_catalog` cria ramos para notebook e desktop. `consolidate_catalog` agrega produtos disponíveis e registra erros dos ramos que falharam, preservando falhas parciais.

### Integração

- `chat/views.py` — endpoint `AgentSendMessageView` (`POST /chat/agent/send/`)
- `chat/urls.py` — rota `/agent/send/`
- `requirements.txt` — dependências LangGraph e LangChain Core
- `produtos.json` — catálogo local

## Estado Compartilhado

```python
class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    user_needs: dict[str, object]
    products_found: list[Product]
    catalog_jobs: list[CatalogJob]
    branch_job: CatalogJob
    catalog_results: Annotated[list[CatalogBranchResult], add]
    errors: Annotated[list[str], add]
    stage: str
    recommendation: str
    report: str
    classified_intent: str
```

`catalog_results` e `errors` usam reducers para reunir resultados dos ramos `catalog_worker`.

## Como Executar

```bash
pip install -r requirements.txt
python manage.py runserver
```

Endpoint:

```bash
curl -X POST http://localhost:8000/chat/agent/send/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, preciso de um notebook para estudos"}'
```

## Documentação Relacionada

- `docs/MODULO2_LANGGRAPH_EVOLUCAO.md`
- `docs/prompts/prompt-modulo2-langgraph-evolucao.md`
- `docs/prompts/prompt-modulo2-langgraph-implementacao.md`
