# Spec 010 — Entrega final

## Objetivo

Fechar entrega reproduzível, com versão única, dois cenários, evidências externas e submissão conforme prazo.

## Contexto mínimo atual

Esta spec executa ações no GitHub e fora do código. Agente pode validar arquivos e preparar roteiro, mas não inventar acesso, vídeo, Kanban ou submissão.

## Escopo autorizado

`README.md`, `docs/`, `specs/`, `.github/` e metadados Git autorizados; GitHub Project, branches, PRs, vídeo e AVA exigem acesso humano quando indisponível.

## Execução

1. Conferir `main`, `develop`, `feature/*`, PRs e commits semânticos sem reescrever histórico.
2. Atualizar Kanban com tarefa, responsável/status e links.
3. Fechar roteiro normal: necessidade → coleta → grafo → tool → memória → resposta.
4. Fechar roteiro de risco: injection, timeout, serviço indisponível ou rate limit → fallback/sinal seguro.
5. Gravar vídeo não listado, recomendado até 10 e máximo 12 minutos, cobrindo rubrica.
6. Conferir README, código, testes, CI, workflow e vídeo apontam para mesma versão.
7. Testar links em janela anônima, pacote/tamanho e instruções limpas.
8. Submeter antes de 31/08/2026 às 15h e congelar repositório.

## Testes obrigatórios

Validar links, comandos de reprodução, dois cenários, pacote final e consistência entre código, README, CI e vídeo. Sem acesso externo, registrar `BLOCKED`.

## Aceite

Kanban, branches e commits são rastreáveis; dois cenários reproduzíveis; vídeo cobre aplicação e evidências; pacote abre/executa ou explica; riscos e limitações declarados.

## Bloqueios

Sem acesso a GitHub Project, YouTube, AVA ou conta do curso: `BLOCKED`, com ação humana e checklist restante. Não marcar submissão feita.

## Evidências

URL do Project, histórico Git, vídeo, capturas dos cenários, checklist revisado e comprovante de submissão.

## Saída

Relatório `DONE` somente com links verificados e prazo confirmado; caso contrário `PARTIAL` ou `BLOCKED`.

## Próximo

Ação humana: submeter e congelar versão.
