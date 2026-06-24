# GTD ETL Fase II — Design Doc

**Date:** 2025-06-24
**Project:** Inteligencia de Negocios — Universidad de Tarapacá
**Phase:** Fase II — Implementación Datawarehouse y Proceso ETL
**Source:** `databases/GTD 5156.xlsx` (~5,165 registros, filtrado Sudamérica)
**Target:** Oracle ROLAP (`146.83.109.225:1521`, SID `INUTA`, user `in2026_dici3`)
**ETL Tool:** Apache Hop

## 1. Architecture Overview

ETL staged approach following `informe/proceso_etl.md` blueprint. Data flows:

```
Excel → GTD Bigtable (Oracle) → Staging Tables → Dimension Tables → Fact Table
```

**14 Pipelines + 1 Workflow** orchestrating them in dependency order.

## 2. Target Schema (Star Schema)

Fact table: `FACT_GTD_EVENT`
Dimensions: `DIM_TIEMPO`, `DIM_LUGAR`, `DIM_ESPEC_LUGAR`, `DIM_DETALLE`, `DIM_DETALLES_A`, `DIM_ARMA`, `DIM_ATAQUE`, `DIM_PERPETRADORES`, `DIM_MCR`, `DIM_GPERP`, `DIM_BT_GRUPO`, `DIM_OBJETIVOS`, `DIM_IMPACTO`

## 3. Database Objects

### 3.1 Bigtable

```sql
CREATE TABLE GTD (
    eventid NUMBER,
    iyear NUMBER,
    imonth NUMBER,
    iday NUMBER,
    -- ... all columns from source Excel
    -- approx 135 columns
);
```

### 3.2 Dimension Tables

| Dimension | Type | Surrogate Key Strategy |
|-----------|------|----------------------|
| DIM_TIEMPO | Static | `tiempo_sk = YYYYMMDD` (numeric) |
| DIM_LUGAR | SCD Type 2 | Sequence + versioning |
| DIM_DETALLE | SCD Type 1 | `detalle_sk NUMBER` |
| DIM_ESPEC_LUGAR | SCD Type 1 | `spec_lugar_sk GENERATED AS IDENTITY` |
| DIM_DETALLES_A | SCD Type 1 | `detalles_a_sk GENERATED AS IDENTITY` |
| DIM_ARMA | SCD Type 1 | `armas_sk GENERATED AS IDENTITY` |
| DIM_ATAQUE | SCD Type 1 | `ataque_sk GENERATED AS IDENTITY` |
| DIM_PERPETRADORES | SCD Type 1 | `perp_sk NUMBER` (rows+1) |
| DIM_MCR | SCD Type 1 | `mcr_sk NUMBER` (rows+1) |
| DIM_GPERP | SCD Type 1 | `grupo_sk NUMBER` |
| DIM_BT_GRUPO | SCD Type 1 | Composite FK |
| DIM_OBJETIVOS | SCD Type 1 | `objetivo_sk NUMBER` (rows+1) |
| DIM_IMPACTO | SCD Type 1 | `impacto_sk GENERATED AS IDENTITY` |

### 3.3 Fact Table

```sql
CREATE TABLE FACT_GTD_EVENT (
    -- FKs to all dimensions
    fk_tiempo_ini NUMBER NOT NULL,
    fk_lugar NUMBER NOT NULL,
    fk_espec_lugar NUMBER NOT NULL,
    fk_detalle NUMBER NOT NULL,
    fk_detalles_a NUMBER NOT NULL,
    fk_arma1 NUMBER,
    fk_arma2 NUMBER,
    fk_arma3 NUMBER,
    fk_arma4 NUMBER,
    fk_ataque NUMBER NOT NULL,
    fk_perpg NUMBER,          -- fk to DIM_GPERP
    fk_obj1 NUMBER NOT NULL,
    fk_obj2 NUMBER,
    fk_obj3 NUMBER,
    fk_impacto NUMBER NOT NULL,
    -- Measures
    nkill NUMBER,
    nwound NUMBER,
    nperps NUMBER,
    nhostkid NUMBER,
    nrelease NUMBER,
    -- Derived
    eventid NUMBER,
    extended NUMBER,
    -- ... additional columns
);
```

## 4. Pipeline Specifications

### Pipeline 0: CARGA BIGTABLE
```
Microsoft Excel Input → Table output (GTD)
```
- Source: `databases/GTD 5156.xlsx`
- Reads all rows, all columns
- Target: Oracle table `GTD`

### Pipeline 1: DIM_TIEMPO
- PL/SQL stored procedure generating dates 1970-01-01 to 2025-12-31
- `tiempo_sk = TO_NUMBER(TO_CHAR(date, 'YYYYMMDD'))`
- Columns: `tiempo_sk`, `iyear`, `imonth`, `iday`

### Pipeline 2: DIM_DETALLE (SCD Type 1)
```
Table Input → Dim Detalle Stg → Combination Lookup/Update → Dim_Detalle
```
- SQL with CASE expressions for text fields
- Key fields: crit1, crit2, crit3, doubtterr, alternative, alternative_txt, multiple
- Technical key: `detalle_sk`

### Pipeline 3: DIM_ESPEC_LUGAR (SCD Type 1)
```
Table Input → If Null → Stg → Combination Lookup/Update → Dim_Espec_Lugar
```
- NULL values → -9 (numeric), "Not specified" (text)
- Technical key: `spec_lugar_sk` (identity)

### Pipeline 4: DIM_DETALLES_A (SCD Type 1)
```
Table Input → Stg → Combination Lookup/Update → Dim_Detalles_A
```
- CASE: 1→Si, 0→No, -9→Desconocido
- Fields: int_log, int_misc, int_any + their text equivalents
- Technical key: `detalles_a_sk` (identity)

