# Resumen: Proceso ETL en Data Warehouses

> Basado en el módulo *Implementación DW* del Dr. Ricardo Valdivia, complementado con la experiencia del proyecto GTD.

---

## 1. ¿Qué es ETL?

**ETL** = **E**xtracción + **T**ransformación + **C**arga.

Es el proceso que mueve datos desde sistemas fuente, los limpia, les da formato y los carga en un Data Warehouse (DW) para análisis.

### ¿Por qué es tan importante?

- Consume alrededor del **80 % del tiempo** de un proyecto DW.
- Es el proceso más subestimado, pero determina la calidad de los análisis.
- Si el ETL falla, los reportes mienten.

### Ejemplo GTD

Nuestra fuente es un archivo Excel (`GTD 5156.xlsx`) con ~5.165 eventos terroristas en Sudamérica. El ETL:

1. **Extrae** el Excel.
2. **Transforma** los códigos numéricos en textos, normaliza armas/objetivos/perpetradores multivaluados y genera claves subrogadas.
3. **Carga** 13 dimensiones y la tabla de hechos `FACT_GTD_EVENT` en Oracle.

---

## 2. Diseño físico del DW (ROLAP en Oracle)

### Tablas de dimensión

- **Clave primaria** sobre la clave subrogada (surrogate key). Crea un índice único implícito.
- **Clave de unicidad** sobre la clave operacional/natural. En SCD Tipo 2 se incluye `VALID_FROM` en la clave.
- Normalmente no se crean índices adicionales.

```sql
-- PK subrogada (confía en ella el optimizador)
ALTER TABLE dim_ataque
ADD CONSTRAINT dim_ataque_pk PRIMARY KEY(ataque_sk) RELY;

-- UK sobre clave natural
ALTER TABLE dim_ataque
ADD CONSTRAINT dim_ataque_uk UNIQUE(attacktype1, success, suicide);
```

### Tabla de hechos

- **FKs** con `RELY DISABLE NOVALIDATE` durante la carga (no frenan inserciones masivas).
- Después del ETL se habilitan con `ENABLE NOVALIDATE`.
- **Bitmap indexes** sobre cada FK para acelerar filtros OLAP.
- Usualmente **no tiene PK**.

```sql
-- FK durante carga
ALTER TABLE fact_gtd_event
ADD CONSTRAINT fk_fact_ataque FOREIGN KEY(fk_ataque)
REFERENCES dim_ataque(ataque_sk) RELY DISABLE NOVALIDATE;

-- Habilitar después del ETL
ALTER TABLE fact_gtd_event
MODIFY CONSTRAINT fk_fact_ataque ENABLE NOVALIDATE;

-- Índice bitmap
CREATE BITMAP INDEX fact_fk_ataque_bm
ON fact_gtd_event(fk_ataque);
```

### Tipos de índice

| Índice | Uso típico | Ejemplo en GTD |
|---|---|---|
| **B-tree** | Búsquedas por rango, unicidad | PKs y UKs de dimensiones |
| **Bitmap** | Atributos de baja cardinalidad, consultas OLAP | Índices sobre `FK_FECHA_INI`, `FK_LUGAR`, etc. |

---

## 3. Fases del proceso ETL

1. **Diseño:** diagramar origen → destino, elegir herramienta, definir transformaciones y secuencia.
2. **Carga inicial:** primer poblamiento completo del DW.
3. **Carga incremental:** actualizar solo lo que cambió desde la última carga.

### Ejemplo GTD

Nuestro proyecto hace una **carga inicial** completa. No hay carga incremental configurada, aunque el workflow (`gtd.hwf`) podría adaptarse para ejecutarse periódicamente.

---

## 4. Área de Staging

Es una zona intermedia de almacenamiento temporal, sin acceso a usuarios, donde se preparan los datos antes de cargarlos al DW.

**Sirve para:**

- Consolidar datos de varias fuentes.
- Estandarizar formatos.
- Mejorar rendimiento.
- Respaldar datos intermedios.
- Detectar cambios (delta).

### Ejemplo GTD

- `GTD` es la tabla de staging principal que genera `carga_bigtables.hpl` desde el Excel.
- `dim_gperp_staging.hpl` genera `DIM_GPERP_STG` y `DIM_BT_GRUPO_STG` antes de la carga final a `DIM_GPERP`.

---

## 5. Pipelines y Workflows en Apache Hop

| Concepto | Qué hace | Ejemplo GTD |
|---|---|---|
| **Pipeline** | Trabaja los datos: lee, transforma, escribe. Las transformaciones internas corren en paralelo. | `dim_ataque.hpl`, `fact_gtd_event_fix.hpl` |
| **Workflow** | Orquesta tareas secuencialmente: ejecuta pipelines, corre SQL, verifica archivos. | `gtd.hwf` |

