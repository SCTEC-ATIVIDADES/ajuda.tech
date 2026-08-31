# Validação humana — Spec 007

DATA: 2026-08-29
ESCOPO: Aceite dos artefatos de análise de logs e do gate CI, sem publicação do site.

CRITÉRIOS:
- Dados sintéticos e anonimizados, sem segredo ou dado pessoal.
- Anomalias acima de 500 ms identificadas.
- Tendência primeira→última calculada com incerteza explícita.
- Risco classificado e justificado.
- Gate determinístico reproduzível no CI.
- Execução IA externa registrada separadamente da análise determinística.
- Resposta IA separada da decisão determinística.

DECISÃO: ACEITO PARA ENTREGA DA SPEC 007; análise IA externa validada em `ai-validation.md`, enquanto `observability-analysis.json` permanece evidência determinística offline.

VALIDAÇÃO:
- O gate determinístico identificou duas anomalias em `catalog`: 700 ms e 900 ms.
- Tendência calculada: +28,57%; incerteza alta com duas observações.
- Risco determinístico: médio, conforme regra reproduzível para anomalia sem falha.
- `ai-response.json` permanece artefato histórico separado; execução IA comprovada está documentada em `ai-validation.md`.
- A análise determinística offline não foi substituída pela análise IA; ambas permanecem identificadas.
- CI verde, falha controlada e recovery foram comprovados por runs registrados no STATUS.

FORA DO ESCOPO: publicação do site não será realizada. Rotação de `LLM_API_KEY` permanece pendência operacional separada e não foi alterada.
