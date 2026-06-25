# Roteiro de Apresentação
**Problema de Atribuição de Leads Comerciais em uma Startup de Impacto**
Tópicos em Otimização — UFRPE, Junho de 2026
Leandro Dos Santos Cesar · Leon Lourenço da Silva Santos · Vithoria Camila Bastos da Silva

---

## Tempo total: 7 a 9 minutos

---

### Slide 1 — Capa
*(~20 s — silêncio ou abertura rápida)*

> "Bom dia/Boa tarde. Vamos apresentar um trabalho de otimização aplicado a dados reais de uma startup pernambucana de impacto ambiental."

---

### Slide 2 — A BFC e o desafio comercial
*(~1 min)*

> "A Biofábrica de Corais é uma startup que faz restauração de recifes de coral e educação ambiental. O braço comercial deles gerencia leads no CRM Monday.com — clientes potenciais que vão desde pessoas físicas querendo uma associação, até grandes empresas com projetos de ESG.

> O problema: eles têm 113 leads cadastrados, 37 desses estão ativos esperando contato, e apenas 3 vendedores para atender todos. O grafo aqui mostra isso visualmente — os nós à esquerda são os leads, à direita os vendedores, e a espessura da aresta representa o valor esperado de cada relação. Reparem que 'Simone' tem a aresta mais grossa de longe."

---

### Slide 3 — A questão
*(~40 s)*

> "A pergunta que guia todo o trabalho é essa: como alocar o tempo da equipe sobre os leads disponíveis de forma a maximizar a receita esperada total?

> Sem um critério formal, a equipe distribui leads por intuição. Com otimização, a gente substitui isso por uma regra baseada em valor esperado — auditável e replicável."

---

### Slide 4 — O modelo
*(~1 min 30 s)*

> "Para quantificar o valor de cada lead, definimos o peso: w igual a probabilidade de conversão vezes o valor estimado do contrato.

> A probabilidade de conversão vem de um sinal que já existe no CRM: o interesse declarado pelo cliente. Alguém que perguntou o horário de visita tem chance de 85%. Alguém sem nenhum dado registrado tem 10%. A tabela está aqui.

> Com esse peso definido, o problema se encaixa em dois formatos clássicos. O primeiro é a Mochila Binária: maximizar a soma dos pesos escolhendo quais leads atender, respeitando a capacidade total de horas. O segundo é o Matching Bipartido: em vez de só escolher quais, atribuir cada lead a um vendedor respeitando a cota individual de cada um. Testamos os dois, mais um Greedy como heurística rápida."

---

### Slide 5 — Carteira ativa: distribuição de valor
*(~40 s)*

> "Antes dos resultados, uma olhada nos dados. A carteira ativa tem uma distribuição muito concentrada. Olhando o gráfico, vemos um grande outlier à direita — é a Simone, com valor esperado de R$ 7.800. Ela representa 30% da carteira inteira. E ela estava sem vendedor atribuído no CRM."

---

### Slide 6 — O achado estrutural
*(~1 min)*

> "Quando rodamos os algoritmos, apareceu um achado que muda a natureza da pergunta. O tempo total para atender todos os 37 leads ativos é de 72,5 horas. A capacidade disponível da equipe é de 100 horas.

> Isso significa que não existe um problema de seleção — não precisamos descartar nenhum lead. A pergunta deixa de ser 'quais atender' e passa a ser 'como distribuir bem entre os vendedores'."

---

### Slide 7 — Comparativo dos três algoritmos
*(~1 min)*

> "Os resultados confirmam o achado. Greedy e Knapsack chegam ao mesmo resultado: alocam todos os 37 leads, capturam R$ 25.391 — 100% do valor possível. São equivalentes aqui porque a restrição de capacidade total não estava ativa.

> O Matching Bipartido chega a R$ 22.750 — alocou 30 leads. Ele respeita a cota individual de cada vendedor, então quando um vendedor chega no limite, os leads excedentes ficam sem atendimento."

---

### Slide 8 — Matching: carga por vendedor
*(~40 s)*

> "Esse gráfico mostra por que o Matching perdeu valor. Dois vendedores ficaram praticamente ociosos enquanto outros chegaram no limite. O algoritmo equilibra carga, mas paga um custo de 10% do valor esperado. Essa é uma decisão de gestão: prefere-se equidade ou maximização?"

---

### Slide 9 — Resposta à questão central
*(~1 min)*

> "Então, respondendo diretamente: como maximizar a receita esperada?

> Primeiro, ação imediata no CRM: atribuir a Simone a um vendedor agora. É R$ 7.800 potenciais sem nenhum ajuste de modelo — só abrir o sistema.

> Segundo: atender todos os 37 leads. A capacidade sobra, não há motivo para descartar nenhum.

> Terceiro: os 8 leads com valor acima de R$ 500 concentram 85% da carteira — esses vão para os vendedores com maior taxa histórica de conversão.

> Quarto: a escolha entre Greedy/Knapsack e Matching depende da gestão. Se equidade de carga importa, usa o Matching e aceita perder 10% de valor."

---

### Slide 10 — Conclusão
*(~40 s)*

> "Para fechar: modelamos 113 leads reais como grafo bipartido e mochila binária, implementamos três algoritmos e entregamos uma resposta quantitativa.

> As limitações são claras — 99% dos valores de contrato são estimativas por segmento, e a afinidade vendedor-lead não foi calculada por falta de histórico estratificado. O modelo melhora à medida que o CRM é alimentado com mais dados. A otimização começa pelo CRM."

---

### Slide 11 — Encerramento
*(~10 s)*

> "Obrigado. Ficamos à disposição para perguntas."

---

## Notas gerais

- **Não ler os slides.** O texto nos slides é mínimo por design — o roteiro acima é o que vai ser falado.
- **Slide 5 (gráfico):** apontar visualmente o outlier à direita enquanto fala de Simone.
- **Slide 7 (comparativo):** apontar as barras dos três algoritmos enquanto explica a diferença.
- **Slide 8 (carga):** mencionar os dois vendedores com barra baixa enquanto fala de ociosidade.
- **Perguntas prováveis:**
  - *"Por que A=1 para afinidade?"* — Não temos histórico estratificado por vendedor/produto. É uma limitação documentada.
  - *"O modelo é aplicável agora?"* — Sim, com os parâmetros atuais já dá a priorização. A estimativa de Vt é o gargalo principal.
  - *"O que muda se o número de leads crescer?"* — O Greedy passa a ser subótimo; o Knapsack mantém a solução exata; o Matching escala bem.
