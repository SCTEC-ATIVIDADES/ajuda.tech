# Spec 009 — README e evidências

## Resumo das lacunas

- README diverge do código em nós, endpoints, histórico, integrantes e paths.
- Não há mapa completo requisito → implementação → evidência.
- Prompts, modelo por ambiente e ciclo de refinamento não estão documentados como operação.
- Evidências de QA, logs, low-code, CI e cenários ainda não estão reunidas.

## Planejamento detalhado

1. Reescrever README a partir do código final, removendo plano antigo e links quebrados.
2. Documentar objetivo, arquitetura, fluxo, estado, tools, memória, segurança e operação.
3. Registrar prompt versionado, modelo por ambiente, parâmetros e mudanças de refinamento.
4. Criar tabela da rubrica com status, link de código, teste e evidência.
5. Referenciar logs sanitizados, relatórios, CI, workflow low-code e vídeo.
6. Documentar execução local, demo sem segredo, troubleshooting e limitações conhecidas.
7. Conferir integrantes, branches, comandos e endpoints.

## TODO

- [ ] Auditar todos links e paths.
- [ ] Atualizar arquitetura real.
- [ ] Documentar prompts e modelos por ambiente.
- [ ] Criar matriz de evidências.
- [ ] Adicionar cenários normal e risco/falha.
- [ ] Registrar decisões e limitações.
- [ ] Revisar README com IA e revisão humana.

## Dúvidas técnicas em aberto

- Evidências ficarão no repositório ou em links externos?
- Quais dados precisam ser anonimizados?
- README deve apontar vídeo não listado diretamente?
- Qual formato final exigido para anexos?

## Critérios de aceite

- README permite instalar, testar e executar demo sem conhecimento oculto.
- Todos endpoints, nós e arquivos citados existem.
- Cada item da rubrica aponta prova verificável.
- Prompts e ciclo de refinamento estão registrados.
- Modelo muda por ambiente sem alteração de código sensível.
- Limitações e riscos são declarados, não mascarados.

## Arquivos afetados

- `README.md`
- `docs/`
- `specs/`
- `.env.example`
- Arquivos de evidência e links do repositório

## Evidências esperadas

- README final revisado.
- Matriz de rastreabilidade.
- Histórico de prompt/refinamento.
- Links para CI, Kanban, logs, workflow, testes e vídeo.

## Dependências

- Todas as specs `001`–`008`.
- [010](010-entrega-final.md)
