"""
Tabla 4 - Tipos de Ataque
Columnas: ATTACKTYPE1_TXT, SUCCESS, SUICIDE
Gráfico: Torta - Distribución de tipos de ataque principales
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

cols = ['ATTACKTYPE1_TXT', 'SUCCESS', 'SUICIDE']
df = pd.read_excel('../GTD_5156.xlsx', usecols=cols)
df['ATTACKTYPE1_TXT'] = df['ATTACKTYPE1_TXT'].fillna('Desconocido')

conteo = df['ATTACKTYPE1_TXT'].value_counts()
top_n = 7
top = conteo.head(top_n)
otros = conteo.iloc[top_n:].sum()
if otros > 0:
    top['Otros'] = otros

colores = [
    '#E53935','#FB8C00','#FDD835','#43A047','#00ACC1',
    '#1E88E5','#8E24AA','#D81B60'
]

fig, axes = plt.subplots(1, 2, figsize=(16, 8))
fig.suptitle('Tabla 4 — Tipos de Ataque Terrorista', fontsize=15, fontweight='bold')

# Torta principal
wedges, texts, autotexts = axes[0].pie(
    top.values,
    labels=None,
    autopct=lambda p: f'{p:.1f}%' if p > 2 else '',
    colors=colores[:len(top)],
    startangle=140,
    pctdistance=0.75,
    wedgeprops=dict(linewidth=1.5, edgecolor='white'),
    explode=[0.03]*len(top)
)
for at in autotexts:
    at.set_fontsize(9)
    at.set_fontweight('bold')

axes[0].legend(
    wedges, [f'{k}\n({v:,})' for k, v in top.items()],
    title='Tipo de ataque',
    loc='lower left',
    fontsize=8,
    bbox_to_anchor=(-0.15, -0.05)
)
axes[0].set_title(f'Distribución de {len(df):,} incidentes', fontsize=12)

# Barras de éxito y suicida por tipo (top 7)

plt.tight_layout()
plt.savefig('tabla4_ataque_torta.png', dpi=150, bbox_inches='tight')
plt.show()
print("Guardado: tabla4_ataque_torta.png")
