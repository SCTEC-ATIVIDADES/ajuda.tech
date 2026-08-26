# Spec 003 — Memória e contexto

## Resumo das lacunas

- Memória atual depende de cookie assinado e sessão curta.
- Não há checkpointer/thread ID ou persistência server-side.
- Janela documentada e janela enviada ao LLM divergem.
- Não há recuperação de contexto demonstrada entre execuções controladas.

## Planejamento detalhado

1. Separar histórico de conversa, necessidades estruturadas e contexto recuperado.
2. Definir limites: mensagens armazenadas, mensagens enviadas ao LLM e tamanho de cada mensagem.
3. Remover limpeza inesperada de sessão em GET, preservando nova conversa em ação explícita.
4. Escolher persistência mínima: banco Django ou checkpointer compatível com LangGraph.
5. Associar execução a thread/session ID sem coletar dado pessoal sensível.
6. Sanitizar e resumir histórico antes do prompt quando necessário.
7. Testar continuidade, truncamento, nova conversa, sessão expirada e concorrência básica.

## TODO

- [ ] Definir contrato de memória.
- [ ] Implementar janela LLM máxima de 20 mensagens, ou atualizar requisito com justificativa.
- [ ] Implementar limite de histórico de 50 entradas.
- [ ] Corrigir comportamento de `GET /`.
- [ ] Avaliar persistência server-side/checkpointer.
- [ ] Documentar retenção e privacidade.

## Dúvidas técnicas em aberto

- Memória entre sessões é obrigatória ou somente contexto durante sessão?
- Banco SQLite basta para demo ou será usado PostgreSQL?
- Resumo automático exige chamada LLM adicional?
- Qual dado deve ser apagado em “nova conversa”?

## Critérios de aceite

- Conversa continua entre requisições sem perder necessidades conhecidas.
- LLM recebe no máximo janela definida.
- Histórico não ultrapassa limite definido.
- Nova conversa limpa memória somente após ação explícita.
- Sessão não contém segredos ou dados pessoais sensíveis.
- Falha de persistência produz resposta segura, não perda silenciosa sem log.

## Arquivos afetados

- `chat/views.py`
- `chat/agent/state.py`
- `chat/agent/graph.py`
- `ajuda_tech/settings.py`
- `chat/tests/test_views.py`
- `chat/tests/test_limits.py`
- `README.md`

## Evidências esperadas

- Teste de continuidade e truncamento.
- Inspeção de estado antes/depois de duas mensagens.
- Documentação de retenção.
- Execução com sessão reiniciada e fallback.

## Dependências

- [001](001-langgraph-completo.md)
- [004](004-seguranca-governanca.md)
