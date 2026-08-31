# Spec 001 — LangGraph completo

## Objetivo

Ajustar grafo para demonstrar estado tipado, sequência, ramificação condicional, fan-out/fan-in paralelo e parada segura, sem depender de API real.

## Contexto mínimo atual

Código atual relevante: `chat/agent/state.py`, `graph.py`, `nodes.py`, `tools.py`. `extract_context` existe; confirmar se deve ser nó. Grafo atual classifica, coleta, recomenda, gera relatório e responde. Não duplicar lógica de catálogo.

## Escopo autorizado

Alterar apenas `chat/agent/state.py`, `chat/agent/graph.py`, `chat/agent/nodes.py`, `chat/agent/tools.py`, testes em `chat/tests/`, `README.md` e `docs/PR_LANGGRAPH_RESUMO.md`.

## Execução

1. Ler arquivos do escopo e testes existentes.
2. Definir contrato tipado para candidatos, erros e resultados dos ramos.
3. Implementar dois trabalhos independentes de catálogo em paralelo e nó de consolidação.
4. Integrar ou remover `extract_context`; corrigir documentação.
5. Preservar roteamento de saudação, dados incompletos, recomendação e intenção inválida.
6. Capturar falha parcial sem descartar ramo saudável.
7. Registrar ordem/status/duração usando observabilidade existente, sem API real.

## Testes obrigatórios

- Grafo compila e executa com estado fixture.
- Saudação, coleta, recomendação e intenção inválida.
- Fan-out/fan-in ocorre e consolida resultados.
- Falha em um ramo produz fallback controlado.
- Estado não perde necessidades conhecidas.

## Aceite

- State tipado documentado.
- Sequência, edge condicional, paralelização e parada comprováveis por teste.
- Nenhum teste depende de rede ou chave.
- README e diagrama refletem código real.

## Evidências

Salvar saída de testes e log sanitizado de execução em diretório definido pelo agente seguinte; não inventar captura.

## Saída

Usar contrato de `000`: STATUS, arquivos, testes, evidências, decisões e pendências.

## Próximo

`002`, após testes passarem. Se tool externa for necessária para desenho do grafo, registrar dependência sem bloquear paralelização local.
