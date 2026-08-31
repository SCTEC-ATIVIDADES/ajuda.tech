# Spec 004 — Segurança e governança

## Objetivo

Fechar entrada não confiável, prompt injection, limites de abuso, configuração segura e autonomia restrita.

## Contexto mínimo atual

Endpoints estão em `chat/views.py`; prompts em `chat/prompts.py`; cliente LLM em `chat/services.py`; settings em `ajuda_tech/settings.py`; testes de limites possuem casos pendentes.

## Escopo autorizado

Alterar `chat/views.py`, `chat/prompts.py`, `chat/services.py`, `chat/agent/nodes.py`, `chat/agent/tools.py`, `ajuda_tech/settings.py`, testes de segurança/limites e `README.md`.

## Execução

1. Criar matriz curta de ameaça: injection, payload grande, abuso/rate limit, segredo, tool indevida e vazamento de prompt.
2. Validar JSON, tipo, tamanho e conteúdo básico nos endpoints principal e legado.
3. Implementar rate limit sem dependência nova se possível; excesso retorna 429 antes do LLM.
4. Isolar instruções do sistema de dados do usuário, catálogo e tools.
5. Responder injection sem revelar prompt, segredo, raciocínio ou executar ação.
6. Corrigir defaults: produção falha com segredo ausente/chave padrão/DEBUG indevido; manter testes locais funcionais por configuração explícita.
7. Preservar CSRF e cookies seguros em produção.

## Testes obrigatórios

JSON inválido, vazio, tipo errado, excesso, rate limit, injection, vazamento, tool fora do escopo, CSRF e `check --deploy`.

## Aceite

Sem chamada LLM após 429; injection tem resposta segura observável; produção não inicia insegura; nenhuma tool é destrutiva; limites de autonomia documentados.

## Bloqueios

Não depender de serviço externo para detectar injection. Se política institucional exigir plataforma externa, registrar como bloqueio.

## Evidências

Matriz de ameaças, testes adversariais, 429 e saída de configuração sanitizada.

## Saída

Usar contrato de `000`: STATUS, arquivos, testes, evidências, decisões e pendências.

## Próximo

`005`.
