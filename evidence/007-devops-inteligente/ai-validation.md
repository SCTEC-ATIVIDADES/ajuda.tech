# Validação da análise IA — Spec 007

## Entrada

- Arquivo: `chat/tests/observability_fixture.json`
- Dados: eventos anonimizados de `request` e `catalog`.
- Limite de anomalia: 500 ms.
- Método de tendência: primeira observação versus última.

## Resposta IA registrada

A análise identificou duas anomalias em `catalog`: 700 ms e 900 ms. A tendência foi `+28,57%`, com incerteza alta por existirem somente duas observações. A IA classificou o risco como alto porque a latência aumentou e as duas medições excederam o limite.

## Validação determinística

O analisador local confirmou as duas anomalias e a tendência de `+28,57%`. Pela regra determinística do projeto, anomalia sem falha explícita resulta em risco médio; portanto, a classificação alta da IA é conservadora, não contraditória.

## Decisão humana

- Achados de latência: aceitos.
- Tendência e incerteza: aceitas.
- Risco: ajustado para `médio` no resultado operacional, pois não há falha registrada.
- A resposta IA fica preservada como opinião analítica; o gate determinístico continua sendo a fonte de bloqueio do CI.
- Nenhuma credencial, prompt interno ou dado pessoal foi processado.

## Rastreabilidade

Prompt: `ai-prompt.txt`.
Resposta: `ai-response.json`.
Dados: `chat/tests/observability_fixture.json`.
Regra executável: `analyze_observability.py`.
Saída determinística: `observability-analysis.json`.
Validação humana: `human-validation.md`.
