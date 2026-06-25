# Universidad de Tarapacá
**Departamento de Ingeniería en Computación e Informática — Facultad de Ingeniería**

---

## 7. Implementación del Data Mart

En esta sección se presentarán los distintos scripts SQL utilizados para la creación de las dimensiones y tablas de hechos necesarias, preparando así la estructura del Data Mart para el proceso E.T.L. con Apache Hop.

---

### 7.1. Dimensión: Olympic Games

*Figura 16: Código SQL: Creación de la dimensión Olympic Games.*

```sql
CREATE TABLE dim_olympic_games (
    su_edition                NUMBER GENERATED ALWAYS AS IDENTITY,
    edition_id                NUMBER,
    edition_name              VARCHAR2(3000),
    edition_year              NUMBER,
    edition_city              VARCHAR2(3000),
    edition_start_date        VARCHAR2(3000),
    edition_end_date          VARCHAR2(3000),
    edition_competition_date  VARCHAR2(3000),
    edition_country_noc       VARCHAR2(100),
    edition_is_held           VARCHAR2(100)
);

ALTER TABLE dim_olympic_games
    ADD CONSTRAINT dim_olympic_games_pk PRIMARY KEY (su_edition) RELY;

ALTER TABLE dim_olympic_games
    ADD CONSTRAINT dim_olympic_games_uk UNIQUE (edition_id);
```

---

### 7.2. Dimensión: Olympic Events

*Figura 17: Código SQL: Creación de la dimensión Olympic Events.*

```sql
CREATE TABLE dim_olympic_events (
    su_event            NUMBER GENERATED ALWAYS AS IDENTITY,
    event_id            NUMBER,
    event_title         VARCHAR2(3000),
    event_sport         VARCHAR2(3000),
    event_date          VARCHAR2(3000),
    event_location      VARCHAR2(3000),
    event_participants  VARCHAR2(3000),
    event_format        VARCHAR2(3000),
    event_detail        VARCHAR2(3000)
);

ALTER TABLE dim_olympic_events
    ADD CONSTRAINT dim_olympic_events_pk PRIMARY KEY (su_event) RELY;

ALTER TABLE dim_olympic_events
    ADD CONSTRAINT dim_olympic_events_uk UNIQUE (event_id);
```

---

### 7.3. Dimensión: Olympic Athlete Biography

*Figura 18: Código SQL: Creación de la dimensión Olympic Athlete Biography.*

```sql
CREATE TABLE dim_olympic_athlete_bio (
    su_athlete        NUMBER,
    athlete_id        NUMBER,
    athlete_name      VARCHAR2(3000),
    athlete_sex       VARCHAR2(50),
    athlete_born      VARCHAR2(3000),
    athlete_year_born NUMBER,
    athlete_height    NUMBER,
    athlete_weight    VARCHAR2(3000),
    date_from         DATE,
    date_to           DATE,
    version           NUMBER
);

ALTER TABLE dim_olympic_athlete_bio
    ADD CONSTRAINT dim_olympic_athlete_bio_pk PRIMARY KEY (su_athlete) RELY;

CREATE SEQUENCE OLYMPIC_ATHLETE_BIO_SEQ
    START WITH 1
    INCREMENT BY 1
    CACHE 10
    NOCYCLE;
```

---

### 7.4. Dimensión: Olympic NOCs

*Figura 19: Código SQL: Creación de la dimensión Olympic NOCs.*

```sql
CREATE TABLE dim_olympic_nocs (
    su_noc          NUMBER,
    noc_code        VARCHAR2(50),
    anoc_code       VARCHAR2(50),
    country_name    VARCHAR2(300),
    continent_name  VARCHAR2(300),
    is_active       VARCHAR2(50),
    date_from       DATE,
    date_to         DATE,
    version         NUMBER
);

ALTER TABLE dim_olympic_nocs
    ADD CONSTRAINT dim_olympic_nocs_pk PRIMARY KEY (su_noc) RELY;

CREATE SEQUENCE OLYMPIC_NOCS_SEQ
    START WITH 1
    INCREMENT BY 1
    CACHE 10
    NOCYCLE;
```

