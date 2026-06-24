# Proceso ETL

## Instalación y Configuración de Apache Hop

### Instalación de Apache Hop y Creación de Pipelines

#### Ingresar a la página web de Apache Hop

Visitar el sitio oficial de Apache Hop. Apache Hop (Hop Orchestration Platform) tiene como objetivo facilitar todos los aspectos de la orquestación de datos y metadatos. Es una plataforma de integración de datos de código abierto, fácil de usar, rápida y flexible.

El desarrollo visual permite a los desarrolladores ser más productivos que con código. Con el principio **"Design once, run anywhere"**, los workflows y pipelines se pueden diseñar en el GUI de Hop y ejecutarse en el motor nativo de Hop (local o remoto), o en Spark, Flink, Google Dataflow o AWS EMR mediante Beam. La **Gestión del Ciclo de Vida** permite a los desarrolladores y administradores cambiar entre proyectos, entornos y propósitos sin salir.

#### Ingresar a la página de descargas y seleccionar la primera opción

Desde la página de descargas, seleccionar la primera opción disponible (Apache Hop Binaries).

- Versión: `2.10.0` — Fecha: Oct. 7th, 2024
- Archivo: `apache-hop-client-2.10.0.zip`

#### Extraer y abrir `hop-gui.bat` (Windows) / `hop-gui.sh` (Unix)

| Archivo      | Descripción                  | Tamaño |
|--------------|------------------------------|--------|
| `hop-gui.bat`| Archivo por lotes de Windows | 5 KB   |
| `hop-gui.sh` | Shell Script                 | 4 KB   |

#### Se abre la ventana principal de Apache Hop

Al iniciar, se muestra una pantalla de bienvenida con el mensaje **"Welcome to the Apache Hop project!"** y enlaces a la documentación.

#### Crear una nueva pipeline

1. Hacer clic en el botón **"Nuevo"** (`Ctrl+N`) para crear una pipeline.
2. Seleccionar la opción **"Pipeline"** (en lugar de Workflow).
3. Se abrirá la pestaña de edición de pipeline. Haciendo doble clic en el área de trabajo, se podrá añadir transformaciones.

#### Seleccionar transformaciones

Al hacer doble clic en el canvas, se abre el panel de selección de transformaciones, organizado en categorías: **Basic**, **Big Data**, **Bulk loading**, **Input**, etc.

Para iniciar el proceso ETL del proyecto, se selecciona la transformación **"Microsoft Excel Input"**, que lee datos desde archivos de Microsoft Excel (formato XLS, XLSX, ODS), correspondiente al tipo de archivo de la GTD.

---

## Conexión con la base de datos de Oracle

Desde una instalación en limpio, Apache Hop no posee un controlador para conectarse a una base de datos Oracle. Se debe instalar externamente.

### Pasos para instalar el controlador JDBC de Oracle

1. Buscar el controlador JDBC (Java Database Connectivity) en la página oficial:
   `https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html`

2. Descargar la versión más apropiada. En este caso se seleccionó **"JDBC Download"** (sin DB Cloud). Se recomienda la versión compatible con las JDKs más recientes para mayor compatibilidad:

   | Driver           | JDK soportado                          |
   |------------------|-----------------------------------------|
   | `ojdbc11.jar`    | JDK11, JDK17, JDK19, JDK21            |
   | `ojdbc8.jar`     | JDK8 y JDK11                           |

3. Instalar manualmente en Apache Hop:
   - Buscar la carpeta `lib` en el directorio de instalación de Apache Hop.
   - Abrir la subcarpeta `jdbc`.
   - Copiar el archivo `ojdbc11.jar` a esa carpeta.

4. Cerrar y reiniciar Apache Hop para que reconozca el controlador.

### Crear la conexión a la base de datos

1. En Apache Hop, ir a **Metadata** (`Ctrl+Shift+M`).
2. Seleccionar **"Relational Database Connection"**.
3. En el formulario completar:

   | Campo              | Valor                                       |
   |--------------------|---------------------------------------------|
   | Connection name    | `inuta-gtd`                                 |
   | Connection type    | Oracle                                      |
   | Installed driver   | `oracle.jdbc.driver.OracleDriver (23.5.0.24.07)` |
   | Username           | `in2024_gtd`                                |
   | Server host name   | `146.83.109.225`                            |
   | Port number        | `1521`                                      |
   | Database name      | `inuta`                                     |

