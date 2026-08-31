# Estrutura do Projeto

Projeto Django sem login obrigatório. Conversa fica em sessão assinada; modelos de conversa permanecem desativados. Grafo e integração LLM ficam separados da camada HTTP.

```text
ajuda.tech/
├── ajuda_tech/
│   ├── settings.py              # ambiente, segurança e sessão
│   ├── urls.py                  # inclui chat.urls
│   └── wsgi.py
├── chat/
│   ├── agent/
│   │   ├── graph.py             # StateGraph, rotas e Send
│   │   ├── nodes.py             # nós do agente
│   │   ├── state.py             # AgentState e reducers
│   │   └── tools.py             # catálogo, comparação e relatório
│   ├── static/chat/             # JS, CSS e testes Vitest
│   ├── templates/chat/chat.html
│   ├── tests/                   # pytest-django
│   ├── prompts.py               # prompts internos
│   ├── services.py              # único cliente OpenRouter
│   ├── views.py                 # endpoints, sessão e webhook
│   └── urls.py
├── core/                        # app auxiliar; não incluída nas rotas atuais
├── docs/                        # documentação
├── evidence/                    # evidências sanitizadas
├── n8n/workflows/               # workflow exportado
├── produtos.json                # catálogo local
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── package.json
├── pytest.ini
├── vitest.config.js
└── manage.py
```

## Fluxo principal

`POST /agent/send/` valida JSON, tamanho, CSRF, injection e rate limit. Depois cria `AgentState`, invoca o grafo e salva histórico/necessidades na sessão.

```text
START → classify_msg
  ├── greet → END
  ├── gather_needs → respond
  └── prepare_catalog → Send(notebook, desktop)
       → catalog_worker → consolidate_catalog
       → compare_catalog_products → recommend → report → respond → END
```

Falha de ramo de catálogo é registrada como resultado parcial.

## Componentes

### `chat/agent/state.py`

`AgentState` tipado contém mensagens, necessidades, trabalhos/resultados de catálogo, erros, recomendação, relatório, IDs de execução e metadados de prazo. Reducers agregam resultados paralelos.

### `chat/agent/tools.py`

Whitelist fixa de três tools read-only:

- `buscar_produtos`: valida categoria/orçamento e consulta catálogo.
- `comparar_produtos`: compara dois IDs válidos.
- `gerar_relatorio`: produz Markdown escapado.

Catálogo externo é opcional via `CATALOG_API_URL`. Resposta passa schema; timeout, conexão e HTTP 5xx têm até duas tentativas; falha usa catálogo local.

### `chat/services.py`

Cliente OpenRouter. Usa `LLM_API_KEY`, `LLM_MODEL`, `LLM_TIMEOUT`, headers de site e limites de tokens. Retenta timeout, conexão e HTTP 5xx; não retenta erros 4xx de autenticação, cobrança ou limite.

### `chat/prompts.py`

Único local de system prompts e instruções de classificação, extração e resposta. Conteúdo é interno e não deve ser exposto.

### `chat/views.py`

Rotas principais: `/`, `/agent/send/`, `/send/`, `/recommend/`, `/new/` e `/automation/webhook/`. Histórico máximo 50 entradas; janela LLM máxima 20 mensagens; mensagem máxima 4.000 caracteres; corpo máximo 8.192 bytes; rate limit 10 requisições por sessão em 60 segundos.

### Frontend

Django template envia CSRF. `marked` renderiza Markdown e `DOMPurify` sanitiza HTML. Estado exibido vive em memória; reload não consulta histórico persistido no backend.

## Ambiente e execução

```bash
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Docker executa migração e servidor; imagem também valida lint e testes frontend durante build.

```bash
docker compose up --build
```

## Segurança

CSRF global; webhook usa HMAC-SHA256 e deduplicação de `event_id`; produção exige configurações seguras; credenciais ficam fora do Git; catálogo e saída Markdown são validados/escapados.

## Estado documental

Este arquivo descreve código existente, não plano futuro. Itens externos sem execução comprovada permanecem `PARTIAL` ou `BLOCKED` na matriz do [README](../README.md).
