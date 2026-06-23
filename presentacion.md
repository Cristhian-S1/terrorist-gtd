# Tecnologías para la Inteligencia de Negocios
## Módulo 3 — Implementación DW

**Dr. Ricardo Valdivia Pinto**
rvaldivi@academicos.uta.cl

Facultad de Ingeniería
Departamento de Ingeniería en Computación e Informática
Universidad de Tarapacá
Arica - Chile

*Inteligencia de Negocios '2023*

---

## Índice

1. Diseño Físico DW
2. Proceso ETL
3. Extracción
4. Transformación
5. Carga

---

## 1. Diseño Físico DW

### Implementación ROLAP - Oracle

**Tablas de Dimensión:**

- Cree una restricción de clave primaria sobre las claves subrogadas (crea un índice único).
- Cree una restricción de unicidad sobre las claves operacionales (creará un índice único). En el caso de una SCD tipo 2 hay que considerar la validez como parte de la clave (valid from).
- Usualmente no se requiere crear índices adicionales sobre las tablas de dimensión.

**Tabla de Hechos:**

- Cree una restricción para cada clave foránea (rely disable/enable) y un índice bitmap sobre cada una de ellas.
- Cree restricciones de no nulidad para cada clave foránea (usualmente las medidas también son no nulas).
- Usualmente no se requiere una restricción de clave primaria en la tabla de hechos.

### Implementación ROLAP — Modelo de datos (ejemplo SuperStore)

> **Diagrama:** modelo entidad-relación (esquema en estrella) implementado en Oracle (esquema `RVALDIVIA`), con las siguientes tablas y sus columnas principales:
>
> - **DIM_DATE** — `DATE_PK` (PK), `YEAR_NUMBER`, `MONTH_NUMBER`, `DAY_OF_YEAR_NUMBER`, `DAY_OF_MONTH_NUMBER`, `DAY_OF_WEEK_NUMBER`, `WEEK_OF_YEAR_NUMBER`, `DAY_NAME`, `MONTH_NAME`, `QUARTER_NUMBER`, `QUARTER_NAME`, `YEAR_QUARTER_NAME`, `WEEKEND_IND`, `DAYS_IN_MONTH_QTY`, `DAY_DESC`, `WEEK_SK`, entre otros.
> - **DIM_ORDERS** — `PK_ORDERS` (PK), `Order Code` (UK), `Order Priority`.
> - **DIM_CUSTOMERS** — `PK_CUSTOMERS` (PK), `VERSION`, `Customer Code` (UK), `Customer Name`, `PROVINCE`, `REGION`, `Customer Segment`, `DATE_FROM`, `DATE_TO` (clave técnica versionada, propia de una dimensión SCD tipo 2).
> - **DIM_PRODUCTS** — `PK_PRODUCTS` (PK), `VERSION`, `Product Code` (UK), `Product Category`, `Product Sub-Category`, `Product Name`, `Product Container`, `DATE_FROM`, `DATE_TO` (también versionada como SCD tipo 2).
> - **FACT_SUPERSTORE** (tabla de hechos) — `Order Quantity`, `SALES`, `DISCOUNT`, `PROFIT`, `Unit Price`, `Shipping Cost`, `Product Base Margin`, más las claves foráneas `FK_ORDERS`, `FK_CUSTOMERS`, `FK_PRODUCTS`, `FK_DATE`, relacionadas con cada una de las dimensiones anteriores.

### Restricciones de claves (DDL Oracle)

```sql
-- primary key rely
alter table dim_products
add constraint dim_products_pk
primary key(pk_products) rely

-- foreign key rely
alter table fact_superstore
add constraint fact_superstore_dim_products_fk
foreign key(fk_products)
references dim_products(pk_products)
rely disable novalidate

-- posterior al proceso etl
alter table fact_superstore
modify constraint fact_superstore_dim_products_fk
enable novalidate
```

### Índices

