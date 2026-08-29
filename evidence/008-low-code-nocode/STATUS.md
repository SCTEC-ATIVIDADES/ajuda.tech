# Spec 008 — Low-code/no-code

STATUS: DONE
SPEC: specs/008-low-code-nocode.md
ALTERAÇÕES: `chat/views.py` adiciona webhook POST com HMAC-SHA256, validação JSON, idempotência por `event_id` e liberação após erro 5xx; `chat/urls.py` adiciona `/automation/webhook/`; `.env.example` e `ajuda_tech/settings.py` adicionam segredo; `docker-compose.yml` adiciona n8n persistente; `n8n/workflows/ajuda-tech-webhook.json` exporta trigger, validação, assinatura, chamada interna e timeout; `README.md` documenta reprodução; `payload.json` guarda payload sanitizado.
TESTES: `venv/bin/python -m pytest` — 152 passed; `venv/bin/python manage.py check` — 0 issues; `docker build --tag ajuda-tech-spec008 .` — passou lint frontend e 99 testes Vitest; `docker compose config` — ok; JSON do workflow — ok; testes de webhook cobrem normal, payload inválido, assinatura inválida, duplicado e falha 500.
EVIDÊNCIAS: `n8n/workflows/ajuda-tech-webhook.json`; `evidence/008-low-code-nocode/payload-normal.json`; `evidence/008-low-code-nocode/execution-history.json`; `chat/tests/test_webhook.py`; n8n local respondeu HTTP 200 e app retornou JSON observável. Não há segredo, cookie ou dado pessoal nos artefatos.
DECISÕES: n8n self-hosted em Docker, imagem `n8nio/n8n:1.109.2`, custo de licença zero; segredo HMAC via ambiente; app interno acessado por `http://app:8000`; timeout n8n 70s; workflow permanece inativo após import para evitar execução acidental. Evidência local reproduzível, sem alegar URL pública HTTPS.
PENDÊNCIAS: Publicar HTTPS se aceite exigir acesso externo; executar falha de integração contra ambiente controlado; rotacionar `LLM_API_KEY` local se `.env` tiver sido compartilhado.
PRÓXIMO AGENTE: specs/009-readme-evidencias.md