4. Hacer clic en **"Test"** para verificar la conexión.
5. Guardar con el botón de disquete azul.

---

## Definición de la Carga Inicial utilizando Apache Hop

### Carga de BigTable GTD

La primera carga consiste en leer el archivo Excel con la transformación **"Microsoft Excel Input"** y escribir el resultado en la tabla `GTD BIGTABLE`.

```
Microsoft Excel Input  →  GTD BIGTABLE
```

---

### Carga de Dimensión Lugar

Para la creación de la dimensión lugar se realiza lectura de la BigTable ya descrita, extrayendo los atributos correspondientes a la dimensión mediante el componente **Table Input**. Al ser modelada como una **SCD tipo 2**, se considera la fecha de cuándo se realizó la pipeline para hacer las operaciones de inserción y actualización en las columnas `valid_from` y `valid_to`. Los campos cambiantes son: `country_txt` y `region_txt`.

```
LECTURA ATRIBUTOS LUGAR  →  OBTENER FECHA DE PIPELINE  →  Dimension lookup/update DIM_LUGAR
```

**Lookup/Update fields:**

| Dimension field | Stream field to compare | Type of dimension update |
|-----------------|-------------------------|--------------------------|
| COUNTRY_TXT     | COUNTRY_TXT             | Insert                   |
| REGION_TXT      | REGION_TXT              | Insert                   |

---

### Carga de Dimensión Detalles

**Creación de tablas:**

```sql
CREATE TABLE DIM_DETALLE_STG (
    detalle_sk numeric,
    crit1 integer,
    crit2 integer,
    crit3 integer,
    doubtterr integer,
    alternative integer,
    alternative_txt varchar2(64),
    multiple integer
);

CREATE TABLE DIM_DETALLE (
    crit1 integer,
    crit2 integer,
    crit3 integer,
    doubtterr integer,
    alternative integer,
    alternative_txt varchar2(64),
    multiple integer,
    CRIT1_TXT VARCHAR2(64),
    CRIT2_TXT VARCHAR2(72),
    CRIT3_TXT VARCHAR2(64),
    MULTIPLE_TXT VARCHAR2(64),
    DOUBTTERR_TXT VARCHAR2(32)
);
```

Para la dimensión detalles es necesario agregar atributos que no están presentes en la fuente de datos original, pero sí en el manual de la GTD. Se utiliza una consulta SELECT con CASE dentro del Table Input para extraer y transformar los campos adicionales. Finalmente, el componente **Combination LookUp** permite hacer actualizaciones para dimensiones descritas como SCD tipo 1.

**Consulta SQL usada:**

```sql
SELECT CRIT1, CRIT2, CRIT3, DOUBTTERR, ALTERNATIVE, ALTERNATIVE_TXT, MULTIPLE,
'POLITICAL, ECONOMIC, RELIGIOUS, OR SOCIAL GOAL' AS CRIT1_TXT,
'INTENTION TO COERCE, INTIMIDATE OR PUBLICIZE TO LARGER AUDIENCE(S)' AS CRIT2_TXT,
'OUTSIDE INTERNATIONAL HUMANITARIAN LAW' AS CRIT3_TXT,
CASE DOUBTTERR WHEN 0 THEN 'NO' WHEN 1 THEN 'YES' ELSE 'Desconocido' END AS DOUBTTERR_TXT,
CASE MULTIPLE WHEN 0 THEN 'NO' WHEN 1 THEN 'YES' ELSE 'DESCONOCIDO' END AS MULTIPLE_TXT
FROM GTD
```

```
Lectura distinct datos de detalle  →  Combination lookup/update
```

---

### Carga de Dimensión Especificación Lugar

**Creación de tablas:**

```sql
CREATE TABLE DIM_ESPEC_LUGAR_STG (
    vicinity number(1),
    vicinity_txt varchar2(64),
    specify integer,
    specify_txt varchar2(255)
);

CREATE TABLE DIM_ESPEC_LUGAR (
    spec_lugar_sk integer generated by default as identity,
    vicinity number(1),
    vicinity_txt varchar2(64),
    specify integer,
    specify_txt varchar2(255)
);
```

