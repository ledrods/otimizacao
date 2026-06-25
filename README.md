# Problema de Atribuição de Leads Comerciais em uma Startup de Impacto

Trabalho da disciplina **Tópicos em Otimização** — Universidade Federal Rural de Pernambuco (UFRPE), 2026.

**Discentes:** Leandro Dos Santos Cesar · Leon Lourenço da Silva Santos · Vithoria Camila Bastos da Silva

---

## Questão central

> *Como alocar o tempo da equipe comercial sobre os leads disponíveis de forma a maximizar a receita esperada total?*

---

## Contexto

A **Biofábrica de Corais (BFC)** é uma startup pernambucana de restauração de recifes e educação ambiental. Seu funil comercial é gerenciado no CRM Monday.com e cobre produtos variados: associações individuais, patrocínios e projetos PDI/ESG com organizações de grande porte.

Com 3 vendedores e capacidade total de 60 horas por ciclo, a equipe não consegue atender todos os leads com a mesma dedicação. Este trabalho modela formalmente esse problema de alocação e aplica algoritmos de otimização combinatória sobre dados reais do CRM.

---

## Dados

| Arquivo | Descrição |
|---|---|
| `leads_master.csv` | 113 leads reais (76 histórico + 37 ativos), 21 atributos |
| `dicionario_dados.csv` | Dicionário com descrição, completude e notas de cada coluna |
| `tabela_comparativa.csv` | Resumo comparativo dos resultados dos algoritmos |
| `eda.ipynb` | Notebook de análise exploratória dos dados |

Os PDFs `ExplorandoDadosBFC (1).pdf` e `Otimizacao_Modelagem_Leads (1).pdf` documentam o contexto original do problema fornecido pela BFC.

---

## Modelagem

Cada lead $l_i$ recebe um **peso** que representa sua receita esperada:

$$w_i = p_c(l_i) \times V_t(l_i)$$

- $p_c$: probabilidade de conversão estimada pelo nível de interesse declarado no CRM (de 0,10 para leads sem dado até 0,85 para interesse Muito Alto)
- $V_t$: valor estimado do contrato por segmento (PJ: R$ 12.000; PF: R$ 2.500–3.000)

O problema é enquadrado de duas formas:

1. **Mochila Binária (Knapsack 0/1):** quais leads atender? $\max \sum w_i$ sujeito a $\sum t_i \leq C$
2. **Matching Bipartido:** quem atende quem? atribuição de leads a vendedores respeitando a cota individual de 20 h por vendedor

---

## Algoritmos implementados

| Algoritmo | Abordagem | Complexidade | Resultado |
|---|---|---|---|
| Greedy | Ordenar por $w_i/t_i$, alocar até esgotar capacidade | $O(n \log n)$ | 30 leads · R$ 24.669,00 |
| Knapsack 0/1 | Programação dinâmica (granularidade 0,5h) | $O(n \cdot C')$ | **31 leads · R$ 24.727,40** |
| Matching Bipartido | Algoritmo Húngaro por vendedor | $O(V^3)$ | 30 leads · R$ 24.669,00 |

Valor máximo possível (todos os 37 leads): **R$ 25.391,75**

O Knapsack entrega a solução ótima (97,4% do valor máximo). O Matching distribui a carga de forma equilibrada entre os 3 vendedores ao custo de R$ 58,40 em relação ao ótimo.

---

## Arquivos do projeto

```
leads_master.csv          # Dataset principal
dicionario_dados.csv      # Dicionário de dados
simulacoes.py             # Implementação dos 3 algoritmos
figuras_artigo_v2.py      # Geração das 7 figuras do artigo
eda.ipynb                 # Análise exploratória
artigo.tex / artigo.pdf   # Artigo científico (LaTeX)
apresentacao.tex / .pdf   # Apresentação Beamer
roteiro.md                # Roteiro da apresentação (7–9 min)
art_fig*.png / .pdf       # Figuras geradas (usadas no artigo e apresentação)
```

---

## Como reproduzir

**Figuras** (requer Python 3.8+ com pandas, numpy, matplotlib):
```bash
python figuras_artigo_v2.py
```

**Simulações:**
```bash
python simulacoes.py
```

**Compilar artigo e apresentação** (requer MiKTeX ou TeX Live):
```bash
pdflatex artigo.tex && pdflatex artigo.tex
pdflatex apresentacao.tex && pdflatex apresentacao.tex
```
