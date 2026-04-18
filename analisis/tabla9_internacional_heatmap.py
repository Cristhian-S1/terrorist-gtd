"""
Tabla 9 - Información Adicional e Internacional
Columnas: INT_LOG, INT_IDEO, INT_MISC, INT_ANY, DBSOURCE, REGION_TXT
Gráfico: Heatmap - Dimensiones internacionales por región
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings('ignore')

cols = ['INT_LOG', 'INT_IDEO', 'INT_MISC', 'INT_ANY', 'DBSOURCE', 'REGION_TXT']
df = pd.read_excel('../GTD_5156.xlsx', usecols=cols)
df = df.dropna(subset=['REGION_TXT'])

int_cols = ['INT_LOG', 'INT_IDEO', 'INT_MISC', 'INT_ANY']
labels_int = {
    'INT_LOG': 'Logístico\nInternacional',
    'INT_IDEO': 'Ideológico\nInternacional',
    'INT_MISC': 'Miscelánea\nInternacional',
    'INT_ANY': 'Cualquier\nDimensión',
}

# Calcular % de incidentes con dimensión internacional (==1) por región
pivot = pd.DataFrame()
for col in int_cols:
    pct = df[df[col] == 1].groupby('REGION_TXT').size() / df.groupby('REGION_TXT').size() * 100
    pivot[labels_int[col]] = pct

pivot = pivot.fillna(0)
pivot = pivot.sort_values('Cualquier\nDimensión', ascending=False)

fig = plt.figure(figsize=(18, 12))
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.4)
fig.suptitle('Tabla 9 — Dimensiones Internacionales de Ataques Terroristas', fontsize=15, fontweight='bold')

# Heatmap principal
ax1 = fig.add_subplot(gs[:, 0])
im = ax1.imshow(pivot.values, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)
ax1.set_xticks(range(len(pivot.columns)))
ax1.set_xticklabels(pivot.columns, fontsize=10)
ax1.set_yticks(range(len(pivot.index)))
ax1.set_yticklabels(pivot.index, fontsize=9)
ax1.set_title('% de ataques con dimensión\ninternacional por región', fontsize=12)
plt.colorbar(im, ax=ax1, shrink=0.7, label='% incidentes')

for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        val = pivot.values[i, j]
        color = 'white' if val > 55 else 'black'
        ax1.text(j, i, f'{val:.1f}%', ha='center', va='center', fontsize=9, color=color, fontweight='bold')

# Panel superior derecho: totales por dimensión (barras)
ax2 = fig.add_subplot(gs[0, 1])
totales = {}
for col in int_cols:
    totales[labels_int[col].replace('\n', ' ')] = (df[col] == 1).sum()
bars = ax2.bar(list(totales.keys()), list(totales.values()),
               color=['#1E88E5', '#E53935', '#FB8C00', '#43A047'],
               edgecolor='white', linewidth=0.7)
for bar in bars:
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
             f'{bar.get_height():,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax2.set_ylabel('Número de incidentes', fontsize=10)
ax2.set_title('Total de incidentes\ncon dimensión internacional', fontsize=11)
ax2.tick_params(axis='x', labelsize=8)
ax2.grid(axis='y', linestyle='--', alpha=0.4)

# Panel inferior derecho: distribución por fuente (DBSOURCE)
ax3 = fig.add_subplot(gs[1, 1])
db_counts = df['DBSOURCE'].value_counts().head(8)
colores_db = plt.cm.Set2(np.linspace(0, 1, len(db_counts)))
ax3.barh(db_counts.index[::-1], db_counts.values[::-1], color=colores_db, edgecolor='white')
for i, (idx, val) in enumerate(zip(db_counts.index[::-1], db_counts.values[::-1])):
    ax3.text(val + 1, i, f'{val:,}', va='center', fontsize=9)
ax3.set_xlabel('Número de incidentes', fontsize=10)
ax3.set_title('Fuente de datos (DBSOURCE)\nTop 6', fontsize=11)
ax3.set_xlim(0, db_counts.max() * 1.18)
ax3.grid(axis='x', linestyle='--', alpha=0.4)

plt.savefig('tabla9_internacional_heatmap.png', dpi=150, bbox_inches='tight')
plt.show()
print("Guardado: tabla9_internacional_heatmap.png")
