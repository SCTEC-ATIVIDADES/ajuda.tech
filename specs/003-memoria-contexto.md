# Spec 003 — Memória e contexto

## Objetivo

Garantir continuidade, limites explícitos, nova conversa previsível e contexto seguro durante execução do agente.

## Contexto mínimo atual

Memória atual usa `request.session` em `chat/views.py`; histórico tem limite declarado divergente; `GET /` pode limpar sessão; não há checkpointer confirmado.

## Escopo autorizado

Alterar `chat/views.py`, `chat/agent/state.py`, `chat/agent/graph.py`, `ajuda_tech/settings.py`, testes de views/limites e `README.md`.

## Execução

1. Inspecionar sessão e testes atuais.
2. Separar histórico, necessidades estruturadas, thread/run ID e contexto recuperado.
3. Fixar limites: histórico máximo 50 entradas, janela LLM máxima 20 mensagens e tamanho máximo de mensagem; se mudar, atualizar todas as specs.
4. Remover limpeza em GET; criar limpeza somente em ação explícita existente ou mínima.
5. Escolher persistência mínima já disponível; evitar banco/checkpointer novo sem necessidade para aceite.
6. Não guardar segredos ou dados pessoais sensíveis.
7. Registrar falha de persistência sem perda silenciosa.

## Testes obrigatórios

Continuidade entre duas requisições, truncamento, nova conversa, sessão expirada, payload grande e ausência de chamada LLM além da janela.

## Aceite

Necessidades conhecidas sobrevivem; limites são aplicados; recarregar página não apaga conversa; nova conversa limpa explicitamente; falhas são seguras e observáveis.

## Evidências

Estado antes/depois, testes e documentação de retenção/privacidade.

## Saída

Usar contrato de `000`: STATUS, arquivos, testes, evidências, decisões e pendências.

## Próximo

`004`.
