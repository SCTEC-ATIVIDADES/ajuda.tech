# Spec 006 — QA com IA

STATUS: PARTIAL
SPEC: specs/006-qa-com-ia.md
ALTERAÇÕES: adicionados/refinados testes de aceitação endpoint→grafo e falha de catálogo em `chat/tests/test_acceptance.py`; testes de grafo/catálogo/observabilidade; corrigidos contratos e fluxos de erro/reenvio em `chat/static/chat/js/chatApi.test.js`, `chatApi.errors.test.js` e `chatApp.test.js`; documentada matriz de rastreabilidade no `README.md`; criadas evidências sanitizadas em `evidence/006-qa-com-ia/`.
TESTES: Docker build PASS; backend em Docker — 146 passed, 93.11% coverage; foco QA — 29 passed; frontend em Docker — 99 passed em 9 arquivos; `python3 -m compileall -q chat` — PASS; `git diff --check` — PASS.
EVIDÊNCIAS: `evidence/006-qa-com-ia/ai-review.md`; `evidence/006-qa-com-ia/risk-matrix.md`; `evidence/006-qa-com-ia/test-results.txt`; commit real `aed90a4d9b80301db7cc121daa66b759bad099b0` e follow-ups até `dc6ef7e`; workflow `.github/workflows/ci.yml`.
DECISÕES: revisão IA foi registrada separada da decisão humana; testes não fazem rede externa; falhas de catálogo retornam resposta segura; itens não verificáveis localmente permanecem BLOCKED; nenhuma alteração funcional nova foi necessária nesta spec.
PENDÊNCIAS: instalar/executar ruff/mypy se adotados pelo projeto; validar links/execução em ambiente limpo; serviço externo real, vídeo e demais evidências externas permanecem BLOCKED.
PRÓXIMO AGENTE: specs/007 — executar após resolver bloqueios de frontend e evidências externas conforme disponibilidade.
