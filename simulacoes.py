"""
Simulações de otimização de alocação de leads BFC.
Três abordagens: Greedy, Knapsack 0/1, Bipartite Matching (Húngaro).
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.optimize import linear_sum_assignment

BLUE, ORANGE, GREEN, RED, PURPLE = '#4878CF', '#E8912D', '#56A45E', '#D65F5F', '#8B5CF6'

# ── Dados ─────────────────────────────────────────────────────────────────────
df = pd.read_csv('leads_master.csv', encoding='utf-8')
ativos = df[df['particao'] == 'ativo'].copy().reset_index(drop=True)

# Capacidade máxima por vendedor (horas/semana úteis × semanas)
# Consenso da equipe: ~20h de atendimento/semana por vendedor
CAPACIDADE_H = 20.0

vendedores = ['Marcela Belo', 'Maria Paula', 'Talita Guedes', 'Karoline Melo', 'Eduarda Malafaia']

n_leads = len(ativos)
n_vend  = len(vendedores)

leads_idx  = list(range(n_leads))
w_vec      = ativos['w_peso_aresta'].values.astype(float)
t_vec      = ativos['t_atendimento_h'].values.astype(float)
ef_vec     = ativos['eficiencia_w_t'].values.astype(float)
nome_vec   = ativos['nome'].values

print(f"Leads ativos: {n_leads} | Vendedores: {n_vend}")
print(f"Capacidade por vendedor: {CAPACIDADE_H}h")
print(f"Capacidade total disponível: {CAPACIDADE_H * n_vend:.0f}h")
print(f"Tempo total requerido (todos os leads): {t_vec.sum():.1f}h\n")

# ═══════════════════════════════════════════════════════════════════════════════
# ALGORITMO 1 — GREEDY (ordenar por eficiência, alocar até capacidade)
# ═══════════════════════════════════════════════════════════════════════════════
def greedy(w, t, capacidade_total):
    ordem = np.argsort(-ef_vec)   # decrescente por w/t
    alocados, valor, tempo = [], 0.0, 0.0
    for i in ordem:
        if tempo + t[i] <= capacidade_total:
            alocados.append(i)
            valor += w[i]
            tempo += t[i]
    return alocados, valor, tempo

cap_total = CAPACIDADE_H * n_vend
g_alocados, g_valor, g_tempo = greedy(w_vec, t_vec, cap_total)
print(f"GREEDY  -> {len(g_alocados)} leads | valor esperado: R${g_valor:,.2f} | tempo: {g_tempo:.1f}h")

# ═══════════════════════════════════════════════════════════════════════════════
# ALGORITMO 2 — KNAPSACK 0/1 (programação dinâmica, granularidade 0.5h)
# ═══════════════════════════════════════════════════════════════════════════════
def knapsack_01(w, t, capacidade, granularidade=0.5):
    n = len(w)
    C = int(round(capacidade / granularidade))
    t_int = [max(1, int(round(ti / granularidade))) for ti in t]

    # DP com array 1D
    dp = np.zeros(C + 1)
    keep = [[False] * (C + 1) for _ in range(n)]

    for i in range(n):
        for c in range(C, t_int[i] - 1, -1):
            novo = dp[c - t_int[i]] + w[i]
            if novo > dp[c]:
                dp[c] = novo
                keep[i][c] = True

    # Rastrear itens escolhidos
    alocados = []
    c = C
    for i in range(n - 1, -1, -1):
        if keep[i][c]:
            alocados.append(i)
            c -= t_int[i]

    valor = sum(w[i] for i in alocados)
    tempo = sum(t[i] for i in alocados)
    return alocados, valor, tempo

k_alocados, k_valor, k_tempo = knapsack_01(w_vec, t_vec, cap_total)
print(f"KNAPSACK-> {len(k_alocados)} leads | valor esperado: R${k_valor:,.2f} | tempo: {k_tempo:.1f}h")

# ═══════════════════════════════════════════════════════════════════════════════
# ALGORITMO 3 — BIPARTITE MATCHING (Húngaro) com restrição de capacidade
# Estratégia: replicar cada vendedor em K slots de capacidade unitária (1 lead/slot)
# Cada lead tem custo -w para maximizar (linear_sum_assignment minimiza)
# ═══════════════════════════════════════════════════════════════════════════════
def bipartite_matching(w, t, vendedores, cap_h):
    """
    Matching leads × slots de vendedor.
    Cada vendedor tem floor(cap_h / min_t) slots.
    Leads não encaixáveis num slot recebem custo 0 (dummy).
    """
    min_t = min(t)
    slots_por_vend = max(1, int(cap_h / min_t))
    total_slots = n_vend * slots_por_vend

    # Matriz de custo (leads × slots) — custo negativo = maximizar valor
    custo = np.zeros((n_leads, total_slots))
    for i in range(n_leads):
        for s in range(total_slots):
            vend_idx = s // slots_por_vend
            custo[i, s] = -w[i]   # mesmo vendedor por slot (sem afinidade)

    row_ind, col_ind = linear_sum_assignment(custo)

    # Reconstruir alocação respeitando capacidade por vendedor
    cap_usada = [0.0] * n_vend
    alocados, alocacao_vend = [], {}
    for lead_i, slot_j in zip(row_ind, col_ind):
        vend_idx = slot_j // slots_por_vend
        if cap_usada[vend_idx] + t[lead_i] <= cap_h and w[lead_i] > 0:
            if lead_i not in alocados:
                alocados.append(lead_i)
                cap_usada[vend_idx] += t[lead_i]
                alocacao_vend[lead_i] = vendedores[vend_idx]

    valor = sum(w[i] for i in alocados)
    tempo = sum(t[i] for i in alocados)
    return alocados, alocacao_vend, valor, tempo, cap_usada

m_alocados, m_alocacao, m_valor, m_tempo, m_cap = bipartite_matching(
    w_vec, t_vec, vendedores, CAPACIDADE_H)
print(f"MATCHING-> {len(m_alocados)} leads | valor esperado: R${m_valor:,.2f} | tempo: {m_tempo:.1f}h")
print(f"  Capacidade usada por vendedor: { {v: f'{c:.1f}h' for v, c in zip(vendedores, m_cap)} }")

# ═══════════════════════════════════════════════════════════════════════════════
# TABELA COMPARATIVA
# ═══════════════════════════════════════════════════════════════════════════════
valor_max_possivel = w_vec.sum()
print(f"\nValor esperado máximo (todos os leads): R${valor_max_possivel:,.2f}")
print(f"Tempo total necessário (todos):         {t_vec.sum():.1f}h")
print(f"Capacidade total disponível:             {cap_total:.0f}h\n")

tabela = pd.DataFrame({
    'Algoritmo':        ['Greedy', 'Knapsack 0/1', 'Bipartite Matching'],
    'Leads alocados':   [len(g_alocados), len(k_alocados), len(m_alocados)],
    'Valor esp. (R$)':  [round(g_valor,2), round(k_valor,2), round(m_valor,2)],
    'Tempo usado (h)':  [round(g_tempo,1), round(k_tempo,1), round(m_tempo,1)],
    'Util. capac. (%)': [round(g_tempo/cap_total*100,1),
                         round(k_tempo/cap_total*100,1),
                         round(m_tempo/cap_total*100,1)],
    'Captura valor (%)': [round(g_valor/valor_max_possivel*100,1),
                          round(k_valor/valor_max_possivel*100,1),
                          round(m_valor/valor_max_possivel*100,1)],
})
print("=== TABELA COMPARATIVA ===")
print(tabela.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURAS PARA O ARTIGO
# ═══════════════════════════════════════════════════════════════════════════════

# ── Fig 6: Comparação dos algoritmos ─────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
algos  = ['Greedy', 'Knapsack\n0/1', 'Matching\nBipartido']
colors = [BLUE, ORANGE, GREEN]

# 6a — Leads alocados
vals_leads = [len(g_alocados), len(k_alocados), len(m_alocados)]
bars = axes[0].bar(algos, vals_leads, color=colors, edgecolor='white', width=0.5)
axes[0].set_ylim(0, n_leads + 3)
axes[0].axhline(n_leads, color='grey', ls='--', lw=1, label=f'Total disponível (n={n_leads})')
axes[0].set_title('Leads alocados')
axes[0].set_ylabel('Nº de leads')
axes[0].legend(fontsize=8)
for bar, v in zip(bars, vals_leads):
    axes[0].text(bar.get_x() + bar.get_width()/2, v + 0.3, str(v),
                 ha='center', fontsize=11, fontweight='bold')

# 6b — Valor esperado total
vals_w = [g_valor, k_valor, m_valor]
bars = axes[1].bar(algos, vals_w, color=colors, edgecolor='white', width=0.5)
axes[1].axhline(valor_max_possivel, color='grey', ls='--', lw=1, label=f'Máximo possível')
axes[1].set_title('Valor esperado total (R$)')
axes[1].set_ylabel('R$')
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x:,.0f}'))
axes[1].legend(fontsize=8)
for bar, v in zip(bars, vals_w):
    axes[1].text(bar.get_x() + bar.get_width()/2, v + 200, f'R${v:,.0f}',
                 ha='center', fontsize=9, fontweight='bold')

# 6c — Utilização da capacidade
vals_util = [g_tempo/cap_total*100, k_tempo/cap_total*100, m_tempo/cap_total*100]
bars = axes[2].bar(algos, vals_util, color=colors, edgecolor='white', width=0.5)
axes[2].set_ylim(0, 110)
axes[2].axhline(100, color='grey', ls='--', lw=1, label='Capacidade total')
axes[2].set_title('Utilização da capacidade (%)')
axes[2].set_ylabel('%')
axes[2].legend(fontsize=8)
for bar, v in zip(bars, vals_util):
    axes[2].text(bar.get_x() + bar.get_width()/2, v + 1, f'{v:.1f}%',
                 ha='center', fontsize=10, fontweight='bold')

plt.suptitle('Figura 6 — Comparação dos algoritmos de otimização\n(leads ativos, n=37, capacidade=100h total)',
             fontsize=12)
plt.tight_layout()
plt.savefig('fig6_comparacao_algoritmos.png', dpi=180, bbox_inches='tight')
plt.close()
print('\nfig6 OK')

# ── Fig 7: Top leads Knapsack (melhor solução) ────────────────────────────────
top_k = sorted(k_alocados, key=lambda i: w_vec[i], reverse=True)[:15]
nomes_k = [nome_vec[i][:18] for i in top_k]
w_k     = [w_vec[i] for i in top_k]
t_k     = [t_vec[i] for i in top_k]

fig, ax = plt.subplots(figsize=(10, 6))
y_pos = range(len(top_k))
bars = ax.barh(y_pos, w_k, color=GREEN, edgecolor='white', alpha=0.88)
ax.set_yticks(y_pos)
ax.set_yticklabels(nomes_k, fontsize=9)
ax.set_xlabel('Valor esperado (R$)')
ax.set_title('Figura 7 — Top leads selecionados pelo Knapsack 0/1\n(ordenados por valor esperado w = Pᶜ × Vt)')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x:,.0f}'))
for bar, w_val, t_val in zip(bars, w_k, t_k):
    ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
            f'R${w_val:,.0f} | {t_val:.1f}h', va='center', fontsize=8)
ax.set_xlim(0, max(w_k) * 1.35)
plt.tight_layout()
plt.savefig('fig7_top_leads_knapsack.png', dpi=180, bbox_inches='tight')
plt.close()
print('fig7 OK')

# ── Fig 8: Distribuição do valor esperado — alocados vs não alocados ──────────
k_set = set(k_alocados)
w_alocados     = [w_vec[i] for i in range(n_leads) if i in k_set]
w_nao_alocados = [w_vec[i] for i in range(n_leads) if i not in k_set]

fig, ax = plt.subplots(figsize=(9, 5))
bins = np.linspace(0, max(w_vec) + 500, 20)
ax.hist(w_alocados,     bins=bins, color=GREEN,  alpha=0.75, label=f'Alocados (n={len(w_alocados)})',     edgecolor='white')
ax.hist(w_nao_alocados, bins=bins, color=RED,    alpha=0.75, label=f'Não alocados (n={len(w_nao_alocados)})', edgecolor='white')
ax.set_xlabel('Valor esperado w (R$)')
ax.set_ylabel('Frequência')
ax.set_title('Figura 8 — Distribuição do valor esperado:\nalocados vs. não alocados (Knapsack 0/1)')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x:,.0f}'))
ax.legend()
plt.tight_layout()
plt.savefig('fig8_alocados_vs_nao.png', dpi=180, bbox_inches='tight')
plt.close()
print('fig8 OK')

# ── Fig 9: Capacidade por vendedor no Matching ────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 4))
nomes_vend_fmt = [v.split()[0] + '\n' + v.split()[1] if len(v.split()) > 1 else v for v in vendedores]
bars = ax.bar(nomes_vend_fmt, m_cap, color=PURPLE, edgecolor='white', alpha=0.85)
ax.axhline(CAPACIDADE_H, color=RED, lw=1.5, ls='--', label=f'Capacidade máx. ({CAPACIDADE_H:.0f}h)')
ax.set_ylabel('Horas utilizadas')
ax.set_title('Figura 9 — Utilização da capacidade por vendedor\n(Bipartite Matching)')
ax.legend()
for bar, v in zip(bars, m_cap):
    ax.text(bar.get_x() + bar.get_width()/2, v + 0.3, f'{v:.1f}h',
            ha='center', fontsize=10, fontweight='bold')
ax.set_ylim(0, CAPACIDADE_H * 1.2)
plt.tight_layout()
plt.savefig('fig9_capacidade_vendedor.png', dpi=180, bbox_inches='tight')
plt.close()
print('fig9 OK')

# ── Salvar tabela comparativa ─────────────────────────────────────────────────
tabela.to_csv('tabela_comparativa.csv', index=False)
print('\nTabela salva em tabela_comparativa.csv')

# ── Detalhe dos leads alocados pelo Knapsack ─────────────────────────────────
detalhe = ativos.iloc[k_alocados][
    ['nome','tipo_cliente','interesse_nivel','responsavel',
     'pc_estimado','vt_estimado_RS','w_peso_aresta','t_atendimento_h','eficiencia_w_t']
].sort_values('w_peso_aresta', ascending=False).reset_index(drop=True)
detalhe.to_csv('leads_alocados_knapsack.csv', index=False)
print(f'Detalhe dos {len(detalhe)} leads Knapsack salvo.')
print(detalhe[['nome','tipo_cliente','interesse_nivel','w_peso_aresta','eficiencia_w_t']].to_string())