Se realiza un Table Input de la BigTable GTD recopilando los datos de la dimensión. Dentro del SELECT se utiliza un CASE para transformar los valores numéricos. Para variables categóricas nulas, se hace conversión al valor numérico `-9` (convención para "desconocido"). La dimensión se trata con **Combination LookUp** (SCD tipo 1).

```
lectura especificación lugar  →  If Null  →  Combination lookup/update
```

---

### Carga de Dimensión Detalles Adicionales

**Creación de tablas:**

```sql
CREATE TABLE DIM_DETALLES_A (
    detalles_a_sk number generated by default as identity,
    int_log number,
    int_log_text varchar2(255),
    int_misc number,
    int_misc_text varchar2(255),
    int_any number,
    int_any_text varchar2(255)
);

CREATE TABLE DIM_DETALLES_A_STG (
    int_log number,
    int_log_text varchar2(255),
    int_misc number,
    int_misc_text varchar2(255),
    int_any number,
    int_any_text varchar2(255)
);
```

Se extraen los datos desde la BigTable GTD con **Table Input** y se usa la expresión CASE para definir el texto de las columnas `int_log_text`, `int_misc_text` e `int_any_text`.

```sql
select distinct
int_log,
case int_log when 1 then 'Si' when 0 then 'No' when -9 then 'Desconocido' END as int_log_text,
int_misc,
case int_misc when 1 then 'Si' when 0 then 'No' when -9 then 'Desconocido' END as int_misc_text,
int_any,
case int_any when 1 then 'Si' when 0 then 'No' when -9 then 'Desconocido' END as int_any_text
from gtd
```

```
GTD  →  DIM_DETALLES_A_STG

DIM_DETALLES_A_STG  →  DIM_DETALLES_A  (Combination Lookup)
```

**Campos comparados en Combination Lookup:**

| # | Dimension field | Field in stream |
|---|-----------------|-----------------|
| 1 | INT_LOG         | INT_LOG         |
| 2 | INT_LOG_TEXT    | INT_LOG_TEXT    |
| 3 | INT_MISC        | INT_MISC        |
| 4 | INT_MISC_TEXT   | INT_MISC_TEXT   |
| 5 | INT_ANY         | INT_ANY         |
| 6 | INT_ANY_TEXT    | INT_ANY_TEXT    |

**Technical key field:** `DETALLES_A_SK`

---

### Carga de Dimensión Armas

**Creación de tablas:**

```sql
CREATE TABLE DIM_ARMAS_STG (
    weaptype number,
    weaptype_txt varchar2(128),
    weapsubtype number,
    weapsubtype_txt varchar2(128)
);

CREATE TABLE DIM_ARMAS (
    armas_sk number generated by default as identity,
    weaptype number,
    weaptype_txt varchar2(128),
    weapsubtype number,
    weapsubtype_txt varchar2(128)
);
```

Dado que la tabla de hechos usa desnormalización para las armas, la dimensión Armas contiene información de un arma por registro. Es necesario extraer todas las columnas de arma individualmente de la BigTable GTD (cuatro conjuntos de columnas: ARMA1, ARMA2, ARMA3, ARMA4). Se usa **If Null** para limpiar valores, luego **Sort rows** y **Unique rows** antes de cargar en `DIM_ARMAS_STG`.

```
ARMA1 ─┐
ARMA2 ─┤→  If Null  →  Sort rows  →  Unique rows  →  Table output
ARMA3 ─┤
ARMA4 ─┘
```

Luego, la pipeline final carga desde la staging a la dimensión:

```
STG ARMAS  →  ARMAS LOOKUP  (Combination Lookup)
```

---

### Carga de Dimensión Ataque

**Creación de tablas:**

```sql
CREATE TABLE DIM_ATAQUE (
    ataque_sk integer generated by default as identity (start with 1),
    attacktype1 int,
    attacktype1_txt varchar2(255),
    attacktype2 int,
    attacktype2_txt varchar2(255),
    attacktype3 int,
    attacktype3_txt varchar2(255),
    success number(1),
    suicide number(1)
);

CREATE TABLE DIM_ATAQUE_STG (
    attacktype1 int,
    attacktype1_txt varchar2(255),
    attacktype2 int,
    attacktype2_txt varchar2(255),
    attacktype3 int,
    attacktype3_txt varchar2(255),
    success number(1),
    suicide number(1)
);
```