- **Índices B-trees:** opción por defecto, útil para verificar unicidad o búsqueda por rango, ideal para ambientes OLTP.
- **Índices Bitmap:** ocupan poco espacio, preferibles para atributos con baja cardinalidad, consultas que involucran atributos de baja cardinalidad (where), ideal para ambientes OLAP.
- **Otros índices:** índices por múltiples atributos, índices basados en funciones, índices bitmap join, índices particionados, ...

```sql
-- unique constraint (indice b-tree implícito)
alter table dim_products
add constraint dim_products_uk
unique("Product Code")

-- indice bitmap
create bitmap index fact_superstore_fk_products_idx_bm
on fact_superstore(fk_products)
```

---

## 2. Proceso ETL

### ¿Qué es ETL?

Es el proceso que permite a las organizaciones mover datos desde múltiples fuentes, reformatearlos y limpiarlos, y cargarlos en otra base de datos, data mart, o data warehouse para su análisis, o en otro sistema operacional para apoyar un proceso de negocios.

### Importancia del proceso ETL

- El proceso más subestimado en el desarrollo DW.
- El proceso que consume más tiempo en el desarrollo DW.
- Sobre el 80 % del tiempo de desarrollo es gastado en el diseño ETL.

**Extracción:** extraer datos relevantes.

**Transformación:** limpieza de datos, transformar datos al formato DW, construir claves subrogadas.

**Carga:** cargar datos en el DW, poblar tablas de agregación.

### Fases del proceso ETL

- **Fase de Diseño** — Diseño de proceso ETL.
- **Fase de Carga Inicial** — Primer poblamiento del DW.
- **Fase de Carga Incremental** — Mantener el DW actualizado con respecto a cambios en las fuentes de datos.

### Área de Staging

Un área de stage (área de pruebas o área de ensayo), también llamada zona de landing (zona de aterrizaje), es un área intermedia de almacenamiento de datos utilizada para el procesamiento de los mismos durante procesos de extracción, transformación y carga.

**El área de staging es...**

- Un área de almacenamiento transitorio de datos en el proceso ETL.
- Sin acceso a los usuarios.
- Implementada con tablas relacionales, archivos planos u otros.
- Útil para consolidación de datos, estandarización, rendimiento, respaldo, detección de cambios, ...

### Diseño ETL: Planificación

- Realizar un diagrama de alto nivel del flujo origen-destino.
- Seleccionar y probar la herramienta ETL.
- Bosquejar las transformaciones complejas, la generación de claves subrogadas y la secuencia de trabajo para cada tabla de destino.

### Diseño ETL: Construcción de Dimensiones

- Construcción y prueba de las dimensiones estáticas.
- Construcción y prueba de una dimensión cambiante.
- Construcción y prueba del resto de las dimensiones.

### Diseño ETL: Dimensiones Estáticas

- Construir el proceso de poblamiento.
- Gestión de dimensiones cambiantes:
    - Gestionar claves subrogadas a partir de una clave de producción.
    - Gestionar actualización/inserción dependiendo del tipo de SCD.
- Poblamiento de dimensiones:
  - Dimensiones pequeñas: remplazar.
  - Dimensiones grandes: cargar solo cambios.

### Diseño ETL - Apache Hop

**Pipeline:** los Pipelines son los *data workers*. Las operaciones en un Pipeline leen, modifican, enriquecen, limpian y escriben datos. Las transformaciones en un Pipeline son ejecutadas en paralelo.

**Workflow:** un Workflow es una secuencia de operaciones que son ejecutadas secuencialmente. Los Workflows usualmente no operan sobre los datos directamente, sino que ejecutan tareas de orquestación.

#### Ejemplo de Pipeline

> **Diagrama:** flujo de un Pipeline de Apache Hop: `CSV file input` → `Filter rows` → (si cumple condición, en verde) → `Text file output`; (si no cumple, en naranjo) → `Microsoft Excel writer`.

#### Ejemplo de Workflow

