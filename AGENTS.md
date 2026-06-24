# AGENTS.md

## Project overview

University BI project (Universidad de Tarapacá) — data warehouse for the Global Terrorism Database (GTD). Organized in 4 phases (0–3) described in `fases.md`. Currently at Fase II (ETL implementation with Apache Hop → Oracle).

## Tech stack

- **Database:** Oracle ROLAP, either local Docker (`gvenzl/oracle-xe:21`) or remote (`146.83.109.225:1521`, SID `INUTA`). See `databases/` for connection details.
- **ETL:** Apache Hop (pipelines + workflows)
- **Analytics:** Pentaho, Apache Superset, or PowerBI Desktop
- **Source data:** `databases/GTD 5156.xlsx`
- **No build tools, no tests, no linters.** This is a documentation + SQL + Excel repository.

## Key files

| File | Purpose |
|------|---------|
| `fases.md` | Full project spec with phase requirements |
| `databases/scheme_2024.sql` | SQL select listing all DW tables (star schema) |
| `presentacion/presentacion.md` | Lecture slides: ROLAP design patterns, ETL with Hop, SCD types |
| `databases/account.txt` | Remote Oracle credentials |
| `databases/docker_oracle.txt` | Local Oracle Docker setup |
| `databases/GTD 5156.xlsx` | Source dataset |

## DW schema (star schema)

Fact table: `fact_gtd_event`. Dimensions: `dim_ataque`, `dim_detalle`, `dim_tiempo`, `dim_lugar`, `dim_espec_lugar`, `dim_arma`, `dim_objetivos`, `dim_gperp`, `dim_bt_grupo`, `dim_mcr`, `dim_perpetradores`, `dim_impacto`, `dim_detalles_a`.

## Conventions

- All names in Spanish (dimensions, tables, attributes, documentation)
- Dimension tables prefixed `dim_`, fact table prefixed `fact_`
- Oracle ROLAP patterns from `presentacion/presentacion.md`: rely-disable-novalidate FK constraints, bitmap indexes on FK columns, surrogate keys with sequences, SCD type 2 with versioning

## Branches

- `main` — current work (Fase II)
- `graphical-analysis` — separate analysis work
