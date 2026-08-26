# Spec 007 — DevOps inteligente

## Resumo das lacunas

- CI roda Python, mas job Vitest está comentado.
- Lint, build/validação e verificação de deploy não formam gate completo.
- Não há análise de logs de duas etapas com anomalia e tendência/risco.
- Deploy Docker usa `runserver` e não está pronto para produção.

## Planejamento detalhado

1. Ativar CI frontend e definir comandos reais de lint, testes e build/validação.
2. Adicionar migração/checks Django e cobertura ao pipeline.
3. Rodar testes sem credenciais externas.
4. Adicionar validação de configuração de produção sem expor segredos.
5. Substituir `runserver` por servidor apropriado ou documentar claramente escopo de demo.
6. Criar fixture de logs de pelo menos duas etapas do agente.
7. Usar IA para identificar anomalia, estimar tendência simples e classificar risco.
8. Registrar método, dados, limites e conclusão humana.

## TODO

- [ ] Descomentar/corrigir job Vitest.
- [ ] Confirmar lint Python/JS existente ou adicionar somente ferramenta necessária.
- [ ] Adicionar build/collectstatic/check deploy conforme ambiente.
- [ ] Corrigir Dockerfile/Compose para execução reproduzível.
- [ ] Criar fixture de logs correlacionados.
- [ ] Criar análise de anomalia e tendência.
- [ ] Publicar artefatos de CI.

## Dúvidas técnicas em aberto

- Qual servidor será usado em produção?
- Build frontend existe ou validação é somente Vitest?
- Análise de logs será script Python, notebook ou workflow externo?
- Qual limiar define anomalia e risco aceitável?

## Critérios de aceite

- CI bloqueia merge quando lint, testes ou validação falham.
- Backend e frontend executam em CI.
- Pipeline não depende de LLM ou rede externa para testes.
- Logs de duas etapas são analisados por IA com anomalia, tendência e risco.
- Análise informa dados usados e incerteza.
- Artefatos e status do CI ficam acessíveis como evidência.

## Arquivos afetados

- `.github/workflows/ci.yml`
- `Dockerfile`
- `docker-compose.yml`
- `package.json`
- Configuração de lint/build existente
- Novo script/fixture de análise
- `README.md`

## Evidências esperadas

- Run verde do CI.
- Run vermelho controlado mostrando gate.
- Logs de duas etapas.
- Saída da análise IA.
- Imagem ou link do pipeline e artefatos.

## Dependências

- [005](005-observabilidade-resiliencia.md)
- [006](006-qa-com-ia.md)
- [009](009-readme-evidencias.md)
