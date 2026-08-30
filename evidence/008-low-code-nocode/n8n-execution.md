# Execução n8n ativa — Spec 008

- Data: 2026-08-30.
- Stack: `app`, `catalog` e `n8n` subidos por Docker Compose.
- Workflow importado e ativado no n8n: `Ajuda Tech webhook`, ID interno `Cvnrk6Lw0GhkWXfI`.
- Após reiniciar o n8n, os logs registraram: `Activated workflow "Ajuda Tech webhook"`.
- Após o reset do volume, uma nova importação foi realizada e o workflow ficou disponível no editor.
- Healthcheck n8n: `{"status":"ok"}`.
- Exportação posterior confirmou `active: true`.

## Trigger

Foi chamado `POST http://localhost:5678/webhook/ajuda-tech` com payload sanitizado e sem credenciais. Após o reset e a nova importação, o n8n recebeu o trigger, porém retornou HTTP 500 porque o downstream respondeu indisponibilidade. O log da aplicação registrou `Erro ao processar resposta` e HTTP 503 em `/automation/webhook/`; portanto, a execução não produziu resposta normal HTTP 200.

## Resultado honesto

A ativação e o trigger real do n8n foram comprovados. A saída normal do workflow ainda não foi comprovada: o endpoint downstream depende do OpenRouter e pode retornar 503, e a execução pelo webhook n8n retornou 500. O cenário de falha é rastreável e não houve falso sucesso.

Os testes automatizados de payload inválido, assinatura inválida, duplicação e falha permanecem em `chat/tests/test_webhook.py`. A evidência de execução direta está em `docker-execution.md`.
