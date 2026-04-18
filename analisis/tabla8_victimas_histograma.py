"""
Tabla 8 - Víctimas y Daños
Columnas: NKILL, NWOUND, NKILLTER, PROPVALUE, ISHOSTKID, NHOSTKID, RANSOM
Gráfico: Histograma - Distribución de víctimas mortales y heridos + análisis de daños
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings('ignore')

cols = ['NKILL', 'NWOUND', 'NKILLTER', 'PROPVALUE', 'ISHOSTKID', 'NHOSTKID', 'RANSOM', 'PROPERTY']
df = pd.read_excel('../GTD_5156.xlsx', usecols=cols)

nkill = df['NKILL'].dropna()
nkill = nkill[nkill >= 0]
nwound = df['NWOUND'].dropna()
nwound = nwound[nwound >= 0]

# Limitar a percentil 99 para legibilidad
cap_kill = nkill.quantile(0.99)
cap_wound = nwound.quantile(0.99)

fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.35)
fig.suptitle('Tabla 8 — Víctimas, Daños Materiales y Secuestros', fontsize=15, fontweight='bold')

# Panel 1: Histograma de muertos
ax1 = fig.add_subplot(gs[0, 0])
datos_kill = nkill[nkill <= cap_kill]
ax1.hist(datos_kill, bins=40, color='#E53935', alpha=0.85, edgecolor='white', linewidth=0.5)
ax1.axvline(datos_kill.median(), color='black', linewidth=1.5, linestyle='--', label=f'Mediana: {datos_kill.median():.1f}')
ax1.axvline(datos_kill.mean(), color='orange', linewidth=1.5, linestyle='-', label=f'Media: {datos_kill.mean():.1f}')
ax1.set_xlabel('Muertes por incidente', fontsize=10)
ax1.set_ylabel('Frecuencia', fontsize=10)
ax1.set_title(f'Distribución de muertos (≤p99={cap_kill:.0f})\nn={len(datos_kill):,}', fontsize=11)
ax1.legend(fontsize=9)
ax1.grid(axis='y', linestyle='--', alpha=0.4)

# Panel 2: Histograma de heridos
ax2 = fig.add_subplot(gs[0, 1])
datos_wound = nwound[nwound <= cap_wound]
ax2.hist(datos_wound, bins=40, color='#FB8C00', alpha=0.85, edgecolor='white', linewidth=0.5)
ax2.axvline(datos_wound.median(), color='black', linewidth=1.5, linestyle='--', label=f'Mediana: {datos_wound.median():.1f}')
ax2.axvline(datos_wound.mean(), color='red', linewidth=1.5, linestyle='-', label=f'Media: {datos_wound.mean():.1f}')
ax2.set_xlabel('Heridos por incidente', fontsize=10)
ax2.set_ylabel('Frecuencia', fontsize=10)
ax2.set_title(f'Distribución de heridos (≤p99={cap_wound:.0f})\nn={len(datos_wound):,}', fontsize=11)
ax2.legend(fontsize=9)
ax2.grid(axis='y', linestyle='--', alpha=0.4)

# Panel 3: Daños a la propiedad (torta)
ax3 = fig.add_subplot(gs[1, 0])
prop_counts = df['PROPERTY'].value_counts()
labels_prop = {1: 'Sí, hubo daños', 0: 'Sin daños', -9: 'Desconocido', 2: 'Dudoso'}
prop_labels = [labels_prop.get(k, str(k)) for k in prop_counts.index]
colores_prop = ['#E53935', '#43A047', '#9E9E9E', '#FDD835']
ax3.pie(prop_counts.values, labels=prop_labels, autopct='%1.1f%%',
        colors=colores_prop[:len(prop_counts)],
        startangle=90, wedgeprops=dict(linewidth=1.5, edgecolor='white'))
ax3.set_title('Daños a la propiedad\n(campo PROPERTY)', fontsize=11)

# Panel 4: Secuestros y rescate
ax4 = fig.add_subplot(gs[1, 1])
hostkid_si = (df['ISHOSTKID'] == 1).sum()
hostkid_no = (df['ISHOSTKID'] == 0).sum()
ransom_si = df[df['ISHOSTKID'] == 1]['RANSOM'].apply(lambda x: 1 if x == 1 else 0).sum()

stats_labels = ['Total incidentes\nc/secuestro', 'Incidentes\nsin secuestro', 'Secuestros con\npetición de rescate']
stats_vals = [hostkid_si, hostkid_no, ransom_si]
bar_colors = ['#E53935', '#43A047', '#FDD835']
bars = ax4.bar(stats_labels, stats_vals, color=bar_colors, edgecolor='white', linewidth=0.7)
for bar in bars:
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
             f'{bar.get_height():,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax4.set_ylabel('Número de incidentes', fontsize=10)
ax4.set_title('Secuestros y rescates\n(campos ISHOSTKID, RANSOM)', fontsize=11)
ax4.grid(axis='y', linestyle='--', alpha=0.4)

plt.savefig('tabla8_victimas_histograma.png', dpi=150, bbox_inches='tight')
plt.show()
print("Guardado: tabla8_victimas_histograma.png")
