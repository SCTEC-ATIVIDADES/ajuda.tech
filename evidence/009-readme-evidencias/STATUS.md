# Spec 009 — README e evidências

STATUS: DONE
SPEC: specs/009-readme-evidencias.md
ARQUIVOS: `README.md`; `docs/ESTRUTURA_PROJETO.md`; `docs/DIAGRAMA_SEQUENCIA.md`; `docs/FLUXO_USUARIO.md`; `.env.example`; evidências 006–009.

VALIDAÇÃO INDEPENDENTE: clone limpo da branch `feature/specs-fase-final` executado em `/tmp/ajuda-tech-spec009-clean` e removido após execução. Compose construiu e iniciou app, catálogo e n8n; `n8n-init` importou workflow e ativou `Ajuda Tech webhook`. Catálogo `/healthz` e `/products`, app `/` e n8n `/healthz` responderam normalmente. O webhook n8n recebeu e processou requisições, mas chamadas ao app retornaram `429` por rate limit da sessão; limitação registrada, não mascarada.

TESTES: clone limpo — build Docker, lint e Vitest 99 passed em 9 arquivos; backend com `CATALOG_API_URL=` para testes unitários, 190 passed, 1 skipped; `manage.py check` PASS; `check --deploy` exit 0 com warnings esperados; `docker compose config -q` PASS; catálogo, app e n8n healthchecks PASS. O teste Compose completo reproduziu 5 falhas de testes unitários por configurar catálogo HTTP externo por padrão; suíte passou com `CATALOG_API_URL=`. `git diff --check` PASS.

EVIDÊNCIAS: matriz de 15 critérios em `README.md`; revisão IA em `ai-review.md`; revisão humana em `human-validation.md`; verificação de links, paths e comandos em `verification.md`.

DECISÕES: documentação descreve código atual; estados usam `DONE`, `PARTIAL` e `BLOCKED`; execução externa não foi inventada; n8n é local/self-hosted; catálogo Compose é endpoint HTTP interno reproduzível, não serviço público de terceiro; esta revisão IA não executou modelo externo.

PENDÊNCIAS DESTA SPEC: nenhuma no escopo técnico/documental local. Catálogo terceiro, HTTPS público n8n, vídeo, Kanban, permissões e publicação externa pertencem à atividade oficial ou são N/A; não bloqueiam esta spec. Testes, paths, comandos e escopo Docker estão registrados.
PRÓXIMO AGENTE: specs/010-entrega-final.md
