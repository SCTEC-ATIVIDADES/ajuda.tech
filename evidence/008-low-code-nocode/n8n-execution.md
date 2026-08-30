# Execução n8n ativa — Spec 008

- Data: 2026-08-30.
- Stack: `app`, `catalog` e `n8n` subidos por Docker Compose.
- Workflow importado e ativado no n8n: `Ajuda Tech webhook`, ID interno `NRymVumbwYr0lxQV`.
- Após reiniciar o n8n, os logs registraram: `Activated workflow "Ajuda Tech webhook"`.
- Healthcheck n8n: `{"status":"ok"}`.
- Exportação posterior confirmou `active: true`.

## Trigger

Foi chamado `POST http://localhost:5678/webhook/ajuda-tech` com payload sanitizado e sem credenciais. O n8n recebeu o trigger, porém retornou HTTP 500 porque a execução da etapa de código/integração não concluiu com sucesso. Os logs do n8n registram a ativação, mas a execução não produziu resposta normal HTTP 200.

## Resultado honesto

A ativação e o trigger real do n8n foram comprovados. A saída normal do workflow ainda não foi comprovada: o endpoint downstream depende do OpenRouter e pode retornar 503, e a execução pelo webhook n8n retornou 500. O cenário de falha é rastreável e não houve falso sucesso.

Os testes automatizados de payload inválido, assinatura inválida, duplicação e falha permanecem em `chat/tests/test_webhook.py`. A evidência de execução direta está em `docker-execution.md`.
