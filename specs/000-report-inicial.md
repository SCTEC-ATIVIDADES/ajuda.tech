# Report inicial — fase final

## Objetivo

Levar Ajuda Tech de MVP funcional a entrega final demonstrável, cobrindo LangGraph, integração, memória, segurança, observabilidade, QA com IA, DevOps, automação low-code/no-code e evidências.

## Diagnóstico

Projeto já possui Django, OpenRouter, LangGraph, estado compartilhado, roteamento condicional, catálogo local, tools, sessão, prompts centralizados, testes backend/frontend e retry. Lacunas abaixo são somente requisitos ainda ausentes ou não comprovados para fase final.

## Specs

1. [LangGraph completo](001-langgraph-completo.md) — paralelização, estado e fluxo executável.
2. [Tools e integrações](002-tools-integracoes.md) — tool externa, contratos, validação e erros.
3. [Memória e contexto](003-memoria-contexto.md) — janela, persistência, recuperação e privacidade.
4. [Segurança e governança](004-seguranca-governanca.md) — injection, limites, segredos e autonomia.
5. [Observabilidade e resiliência](005-observabilidade-resiliencia.md) — logs correlacionados, sinais, timeout e fallback.
6. [QA com IA](006-qa-com-ia.md) — code review, testes gerados/refinados e risco.
7. [DevOps inteligente](007-devops-inteligente.md) — CI, análise de logs, anomalia e risco.
8. [Low-code/no-code](008-low-code-nocode.md) — trigger, integração real e saída observável.
9. [README e evidências](009-readme-evidencias.md) — documentação, provas e rastreabilidade.
10. [Entrega final](010-entrega-final.md) — cenários, vídeo, Kanban, branches e submissão.

## Ordem sugerida

`001 → 002 → 003 → 004 → 005 → 006 → 007 → 008 → 009 → 010`

## Dependências globais

- Chave OpenRouter para demonstração real.
- Ambiente separado para testes e produção.
- Definição de ferramenta externa e automação low-code.
- Acesso ao GitHub Project e repositório.
- Capturas de execução, logs e resultados de CI.

## Riscos principais

- Dependência de API externa durante demo.
- Divergência entre documentação e código.
- Evidência insuficiente de requisitos feitos fora do código.
- Exposição de dados de conversa em logs ou sessão.
- Entrega sem cenário adversarial reproduzível.

## Critério global

Cada item da rubrica deve possuir implementação verificável, teste ou execução reproduzível e evidência vinculada no README.
