# Ajuda Tech

Assistente conversacional Django que traduz necessidades de compra em recomendações de computadores. Fluxo principal usa LangGraph, catálogo local validado e OpenRouter opcional.

## Estado da entrega

| Critério | Estado | Implementação → teste/evidência |
|---|---|---|
| Grafo LangGraph compilado | DONE | [`chat/agent/graph.py`](chat/agent/graph.py) → [`test_agent_graph.py`](chat/tests/test_agent_graph.py) |
| Estado tipado | DONE | [`chat/agent/state.py`](chat/agent/state.py) → [`test_agent_graph.py`](chat/tests/test_agent_graph.py) |
| Roteamento condicional | DONE | [`chat/agent/graph.py`](chat/agent/graph.py) → [`test_agent_graph.py`](chat/tests/test_agent_graph.py) |
| Fan-out/fan-in de catálogo | DONE | [`chat/agent/nodes.py`](chat/agent/nodes.py) → [`test_agent_graph.py`](chat/tests/test_agent_graph.py) |
| Tools read-only e whitelist | DONE | [`chat/agent/tools.py`](chat/agent/tools.py) → [`test_agent_tools.py`](chat/tests/test_agent_tools.py) |
| Catálogo local validado | DONE | [`produtos.json`](produtos.json) → [`test_agent_tools.py`](chat/tests/test_agent_tools.py) |
| Catálogo HTTP local, retry e fallback | DONE | [`chat/agent/tools.py`](chat/agent/tools.py) → [`test_catalog_integration.py`](chat/tests/test_catalog_integration.py); serviço Docker reproduzível |
| Memória e nova conversa | DONE | [`chat/views.py`](chat/views.py) → [`test_acceptance.py`](chat/tests/test_acceptance.py) |
| Limites de contexto e payload | DONE | [`chat/views.py`](chat/views.py) → [`test_limits.py`](chat/tests/test_limits.py) |
| Segurança, CSRF e injection | DONE | [`ajuda_tech/settings.py`](ajuda_tech/settings.py) → [`test_views.py`](chat/tests/test_views.py) |
| Observabilidade e resiliência | DONE | [`chat/observability.py`](chat/observability.py) → [`test_observability.py`](chat/tests/test_observability.py) |
| Frontend sanitizado em Docker | DONE | [`chatApp.js`](chat/static/chat/js/chatApp.js) → [`evidence/006-qa-com-ia/test-results.txt`](evidence/006-qa-com-ia/test-results.txt) |
| CI e build Docker | DONE | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) → [`evidence/007-devops-inteligente/STATUS.md`](evidence/007-devops-inteligente/STATUS.md) |
| Automação n8n local | DONE | [`n8n/workflows/ajuda-tech-webhook.json`](n8n/workflows/ajuda-tech-webhook.json) → [`evidence/008-low-code-nocode/STATUS.md`](evidence/008-low-code-nocode/STATUS.md) |
| Vídeo, Kanban, permissões e publicação externa | BLOCKED | Entrega externa, não necessária para execução local |

## Arquitetura

```text
POST /agent/send/
  -> valida JSON, CSRF, injection e rate limit
  -> sessão Django: histórico, necessidades, thread_id, run_id
  -> classify_msg
     -> greet
     -> gather_needs -> respond (dados insuficientes)
     -> prepare_catalog -> Send(notebook, desktop)
        -> catalog_worker -> consolidate_catalog
        -> compare_catalog_products -> recommend -> report -> respond
```

`AgentState` é um `TypedDict`. Reducers agregam mensagens, resultados de catálogo e erros. Falha de um ramo vira resultado parcial; não interrompe outros ramos. O contexto recuperado da sessão é incorporado ao estado antes da coleta de necessidades.

Código principal:

- [`chat/agent/state.py`](chat/agent/state.py): estado e tipos.
- [`chat/agent/graph.py`](chat/agent/graph.py): grafo e roteamento.
- [`chat/agent/nodes.py`](chat/agent/nodes.py): nós.
- [`chat/agent/tools.py`](chat/agent/tools.py): `buscar_produtos`, `comparar_produtos`, `gerar_relatorio`.
- [`chat/services.py`](chat/services.py): único ponto de contato com OpenRouter.
- [`chat/prompts.py`](chat/prompts.py): prompts internos, não exibidos ao usuário.
- [`chat/views.py`](chat/views.py): endpoints e sessão.

## Endpoints

| Método | Rota | Função |
|---|---|---|
| GET | `/` | Interface do chat |
| POST | `/agent/send/` | Fluxo principal LangGraph |
| POST | `/send/` | Fluxo legado direto com OpenRouter |
| POST | `/recommend/` | Fluxo legado de extração |
| POST | `/new/` | Limpa sessão e inicia conversa |
| POST | `/automation/webhook/` | Webhook HMAC para n8n |

## Catálogo, modelo e contexto

- Catálogo padrão: [`produtos.json`](produtos.json), 12 produtos.
- `CATALOG_API_URL` aponta para serviço HTTP de leitura; Compose usa o mock reproduzível `http://catalog:8080/products`. A resposta passa validação de schema e, em falha, usa catálogo local. `buscar_produtos` retorna JSON com `ok`, `origem`, `codigo`, `mensagem` e `produtos`; erros usam `catalog_unavailable` ou `invalid_argument`.
- `comparar_produtos` retorna JSON com `ok`, `codigo`, `origem` e `comparacao`; `gerar_relatorio` valida textos, tipo, preço e especificações antes de gerar Markdown.
- Integração HTTP é somente leitura, com timeout de `CATALOG_TIMEOUT` e até dois retries para timeout/conexão/5xx; o serviço local reproduzível não exige credencial. API externa de terceiros continua opcional e não é declarada como validada.
- OpenRouter usa `LLM_API_KEY`, `LLM_MODEL` e `LLM_TIMEOUT`. `LLM_PROVIDER` é mantido por compatibilidade, mas não altera a chamada atual.
- Histórico fica em cookie de sessão Django por até 24 horas; backend retém até 50 entradas e envia até 20 mensagens ao LLM. Mensagem máxima: 4.000 caracteres. Rate limit: 10 requisições por sessão em 60 segundos.
- `POST /new/` faz limpeza explícita. Recarregar página mantém sessão no backend, mas frontend não busca histórico antigo para renderização. Fechar/expirar sessão pode perder contexto.
- Não há banco de conversas nem checkpointer externo. SQLite serve às sessões e testes.