### Ejemplo de pipeline: `dim_ataque.hpl`

```
Table Input (SELECT DISTINCT ... FROM GTD)
    ↓
If Null (reemplaza nulos por -9 / 'Desconocido')
    ↓
Combination Lookup/Update (inserta/busca SK por clave natural)
```

### Ejemplo de workflow: `gtd.hwf`

```
Start → carga_bigtables → [dimensiones en paralelo] → Dimensions loaded
                                              ↓
                              dim_tiempo.sql → fact_gtd_event_fix
                                              ↓
                    post_etl_constraints.sql → verification_queries.sql → Success
```

---

## 6. Dimensiones SCD Tipo 1 vs. Tipo 2

### SCD Tipo 1: sobrescribe el cambio

- No guarda historia.
- Si un atributo cambia, se actualiza la fila existente.
- En Hop: `Combination Lookup/Update` o `Insert/Update`.

**Ejemplo GTD:**

`dim_ataque` usa SCD Tipo 1. Si dos filas tienen el mismo `(attacktype1, success, suicide)`, solo debe existir una. Corregimos la pipeline para agrupar por esa clave natural y evitar duplicados.

### SCD Tipo 2: guarda historia con versiones

- Crea una nueva fila cuando cambian atributos relevantes.
- Usa campos `VALID_FROM`, `VALID_TO`, `VERSION`.
- En Hop: `Dimension Lookup/Update`.

**Ejemplo GTD:**

`dim_lugar` es la única dimensión SCD Tipo 2. Si cambia el nombre de una ciudad, se inserta una nueva versión y la anterior queda con `VALID_TO` antiguo.

```sql
-- Clave natural de dim_lugar considera validez temporal
(country, region, provstate, city, valid_from)
```

---

## 7. Construcción de dimensiones

### Pasos generales

1. Extraer datos de la fuente.
2. Seleccionar/limpiar atributos.
3. Eliminar duplicados (clave natural).
4. Generar claves subrogadas.
5. Cargar en la tabla de dimensión.

### Ejemplo GTD: `dim_arma`

El GTD tiene hasta 4 armas por evento (`WEAPTYPE1..4`). La pipeline hace `UNION All` de las 4 columnas para normalizarlos:

```sql
SELECT DISTINCT
    COALESCE(WEAPTYPE, -1) AS WEAPTYPE,
    COALESCE(WEAPTYPE_TXT, 'Not applicable') AS WEAPTYPE_TXT,
    COALESCE(WEAPSUBTYPE, -1) AS WEAPSUBTYPE,
    COALESCE(WEAPSUBTYPE_TXT, 'Not applicable') AS WEAPSUBTYPE_TXT
FROM (
    SELECT WEAPTYPE1, WEAPTYPE1_TXT, WEAPSUBTYPE1, WEAPSUBTYPE1_TXT FROM GTD
    UNION ALL
    SELECT WEAPTYPE2, WEAPTYPE2_TXT, WEAPSUBTYPE2, WEAPSUBTYPE2_TXT FROM GTD
    UNION ALL
    SELECT WEAPTYPE3, WEAPTYPE3_TXT, WEAPSUBTYPE3, WEAPSUBTYPE3_TXT FROM GTD
    UNION ALL
    SELECT WEAPTYPE4, WEAPTYPE4_TXT, WEAPSUBTYPE4, WEAPSUBTYPE4_TXT FROM GTD
)
```

Lo mismo aplica a `dim_objetivos` (`TARGTYPE1..3`) y `dim_perpretadores` (`GNAME1..3`).

---

## 8. Construcción de la tabla de hechos

### Pasos generales

1. Leer los datos de hechos (medidas + claves operacionales).
2. Buscar las claves subrogadas de cada dimensión.
3. Cargar en `FACT_*`.

### Estrategia de lookups

**Opción A: Database Lookup (uno por dimensión)**

Fácil de armar, pero abre muchas conexiones. En GTD causó `ORA-12170` (demasiadas conexiones simultáneas a Oracle).

**Opción B: SQL Joins (recomendada)**

Un solo `Table Input` con joins contra todas las dimensiones reduce conexiones y es más rápida.

```sql
SELECT
    g.EVENT_ID,
    g.NKILL,
    g.NWOUND,
    d.DETALLE_SK,
    t.TIEMPO_SK,
    l.LUGAR_SK,
    a.ATAQUE_SK
FROM GTD g
JOIN DIM_DETALLE d ON ...
JOIN DIM_TIEMPO t ON ...
JOIN DIM_LUGAR l ON ...
JOIN DIM_ATAQUE a ON ...
```

