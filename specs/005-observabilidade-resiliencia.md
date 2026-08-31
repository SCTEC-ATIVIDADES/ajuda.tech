# Spec 005 — Observabilidade e resiliência

## Objetivo

Permitir reconstruir uma execução e demonstrar latência, falha, retry, timeout e fallback com dois sinais correlacionados.

## Contexto mínimo atual

Logging existe em `ajuda_tech/settings.py`; LLM, tools e nós ficam em `chat/services.py`, `chat/agent/` e `chat/views.py`. Não logar prompts completos.

## Escopo autorizado

Alterar settings, views, services, graph, nodes, tools, testes e utilitários/fixtures de observabilidade. Atualizar README apenas para operação.

## Execução

1. Definir schema JSON: `timestamp`, `trace_id`, `run_id`, `stage`, `event`, `status`, `duration_ms`, `error_type`.
2. Gerar IDs por request/execução e propagar aos nós/tools.
3. Instrumentar ordem, duração, retry, timeout, fallback e status.
4. Escolher segundo sinal mínimo já disponível: contador/métrica agregada ou arquivo estruturado; usar mesmos IDs.
5. Fixar timeout total e por dependência; retry só para erros recuperáveis.
6. Criar fixture de execução normal e falha e script determinístico de correlação/análise.
7. Sanitizar conteúdo e testar ausência de segredo.

## Testes obrigatórios

IDs presentes, ordem/duração, correlação dos dois sinais, timeout sem request pendente, retry limitado, erro não recuperável sem retry e fallback.

## Aceite

Investigação identifica execução, etapa lenta/falha e causa provável. Logs são estruturados e úteis sem conteúdo sensível.

## Evidências

JSON real sanitizado, tabela de latência, análise normal/falha e comandos reproduzíveis.

## Saída

Usar contrato de `000`: STATUS, arquivos, testes, evidências, decisões e pendências.

## Próximo

`006`.
