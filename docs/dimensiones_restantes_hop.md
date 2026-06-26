# Guía de creación de dimensiones restantes en Apache Hop 2.18.1

> Basado en `create_tables.sql` y `informe/proceso_etl.md`. Todas las dimensiones usan `Combination Lookup/Update` (SCD Type 1) salvo `DIM_LUGAR` que ya fue implementada como SCD Type 2.

## Recomendaciones generales

1. **Conexión:** usar `inuta-gtd` en todos los transforms.
2. **Tipo de clave subrogada:** si obtienes errores de tipo `Long` vs `BigDecimal`, altera las columnas SK a `NUMBER(38,0)`:
   ```sql
   ALTER TABLE DIM_DETALLE MODIFY DETALLE_SK NUMBER(38,0);
   ```
3. **Manejo de nulos:** reemplazar nulos numéricos por `-1` y textos por `'Not applicable'` / `'Desconocido'`.
4. **Normalización de nombres de columna:** Hop pasa los nombres a mayúsculas por defecto. Usa los nombres tal como aparecen en el DDL (mayúsculas) en las configuraciones.
5. **Secuencias:** para SCD Type 1 con `Combination Lookup/Update` puedes dejar que Hop genere la clave automáticamente (`<max(table)> + 1`). Si prefieres secuencias, créalas previamente.

---

## 1. DIM_DETALLE (SCD Type 1)

### DDL relevante
```sql
CREATE TABLE DIM_DETALLE (
    DETALLE_SK NUMBER,
    CRIT1 NUMBER,
    CRIT2 NUMBER,
    CRIT3 NUMBER,
    DOUBTTERR NUMBER,
    ALTERNATIVE NUMBER,
    ALTERNATIVE_TXT VARCHAR2(255),
    MULTIPLE NUMBER,
    CRIT1_TXT VARCHAR2(255),
    CRIT2_TXT VARCHAR2(255),
    CRIT3_TXT VARCHAR2(255),
    DOUBTTERR_TXT VARCHAR2(64),
    MULTIPLE_TXT VARCHAR2(32)
);
```

### Pipeline
```
Table Input (dim_detalle)
    ↓
If Null
    ↓
Combination Lookup/Update → DIM_DETALLE
```

### SQL Table Input
```sql
SELECT DISTINCT
    CRIT1, CRIT2, CRIT3, DOUBTTERR, ALTERNATIVE, ALTERNATIVE_TXT, MULTIPLE,
    'POLITICAL, ECONOMIC, RELIGIOUS, OR SOCIAL GOAL' AS CRIT1_TXT,
    'INTENTION TO COERCE, INTIMIDATE OR PUBLICIZE TO LARGER AUDIENCE(S)' AS CRIT2_TXT,
    'OUTSIDE INTERNATIONAL HUMANITARIAN LAW' AS CRIT3_TXT,
    CASE DOUBTTERR WHEN 0 THEN 'NO' WHEN 1 THEN 'YES' ELSE 'Desconocido' END AS DOUBTTERR_TXT,
    CASE MULTIPLE WHEN 0 THEN 'NO' WHEN 1 THEN 'YES' ELSE 'DESCONOCIDO' END AS MULTIPLE_TXT
FROM GTD
```

### Configuración Combination Lookup/Update
- **Target table:** `DIM_DETALLE`
- **Technical key field:** `DETALLE_SK`
- **Fields to compare** (pestaña `Keys`):
  - `CRIT1`, `CRIT2`, `CRIT3`, `DOUBTTERR`, `ALTERNATIVE`, `ALTERNATIVE_TXT`, `MULTIPLE`
  - `CRIT1_TXT`, `CRIT2_TXT`, `CRIT3_TXT`, `DOUBTTERR_TXT`, `MULTIPLE_TXT`

> Si usas secuencia, crear `CREATE SEQUENCE DIM_DETALLE_SEQ START WITH 1 INCREMENT BY 1;` y seleccionarla en el transform. Si no, deja que Hop use `max(DETALLE_SK)+1`.

---

## 2. DIM_ESPEC_LUGAR (SCD Type 1)

