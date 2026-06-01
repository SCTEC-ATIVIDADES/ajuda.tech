# CLAUDE.md — Ajuda Tech

## Visão Geral do Projeto

**Ajuda Tech** é uma aplicação web com IA integrada que ajuda usuários leigos a escolherem o computador ideal (PC ou Notebook) através de uma conversa natural. O assistente se chama **Herbert** e nunca usa jargões técnicos com o usuário.

**Proposta de valor:** "Você descreve o que quer fazer. Nós indicamos o computador certo para você."

---

## Stack Técnica

| Camada       | Tecnologia                                        |
|--------------|---------------------------------------------------|
| Linguagem    | Python 3.12+                                      |
| Framework    | Django 5.x                                        |
| Banco        | SQLite com persistência (models `Conversation` e `Message`) |
| IA           | OpenRouter API (via `requests`, modelo padrão: `deepseek/deepseek-v4-flash:free`) |
| Frontend     | Django Templates + HTML/CSS + módulos JS (Vitest) |
| Sessão       | `django.contrib.sessions.backends.db` (banco, 24h) |

**Sem login, sem autenticação de usuários. A sessão Django identifica cada conversa.**

---

## Estrutura do Projeto

```
ajuda.tech/
├── ajuda_tech/              # Configurações Django (settings, urls, wsgi)
├── core/                    # App da landing page
│   ├── views.py
│   ├── urls.py
│   └── templates/core/index.html
├── chat/                    # App principal do assistente
│   ├── views.py             # ChatView, SendMessageView, RecommendView
│   ├── services.py          # Classe OpenRouterClient — único ponto de contato com a API
│   ├── prompts.py           # System prompts — NÃO misturar com services
│   ├── exceptions.py        # Hierarquia de exceções customizadas
│   ├── models.py            # Conversation, Message
│   ├── urls.py
│   ├── tests/               # Testes Python (pytest-django)
│   │   ├── test_views.py
│   │   ├── test_services.py
│   │   ├── test_prompts.py
│   │   ├── test_models.py
│   │   └── test_limits.py   # Features pendentes marcadas com xfail
│   ├── templates/chat/chat.html
│   └── static/chat/
│       ├── css/chat.css
│       └── js/              # chatApi.js, chatApp.js, chatUi.js, chatState.js, chatTheme.js
│                            # + testes Vitest (*.test.js, *.edge.test.js)
├── prompts/                 # Histórico de sessões de prompts (arquivos .md datados)
├── docs/                    # PRD, User Stories, Diagramas, Fluxo
├── prompts.md               # Documentação do system prompt do Herbert
├── AGENTS.md                # Instruções de arquitetura para agentes de IA (Cursor, Copilot)
├── VIABILIDADE.md           # Análise de viabilidade técnica e de negócio
├── package.json             # Dependências JS (Vitest)
├── vitest.config.js
├── requirements.txt
└── manage.py
```

---

## Arquivos Críticos

### `chat/services.py` — classe `OpenRouterClient`
Único ponto de contato com a API OpenRouter. Implementa:
- `chat_completion(messages)` — envia histórico, retorna resposta do Herbert
- `get_product_recommendations(history)` — gera lista de 3 produtos em JSON (budget/ideal/premium)
- Retry com exponential backoff para erros 5xx e timeout
- Contador separado para 429 (`max_rate_limit_retries=10`)
- Suporte a HTTP 402 (sem créditos no OpenRouter)
- Remoção de blocos `<think>...</think>` que alguns modelos (ex: DeepSeek) incluem

### `chat/prompts.py`
System prompts isolados aqui. Nunca embutir prompts em `views.py` ou `services.py`.
- `SYSTEM_PROMPT` — instruções do Herbert
- `PRODUCT_EXTRACTION_PROMPT` — instrução para gerar o JSON de produtos
- `temperature: 0.7`, `max_tokens: 800` (chat) / `1500` (extração de produtos)

### `chat/exceptions.py`
Hierarquia de exceções customizadas derivadas de `OpenRouterError`:
- `AuthenticationError` — HTTP 401
- `RateLimitError` — HTTP 429 (carrega `retry_after`)
- `ServiceUnavailableError` — 5xx, timeout, erro de rede
- `InvalidResponseError` — JSON inválido ou estrutura inesperada

### `chat/static/chat/js/chatUi.js`
Renderização de mensagens no DOM. Cada mensagem do bot é estruturada em dois elementos filhos:
- `.chat-message-content` — HTML renderizado do markdown
- `.chat-message-actions` — contém `.chat-copy-btn` (sempre) e `.chat-share-btn` (quando `navigator.share` disponível)

O botão de cópia usa `navigator.clipboard.writeText()` e exibe feedback visual ("Copiado!" por 2 segundos). O botão de compartilhar usa a Web Share API (disponível principalmente em mobile).

### `chat/views.py`
- `GET /chat/` → `ChatView` — renderiza a interface, limpa sessão a cada carregamento
- `POST /chat/send/` → `SendMessageView` — recebe `{"message": "..."}`, retorna `{"reply": "..."}`
- `POST /chat/recommend/` → `RecommendView` — retorna `{"products": [...]}`
- Persiste mensagens via `Message.objects.create()` (banco, não sessão)

