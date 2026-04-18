"""
Tabla 7 - Perpetradores
Columnas: GNAME, INDIVIDUAL, NPERPS, NPERPCAP, CLAIMED
Gráfico: Boxplot - Distribución de perpetradores en los grupos con más ataques
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

cols = ['GNAME', 'INDIVIDUAL', 'NPERPS', 'NPERPCAP', 'CLAIMED', 'GUNCERTAIN1']
df = pd.read_excel('../GTD_5156.xlsx', usecols=cols)
df['GNAME'] = df['GNAME'].fillna('Desconocido')

# Top 10 grupos por número de ataques (excluyendo Unknown)
grupos_top = (df[df['GNAME'] != 'Unknown Terrorist Group(s)']
              ['GNAME'].value_counts().head(10).index.tolist())

df_f = df[df['GNAME'].isin(grupos_top)].copy()
df_f = df_f[df_f['NPERPS'] > 0]  # solo filas con dato de perpetradores

# Preparar datos para boxplot
data_boxes = [df_f[df_f['GNAME'] == g]['NPERPS'].dropna().values for g in grupos_top]

# Estadísticas de atribución
claimed_pct = {}
for g in grupos_top:
    sub = df[df['GNAME'] == g]
    pct = (sub['CLAIMED'] == 1).sum() / len(sub) * 100
    claimed_pct[g] = round(pct, 1)

fig, axes = plt.subplots(1, 2, figsize=(18, 8))
fig.suptitle('Tabla 7 — Análisis de Grupos Perpetradores', fontsize=15, fontweight='bold')

# Boxplot de perpetradores
colores = plt.cm.tab10(np.linspace(0, 1, len(grupos_top)))
bp = axes[0].boxplot(
    data_boxes,
    vert=False,
    patch_artist=True,
    showfliers=True,
    flierprops=dict(marker='o', markersize=3, alpha=0.4),
    medianprops=dict(color='white', linewidth=2),
    whiskerprops=dict(linewidth=1.5),
    capprops=dict(linewidth=1.5),
)
for patch, color in zip(bp['boxes'], colores):
    patch.set_facecolor(color)
    patch.set_alpha(0.75)

etiquetas = [g[:35] for g in grupos_top]
axes[0].set_yticklabels(etiquetas, fontsize=9)
axes[0].set_xlabel('Número de perpetradores reportados', fontsize=11)
axes[0].set_title('Distribución de perpetradores\npor grupo (top 10)', fontsize=12)
axes[0].set_xlim(0, None)
axes[0].grid(axis='x', linestyle='--', alpha=0.4)

# Barras de % ataques atribuidos + total de ataques
counts_total = [df[df['GNAME'] == g].shape[0] for g in grupos_top]
pcts = [claimed_pct[g] for g in grupos_top]

y = np.arange(len(grupos_top))
axes[1].barh(y, pcts, color=colores, alpha=0.8, edgecolor='white')
for i, (p, n) in enumerate(zip(pcts, counts_total)):
    axes[1].text(p + 0.5, i, f'{p}% ({n} ataques)', va='center', fontsize=9)

axes[1].set_yticks(y)
axes[1].set_yticklabels(etiquetas, fontsize=9)
axes[1].set_xlabel('% ataques con atribución reclamada', fontsize=11)
axes[1].set_title('Tasa de atribución por grupo', fontsize=12)
axes[1].set_xlim(0, 115)
axes[1].grid(axis='x', linestyle='--', alpha=0.4)

plt.tight_layout()
plt.savefig('tabla7_perpetradores_boxplot.png', dpi=150, bbox_inches='tight')
plt.show()
print("Guardado: tabla7_perpetradores_boxplot.png")
