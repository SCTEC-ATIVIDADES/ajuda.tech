# 💻 Ajuda Tech — Assistente Inteligente para Compra de Computadores

Ajuda Tech é uma aplicação web com IA integrada que auxilia usuários leigos a encontrarem o computador ideal (PC ou Notebook) de acordo com sua necessidade e orçamento — sem precisar entender de tecnologia.

<img width="821" height="948" alt="ajudatech-ai" src="https://github.com/user-attachments/assets/d6c5d397-0ccb-4011-bda1-3ea6eec01aac" />

---

## 🎯 Objetivo

Muitas pessoas têm dificuldade em escolher um computador porque não entendem as especificações técnicas. O Ajuda Tech resolve isso com uma conversa simples: o usuário descreve o que quer fazer com o computador e o assistente **Herbert** recomenda a melhor opção — sem jargões técnicos.

---

## 🚀 Funcionalidades

- Chat interativo com IA (Herbert) para coleta de necessidades do usuário
- Recomendações em 3 categorias: **econômica**, **ideal** e **premium**
- Explicações em linguagem simples, sem jargões técnicos
- Histórico de conversa por sessão (sem necessidade de login ou cadastro)
- Botão de copiar e compartilhar mensagens do assistente
- Tema claro/escuro
- Interface web responsiva (desktop e mobile)

---

## 🛠️ Tecnologias

| Camada    | Tecnologia                                        |
|-----------|---------------------------------------------------|
| Backend   | Python 3.12+                                      |
| Framework | Django 5.x                                        |
| Banco     | SQLite com `django.contrib.sessions`              |
| IA        | OpenRouter API (`requests`) — padrão: DeepSeek    |
| Frontend  | Django Templates + HTML/CSS + módulos ES (JS)     |
| Testes JS | Vitest                                            |
| Testes PY | pytest + pytest-django                            |

---

## 📦 Instalação e Configuração

### Pré-requisitos

- Python 3.12 ou superior
- Node.js 18+ (para testes JavaScript)
- Chave de API do [OpenRouter](https://openrouter.ai/keys)

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/SCTECH-ATIVIDADES/ajuda.tech.git
cd ajuda.tech

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Instale as dependências Python
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com sua LLM_API_KEY e SECRET_KEY

# 5. Aplique as migrações
python manage.py migrate

# 6. Inicie o servidor de desenvolvimento
python manage.py runserver
```

Acesse em: `http://localhost:8000`

### Testes

```bash
# Testes Python
pytest

# Testes JavaScript
npm install
npm test
```

---

## ⚙️ Variáveis de Ambiente

```env
SECRET_KEY=sua_chave_secreta_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
LLM_API_KEY=sua_chave_openrouter
LLM_PROVIDER=openai
LLM_MODEL=deepseek/deepseek-v4-flash:free
LLM_TIMEOUT=30
SITE_URL=http://localhost:8000
SITE_NAME=Ajuda Tech
LOG_LEVEL=INFO
```

---

## 📁 Estrutura do Projeto

```
ajuda.tech/
├── ajuda_tech/              # Configurações Django (settings, urls, wsgi)
├── core/                    # App da landing page
│   ├── views.py
│   ├── urls.py
│   └── templates/core/
├── chat/                    # App principal do assistente Herbert
│   ├── views.py             # ChatView, SendMessageView, RecommendView
│   ├── services.py          # OpenRouterClient — integração com a API de LLM
│   ├── prompts.py           # System prompts isolados
│   ├── exceptions.py        # Hierarquia de exceções customizadas
│   ├── models.py            # Conversation, Message
│   ├── urls.py
│   ├── tests/               # Testes Python (pytest-django)
│   ├── templates/chat/
│   └── static/chat/
│       ├── css/chat.css
│       └── js/              # chatApi.js, chatApp.js, chatUi.js, chatState.js, chatTheme.js
├── docs/                    # PRD, User Stories, Diagramas
├── manage.py
├── requirements.txt
├── package.json
└── README.md
```

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
