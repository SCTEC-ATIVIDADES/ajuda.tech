# Evidência de análise de observabilidade — Spec 007

- Fixture: `chat/tests/observability_fixture.json`
- Limite: 500 ms
- `request`: 10 ms, normal
- `catalog`: 700 ms e 900 ms, duas anomalias
- Tendência catalog: `+28,57%`
- Incerteza: alta, somente duas observações
- Risco determinístico: médio, sem falha explícita
- Risco IA: alto, classificação conservadora validada e ajustada humanamente para médio
- Análise externa: registrada em `ai-prompt.txt` e `ai-response.json`
- Análise reproduzível: `analyze_observability.py`
