"""
Tabla 2 - Criterios de Terrorismo
Columnas: CRIT1, CRIT2, CRIT3, DOUBTTERR, MULTIPLE, SUCCESS, SUICIDE
Gráfico: Barras agrupadas - % de incidentes que cumplen cada criterio
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

cols = ['CRIT1', 'CRIT2', 'CRIT3', 'DOUBTTERR', 'MULTIPLE', 'SUCCESS', 'SUICIDE']
df = pd.read_excel('../GTD_5156.xlsx', usecols=cols)

total = len(df)

etiquetas = {
    'CRIT1': 'Meta\npolítica/econ/rel.',
    'CRIT2': 'Intención de\ncoaccionar',
    'CRIT3': 'Fuera del contexto\nde guerra legítima',
    'DOUBTTERR': 'Duda si es\nterrorismo',
    'MULTIPLE': 'Parte de serie\nmúltiple',
    'SUCCESS': 'Ataque\nexitoso',
    'SUICIDE': 'Ataque\nsuicida',
}

pct_si = {}
pct_no = {}
for col in cols:
    serie = df[col].fillna(-1)
    pct_si[col] = round((serie == 1).sum() / total * 100, 1)
    pct_no[col] = round((serie == 0).sum() / total * 100, 1)

nombres = [etiquetas[c] for c in cols]
vals_si = [pct_si[c] for c in cols]
vals_no = [pct_no[c] for c in cols]

x = np.arange(len(cols))
ancho = 0.38

fig, ax = plt.subplots(figsize=(14, 7))
fig.suptitle('Tabla 2 — Criterios de Clasificación Terrorista', fontsize=15, fontweight='bold')

bars_si = ax.bar(x - ancho/2, vals_si, ancho, label='Sí (1)', color='#E53935', edgecolor='white', linewidth=0.5)
bars_no = ax.bar(x + ancho/2, vals_no, ancho, label='No (0)', color='#43A047', edgecolor='white', linewidth=0.5)

for bar in bars_si:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.8, f'{h}%', ha='center', va='bottom', fontsize=9, color='#E53935', fontweight='bold')
for bar in bars_no:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.8, f'{h}%', ha='center', va='bottom', fontsize=9, color='#43A047', fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(nombres, fontsize=10)
ax.set_ylabel('Porcentaje de incidentes (%)', fontsize=11)
ax.set_ylim(0, 115)
ax.legend(fontsize=11)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_title(f'Distribución de criterios sobre {total} incidentes', fontsize=12)

plt.tight_layout()
plt.savefig('tabla2_criterios_barras.png', dpi=150, bbox_inches='tight')
plt.show()
print("Guardado: tabla2_criterios_barras.png")
