# Spec 005 — Observabilidade e resiliência

## Resumo das lacunas

- Logs não possuem correlação completa por execução.
- Não há dois sinais correlacionados demonstrados, incluindo logs estruturados.
- Falta latência por nó, contagem de tokens/custo e métricas de erro.
- Timeout/retry existem, mas fallback e investigação de execução não estão evidenciados.

## Planejamento detalhado

1. Criar `trace_id` por requisição e `run_id` por execução do grafo.
2. Emitir logs JSON com evento, etapa, status, duração, erro sanitizado e IDs correlacionados.
3. Adicionar segundo sinal: métricas ou eventos estruturados agregáveis.
4. Instrumentar chamada LLM, tools e nós LangGraph.
5. Definir timeout total, timeout por dependência, retry limitado e fallback local.
6. Evitar logging de prompt completo, chave, conteúdo sensível e resposta bruta sem necessidade.
7. Criar cenário de investigação: localizar execução, identificar etapa lenta/falha e concluir causa provável.

## TODO

- [ ] Definir schema de log.
- [ ] Gerar IDs de correlação.
- [ ] Medir duração e status por nó.
- [ ] Registrar retry e fallback.
- [ ] Expor ou exportar métrica agregada.
- [ ] Criar script/fixture de análise de logs.
- [ ] Documentar investigação de uma execução normal e uma falha.

## Dúvidas técnicas em aberto

- Segundo sinal será métrica Prometheus, contador em log ou dashboard externo?
- Logs ficarão em arquivo, stdout ou serviço externo?
- Fallback deve usar catálogo determinístico sem LLM?
- Qual p95 será usado como referência de desempenho?

## Critérios de aceite

- Toda execução possui `trace_id` e `run_id`.
- Logs estruturados permitem reconstruir ordem e duração das etapas.
- Dois sinais usam IDs comuns e podem ser correlacionados.
- Timeout não deixa request pendurada indefinidamente.
- Retry não ocorre em erros não recuperáveis.
- Falha LLM produz fallback amigável e evento observável.
- Existe investigação reproduzível de execução normal e falha.

## Arquivos afetados

- `ajuda_tech/settings.py`
- `chat/views.py`
- `chat/services.py`
- `chat/agent/graph.py`
- `chat/agent/nodes.py`
- `chat/agent/tools.py`
- `chat/tests/test_services.py`
- Novos utilitários/testes de observabilidade

## Evidências esperadas

- Logs JSON reais.
- Consulta ou script que correlaciona sinais.
- Tabela de latência por etapa.
- Execução com timeout/retry/fallback.
- Relatório de investigação com hipótese e conclusão.

## Dependências

- [001](001-langgraph-completo.md)
- [002](002-tools-integracoes.md)
- [004](004-seguranca-governanca.md)
- [007](007-devops-inteligente.md)
