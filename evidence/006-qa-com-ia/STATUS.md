# Spec 006 — QA com IA

STATUS: DONE
SPEC: specs/006-qa-com-ia.md
ALTERAÇÕES: adicionados/refinados testes de aceitação endpoint→grafo e falha de catálogo em `chat/tests/test_acceptance.py`; testes de grafo/catálogo/observabilidade; corrigidos contratos e fluxos de erro/reenvio em `chat/static/chat/js/chatApi.test.js`, `chatApi.errors.test.js` e `chatApp.test.js`; documentada matriz de rastreabilidade no `README.md`; criadas evidências sanitizadas em `evidence/006-qa-com-ia/`.
TESTES: Docker build PASS; backend em Docker — 190 passed, cobertura acima de 80%; frontend em Docker — 99 passed em 9 arquivos; foco QA e rastreabilidade — PASS; `git diff --check` — PASS.
EVIDÊNCIAS: `evidence/006-qa-com-ia/ai-review.md`; `evidence/006-qa-com-ia/traceability.md`; `evidence/006-qa-com-ia/risk-matrix.md`; `evidence/006-qa-com-ia/test-results.txt`; commits reais `aed90a4`, `92405f0`, `df07614`, `89e356c`, `58601e0`, `d603fdc`; workflow `.github/workflows/ci.yml`.
DECISÕES: revisão IA e decisão humana foram registradas separadamente; geração/refinamento de testes está rastreável em `traceability.md`; testes não fazem rede externa; falhas de catálogo retornam resposta segura; `ruff`/`mypy` não são gates deste projeto; itens externos pertencem às Specs 009–010.
PENDÊNCIAS: nenhuma pendência técnica desta spec. Vídeo, publicação, permissões e ambiente público permanecem nas Specs 009–010.
PRÓXIMO AGENTE: specs/007.
