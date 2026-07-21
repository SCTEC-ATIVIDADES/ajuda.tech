# Exemplos de Execução — Ajuda Tech

Este documento apresenta exemplos reais de interação com o agente Herbert.

---

## Exemplo 1: Saudação e coleta de dados

### Entrada
```
Usuário: oi
```

### Saída
```
Olá! Me chamo Herbert e vou te ajudar a encontrar o computador perfeito
para você. Me conta: para que você pretende usar o computador?
```

---

## Exemplo 2: Fornecendo informações

### Entrada
```
Usuário: quero um notebook pra estudar na faculdade
```

### Saída
```
Ótimo! Para estudos na faculdade você vai precisar de um notebook que
 rode bem o Office, navegue na internet e talvez rode algum software
específico do curso. Qual é o seu orçamento aproximado?
```

---

## Exemplo 3: Recomendação completa

### Entrada
```
Usuário: até 3000 reais
```

### Saída
```
Com R$ 3.000 você consegue um notebook ótimo para estudos! O Samsung Book
i3 é uma ótima opção — processador Intel Core i3, 8 GB de memória e tela
de 15.6". Perfeito para navegar, usar o Office e assistir aulas. Ele custa
R$ 2.799,00 e vai atender muito bem o que você precisa.

Se quiser, posso te mostrar o relatório completo com todas as especificações!
```

---

## Exemplo 4: Sem produtos no catálogo

### Entrada
```
Usuário: quero um desktop gamer até 2000 reais
```

### Saída
```
No momento não temos um produto ideal para o seu perfil no nosso catálogo.
Posso buscar uma opção com orçamento um pouco maior ou outro tipo de
computador.
```

---

## Exemplo 5: Pergunta fora do tema

### Entrada
```
Usuário: qual o melhor antivírus?
```

### Saída
```
Boa pergunta, mas esse assunto está um pouquinho fora do que eu sou
especialista! Meu foco é ajudar na escolha do computador ideal para você.
Se ainda não encontrou o certo, é só me contar o que você precisa e eu
te ajudo!
```

---

## Fluxo interno do agente (debug)

Para visualizar o fluxo interno do agente, ative o log em nível DEBUG:

```env
LOG_LEVEL=DEBUG
```

Exemplo de log com classificação → coleta → recomendação:

```
DEBUG classify_msg: intent=dados
DEBUG gather_needs: needs={'proposito': 'estudos', 'orcamento': 3000, 'mobilidade': 'alta'}
DEBUG recommend: cat=notebook orc=3000 prods=2
  -> Samsung Book i3 R$2799.00
  -> Acer Aspire 3 R$2999.00
DEBUG report: produto Samsung Book i3
```