### DDL relevante
```sql
CREATE TABLE DIM_ESPEC_LUGAR (
    SPEC_LUGAR_SK NUMBER,
    VICINITY NUMBER,
    VICINITY_TXT VARCHAR2(255),
    SPECIFY NUMBER,
    SPECIFY_TXT VARCHAR2(255)
);
```

### Pipeline
```
Table Input
    ↓
If Null
    ↓
Combination Lookup/Update → DIM_ESPEC_LUGAR
```

### SQL Table Input

> El SQL en `informe/proceso_etl.md` no incluye `VICINITY_TXT`, pero el DDL y el ejemplo `spec_lugar.csv` sí lo requieren. Se agrega la derivación de `VICINITY_TXT` y los textos largos de `SPECIFY_TXT` tal como aparecen en el CSV de ejemplo.

```sql
SELECT DISTINCT
    COALESCE(VICINITY, -9) AS VICINITY,
    CASE COALESCE(VICINITY, -9)
        WHEN 0 THEN 'NO'
        WHEN 1 THEN 'YES'
        ELSE 'Unknown'
    END AS VICINITY_TXT,
    COALESCE(SPECIFICITY, -1) AS SPECIFY,
    CASE
        WHEN SPECIFICITY IS NULL OR SPECIFICITY = -1 THEN 'Not applicable'
        WHEN SPECIFICITY = 1 THEN 'event occurred in city/village/town and lat/long is for that location'
        WHEN SPECIFICITY = 2 THEN 'event occurred in city/village/town and no lat/long could be found, so coordinates are for centroid of smallest subnational administrative region identified'
        WHEN SPECIFICITY = 3 THEN 'event did not occur in city/village/town, so coordinates are for centroid of smallest subnational administrative region identified'
        WHEN SPECIFICITY = 4 THEN 'no 2nd order or smaller region could be identified, so coordinates are for center of 1st order administrative region'
        WHEN SPECIFICITY = 5 THEN 'no 1st order administrative region could be identified for the location of the attack, so latitude and longitude are unknown'
        ELSE 'unknown'
    END AS SPECIFY_TXT
FROM GTD
ORDER BY VICINITY, SPECIFY
```

### Configuración Combination Lookup/Update
- **Target table:** `DIM_ESPEC_LUGAR`
- **Technical key field:** `SPEC_LUGAR_SK`
- **Fields to compare:** `VICINITY`, `VICINITY_TXT`, `SPECIFY`, `SPECIFY_TXT`

---

## 3. DIM_DETALLES_A (SCD Type 1)

### DDL relevante
```sql
CREATE TABLE DIM_DETALLES_A (
    DETALLES_A_SK NUMBER,
    INT_LOG NUMBER,
    INT_LOG_TEXT VARCHAR2(255),
    INT_MISC NUMBER,
    INT_MISC_TEXT VARCHAR2(255),
    INT_ANY NUMBER,
    INT_ANY_TEXT VARCHAR2(255)
);
```

### Pipeline
```
Table Input
    ↓
If Null
    ↓
Combination Lookup/Update → DIM_DETALLES_A
```

### SQL Table Input
```sql
SELECT DISTINCT
    COALESCE(INT_LOG, -9) AS INT_LOG,
    CASE COALESCE(INT_LOG, -9) WHEN 1 THEN 'Si' WHEN 0 THEN 'No' WHEN -9 THEN 'Desconocido' ELSE 'Desconocido' END AS INT_LOG_TEXT,
    COALESCE(INT_MISC, -9) AS INT_MISC,
    CASE COALESCE(INT_MISC, -9) WHEN 1 THEN 'Si' WHEN 0 THEN 'No' WHEN -9 THEN 'Desconocido' ELSE 'Desconocido' END AS INT_MISC_TEXT,
    COALESCE(INT_ANY, -9) AS INT_ANY,
    CASE COALESCE(INT_ANY, -9) WHEN 1 THEN 'Si' WHEN 0 THEN 'No' WHEN -9 THEN 'Desconocido' ELSE 'Desconocido' END AS INT_ANY_TEXT
FROM GTD
```

### Configuración Combination Lookup/Update
- **Target table:** `DIM_DETALLES_A`
- **Technical key field:** `DETALLES_A_SK`
- **Fields to compare:** `INT_LOG`, `INT_LOG_TEXT`, `INT_MISC`, `INT_MISC_TEXT`, `INT_ANY`, `INT_ANY_TEXT`

