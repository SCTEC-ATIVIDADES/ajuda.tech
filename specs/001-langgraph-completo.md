# Spec 001 — LangGraph completo

## Resumo das lacunas

- Grafo não possui paralelização explícita.
- `extract_context` existe, mas não participa do fluxo.
- Estado usa tipos amplos e não documenta contrato completo.
- Não há evidência única de execução sequencial, condicional e paralela.

## Planejamento detalhado

1. Definir fluxo real: classificar entrada, extrair contexto, coletar necessidades, buscar candidatos em paralelo, consolidar, gerar relatório e responder.
2. Adicionar dois nós independentes de busca, por exemplo filtro por orçamento e filtro por mobilidade, executados em paralelo.
3. Adicionar nó de consolidação após ambas as buscas.
4. Registrar `extract_context` apenas se ele tiver responsabilidade distinta e teste próprio.
5. Tipar estado com `TypedDict`/modelos já disponíveis no projeto, sem duplicar contratos.
6. Testar cada transição e uma execução ponta a ponta.
7. Atualizar diagramas e README para refletir grafo real.

## TODO

- [ ] Modelar estado final e reducers.
- [ ] Implementar fan-out/fan-in no grafo.
- [ ] Integrar `extract_context` ou removê-lo e corrigir docs.
- [ ] Garantir roteamento seguro para intenção inválida.
- [ ] Testar execução sequencial, condicional e paralela.
- [ ] Medir tempo de execução paralela versus sequencial.

## Dúvidas técnicas em aberto

- Paralelização deve usar dois nós de catálogo ou busca de catálogo e validação de requisitos?
- `extract_context` será nó obrigatório ou função interna de coleta?
- Estado precisa suportar múltiplos candidatos e erros parciais?

## Critérios de aceite

- Grafo compilado e invocável sem API real nos testes.
- Estado tipado documentado.
- Existe sequência de nós, edge condicional e fan-out/fan-in verificável.
- Falha em ramo paralelo não corrompe outro ramo e produz fallback controlado.
- Execução registra ordem, duração e resultado de cada nó.

## Arquivos afetados

- `chat/agent/state.py`
- `chat/agent/graph.py`
- `chat/agent/nodes.py`
- `chat/agent/tools.py`
- `chat/tests/test_agent_nodes.py`
- Novo teste de grafo em `chat/tests/`
- `README.md`
- `docs/PR_LANGGRAPH_RESUMO.md`

## Evidências esperadas

- Diagrama atualizado.
- Log de execução mostrando branches paralelos e consolidação.
- Teste ponta a ponta.
- Captura ou gravação do fluxo normal e de erro.

## Dependências

- [002](002-tools-integracoes.md)
- [005](005-observabilidade-resiliencia.md)