---

### 7.5. Dimensión: Medal Results

*Figura 20: Código SQL: Creación de la dimensión Olympic Medal Results.*

```sql
CREATE TABLE dim_olympic_medal_results (
    su_result      NUMBER GENERATED ALWAYS AS IDENTITY,
    medal_result   VARCHAR2(15),
    format_result  VARCHAR2(15)
);

ALTER TABLE dim_olympic_medal_results
    ADD CONSTRAINT dim_medal_results_pk PRIMARY KEY (su_result) RELY;
```

---

### 7.6. Tabla de Hechos: Athlete Event Results

*Figura 21: Código SQL: Creación de la tabla de hechos Athlete Event Results.*

```sql
CREATE TABLE fact_athlete_event_results (
    fk_event    NUMBER CONSTRAINT fact_athlete_event_event_results_event_nn   NOT NULL,
    fk_edition  NUMBER CONSTRAINT fact_athlete_event_event_results_edition_nn NOT NULL,
    fk_result   NUMBER CONSTRAINT fact_athlete_event_event_results_result_nn  NOT NULL,
    fk_athlete  NUMBER CONSTRAINT fact_athlete_event_event_results_athlete_nn NOT NULL,
    fk_noc      NUMBER CONSTRAINT fact_athlete_event_event_results_noc_nn     NOT NULL
);

-- Constraints
ALTER TABLE fact_athlete_event_results
    ADD CONSTRAINT fact_aev_dim_olympic_events_fk
    FOREIGN KEY (fk_event) REFERENCES dim_olympic_events
    RELY DISABLE NOVALIDATE;

ALTER TABLE fact_athlete_event_results
    ADD CONSTRAINT fact_aev_dim_olympic_games_fk
    FOREIGN KEY (fk_edition) REFERENCES dim_olympic_games
    RELY DISABLE NOVALIDATE;

ALTER TABLE fact_athlete_event_results
    ADD CONSTRAINT fact_aev_dim_olympic_result_fk
    FOREIGN KEY (fk_result) REFERENCES dim_olympic_medal_results
    RELY DISABLE NOVALIDATE;

ALTER TABLE fact_athlete_event_results
    ADD CONSTRAINT fact_aev_dim_olympic_athlete_bio_fk
    FOREIGN KEY (fk_athlete) REFERENCES dim_olympic_athlete_bio
    RELY DISABLE NOVALIDATE;

ALTER TABLE fact_athlete_event_results
    ADD CONSTRAINT fact_aev_dim_olympic_nocs_fk
    FOREIGN KEY (fk_noc) REFERENCES dim_olympic_nocs
    RELY DISABLE NOVALIDATE;

-- Bitmaps
CREATE BITMAP INDEX fact_athlete_event_results_fk_event_idx_bm
    ON fact_athlete_event_results (fk_event);

CREATE BITMAP INDEX fact_athlete_event_results_fk_edition_idx_bm
    ON fact_athlete_event_results (fk_edition);

CREATE BITMAP INDEX fact_athlete_event_results_fk_medal_result_idx_bm
    ON fact_athlete_event_results (fk_result);

CREATE BITMAP INDEX fact_athlete_event_results_fk_athlete_idx_bm
    ON fact_athlete_event_results (fk_athlete);

CREATE BITMAP INDEX fact_athlete_event_results_fk_noc_idx_bm
    ON fact_athlete_event_results (fk_noc);
```

---

### 7.7. Tabla de Hechos Agregada: Olympic Medal Tally

*Figura 22: Código SQL: Creación de la tabla agregada Olympic Medal Tally.*