---

## 4. DIM_ARMA (SCD Type 1 + UNPIVOT)

### DDL relevante
```sql
CREATE TABLE DIM_ARMA (
    ARMAS_SK NUMBER,
    WEAPTYPE NUMBER,
    WEAPTYPE_TXT VARCHAR2(255),
    WEAPSUBTYPE NUMBER,
    WEAPSUBTYPE_TXT VARCHAR2(255)
);
```

### Pipeline (staging opcional)
```
Table Input (UNPIVOT)
    ↓
If Null
    ↓
Sort rows
    ↓
Unique rows
    ↓
Combination Lookup/Update → DIM_ARMA
```

### SQL Table Input (UNPIVOT con UNION ALL)
```sql
SELECT DISTINCT
    COALESCE(WEAPTYPE, -1) AS WEAPTYPE,
    COALESCE(WEAPTYPE_TXT, 'Not applicable') AS WEAPTYPE_TXT,
    COALESCE(WEAPSUBTYPE, -1) AS WEAPSUBTYPE,
    COALESCE(WEAPSUBTYPE_TXT, 'Not applicable') AS WEAPSUBTYPE_TXT
FROM (
    SELECT WEAPTYPE1 AS WEAPTYPE, WEAPTYPE1_TXT AS WEAPTYPE_TXT, WEAPSUBTYPE1 AS WEAPSUBTYPE, WEAPSUBTYPE1_TXT AS WEAPSUBTYPE_TXT FROM GTD
    UNION ALL
    SELECT WEAPTYPE2, WEAPTYPE2_TXT, WEAPSUBTYPE2, WEAPSUBTYPE2_TXT FROM GTD
    UNION ALL
    SELECT WEAPTYPE3, WEAPTYPE3_TXT, WEAPSUBTYPE3, WEAPSUBTYPE3_TXT FROM GTD
    UNION ALL
    SELECT WEAPTYPE4, WEAPTYPE4_TXT, WEAPSUBTYPE4, WEAPSUBTYPE4_TXT FROM GTD
)
```

### If Null
- `WEAPTYPE` → `-1`
- `WEAPSUBTYPE` → `-1`
- `WEAPTYPE_TXT` → `Not applicable`
- `WEAPSUBTYPE_TXT` → `Not applicable`

### Sort rows + Unique rows
Ordenar y eliminar duplicados por: `WEAPTYPE`, `WEAPTYPE_TXT`, `WEAPSUBTYPE`, `WEAPSUBTYPE_TXT`.

### Configuración Combination Lookup/Update
- **Target table:** `DIM_ARMA`
- **Technical key field:** `ARMAS_SK`
- **Fields to compare:** `WEAPTYPE`, `WEAPTYPE_TXT`, `WEAPSUBTYPE`, `WEAPSUBTYPE_TXT`

---

## 5. DIM_ATAQUE (SCD Type 1)

### DDL relevante
```sql
CREATE TABLE DIM_ATAQUE (
    ATAQUE_SK NUMBER,
    ATTACKTYPE1 NUMBER,
    ATTACKTYPE1_TXT VARCHAR2(255),
    ATTACKTYPE2 NUMBER,
    ATTACKTYPE2_TXT VARCHAR2(255),
    ATTACKTYPE3 NUMBER,
    ATTACKTYPE3_TXT VARCHAR2(255),
    SUCCESS NUMBER,
    SUICIDE NUMBER
);
```

### Pipeline
```
Table Input
    ↓
If Null
    ↓
Combination Lookup/Update → DIM_ATAQUE
```

### SQL Table Input
```sql
SELECT DISTINCT
    COALESCE(ATTACKTYPE1, -9) AS ATTACKTYPE1,
    COALESCE(ATTACKTYPE1_TXT, 'Desconocido') AS ATTACKTYPE1_TXT,
    COALESCE(ATTACKTYPE2, -1) AS ATTACKTYPE2,
    COALESCE(ATTACKTYPE2_TXT, 'Not applicable') AS ATTACKTYPE2_TXT,
    COALESCE(ATTACKTYPE3, -1) AS ATTACKTYPE3,
    COALESCE(ATTACKTYPE3_TXT, 'Not applicable') AS ATTACKTYPE3_TXT,
    COALESCE(SUCCESS, -9) AS SUCCESS,
    COALESCE(SUICIDE, -9) AS SUICIDE
FROM GTD
```

