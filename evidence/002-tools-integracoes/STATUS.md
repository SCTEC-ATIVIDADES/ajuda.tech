# Spec 002 — Status

STATUS: PARTIAL
SPEC: 002-tools-integracoes

## Aceite verificado

- `buscar_produtos` valida argumentos e catálogo antes de filtrar.
- Catálogo externo configurado retorna `origem: externo`.
- Falha externa usa catálogo local como fallback.
- Falha local e fallback inválido retornam erro normalizado `catalog_unavailable`.
- `comparar_produtos` retorna contrato JSON com `ok`, `codigo`, `origem` e `comparacao`.
- `gerar_relatorio` rejeita nome e justificativa vazios.
- Integração permanece somente leitura e sem ações destrutivas.

## Testes Docker

- `docker build --tag ajuda-tech-spec002 .`: PASS; lint e Vitest: 99 testes em 9 arquivos.
- `docker run ... python manage.py check`: PASS, 0 issues.
- `docker run ... python manage.py migrate --no-input`: PASS.
- `docker run ... pytest -q chat/tests/test_agent_tools.py chat/tests/test_catalog_integration.py`: 24 passed.
- `docker run ... pytest -q`: 172 passed.

## Evidências

- `chat/tests/test_agent_tools.py`
- `chat/tests/test_catalog_integration.py`
- `chat/agent/tools.py`

## Decisões

- Integração externa usa `CATALOG_API_URL`, sem credenciais versionadas.
- Testes simulam respostas para não depender de rede.
- Falhas de integração não interrompem recomendação quando catálogo local está disponível.

## Pendências

- Executar contra serviço externo real e registrar payload/log sanitizado; permanece BLOCKED sem serviço ou credencial fornecidos.
- Executar validação Docker completa antes do fechamento.

## Próximo

Executar Spec 003 após resolver ou registrar bloqueio externo.
