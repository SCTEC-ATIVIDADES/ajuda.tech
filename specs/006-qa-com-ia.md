# Spec 006 — QA com IA

## Objetivo

Produzir prova de code review com IA e testes gerados/refinados para riscos reais, incluindo integração ou aceitação.

## Contexto mínimo atual

Alterações anteriores devem existir no histórico local. Testes backend ficam em `chat/tests/`, frontend em `chat/static/chat/js/`; CI em `.github/workflows/ci.yml`.

## Escopo autorizado

Código de teste e alteração real escolhida, CI se necessário, `README.md` e diretório de evidências definido em `009`. Não fabricar review retroativo.

## Execução

1. Selecionar commit/PR real de 001–005.
2. Executar IA sobre diff; salvar prompt, resposta, data, modelo e decisão humana sem segredos.
3. Registrar achados aceitos, rejeitados e correções.
4. Pedir testes derivados dos critérios de aceite; revisar manualmente e refinar.
5. Adicionar teste de integração endpoint/grafo e aceitação/E2E mínima sem rede externa.
6. Criar matriz risco → teste → evidência e priorizar segurança, contexto, falha externa, UX e custo.
7. Rodar suíte completa e cobertura disponível.

## Testes obrigatórios

Teste novo falha quando comportamento crítico quebra; integração cobre cenário normal e falha; frontend cobre resposta/erro se fluxo tocar UI.

## Aceite

Diff real revisado, geração e refinamento rastreáveis, riscos críticos testados ou justificados, suíte sem API externa.

## Bloqueios

Se não houver ferramenta IA acessível, marcar evidência de review como `BLOCKED`; não atribuir texto humano à IA.

## Evidências

Diff, prompt/resposta, matriz, testes e resultados.

## Saída

Usar contrato de `000`: STATUS, arquivos, testes, evidências, decisões e pendências.

## Próximo

`007`.