### Configuración Combination Lookup/Update
- **Target table:** `DIM_ATAQUE`
- **Technical key field:** `ATAQUE_SK`
- **Fields to compare:** `ATTACKTYPE1`, `ATTACKTYPE1_TXT`, `ATTACKTYPE2`, `ATTACKTYPE2_TXT`, `ATTACKTYPE3`, `ATTACKTYPE3_TXT`, `SUCCESS`, `SUICIDE`

---

## 6. DIM_PERPETRADORES (SCD Type 1 + UNPIVOT)

### DDL relevante
```sql
CREATE TABLE DIM_PERPETRADORES (
    PERP_SK NUMBER,
    GNAME VARCHAR2(512),
    GSUBNAME VARCHAR2(512)
);
```

### Pipeline
```
Table Input (UNPIVOT)
    ↓
Filter rows (GNAME IS NOT NULL)
    ↓
If Null
    ↓
Sort rows
    ↓
Unique rows
    ↓
Combination Lookup/Update → DIM_PERPETRADORES
```

### SQL Table Input (UNPIVOT con UNION ALL)
```sql
SELECT DISTINCT
    GNAME,
    COALESCE(GSUBNAME, 'Not specified') AS GSUBNAME
FROM (
    SELECT GNAME, GSUBNAME FROM GTD WHERE GNAME IS NOT NULL
    UNION ALL
    SELECT GNAME2, GSUBNAME2 FROM GTD WHERE GNAME2 IS NOT NULL
    UNION ALL
    SELECT GNAME3, GSUBNAME3 FROM GTD WHERE GNAME3 IS NOT NULL
)
```

### If Null
- `GNAME` → `Unknown`
- `GSUBNAME` → `Not specified`

### Configuración Combination Lookup/Update
- **Target table:** `DIM_PERPETRADORES`
- **Technical key field:** `PERP_SK`
- **Fields to compare:** `GNAME`, `GSUBNAME`

---

## 7. DIM_MCR (SCD Type 1)

### DDL relevante
```sql
CREATE TABLE DIM_MCR (
    MCR_SK NUMBER,
    CLAIMMODE NUMBER,
    CLAIMMODE_TXT VARCHAR2(255)
);
```

### Pipeline
```
Table Input
    ↓
If Null
    ↓
Combination Lookup/Update → DIM_MCR
```

### SQL Table Input
```sql
SELECT DISTINCT
    COALESCE(CLAIMMODE, -1) AS CLAIMMODE,
    COALESCE(CLAIMMODE_TXT, 'Not specified') AS CLAIMMODE_TXT
FROM GTD
ORDER BY CLAIMMODE
```

### Configuración Combination Lookup/Update
- **Target table:** `DIM_MCR`
- **Technical key field:** `MCR_SK`
- **Fields to compare:** `CLAIMMODE`, `CLAIMMODE_TXT`

---

## 8. DIM_OBJETIVOS (SCD Type 1 + UNPIVOT)

### DDL relevante
```sql
CREATE TABLE DIM_OBJETIVOS (
    OBJETIVO_SK NUMBER,
    TARGTYPE NUMBER,
    TARGTYPE_TXT VARCHAR2(255),
    TARGSUBTYPE NUMBER,
    TARGSUBTYPE_TXT VARCHAR2(255),
    CORP VARCHAR2(255),
    TARGET VARCHAR2(512),
    NATLTY NUMBER,
    NATLTY_TXT VARCHAR2(255)
);
```

### Pipeline
```
Table Input (UNPIVOT)
    ↓
If Null
    ↓
Sort rows
    ↓
Unique rows
    ↓
Combination Lookup/Update → DIM_OBJETIVOS
```

