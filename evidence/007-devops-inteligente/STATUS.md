# Spec 007 — DevOps inteligente

STATUS: PARTIAL
SPEC: specs/007-devops-inteligente.md
ALTERAÇÕES: CI executa Django check/migrations, backend com cobertura, frontend lint/testes, build Docker e análise determinística; analyzer calcula anomalia, tendência e risco; fixture contém duas etapas e observações repetidas; artefatos CI publicados; Docker Compose usa dependências da imagem; `.dockerignore` adicionado.
TESTES: `venv/bin/python manage.py check` passou; `venv/bin/python manage.py migrate --no-input` passou; `venv/bin/python -m pytest --cov=chat --cov-report=term-missing --cov-fail-under=80` passou: 147 testes, 93.02%; `venv/bin/python analyze_observability.py chat/tests/observability_fixture.json` passou; `docker build --no-cache --tag ajuda-tech-frontend-ci .` passou com `npm run lint` e `npm test`: 9 arquivos, 99 testes; `npm` continua ausente no host, mas frontend validado na imagem Docker.
EVIDÊNCIAS: `chat/tests/observability_fixture.json`; `chat/tests/test_observability_analysis.py`; `evidence/007-devops-inteligente/observability-analysis.json`; run verde CI `33275501844`: https://github.com/SCTEC-ATIVIDADES/ajuda.tech/actions/runs/33275501844; artefatos `observability-analysis.json` e `coverage.xml` publicados pelo job CI; execução local reproduzível pelos comandos acima.
DECISÕES: Sem chamada IA externa: gate usa análise determinística reproduzível e registra `ai_analysis.status=not_called`; anomalia acima de 500ms; tendência é variação percentual primeira→última observação; menos de duas observações implica incerteza alta; risco alto para falha, médio para anomalia, baixo caso contrário.
PENDÊNCIAS: Falha controlada de gate será validada em branch temporária; validação humana da resposta IA, IA externa e deploy permanecem BLOCKED conforme spec; prompt/resposta IA não existem porque IA externa não foi chamada.
PRÓXIMO AGENTE: specs/008-low-code-nocode.md