## Segurança

- CSRF global; frontend envia `X-CSRFToken`.
- Webhook usa HMAC-SHA256, `event_id`, deduplicação e validação de payload.
- Credenciais vêm de ambiente; `.env` não deve ser versionado. `.env.example` contém placeholders.
- Produção exige `DEBUG=False`, chave Django não padrão, `SECRET_KEY` e `LLM_API_KEY`.
- Ferramentas são whitelist read-only. Catálogo e Markdown são escapados; frontend usa DOMPurify.
- Entradas suspeitas são bloqueadas antes do LLM; dados do usuário são delimitados nos prompts.

## Instalação local

Requisito: Docker Engine com Docker Compose. Toda a stack e validação executam em containers.

```bash
git clone https://github.com/SCTEC-ATIVIDADES/ajuda.tech.git
cd ajuda.tech
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# edite SECRET_KEY e LLM_API_KEY
python manage.py migrate
python manage.py runserver
```

Acesse `http://localhost:8000`. Sem `LLM_API_KEY`, use testes ou configure uma chave antes de enviar mensagens ao agente.

## Docker

Crie `.env` conforme instalação local antes de iniciar Compose.

```bash
docker compose up --build
```

App fica em `http://localhost:8001`; n8n fica em `http://localhost:5678`.

## Testes e checks

```bash
python -m pytest
python manage.py check
python manage.py check --deploy
npm ci
npm run lint
npm test
```

CI também executa migração, cobertura mínima de 80%, análise offline de observabilidade e build Docker. Verificação Docker Spec 009: lint PASS, Vitest 99 passed/9 arquivos, backend 190 passed e 1 skipped com `CATALOG_API_URL=` para testes unitários, e `manage.py check` sem issues. `check --deploy` em ambiente de teste gera warnings esperados; produção exige variáveis seguras. `node`, `npm`, `ruff` e `mypy` podem não existir no host, conforme [`evidence/009-readme-evidencias/verification.md`](evidence/009-readme-evidencias/verification.md).

## n8n local

Configure `AUTOMATION_WEBHOOK_SECRET` e `N8N_ENCRYPTION_KEY` no `.env` e execute `docker compose up --build`. O serviço `n8n-init` importa o workflow versionado e o ativa automaticamente na primeira inicialização do volume; execuções seguintes reutilizam o volume. O n8n assina payload HMAC e chama `http://app:8000/automation/webhook/`. Use `http://localhost:5678/webhook/ajuda-tech`; resposta JSON é observável. Execução local não é URL HTTPS pública.

## Evidências

- Spec 006: [`evidence/006-qa-com-ia/`](evidence/006-qa-com-ia/): revisão IA, decisão humana, matriz de riscos e resultados Docker.
- Spec 007: [`evidence/007-devops-inteligente/`](evidence/007-devops-inteligente/): CI, fixture, análise determinística e validação humana.
- Spec 008: [`evidence/008-low-code-nocode/`](evidence/008-low-code-nocode/): workflow, payload sanitizado e histórico local.
- Spec 009: [`evidence/009-readme-evidencias/`](evidence/009-readme-evidencias/): verificação documental e revisão.

## Limitações e decisões

- Catálogo HTTP local roda em container separado e usa os mesmos dados versionados; serviço externo de terceiros não faz parte do escopo.
- Modelos gratuitos podem variar, falhar ou emitir marcadores de raciocínio; serviço filtra esses marcadores.
- Sem login, persistência entre sessões, comparação visual garantida, lazy load ou promessa de tempo de resposta.
- n8n é self-hosted em container Docker e validado localmente; HTTPS público não faz parte do escopo.
- LangGraph foi escolhido por tornar roteamento e fan-out/fan-in explícitos; sessão Django evita criar persistência adicional para MVP.

## Estrutura

```text
ajuda.tech/
├── ajuda_tech/                 # settings, URLs e WSGI
├── chat/
│   ├── agent/                  # grafo, nós, estado e tools
│   ├── static/chat/            # frontend JS/CSS
│   ├── templates/chat/         # template Django
│   ├── tests/                  # testes backend
│   ├── prompts.py              # prompts internos
│   ├── services.py             # OpenRouter
│   ├── views.py                # endpoints
│   └── urls.py                 # rotas
├── core/                       # app auxiliar não incluída nas rotas atuais
├── docs/                       # documentação
├── evidence/                   # evidências sanitizadas
├── n8n/workflows/              # exportação n8n
├── produtos.json
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── package.json
└── manage.py
```

## Referências

- [Estrutura](docs/ESTRUTURA_PROJETO.md)
- [Fluxo do usuário](docs/FLUXO_USUARIO.md)
- [Diagrama de sequência](docs/DIAGRAMA_SEQUENCIA.md)
- [PRD](docs/PRD.md)
- [User stories](docs/USER_STORIES.md)
- [Specs e contratos](specs/)
