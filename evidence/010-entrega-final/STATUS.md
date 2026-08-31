# Spec 010 — Entrega final

STATUS: PARTIAL/BLOCKED
SPEC: specs/010-entrega-final.md
VERSAO: feature/specs-fase-final @ 9f54674ec6f280ba97a67f14e782d2286441b356

## Validação local

- `git diff --check origin/main...HEAD`: PASS.
- `docker compose config -q`: PASS.
- CI remoto do PR #34: 6 checks PASS.
- Evidência anterior: backend 190 passed, 1 skipped; frontend 99 passed em 9 arquivos; cobertura 94,77%; build Docker PASS; migrations/check PASS.
- Cenário normal: coberto por `chat/tests/test_acceptance.py::test_agent_recommendation_persists_session_across_requests`.
- Cenário de risco: injection e catálogo indisponível cobertos por `chat/tests/test_acceptance.py` e `chat/tests/test_security.py`.
- Host atual não possui `python` nem `npm`; validação local direta não executou.

## Rastreabilidade Git/GitHub

- `main`: `e183b10`.
- `feature/specs-fase-final`: `9f54674`, alinhada ao remoto.
- `develop`: ausente local/remoto.
- Commits semânticos: 29/29 válidos.
- PR: https://github.com/SCTEC-ATIVIDADES/ajuda.tech/pull/34
- PR aberto, `BLOCKED`, aprovação requerida; 6 checks PASS.
- Project: https://github.com/orgs/SCTEC-ATIVIDADES/projects/1
- PR #34 aparece no Project, sem responsável/status explícito.

## Bloqueios externos

- Criar/publicar branch `develop`.
- Obter aprovação obrigatória e concluir/fechar PR #34.
- Definir responsável/status do item no GitHub Project.
- Gravar vídeo não listado, validar duração e publicar URL.
- Capturar cenários normal/risco em mesma versão.
- Testar links em janela anônima.
- Submeter no AVA e anexar comprovante.
- Confirmar prazo operacional e congelar repositório.

## Pendências

Ação humana necessária. Não marcar entrega final como DONE, submissão como feita ou repositório como congelado até resolver bloqueios acima.