### Pipeline 5: DIM_ARMA (SCD Type 1)
```
4x Table Input (ARMA1..4) → Union → If Null → Sort → Unique → Stg → Combination L/U → Dim_Arma
```
- UNPIVOT: weaptype1-4_txt + weapsubtype1-4_txt → single columns
- NULL weapon rows filtered out
- Technical key: `armas_sk` (identity)

### Pipeline 6: DIM_ATAQUE (SCD Type 1)
```
Table Input → If Null → Stg → Combination Lookup/Update → Dim_Ataque
```
- NULL attacktype2/3 → -1, "Not applicable"
- Fields: attacktype1-3 + txt, success, suicide
- Technical key: `ataque_sk` (identity)

### Pipeline 7: DIM_PERPETRADORES (SCD Type 1)
```
Table Input (UNPIVOT) → Filter nulls → If Null → Sort → Unique → Stg → Combination L/U → Dim_Perpetradores
```
- UNPIVOT gname1-3, gsubname1-3
- NULL gname filtered
- Technical key: `perp_sk` (COUNT(*) + 1)

### Pipeline 8: DIM_MCR (SCD Type 1)
```
Table Input → Filter nulls → If Null → Stg → Combination L/U → Dim_MCR
```
- Simple distinct claimmode + claimmode_txt
- Technical key: `mcr_sk` (COUNT(*) + 1)

### Pipeline 9: DIM_OBJETIVOS (SCD Type 1)
```
3x Table Input (OBJ1..3) → Union → If Null → Sort → Unique → Stg → Combination L/U → Dim_Objetivos
```
- UNPIVOT: targtype1-3 + txt, targsubtype1-3 + txt, corp1-3, target1-3, natlty1-3 + txt
- Technical key: `objetivo_sk` (COUNT(*) + 1)

### Pipeline 10: DIM_IMPACTO (SCD Type 1)
```
Table Input → If Null → Stg → Combination Lookup/Update → Dim_Impacto
```
- NULL → -1 (numeric), "Not applicable" (text)
- Fields: property, propextent, ishostkid, hostkidoutcome
- Technical key: `impacto_sk` (identity)

### Pipeline 11: DIM_LUGAR (SCD Type 2)
```
Table Input → Get System Date → Dimension Lookup/Update → Dim_Lugar
```
- **SCD Type 2** with versioning fields: `valid_from`, `valid_to`, `version`
- Lookup key: country_txt (natural key)
- Changed fields monitored: country_txt, region_txt

### Pipeline 12: DIM_GPERP + DIM_BT_GRUPO (Complex, 3 sub-pipelines)

**Sub-pipeline 12a:** Extraction and primary staging
```
Table Input → Unique rows → Filter nulls → If Null → Lookup FKs → Staging (gperp_stg, bt_grupo_stg)
```

**Sub-pipeline 12b:** Denormalization
```
Table Input (CTE + PIVOT) → denormalized_data_stg
```
- CTE enumerates perpetrators per group (row_number)
- PIVOT to spread perpetrator columns horizontally (perp_fk1, mcr_fk1, claimed1, guncertain1, ...)

**Sub-pipeline 12c:** Final dimension loading
```
Table Input (checksum join) → dim_gperp + dim_bt_grupo (Combination L/U)
```
- Checksum-based uniqueness verification
- Only new combinations inserted

### Pipeline 13: FACT_GTD_EVENT
```
Table Input (GTD) → Database Lookup ×13 → Table Output (fact_gtd_event)
```
- Database Lookup per dimension FK (seeks surrogate key)
- 4 lookups for weapon FKs, 3 for target FKs
- Stream Lookup for group perpetrator FK

## 5. Post-ETL Constraints

```sql
-- RELY foreign keys (disable novalidate)
ALTER TABLE fact_gtd_event ADD CONSTRAINT fk_tiempo
  FOREIGN KEY(fk_tiempo_ini) REFERENCES dim_tiempo(tiempo_sk) RELY DISABLE NOVALIDATE;
-- ... (all FKs)

-- Bitmap indexes
CREATE BITMAP INDEX fact_fk_tiempo_bm ON fact_gtd_event(fk_tiempo_ini);
-- ... (all FKs)

-- Enable FKs after ETL
ALTER TABLE fact_gtd_event MODIFY CONSTRAINT fk_tiempo ENABLE NOVALIDATE;
```

## 6. Workflow Orchestration

```
Start → Check DB connections
  → CARGA BIGTABLE
  → DIM LUGAR
  → DIM DETALLE
  → DIM ESPEC LUGAR
  → STG DETALLES ADICIONALES → DIM DETALLES ADICIONALES
  → STG ARMAS → DIM ARMAS
  → STG ATAQUE → DIM ATAQUE
  → DIM PERP STG → DIM PERPETRADORES
  → STG MCR → DIM MCR
  → STG IMPACTO → DIM IMPACTO
  → STG OBJETIVOS → DIM OBJETIVOS
  → UNION DIMENSIONES PERP → DESNORMALIZACION GRUPOS → STG BT PERPETRADORES
  → FACT TABLE
  → Success
```

## 7. Testing Queries

Post-load verification queries (from informe):
- Ranking de años por cantidad de atentados
- Porcentaje de ataques suicidas por grupo
- Cantidad de ataques por región, país, ciudad
- Cantidad de ataques por grupo perpetrador y tipo de ataque

## 8. Carga Periódica

- Periodicidad: anual (GTD se actualiza anualmente)
- Solo DIM_LUGAR es SCD Tipo 2 → requiere manejo de versiones en cargas incrementales
- Resto de dimensiones SCD Tipo 1: Combination Lookup detecta cambios automáticamente
