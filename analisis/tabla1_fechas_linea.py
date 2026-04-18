"""
Tabla 1 - Identificadores y Fechas
Columnas: IYEAR, IMONTH, EXTENDED
Gráfico: Línea - Evolución de ataques por año y ataques extendidos
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import warnings
warnings.filterwarnings('ignore')

df = pd.read_excel('../GTD_5156.xlsx', usecols=['IYEAR', 'IMONTH', 'IDAY', 'EXTENDED'])

# Ataques por año (total)
ataques_anio = df.groupby('IYEAR').size().reset_index(name='total')

# Ataques extendidos por año
extendidos = df[df['EXTENDED'] == 1].groupby('IYEAR').size().reset_index(name='extendidos')

merged = ataques_anio.merge(extendidos, on='IYEAR', how='left').fillna(0)
merged['pct_extendidos'] = (merged['extendidos'] / merged['total'] * 100).round(2)

fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
fig.suptitle('Tabla 1 — Evolución Temporal de Ataques Terroristas', fontsize=15, fontweight='bold', y=0.98)

# Panel superior: total de ataques por año
axes[0].plot(merged['IYEAR'], merged['total'], color='#2196F3', linewidth=2.2, marker='o', markersize=5)
axes[0].fill_between(merged['IYEAR'], merged['total'], alpha=0.15, color='#2196F3')
axes[0].set_ylabel('Total de ataques', fontsize=11)
axes[0].set_title('Total de incidentes por año', fontsize=12)
axes[0].yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
axes[0].grid(axis='y', linestyle='--', alpha=0.5)
for x, y in zip(merged['IYEAR'], merged['total']):
    axes[0].annotate(str(y), (x, y), textcoords='offset points', xytext=(0, 6), ha='center', fontsize=8)

# Panel inferior: % ataques extendidos
axes[1].plot(merged['IYEAR'], merged['pct_extendidos'], color='#E91E63', linewidth=2.2, marker='s', markersize=5)
axes[1].fill_between(merged['IYEAR'], merged['pct_extendidos'], alpha=0.15, color='#E91E63')
axes[1].set_ylabel('% ataques extendidos', fontsize=11)
axes[1].set_xlabel('Año', fontsize=11)
axes[1].set_title('Porcentaje de ataques extendidos (>24h) por año', fontsize=12)
axes[1].grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('tabla1_fechas_linea.png', dpi=150, bbox_inches='tight')
plt.show()
print("Guardado: tabla1_fechas_linea.png")