> **Diagrama:** flujo de un Workflow de Apache Hop: `Start` → `File exists` → (si existe) → `demo1.hpl` → `Delete filenames from result` → `Mail`; (si no existe) → `Abort workflow`.

### Dimensiones Estáticas — Dimension Date Pipeline

> **Diagrama:** Pipeline de la dimensión de fecha (`Dimension Date Pipeline`): `40000 days: 100+ years` → `Days_since` → `Calc Date` → `DayOfWeekDesc` y `MonthDesc` (cada uno alimentado por su respectivo `*_Norm` y `*_Gen`) → `Select values 2` → `Java Script Value` → `Select values` → `DIMENSION_DATE`.

### Dimensiones SCD (tipo 1)

**Stage Orders Pipeline:**

> **Diagrama:** `CSV SUPERSTORE` → `SEL_ORDERS` → `SORT_UNIQUE_ORDERS` → `STG_ORDERS`.

**Transformation Insert/Update:**

- Se busca una fila en una tabla usando una o más *lookup keys*. Si no se encuentra la fila asociada a la clave, se inserta una nueva fila.
- Si se encuentra y los atributos a actualizar son similares, no se realiza nada.
- Si no son todos iguales, la fila se actualiza.

**Dim Orders Pipeline:**

> **Diagrama:** `STG_ORDERS` → `DIM_ORDERS`, mediante una transformación *Insert/Update* configurada así: tabla destino `RVALDIVIA.DIM_ORDERS`, clave de búsqueda `Order Code = Order Code`, y campos de actualización: `Order Code` (no se actualiza) y `Order Priority` (sí se actualiza).

**Clave Primaria Autogenerada:**

```sql
-- primary key

CREATE TABLE DIM_ORDERS (
PK_ORDERS INTEGER GENERATED ALWAYS AS IDENTITY CONSTRAINT DIM_ORDERS_PK PRIMARY KEY,
"Order Code" INTEGER,
"Order Priority" VARCHAR2(50)
)
```

### Dimensiones SCD (tipo 2)

**Stage Products Pipeline:**

> **Diagrama:** `CSV SUPERSTORE` → `SEL_PRODUCTS` → `SORT_UNIQUE_PRODUCTS` → `STG_PRODUCTS`.

**Transformation Dimension Lookup/Update:**

- Si los registros no son encontrados: se insertan en la tabla.
- Si los registros son encontrados y:
  - Uno o más atributos son diferentes y tienen un **insert** (Kimball Type II): un nuevo registro es insertado.
  - Uno o más atributos son diferentes y tienen un **punch through** (Kimball Type I): estos atributos se actualizan en todas las versiones del registro.
  - Uno o más atributos son diferentes y tienen un **update**: estos atributos se actualizan en la última versión del registro.
  - Todos los atributos son iguales: no se ejecutan actualizaciones ni inserciones.

**Dimension Products Pipeline:**

> **Diagrama:** `STG_PRODUCTS` → `DIM_PRODUCTS`, mediante una transformación *Dimension lookup/update* (con "Update the dimension?" activado), configurada con:
> - **Pestaña Keys:** clave de búsqueda `Product Code` (campo de dimensión) = `Product Code` (campo del stream).
> - **Pestaña Versioning:** `Version field = version`, `Date range start field = date_from` (año mínimo 1900), `Table date range end = date_to` (año máximo 2199) — esto define el versionamiento típico de una dimensión SCD tipo 2.

**Dimension Customers Pipeline:**

> **Diagrama:** `STG_CUSTOMERS` → `DIM_CUSTOMERS`, mediante una transformación *Dimension lookup/update* similar a la de productos. En la pestaña **Technical key** se define `Technical key field = PK_CUSTOMERS`, generado mediante "Use sequence" con la secuencia `DIM_CUSTOMERS_SEQ`.

**Sequence (secuencia para clave técnica):**

