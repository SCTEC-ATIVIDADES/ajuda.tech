# Validação da análise IA — Spec 007

## Execução real

- Data: `2026-08-30T04:44:01Z`
- Modelo: `nvidia/nemotron-3-ultra-550b-a55b:free`
- Provedor: OpenRouter
- Entrada: `ai-data.json`, contendo apenas eventos anonimizados.
- Prompt: `ai-prompt.txt`.
- Script: `run_ai_observability.py`, executado dentro da imagem Docker.

## Resultado

A IA identificou anomalias no estágio `catalog` em 700 ms e 900 ms, calculou tendência de 28,57%, classificou incerteza como alta por haver somente duas observações e classificou risco como alto devido à violação consistente do limite de 500 ms.

## Validação humana

A análise determinística local confirmou as duas anomalias e a tendência de 28,57%. A classificação alta é conservadora; o resultado operacional do projeto permanece médio porque não há falha explícita, apenas latência acima do limite. O achado e a tendência foram aceitos; a diferença de risco foi registrada como decisão de governança.

Nenhum segredo, prompt interno, dado pessoal ou payload externo foi salvo nos artefatos.
