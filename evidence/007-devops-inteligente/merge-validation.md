
## Validação de merge

- PR: https://github.com/SCTEC-ATIVIDADES/ajuda.tech/pull/34
- O primeiro run após a atualização do CI falhou no teste `test_agent_catalog_failure_returns_safe_response_and_persists_session`; a falha foi corrigida no commit `cc987f9`.
- Run de recuperação: https://github.com/SCTEC-ATIVIDADES/ajuda.tech/actions/runs/33294057307
- Checks aprovados: `Testes automatizados (Python 3.12)`, `Testes frontend (Node.js)` e `Validar imagem Docker`.
- Estado do PR após a recuperação: `CLEAN`.
- Branch protection configurada em `main` após o repositório tornar-se público.
- Regras ativas: check obrigatório `Testes automatizados (Python 3.12)`, branch atualizada antes do merge, uma aprovação obrigatória, administradores incluídos e force-push/delete desabilitados.
- Evidência operacional: PR permanece `BLOCKED` enquanto a aprovação obrigatória não existe, mesmo com todos os checks verdes.
