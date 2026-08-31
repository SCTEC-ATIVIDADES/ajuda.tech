# Spec 008 — Low-code/no-code

## Objetivo

Entregar automação demonstrável com trigger, integração real, saída observável e falha rastreável.

## Contexto mínimo atual

A automação não existe no repositório. Pode envolver n8n, Make, Zapier ou serviço permitido pelo curso. Arquivos locais não substituem execução externa real.

## Escopo autorizado

Workflow exportável/capturas, endpoint ou webhook mínimo autorizado, `.env.example` apenas com nomes e evidências em `009`.

## Execução

1. Escolher plataforma disponível e permitida; registrar decisão e custo.
2. Definir trigger reproduzível: webhook, evento de CI, issue ou formulário.
3. Integrar endpoint/serviço real do projeto.
4. Validar assinatura/segredo, payload, idempotência, timeout e falha.
5. Produzir saída visível: issue, relatório, registro ou atualização de quadro.
6. Executar cenário normal, duplicado e falha; salvar histórico sem segredos.
7. Exportar workflow ou capturar configuração suficiente para reexecução.

## Testes obrigatórios

Executar trigger normal, payload inválido, assinatura inválida, duplicação e falha de integração. Confirmar que falha não produz sucesso falso.

## Aceite

Trigger inicia workflow; resposta é validada; saída é observável; falha não vira sucesso; credencial e dados pessoais não aparecem; README permite reprodução.

## Bloqueios

Sem plataforma, conta ou permissão, parar como `BLOCKED` e listar ação humana exata. Não criar falsa evidência com mock.

## Evidências

Export/diagrama, payload sanitizado, histórico normal/falha e saída criada.

## Saída

Usar contrato de `000`: STATUS, arquivos, testes, evidências, decisões e pendências.

## Próximo

`009`.
