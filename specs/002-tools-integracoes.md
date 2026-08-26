# Spec 002 — Tools e integrações

## Resumo das lacunas

- `comparar_produtos` existe, mas não participa do fluxo principal.
- Não há integração externa claramente demonstrada via API, MCP, serviço ou webhook.
- Contratos de entrada/saída e erros das tools não estão formalizados.

## Planejamento detalhado

1. Escolher uma integração externa de baixo risco e leitura, preferencialmente serviço de cotação, consulta de disponibilidade ou endpoint mockado reproduzível.
2. Isolar chamada em `services.py` ou módulo próprio, mantendo views fora da API.
3. Definir schema de entrada, saída, timeout, retry limitado e erros normalizados.
4. Conectar integração a nó do grafo.
5. Usar `comparar_produtos` em recomendação ou consulta explícita.
6. Validar catálogo e resposta externa antes de usar dados no prompt.
7. Testar sucesso, timeout, resposta inválida, 4xx, 5xx e ausência de resultados.

## TODO

- [ ] Escolher serviço e registrar justificativa.
- [ ] Criar contrato tipado da tool.
- [ ] Adicionar validação de argumentos.
- [ ] Integrar tool ao grafo.
- [ ] Implementar fallback sem serviço externo.
- [ ] Testar erros e dados malformados.

## Dúvidas técnicas em aberto

- Serviço real exige credencial ou pode ser API pública/mock controlado?
- Integração deve alterar recomendação ou apenas enriquecer relatório?
- Qual limite de custo e chamadas por execução?

## Critérios de aceite

- Tool recebe somente dados validados.
- Tool retorna estrutura previsível ou erro estruturado.
- Agente continua operando quando serviço falha.
- `comparar_produtos` é alcançável por fluxo demonstrável.
- Testes não dependem de rede.
- README documenta integração, limites e fallback.

## Arquivos afetados

- `chat/agent/tools.py`
- `chat/agent/nodes.py`
- `chat/agent/graph.py`
- `chat/services.py`
- `chat/tests/test_agent_tools.py`
- `chat/tests/test_services.py`
- `requirements.txt` somente se necessário

## Evidências esperadas

- Payload e resposta sanitizados.
- Teste automatizado da tool.
- Log de sucesso e falha.
- Execução da recomendação usando integração.

## Dependências

- [001](001-langgraph-completo.md)
- [004](004-seguranca-governanca.md)
- [005](005-observabilidade-resiliencia.md)