**Pipeline de carga:**

```
GTD  →  If Null  →  DIM_ATAQUE_STG

DIM_ATAQUE_STG  →  DIM_ATAQUE  (Combination Lookup)
```

**SELECT usado:**

```sql
SELECT DISTINCT attacktype1, attacktype1_txt,
attacktype2, attacktype2_txt,
attacktype3, attacktype3_txt,
success, suicide FROM GTD
```

Los nulos en `ATTACKTYPE2`, `ATTACKTYPE3` y sus textos se reemplazan por `-1` y `"Not applicable"` respectivamente.

**Campos comparados:**

| # | Dimension field  | Field in stream  |
|---|------------------|------------------|
| 1 | ATTACKTYPE1      | ATTACKTYPE1      |
| 2 | ATTACKTYPE1_TXT  | ATTACKTYPE1_TXT  |
| 3 | ATTACKTYPE2      | ATTACKTYPE2      |
| 4 | ATTACKTYPE2_TXT  | ATTACKTYPE2_TXT  |
| 5 | ATTACKTYPE3      | ATTACKTYPE3      |
| 6 | ATTACKTYPE3_TXT  | ATTACKTYPE3_TXT  |
| 7 | SUCCESS          | SUCCESS          |
| 8 | SUICIDE          | SUICIDE          |

**Technical key field:** `ATAQUE_SK`

---

### Carga de Dimensión Perpetradores

**Creación de tablas:**

```sql
CREATE TABLE dim_perpetradores_stg (
    gname varchar2(512),
    gsubname varchar2(512)
);

CREATE TABLE dim_perpetradores (
    perp_sk integer,
    gname varchar2(512),
    gsubname varchar2(512)
);
```

Dado que pueden aparecer hasta tres perpetradores por evento, se normaliza la tabla. Se hace un **UNPIVOT** de los grupos para tenerlos todos en las mismas columnas:

```sql
select distinct gname, gsubname
from gtd
unpivot (
    (gname, gsubname) for name_type in (
        (gname, gsubname) as 'group1',
        (gname2, gsubname2) as 'group2',
        (gname3, gsubname3) as 'group3'
    )
)
```

**Pipeline de staging:**

```
Perpetradores Unpivoteados  →  Filtrar GNAME nulo  →  GSUBNAME NULL  →  Sort rows  →  PERPETRADORES STG
```

**Pasos:**
1. Filtrado de nulos por posibles filas vacías
2. Tratado de nulos (valores vacíos → `"Not specified"` y `-1`)
3. Ordenar filas por todas las columnas
4. Cargar tabla de staging

**Pipeline final:**

```
PERPETRADORES STG  →  CL/U DIM PERPETRADORES
```

La clave subrogada usa la estrategia `<Nro Filas Tabla> + 1`.

---

### Carga de Dimensión MCR

**Consulta para valores únicos:**

```sql
select DISTINCT
    claimmode,
    claimmode_txt
from gtd
ORDER by claimmode
```

**Creación de tablas:**

```sql
CREATE TABLE dim_mcr_stg (
    claimmode integer,
    claimmode_txt varchar2(255)
);

CREATE TABLE dim_mcr (
    mcr_sk integer,
    claimmode integer,
    claimmode_txt varchar2(255)
);
```

**Pasos de la pipeline:**
1. Cargar la información única de MCRs
2. Filtrar posibles datos nulos
3. Generar el caso no especificado (evitar guardar nulos)
4. Llenar la tabla de staging

**Pipeline final:**

```
MCR STG  →  CL/U DIM MCR
```

1. Los datos se extraen de la fase de staging
2. Se realiza un Combination Lookup para garantizar unicidad

La clave subrogada usa la estrategia `<Nro Filas Tabla> + 1`.

---

### Carga de Dimensión Grupo Perpetradores y BT Grupo

Dentro de la GTD los perpetradores no tienen preferencia; se ordenan por aparición. Un grupo terrorista se diferencia de otro si tiene un motivo o tipo de conflicto de reclamación diferente.

**Creación de tablas:**

