# PR: Implementação do Agente LangGraph — Módulo 2

## Resumo

Implementação completa do agente **Herbert** usando **LangGraph** para o Módulo 2 do projeto Ajuda Tech. O agente agora fluxo em grafo com 7 nós, 3 tools integradas e estado compartilhado.

## Mudanças Principais

### Novo módulo `chat/agent/`

| Arquivo | Descrição |
|---------|-----------|
| `state.py` | Estado compartilhado (`AgentState` TypedDict) com messages, user_needs, products_found, stage, recommendation, report, classified_intent |
| `tools.py` | 3 tools: `buscar_produtos` (consulta JSON), `comparar_produtos` (comparação), `gerar_relatorio` (relatório Markdown) |
| `nodes.py` | 7 nós do grafo: classify, greet, gather_needs, extract_context, recommend, report, respond |
| `graph.py` | StateGraph montado com edges condicionais e compilado |

### Base de dados

- `produtos.json` — 12 produtos (6 notebooks + 6 desktops), faixas R$2.199 a R$7.999

### Integração

- `chat/views.py` — Novo endpoint `AgentSendMessageView` (`POST /chat/agent/send/`)
- `chat/urls.py` — Rota `/agent/send/` adicionada
- `requirements.txt` — `langgraph>=0.2.0` e `langchain-core>=0.3.0`

### Documentação

- `docs/MODULO2_LANGGRAPH_EVOLUCAO.md` — Plano de evolução com gap analysis
- `docs/prompts/prompt-modulo2-langgraph-evolucao.md` — Prompts da fase de planejamento
- `docs/prompts/prompt-modulo2-langgraph-implementacao.md` — Prompts da fase de implementação + prompts internos dos nós

## Fluxo do Agente

```
START → classify_msg → [greet | gather_needs | recommend]
                              ↓
                        extract_context → recommend → report → respond → END
```

## Como Testar

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar o servidor
python manage.py runserver

# Testar o endpoint do agente
curl -X POST http://localhost:8000/chat/agent/send/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, preciso de um notebook para estudos"}'
```

## Checklists do Módulo 2

- [x] Definir processo real a ser automatizado
- [x] Implementar com LangGraph (estado, nós, conexões)
- [x] Integrar pelo menos 1 tool (`buscar_produtos`, `comparar_produtos`, `gerar_relatorio`)
- [x] Usar memória/contexto durante execução
- [x] Registrar prompts em arquivos `.md`
- [x] Documentar no README
- [x] Versionado no GitHub

## Commits

| Hash | Descrição |
|------|-----------|
| `aed90a4` | feat: implement LangGraph agent with message handling and product recommendation |
| `3593f5d` | docs: add implementation prompts for LangGraph module 2 |

## Decisões do Grupo

| Questão | Decisão |
|---------|---------|
| Model LLM | Manter DeepSeek |
| Quantidade de tools | 3 tools |
| Checkpointer | Manter cookies (implementar depois) |
| Nós do grafo | 7 nós (classify, greet, gather, extract, recommend, report, respond) |
| Divisão de tarefas | Passo 1 e 2 juntos; resto dividido |
