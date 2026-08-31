# Evidência — Spec 005

STATUS: DONE

## Aceite verificado

- Eventos estruturados possuem `timestamp`, `trace_id`, `run_id`, `stage`, `event`, `status`, `duration_ms` e `error_type`.
- Requests legado, recomendação e agente geram contexto técnico e eventos correlacionados.
- Nós e ramos de catálogo propagam contexto; métricas agregam etapa, evento, status e duração.
- `analyze_events` reconstrói ordem, acumula duração por etapa e identifica etapa lenta, falhas e causa provável.
- Timeout retorna resposta controlada; retry ocorre somente para falhas recuperáveis; 4xx e 429 não repetem chamada.
- Logs estruturados não registram chave, prompt, payload ou corpo externo completo.
- Teste runtime correlaciona logs capturados e `metrics_snapshot()` com os mesmos IDs.
- Teste de execução direta do grafo comprova propagação de IDs do estado.

## Validação Docker

Imagem `ajuda-tech-spec005`:

- `docker build --tag ajuda-tech-spec005 .`: aprovado.
- Build executou `npm run lint`: aprovado.
- Build executou Vitest: 9 arquivos, 99 testes aprovados.
- `python manage.py check`: aprovado, 0 issues.
- `python manage.py migrate --no-input`: aprovado.
- `pytest -q`: 190 testes aprovados.
- `pytest` focado em observabilidade/resiliência: 67 testes aprovados.
- Análise determinística normal: risco baixo, sem anomalia.
- Análise determinística de falha: anomalia de 5011 ms, causa provável `TimeoutError`, risco alto.

## Evidências

- `normal-events.json` e `failure-events.json`: eventos sanitizados com todos os campos obrigatórios e IDs técnicos.
- `normal-analysis.json` e `failure-analysis.json`: saídas geradas pelo analisador dentro do container Docker.
- `latency-table.md`: latência por etapa e ramo.
- `commands.txt`: comandos reproduzíveis.
- `chat/tests/test_spec005_observability.py`: correlação runtime entre logs e métricas, IDs do grafo e timeout controlado.
- `chat/observability.py`: schema, métrica e análise.
- `chat/views.py`: correlação por endpoint e timeout controlado.
- `chat/agent/graph.py` e `chat/agent/nodes.py`: propagação de contexto e ramos.
- `chat/services.py`: retry, timeout e tratamento sem vazamento.

## Decisões

- Segundo sinal usa métrica agregada em memória, correlacionada por `trace_id` e `run_id`.
- Conteúdo de usuário, prompts, respostas completas e credenciais ficam fora dos eventos.
- IDs são técnicos e não contêm dados pessoais.
- Análise usa método determinístico local; nenhum provedor de IA externo foi chamado.

## Pendências

- A análise por IA externa não foi executada; não é necessária para o aceite técnico da Spec 005.
- O analisador informa tendência como `insufficient_data` quando há menos de dois pontos comparáveis; não há série histórica persistente.

## Próximo

`006`, conforme ordem das specs.