```sql
CREATE TABLE fact_olympic_medal_tally (
    fk_edition  NUMBER CONSTRAINT medal_tally_edition_nn NOT NULL,
    fk_noc      NUMBER CONSTRAINT medal_tally_noc_nn     NOT NULL,
    gold        NUMBER,
    silver      NUMBER,
    bronze      NUMBER,
    total       NUMBER
);

-- Constraints
ALTER TABLE fact_olympic_medal_tally
    ADD CONSTRAINT fact_mtally_dim_olympic_games_fk
    FOREIGN KEY (fk_edition) REFERENCES dim_olympic_games
    RELY DISABLE NOVALIDATE;

ALTER TABLE fact_olympic_medal_tally
    ADD CONSTRAINT fact_mtally_dim_olympic_nocs_fk
    FOREIGN KEY (fk_noc) REFERENCES dim_olympic_nocs
    RELY DISABLE NOVALIDATE;

-- Bitmaps
CREATE BITMAP INDEX fact_olympic_medal_tally_fk_edition_idx_bm
    ON fact_olympic_medal_tally (fk_edition);

CREATE BITMAP INDEX fact_olympic_medal_tally_fk_noc_idx_bm
    ON fact_olympic_medal_tally (fk_noc);
```

---

## 8. Descripción del proceso de E.T.L.

### 8.1. Definición del proceso de carga inicial

#### 8.1.1. Proceso E.T.L: Dimensión: Olympic Games

Para el poblamiento de la dimensión Olympic Games, primero se formatearon los valores nulos existentes en el dataset en las columnas `competition_date`, `start_date` y `end_date`, para esto se reemplazó por un valor mágico `"Not specific date"`. De igual manera, se formateó la columna `is_held` utilizando `"Yes"` y `"No"`, y se ordenaron según el año de forma ascendente. Finalmente el proceso de carga inserta o actualiza los registros en la base de datos:

- Si el registro ya existe y alguno de sus valores ha cambiado, se **actualiza**, ya que la dimensión es una Slowly Changing Dimension (SCD) de Tipo 1.
- Si el registro no existe, se **inserta** asignándole una surrogate key a nivel de base de datos, definida mediante "Auto Increment".

> **Figura 23:** Proceso E.T.L Dimensión Olympic Games

> **Figura 24:** Vista de la dimensión Olympic Games

---

#### 8.1.2. Proceso E.T.L: Dimensión: Olympic Events

Para la dimensión Olympic Events, se aplicó el mismo procedimiento que en la anterior. En este caso no se utilizaron componentes para formatear las columnas del dataset, ya que los valores nulos estaban representados mediante un valor mágico. Al igual que en el caso anterior, esta dimensión es una Slowly Changing Dimension (SCD) de Tipo 1, por lo que al momento de poblar la dimensión:

- Si un registro ya existe pero tiene valores distintos, se **actualiza**.
- En caso de no existir, se **crea** un nuevo registro asignándole una surrogate key a nivel de base de datos.

> **Figura 25:** Proceso E.T.L Dimensión Olympic Events

> **Figura 26:** Vista de la dimensión Olympic Events

---

#### 8.1.3. Proceso E.T.L: Dimensión: Olympic Athlete Biography

Para el poblamiento de la dimensión Olympic Athlete Biography, el principal problema fue obtener el año de nacimiento del atleta, que aparecía en distintos formatos y era fundamental para responder una de las preguntas de investigación. Para solucionar esto:

1. Se filtraron los registros que contenían fechas de nacimiento que terminaran en dígitos, ya que estos generalmente corresponden al año de nacimiento.
2. Se extrajeron los últimos cuatro caracteres de esas fechas para obtener el año de nacimiento, que fue convertido a entero para facilitar el cálculo de la edad.
3. Para el manejo de valores nulos, estos se convirtieron en `0`.

Además, dado que esta dimensión es una Slowly Changing Dimension (SCD) de Tipo 2, para el manejo adecuado de los cambios en atributos como nombre, altura y peso de los atletas existentes, se configuró para crear nuevas versiones del perfil del atleta cuando ocurren modificaciones, gestionadas a través del componente "Dimension lookup/update", el cual también utiliza una secuencia previamente creada para asignar una surrogate key a cada nuevo registro.

> **Figura 27:** Proceso E.T.L Dimensión Olympic Athlete Biography

> **Figura 28:** Vista de la dimensión Olympic Athlete Biography

---

#### 8.1.4. Proceso E.T.L: Dimensión: Olympic NOCs