```sql
-- DIMENSIÓN GRUPOS PERPETRADORES
CREATE TABLE dim_gperp_stg (
    grupo integer,
    compclaim number(1),
    motive clob
);

CREATE TABLE dim_gperp (
    grupo_sk integer,
    compclaim number(1),
    motive clob
);

-- DIMENSIÓN BT GPERPS
CREATE TABLE dim_bt_grupo_stg (
    grupo integer,
    perp_fk integer,
    mcr_fk integer,
    guncertain integer,
    claimed int
);

CREATE TABLE dim_bt_grupo (
    grupo_fk integer,
    perp_fk integer,
    guncertain number(1),
    claimed number(1),
    mcr_fk int
);
```

**Tablas y artefactos adicionales:**

```sql
CREATE TABLE denormalized_data_stg (
    grupo integer, compclaim number(1), motive clob,
    perp_fk1 integer, mcr_fk1 integer, claimed1 integer, guncertain1 integer,
    perp_fk2 integer, mcr_fk2 integer, claimed2 integer, guncertain2 integer,
    perp_fk3 integer, mcr_fk3 integer, claimed3 integer, guncertain3 integer,
    checksum integer
);

CREATE SEQUENCE grupo_seq
    INCREMENT BY 1 START WITH 0
    NOMAXVALUE MINVALUE 0 NOCYCLE CACHE 100;
```

**En total se utilizaron tres pipelines distintas:**
1. Extracción y tratado primario de la información
2. Desnormalización para el tratado de la unicidad de los datos
3. Filtrado de unicidad, renormalización y poblamiento de las dimensiones

**Pasos de la primera pipeline (para BT_GRUPO_STG):**
1. Extraer todos los datos de las combinaciones de perpetradores
2. Conservar las combinaciones únicas (`Unique rows (HashSet)`)
3. Enumerar los grupos
4. Normalización de la información
5. Filtrado de nulos
6. Tratado de nulos (`"Not specified"` y `"-1"`)
7. Búsqueda de llaves foráneas (MCR_FK L/U y PERP_FK L/U)
8. Selección de valores pertinentes
9. Carga a tablas de staging

**Segunda pipeline — query de desnormalización:**

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

**Tercera pipeline — verificación de unicidad:**

```sql
SELECT dds.*
FROM denormalized_data_stg dds
LEFT JOIN denormalized_data_dim ddd ON (dds.checksum = ddd.checksum)
WHERE ddd.checksum IS NULL
```

---

### Carga de Dimensión Objetivo

**Creación de tablas:**

```sql
CREATE TABLE dim_objetivos_stg (
    targtype integer, targtype_txt varchar2(255),
    targsubtype integer, targsubtype_txt varchar2(255),
    corp varchar2(255), target varchar2(512),
    natlty integer, natlty_txt varchar2(255)
);

CREATE TABLE dim_objetivos (
    objetivo_sk integer,
    targtype integer, targtype_txt varchar2(255),
    targsubtype integer, targsubtype_txt varchar2(255),
    corp varchar2(255), target varchar2(512),
    natlty integer, natlty_txt varchar2(255)
);
```

Dado que un evento terrorista puede tener más de un objetivo, la información se normalizó para una eficiente referenciación.

**Pasos de la pipeline:**
1. Normalizar la información a subir
2. Tratado de nulos
3. Ordenado de la información
4. Filtrado de valores únicos (`Unique rows`)
5. Población de la tabla de staging

```
OBJ1  ─┐
OBJ1 2 ─┤→  TRATADO NULOS  →  Sort rows  →  Unique rows  →  OBJETIVOS STG
OBJ1 3 ─┘

OBJETIVOS STG  →  CL/U DIM OBJETIVOS
```

La clave subrogada usa la estrategia `<Nro Filas Tabla> + 1`.

---

### Carga de Dimensión Impacto

**Creación de tablas:**

```sql
CREATE TABLE DIM_IMPACTO (
    impacto_sk integer generated by default as identity (start with 1),
    property integer,
    propextent integer,
    propextent_txt varchar2(255),
    ishostkid integer,
    hostkidoutcome integer,
    hostkidoutcome_txt varchar2(255)
);

CREATE TABLE DIM_IMPACTO_STG (
    property integer,
    propextent integer,
    propextent_txt varchar2(255),
    ishostkid integer,
    hostkidoutcome integer,
    hostkidoutcome_txt varchar2(255)
);
```

**Pipeline:**

```
GTD  →  If Null  →  STG_DIM_IMPACTO

DIM_IMPACTO_STG  →  DIM_IMPACTO  (Combination Lookup)
```

