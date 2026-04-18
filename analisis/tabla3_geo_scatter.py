"""
Tabla 3 - Geolocalización
Columnas: LATITUDE, LONGITUDE, REGION_TXT, COUNTRY_TXT
Gráfico: Scatter - Distribución geográfica de ataques coloreada por región
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

cols = ['LATITUDE', 'LONGITUDE', 'REGION_TXT', 'COUNTRY_TXT', 'IYEAR']
df = pd.read_excel('../GTD_5156.xlsx', usecols=cols)
df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])
df = df[(df['LATITUDE'].between(-90, 90)) & (df['LONGITUDE'].between(-180, 180))]

regiones = df['REGION_TXT'].unique()
colores_lista = [
    '#E53935','#FB8C00','#FDD835','#43A047','#00ACC1',
    '#1E88E5','#8E24AA','#D81B60','#6D4C41','#546E7A','#00897B','#FFB300'
]
color_map = {r: colores_lista[i % len(colores_lista)] for i, r in enumerate(sorted(regiones))}
df['color'] = df['REGION_TXT'].map(color_map)

fig, ax = plt.subplots(figsize=(16, 9))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

for region in sorted(regiones):
    sub = df[df['REGION_TXT'] == region]
    ax.scatter(sub['LONGITUDE'], sub['LATITUDE'],
               c=color_map[region], s=12, alpha=0.65, linewidths=0,
               label=region)

ax.set_xlim(-185, 185)
ax.set_ylim(-65, 85)
ax.set_xlabel('Longitud', fontsize=11, color='white')
ax.set_ylabel('Latitud', fontsize=11, color='white')
ax.set_title('Tabla 3 — Distribución Geográfica de Ataques Terroristas por Región', fontsize=14, fontweight='bold', color='white', pad=12)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_edgecolor('#444466')

ax.axhline(0, color='#444466', linewidth=0.7, linestyle='--')
ax.axvline(0, color='#444466', linewidth=0.7, linestyle='--')

legend = ax.legend(title='Región', fontsize=8, title_fontsize=9,
                   loc='lower left', framealpha=0.3,
                   labelcolor='white', facecolor='#1a1a2e', edgecolor='#444466')
legend.get_title().set_color('white')

ax.text(0.99, 0.01, f'n = {len(df):,} ataques', transform=ax.transAxes,
        ha='right', va='bottom', fontsize=9, color='#aaaacc')

plt.tight_layout()
plt.savefig('tabla3_geo_scatter.png', dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.show()
print("Guardado: tabla3_geo_scatter.png")
