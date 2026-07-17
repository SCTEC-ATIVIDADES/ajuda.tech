# Prompt — Módulo 2: Implementação do Agente LangGraph

## 1. Prompts Utilizados

### Prompt 4 — Decisões do Grupo + Início da Implementação

**Data:** 16/07/2026

```markdown
Vamos começar a implementar o módulo 2 do projeto com langgraph. ajuda para
seguir os passos: - Perguntas para o grupo
[ ] Qual model LLM usar? (manter DeepSeek ou trocar?)
Manter

[ ] Quantas tools criar no mínimo? (1 basta, mas 3 é mais robusto)
3

[ ] Usar checkpointer SQLite ou manter cookie? Manter cookies e deixar por ultimo

[ ] Criar um agente simples (4 nós) ou mais completo (6+ nós)? os 6 sugeridos

[ ] Como dividir as tarefas entre integrantes? vamos fazer juntos passo 1 e 2.
o resto vamos dividir
```

**Objetivo:** Definir decisões do grupo e iniciar a implementação do agente LangGraph.

**Decisões tomadas:**

| Pergunta | Decisão |
|----------|---------|
| Qual model LLM usar? | Manter DeepSeek (`deepseek/deepseek-v4-flash:free`) |
| Quantas tools criar? | 3 tools (`buscar_produtos`, `comparar_produtos`, `gerar_relatorio`) |
| Checkpointer? | Manter cookies (checkpointer por último) |
| Nós do grafo? | 6 nós sugeridos (classify, greet, gather, extract, recommend, report, respond) |
| Divisão de tarefas | Passo 1 e 2 juntos; resto dividido |

**Arquivos criados nesta etapa:**
- `chat/agent/__init__.py`
- `chat/agent/state.py`
- `chat/agent/tools.py`
- `chat/agent/nodes.py`
- `chat/agent/graph.py`
- `produtos.json`
- `requirements.txt` (atualizado)
- `chat/views.py` (atualizado — novo endpoint)
- `chat/urls.py` (atualizado — nova rota)

---

### Prompt 5 — Documentação de Prompts

**Data:** 16/07/2026

```markdown
Salve meus prompts para gerar este documento como necessário reorganize e padronize.
```

**Objetivo:** Salvar e organizar os prompts usados na fase de planejamento do Módulo 2.

**Arquivo gerado:** `docs/prompts/prompt-modulo2-langgraph-evolucao.md`

---

### Prompt 6 — Correção de Data

**Data:** 16/07/2026

```markdown
Faltou colocar a data
```

**Objetivo:** Adicionar data em cada seção de prompt do arquivo de documentação.

**Alteração aplicada:** Adicionada `**Data:** 16/07/2026` em cada prompt do arquivo `prompt-modulo2-langgraph-evolucao.md`.

---

### Prompt 7 — Branch Nova para Prompts

**Data:** 16/07/2026

```markdown
suba o arquivo em uma branch nova docs/langgraph-m2-prompt
```

**Objetivo:** Criar branch separada para o arquivo de prompts.

**Branch criada:** `docs/langgraph-m2-prompt`
**Commit:** `e960feb` — `docs: add prompts for LangGraph module 2 evolution plan`

---

### Prompt 8 — Documentação por Data

**Data:** 16/07/2026

```markdown
Documente os prompts do que foi gerado da sessão do módulo 2 por data.
```

**Objetivo:** Documentar todos os prompts da sessão de implementação do Módulo 2.

**Arquivo gerado:** Este arquivo (`docs/prompts/prompt-modulo2-langgraph-implementacao.md`)

---

## 2. Prompts Internos dos Nós LangGraph

Cada nó do grafo contém um prompt interno enviado ao LLM. Abaixo os prompts completos de cada nó.

### Nó `classify_msg`

**Arquivo:** `chat/agent/nodes.py` (linha 34)

```
Classifique a mensagem do usuário em UMA das categorias abaixo:
- saudacao: cumprimentos, "oi", "olá", "bom dia", etc.
- dados: o usuário está fornecendo informações (propósito, orçamento, mobilidade)
- pergunta: o usuário quer saber algo sobre computadores, especificações, diferenças
- recomendacao: o usuário pede uma recomendação ou sugestão de produto

Mensagem do usuário: "{user_text}"

Responda APENAS com a categoria (uma palavra).
```

**Objetivo:** Classificar a intenção do usuário para roteamento no grafo.
**Saída esperada:** Uma palavra (`saudacao`, `dados`, `pergunta` ou `recomendacao`).

---

### Nó `greet`

**Arquivo:** `chat/agent/nodes.py` (linha 59)

```
Você é Herbert, assistente da Ajuda Tech.
O usuário acabou de cumprimentar. Responda de forma breve e amigável (1-2 frases),
diga que você ajuda a escolher computadores e pergunte como pode ajudar.
```

**Objetivo:** Gerar resposta de saudação personalizada.
**Saída esperada:** Mensagem curta e amigável (1-2 frases).

---

### Nó `gather_needs`

**Arquivo:** `chat/agent/nodes.py` (linha 81)

```
Você é Herbert, assistente da Ajuda Tech.

Analise a conversa abaixo e extraia as necessidades do usuário.
Necessidades conhecidas até agora: {current_needs}

Conversa:
{history}

Extraia e retorne um JSON com as seguintes chaves (preencha o que conseguir):
{
  "proposito": "para que o computador será usado (ex: estudos, games, escritório)",
  "orcamento": valor numérico máximo em reais (ou null se não informado),
  "mobilidade": "alta", "media" ou "baixa" (ou null se não informado),
  "prioridades": ["lista", "de", "prioridades"]
}

Se o usuário não forneceu uma informação ainda, deixe null.
Retorne APENAS o JSON, sem texto adicional.
```

