# Spec 004 — Status

STATUS: DONE

## Aceite verificado

- JSON inválido, corpo não-objeto, mensagem vazia, mensagem excessiva e corpo excessivo são rejeitados.
- Rate limit de sessão ocorre antes de qualquer chamada ao LLM ou ao grafo, inclusive em `/recommend/`.
- Prompt injection recebe resposta segura e gera evento estruturado `security/prompt_injection/blocked`.
- Dados do usuário são delimitados antes de entrar em prompts; prompts, segredos e raciocínio privado não são expostos.
- `TOOLS` contém somente `buscar_produtos`, `comparar_produtos` e `gerar_relatorio`.
- Tools são somente leitura: não compram, pagam, apagam, alteram catálogo nem executam efeitos externos.
- CSRF permanece obrigatório nos endpoints JSON; cookies de sessão e CSRF ficam seguros quando `DEBUG=False`.
- Configuração insegura de produção falha com `ImproperlyConfigured`; configuração de produção válida passa `check --deploy` sem issues.
- Matriz de ameaças está em `risk-matrix.md`.

## Arquivos

- `ajuda_tech/settings.py`
- `chat/views.py`
- `chat/tests/test_security.py`
- `evidence/004-seguranca-governanca/risk-matrix.md`
- `evidence/004-seguranca-governanca/STATUS.md`

## Testes Docker

- `docker build --tag ajuda-tech-spec004 .` — PASS; lint frontend e 99 testes Vitest.
- `pytest -q` na imagem — PASS; 186 testes.
- `python manage.py migrate --no-input` — PASS.
- `DEBUG=False` com segredo e chave válidos + `python manage.py check --deploy` — PASS; 0 issues.
- `DEBUG=False` sem configuração segura — FAIL controlado com `ImproperlyConfigured`.

## Evidências

- Testes adversariais em `chat/tests/test_security.py`.
- Testes de limites, endpoints, sessão e CSRF em `chat/tests/test_limits.py` e `chat/tests/test_views.py`.
- Matriz de ameaças em `risk-matrix.md`.
- Saída de configuração foi sanitizada; nenhum segredo foi registrado.

## Decisões

- `DEBUG` default é `False`; desenvolvimento deve declarar `DEBUG=True` explicitamente.
- Rate limit permanece por sessão, sem dependência externa.
- `/automation/webhook/` não usa CSRF porque valida assinatura HMAC e idempotência próprias.

## Pendências

Nenhuma pendência técnica da Spec 004.

## Próximo

Executar Spec 005 — observabilidade e resiliência.
