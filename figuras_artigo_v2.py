"""
Figuras do artigo v2 - corrigidas para nao sobrepor textos.
Estilo acadêmico limpo, margens generosas, fontes menores onde necessário.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

# Estilo global limpo
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.titlepad': 10,
    'axes.labelsize': 10,
    'xtick.labelsize': 8.5,
    'ytick.labelsize': 8.5,
    'legend.fontsize': 8.5,
    'figure.dpi': 180,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
    'savefig.dpi': 200,
})

C1 = '#1A3A5C'   # azul muito escuro
C2 = '#2C5F8A'   # azul escuro
C3 = '#5B9EC9'   # azul medio
C4 = '#A8C8E8'   # azul claro
CGRAY  = '#888888'
CDGRAY = '#444444'
CRED   = '#B03A2E'
CGRN   = '#1E8449'

df     = pd.read_csv('leads_master.csv', encoding='utf-8')
hist   = df[df['particao'] == 'historico'].copy()
ativos = df[df['particao'] == 'ativo'].copy().reset_index(drop=True)
hist['conv'] = pd.to_numeric(hist['converteu'], errors='coerce')

w_vec  = ativos['w_peso_aresta'].values.astype(float)
t_vec  = ativos['t_atendimento_h'].values.astype(float)

CAPACIDADE_H = 20.0
n_vend = 3
cap_total = CAPACIDADE_H * n_vend

# Resultados das simulacoes (3 vendedores, cap_total=60h)
res = {
    'Greedy':             {'leads': 30, 'valor': 24669.00, 'tempo': 59.0},
    'Knapsack 0/1':       {'leads': 31, 'valor': 24727.40, 'tempo': 60.0},
    'Match. Bipartido':   {'leads': 30, 'valor': 24669.00, 'tempo': 59.0},
}
valor_max = w_vec.sum()

# ─────────────────────────────────────────────────────────────────────────────
# FIG 1 - Completude por coluna
# ─────────────────────────────────────────────────────────────────────────────
pct = (df.replace('', np.nan).notna().sum() / len(df) * 100).round(1).sort_values()

rename = {
    'lead_id': 'lead\_id',
    'nome': 'nome',
    'particao': 'particao',
    'status_funil': 'status\_funil',
    'converteu': 'converteu',
    'tipo_cliente': 'tipo\_cliente',
    'interesse_nivel': 'interesse\_nivel',
    'interesse_produto': 'interesse\_produto',
    'responsavel': 'responsavel',
    'data_criacao': 'data\_criacao',
    'data_inicio_negociacao': 'data\_inicio\_neg.',
    'dias_no_funil': 'dias\_no\_funil',
    'pc_estimado': 'pc\_estimado',
    'pc_fonte': 'pc\_fonte',
    'vt_estimado_RS': 'vt\_estimado',
    'vt_fonte': 'vt\_fonte',
    't_atendimento_h': 't\_atend. (h)',
    't_fonte': 't\_fonte',
    'w_peso_aresta': 'w = pc x Vt',
    'eficiencia_w_t': 'eficiencia (w/t)',
    'qualidade_dado': 'qualidade\_dado',
}
labels = [rename.get(c, c) for c in pct.index]
colors_bar = [CRED if v < 50 else CGRAY if v < 80 else C2 for v in pct.values]

fig, ax = plt.subplots(figsize=(7, 6))
bars = ax.barh(labels, pct.values, color=colors_bar, edgecolor='white', linewidth=0.5, height=0.65)
ax.axvline(100, color='black', lw=0.6, ls='--', alpha=0.4)
ax.set_xlabel('Completude (%)', labelpad=6)
ax.set_title('Completude das colunas do dataset', pad=10)
ax.set_xlim(0, 128)
# Rotulos fora da barra para nao sobrepor
for bar, val in zip(bars, pct.values):
    ax.text(val + 1.5, bar.get_y() + bar.get_height() / 2,
            f'{val:.0f}%', va='center', fontsize=7.5, color=CDGRAY)

patch_alta  = mpatches.Patch(color=C2,    label='$\geq$ 80%')
patch_media = mpatches.Patch(color=CGRAY, label='50-79%')
patch_baixa = mpatches.Patch(color=CRED,  label='< 50%')
ax.legend(handles=[patch_alta, patch_media, patch_baixa],
          loc='lower right', framealpha=0.9, fontsize=8)
plt.tight_layout()
plt.savefig('art_fig1_completude.png')
plt.savefig('art_fig1_completude.pdf')
plt.close()
print('fig1 OK')

# ─────────────────────────────────────────────────────────────────────────────
# FIG 2 - Distribuicao de pc e comparacao historico x ativo
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))

# 2a - histograma pc por fonte
for fonte, cor, label in [
    ('prior_interesse', C2,  'Interesse declarado (n=67)'),
    ('prior_sem_dado',  C4,  'Sem dado - prior minimo (n=46)'),
]:
    sub = df[df['pc_fonte'] == fonte]['pc_estimado']
    axes[0].hist(sub, bins=12, color=cor, alpha=0.88, edgecolor='white', label=label)
axes[0].set_xlabel('Probabilidade de conversao estimada ($p_c$)', labelpad=5)
axes[0].set_ylabel('Frequencia')
axes[0].set_title('Distribuicao de $p_c$ por fonte de estimativa')
axes[0].legend(loc='upper right')
axes[0].set_xlim(-0.05, 1.0)

# 2b - boxplot por particao
data_parts = [
    df[df['particao'] == 'historico']['pc_estimado'].values,
    df[df['particao'] == 'ativo']['pc_estimado'].values,
]
bp = axes[1].boxplot(data_parts, patch_artist=True, widths=0.38,
                     medianprops=dict(color='black', lw=2),
                     flierprops=dict(marker='o', markersize=3, alpha=0.5))
for patch, cor in zip(bp['boxes'], [C2, C4]):
    patch.set_facecolor(cor)
    patch.set_alpha(0.85)
axes[1].set_xticklabels(['Historico\n(n=76)', 'Ativos\n(n=37)'])
axes[1].set_ylabel('$p_c$ estimado')
axes[1].set_title('$p_c$ por particao do dataset')
axes[1].set_ylim(-0.05, 1.05)
axes[1].yaxis.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('art_fig2_pc.png')
plt.savefig('art_fig2_pc.pdf')
plt.close()
print('fig2 OK')

# ─────────────────────────────────────────────────────────────────────────────
# FIG 3 - Grafo bipartido esquematico (mais legivel)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, 10)
ax.set_ylim(-0.5, 7.5)
ax.axis('off')

leads_ex = [
    ('Simone (PJ)', 'Alto', 7800),
    ('Monica Brasil (PF)', 'Alto', 1625),
    ('Ana Barbara (PJ)', 'sem dado', 679),
    ('Lucas Diniz (PJ)', 'sem dado', 659),
    ('Marina Barck', 'sem dado', 191),
]
vend_ex = [
    ('Marcela Belo', 'Cap. 20h'),
    ('Maria Paula', 'Cap. 20h'),
    ('Talita Guedes', 'Cap. 20h'),
]

ly = [6.5, 5.0, 3.5, 2.0, 0.5]
vy = [5.5, 3.0, 0.5]

# Leads (esquerda)
for i, (nome, nivel, w) in enumerate(leads_ex):
    rect = mpatches.FancyBboxPatch((0.1, ly[i] - 0.32), 3.2, 0.64,
        boxstyle='round,pad=0.08', facecolor=C4, edgecolor=C2, linewidth=1.2, zorder=3)
    ax.add_patch(rect)
    ax.text(1.7, ly[i] + 0.08, nome, ha='center', va='center',
            fontsize=8, fontweight='bold', zorder=4, color=C1)
    ax.text(1.7, ly[i] - 0.17, f'nivel: {nivel}  |  w = R${w:,}',
            ha='center', va='center', fontsize=7, zorder=4, color=CDGRAY)

# Vendedores (direita)
for j, (vend, cap) in enumerate(vend_ex):
    rect = mpatches.FancyBboxPatch((6.7, vy[j] - 0.32), 3.1, 0.64,
        boxstyle='round,pad=0.08', facecolor=C2, edgecolor=C1, linewidth=1.2, zorder=3)
    ax.add_patch(rect)
    ax.text(8.25, vy[j] + 0.08, vend, ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='white', zorder=4)
    ax.text(8.25, vy[j] - 0.17, cap, ha='center', va='center',
            fontsize=7.5, color='#C8DFF0', zorder=4)

# Arestas representativas com espessura proporcional a w
edges = [
    (0, 0, 7800),
    (1, 0, 1625),
    (1, 1, 1625),
    (2, 1, 679),
    (3, 2, 659),
    (4, 2, 191),
]
max_w = 7800
for (li, vi, w) in edges:
    lw = 0.6 + 4.0 * (w / max_w)
    alpha = 0.35 + 0.55 * (w / max_w)
    ax.plot([3.3, 6.7], [ly[li], vy[vi]],
            color=C2, lw=lw, alpha=alpha, zorder=1, solid_capstyle='round')
    # rotulo no meio da aresta
    xm, ym = 5.0, ly[li] * 0.45 + vy[vi] * 0.55
    ax.text(xm, ym, f'R${w:,}', fontsize=6.5, ha='center',
            va='center', color=CDGRAY,
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))

# Cabecalhos
ax.text(1.7, 7.2, 'Leads  (L)', ha='center', fontsize=11,
        fontweight='bold', color=C1)
ax.text(8.25, 7.2, 'Vendedores  (V)', ha='center', fontsize=11,
        fontweight='bold', color=C1)

# Legenda espessura
ax.text(5.0, 7.2,
        'Espessura da aresta\nproportional a $w_{ij} = p_c \cdot V_t$',
        ha='center', fontsize=8, style='italic', color=CGRAY)

ax.text(5.0, -0.4,
        'Grafo bipartido $G = (L, V, E)$ --- cinco leads representativos e tres vendedores',
        ha='center', fontsize=9, color=CDGRAY)

plt.tight_layout()
plt.savefig('art_fig3_grafo.png')
plt.savefig('art_fig3_grafo.pdf')
plt.close()
print('fig3 OK')

# ─────────────────────────────────────────────────────────────────────────────
# FIG 4 - Vendedores (uma figura por subfigura, sem texto sobreposto)
# ─────────────────────────────────────────────────────────────────────────────
vend_df   = df[df['responsavel'].notna() & (df['responsavel'] != '')].copy()
vend_hist = vend_df[vend_df['particao'] == 'historico'].copy()
vend_hist['conv_num'] = pd.to_numeric(vend_hist['converteu'], errors='coerce')

resumo = vend_hist.groupby('responsavel').agg(
    n_leads  = ('lead_id', 'count'),
    taxa     = ('conv_num', 'mean'),
    w_total  = ('w_peso_aresta', 'sum'),
).sort_values('n_leads', ascending=True)
resumo['taxa_pct'] = (resumo['taxa'] * 100).round(1)

vnames = [v.split()[0] for v in resumo.index]

fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

# 4a - leads
axes[0].barh(vnames, resumo['n_leads'], color=C2, edgecolor='white', height=0.55)
axes[0].set_title('Leads no historico por vendedor')
axes[0].set_xlabel('Numero de leads')
axes[0].set_xlim(0, resumo['n_leads'].max() * 1.28)
for i, v in enumerate(resumo['n_leads']):
    axes[0].text(v + 0.4, i, str(int(v)), va='center', fontsize=9)

# 4b - taxa conversao
tc_colors = [CGRN if v >= 90 else C3 for v in resumo['taxa_pct']]
axes[1].barh(vnames, resumo['taxa_pct'], color=tc_colors, edgecolor='white', height=0.55)
axes[1].set_title('Taxa de conversao no historico (%)')
axes[1].set_xlabel('Taxa (%)')
axes[1].set_xlim(0, 125)
axes[1].axvline(100, color='black', lw=0.7, ls='--', alpha=0.5)
for i, v in enumerate(resumo['taxa_pct']):
    axes[1].text(v + 1, i, f'{v:.0f}%', va='center', fontsize=9)

# 4c - valor esperado total
axes[2].barh(vnames, resumo['w_total'], color=C4, edgecolor=C2, linewidth=0.8, height=0.55)
axes[2].set_title('Valor esperado acumulado por vendedor (R$)')
axes[2].set_xlabel('R$')
axes[2].set_xlim(0, resumo['w_total'].max() * 1.32)
axes[2].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x/1000:.0f}k'))
for i, v in enumerate(resumo['w_total']):
    axes[2].text(v + 300, i, f'R${v:,.0f}', va='center', fontsize=8)

for ax in axes:
    ax.yaxis.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('art_fig4_vendedores.png')
plt.savefig('art_fig4_vendedores.pdf')
plt.close()
print('fig4 OK')

# ─────────────────────────────────────────────────────────────────────────────
# FIG 5 - Comparacao dos algoritmos (3 paineis)
# ─────────────────────────────────────────────────────────────────────────────
algos  = list(res.keys())
cores  = [C1, C2, C4]

fig, axes = plt.subplots(1, 3, figsize=(13, 4.8))
n_leads = 37

# 5a - leads alocados
vals = [r['leads'] for r in res.values()]
bars = axes[0].bar(algos, vals, color=cores, edgecolor='white', width=0.52)
axes[0].axhline(n_leads, color='black', ls='--', lw=1, alpha=0.6,
                label=f'Total disponivel (n={n_leads})')
axes[0].set_ylim(0, n_leads + 9)
axes[0].set_title('Leads alocados por algoritmo')
axes[0].set_ylabel('Numero de leads')
axes[0].legend(loc='upper right')
for bar, v in zip(bars, vals):
    axes[0].text(bar.get_x() + bar.get_width() / 2, v + 0.5,
                 str(v), ha='center', fontsize=11, fontweight='bold', color=CDGRAY)

# 5b - valor esperado
vals_w = [r['valor'] for r in res.values()]
bars = axes[1].bar(algos, vals_w, color=cores, edgecolor='white', width=0.52)
axes[1].axhline(valor_max, color='black', ls='--', lw=1, alpha=0.6,
                label='Valor maximo possivel')
axes[1].set_ylim(0, valor_max * 1.22)
axes[1].set_title('Valor esperado total capturado (R$)')
axes[1].set_ylabel('R$')
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x:,.0f}'))
axes[1].legend(loc='upper right')
for bar, v in zip(bars, vals_w):
    axes[1].text(bar.get_x() + bar.get_width() / 2, v + 400,
                 f'R${v:,.0f}', ha='center', fontsize=8.5,
                 fontweight='bold', color=CDGRAY)

# 5c - utilizacao capacidade
vals_util = [r['tempo'] / cap_total * 100 for r in res.values()]
bars = axes[2].bar(algos, vals_util, color=cores, edgecolor='white', width=0.52)
axes[2].axhline(100, color='black', ls='--', lw=1, alpha=0.6,
                label='Capacidade maxima')
axes[2].set_ylim(0, 118)
axes[2].set_title('Utilizacao da capacidade total (%)')
axes[2].set_ylabel('%')
axes[2].legend(loc='upper right')
for bar, v in zip(bars, vals_util):
    axes[2].text(bar.get_x() + bar.get_width() / 2, v + 1.5,
                 f'{v:.1f}%', ha='center', fontsize=10,
                 fontweight='bold', color=CDGRAY)

for ax in axes:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='x', labelsize=8.5)

plt.tight_layout()
plt.savefig('art_fig5_comparacao.png')
plt.savefig('art_fig5_comparacao.pdf')
plt.close()
print('fig5 OK')

# ─────────────────────────────────────────────────────────────────────────────
# FIG 6 - Distribuicao do valor esperado nos leads ativos
# ─────────────────────────────────────────────────────────────────────────────
bins = np.linspace(0, max(w_vec) + 500, 17)
prioritarios = w_vec[w_vec >= 500]
baixo_valor  = w_vec[w_vec < 500]

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.hist(prioritarios, bins=bins, color=C2, alpha=0.88, edgecolor='white',
        label=f'w $\geq$ R$500 (n={len(prioritarios)}, leads prioritarios)')
ax.hist(baixo_valor,  bins=bins, color=C4, alpha=0.88, edgecolor='white',
        label=f'w < R$500 (n={len(baixo_valor)}, leads de baixo valor)')
ax.set_xlabel('Valor esperado $w = p_c \\times V_t$ (R$)', labelpad=5)
ax.set_ylabel('Frequencia')
ax.set_title('Distribuicao do valor esperado nos 37 leads ativos')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R${x:,.0f}'))
ax.legend(loc='upper right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('art_fig6_dist_valor.png')
plt.savefig('art_fig6_dist_valor.pdf')
plt.close()
print('fig6 OK')

# ─────────────────────────────────────────────────────────────────────────────
# FIG 7 - Capacidade por vendedor no Matching Bipartido
# ─────────────────────────────────────────────────────────────────────────────
vend_nomes = ['Marcela Belo', 'Maria Paula', 'Talita Guedes']
cap_usada  = [19.5, 19.5, 20.0]
vnames_fmt = ['Marcela', 'Maria Paula', 'Talita']

fig, ax = plt.subplots(figsize=(8, 4.2))
bar_colors = [C2 if v > 0 else C4 for v in cap_usada]
bars = ax.bar(vnames_fmt, cap_usada, color=bar_colors, edgecolor='white', width=0.52)
ax.axhline(CAPACIDADE_H, color='black', lw=1.2, ls='--', alpha=0.7,
           label=f'Capacidade maxima ({CAPACIDADE_H:.0f}h/vendedor)')
ax.set_ylabel('Horas utilizadas')
ax.set_title('Utilizacao de capacidade por vendedor -- Matching Bipartido')
ax.set_ylim(0, CAPACIDADE_H * 1.28)
ax.legend(loc='upper right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
for bar, v in zip(bars, cap_usada):
    label = f'{v:.1f}h' if v > 0 else '0h\n(ocioso)'
    ypos  = v + 0.4 if v > 0 else 0.5
    ax.text(bar.get_x() + bar.get_width() / 2, ypos,
            label, ha='center', fontsize=9.5, fontweight='bold', color=CDGRAY)

plt.tight_layout()
plt.savefig('art_fig7_cap_vendedor.png')
plt.savefig('art_fig7_cap_vendedor.pdf')
plt.close()
print('fig7 OK')

print('\nTodas as figuras v2 geradas.')
