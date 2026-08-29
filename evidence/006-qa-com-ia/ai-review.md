# Evidência de revisão com IA — Spec 006

## Alvo

- Commit: `aed90a4d9b80301db7cc121daa66b759bad099b0`
- Descrição: `feat: implement LangGraph agent with message handling and product recommendation`
- Escopo revisado: `aed90a4..dc6ef7e`
- Arquivos principais: `chat/agent/{graph,nodes,state,tools}.py`, `chat/views.py`, `chat/urls.py`, `produtos.json`, `requirements.txt`
- Data da execução: 2026-08-29
- Modelo: `omniroute/default` (modelo do runtime desta sessão; não foi atribuído outro identificador ao subagente)

## Prompt enviado à IA

> Revise o diff real do commit aed90a4 e seus follow-ups até dc6ef7e como code reviewer de QA. Priorize riscos de integração endpoint→grafo, persistência de sessão/contexto, falhas de catálogo externo, segurança de entrada, custo/latência do fan-out, contratos frontend/backend e CSRF. Para cada achado informe severidade, localização, impacto e um teste reproduzível. Não inclua segredos nem faça chamadas externas.

## Resposta da IA

1. **High — integração do grafo não testada:** testes do endpoint mockam `_get_agent_graph`; adicionar fluxo do grafo compilado com LLM/catálogo mockados.
2. **High — persistência de contexto entre requisições não comprovada:** testar segunda mensagem e limpeza por `/new/`.
3. **High — falha do catálogo sem cobertura no endpoint:** testar timeout, resposta inválida e falha dos dois ramos com resposta segura.
4. **Medium — filtro de injection limitado a frases em inglês:** testar variantes em português, caixa e espaçamento; verificar que o grafo não é chamado.
5. **Medium — fan-out pode multiplicar custo/latência:** medir chamadas de catálogo/LLM e documentar limite ou cache.
6. **Medium — coerção de orçamento booleano:** testar contexto persistido/LLM inválido.
7. **Medium — contratos frontend desatualizados:** alinhar `/agent/send/`, `reply`, erro e reenvio.
8. **Low — CSRF incompleto nos endpoints novos:** testar `/agent/send/` e `/new/` com verificação CSRF.
9. **Bloqueio de verificação:** a coleta local exigia instalar `langgraph`/`langchain-core`.

## Decisão humana e rastreabilidade

- **Aceitos e implementados:** 1, 2, 3 e 7. Evidências: `chat/tests/test_acceptance.py`, `chat/tests/test_agent_graph.py`, `chat/tests/test_catalog_integration.py`, `chat/static/chat/js/chatApi.test.js`, `chat/static/chat/js/chatApi.errors.test.js`, `chat/static/chat/js/chatApp.test.js`.
- **Aceitos como já cobertos no working tree:** 4, 6 e 8. Evidências: `chat/tests/test_views.py`, `chat/tests/test_limits.py`, `chat/tests/test_agent_nodes.py`.
- **Aceito e medido, sem alteração adicional:** 5. O teste de aceitação verifica a execução normal e suas chamadas; o fan-out permanece deliberado por categoria.
- **Rejeitado como alteração nesta spec:** nenhum achado; não foi feita mudança funcional fora do escopo autorizado.
- **Resolvido:** 9. Dependências foram instaladas localmente; testes não fazem chamadas à API externa.

Esta resposta é a saída atribuída à IA. Refinamentos, decisões e alterações de teste foram revisados pelo agente executor e estão separados acima.
