# Verificação documental — Spec 009

DATA: 2026-08-30
COMMIT: branch `feature/specs-fase-final`, validação em clone limpo antes deste registro

## Ambiente independente

- Clone temporário da branch `feature/specs-fase-final` criado em `/tmp/ajuda-tech-spec009-clean`, `.env` copiado somente para execução e removido ao final.
- Compose iniciou app, catálogo, `n8n-init` e n8n. O bootstrap importou e ativou `Ajuda Tech webhook`; `n8n list:workflow --only-active` confirmou o workflow.
- `GET /healthz` do catálogo e n8n retornou HTTP 200; `/products` retornou catálogo JSON; app retornou HTTP 200 e token CSRF.
- O webhook n8n recebeu POST e executou Webhook → Validate and sign → Send to Ajuda Tech. O app respondeu HTTP 429 por rate limit de sessão, portanto o fluxo n8n foi comprovado até a integração, mas resposta final de sucesso não foi declarada.

## Paths e links locais

- README aponta para arquivos existentes de código, docs, specs, testes e evidências.
- Matriz principal está em `README.md`, linhas 7–18.
- Evidências 006, 007, 008 e 009 possuem paths relativos válidos no repositório.
- URLs externas presentes são links fornecidos em artefatos anteriores; não foram tratadas como acessíveis nesta execução.

## Comandos documentados e executados

- Instalação: `python -m pip install -r requirements.txt`, `python manage.py migrate`.
- Backend: `python -m pytest`, `python manage.py check`, `python manage.py check --deploy`.
- Frontend: `npm ci`, `npm run lint`, `npm test`.
- Docker: `docker compose up --build`.

## Resultados do clone limpo

- Build Docker com lint e Vitest: **99 passed em 9 arquivos**.
- Backend com `CATALOG_API_URL=` para preservar testes unitários locais: **190 passed, 1 skipped**.
- `python manage.py check`: **PASS**, 0 issues.
- `python manage.py check --deploy`: exit 0, warnings esperados de ambiente inseguro.
- `docker compose config -q`: **PASS**.
- Catálogo, app e n8n: healthchecks e endpoints básicos **PASS**.
- Com Compose configurando catálogo HTTP, suíte reproduziu 5 falhas de testes unitários que esperam catálogo local; execução isolada com `CATALOG_API_URL=` passou. Isso é diferença de configuração de teste, não foi ocultado.

## Coerência

- Fluxo principal documentado como `POST /agent/send/`; `/send/` e `/recommend/` marcados como legados.
- Sessão Django, limite de 50 entradas, janela LLM de 20, mensagem de 4.000 caracteres e rate limit de 10/60s conferem com código auditado.
- Frontend Docker aprovado; host sem `node`/`npm` permanece limitação.
- Catálogo HTTP interno reproduzível e n8n local estão separados de validação externa.
- README não promete serviço externo de terceiro, HTTPS público, quantidade fixa de produtos, latência, lazy load ou histórico visível após reload.

## Resultado

Verificação de paths, coerência e execução independente concluída. Catálogo de terceiro, URLs externas, HTTPS público n8n e ambiente de produção não foram validados; dependências e credenciais externas não devem ser inferidas.
