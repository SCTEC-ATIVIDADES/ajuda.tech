
## Validação de merge

- PR: https://github.com/SCTEC-ATIVIDADES/ajuda.tech/pull/34
- O primeiro run após a atualização do CI falhou no teste `test_agent_catalog_failure_returns_safe_response_and_persists_session`; a falha foi corrigida no commit `cc987f9`.
- Run de recuperação: https://github.com/SCTEC-ATIVIDADES/ajuda.tech/actions/runs/33294057307
- Checks aprovados: `Testes automatizados (Python 3.12)`, `Testes frontend (Node.js)` e `Validar imagem Docker`.
- Estado do PR após a recuperação: `CLEAN`.
- Branch protection formal não pôde ser configurada: GitHub retornou HTTP 403 informando que o recurso exige GitHub Pro ou repositório público.