### SQL Table Input (UNPIVOT con UNION ALL)
```sql
SELECT DISTINCT
    COALESCE(TARGTYPE, -1) AS TARGTYPE,
    COALESCE(TARGTYPE_TXT, 'Not applicable') AS TARGTYPE_TXT,
    COALESCE(TARGSUBTYPE, -1) AS TARGSUBTYPE,
    COALESCE(TARGSUBTYPE_TXT, 'Not applicable') AS TARGSUBTYPE_TXT,
    COALESCE(CORP, 'Not applicable') AS CORP,
    COALESCE(TARGET, 'Not applicable') AS TARGET,
    COALESCE(NATLTY, -1) AS NATLTY,
    COALESCE(NATLTY_TXT, 'Not applicable') AS NATLTY_TXT
FROM (
    SELECT TARGTYPE1 AS TARGTYPE, TARGTYPE1_TXT AS TARGTYPE_TXT, TARGSUBTYPE1 AS TARGSUBTYPE, TARGSUBTYPE1_TXT AS TARGSUBTYPE_TXT, CORP1 AS CORP, TARGET1 AS TARGET, NATLTY1 AS NATLTY, NATLTY1_TXT AS NATLTY_TXT FROM GTD
    UNION ALL
    SELECT TARGTYPE2, TARGTYPE2_TXT, TARGSUBTYPE2, TARGSUBTYPE2_TXT, CORP2, TARGET2, NATLTY2, NATLTY2_TXT FROM GTD
    UNION ALL
    SELECT TARGTYPE3, TARGTYPE3_TXT, TARGSUBTYPE3, TARGSUBTYPE3_TXT, CORP3, TARGET3, NATLTY3, NATLTY3_TXT FROM GTD
)
```

### If Null
- Campos numéricos → `-1`
- Campos de texto → `'Not applicable'`

### Configuración Combination Lookup/Update
- **Target table:** `DIM_OBJETIVOS`
- **Technical key field:** `OBJETIVO_SK`
- **Fields to compare:** `TARGTYPE`, `TARGTYPE_TXT`, `TARGSUBTYPE`, `TARGSUBTYPE_TXT`, `CORP`, `TARGET`, `NATLTY`, `NATLTY_TXT`

---

## 9. DIM_IMPACTO (SCD Type 1)

### DDL relevante
```sql
CREATE TABLE DIM_IMPACTO (
    IMPACTO_SK NUMBER,
    PROPERTY NUMBER,
    PROPEXTENT NUMBER,
    PROPEXTENT_TXT VARCHAR2(255),
    ISHOSTKID NUMBER,
    HOSTKIDOUTCOME NUMBER,
    HOSTKIDOUTCOME_TXT VARCHAR2(255)
);
```

### Pipeline
```
Table Input
    ↓
If Null
    ↓
Combination Lookup/Update → DIM_IMPACTO
```

### SQL Table Input
```sql
SELECT DISTINCT
    COALESCE(PROPERTY, -1) AS PROPERTY,
    COALESCE(PROPEXTENT, -1) AS PROPEXTENT,
    COALESCE(PROPEXTENT_TXT, 'Not applicable') AS PROPEXTENT_TXT,
    COALESCE(ISHOSTKID, -1) AS ISHOSTKID,
    COALESCE(HOSTKIDOUTCOME, -1) AS HOSTKIDOUTCOME,
    COALESCE(HOSTKIDOUTCOME_TXT, 'Not applicable') AS HOSTKIDOUTCOME_TXT
FROM GTD
```

### Configuración Combination Lookup/Update
- **Target table:** `DIM_IMPACTO`
- **Technical key field:** `IMPACTO_SK`
- **Fields to compare:** `PROPERTY`, `PROPEXTENT`, `PROPEXTENT_TXT`, `ISHOSTKID`, `HOSTKIDOUTCOME`, `HOSTKIDOUTCOME_TXT`

---

## 10. DIM_GPERP + DIM_BT_GRUPO (Complejo)

### DDL relevante
```sql
CREATE TABLE DIM_GPERP (
    GRUPO_SK NUMBER,
    COMPCLAIM NUMBER,
    MOTIVE CLOB
);

CREATE TABLE DIM_BT_GRUPO (
    GRUPO_FK NUMBER,
    PERP_FK NUMBER,
    GUNCERTAIN NUMBER,
    CLAIMED NUMBER,
    MCR_FK NUMBER
);
```