```sql
-- sequence

CREATE SEQUENCE dim_customers_seq
START WITH     1
INCREMENT BY   1
CACHE 10000;
```

### Diseño ETL: Construcción de las Tablas de Hechos

- Construcción y prueba del poblamiento inicial.
- Construcción y prueba de la carga incremental.
- Construcción y prueba de las tablas de agregados.

### Tabla de Hechos — Fact SuperStore Pipeline

> **Diagrama:** `STG_SUPERSTORE` → `LOOK_ORDERS` → `LOOK_PRODUCTS` → `LOOK_CUSTOMERS` → `LOOK_DATE` → `SEL_SUPERSTORE` → `FACT_SUPERSTORE`. Cada transformación `LOOK_*` es un *Database lookup* contra la dimensión correspondiente; por ejemplo, `LOOK_ORDERS` busca en `DIM_ORDERS` por `Order Code = Order Code` y retorna el campo `PK_ORDERS` (renombrado como `FK_ORDERS`, tipo Integer).

### Diseño ETL: Carga inicial vs. Carga incremental

**Carga inicial:**

- ETL para todos los datos hasta ahora.
- Se realiza cuando el DW se puebla la primera vez.
- Muy pesado - grandes volúmenes de datos.

**Carga incremental:**

- Mover solo los cambios desde la última carga.
- Se realiza periódicamente después del inicio de DW.
- Menos pesado - volúmenes de datos más pequeños.
- Las dimensiones deben actualizarse antes que los hechos.

### Workflow — SuperStore Workflow

> **Diagrama:** orquestación completa del proceso ETL del caso SuperStore: `START` → `STG_ORDERS` → `STG_PRODUCTS` → `STG_CUSTOMERS` → `STG_SUPERSTORE` → `FACT_SUPERSTORE` → `DIM_CUSTOMERS` → `DIM_PRODUCTS` → `DIM_ORDERS` → `Success`. Es decir, primero se pueblan las áreas de staging y luego se cargan la tabla de hechos y las dimensiones.

---

## 3. Extracción

### Full Extraction vs. Incremental Extraction

**Full Extraction:** los datos son extraídos completamente desde las fuentes de datos. Debido a que esta extracción refleja todos los datos actualmente disponibles en las fuentes de datos, no hay necesidad de mantener un seguimiento de los cambios en la fuente de datos desde la última extracción exitosa.

**Incremental Extraction:** sólo se extraen los datos que han cambiado desde un momento bien definido del tiempo. Este momento puede corresponder a la última extracción realizada o a un evento empresarial más complejo.

### Seguimiento del cambio (delta)

- Timestamps
- Partitioning
- Triggers
- Change Data Capture

### Partition Tables

> **Diagrama:** acceso directo a una tabla particionada — `SELECT * FROM EMP` puede dirigirse a una partición específica en lugar de escanear toda la tabla.

```sql
ALTER TABLE earthquake MODIFY
PARTITION BY RANGE (occurred_on)
(
PARTITION earthquakes1960
VALUES LESS THAN (TO_DATE('01/01/1970','DD/MM/YYYY')),
PARTITION earthquakes1970
VALUES LESS THAN (TO_DATE('01/01/1980','DD/MM/YYYY')),
PARTITION earthquakes1980
VALUES LESS THAN (TO_DATE('01/01/1990','DD/MM/YYYY')),
PARTITION earthquakes1990
VALUES LESS THAN (TO_DATE('01/01/2000','DD/MM/YYYY')),
PARTITION earthquakes2000
VALUES LESS THAN (TO_DATE('01/01/2010','DD/MM/YYYY')),
PARTITION earthquakes2010
VALUES LESS THAN (TO_DATE('01/01/2020','DD/MM/YYYY')))

select *
from earthquake partition(earthquakes1990)
```

### On line Extraction vs. Off line Extraction

**On line Extraction:** los datos son directamente extraídos desde el sistema fuente (accediendo directamente a las tablas de datos o a un sistema intermedio) (DBLink, Oracle GoldenGate, ...).

