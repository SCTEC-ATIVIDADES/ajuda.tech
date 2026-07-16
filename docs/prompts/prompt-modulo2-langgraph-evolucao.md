# Prompt — Módulo 2: Evolução do Projeto com LangGraph

## 1. Prompts Utilizados

### Prompt 1 — Análise Inicial do Projeto

**Data:** 16/07/2026

```markdown
analise o projeto de trabalho ajuda tech, é um trabalho de um curso.
após análise, precisamos sugerir idéias simples para evoluer com ele
usando LangGraph. Talvez utilisar um novo agente para isso. Pode me ajudar?
```

**Objetivo:** Explorar o projeto atual, identificar limitações e sugerir caminhos de evolução com LangGraph.

**Ferramentas utilizadas:**
- `task` (agente explore) — Leitura completa do projeto (estrutura, código, docs)
- `websearch` — Pesquisa sobre LangGraph, padrões multi-agent, tutoriais 2025/2026

**Resultado:** Análise completa do projeto + 4 ideias de evolução (grafo sequencial, supervisor, ReAct agent, human-in-the-loop).

---

### Prompt 2 — Requisitos do Módulo 2

**Data:** 16/07/2026

```markdown
Ou te dar mais detalhes do modulo 2 desse trabalho:

REQUISITOS DA APLICAÇÃO
O projeto deverá atender aos seguintes requisitos técnicos e de execução:
- Definir um processo real a ser automatizado, descrevendo o objetivo
  do agente, a entrada esperada, as etapas principais e a saída produzida.
- Implementar o agente com LangGraph, utilizando um fluxo organizado
  com estado, nós e conexões entre as etapas.
- Integrar pelo menos uma ferramenta ao agente, como leitura de arquivo,
  escrita de relatório, chamada a API, consulta a dados ou execução
  de função controlada.
- Utilizar memória ou contexto durante a execução, mantendo informações
  relevantes no estado do agente ou em uma estrutura simples de apoio.
- Registrar os principais prompts utilizados em arquivo .md, incluindo
  prompts usados para planejar, implementar, corrigir ou melhorar o agente.
- Documentar no README.md como o agente funciona, como executar o
  projeto e quais decisões principais foram tomadas.
- Manter o projeto versionado no GitHub. Em projetos em grupo, cada
  integrante deverá apresentar contribuição rastreável.

DEFINIÇÃO DO AGENTE
- O projeto deverá apresentar claramente o agente que será construído
  e qual papel ele terá dentro da solução.
- Definir o objetivo do agente.
- Informar quais entradas o agente irá receber.
- Informar quais saídas o agente deverá produzir.
- Descrever quais etapas principais o agente deverá executar.
- Explicar, de forma breve, por que a solução pode ser considerada um agente.

IMPLEMENTAÇÃO COM LANGGRAPH, FERRAMENTA E CONTEXTO
- Estado compartilhado para armazenar informações da execução;
- Nós responsáveis pelas etapas principais do processo;
- Conexões entre os nós;
- Pelo menos uma ferramenta integrada ao fluxo;
- Uso de contexto ou memória durante a execução;
- Geração de uma resposta final estruturada.
```

**Objetivo:** Mapear os requisitos obrigatórios do módulo 2 e cruzar com o estado atual do projeto (gap analysis).

**Resultado:** Gap analysis detalhada + plano de implementação com estrutura de arquivos, fluxo do grafo, tools, estado compartilhado e checklist de entregas.

---

### Prompt 3 — Ajuste: Remover Pagamentos

**Data:** 16/07/2026

```markdown
Uma unica alteração no plano, é que não vamos implementar pagamentos.
Seria só mais para relatórios.
```

**Objetivo:** Remover a tool `calcular_parcelas` e substituir por `gerar_relatorio`.

**Alterações aplicadas:**
- Tool removida: `calcular_parcelas` (função pura de cálculo de parcelas)
- Tool adicionada: `gerar_relatorio` (gera relatório em Markdown)
- Nó adicionado ao grafo: `report`
- Campo adicionado ao estado: `report: str`
- Fluxo atualizado: `recommend → report → respond`

---

## 2. Dados da Execução

| Campo | Valor |
|-------|-------|
| **Data** | 16/07/2026 |
| **Ferramenta** | opencode (mimo-v2.5-free) |
| **Ciclos** | 4 prompts |

---

## 3. Padrões de Prompting Aplicados

| Padrão | Onde foi aplicado | Evidência |
|--------|------------------|-----------|
| **Contexto + Tarefa** | Prompt 1 | "analise o projeto... após análise, sugerir ideias com LangGraph" |
| **Dados brutos + Esperado** | Prompt 2 | Requisitos copiados do edital + pedido de análise |
| **Restrição explícita** | Prompt 3 | "não vamos implementar pagamentos" |

---

## 4. Resultado Final

Arquivo gerado: [`docs/MODULO2_LANGGRAPH_EVOLUCAO.md`](../MODULO2_LANGGRAPH_EVOLUCAO.md)

Conteúdo:
- Situação atual do projeto
- Requisitos do módulo 2 (checklist)
- Gap analysis
- Definição formal do agente
- Fluxo com LangGraph (diagrama ASCII)
- Estado compartilhado
- Nós do grafo
- Tools a implementar
- Estrutura de arquivos proposta
- Dependências novas
- Documentação necessária
- Próximos passos + perguntas para o grupo
- Comparativo antes vs. depois