### `chat/models.py`
- `Conversation` — vinculada à `session_key`, tem flag `is_completed`
- `Message` — role (`user` | `assistant`) + content + timestamp
- `Conversation.get_history()` retorna `list[dict]` com `role` e `content`

---

## Features pendentes (xfail em `chat/tests/test_limits.py`)

Documentadas no código, ainda não implementadas:

| Feature | Onde implementar |
|---|---|
| Limite de 50 mensagens por sessão | `chat/views.py` — `SendMessageView` |
| Janela de 20 mensagens enviadas à LLM | `chat/services.py` — `chat_completion()` |
| Rate limiting de 10 msgs/min por sessão | `chat/views.py` ou middleware |

---

## Comportamento da IA (Herbert)

O assistente **deve coletar estas 4 informações antes de recomendar**:
1. Finalidade (trabalho, estudo, jogos, uso básico, design)
2. Mobilidade (fica em casa ou precisa carregar)
3. Orçamento aproximado
4. Exigência especial (durabilidade, tela grande, bateria longa)

**Regras de comportamento:**
- Fazer **UMA pergunta por vez**
- Nunca recomendar antes de ter as informações essenciais
- Fallback após 8 trocas: recomendar com o que tem
- Redirecionar gentilmente se o usuário fugir do tema

**Formato da recomendação final — sempre 3 opções (JSON):**
- `budget` — opção mais barata que resolve o problema
- `ideal` — melhor custo-benefício
- `premium` — durabilidade e desempenho futuros

---

## Variáveis de Ambiente

```env
SECRET_KEY=                        # Chave secreta Django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
LLM_API_KEY=                       # Chave da API OpenRouter
LLM_PROVIDER=openai                # openai ou gemini (via OpenRouter)
LLM_MODEL=deepseek/deepseek-v4-flash:free
LLM_TIMEOUT=30
SITE_URL=http://localhost:8000
SITE_NAME=Ajuda Tech
LOG_LEVEL=INFO
```

**Nunca hardcodar chaves no código-fonte.** Usar `python-decouple` (`config()`).

---

## Como Rodar o Projeto

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
pip install -r requirements.txt
cp .env.example .env            # preencher com LLM_API_KEY e SECRET_KEY
python manage.py migrate
python manage.py runserver
# Acesse: http://localhost:8000

# Testes Python
pytest

# Testes JavaScript
npm install
npx vitest run
```

---

## Logging

Configurado em `settings.py` com `RotatingFileHandler`:
- `logs/app.log` — nível INFO, máx 5 MB × 5 arquivos
- `logs/errors.log` — nível WARNING+, máx 5 MB × 5 arquivos

---

## Convenções

- **Apps Django:** minúsculo (`chat`, `core`)
- **Views e URLs:** snake_case (`send_message`, `recommend`)
- **Templates:** snake_case + `.html`
- **Commits:** descritivos em português ou inglês (prefixo `feat:`, `fix:`, `docs:`, `ci:`)
- **Branches:** `feature/<nome>`, `fix/<nome>`, `docs/<nome>`

---

## Segurança

- Proteção CSRF ativa em todos os formulários Django
- Nenhum dado pessoal sensível coletado ou armazenado
- Validação de input do lado do servidor (não confiar apenas no frontend)
- Sanitizar entradas para evitar prompt injection

---

## Escopo atual

**Implementado:**
- Chat conversacional com IA (Herbert)
- Persistência de conversa em banco SQLite por sessão
- Endpoint de extração de recomendações em JSON estruturado (3 opções)
- Interface responsiva (desktop + mobile) com módulos JS separados
- Testes Python (pytest) e JavaScript (Vitest)
- Logging rotativo em arquivo
- Botão de copiar/compartilhar em cada mensagem do bot (clipboard API + Web Share API)

**Pendente (xfail):**
- Limite de 50 mensagens por sessão
- Janela de 20 mensagens enviadas à LLM
- Rate limiting de 10 msgs/min por sessão

**Fora do escopo (pós-MVP):**
- Login / histórico persistente entre sessões
- Links de afiliados / comparativo de produtos reais
- App mobile nativo
- Múltiplos idiomas

---

## Documentação Interna

| Arquivo                     | Conteúdo                                    |
|-----------------------------|---------------------------------------------|
| `docs/PRD.md`               | Requisitos funcionais e não-funcionais      |
| `docs/USER_STORIES.md`      | 3 User Stories com critérios BDD            |
| `docs/ESTRUTURA_PROJETO.md` | Estrutura de pastas detalhada               |
| `docs/DIAGRAMA_SEQUENCIA.md`| Fluxo de uma mensagem (PlantUML)            |
| `docs/FLUXO_USUARIO.md`     | Jornada do usuário (Mermaid)                |
| `prompts.md`                | System prompt do Herbert + exemplos few-shot |
| `AGENTS.md`                 | Instruções para agentes de IA               |
| `VIABILIDADE.md`            | Análise de viabilidade técnica e de negócio |