En esta dimensión, el poblamiento no presentó dificultades, ya que los registros del dataset no tenían problemas de formato ni contenían valores nulos. Simplemente se procedió a realizar la configuración para gestionar las versiones de los cambios en los atributos de los comités, ya que esta dimensión es una Slowly Changing Dimension (SCD) de Tipo 2, lo cual es crucial para mantener un historial que refleje:

- Cómo los comités pueden pertenecer a distintas organizaciones continentales (ANOC).
- El estado de los comités (activos o inactivos en distintos momentos).

Esta configuración se realizó en el componente "Dimension lookup/update", al igual que la asignación de la surrogate key a los nuevos registros, utilizando una secuencia generada previamente.

> **Figura 29:** Proceso E.T.L Dimensión Olympic NOCs

> **Figura 30:** Vista de la dimensión Olympic NOCs

---

#### 8.1.5. Proceso E.T.L: Dimensión: Olympic Medal Results

Para la dimensión Medal Result, que es estática, se optó por realizar el poblamiento utilizando Apache Hop, aunque también se podría haber hecho durante la creación de la tabla mediante código SQL. Los registros de esta dimensión representan los posibles resultados que puede obtener un atleta. El proceso fue sencillo:

1. Se generaron todos los registros que reflejan los distintos resultados posibles, como ganar una medalla de algún tipo o no, y si la modalidad fue individual o en pareja.
2. Estos registros se insertan en la base de datos. Este proceso se realiza una **única vez** debido a que es una dimensión estática.

> **Figura 31:** Proceso E.T.L Dimensión Olympic Medal Results

> **Figura 32:** Vista de la dimensión Olympic Medal Results

La dimensión contiene los siguientes registros:

| SU_RESULT | MEDAL_RESULT | FORMAT_RESULT |
|-----------|--------------|---------------|
| 1 | Gold | Individual |
| 2 | Gold | Team |
| 3 | Silver | Individual |
| 4 | Silver | Team |
| 5 | Bronze | Individual |
| 6 | Bronze | Team |
| 7 | No Medal | Individual |
| 8 | No Medal | Team |

---

#### 8.1.6. Proceso E.T.L: Tabla de hechos: Athlete Event Results

Para el proceso de carga de la tabla de hechos "Athlete Event Results", se inicia extrayendo los datos desde un archivo CSV con los resultados iniciales. Durante la transformación:

1. Se agrega la fecha del sistema para simular la fecha de inserción de cada registro, con la intención de comparar los registros con múltiples versiones para las dimensiones de tipo SCD 2.
2. Dado que algunas columnas no incluyen explícitamente la clave del resultado del atleta (indicando el tipo de medalla y si fue en equipo o individual), se normalizan estos datos para que coincidan con la dimensión estática "Medal Results".
3. Posteriormente, se seleccionan las columnas relevantes y se realiza un "lookup" en la base de datos Oracle para obtener las claves subrogadas de cada dimensión.
4. Una vez obtenidas, estas claves se incorporan como claves foráneas en la tabla de hechos para completar la carga.

> **Figura 33:** Proceso E.T.L Tabla de hechos Athlete Event Results

> **Figura 34:** Vista de la tabla de hechos Athlete Event Results

---

#### 8.1.7. Proceso E.T.L: Tabla de hechos: Olympic Medal Tally

Al igual que en el proceso ETL de la tabla de hechos anterior, la carga inicial se realizará utilizando un archivo CSV que contiene el medallero del dataset. Durante la transformación:

1. Se añadirá una fecha de inserción para permitir la comparación de versiones en las dimensiones de tipo SCD 2.
2. Se seleccionarán las columnas relevantes.
3. Se ejecutará un "database lookup" para obtener las claves subrogadas de dichas dimensiones.
4. Finalmente, estas claves se incorporarán como claves foráneas en la dimensión, estableciendo la referencia adecuada a las claves subrogadas y asegurando la consistencia en la estructura de datos.

> **Figura 35:** Proceso E.T.L Tabla de hechos Olympic Medal Tally

> **Figura 35:** Vista de la tabla de hechos Olympic Medal Tally

---

### 8.2. Definición del proceso de carga periódica

