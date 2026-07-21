# Apresentação — Ajuda Tech (2 Slides)

---

## Slide 1 — Problema e Solução

**Ajuda Tech — Assistente Inteligente para Compra de Computadores**

**Problema:** Muitas pessoas não conseguem escolher um computador porque não entendem especificações técnicas e ficam perdidas entre opções de preço e modelo.

**Solução:** Um agente conversacional com IA que conduz o usuário em uma coleta guiada de informações e recomenda o computador ideal a partir de um catálogo de produtos reais.

**Como funciona:**
1. Usuário descreve o que precisa (estudar, trabalhar, jogar)
2. Agente pergunta sobre orçamento e mobilidade
3. Busca produtos no catálogo que se encaixam no perfil
4. Recomenda a melhor opção em linguagem simples

---

## Slide 2 — Fluxo, Ferramentas e Tecnologias

**Fluxo do Agente (LangGraph):**

```
Entrada do usuário → Classificação de intenção → [Saudação | Coleta de dados | Recomendação]
                                                          ↓
                                              Necessidades completas?
                                              Não → Pergunta faltante
                                              Sim → Busca no catálogo → Gera relatório → Resposta final
```

**Ferramentas integradas:**
- `buscar_produtos` — filtra catálogo por tipo e orçamento
- `comparar_produtos` — compara especificações de dois produtos
- `gerar_relatorio` — gera relatório em Markdown

**Tecnologias:** Python · Django · LangGraph · OpenRouter API · JavaScript

**Memória:** Sessão Django mantém histórico e necessidades do usuário entre mensagens