Los valores nulos se reemplazan: campos numéricos → `-1`, campos de texto → `"Not applicable"`.

**Technical key field:** `IMPACTO_SK`

---

### Carga de Dimensión Tiempo

Al ser una dimensión estática, se utilizó un procedimiento almacenado en Oracle que genera registros para el rango de fechas completo (1 de enero de 1970 al 1 de enero de 2199).

```sql
CREATE OR REPLACE PROCEDURE generar_rango AS
    fecha_inicio Date := TO_DATE('01-01-1970','dd-MM-YYYY');
    fecha_fin    Date := TO_DATE('01-01-2199','dd-MM-YYYY');
    variable_tiempo_sk numeric;
    variable_agno      numeric;
    variable_mes       numeric;
    variable_dia       numeric;
BEGIN
    WHILE fecha_inicio <= fecha_fin LOOP
        variable_tiempo_sk := TO_NUMBER(TO_CHAR(fecha_inicio,'YYYYMMDD'));
        variable_agno      := TO_NUMBER(TO_CHAR(fecha_inicio,'YYYY'));
        variable_mes       := TO_NUMBER(TO_CHAR(fecha_inicio,'MM'));
        variable_dia       := TO_NUMBER(TO_CHAR(fecha_inicio,'DD'));
        INSERT INTO dim_tiempo (tiempo_sk, iyear, imonth, iday)
        VALUES (variable_tiempo_sk, variable_agno, variable_mes, variable_dia);
        fecha_inicio := fecha_inicio + 1;
    END LOOP;
END;

BEGIN
    GENERAR_RANGO;
END;
```

---

### Carga de Fact GTD

Para cargar la tabla de hechos es necesario tener cargadas todas las demás dimensiones. La pipeline usa el componente **Database Lookup** que busca, dimensión por dimensión, los registros de la BigTable GTD y retorna el valor de la clave subrogada correspondiente.

Para las dimensiones normalizadas dentro de la tabla de hechos (armas, víctimas), se hace la misma cantidad de lookups que de relaciones con la dimensión asociada.

Para la dimensión de grupo de perpetradores se usa un **Table Input** que obtiene la información desnormalizada de cada grupo con su surrogate key. Luego, un **Stream Lookup** recupera la clave subrogada comparando todos los atributos del grupo.

**Atributos del Stream Lookup:**

| # | Field        | Lookup field |
|---|--------------|--------------|
| 1 | MOTIVE       | MOTIVE       |
| 2 | COMPCLAIM    | COMPCLAIM    |
| 3 | PERP_FK1     | PERP_FK1     |
| 4 | MCR_FK1      | MCR_FK1      |
| 5 | CLAIMED      | CLAIMED1     |
| 6 | GUNCERTAIN1  | GUNCERTAIN1  |
| 7 | PERP_FK2     | PERP_FK2     |
| 8 | MCR_FK2      | MCR_FK2      |
| 9 | CLAIM2       | CLAIMED2     |
| 10| GUNCERTAIN2  | GUNCERTAIN2  |
| 11| PERP_FK3     | PERP_FK3     |
| 12| MCR_FK3      | MCR_FK3      |
| 13| CLAIM3       | CLAIMED3     |
| 14| GUNCERTAIN3  | GUNCERTAIN3  |

---

## Definición de carga periódica para la base de datos

Existe solo una SCD tipo 2 en el modelo (dimensión **Lugar**). Las cargas periódicas para las SCD tipo 1 son relativamente sencillas: se tratan los datos y se comparan con los valores existentes usando un lookup simple. Para la SCD tipo 2 se usan los atributos de validez (`valid_from`, `valid_to`) y versión.

### Periodicidad de las cargas

La tabla de hechos está diseñada para recibir datos **anualmente**, ya que la organización detrás de la GTD (START) recopila y trata los datos de forma anual antes de subirlos a la base de datos oficial.

---

## Creación de Workflow para Carga Completa del Datamart

Una vez determinadas todas las pipelines, se creó el **workflow** que inicia el poblamiento masivo del datamart de GTD.

Durante la ejecución, se detectó que la velocidad era de aproximadamente **1 fila cada 2 segundos**, lo que implicaría una duración estimada de **6 días** para el dataset completo. Se optó por usar un subconjunto de datos (eventos después de 2019), cargando aproximadamente **20.000 filas** con una duración total de **~10 horas**.

