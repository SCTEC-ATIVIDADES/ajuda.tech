# Verificação documental — Spec 009

DATA: 2026-08-30
ESCOPO: stack integral em Docker Compose; catálogo HTTP local e n8n self-hosted local.

## Ambiente independente

- Clone limpo da branch `feature/specs-fase-final` executado em `/tmp/ajuda-tech-spec009-clean` e removido após execução.
- Compose iniciou `app`, `catalog`, `n8n-init` e `n8n`; workflow `Ajuda Tech webhook` foi importado e ativado.
- Catálogo `/healthz` e `/products`, app `/` e n8n `/healthz` responderam HTTP 200.
- Webhook n8n recebeu POST e executou Webhook → Validate and sign → Send to Ajuda Tech. O primeiro ensaio encontrou `429` da sessão; a causa e o limite estão documentados. Os testes automatizados do webhook cobrem sucesso, assinatura inválida, payload inválido, duplicata e falha.

## Paths, comandos e coerência

- README aponta para arquivos existentes de código, docs, specs, testes e evidências.
- Matriz de 15 critérios está em `README.md`.
- Instalação e execução oficial usam Docker: `docker compose up --build`.
- Validação oficial usa containers; host não precisa de Node/npm/Python.
- Fluxo principal, endpoints, sessão, limites, segurança, catálogo local e n8n conferem com código atual.
- Catálogo terceiro, HTTPS público n8n e deploy externo são N/A para escopo local; não são apresentados como funcionalidades.

## Resultados reproduzíveis

- Docker build: PASS.
- Lint frontend no container: PASS.
- Vitest: **99 passed em 9 arquivos**.
- Backend com fixture de teste isolando `CATALOG_API_URL`: **190 passed, 1 skipped**.
- `manage.py check`: PASS, 0 issues.
- `manage.py check --deploy`: exit 0, warnings esperados de ambiente local.
- `docker compose config -q`: PASS.
- Healthchecks de catálogo, app e n8n: PASS.
- `git diff --check`: PASS.

## Revisões

- Revisão IA documental registrada em `ai-review.md`; não é alegada como execução externa.
- Revisão humana registrada em `human-validation.md`.
- Nenhum segredo aparece nos artefatos.

## Resultado

Spec 009 concluída para escopo Docker-only. Itens de atividade oficial — vídeo, Kanban, permissões, aprovação/merge e submissão — permanecem fora desta spec e devem ser controlados em Spec 010.
