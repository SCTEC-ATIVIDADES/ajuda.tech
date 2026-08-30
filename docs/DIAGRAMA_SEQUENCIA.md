# Diagrama de Sequência — Fluxo Principal

Estado atual: chat sem login, sessão Django assinada, sem banco de conversas e sem checkpointer externo.

```plantuml
@startuml
title POST /agent/send/ — Ajuda Tech

actor Usuário
participant Frontend
participant "AgentSendMessageView\nchat/views.py" as View
participant "Sessão Django" as Session
participant "StateGraph\nchat/agent/graph.py" as Graph
participant "Catálogo/tools" as Catalog
participant "OpenRouter\nchat/services.py" as LLM

Usuário -> Frontend: Digita mensagem
Frontend -> View: POST /agent/send/\nJSON + X-CSRFToken
View -> View: Valida body, mensagem, injection e rate limit
View -> Session: Lê histórico e necessidades
Session --> View: Contexto limitado
View -> Graph: Invoca AgentState
Graph -> Graph: classify_msg
alt Cumprimento
  Graph --> View: resposta greet
else Dados insuficientes
  Graph --> View: pergunta respond
else Propósito + orçamento
  Graph -> Catalog: Send notebook
  Graph -> Catalog: Send desktop
  Catalog --> Graph: resultados ou falhas parciais
  Graph -> Graph: consolidate → compare → recommend → report → respond
  Graph --> View: resposta final
end
View -> Session: Salva histórico, necessidades, thread_id e run_id
View --> Frontend: JSON {reply}
Frontend -> Frontend: Markdown + DOMPurify

@enduml
```

## Limites e falhas

- Corpo: 8.192 bytes; mensagem: 4.000 caracteres.
- Histórico: 50 entradas; janela enviada ao LLM: 20 mensagens.
- Rate limit: 10 requisições por sessão em 60 segundos; bloqueio ocorre antes do grafo/LLM.
- Timeout, conexão e HTTP 5xx do LLM/catálogo têm retry limitado. Falha de catálogo não derruba outro ramo.
- `/new/` limpa sessão via `POST`. GET `/` não limpa histórico.
- Webhook `/automation/webhook/` é fluxo separado: HMAC, validação e idempotência.

## Visualização

Use extensão PlantUML no editor. Java/Graphviz podem ser necessários para renderização local.

## Componentes

| Componente | Papel |
|---|---|
| `chat/views.py` | HTTP, segurança, sessão |
| `chat/agent/graph.py` | StateGraph, roteamento e fan-out/fan-in |
| `chat/agent/nodes.py` | classificação, catálogo, recomendação e resposta |
| `chat/agent/tools.py` | catálogo e relatório |
| `chat/services.py` | OpenRouter, retry, timeout e sanitização |
| `chat/prompts.py` | prompts internos |
| Frontend | contrato JSON e renderização sanitizada |