El workflow incluye los siguientes nodos principales:

```
Start → Check DB connections → CARGA BIGTABLE → DIM LUGAR → DIM DETALLE → DIM ESPEC LUGAR
      → STG DETALLES ADICIONALES → DIM DETALLES ADICIONALES → STG ARMAS → DIM ARMAS
      → STG ATAQUE → DIM ATAQUE → DIM PERP STG → DIM PERPETRADORES → STG MCR → DIM MCR
      → STG IMPACTO → DIM OBJETIVOS → STG OBJETIVOS → UNION DIMENSIONES PERP
      → DESNORMALIZACION GRUPOS → STG BT PERPETRADORES → FACT TABLE! → Success
```

---

## Pruebas iniciales al Datamart de GTD

Se cargaron **17.834 registros** para las pruebas iniciales. Se detectó una gran cantidad de datos nulos en ciertas medidas, por lo que las consultas tienden a usar funciones `count()`.

### Consultas de prueba

#### Ranking de años por cantidad de atentados

```sql
SELECT
    rank() OVER (ORDER BY cantidad_atentados DESC) AS ranking,
    iyear,
    cantidad_atentados
FROM (
    SELECT iyear, count(1) cantidad_atentados
    FROM fact_gtd_event
    JOIN dim_tiempo ON (fk_fecha_ini = tiempo_sk)
    GROUP BY iyear
);
```

**Resultados:**

| Ranking | Año  | Cantidad |
|---------|------|----------|
| 1       | 2019 | 8537     |
| 2       | 2020 | 8438     |
| 3       | 1972 | 146      |
| 4       | 1970 | 118      |
| 5       | 1977 | 101      |
| 6       | 1973 | 95       |
| 7       | 1971 | 89       |
| 8       | 1976 | 83       |
| 9       | 1974 | 72       |
| 10      | 1975 | 68       |
| 11      | 1978 | 42       |
| 12      | 1979 | 29       |

---

#### Porcentaje de ataques en los que el perpetrador se suicidó

```sql
SELECT
    CASE WHEN suicide = 1 THEN 'Si' ELSE 'No' END AS suicidio,
    count(*) AS cantidad,
    round((count(*) / (SELECT count(*) FROM fact_gtd_event)) * 100, 2) AS porcentaje
FROM fact_gtd_event
JOIN dim_ataque ON fk_ataque = ataque_sk
GROUP BY suicide;
```

**Resultados:**

| Suicidio | Cantidad | Porcentaje |
|----------|----------|------------|
| Si       | 5767     | 32.34%     |
| No       | 11981    | 67.18%     |

---

#### Cantidad de tipos de ataque por grupo perpetrador

```sql
SELECT gname AS Nombre_GPERPETRADOR, attacktype1_txt AS TIPO_ATAQUE, count(*) CANTIDAD
FROM fact_gtd_event
JOIN dim_gperp ON (grupo_sk = fk_perpg)
JOIN dim_bt_grupo ON grupo_sk = grupo_fk
JOIN dim_perpetradores ON (perp_fk = perp_sk)
JOIN dim_ataque ON (fk_ataque = ataque_sk)
GROUP BY rollup(gname, attacktype1_txt);
```

---

#### Cantidad de ataques por grupo perpetrador, año y mes

```sql
SELECT iyear, imonth, gname AS Nombre_GPERPETRADOR, count(1) CANTIDAD
FROM fact_gtd_event
JOIN dim_gperp ON (grupo_sk = fk_perpg)
JOIN dim_bt_grupo ON grupo_sk = grupo_fk
JOIN dim_perpetradores ON (perp_fk = perp_sk)
JOIN dim_tiempo ON (fk_fecha_ini = tiempo_sk)
GROUP BY rollup(iyear, imonth, gname);
```

---

#### Cantidad de ataques por región, país, ciudad, tipo de objetivo y nombre de objetivo

```sql
SELECT region_txt, country_txt, city, targtype_txt, target, count(1) cantidad
FROM fact_gtd_event
JOIN dim_objetivos ON (fk_obj1 = objetivo_sk)
JOIN dim_lugar ON (fk_lugar = lugar_sk)
GROUP BY rollup(region_txt, country_txt, city, targtype_txt, target);
```
