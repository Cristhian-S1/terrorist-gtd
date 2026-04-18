#!/usr/bin/env bash
# Ejecuta los 9 análisis en secuencia usando el entorno virtual
PYTHON="../.venv/bin/python"
SCRIPTS=(
    "tabla1_fechas_linea.py"
    "tabla2_criterios_barras.py"
    "tabla3_geo_scatter.py"
    "tabla4_ataque_torta.py"
    "tabla5_armas_barras.py"
    "tabla6_objetivos_heatmap.py"
    "tabla7_perpetradores_boxplot.py"
    "tabla8_victimas_histograma.py"
    "tabla9_internacional_heatmap.py"
)

cd "$(dirname "$0")"
for script in "${SCRIPTS[@]}"; do
    echo ">>> Ejecutando $script ..."
    $PYTHON "$script"
    echo ""
done
echo "=== Todos los análisis completados ==="
