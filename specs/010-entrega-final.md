# Spec 010 — Entrega final

## Resumo das lacunas

- Não há evidência comprovada de GitHub Project Kanban.
- Branches `develop`, `feature/*` e `main` não estão comprovadas.
- Vídeo final e roteiro ainda não estão reunidos.
- Dois cenários obrigatórios, normal e risco/falha, não estão fechados.
- Commits semânticos e rastreabilidade final precisam ser conferidos.

## Planejamento detalhado

1. Criar/organizar GitHub Project com colunas backlog, fazendo, revisão e concluído.
2. Garantir branches e pull requests rastreáveis, sem reescrever histórico necessário.
3. Usar commits semânticos nas alterações finais.
4. Preparar cenário normal: usuário informa necessidade, agente coleta contexto, executa grafo, consulta tools e responde.
5. Preparar cenário de risco/falha: injection, timeout, serviço indisponível ou limite excedido.
6. Gravar vídeo de até 10 minutos, máximo 12, mostrando produto, arquitetura, execução, evidências e análise crítica.
7. Validar links, permissões, vídeo não listado e prazo de submissão.
8. Montar pacote final conforme regras do curso.

## TODO

- [ ] Conferir branch base e branches de trabalho.
- [ ] Organizar Kanban.
- [ ] Fechar dois roteiros reproduzíveis.
- [ ] Gravar vídeo.
- [ ] Revisar pacote e tamanho.
- [ ] Verificar links em janela anônima.
- [ ] Fazer submissão antes de 31/08/2026 15h.

## Dúvidas técnicas em aberto

- Onde será hospedado o vídeo e quem poderá vê-lo?
- Avaliador terá acesso ao GitHub Project privado?
- Entrega exige ZIP, link ou ambos?
- Quais integrantes e créditos devem aparecer no vídeo?

## Critérios de aceite

- Kanban mostra tarefas, responsáveis/status e histórico.
- Branches e commits comprovam desenvolvimento rastreável.
- Vídeo não listado respeita duração máxima e cobre rubrica.
- Cenário normal funciona com evidência.
- Cenário de risco falha de modo seguro e deixa sinais observáveis.
- README, código, testes, CI, workflow e vídeo apontam para a mesma versão.
- Pacote final abre, executa ou possui instruções válidas.

## Arquivos afetados

- `README.md`
- `specs/`
- `docs/`
- `.github/`
- GitHub Project, branches, tags e pull requests
- Roteiro e vídeo fora do repositório

## Evidências esperadas

- URL do Project.
- Histórico de branches/PRs/commits.
- Vídeo não listado.
- Capturas dos cenários.
- Checklist final assinado/revisado.
- Pacote ou link de submissão.

## Dependências

- [009](009-readme-evidencias.md)
- Todas as implementações e evidências anteriores.
