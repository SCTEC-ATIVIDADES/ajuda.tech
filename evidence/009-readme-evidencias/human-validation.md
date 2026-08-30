# Validação humana — README e evidências

DATA: 2026-08-30
ESCOPO: README, matriz de 15 critérios, docs de arquitetura/fluxo e evidências 006–009.

CRITÉRIOS:

- Instalação, execução local, Docker e testes possuem comandos.
- Arquitetura e endpoints refletem código atual.
- Claims não comprovados estão marcados `PARTIAL` ou `BLOCKED`.
- Evidências externas, vídeo, Kanban e permissões não são simuladas.
- Segredos não aparecem nos artefatos.
- Limitações de sessão frontend, catálogo externo e host sem Node estão explícitas.

DECISÃO: ACEITO PARCIALMENTE PARA ENTREGA DA SPEC 009.

PENDÊNCIAS ACEITAS: catálogo externo de terceiro; publicar HTTPS n8n se exigido; anexar vídeo, Kanban e permissões se exigidos pelo aceite final. Ambiente limpo validado em clone temporário: Compose, catálogo, app e n8n subiram; workflow foi importado e ativado; webhook recebeu e processou a requisição, mas resposta final foi limitada por 429 da sessão. Evidência detalhada em `verification.md`.
