# Spec 001 — Status

STATUS: DONE
SPEC: 001-langgraph-completo

## Aceite verificado

- `AgentState` usa contratos `TypedDict` para estado, trabalhos e resultados.
- Grafo compila e executa com `invoke()` usando fixtures e mocks locais.
- Fluxo sequencial comprovado: classificação, coleta, catálogo, consolidação, comparação, recomendação, relatório e resposta.
- Roteamento condicional comprovado para saudação, dados incompletos, recomendação e intenção desconhecida.
- Fan-out/fan-in comprovado com dois ramos de catálogo.
- Falha parcial preserva ramo saudável e registra erro controlado.
- Necessidades já conhecidas permanecem no estado.
- Parada em `END` comprovada pelos fluxos de saudação e resposta.
- Ordem, status, duração, `trace_id` e `run_id` registrados sem conteúdo de prompt.
- Testes não usam rede nem chave de API.
- `extract_context` órfão removido.
- README e resumo do LangGraph refletem o grafo atual.

## Arquivos alterados

- `chat/agent/nodes.py`
- `chat/prompts.py`
- `chat/tests/test_agent_graph.py`
- `chat/tests/test_agent_prompts.py`
- `docs/PR_LANGGRAPH_RESUMO.md`

## Testes Docker

- `docker build --tag ajuda-tech-spec001 .`: PASS
- Build executou `npm run lint`: PASS
- Build executou Vitest: 99 testes PASS em 9 arquivos
- `python manage.py check`: PASS, 0 issues
- Testes relacionados: 20 PASS
- Suíte backend completa: 167 PASS

## Evidências

- `graph-execution.log`: saída sanitizada da execução instrumentada.
- `chat/tests/test_agent_graph.py`: invoke real, roteamento, fan-out/fan-in, falha parcial, estado e correlação.
- `chat/tests/test_acceptance.py`: fluxos de aceitação.
- `chat/tests/test_observability.py`: eventos correlacionados.

## Decisões

- `extract_context` foi removido, pois não era nó nem era chamado pelo grafo.
- O catálogo usa mocks nos testes para manter execução determinística e sem dependência externa.

## Pendências

Nenhuma pendência técnica da Spec 001.

## Próximo

Executar Spec 002 usando este status como pré-condição.
