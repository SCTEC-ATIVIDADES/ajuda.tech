# Verificação documental — Spec 009

DATA: 2026-08-30T20:49:28Z
COMMIT: 6cbbe1f + alterações locais validadas
IMAGEM: ajuda-tech-spec009-final:latest
DIGEST: sha256:ba31f6fa2e47129e2ca07880b0e3c413df14a18e20ea9cc1256a5d339b808dc3

Execução Docker reproduzível registrada abaixo contra worktree atual; resultado só fica reproduzível por terceiros após commit/publicação destas alterações. Resultados anteriores são históricos.

## Paths e links locais

- README aponta para arquivos existentes de código, docs, specs, testes e evidências.
- Matriz principal está em `README.md`, linhas 7–18.
- Evidências 006, 007, 008 e 009 possuem paths relativos válidos no repositório.
- URLs externas já presentes são links fornecidos em artefatos anteriores; não foram tratados como acessíveis nesta execução.

## Comandos documentados

- Instalação: `python -m pip install -r requirements.txt`, `python manage.py migrate`.
- Backend: `python -m pytest`, `python manage.py check`, `python manage.py check --deploy`.
- Frontend: `npm ci`, `npm run lint`, `npm test`.
- Docker: `docker compose up --build`.

## Coerência

- Fluxo principal documentado como `POST /agent/send/`; `/send/` e `/recommend/` marcados como legados.
- Sessão Django, limite de 50 entradas, janela LLM de 20, mensagem de 4.000 caracteres e rate limit de 10/60s conferem com código auditado.
- Frontend Docker aprovado; host sem `node`/`npm` permanece limitação.
- Catálogo externo e n8n local estão separados de validação externa.
- README não promete quantidade fixa de produtos, latência, lazy load ou histórico visível após reload.

## Verificação Docker

Ambiente: Python 3.12.14, pytest 9.1.1, Django 5.2.17; variáveis de teste dummy, `DEBUG=True`.

- `docker build --no-cache --tag ajuda-tech-spec009:latest .` — PASS.
- `docker compose config -q` — PASS.
- `docker run ... python manage.py check` — PASS, 0 issues.
- `docker run ... python -m pytest -q` — 191 coletados, **190 passed, 1 skipped**.
- `docker run ... npm run lint` — PASS.
- `docker run ... npm test -- --run` — **99 passed em 9 arquivos**.
- `docker run ... python manage.py check --deploy` — exit 0, com warnings esperados W004/W008/W009/W012/W016/W018 por ambiente de teste inseguro.

Comandos completos usam imagem `ajuda-tech-spec009:latest`, `SECRET_KEY=django-insecure-ci-key-nao-usar-em-producao`, `LLM_API_KEY=sk-test-dummy-key-para-ci`, `DEBUG=True` e `ALLOWED_HOSTS=localhost,127.0.0.1`.

## Resultado

Verificação de paths, coerência e execução Docker concluída. Catálogo/URLs externas e ambiente de produção não foram validados; dependências e credenciais externas não devem ser inferidas.
