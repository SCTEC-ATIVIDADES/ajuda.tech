# Execução n8n ativa — Spec 008

- Data: 2026-08-30.
- Stack: `app`, `catalog` e `n8n` subidos por Docker Compose.
- Workflow importado e ativado automaticamente pelo serviço `n8n-init`: `Ajuda Tech webhook`.
- O bootstrap monta o export versionado, importa apenas quando marcador de volume não existe e preserva configuração em reinícios.
- Validação limpa executada em 2026-08-30T21:30Z com volume novo: `n8n-init` importou 1 workflow e o n8n iniciou com healthcheck HTTP 200. `n8n list:workflow --only-active` confirmou `Ajuda Tech webhook` ativo.
- Healthcheck n8n: `{"status":"ok"}`.
- O export versionado declara `active: true`; o runtime recebe essa configuração no bootstrap. O volume nomeado preserva workflow e credenciais internas entre reinícios.

## Trigger

Foi chamado `POST http://localhost:5678/webhook/ajuda-tech` com payload sanitizado e sem credenciais. Após importar a versão corrigida do workflow e reiniciar o n8n, o trigger retornou HTTP 200 com corpo JSON observável: `{"reply":"Qual é o seu orçamento aproximado?", "trace_id":"<uuid>", "run_id":"<uuid>"}`.

## Resultado honesto

A ativação, o trigger real e a saída normal do workflow foram comprovados. O cenário de falha continua coberto pelos testes automatizados, sem expor credenciais.

Os testes automatizados de payload inválido, assinatura inválida, duplicação e falha permanecem em `chat/tests/test_webhook.py`. A evidência de execução direta está em `docker-execution.md`.