Para los procesos de carga periódica, sólo es necesario reemplazar el archivo CSV con los nuevos registros tanto para las dimensiones como para los datos de la tabla de hechos. Además es importante que el archivo CSV mantenga los mismos tipos de datos en sus columnas que los definidos en la base de datos (por ejemplo, si una columna está definida como `VARCHAR2`, los datos en el CSV deben estar en formato `STRING`).

Luego de hacer el cambio de archivo CSV con los nuevos registros y de asegurarse el tipo de dato de las columnas, se ejecutará un **workflow** que ejecutará cada pipeline con los nuevos registros, actualizando o insertando las dimensiones y luego realizando la inserción en la tabla de hechos.

> **Figura 36:** Workflow para la carga incremental

---

### 8.3. Definición de la periodicidad de las cargas

Dado que los Juegos Olímpicos se celebran **cada cuatro años**, la carga de datos debe realizarse con la misma periodicidad, comenzando el primer año posterior a cada edición. Esto asegura que los datos y resultados estén completos y correctamente verificados antes de su incorporación a la base de datos.

---

## 9. Testing sobre la base de datos

Después de cargar los datos, se realizan consultas para verificar la integridad de la información, con el fin de responder algunas preguntas de investigación planteadas al inicio del proyecto.

---

### 9.1. Evolución de las participaciones de atletas femeninas en los Juegos Olímpicos

*Figura 37: Código SQL: Consulta: Evolución de atletas femeninas*

```sql
SELECT
    ga.edition_year,
    COUNT(DISTINCT ft.fk_athlete) AS n_mujeres_particpantes
FROM fact_athlete_event_results ft
JOIN dim_olympic_games ga       ON (ft.fk_edition = ga.su_edition)
JOIN dim_olympic_athlete_bio at ON (ft.fk_athlete = at.su_athlete)
WHERE at.athlete_sex = 'Female'
GROUP BY ga.edition_year
ORDER BY ga.edition_year;
```

> **Figura 38:** Vista de la consulta Evolución de atletas femeninas

---

### 9.2. Los deportes han experimentado un aumento o disminución en el número de participantes

*Figura 39: Código SQL: Consulta: Deportes en aumento o disminución*

```sql
SELECT
    ev.event_sport AS sport,
    COUNT(CASE WHEN ga.edition_year BETWEEN 1896 AND 1924 THEN 1 END) AS "1896-1924",
    COUNT(CASE WHEN ga.edition_year BETWEEN 1924 AND 1952 THEN 1 END) AS "1924-1952",
    COUNT(CASE WHEN ga.edition_year BETWEEN 1952 AND 1980 THEN 1 END) AS "1952-1980",
    COUNT(CASE WHEN ga.edition_year BETWEEN 1980 AND 2008 THEN 1 END) AS "1980-2008",
    -- Columna de diferencia (Más arriba = Mayor aumento, Más abajo = Mayor disminución)
    (COUNT(CASE WHEN ga.edition_year BETWEEN 1980 AND 2008 THEN 1 END) -
     COUNT(CASE WHEN ga.edition_year BETWEEN 1896 AND 1924 THEN 1 END)) AS diff
FROM fact_athlete_event_results ft
JOIN dim_olympic_events ev  ON ft.fk_event   = ev.su_event
JOIN dim_olympic_games  ga  ON ft.fk_edition = ga.su_edition
WHERE ev.event_sport IS NOT NULL
GROUP BY ev.event_sport
ORDER BY diff DESC;
```

> **Figura 40:** Vista de la consulta Deportes en aumento o disminución

---

### 9.3. Cómo ha evolucionado el rendimiento de los atletas chilenos en los Juegos Olímpicos

*Figura 41: Código SQL: Consulta: Evolución de atletas chilenos*

