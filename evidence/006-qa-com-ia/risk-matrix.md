# Matriz risco → teste → evidência

| Prioridade | Risco | Teste | Evidência | Status |
|---|---|---|---|---|
| P0 | Endpoint e grafo compilado divergirem | Fluxo normal endpoint→grafo→LLM→catálogo | `chat/tests/test_acceptance.py::test_agent_recommendation_persists_session_across_requests` | DONE |
| P0 | Falha do catálogo vazar traceback ou derrubar resposta | Ramos do catálogo falhando | `chat/tests/test_acceptance.py::test_agent_catalog_failure_returns_safe_response_and_persists_session` | DONE |
| P0 | Contexto não persistir entre turnos | Duas requisições e inspeção da sessão | `chat/tests/test_acceptance.py::test_agent_recommendation_persists_session_across_requests` | DONE |
| P0 | Contrato frontend/backend quebrar | Resposta `reply` e erro `failed_message` | `chat/static/chat/js/chatApi.test.js`, `chatApi.errors.test.js` | DONE |
| P0 | Usuário não conseguir recuperar falha | Reenvio com sucesso e nova falha | `chat/static/chat/js/chatApp.test.js` | DONE |
| P1 | Prompt injection chegar ao modelo | Variantes de entrada bloqueadas | `chat/tests/test_views.py`, `chat/tests/test_agent_nodes.py` | DONE |
| P1 | Payload malformado ou grande causar erro | JSON/tipos/limites | `chat/tests/test_views.py` | DONE |
| P1 | Abuso consumir LLM | Limite por sessão | `chat/tests/test_limits.py` | DONE |
| P1 | CSRF em endpoint novo | Cliente sem token | `chat/tests/test_views.py` | DONE |
| P1 | Histórico enviar contexto excessivo | Limites de histórico e janela LLM | `chat/tests/test_limits.py` | DONE |
| P1 | Falha de integração externa | Lista/objeto inválido, 4xx/5xx e fallback | `chat/tests/test_catalog_integration.py` | DONE |
| P1 | Produtos inválidos entrarem no prompt | Schema e filtros do catálogo | `chat/tests/test_agent_tools.py`, `test_catalog_integration.py` | DONE |
| P1 | Roteamento LangGraph quebrar | Rotas, fan-out/fan-in e falha parcial | `chat/tests/test_agent_graph.py` | DONE |
| P2 | Segredos ou raciocínio aparecerem na saída/log | Prompts, sanitização e filtros | `chat/tests/test_prompts.py`, `test_agent_nodes.py`, `test_observability.py` | DONE |
| P2 | Frontend não ser validado no ambiente atual | Vitest completo | `npm test` | BLOCKED — `node`/`npm` indisponíveis |
| P2 | Serviço externo real não ser comprovado | Execução com serviço/credencial real | `README.md:117-119` | BLOCKED — não permitido nesta suíte |

## Verificação executada

- `python3 -m pytest --cov=chat --cov-report=term-missing --cov-report=xml --cov-fail-under=80 -q`: 146 passed; 93.11% coverage.
- `python3 -m pytest chat/tests/test_acceptance.py chat/tests/test_agent_graph.py chat/tests/test_agent_nodes.py chat/tests/test_agent_tools.py chat/tests/test_catalog_integration.py -q`: 29 passed.
- `python3 -m compileall -q chat`: passed.
- `git diff --check`: passed.
- `node`, `npm`, `ruff`, `mypy`: unavailable in the environment.
