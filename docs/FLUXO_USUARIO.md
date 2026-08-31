# Fluxo do Usuário

Fluxo real é condicional: agente coleta somente dados ausentes, preserva necessidades na sessão e consulta catálogo quando há propósito e orçamento suficientes. Não há roteiro fixo de quatro perguntas nem promessa de tempo, bateria ou desempenho.

```mermaid
graph TD
    A[Usuário abre /] --> B[Frontend envia POST /agent/send/]
    B --> C{Validação}
    C -->|inválida, injection ou rate limit| D[Erro JSON ou HTTP 429]
    C -->|válida| E[Lê sessão Django]
    E --> F[classify_msg]
    F -->|cumprimento| G[greet]
    F -->|necessidades incompletas| H[gather_needs]
    F -->|necessidades suficientes| I[prepare_catalog]
    H --> J{Propósito e orçamento existem?}
    J -->|não| K[respond pergunta dados faltantes]
    J -->|sim| I
    I --> L[Fan-out: notebook + desktop]
    L --> M[Busca e valida produtos]
    M --> N[Consolida resultados; mantém falhas parciais]
    N --> O[Comparação e recomendação]
    O --> P[Relatório Markdown]
    G --> Q[respond]
    K --> Q
    P --> Q
    Q --> R[Salva histórico/necessidades na sessão]
    R --> S[Frontend renderiza resposta sanitizada]
    S --> T{Continuar?}
    T -->|sim| B
    T -->|nova conversa| U[POST /new/; limpa sessão]
    T -->|não| V[Fim]
```

## Comportamento comprovado

- Sem login obrigatório.
- Sessão retém até 50 entradas por 24 horas; LLM recebe até 20 mensagens.
- Mensagem máxima: 4.000 caracteres; rate limit: 10 requisições por sessão em 60 segundos.
- Recarregar mantém dados no backend, mas frontend não busca histórico antigo para exibição.
- Catálogo usa `produtos.json`; `CATALOG_API_URL` é opcional e falhas usam fallback local.
- Especificações podem aparecer na resposta, mas comparação visual, lazy load, três produtos exatos, seminovos e garantias não são garantias do código atual.

## Visualização

Use extensão Mermaid no VS Code ou outro editor compatível.
