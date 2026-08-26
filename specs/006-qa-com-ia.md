# Spec 006 — QA com IA

## Resumo das lacunas

- Não há evidência de IA usada em code review de alteração real.
- Não há geração e refinamento documentados de testes por IA.
- Testes de integração/aceitação/E2E não estão organizados como evidência de risco.
- Não há priorização formal por risco.

## Planejamento detalhado

1. Escolher uma alteração real do projeto, preferencialmente rate limit, injection ou fluxo paralelo.
2. Usar IA para revisar diff, registrar achados e decisão humana.
3. Pedir geração de testes a partir dos critérios de aceite.
4. Revisar testes, corrigir casos incompletos e registrar refinamentos.
5. Separar testes unitários, integração endpoint/grafo e aceitação do fluxo.
6. Priorizar riscos: segurança, perda de contexto, falha externa, regressão de UX e custo.
7. Executar suíte e anexar resultados ao README.

## TODO

- [ ] Selecionar PR/commit real.
- [ ] Salvar prompt e resposta de code review.
- [ ] Registrar achados aceitos e rejeitados.
- [ ] Gerar testes com IA.
- [ ] Refinar testes com revisão humana.
- [ ] Adicionar integração/aceitação/E2E de maior risco.
- [ ] Criar matriz risco → teste → evidência.

## Dúvidas técnicas em aberto

- IA será usada via ferramenta local, revisão de PR ou modelo externo?
- Qual alteração fornece melhor evidência sem inventar trabalho?
- E2E precisa navegador real ou teste de endpoint cobre aceitação?
- Quais riscos recebem bloqueio obrigatório no CI?

## Critérios de aceite

- Existe alteração real revisada por IA, com diff e registro.
- Review identifica pelo menos riscos relevantes e decisões humanas ficam documentadas.
- IA gera testes que são executados e refinados.
- Há testes além de unidade para fluxo principal e falha.
- Cada risco crítico possui teste ou justificativa explícita.
- Resultado da suíte passa sem depender de API externa.

## Arquivos afetados

- Código da alteração escolhida.
- `chat/tests/`
- `chat/static/chat/js/*.test.js`
- `.github/workflows/ci.yml`
- `README.md`
- `docs/` ou diretório de evidências definido em [009](009-readme-evidencias.md)

## Evidências esperadas

- Diff revisado.
- Prompt/resposta da IA.
- Matriz de riscos.
- Testes gerados, refinados e resultado de execução.
- Relatório de cobertura e falhas corrigidas.

## Dependências

- [004](004-seguranca-governanca.md)
- [005](005-observabilidade-resiliencia.md)
- [007](007-devops-inteligente.md)
