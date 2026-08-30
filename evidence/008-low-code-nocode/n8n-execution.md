# Execução n8n ativa — Spec 008

- Data: 2026-08-30.
- Stack: `app`, `catalog` e `n8n` subidos por Docker Compose.
- Workflow importado e ativado no n8n: `Ajuda Tech webhook`, ID interno `Cvnrk6Lw0GhkWXfI`.
- Após reiniciar o n8n, os logs registraram: `Activated workflow "Ajuda Tech webhook"`.
- Após o reset do volume, uma nova importação foi realizada e o workflow ficou disponível no editor.
- Healthcheck n8n: `{"status":"ok"}`.
- O runtime registrou workflow ativo; isso não altera o export versionado, que mantém `active: false`. Estado runtime observado em 2026-08-30, workflow ID `Cvnrk6Lw0GhkWXfI`; não há export runtime anexado para provar persistência após reinício.

## Trigger

Foi chamado `POST http://localhost:5678/webhook/ajuda-tech` com payload sanitizado e sem credenciais. Após importar a versão corrigida do workflow e reiniciar o n8n, o trigger retornou HTTP 200 com corpo JSON observável: `{"reply":"Qual é o seu orçamento aproximado?", "trace_id":"<uuid>", "run_id":"<uuid>"}`.

## Resultado honesto

A ativação, o trigger real e a saída normal do workflow foram comprovados. O cenário de falha continua coberto pelos testes automatizados, sem expor credenciais.

Os testes automatizados de payload inválido, assinatura inválida, duplicação e falha permanecem em `chat/tests/test_webhook.py`. A evidência de execução direta está em `docker-execution.md`.
