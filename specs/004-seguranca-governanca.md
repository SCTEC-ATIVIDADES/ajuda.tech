# Spec 004 — Segurança e governança

## Resumo das lacunas

- Não há defesa robusta contra prompt injection.
- Limite de corpo, mensagem e rate limit ainda não estão ativos.
- Defaults de `SECRET_KEY` e `DEBUG` são inseguros para produção.
- Não há cenário adversarial documentado.
- Limites de autonomia e tratamento de conteúdo não confiável não estão formalizados.

## Planejamento detalhado

1. Validar tipo, tamanho e conteúdo básico de entrada no endpoint principal e legado.
2. Implementar rate limit por sessão/IP com resposta 429 e janela documentada.
3. Separar instruções do sistema, dados do usuário, catálogo e respostas de tools.
4. Adicionar classificação/defesa contra tentativas de revelar prompts, ignorar regras ou executar ações não autorizadas.
5. Garantir que tools aceitem somente argumentos validados e não executem ações destrutivas.
6. Fazer aplicação falhar em produção quando segredo obrigatório faltar ou DEBUG estiver ativo indevidamente.
7. Configurar cookies e headers de produção conforme ambiente.
8. Criar teste adversarial com resultado esperado seguro.

## TODO

- [ ] Definir matriz de ameaças.
- [ ] Ativar limites de input e rate limit.
- [ ] Implementar isolamento de conteúdo não confiável.
- [ ] Adicionar testes de injection e vazamento de prompt.
- [ ] Corrigir defaults de configuração.
- [ ] Documentar autonomia permitida e ações proibidas.

## Dúvidas técnicas em aberto

- Rate limit será por IP, sessão ou combinação?
- Qual biblioteca já instalada atende ao rate limit sem nova dependência?
- Defesa injection será regra determinística, prompt dedicado ou ambos?
- Quais campos podem aparecer em logs sem risco de exposição?

## Critérios de aceite

- Input vazio, excessivo, não textual ou JSON inválido retorna erro controlado.
- Excesso de chamadas retorna 429 sem chamar LLM.
- Prompt injection não revela system prompt, segredos ou instruções internas.
- Tool não executa ação fora do escopo de recomendação.
- Produção rejeita chave padrão e configuração insegura.
- Cenário adversarial possui teste, log e resposta observável.
- CSRF continua ativo em formulários e POSTs.

## Arquivos afetados

- `chat/views.py`
- `chat/prompts.py`
- `chat/services.py`
- `chat/agent/nodes.py`
- `chat/agent/tools.py`
- `ajuda_tech/settings.py`
- `chat/tests/test_limits.py`
- Novos testes de segurança em `chat/tests/`

## Evidências esperadas

- Matriz de ameaças.
- Teste adversarial reproduzível.
- Resposta HTTP 429 sob excesso.
- Saída de `check --deploy` corrigida.
- Configuração por ambiente sem segredo versionado.

## Dependências

- [003](003-memoria-contexto.md)
- [005](005-observabilidade-resiliencia.md)
- [009](009-readme-evidencias.md)