```sql
SELECT
    '1896-1930' AS "Year Range",
    SUM(fa.gold)   AS gold,
    SUM(fa.silver) AS silver,
    SUM(fa.bronze) AS bronze,
    SUM(fa.total)  AS total
FROM fact_olympic_medal_tally fa
JOIN dim_olympic_nocs  no ON (fa.fk_noc     = no.su_noc)
JOIN dim_olympic_games ga ON (fa.fk_edition = ga.su_edition)
WHERE no.country_name LIKE 'Chile'
  AND ga.edition_year BETWEEN 1896 AND 1930

UNION ALL

SELECT
    '1930-1960' AS "Year Range",
    SUM(fa.gold)   AS gold,
    SUM(fa.silver) AS silver,
    SUM(fa.bronze) AS bronze,
    SUM(fa.total)  AS total
FROM fact_olympic_medal_tally fa
JOIN dim_olympic_nocs  no ON (fa.fk_noc     = no.su_noc)
JOIN dim_olympic_games ga ON (fa.fk_edition = ga.su_edition)
WHERE no.country_name LIKE 'Chile'
  AND ga.edition_year BETWEEN 1930 AND 1960

UNION ALL

SELECT
    '1960-2024' AS "Year Range",
    SUM(fa.gold)   AS gold,
    SUM(fa.silver) AS silver,
    SUM(fa.bronze) AS bronze,
    SUM(fa.total)  AS total
FROM fact_olympic_medal_tally fa
JOIN dim_olympic_nocs  no ON (fa.fk_noc     = no.su_noc)
JOIN dim_olympic_games ga ON (fa.fk_edition = ga.su_edition)
WHERE no.country_name LIKE 'Chile'
  AND ga.edition_year BETWEEN 1960 AND 2008;
```

*Figura 42: Vista de la consulta Evolución de atletas chilenos*

| Year Range | GOLD | SILVER | BRONZE | TOTAL |
|------------|------|--------|--------|-------|
| 1896-1930 | 0 | 1 | 0 | 1 |
| 1930-1960 | 0 | 4 | 2 | 6 |
| 1960-2024 | 2 | 2 | 2 | 6 |

---

## 10. Conclusión

Durante la fase 2, no fue necesario realizar correcciones en el diseño multidimensional establecido en la fase 1, lo que permitió dedicar más tiempo al proceso de implementación y a las operaciones de extracción, transformación y carga (ETL) del Data Mart. Sin embargo, surgieron algunos problemas durante la transformación de datos, especialmente en la carga de dimensiones y tablas de hechos.

**Problema 1 — Datos faltantes en dimensiones:** Algunos datos referenciados en la tabla de hechos no estaban presentes en ciertas dimensiones para su carga inicial. Para solucionar este problema, se creó un registro con un valor especial que indica que no hay información disponible para esos registros dentro de la dimensión.

**Problema 2 — Valores nulos no reconocidos:** Al transformar los datos de los Juegos Olímpicos, el transformador "Null If" no pudo reconocer los valores nulos en el conjunto de datos. Para solucionar este inconveniente, se utilizó el "Value Mapper" para gestionar esos nulos de manera más específica.

**Problema 3 — Conexión a Oracle con fechas:** Otro desafío importante fue la configuración de la conexión a la base de datos Oracle correctamente. Al intentar obtener las fechas (`date_from` y `date_to`) mediante el "Database Lookup", el software devolvía valores nulos para esas columnas. Este problema se resolvió al habilitar la opción **"Supports the Timestamp data type"** dentro de Apache Hop, que estaba desactivada inicialmente.

---

## 11. Bibliografía

1. Olympic Historical Dataset (1896 - 2022). (2024b, agosto 6). *Kaggle*. https://www.kaggle.com/datasets/muhammadehsan02/126-years-of-historical-olympic-dataset
2. Olympedia – main page. (s. f.). https://www.olympedia.org
3. Olympics | Olympic Games, medals, results & latest news. (s. f.). https://olympics.com
4. Pandas Development Team. (n.d.). *Pandas documentation*. Retrieved August 20, 2024, from https://pandas.pydata.org/docs/index.html
5. Matplolib. (n.d.). *Matplotlib documentation — Matplotlib 3.9.2 documentation*. (s. f.). https://matplotlib.org/stable/index.html
6. ANOC. (2024, September 10). https://www.anocolympic.org
7. Apache Hop. *Apache Hop Transform Plugins documentation*. https://hop.apache.org/manual/latest/pipeline/transforms.html

---

*Fase 2: Rodrigo Suaña, Eduardo Apata, Jorge Gutiérrez, Iván Callasaya*
