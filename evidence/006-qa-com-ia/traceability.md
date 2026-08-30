# Rastreabilidade de geração e refinamento — Spec 006

## Execução IA

- Alvo inicial: commit real `aed90a4` e follow-ups até `dc6ef7e`.
- Reanálise do estado final: commits `92405f0`, `df07614`, `89e356c`, `58601e0` e `d603fdc`.
- Modelo registrado: `omniroute/default`.
- Data: 2026-08-30.
- Restrições: sem credenciais, sem dados pessoais e sem chamadas externas.

## Matriz de rastreabilidade

| Risco identificado pela IA | Teste inicialmente proposto | Refinamento aplicado | Evidência | Resultado |
|---|---|---|---|---|
| Endpoint e grafo divergirem | Executar grafo compilado com dependências mockadas | Invocar grafo real e endpoint com LLM/catálogo mockados | `chat/tests/test_agent_graph.py`; `chat/tests/test_acceptance.py` | Passou |
| Contexto não persistir | Enviar segunda mensagem e limpar sessão | Verificar `user_needs`, histórico, `thread_id`, expiração e `/new/` | `chat/tests/test_acceptance.py`; `chat/tests/test_views.py`; `chat/tests/test_limits.py` | Passou |
| Falha de catálogo derrubar resposta | Simular timeout/resposta inválida | Cobrir dois ramos, fallback local, resposta segura e persistência | `chat/tests/test_acceptance.py`; `chat/tests/test_catalog_integration.py` | Passou |
| Prompt injection alcançar modelo | Testar frases em inglês | Adicionar variantes em português, caixa, espaçamento e afirmar ausência de chamada ao grafo | `chat/tests/test_security.py`; `chat/tests/test_acceptance.py` | Passou |
| Fan-out multiplicar custo/latência | Medir chamadas | Testar dois ramos, duração, eventos correlacionados e limites | `chat/tests/test_agent_graph.py`; `chat/tests/test_spec005_observability.py` | Passou |
| Orçamento inválido ser aceito | Testar coerção de booleano | Validar valores inválidos, histórico recuperado e contrato das tools | `chat/tests/test_agent_tools.py`; `chat/tests/test_limits.py` | Passou |
| Contrato frontend/backend quebrar | Verificar resposta e erro | Cobrir `reply`, `report`, `failed_message`, loading, erro e reenvio | `chat/static/chat/js/chatApi.test.js`; `chatApi.errors.test.js`; `chatApp.test.js` | Passou |
| Segurança de entrada e CSRF | Testar JSON e CSRF | Aplicar matriz aos endpoints legado, agente e recomendação, com rate limit antes do LLM | `chat/tests/test_security.py`; `chat/tests/test_views.py` | Passou |
| Resiliência e observabilidade insuficientes | Testar timeout e retry | Correlacionar logs/métricas, validar 4xx sem retry e analisar cenário normal/falha | `chat/tests/test_spec005_observability.py`; `evidence/005-observabilidade-resiliencia/` | Passou |

## Decisões humanas

- Achados de alta severidade foram aceitos e mitigados com testes de integração e aceitação.
- Testes sem rede externa foram mantidos para determinismo; integração HTTP local versionada foi validada separadamente.
- Custos de fan-out foram limitados a dois ramos determinísticos.
- Prompt injection é bloqueado antes do grafo; nenhum prompt interno é retornado.
- `ruff` e `mypy` não foram adicionados porque não fazem parte das dependências/gates atuais; frontend foi validado dentro da imagem Docker.
- Vídeo, publicação e validações externas pertencem às Specs 009–010, não a esta spec.

## Evidência red/green

O comportamento crítico endpoint → grafo possui testes de aceitação que falham se o grafo for substituído por mock incorreto, se a sessão não persistir ou se a falha do catálogo produzir erro não controlado. Os testes foram executados na suíte Docker atual, sem API externa.

## Resultado

A geração e o refinamento estão rastreáveis da análise IA aos testes, arquivos e resultados. Nenhum achado foi atribuído retroativamente a uma IA sem registro.