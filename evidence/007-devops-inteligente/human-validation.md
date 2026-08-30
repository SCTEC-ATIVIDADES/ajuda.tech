# Validação humana — Spec 007

DATA: 2026-08-29
ESCOPO: Aceite dos artefatos de análise de logs e do gate CI, sem publicação do site.

CRITÉRIOS:
- Dados sintéticos e anonimizados, sem segredo ou dado pessoal.
- Anomalias acima de 500 ms identificadas.
- Tendência primeira→última calculada com incerteza explícita.
- Risco classificado e justificado.
- Gate determinístico reproduzível no CI.
- Artefato IA ausente ou não chamado identificado sem substituição silenciosa.
- Resposta IA separada da decisão determinística.

DECISÃO: ACEITO PARCIALMENTE PARA ENTREGA DA SPEC 007; análise IA externa permanece BLOCKED.

VALIDAÇÃO:
- O gate determinístico identificou duas anomalias em `catalog`: 700 ms e 900 ms.
- Tendência calculada: +28,57%; incerteza alta com duas observações.
- Risco determinístico: médio, conforme regra reproduzível para anomalia sem falha.
- `ai-response.json` não é tratado como execução IA comprovada; seu risco alto permanece apenas artefato histórico não validado.
- Ausência de chamada IA foi mantida visível; não foi ocultada nem simulada.
- CI verde, falha controlada e recovery foram comprovados por runs registrados no STATUS.

FORA DO ESCOPO: publicação do site não será realizada. Rotação de `LLM_API_KEY` permanece pendência operacional separada e não foi alterada.
