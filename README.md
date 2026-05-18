# 💻 Ajuda Tech — Assistente Inteligente para Compra de Computadores

Ajuda Tech é uma aplicação web com IA integrada que auxilia usuários leigos a encontrarem o computador ideal (PC ou Notebook) de acordo com sua necessidade e orçamento — sem precisar entender de tecnologia.

---

## 🎯 Objetivo

Muitas pessoas têm dificuldade em escolher um computador porque não entendem as especificações técnicas. O Ajuda Tech resolve isso com uma conversa simples: o usuário descreve o que quer fazer com o computador e a IA recomenda a melhor opção.

---

## 🚀 Funcionalidades

- Chat interativo com IA para coleta de necessidades do usuário
- Recomendação personalizada de PC ou Notebook com base no perfil do usuário
- Explicações em linguagem simples, sem jargões técnicos
- Histórico de conversas por sessão
- Interface web responsiva e acessível

---

## 🛠️ Tecnologias (MVP)

| Camada         | Tecnologia                   |
| -------------- | ---------------------------- |
| Backend        | Python 3.12+                 |
| Framework      | Django 5.x                   |
| Banco de dados | SQLite                       |
| IA             | API de LLM (OpenAI / Gemini) |
| Frontend       | Django Templates + HTML/CSS  |

---

## 📦 Instalação e Configuração

### Pré-requisitos

- Python 3.12 ou superior
- pip
- Chave de API do provedor de LLM (OpenAI ou Gemini)

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/Ajuda Tech.git
cd Ajuda Tech

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env e adicione sua chave de API

# 5. Aplique as migrações
python manage.py migrate

# 6. Inicie o servidor de desenvolvimento
python manage.py runserver
```

Acesse em: `http://localhost:8000`

---

## ⚙️ Variáveis de Ambiente

```env
SECRET_KEY=sua_chave_secreta_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
LLM_API_KEY=sua_chave_de_api_da_ia
LLM_PROVIDER=openai  # ou gemini
```

---

## 📁 Estrutura do Projeto

```
Ajuda Tech/
├── core/                   # App principal do Django
│   ├── models.py           # Modelos: Sessão, Mensagem, Recomendação
│   ├── views.py            # Views do chat e resultado
│   ├── urls.py
│   └── services/
│       └── ai_service.py   # Integração com a API de LLM
├── templates/              # Templates HTML
├── static/                 # CSS, JS, imagens
├── Ajuda Tech/               # Configurações do projeto Django
│   ├── settings.py
│   └── urls.py
├── docs/                   # Documentação do projeto
├── manage.py
├── requirements.txt
├── .env.example
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
