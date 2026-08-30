# Spec 002 — Status

STATUS: DONE
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

- `docker compose up -d --build`: PASS; serviços `app`, `catalog` e `n8n` iniciados.
- `docker compose exec -T catalog ...`: PASS; `/products` respondeu HTTP 200 com 12 produtos e `/products/empty` respondeu HTTP 200 com lista vazia.
- `docker compose exec -T -e CATALOG_API_URL=http://catalog:8080/products app ... buscar_produtos`: PASS; retorno com `origem: externo`.
- `docker compose exec -T -e CATALOG_API_URL= app pytest -q`: PASS, 186 testes.
- `docker compose exec -T -e CATALOG_API_URL= app python manage.py check`: PASS, 0 issues.
- `docker compose exec -T -e CATALOG_API_URL= app python manage.py migrate --no-input`: PASS, sem migrações pendentes.
- Build da imagem app executou lint e Vitest: 99 testes em 9 arquivos.

## Evidências

- `catalog_service.py` e `catalog.Dockerfile`: serviço HTTP local versionado.
- `docker-compose.yml`: rede app → catalog por `http://catalog:8080/products`.
- `integration-success.json`: resposta sanitizada de sucesso.
- `integration-failure.json`: cenários vazio, 503 e rota inexistente.
- `commands.txt`: comandos e resultados reproduzíveis.
- `chat/tests/test_agent_tools.py`
- `chat/tests/test_catalog_integration.py`
- `chat/agent/tools.py`

## Decisões

- Integração externa usa `CATALOG_API_URL`, sem credenciais versionadas.
- Testes simulam respostas para não depender de rede.
- Falhas de integração não interrompem recomendação quando catálogo local está disponível.

## Pendências

- API externa de terceiros não foi acionada; não é requisito do aceite local e permanece opcional.

## Próximo

Executar Spec 003 após publicação desta entrega.