**Objetivo:** Extrair e estruturar as necessidades do usuário a partir da conversa.
**Saída esperada:** JSON com `proposito`, `orcamento`, `mobilidade`, `prioridades`.

---

### Nó `extract_context`

**Arquivo:** `chat/agent/nodes.py` (linha 122)

```
Você é Herbert, assistente da Ajuda Tech.

Analise as necessidades coletadas do usuário e confirme se estão suficientes
para fazer uma recomendação:

{needs}

Necessidades mínimas para recomendar:
- propósito de uso (obrigatório)
- orçamento ou faixa de preço (obrigatório)

Responda um JSON:
{
  "suficiente": true/false,
  "mensagem_confirmacao": "resumo do que entendeu do usuário",
  "faltando": ["lista de informações faltantes"]
}

Retorne APENAS o JSON.
```

**Objetivo:** Validar se os dados coletados são suficientes para recomendar.
**Saída esperada:** JSON com `suficiente` (boolean), `mensagem_confirmacao`, `faltando`.

---

### Nó `recommend`

**Arquivo:** `chat/agent/nodes.py` (linha 182)

```
Você é Herbert, assistente da Ajuda Tech.

Necessidades do usuário:
- Propósito: {proposito}
- Orçamento: R$ {orcamento}
- Mobilidade: {mobilidade}

Produtos disponíveis no catálogo:
{produtos}

Com base nas necessidades e produtos disponíveis, gere uma recomendação clara
e objetiva em linguagem simples (máximo 3 frases).
Explique por que o produto recomendado atende as necessidades.

Se nenhum produto se encaixar, diga que não encontrou algo adequado e sugira
aumentar o orçamento ou mudar os critérios.

Retorne apenas o texto da recomendação.
```

**Objetivo:** Gerar recomendação personalizada com base nos produtos encontrados.
**Saída esperada:** Texto de recomendação em linguagem simples (máximo 3 frases).
**Tool utilizada:** `buscar_produtos` (chamada antes do prompt para obter produtos do catálogo).

---

### Nó `report`

**Arquivo:** `chat/agent/nodes.py` (linha 210)

Este nó não contém prompt de texto — ele invoca a tool `gerar_relatorio` diretamente com os dados do produto selecionado.

**Parâmetros passados à tool:**
- `nome`: Nome do produto
- `preco`: Preço em reais
- `tipo`: "notebook" ou "desktop"
- `especificacoes`: Dict com specs técnicas
- `justificativa`: Por que o produto foi indicado

**Objetivo:** Gerar relatório estruturado em Markdown.
**Saída esperada:** Relatório em Markdown com tabelas e especificações.

---

### Nó `respond`

**Arquivo:** `chat/agent/nodes.py` (linha 243)

```
Você é Herbert, assistente da Ajuda Tech.

Monte a resposta final para o usuário com base na recomendação e relatório:

Recomendação:
{recommendation}

Relatório:
{report_text}

Instruções:
- Responda de forma amigável e simples (máximo 4 frases)
- Destaque o produto recomendado e o preço
- Ofereça gerar o relatório completo se o usuário quiser
- Não use jargões técnicos

Retorne apenas a mensagem final para o usuário.
```

**Objetivo:** Montar a resposta final completa para o usuário.
**Saída esperada:** Mensagem amigável com recomendação e oferta de relatório.

---

## 3. Dados da Execução

| Campo | Valor |
|-------|-------|
| **Data** | 16/07/2026 |
| **Ferramenta** | opencode (mimo-v2.5-free) |
| **Ciclos** | 8 prompts |

---

## 4. Padrões de Prompting Aplicados

| Padrão | Onde foi aplicado | Evidência |
|--------|------------------|-----------|
| **Contexto + Tarefa** | Prompt 4 | "Vamos começar a implementar... segue as perguntas para o grupo" |
| **Dados brutos + Esperado** | Prompt 4 | Tabela de perguntas com respostas diretas |
| **Correção direta** | Prompt 6 | "Faltou colocar a data" |
| **Instrução concisa** | Prompt 7 | "suba o arquivo em uma branch nova" |
| **Role-based** | Nós internos | "Você é Herbert, assistente da Ajuda Tech" |
| **Few-shot (JSON)** | Nós gather, extract | Exemplos de JSON estruturado nos prompts |
| **Restrição de saída** | Nós classificar, gather, extract | "Retorne APENAS o JSON" / "APENAS com a categoria" |

---

## 5. Arquivos Gerados nesta Sessão

| Arquivo | Descrição |
|---------|-----------|
| `chat/agent/__init__.py` | Módulo LangGraph |
| `chat/agent/state.py` | Estado compartilhado (AgentState TypedDict) |
| `chat/agent/tools.py` | 3 tools: buscar_produtos, comparar_produtos, gerar_relatorio |
| `chat/agent/nodes.py` | 7 nós do grafo com prompts internos |
| `chat/agent/graph.py` | StateGraph montado e compilado |
| `produtos.json` | Base de dados com 12 produtos |
| `chat/views.py` | Atualizado com AgentSendMessageView |
| `chat/urls.py` | Atualizado com rota `/agent/send/` |
| `requirements.txt` | Atualizado com langgraph e langchain-core |
| `docs/MODULO2_LANGGRAPH_EVOLUCAO.md` | Plano de evolução do projeto |
| `docs/prompts/prompt-modulo2-langgraph-evolucao.md` | Prompts da fase de planejamento |
| `docs/prompts/prompt-modulo2-langgraph-implementacao.md` | Este arquivo |
