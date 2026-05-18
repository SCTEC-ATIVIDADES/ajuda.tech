# PRD — Product Requirements Document

## Ajuda Tech: Assistente Inteligente para Compra de Computadores

**Versão:** 1.0  
**Data:** Maio de 2026  
**Status:** Em definição

---

## 1. Visão Geral do Produto

### 1.1 Resumo

O Ajuda Tech é uma plataforma web que utiliza Inteligência Artificial para guiar usuários leigos na escolha do computador ideal. Por meio de uma conversa natural, a IA coleta informações sobre as necessidades e o orçamento do usuário e recomenda a melhor opção de PC ou Notebook.

### 1.2 Problema

Consumidores sem conhecimento técnico enfrentam dificuldades ao comprar computadores:

- Não entendem especificações técnicas (RAM, processador, SSD, etc.)
- São facilmente influenciados por vendedores sem base nas suas reais necessidades
- Compram equipamentos subdimensionados ou superdimensionados para suas tarefas
- Falta de uma fonte confiável, neutra e acessível de orientação

### 1.3 Solução

Um assistente conversacional baseado em IA que:

1. Faz perguntas simples sobre a finalidade do computador
2. Interpreta as respostas em linguagem natural
3. Recomenda o tipo de máquina (PC ou Notebook) e as especificações mínimas recomendadas
4. Explica o motivo da recomendação de forma clara e acessível

---

## 2. Usuários-Alvo

### Persona Principal: O Comprador Leigo

| Atributo          | Descrição                                           |
| ----------------- | --------------------------------------------------- |
| **Nome fictício** | Carlos, 42 anos                                     |
| **Perfil**        | Pai de família, trabalha em área não-técnica        |
| **Objetivo**      | Comprar um computador para uso doméstico e do filho |
| **Dores**         | Não entende de hardware, tem medo de errar a compra |
| **Canal**         | Acessa pelo celular ou computador da biblioteca     |

### Persona Secundária: O Estudante Iniciante

| Atributo          | Descrição                                          |
| ----------------- | -------------------------------------------------- |
| **Nome fictício** | Beatriz, 18 anos                                   |
| **Perfil**        | Entrando na faculdade, primeiro computador próprio |
| **Objetivo**      | Notebook para estudos com orçamento limitado       |
| **Dores**         | Recebe indicações contraditórias de amigos e lojas |

---

## 3. Requisitos Funcionais

### RF01 — Início de Conversa

- O sistema deve apresentar uma mensagem de boas-vindas ao usuário
- A IA deve iniciar a coleta de necessidades com uma pergunta aberta

### RF02 — Coleta de Necessidades

A IA deve identificar, ao longo da conversa:

- [ ] Finalidade principal do computador (trabalho, estudo, jogos, uso básico, design, etc.)
- [ ] Mobilidade necessária (fica em casa, precisa carregar)
- [ ] Orçamento aproximado
- [ ] Nível de exigência de desempenho

### RF03 — Recomendação

- [ ] Ao final da conversa, a IA deve gerar uma recomendação clara
- [ ] A recomendação deve incluir: tipo (PC/Notebook), especificações mínimas recomendadas e justificativa em linguagem simples
- [ ] A recomendação deve ser exibida de forma destacada na interface

### RF04 — Histórico da Sessão

- [ ] As mensagens da conversa devem ser salvas durante a sessão do usuário
- [ ] O histórico deve ser exibido na tela do chat em ordem cronológica

### RF05 — Nova Conversa

- [ ] O usuário deve poder iniciar uma nova conversa a qualquer momento
- [ ] Ao iniciar nova conversa, a sessão anterior é encerrada

---

## 4. Requisitos Não-Funcionais

### RNF01 — Usabilidade

- Interface simples, sem menus complexos
- Funcionar bem em dispositivos móveis (design responsivo)
- Tempo de resposta da IA inferior a 5 segundos

### RNF02 — Acessibilidade

- Linguagem sempre simples, sem jargões técnicos
- Contraste adequado de cores para legibilidade

### RNF03 — Segurança

- Nenhum dado pessoal sensível deve ser coletado ou armazenado
- Variáveis de ambiente para chaves de API (nunca hardcoded)
- Proteção contra CSRF nos formulários Django

### RNF04 — Disponibilidade (MVP)

- Ambiente de desenvolvimento local
- Escalabilidade não é prioridade no MVP

---

## 5. User Stories

| ID    | Como...       | Quero...                                               | Para...                                            |
| ----- | ------------- | ------------------------------------------------------ | -------------------------------------------------- |
| US-01 | usuário leigo | descrever o que faço no computador em palavras simples | receber uma recomendação adequada                  |
| US-02 | usuário       | entender por que a IA recomendou aquela opção          | confiar na sugestão                                |
| US-03 | usuário       | saber se preciso de PC ou Notebook                     | não errar na hora da compra                        |
| US-04 | usuário       | indicar meu orçamento                                  | receber sugestões dentro do meu alcance financeiro |
| US-05 | usuário       | recomeçar a conversa                                   | testar cenários diferentes                         |

---

## 6. Escopo do MVP

### Dentro do Escopo (MVP)

- Chat com IA via interface web
- Recomendação ao final da conversa
- Histórico da sessão ativa
- Backend com Django + SQLite
- Integração com uma API de LLM (OpenAI ou Gemini)

### Fora do Escopo (Pós-MVP)

- Cadastro e login de usuários
- Histórico persistente entre sessões
- Links de produtos para compra
- Comparativo entre múltiplos modelos
- App mobile nativo
- Múltiplos idiomas

---

## 7. Critérios de Aceite do MVP

- [ ] Usuário consegue descrever sua necessidade em linguagem natural
- [ ] IA conduz a conversa com no mínimo 3 perguntas antes de recomendar
- [ ] Recomendação inclui tipo de máquina + especificações + justificativa
- [ ] Interface funciona em desktop e mobile
- [ ] Nenhuma chave de API exposta no código-fonte
