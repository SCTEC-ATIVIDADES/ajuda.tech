# 💻 Ajuda Tech — Assistente Inteligente para Compra de Computadores

Segue nosso trabalho do Grupo 10 / 12
Entrega 07/06

Wagner Sousa
Rafael Santos
Rafael 
Gisele Tavares
Luan Rodrigues

Apresentação:
https://gamma.app/docs/Untitled-gqu51wdlkr5cbnw?mode=doc

Repositório:
https://github.com/SCTECH-ATIVIDADES/ajuda.tech

Video:
https://www.youtube.com/watch?v=z0OYyr210F8

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM_API-412991?style=for-the-badge)
![JavaScript](https://img.shields.io/badge/JavaScript-ESM-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Vitest](https://img.shields.io/badge/Vitest-Tests-6E9F18?style=for-the-badge&logo=vitest&logoColor=white)
![Dev_Container](https://img.shields.io/badge/Dev%20Container-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

> Ajuda Tech é uma aplicação web com IA integrada que ajuda usuários leigos a encontrarem o computador ideal de acordo com sua necessidade e orçamento, sem exigir conhecimento técnico.

<img width="1079" height="821" alt="image" src="https://github.com/user-attachments/assets/b5b4b107-5f0e-4838-ba09-a8de4c43bdda" />

---

## 🎯 Sobre o Projeto

Muitas pessoas têm dificuldade em escolher um computador porque não entendem as especificações técnicas. O Ajuda Tech resolve isso com uma conversa simples: o usuário descreve o que quer fazer com o computador e a IA recomenda a melhor opção.

URL do Board 1:
https://github.com/orgs/SCTECH-ATIVIDADES/projects/1

URL do Board 2 (fork):
https://github.com/users/wagner-sousa/projects/4/views/1

Obs: fizemos um fork para separar as fases do projeto mas a separação ficou por data mesmo. A partir do dia 22/05 começamos a trabalhar na Fase 2.

### Funcionalidades

- Chat interativo com IA para coleta de necessidades do usuário
- Recomendação personalizada de PC ou Notebook com base no perfil do usuário
- Explicações em linguagem simples, sem jargões técnicos
- Histórico de conversas por sessão
- Interface web responsiva e acessível
- Preview isolado do frontend sem depender do Django
- Suporte a tema claro/escuro e renderização segura de Markdown no chat

## 📦 Pré-requisitos

- Python 3.12 ou superior — verifique com `python --version`
- pip — recomendado usar `python -m pip --version`
- Node.js e npm para testes e preview do frontend — verifique com `node --version` e `npm --version`
- Chave de API do provedor de LLM para executar a integração com IA, obtida em [OpenRouter](https://openrouter.ai)
- Docker e VS Code Dev Containers, se quiser rodar o projeto no ambiente containerizado de desenvolvimento

---

## 🚀 Instalação

### Ambiente local

#### Clone o repositório

```bash
git clone https://github.com/SCTECH-ATIVIDADES/ajuda.tech.git
cd ajuda.tech
```

# Este projeto utiliza a IDE VSCode com extensão de Dev Containers para facilitar o setup
Dev Containers 0.459.1 in VS Code 1.123.0 

## Crie um container Docker com extensão no VSCode 
Instalar a extensão Dev Containers  e ativar no projeto antes de criar o ambiente virtual, para evitar conflitos de dependências. Façpa manualmente ou peça para sua IA assistente criar o container e abrir o projeto dentro dele. O container já tem Python 3.12 e Node.js pré-instalados, além de configurar o ambiente virtual e instalar as dependências automaticamente.

### Crie e ative o ambiente virtual no docker 

```bash
python -m venv venv
```

No Windows:

```bash
python -m venv venv
```
Depois:

```bash
venv\Scripts\activate
```

#### Instale as dependências do backend

```bash
python -m pip install -r requirements.txt
```

#### Crie o arquivo de ambiente

```bash
cp .env.example .env
```

Depois, edite o arquivo `.env` com os valores do seu ambiente e chave da sua LLM escolhida.


#### Inicie o servidor de desenvolvimento

```bash
python manage.py runserver
```

Acesse em: `http://localhost:8000`

### Dev Container com Docker

O projeto inclui configuração de desenvolvimento em container por meio de [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) e [.devcontainer/Dockerfile](.devcontainer/Dockerfile).

#### Requisitos para usar o Dev Container

- Docker em execução na máquina
- VS Code com a extensão Dev Containers

#### Como abrir o projeto no container

1. Clone o repositório.
2. Abra a pasta `ajuda.tech` no VS Code.
3. Execute o comando `Dev Containers: Reopen in Container`.
4. Aguarde o `postCreateCommand` instalar automaticamente as dependências Python e Node.
5. Inicie a aplicação com `python manage.py runserver`.

### Frontend do chat (preview local, sem Django)

```bash
npm install
npm test
npx serve chat/static/chat
```

Abra a URL exibida (ex.: `http://localhost:3000`) para ver a página de chat com API mockada.

---

## ⚙️ Variáveis de Ambiente

```env
SECRET_KEY=sua_chave_secreta_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
LLM_API_KEY=sua_chave_de_api_da_ia
LLM_PROVIDER=openai
LLM_MODEL=deepseek/deepseek-v4-flash:free
LLM_TIMEOUT=30
SITE_URL=http://localhost:8000
SITE_NAME=Ajuda Tech
LOG_LEVEL=INFO
```

O repositório não deve receber chaves reais. Use o `.env.example` como base e ajuste os valores conforme seu ambiente.

O token usado em `LLM_API_KEY` deve ser gerado na sua conta em [OpenRouter](https://openrouter.ai).

---

## 🧪 Testes
Atualize as depedências e rode os testes com:

```bash
npm install
```

### Backend

```bash
pytest
```

### Frontend

```bash
npm test
```

### Modo watch para os testes JS

```bash
npm run test:watch
```

Os testes JavaScript usam Vitest com ambiente `jsdom`, e os testes Python usam `pytest` com configuração definida em `pytest.ini`.

---

## 🌐 Endpoints Principais

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | / | Renderiza o chat e inicia uma nova sessão |
| POST | /send/ | Recebe a mensagem do usuário e retorna a resposta da IA |
| POST | /recommend/ | Retorna uma recomendação estruturada com produtos |

---

## 📁 Estrutura do Projeto

### Visão simplificada

```shell
ajuda.tech/
├── .devcontainer/
├── ajuda_tech/
├── chat/
│   ├── static/chat/
│   │   ├── css/
│   │   └── js/
│   ├── templates/chat/
│   ├── tests/
│   ├── prompts.py
│   ├── services.py
│   ├── urls.py
│   └── views.py
├── core/
├── docs/
├── logs/
├── manage.py
├── package.json
├── pytest.ini
├── requirements.txt
└── README.md
```

### Diagrama do Ecossistema

O diagrama abaixo representa a arquitetura completa do Ajuda Tech, incluindo frontend, backend, banco de dados, integração com API externa, infraestrutura e documentação:

```mermaid
graph TB
    subgraph "🌐 Frontend (Navegador)"
        CHAT_HTML["chat.html<br/>(Django Template)"]
        INDEX_HTML["index.html<br/>(Preview Standalone)"]
        CSS["chat.css<br/>(Estilos + Temas)"]
        JS_APP["chatApp.js<br/>(Orquestrador)"]
        JS_API["chatApi.js<br/>(HTTP + CSRF)"]
        JS_UI["chatUi.js<br/>(DOM)"]
        JS_STATE["chatState.js<br/>(Estado)"]
        JS_THEME["chatTheme.js<br/>(Dark/Light)"]
        LIBS["marked + DOMPurify<br/>(Markdown Seguro)"]
        TESTS_JS["Testes Vitest<br/>(7 arquivos .test.js)"]
    end

    subgraph "🐍 Backend Django"
        subgraph "Config"
            SETTINGS["settings.py<br/>(Apps, Middleware, DB, LLM)"]
            ROOT_URLS["urls.py<br/>(Raiz → chat.urls)"]
            WSGI["wsgi.py"]
        end
        subgraph "App: chat"
            VIEWS["views.py<br/>ChatView | SendMessageView | RecommendView"]
            URLS_CHAT["urls.py<br/>/ | /send/ | /recommend/"]
            SERVICES["services.py<br/>OpenRouterClient"]
            PROMPTS["prompts.py<br/>System Prompts (Herbert)"]
            MODELS["models.py<br/>Conversation + Message"]
            EXCEPTIONS["exceptions.py<br/>AuthError | RateLimitError | ServiceUnavailable"]
            ADMIN["admin.py<br/>(Desabilitado)"]
            TEMPLATES["templates/chat/chat.html"]
            TESTS_PY["tests/<br/>test_models | test_views<br/>test_services | test_prompts | test_limits"]
        end
        subgraph "App: core"
            CORE_VIEWS["views.py<br/>IndexView (TemplateView)"]
            CORE_URLS["urls.py<br/>(Não roteado)"]
            CORE_TEMPLATE["templates/core/index.html"]
        end
        DJANGO_MGMT["manage.py"]
    end

    subgraph "🗄️ Banco de Dados"
        SQLITE[("db.sqlite3<br/>SQLite")]
        SESSION_DB[("Sessões<br/>Cookies Assinados")]
    end

    subgraph "☁️ API Externa"
        OPENROUTER["OpenRouter API<br/>api.openrouter.ai/v1/chat/completions"]
        LLM_MODEL["Modelo LLM<br/>DeepSeek"]
    end

    subgraph "⚙️ Infraestrutura"
        GIT["Git + GitHub"]
        CI_CD["GitHub Actions<br/>test (pytest) | frontend-test (vitest)"]
        ENV[".env<br/>LLM_API_KEY, SECRET_KEY, DEBUG"]
        REQS["requirements.txt<br/>Django, decouple, requests"]
        PACKAGE["package.json<br/>vitest, dompurify, marked"]
        DEVCONTAINER[".devcontainer<br/>Dockerfile + devcontainer.json"]
    end

    subgraph "📚 Documentação"
        README["README.md"]
        DOCS["docs/<br/>PRD, User Stories, Diagramas"]
        PROMPTS_DOC["prompts/<br/>Histórico de Prompts"]
        PROMPTS_MINI["prompts-mini-projeto/<br/>Sessões Anteriores"]
    end

    CHAT_HTML -->|"Renderiza"| JS_APP
    JS_APP -->|"Importa"| JS_API
    JS_APP -->|"Importa"| JS_UI
    JS_APP -->|"Importa"| JS_STATE
    JS_APP -->|"Importa"| JS_THEME
    JS_APP -->|"Usa"| LIBS
    CHAT_HTML -->|"Carrega"| CSS

    JS_API -->|"POST /send/ (JSON + CSRF)"| VIEWS

    ROOT_URLS -->|"include"| URLS_CHAT
    VIEWS -->|"Chama"| SERVICES
    SERVICES -->|"Lê"| PROMPTS
    SERVICES -->|"Lança"| EXCEPTIONS
    VIEWS -->|"Renderiza"| TEMPLATES
    SETTINGS -->|"Configura"| VIEWS
    SETTINGS -->|"Configura"| SERVICES

    CORE_VIEWS -.->|"⚠️ Não roteado"| CORE_URLS
    CORE_VIEWS -->|"Renderiza"| CORE_TEMPLATE

    VIEWS -->|"Sessões"| SESSION_DB
    DJANGO_MGMT -->|"manage.py migrate"| SQLITE

    SERVICES -->|"HTTP POST<br/>Bearer Token"| OPENROUTER
    OPENROUTER -->|"Roteia"| LLM_MODEL

    GIT -->|"Push"| CI_CD
    CI_CD -->|"Roda"| TESTS_PY
    CI_CD -->|"Roda"| TESTS_JS
    ENV -->|"Alimenta"| SETTINGS
    REQS -->|"Instala"| DJANGO_MGMT

    DOCS -.->|"Referencia"| README
    PROMPTS_DOC -.->|"Alimenta"| PROMPTS
```

---

## 🧭 Desenvolvimento

- O backend expõe as rotas principais em `chat/urls.py`.
- O frontend do chat fica em `chat/static/chat/` com JavaScript modular.
- O projeto usa sessões em cookies assinados para manter o estado da conversa.
- Os logs são gravados em `logs/app.log` e `logs/errors.log` com rotação de arquivos.

---

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas alterações (`git commit -m 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
