# Spec 004 — Matriz de ameaças

| Ameaça | Controle | Evidência |
|---|---|---|
| Prompt injection | Detecção antes do LLM, resposta segura e evento estruturado | `chat/tests/test_security.py::test_injection_is_blocked_before_llm`, `test_prompt_injection_block_is_observable` |
| Payload excessivo | Limite de body em 8.192 bytes e mensagem em 4.000 caracteres | `chat/tests/test_views.py`, `chat/tests/test_security.py` |
| Abuso | Rate limit de 10 requisições por sessão em 60 segundos, antes do LLM | `chat/tests/test_limits.py`, `chat/tests/test_security.py::test_recommend_rate_limit_blocks_llm` |
| Segredos | Variáveis de ambiente, `.env` fora do Git e produção exige chave não padrão | `ajuda_tech/settings.py`, `docker run ... manage.py check --deploy` |
| Tool indevida | Allowlist exata de três tools somente leitura | `chat/tests/test_security.py::test_tools_are_read_only_allowlist` |
| Vazamento de prompt/raciocínio | Resposta fixa para injection e remoção de conteúdo de raciocínio | `chat/tests/test_security.py`, `chat/tests/test_agent_nodes.py` |
| CSRF | Middleware Django e token obrigatório nos endpoints JSON | `chat/tests/test_security.py`, `chat/tests/test_views.py` |

Nenhuma tool compra, paga, apaga, grava catálogo ou executa efeito externo.
