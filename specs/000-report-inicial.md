# Protocolo de execução — fase final

## Como usar este diretório

Cada arquivo `001`–`010` é uma tarefa independente para um agente sem contexto. Agente deve ler somente a spec recebida e os arquivos listados em `Arquivos permitidos`. Não assumir decisões de conversas anteriores.

## Ordem de execução

Executar em sequência: `001 → 002 → 003 → 004 → 005 → 006 → 007 → 008 → 009 → 010`.

Agente seguinte pode iniciar somente quando agente anterior entregar relatório de saída e testes passarem. Se houver dependência externa, marcar `BLOCKED`, registrar decisão necessária e não inventar credenciais, URLs, evidências ou resultados.

## Contrato obrigatório de cada agente

1. Ler esta spec e arquivos permitidos.
2. Inspecionar código existente antes de editar.
3. Implementar menor alteração que atende aceite.
4. Não adicionar dependências sem justificar na saída.
5. Modificar somente arquivos listados, salvo teste novo explicitamente permitido.
6. Rodar testes diretamente relacionados, lint e typecheck/validação disponível.
7. Não chamar API externa em testes.
8. Não expor segredos, prompts internos ou dados pessoais.
9. Registrar evidências reproduzíveis.
10. Encerrar com relatório no formato abaixo.

## Formato de saída do agente

```text
STATUS: DONE | BLOCKED | PARTIAL
SPEC: <arquivo>
ALTERAÇÕES: <lista de arquivos e mudança>
TESTES: <comandos e resultado>
EVIDÊNCIAS: <paths, URLs já fornecidas ou comandos>
DECISÕES: <defaults adotados>
PENDÊNCIAS: <itens concretos>
PRÓXIMO AGENTE: <spec ou ação humana>
```

## Regras de decisão

- Preferir biblioteca, helper e padrão já existentes.
- Dúvida de implementação: escolher opção mínima compatível com critérios e registrar.
- Credencial, acesso externo, vídeo, Kanban, submissão e aprovação humana: `BLOCKED`, nunca simular.
- Critério impossível por conflito com código: preservar segurança, registrar conflito e propor menor correção.

## Mapa

- [001 LangGraph](001-langgraph-completo.md)
- [002 Tools](002-tools-integracoes.md)
- [003 Memória](003-memoria-contexto.md)
- [004 Segurança](004-seguranca-governanca.md)
- [005 Observabilidade](005-observabilidade-resiliencia.md)
- [006 QA com IA](006-qa-com-ia.md)
- [007 DevOps](007-devops-inteligente.md)
- [008 Low-code](008-low-code-nocode.md)
- [009 README e evidências](009-readme-evidencias.md)
- [010 Entrega](010-entrega-final.md)

## Critério global

Cada requisito deve ter implementação, teste ou evidência externa verificável. Não declarar concluído com base somente em documentação.

## Rubrica final

A entrega precisa cobrir vídeo, Kanban, versionamento, README, aplicação, LangGraph, tool, memória, segurança, observabilidade/resiliência, QA com IA, DevOps/anomalias, low-code, prompts/modelos/refinamento e análise crítica/evidências. Total: 10 pontos. Credenciais expostas, artefatos inacessíveis ou código não explicável podem zerar a entrega.

## Checklist humano

- [ ] Revisar relatórios dos agentes.
- [ ] Resolver bloqueios externos.
- [ ] Confirmar branches, PRs, Kanban e permissões.
- [ ] Gravar vídeo não listado de até 12 minutos.
- [ ] Validar links em janela anônima.
- [ ] Submeter antes de 31/08/2026 às 15h.
- [ ] Não alterar repositório após submissão.
