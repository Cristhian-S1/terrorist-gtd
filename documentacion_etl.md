# Documentación ETL - Data Warehouse GTD

## 1. Resumen

Proyecto de BI para la Universidad de Tarapacá. Se construye un data warehouse ROLAP en Oracle a partir del subset de Sudamérica de la Global Terrorism Database (GTD), con ~5.165 eventos terroristas.

## 2. Arquitectura

Esquema en estrella:

- **Tabla de hechos:** `FACT_GTD_EVENT`
- **Dimensiones (13):** `dim_ataque`, `dim_detalle`, `dim_tiempo`, `dim_lugar`, `dim_espec_lugar`, `dim_arma`, `dim_objetivos`, `dim_gperp`, `dim_bt_grupo`, `dim_mcr`, `dim_perpetradores`, `dim_impacto`, `dim_detalles_a`

`dim_lugar` es la única dimensión con **SCD Tipo 2** (`VALID_FROM`, `VALID_TO`, `VERSION`). El resto son SCD Tipo 1.

## 3. Flujo ETL

Orden de ejecución:

1. **DDL:** `databases/create_tables.sql`
2. **Carga fuente:** `carga_bigtables.hpl` (Excel → tabla `GTD`)
3. **Dimensiones:** pipelines en paralelo
4. **Tiempo:** `databases/dim_tiempo.sql` (PL/SQL, 1994-2021)
5. **Hechos:** `fact_gtd_event_fix.hpl`
6. **Post-ETL:** `databases/post_etl_constraints.sql` (PKs, FKs, bitmap indexes)
7. **Verificación:** `databases/verification_queries.sql`

## 4. Workflow

Archivo: `/home/cristhian/Downloads/gtd.hwf`

Orquesta todo el proceso:

- Ejecuta `carga_bigtables.hpl`.
- Lanza las dimensiones independientes en paralelo.
- Ejecuta la cadena GPERP en secuencia (`dim_gperp_staging` → `dim_bt_grupo_staging` → `dim_gperp_denorm` → `dim_gperp_final`).
- Espera a que terminen todas en un `DUMMY` "Dimensions loaded".
- Ejecuta `dim_tiempo.sql`, `fact_gtd_event_fix.hpl`, `post_etl_constraints.sql` y `verification_queries.sql`.

## 5. Tabla de hechos `FACT_GTD_EVENT`

Contiene una fila por evento del GTD.

**Medidas principales:** coordenadas, número de perpetradores/capturados, muertos/heridos, valor de propiedades, rehenes, rescates, etc.

**Claves foráneas:** apunta a todas las dimensiones. `FK_FECHA_RES` es nullable (solo incidentes extendidos).

La carga se hace con un único `Table Input` que hace joins contra todas las dimensiones, reduciendo el número de conexiones abiertas a Oracle y evitando el error `ORA-12170`.

## 6. Dimensiones

| Dimensión | Pipeline | Descripción breve |
|---|---|---|
| `dim_lugar` | `dim_lugar.hpl` | País, región, provincia, ciudad. **SCD Tipo 2**. |
| `dim_espec_lugar` | `dim_espec_lugar.hpl` | `VICINITY` y `SPECIFICITY` del lugar. |
| `dim_ataque` | `dim_ataque.hpl` | Tipo de ataque (`ATTACKTYPE1-3`), éxito, suicida. |
| `dim_detalle` | `dim_detalle.hpl` | Criterios GTD (`CRIT1-3`), duda terrorismo, alternativa. |
| `dim_detalles_a` | `dim_detalles_a.hpl` | Detalles adicionales: `INT_LOG`, `INT_MISC`, `INT_ANY`. |
| `dim_arma` | `dim_armas.hpl` | Armas usadas (`UNION ALL` de WEAPTYPE1-4). |
| `dim_objetivos` | `dim_objetivos.hpl` | Objetivos (`UNION ALL` de TARGTYPE1-3). |
| `dim_impacto` | `dim_impacto.hpl` | Daños, secuestros, resultado de rehenes. |
| `dim_mcr` | `dim_mcr.hpl` | Modo de reclamo (`CLAIMMODE`). |
| `dim_perpetradores` | `dim_perpretadores.hpl` | Nombre y subnombre de grupos (`UNION ALL` GNAME1-3). |
| `dim_gperp` | Cadena GPERP | Grupo de perpetradores con hasta 3 perpetradores asociados (bridge). |

## 7. Consideraciones importantes

- **Conexión Hop:** usar siempre `GTD_DB` (Oracle `146.83.109.225:1521/inuta`, usuario `in2026_dici3`).
- **Tipos de datos:** las SK deben ser `NUMBER(38,0)` para evitar errores de cast entre `Long` y `BigDecimal` de Hop.
- **Duplicados en dimensiones:** `dim_ataque` y `dim_detalle` fueron corregidas para agrupar por su clave natural. Si aún hay duplicados heredados, truncar y recargar.
- **SCD Tipo 2:** solo `dim_lugar`. Usa `Dimension Lookup/Update`; las demás usan `Combination Lookup/Update`.
- **Multivaluados:** armas, objetivos y perpetradores se normalizan con `UNION ALL`.
- **GPERP:** requiere 4 pipelines en orden estricto (staging → bridge → denorm → final).
- **post_etl_constraints.sql:** idempotente. Valida duplicados y NULLs antes de crear PKs. Ejecutar solo después de cargar `FACT_GTD_EVENT`.
- **Workflow:** usa rutas absolutas. Si se mueve el archivo o los pipelines, actualizar las rutas en las acciones.
