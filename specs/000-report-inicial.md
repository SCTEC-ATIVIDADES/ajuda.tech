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

## TODO

### Critérios de avaliação

- [ ] **1. Vídeo — 1,00:** YouTube não listado, até 12 minutos, cobrindo aplicação e evidências.
- [ ] **2. Quadro GitHub — 0,50:** cards claros, coerentes e atualizados durante desenvolvimento.
- [ ] **3. Versionamento — 0,75:** `develop`, `feature/*` e `main`, commits semânticos e evolução rastreável.
- [ ] **4. README — 0,75:** solução compreensível, executável, avaliável e documentada.
- [ ] **5. Aplicação — 0,75:** ponta a ponta, domínio definido, dois cenários e saída estruturada.
- [ ] **6. LangGraph — 0,75:** state tipado, nodes, edges, sequência, condição, paralelização e parada.
- [ ] **7. Tool — 0,75:** integração funcional via MCP, API, serviço, backend ou webhook, com validação e falhas.
- [ ] **8. Memória — 0,75:** memória ou recuperação contextual adequada e demonstrável.
- [ ] **9. Segurança — 0,75:** segredos protegidos, entradas validadas, autonomia limitada e cenário adversarial.
- [ ] **10. Observabilidade/resiliência — 0,75:** logs estruturados, segundo sinal correlacionado, investigação, timeout/retry/fallback.
- [ ] **11. QA com IA — 0,50:** code review real, testes gerados/refinados, integração/aceitação/E2E e priorização por risco.
- [ ] **12. DevOps/anomalias — 0,50:** pipeline com lint, testes e build/validação; análise IA de logs, anomalia e risco.
- [ ] **13. Low-code/no-code — 0,50:** trigger, integração real, saída observável e reprodução documentada.
- [ ] **14. Prompts/modelos/refinamento:** prompts documentados, modelo por ambiente e ciclo de refinamento comprovado.
- [ ] **15. Análise crítica/evidências — 0,50:** problema, alteração, justificativa, resultado e provas do desenvolvimento.

**Total:** 10,00 pontos. Projeto pode receber nota zero por plágio, credenciais expostas, artefatos inacessíveis ou código não explicável na demonstração.

### Checklist final de entrega

#### Repositório e organização

- [ ] Repositório criado; professor adicionado; nenhum segredo ou `.env` versionado.
- [ ] Quadro Kanban atualizado durante desenvolvimento.
- [ ] Fluxo `develop → feature/* → develop → main` utilizado.
- [ ] Commits semânticos e coerentes com evolução real.
- [ ] Versão final funcional mantida em `main`.

#### Domínio, arquitetura e agente

- [ ] Problema, domínio e dois cenários definidos; um cenário envolve risco, falha, exceção ou anomalia.
- [ ] LangGraph implementa state, nodes, sequência, ramificação, paralelização e parada.
- [ ] Tool funcional integrada por MCP, API, serviço, backend ou webhook.
- [ ] Memória ou recuperação contextual adequada implementada.

#### Segurança, observabilidade e resiliência

- [ ] Payloads, parâmetros, schemas e permissões validados.
- [ ] Limites de autonomia e aprovação humana definidos quando necessários.
- [ ] Cenário adversarial de prompt injection ou entrada não confiável demonstrado.
- [ ] Logs estruturados e segundo sinal correlacionado registram fluxo, erros e latência.
- [ ] Timeout, retry limitado ou fallback aplicado quando necessário.

#### QA, DevOps e low-code

- [ ] Code review com IA realizado em alteração real.
- [ ] Testes relevantes gerados/refinados com IA, incluindo integração, aceitação ou E2E.
- [ ] Teste prioritário justificado por risco, impacto ou criticidade.
- [ ] Pipeline executa lint, testes e build/validação equivalente.
- [ ] IA analisou logs de duas etapas, detectou anomalia e estimou tendência/risco.
- [ ] Automação low-code/no-code integrada, com trigger e saída observável.

#### README e evidências

- [ ] README permite compreender, configurar, executar e avaliar solução.
- [ ] Prompts principais, modelo por variável de ambiente e ciclo de refinamento documentados.
- [ ] Evidências de testes, observabilidade, QA, DevOps e low-code organizadas.
- [ ] Link do vídeo incluído no README.

#### Vídeo e submissão

- [ ] Vídeo não listado, recomendado até 10 minutos e máximo de 12.
- [ ] Vídeo demonstra dois cenários, pipeline, análise de logs, anomalia, risco e low-code.
- [ ] Repositório e quadro contêm evidências do desenvolvimento individual.
- [ ] Links de repositório, quadro e vídeo submetidos no AVA antes de **31/08/2026 às 15h**.
- [ ] Repositório não alterado após entrega.
