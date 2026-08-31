# Spec 003 — Status

STATUS: DONE
SPEC: 003-memoria-contexto

## Aceite verificado

- Sessão mantém até 50 entradas e o agente envia no máximo 20 mensagens ao grafo/LLM.
- Mensagem máxima é 4.000 caracteres; corpo JSON máximo é 8.192 bytes.
- Necessidades recuperadas da sessão são incorporadas ao estado e usadas na coleta.
- `thread_id` permanece estável entre requisições; `run_id` identifica execução.
- Recarregar `/` preserva sessão; `POST /new/` limpa explicitamente contexto e histórico.
- Sessão expirada não reaproveita necessidades antigas.
- Falha de persistência retorna erro seguro e emite evento estruturado `memory/persist/error`.
- Histórico contém somente conversa e necessidades estruturadas; não armazena segredos ou dados pessoais sensíveis por projeto.

## Testes Docker

- `docker build --tag ajuda-tech-spec003 .`: PASS; lint e Vitest: 99 testes em 9 arquivos.
- `docker run ... python manage.py check`: PASS, 0 issues.
- `docker run ... python manage.py migrate --no-input`: PASS.
- `docker run ... pytest -q`: PASS, 176 testes.

## Evidências

- `chat/agent/state.py`: campos tipados para sessão, contexto recuperado e IDs.
- `chat/views.py`: limites, continuidade, nova conversa e persistência observável.
- `chat/agent/nodes.py`: consumo de `recovered_context`.
- `chat/tests/test_views.py`: corpo grande, sessão expirada e falha de persistência.
- `chat/tests/test_limits.py`: histórico e janela de contexto.
- `chat/tests/test_acceptance.py`: continuidade do agente e `thread_id` estável.
- `chat/tests/test_agent_graph.py`: execução do grafo com estado fixture.

## Decisões

- Manter `request.session` como memória mínima, sem adicionar banco ou checkpointer.
- Separar histórico conversacional, necessidades estruturadas, contexto recuperado e IDs de execução.
- Aplicar limites antes de chamar o agente ou o provedor LLM.

## Pendências

- Nenhuma pendência técnica da spec; persistência continua limitada ao ciclo de vida da sessão, conforme escopo aprovado.

## Próximo

Executar Spec 004.
