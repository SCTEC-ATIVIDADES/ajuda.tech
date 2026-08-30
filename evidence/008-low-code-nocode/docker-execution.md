# Execução Docker real — Spec 008

- Data: 2026-08-30.
- Stack: `app`, `catalog` e `n8n` iniciados por `docker compose up -d --build`.
- Healthcheck n8n: `{"status":"ok"}`.
- Aplicação respondeu `GET /` com HTTP 200.

## Cenários executados contra o endpoint real da aplicação

| Cenário | Resultado | Evidência |
|---|---:|---|
| Payload normal assinado | HTTP 503 | OpenRouter indisponível; não houve falso sucesso |
| Mesmo `event_id` novamente | HTTP 503 | Falha não foi convertida em sucesso; idempotência libera retry após 5xx |
| Payload inválido | HTTP 400 | Campos obrigatórios rejeitados |
| Assinatura inválida | HTTP 401 | Assinatura rejeitada |

## Observação

O endpoint real foi exercitado dentro da rede Docker. O cenário normal chegou à integração com o OpenRouter, mas a dependência LLM retornou indisponibilidade; por isso não houve resposta `200` nem saída de recomendação. Isso é evidência válida de falha rastreável, não de sucesso normal do workflow n8n.

O workflow exportado permanece disponível em `n8n/workflows/ajuda-tech-webhook.json`. A URL pública HTTPS e a ativação externa continuam fora do escopo do plano local.
