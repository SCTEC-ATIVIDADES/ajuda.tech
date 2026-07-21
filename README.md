# Ajuda Tech — Assistente Inteligente para Compra de Computadores

# Módulo 2 — Evolução do Projeto com LangGraph

> Documento de análise e planejamento para discussão em grupo.
> Criado em: 2026-07-16

Trabalho módulo 2 com LangGraph

Grupo Dupla
Gisele Tavares
Wagner Sousa

Slides:
https://gamma.app/docs/Ajuda-Tech-Problema-e-Solucao-r9t5jfg1cwkiv0e

Repositório:
https://github.com/SCTECH-ATIVIDADES/ajuda.tech

## Integrantes

- Wagner Sousa
- Rafael Santos
- Rafael
- Gisele Tavares
- Luan Rodrigues

## Links

- [Apresentação (Gamma)](https://gamma.app/docs/Untitled-gqu51wdlkr5cbnw?mode=doc)
- [Repositório](https://github.com/SCTECH-ATIVIDADES/ajuda.tech)
- [Vídeo explicativo](https://www.youtube.com/watch?v=z0OYyr210F8)

---

## 1. Problema

Muitas pessoas têm dificuldade em escolher um computador porque não entendem as especificações técnicas. Elas precisam de ajuda para traduzir suas necessidades reais (estudar, trabalhar, jogar) em uma compra adequada ao seu orçamento.

## 2. Objetivo do Agente

O **Herbert** é um agente conversacional que conduz o usuário em uma coleta guiada de informações e recomenda o computador ideal (notebook ou desktop) com base em um catálogo de produtos reais.

- **Entrada:** mensagem do usuário descrevendo o que precisa
- **Saída:** recomendação personalizada de produto do catálogo + relatório em Markdown

## 3. Fluxo com LangGraph

O agente é implementado com **LangGraph** (StateGraph), organizado em 6 nós com roteamento condicional:

```
START → classify_msg → [greet | gather_needs | recommend]
                           ↓              ↓
                         END     [recommend | respond]
                                       ↓
                                  report → respond → END
```

### Nós do grafo

| Nó | Função |
|----|--------|
| `classify_msg` | Classifica a intenção do usuário (saudação, dados, pergunta, recomendação) |
| `greet` | Responde cumprimentos e inicia a conversa |
| `gather_needs` | Extrai necessidades do usuário (propósito, orçamento, mobilidade) |
| `recommend` | Busca produtos no catálogo e gera recomendação personalizada |
| `report` | Gera relatório estruturado em Markdown com a recomendação |
| `respond` | Monta a resposta final ou faz perguntas para coletar dados faltantes |

### Estado compartilhado

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # Histórico da conversa
    user_needs: dict                         # propósito, orçamento, mobilidade, prioridades
    products_found: list                     # Produtos encontrados pela tool
    stage: str                               # Etapa atual do fluxo
    recommendation: str                      # Texto da recomendação
    report: str                              # Relatório em Markdown
    classified_intent: str                   # Intenção classificada
```

## 4. Ferramentas Integradas

O agente utiliza **3 ferramentas** (tools) registradas via LangChain `@tool`:

| Tool | Descrição |
|------|-----------|
| `buscar_produtos` | Lê o catálogo `produtos.json` e filtra por categoria (notebook/desktop) e orçamento máximo |
| `comparar_produtos` | Compara especificações de dois produtos pelo ID |
| `gerar_relatorio` | Gera relatório em Markdown com nome, preço, specs e justificativa |

A principal ferramenta usada no fluxo é `buscar_produtos`, chamada pelo nó `recommend`.

## 5. Memória e Contexto

- O histórico de conversa é mantido na **sessão Django** (`request.session`)
- A cada mensagem, o histórico (últimas 20 mensagens) é injetado no estado `AgentState.messages`
- As necessidades extraídas (`user_needs`) persistem entre mensagens via sessão
- O LangGraph usa `Annotated[list, add_messages]` para acumular mensagens automaticamente

## 6. Segurança

- Chaves de API ficam apenas em `.env` (excluído do Git via `.gitignore`)
- `.env.example` contém apenas nomes das variáveis, sem valores reais
- Nenhuma credencial versionada no repositório
- Proteção CSRF em todos os formulários Django
- Não são coletados dados pessoais sensíveis

## 7. Como Executar

### Pré-requisitos
- Python 3.12+
- Chave de API do [OpenRouter](https://openrouter.ai)

### Instalação

```bash
git clone https://github.com/SCTECH-ATIVIDADES/ajuda.tech.git
cd ajuda.tech
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env   # edite com sua LLM_API_KEY
python manage.py migrate
python manage.py runserver
```

Acesse: `http://localhost:8000`

### Com Docker

```bash
docker compose up --build
```

Acesse: `http://localhost:8001`

### Testes

```bash
pytest              # backend
npm test            # frontend
```

## 8. Exemplo de Entrada e Saída

Veja [docs/exemplos_execucao.md](docs/exemplos_execucao.md) para exemplos detalhados de conversas com o agente.

**Resumo rápido:**

```
Usuário: oi
Herbert: Olá! Me chamo Herbert e vou te ajudar a encontrar o computador
perfeito para você. Me conta: para que você pretende usar o computador?

Usuário: quero um notebook pra estudar
Herbert: Ótimo! E qual é o seu orçamento aproximado?

Usuário: até 3000 reais
Herbert: Com R$ 3.000 você consegue um notebook ótimo para estudos!
O Samsung Book i3 é uma ótima opção — processador Intel Core i3,
8 GB de memória e tela de 15.6". Perfeito para navegar, usar o
Office e assistir aulas. Ele custa R$ 2.799,00 e vai atender
muito bem o que você precisa.
```

## 9. Decisões Tomadas

- **LangGraph sobre abordagem procedural:** escolhemos o framework porque permite visualizar o fluxo do agente como um grafo, facilitando manutenção e testes
- **OpenRouter como provedor:** permite testar diferentes modelos LLM sem trocar o código
- **Catálogo JSON local:** produto simples, sem necessidade de banco de dados para o catálogo
- **Sessão Django para memória:** evita persistência desnecessária, mantendo dados apenas durante a sessão do usuário
- **Roteamento condicional:** classifica a intenção do usuário antes de decidir o próximo nó, reduzindo chamadas LLM desnecessárias

## 10. Limitações

- **Limite de requests:** a conta free tier do OpenRouter permite ~50 requests/dia
- **Qualidade do modelo:** modelos gratuitos podem expor raciocínio interno (chain-of-thought), que é filtrado pelo código
- **Simplicidade do catálogo:** apenas 12 produtos; em produção seria necessário um banco de dados
- **Sem persistência entre sessões:** ao fechar o navegador, o histórico é perdido
- **Safety filters:** alguns modelos retornam respostas bloqueadas por filtros de segurança; o código trata esses casos

## Estrutura do Projeto

```shell
ajuda.tech/
├── ajuda_tech/          # Configurações Django
├── chat/
│   ├── agent/
│   │   ├── graph.py     # Grafo LangGraph (StateGraph + nós + edges)
│   │   ├── nodes.py     # Funções de cada nó do grafo
│   │   ├── state.py     # AgentState (TypedDict)
│   │   └── tools.py     # Ferramentas: buscar_produtos, comparar_produtos, gerar_relatorio
│   ├── static/chat/     # Frontend (JS modular + CSS)
│   ├── templates/chat/  # Template Django
│   ├── tests/           # Testes backend (pytest)
│   ├── prompts.py       # System Prompts do agente
│   ├── services.py      # Cliente OpenRouter
│   ├── views.py         # Endpoints Django
│   └── urls.py          # Rotas
├── core/                # Landing page
├── docs/                # Documentação do projeto
├── produtos.json        # Catálogo de produtos (12 itens)
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```
