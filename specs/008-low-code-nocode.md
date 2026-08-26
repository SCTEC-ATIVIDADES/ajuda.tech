# Spec 008 — Low-code/no-code

## Resumo das lacunas

- Não há automação low-code/no-code comprovada.
- Falta trigger, integração real e saída observável.
- Não há documentação de limites, falha ou governança da automação.

## Planejamento detalhado

1. Escolher plataforma acessível para demonstração, como n8n, Make, Zapier ou GitHub Actions visualizado como workflow, conforme regra do curso.
2. Definir trigger reproduzível: webhook, issue, formulário ou evento de CI.
3. Integrar com Ajuda Tech ou serviço externo real.
4. Produzir saída observável: issue, mensagem, registro, relatório ou atualização de quadro.
5. Incluir validação de payload, autenticação, timeout e tratamento de falha.
6. Registrar execução normal e falha.

## TODO

- [ ] Escolher ferramenta e justificar.
- [ ] Criar workflow com trigger.
- [ ] Conectar endpoint/serviço real.
- [ ] Validar payload e segredo do webhook.
- [ ] Definir saída verificável.
- [ ] Testar duplicação, falha e retry.
- [ ] Capturar evidências sem expor credenciais.

## Dúvidas técnicas em aberto

- Qual plataforma está disponível e permitida no curso?
- Trigger será webhook de recomendação ou evento do GitHub?
- Saída deve alimentar Kanban, enviar alerta ou gerar relatório?
- Onde guardar credenciais e histórico de execução?

## Critérios de aceite

- Workflow inicia por trigger reproduzível.
- Integração chama sistema real e recebe resposta validada.
- Saída pode ser vista por avaliador sem acesso secreto.
- Falhas aparecem no histórico e não geram sucesso falso.
- Workflow não expõe chaves nem dados pessoais.
- README contém passo a passo e link/captura da execução.

## Arquivos afetados

- `README.md`
- `.env.example` somente para nomes de variáveis
- Endpoint/webhook escolhido no projeto
- Arquivos exportados do workflow, se plataforma permitir
- Diretório de evidências definido em [009](009-readme-evidencias.md)

## Evidências esperadas

- Diagrama ou export do workflow.
- Payload do trigger sem segredo.
- Histórico de execução normal e falha.
- Saída criada pela automação.
- Documentação de autenticação e limites.

## Dependências

- [004](004-seguranca-governanca.md)
- [005](005-observabilidade-resiliencia.md)
- [009](009-readme-evidencias.md)