**Off line Extraction:** los datos no son directamente extraídos desde el sistema fuente, sino almacenados explícitamente fuera de éste (flat files, dump files, logs, transportable tablespaces, external tables, ...).

### External Tables

> **Diagrama:** una consulta `SELECT * FROM EMP` sobre una *external table* puede leer indistintamente desde la base de datos o directamente desde un archivo plano externo (`emp_data.txt`).

```sql
create or replace directory dirxe as 'C:\tmp';

CREATE TABLE saludos_ext (
id number,
saludo varchar2(20)
)
ORGANIZATION EXTERNAL (
TYPE ORACLE_LOADER
DEFAULT DIRECTORY dirxe
ACCESS PARAMETERS (
RECORDS DELIMITED BY NEWLINE
FIELDS TERMINATED BY ','
MISSING FIELD VALUES ARE NULL
)
LOCATION ('saludos.txt')
)

select * from saludos_ext;
```

### DBLinks

> **Diagrama:** el usuario `Scott` ejecuta `SELECT * FROM emp` sobre un sinónimo público (`emp -> emp@HQ.ACME.COM`) que, a través de un *database link* (unidireccional), accede a la tabla `EMP` de una base de datos remota.

```sql
CREATE PUBLIC DATABASE LINK sbduta
CONNECT TO rvaldivia IDENTIFIED BY 123
USING '(description =
(address =
(protocol = tcp)
(host = 146.83.109.225)
(Port = 1521))
(connect_data =
(sid = sbduta))
)';

select * from saludos@sbduta
```

### Materialized Views

```sql
CREATE MATERIALIZED VIEW saludos_mv
BUILD IMMEDIATE
REFRESH FORCE
ON DEMAND
AS
SELECT * FROM saludos@sbduta;

-- En la instancia master
CREATE MATERIALIZED VIEW LOG ON rvaldivia.saludos
TABLESPACE users
WITH PRIMARY KEY
INCLUDING NEW VALUES;

EXEC DBMS_MVIEW.refresh('saludos_mv');

select * from saludos_mv
```

### GoldenGate

> **Diagrama:** arquitectura de replicación de Oracle GoldenGate. En el **origen**: `App` → `Transacción` → `Base de datos` → `Cambios` → `Ficheros de logs`, los cuales son procesados por `ORACLE GoldenGate` y enviados (vía "Cambios") hacia **múltiples destinos**: bases de datos, bases de datos analíticas, Data Lake, servicios Cloud, procesadores/streaming, bus de eventos y apps, permitiendo que `App` y `Dashboard` en el destino consuman los datos replicados.
>
> Fuente: <https://www.paradigmadigital.com/dev/que-es-oracle-goldengate/>

---

## 4. Transformación

### Transformaciones usuales

- Conversiones de tipos de datos.
- Normalización − desnormalización.
- Claves de producción a claves subrogadas.

### Buenas prácticas de transformación

- **No usar valores "especiales"** (e.d., 0, -1) en los datos de las dimensiones. Estos son difíciles de entender en operaciones de consulta/análisis.
- **Marcar los hechos con una dimensión de "Data Quality"**: normal, anormal, fuera de los límites, imposible, ...
- **Tratamiento de valores NULL:**
  - Uso de nulos sólo para valores de medidas (cuidado).
  - Uso de un registro de dimensión especial para valores desconocidos/no aplicables.
  - Por ejemplo, para la dimensión de tiempo, en vez de NULL, use una clave especial para representar "Dato no conocido", ...
  - Evita problemas en joins.

---

## 5. Carga

- Cargas offline vs. cargas online.
- No verificar restricciones de integridad (debería asegurarse en el proceso ETL).
- Utilizar tablas de índice para mejorar los accesos, pero no habilitar durante el proceso de carga.
- La tabla de hechos es una buena candidata para particionamiento.
