# Spec 002 — Tools e integrações

## Objetivo

Tornar tools alcançáveis, validadas e demonstráveis, incluindo uma integração HTTP de leitura em serviço Docker separado com fallback local.

## Contexto mínimo atual

`chat/agent/tools.py` possui `buscar_produtos`, `comparar_produtos` e `gerar_relatorio`; catálogo está em `produtos.json`; contato OpenRouter fica em `chat/services.py`. Views não devem chamar integração diretamente.

## Escopo autorizado

Alterar `chat/agent/tools.py`, `chat/agent/nodes.py`, `chat/agent/graph.py`, `chat/services.py`, testes correspondentes e `README.md`. Dependência nova somente se inevitável e aprovada no relatório.

## Execução

1. Escolher integração de baixo risco e leitura; usar endpoint Docker local reproduzível, sem credencial externa.
2. Registrar decisão: finalidade, origem, limites e fallback.
3. Criar contrato tipado, validação de entrada e erro normalizado.
4. Integrar tool a nó alcançável do grafo e tornar `comparar_produtos` demonstrável.
5. Validar schema do catálogo e resposta do serviço HTTP local antes do prompt.
6. Aplicar timeout/retry limitado somente onde já houver padrão.
7. Nunca usar rede nos testes.

## Testes obrigatórios

Sucesso, argumento inválido, catálogo vazio/malformado, timeout, 4xx, 5xx, resposta do serviço HTTP local inválida e fallback.

## Aceite

Tool recebe dados validados, retorna contrato previsível, falha sem quebrar recomendação e não executa ação destrutiva. README explica integração, limites e fallback.

## Bloqueios

Sem serviço externo, implementar adaptador HTTP local controlado e marcar API terceira como `N/A`; não fingir integração pública.

## Evidências

Payload sanitizado, testes, logs de sucesso/falha e execução do fluxo.

## Saída

Usar contrato de `000`: STATUS, arquivos, testes, evidências, decisões e pendências.

## Próximo

`003`.
