# Spec 008 — Low-code/no-code

STATUS: DONE
SPEC: specs/008-low-code-nocode.md
ALTERAÇÕES: `chat/views.py` adiciona webhook POST com HMAC-SHA256, validação JSON, idempotência por `event_id` e liberação após erro 5xx; `chat/urls.py` adiciona `/automation/webhook/`; `.env.example` e `ajuda_tech/settings.py` adicionam segredo; `docker-compose.yml` adiciona n8n persistente e serviço `n8n-init`; `n8n/workflows/ajuda-tech-webhook.json` exporta trigger ativo, validação, assinatura, chamada interna e timeout; `README.md` documenta reprodução automática; `payload.json` guarda payload sanitizado.
TESTES: execução histórica `venv/bin/python -m pytest` — 152 passed. Execução final Docker — 191 collected, 190 passed, 1 skipped; `manage.py check` — 0 issues; frontend — lint passou e 99 testes Vitest; `docker compose config` — ok; JSON do workflow — ok. Testes de webhook cobrem normal, payload inválido, assinatura inválida, duplicado e falha 500.
EVIDÊNCIAS: `n8n/workflows/ajuda-tech-webhook.json`; `evidence/008-low-code-nocode/payload-normal.json`; `evidence/008-low-code-nocode/execution-history.json`; `evidence/008-low-code-nocode/docker-execution.md`; `evidence/008-low-code-nocode/n8n-execution.md`; `chat/tests/test_webhook.py`. Healthcheck n8n e trigger local retornaram HTTP 200; execução direta do app sem OpenRouter retornou HTTP 503; cenários inválido/assinatura retornaram 400/401. Não há segredo, cookie ou dado pessoal nos artefatos.
DECISÕES: n8n self-hosted em Docker, imagem `n8nio/n8n:1.109.2`, custo de licença zero; segredo HMAC via ambiente; app interno acessado por `http://app:8000`; timeout n8n 70s. O serviço `n8n-init` monta export versionado, importa e ativa workflow uma vez por volume; marcador `.ajuda-tech-workflow-imported` evita reimportação em reinícios. Não há URL pública HTTPS.
PENDÊNCIAS: URL pública HTTPS permanece fora do plano local. Rotacionar `LLM_API_KEY` se `.env` tiver sido compartilhado.
PRÓXIMO AGENTE: specs/009-readme-evidencias.md