En GTD usamos esta segunda opción en `fact_gtd_event_fix.hpl`.

---

## 9. Carga inicial vs. incremental

| Aspecto | Carga inicial | Carga incremental |
|---|---|---|
| **Volumen** | Grande (histórico completo) | Pequeño (solo cambios) |
| **Cuándo** | Primera vez | Periódicamente |
| **Dimensiones** | Se cargan completas | Solo cambios detectados |
| **Hechos** | Se cargan todos | Solo nuevos/modificados |
| **Orden** | Dimensiones primero, hechos después | Igual: dimensiones antes que hechos |

### Ejemplo GTD

Actualmente es carga inicial. Si se quisiera incremental, se podría:

- Comparar `EVENT_ID` de la fuente contra los ya cargados.
- Procesar solo eventos nuevos.
- Actualizar primero las dimensiones y luego insertar los nuevos hechos.

---

## 10. Extracción: full vs. incremental

| Extracción | Descripción | Ejemplo |
|---|---|---|
| **Full** | Trae todos los datos. No requiere rastrear cambios. | Cargar todo el Excel GTD cada vez. |
| **Incremental** | Trae solo cambios desde la última extracción. | Usar `eventid` nuevos o timestamps. |

### Métodos para detectar cambios (delta)

- **Timestamps:** columnas `created_at` / `updated_at`.
- **Partitioning:** procesar solo particiones nuevas.
- **Triggers:** registrar cambios en tabla auxiliar.
- **Change Data Capture (CDC):** captura cambios en tiempo real.
- **External tables / DBLinks / GoldenGate:** otras formas de extraer datos.

### Ejemplo GTD

Usamos **extracción full** desde Excel. No hay CDC ni particiones porque la fuente es un archivo plano.

---

## 11. Transformaciones usuales

- Conversión de tipos de datos.
- Normalización/denormalización.
- Reemplazo de claves operacionales por claves subrogadas.
- Limpieza de nulos.
- División de columnas multivaluadas (`UNPIVOT`).
- Cálculo de campos derivados.

### Ejemplo GTD: limpieza de nulos

En varias dimensiones usamos `COALESCE` y el transform `If Null`:

```sql
COALESCE(ATTACKTYPE1, -9)        AS ATTACKTYPE1,
COALESCE(ATTACKTYPE1_TXT, 'Desconocido') AS ATTACKTYPE1_TXT
```

---

## 12. Buenas prácticas de transformación

1. **No usar valores "especiales"** como `-1` o `0` en dimensiones si se puede evitar; pueden confundir en análisis.
2. **Crear registros de dimensión para "desconocido" y "no aplica"** en lugar de dejar NULLs.
3. **Mantener calidad de datos:** marcar hechos anormales si es necesario.
4. **Evitar duplicados** en las claves naturales antes de cargar dimensiones.

### Ejemplo GTD

- Para atributos no aplicables usamos `-1` y textos como `'Not applicable'`.
- Para desconocidos usamos `-9` y `'Desconocido'`.
- Corregimos `dim_ataque` y `dim_detalle` para evitar duplicados por clave natural.

---

## 13. Carga: consideraciones finales

- **Cargas offline vs. online:** offline permite mantener índices deshabilitados durante la carga.
- **Desactivar constraints durante la carga** para mejorar rendimiento; habilitarlas después.
- **Usar bitmap indexes** en la tabla de hechos, pero crearlos después de la carga.
- **Particionar tablas grandes** si el volumen lo justifica.

### Ejemplo GTD

- Durante la carga las FKs están `DISABLE NOVALIDATE`.
- Después de cargar `FACT_GTD_EVENT` se ejecuta `post_etl_constraints.sql`, que:
  1. Crea PKs en dimensiones.
  2. Crea FKs en la tabla de hechos.
  3. Crea bitmap indexes.
  4. Habilita las FKs con `ENABLE NOVALIDATE`.

---

## Checklist para un ETL exitoso

- [ ] Definir esquema en estrella (dimensiones y hechos).
- [ ] Crear tablas con tipos adecuados (`NUMBER(38,0)` para SKs en GTD).
- [ ] Construir pipelines de dimensiones (SCD Tipo 1 o 2 según corresponda).
- [ ] Verificar que no hay duplicados en claves naturales.
- [ ] Construir pipeline de hechos resolviendo todas las FKs.
- [ ] Orquestar todo en un workflow.
- [ ] Ejecutar scripts post-ETL (constraints e índices).
- [ ] Validar con consultas de verificación.
