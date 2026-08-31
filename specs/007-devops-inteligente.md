# Spec 007 — DevOps inteligente

## Objetivo

Criar gate de CI reproduzível e análise de logs por IA com anomalia, tendência simples e risco.

## Contexto mínimo atual

Workflow está em `.github/workflows/ci.yml`; comandos devem vir de `package.json`, `requirements.txt` e configurações existentes. Docker usa arquivos raiz.

## Escopo autorizado

Alterar workflow, Dockerfile/Compose somente se necessário, package/config de lint, script/fixture de análise e README.

## Execução

1. Inspecionar comandos reais antes de ativar jobs.
2. Fazer CI executar lint, testes backend, testes frontend e build/validação equivalente; não depender de LLM/rede externa.
3. Adicionar migração/checks Django e cobertura existente.
4. Corrigir execução Docker mínima reproduzível; não prometer produção se não houver servidor adequado.
5. Usar fixture com duas etapas e dados suficientes.
6. Pedir IA para detectar anomalia, calcular tendência simples explicitando método/limite/incerteza e classificar risco.
7. Salvar prompt, dados anonimizados, resposta, validação humana e artefatos CI.

## Testes obrigatórios

CI verde, falha controlada de gate e execução local equivalente. Análise reproduzível com fixture.

## Aceite

Merge bloqueado por lint/teste/validação; backend/frontend no CI; análise informa dados e incerteza; artefatos acessíveis.

## Bloqueios

GitHub Actions privado, IA externa ou deploy real são evidências humanas/externas; marcar `BLOCKED` sem simular.

## Evidências

Runs verde/vermelho, logs, saída IA e risco/tendência.

## Saída

Usar contrato de `000`: STATUS, arquivos, testes, evidências, decisões e pendências.

## Próximo

`008`.
