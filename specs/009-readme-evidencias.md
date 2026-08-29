# Spec 009 — README e evidências

## Objetivo

Alinhar documentação ao código final e criar matriz requisito → implementação → teste/evidência → status.

## Contexto mínimo atual

README e docs atuais possuem divergências históricas. Implementações de 001–008 e relatórios dos agentes são fonte de verdade; não manter plano descrito como funcional.

## Escopo autorizado

`README.md`, `docs/`, `specs/`, `.env.example` e diretório de evidências existente ou criado somente se necessário. Não alterar código funcional sem abrir bloqueio para spec anterior.

## Execução

1. Ler código final e todos relatórios anteriores.
2. Corrigir endpoints, nós, estado, tools, memória, limites, comandos e paths.
3. Documentar instalação, testes, demo, arquitetura, prompts, modelo por ambiente, refinamentos, segurança e limitações.
4. Organizar evidências sanitizadas de QA, CI, logs, low-code e cenários.
5. Montar tabela dos 15 critérios da rubrica com links reais e status `DONE/PARTIAL/BLOCKED`.
6. Verificar links locais, URLs já fornecidas e instruções em ambiente limpo.
7. Revisar README com IA e revisão humana; registrar ambas sem credenciais.

## Testes obrigatórios

Verificação de links/paths, comandos de instalação/teste e coerência entre README e código.

## Aceite

Avaliador entende, configura, executa e verifica solução sem contexto oculto. Nenhum item parcial é mascarado como concluído.

## Bloqueios

Vídeo, Kanban, permissões e URLs externas sem acesso ficam pendentes e identificados.

## Evidências

README final, matriz de rastreabilidade, histórico de prompts e links acessíveis.

## Saída

Usar contrato de `000`: STATUS, arquivos, testes, evidências, decisões e pendências.

## Próximo

`010`.
