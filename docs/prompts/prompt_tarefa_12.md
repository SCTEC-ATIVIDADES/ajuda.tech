# Documento histórico — não descreve arquitetura operacional atual

# Role: Desenvolvedor Backend Django Sênior

## Contexto
O projeto **Ajuda Tech** (assistente de IA para compra de computadores) está em fase de simplificação do MVP. Conforme definido no PRD original, a aplicação não deve depender de persistência em banco de dados relacional para o histórico de conversas, utilizando apenas a sessão do usuário em memória/cookies para manter o contexto.

Atualmente, o projeto utiliza Django Models (`Conversation` e `Message`) e SQLite, o que diverge da arquitetura pretendida.

## Tarefa
Sua tarefa é refatorar o fluxo de chat para remover completamente a dependência de Models e SQLite, migrando toda a gestão de histórico para `request.session`.

### Atividades Detalhadas:
1. **Refatorar `chat/views.py`**:
    - Alterar `SendMessageView` para que as mensagens (usuário e assistente) sejam armazenadas em uma lista dentro de `request.session['chat_history']`.
    - Alterar `RecommendView` para recuperar o histórico diretamente da sessão.
    - Remover métodos auxiliares que interagem com o banco (ex: `_get_or_create_conversation`).

2. **Desativar `chat/models.py`**:
    - Comentar ou remover as classes `Conversation` e `Message`.
    - Garantir que o `admin.py` não tente registrar esses modelos.

3. **Ajustar `chat/services.py`**:
    - Validar se o cliente da API continua recebendo corretamente a lista de dicionários `{role, content}` vinda da sessão.

4. **Atualizar `chat/tests/`**:
    - Ajustar os testes de view e service para utilizarem o motor de sessão do Django (`self.client.session`) em vez de verificar registros no banco de dados.

5. **Limpeza de Infraestrutura**:
    - Indicar a remoção das migrations em `chat/migrations/`.
    - Garantir que o `settings.py` utilize `SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'` (ou similar em memória).

## Restrições
- A estrutura das mensagens enviadas para a API (OpenRouter) deve permanecer `{"role": "...", "content": "..."}`.
- O histórico não deve ultrapassar 50 mensagens por sessão.
- O funcionamento do frontend não deve ser alterado (os endpoints `/send/` e `/recommend/` devem manter o mesmo contrato JSON).

## Entrega Esperada
1. O código refatorado dos arquivos afetados.
2. Comandos para limpeza de banco e migrations.
3. Plano de testes para validar que a sessão está mantendo o contexto entre requisições.