### Visión general
Se requieren **tres pipelines**:
1. **BT_GRUPO_STG:** extrae combinaciones únicas de grupos, les asigna `GRUPO` (secuencia), y resuelve `PERP_FK` y `MCR_FK` con `Database Lookup`.
2. **DENORMALIZED_DATA_STG:** convierte las filas de `DIM_BT_GRUPO_STG` a formato desnormalizado (perp1, perp2, perp3) con `row_number()`.
3. **Carga final:** verifica unicidad y carga `DIM_GPERP` y `DIM_BT_GRUPO`.

### Pipeline 1: DIM_GPERP_STG + DIM_BT_GRUPO_STG

```
Table Input (combinaciones de grupos)
    ↓
Unique rows (hashset)
    ↓
Add sequence → GRUPO
    ↓
Table Output → DIM_GPERP_STG
    ↓
Database Lookup PERP_FK (DIM_PERPETRADORES)
    ↓
Database Lookup MCR_FK (DIM_MCR)
    ↓
Table Output → DIM_BT_GRUPO_STG
```

### Pipeline 2: Desnormalización

```sql
WITH perpetradores_enumerados AS (
    SELECT grupo, perp_fk, mcr_fk, claimed, guncertain,
           row_number() OVER (PARTITION BY grupo ORDER BY perp_fk) AS nro_perp
    FROM dim_bt_grupo_stg
)
SELECT
    g.grupo, g.compclaim, to_char(g.motive) AS motive,
    max(CASE WHEN bg.nro_perp = 1 THEN bg.perp_fk END) AS perp_fk1,
    max(CASE WHEN bg.nro_perp = 1 THEN bg.mcr_fk END) AS mcr_fk1,
    max(CASE WHEN bg.nro_perp = 1 THEN bg.claimed END) AS claimed1,
    max(CASE WHEN bg.nro_perp = 1 THEN bg.guncertain END) AS guncertain1,
    max(CASE WHEN bg.nro_perp = 2 THEN bg.perp_fk END) AS perp_fk2,
    max(CASE WHEN bg.nro_perp = 2 THEN bg.mcr_fk END) AS mcr_fk2,
    max(CASE WHEN bg.nro_perp = 2 THEN bg.claimed END) AS claimed2,
    max(CASE WHEN bg.nro_perp = 2 THEN bg.guncertain END) AS guncertain2,
    max(CASE WHEN bg.nro_perp = 3 THEN bg.perp_fk END) AS perp_fk3,
    max(CASE WHEN bg.nro_perp = 3 THEN bg.mcr_fk END) AS mcr_fk3,
    max(CASE WHEN bg.nro_perp = 3 THEN bg.claimed END) AS claimed3,
    max(CASE WHEN bg.nro_perp = 3 THEN bg.guncertain END) AS guncertain3
FROM dim_gperp_stg g
JOIN perpetradores_enumerados bg ON g.grupo = bg.grupo
GROUP BY g.grupo, g.compclaim, to_char(g.motive)
ORDER BY g.grupo
```

### Pipeline 3: Verificación de unicidad

```sql
SELECT dds.*
FROM denormalized_data_stg dds
LEFT JOIN denormalized_data_dim ddd ON (dds.checksum = ddd.checksum)
WHERE ddd.checksum IS NULL
```

> Esta dimensión es la más compleja. Se recomienda implementarla después de tener `DIM_PERPETRADORES` y `DIM_MCR` cargadas.

---

## Notas sobre Combination Lookup/Update en Hop 2.18.1

- **Target table:** nombre de la tabla destino.
- **Technical key field:** columna SK (ej. `DETALLE_SK`).
- **Fields to compare:** en la pestaña `Keys`, coloca todos los campos que definen unicidad de la dimensión.
- Si usas secuencia, actívala en la sección correspondiente; si no, Hop calculará `max(SK)+1`.
- No es necesario incluir el SK en `Keys` ni en los campos de comparación.

---

## Orden recomendado de implementación

1. `DIM_DETALLE`
2. `DIM_ESPEC_LUGAR`
3. `DIM_DETALLES_A`
4. `DIM_ATAQUE`
5. `DIM_MCR`
6. `DIM_ARMA`
7. `DIM_PERPETRADORES`
8. `DIM_OBJETIVOS`
9. `DIM_IMPACTO`
10. `DIM_GPERP` + `DIM_BT_GRUPO`
11. `FACT_GTD_EVENT`
