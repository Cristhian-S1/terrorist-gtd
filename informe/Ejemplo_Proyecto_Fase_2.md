# Inteligencia de Negocios

## 5. Implementación del Datawarehouse y proceso ETL

### 5.1. Definición del proceso de carga inicial

#### 5.1.1. Dimensión "Time"

Para la dimensión estática "Time", se optó por crearla a través de procedimientos almacenados y funciones de SQL en Oracle. Primero, se creó una tabla temporal `TEMP_TIME` que almacenará las fechas que se usarán para la dimensión de tiempo. En el segmento de código a continuación se muestra el procedimiento utilizado.

```sql
CREATE TABLE temp_time(
    dt DATE
);

CREATE OR REPLACE PROCEDURE temp_time_poblation
( start_date IN DATE,
  end_date IN DATE DEFAULT CURRENT_DATE )
AS
BEGIN
    INSERT INTO temp_time
    SELECT start_date + level - 1 dt FROM dual
    CONNECT BY LEVEL <= (end_date - start_date + 1);
END temp_time_poblation;
```

Se ejecuta el procedimiento para crear fechas en un rango de 50 años, y se ve su resultado realizando un SELECT (véase Figura 10):

```sql
BEGIN
    temp_time_poblation(date'1982-01-01', date'2032-12-31');
END;

SELECT * FROM TEMP_TIME tt;
```

> **Figura 10:** Consulta tabla TEMP_TIME

---

Se crea la tabla de la dimensión "Time" y las funciones para comprobar si una fecha específica corresponde a un fin de semana y si el año es bisiesto:

```sql
CREATE TABLE time (
    timeKey       NUMBER(8),
    fullDate      DATE,
    dayOfWeek     NUMBER(1),
    dayOfWeekDesc VARCHAR2(10),
    dayOfMonth    NUMBER(2),
    dayOfYear     NUMBER(3),
    weekOfYear    NUMBER(2),
    monthOfYear   NUMBER(2),
    monthDesc     VARCHAR2(10),
    year          NUMBER(4),
    isWeekend     CHAR(1),
    isLeapYear    CHAR(1)
);

CREATE OR REPLACE FUNCTION is_weekend
( date_par IN DATE )
RETURN CHAR
AS
    day_num NUMBER;
BEGIN
    day_num := TO_NUMBER(TO_CHAR(date_par - 1, 'D'));
    IF day_num >= 6 THEN
        RETURN '1';
    ELSE
        RETURN '0';
    END IF;
END is_weekend;

CREATE OR REPLACE FUNCTION is_leapYear
( date_par IN DATE )
RETURN CHAR
AS
    year_num NUMBER;
BEGIN
    year_num := TO_NUMBER(TO_CHAR(date_par, 'YYYY'));
    IF MOD(year_num, 4000) = 0 THEN
        RETURN '1';
    ELSIF MOD(year_num, 1000) = 0 THEN
        RETURN '0';
    ELSIF MOD(year_num, 4) = 0 THEN
        RETURN '1';
    ELSE
        RETURN '0';
    END IF;
END is_leapYear;
```

Finalmente, se realiza el poblamiento de la dimensión "Time" con las fechas de la tabla temporal `TEMP_TIME`. Los resultados se reflejan en la Figura 11:

```sql
INSERT INTO time
SELECT
    TO_NUMBER(TO_CHAR(dt, 'YYYYMMDD'))                       timekey,
    dt                                                        fullDate,
    TO_NUMBER(TO_CHAR(dt - 1, 'D'))                          dayOfWeek,
    TO_CHAR(dt, 'fmDay', 'nls_date_language = English')      dayOfWeekDesc,
    TO_NUMBER(TO_CHAR(dt, 'DD'))                             dayOfMonth,
    TO_NUMBER(TO_CHAR(dt, 'DDD'))                            dayOfYear,
    TO_NUMBER(TO_CHAR(dt, 'IW'))                             weekOfYear,
    TO_NUMBER(TO_CHAR(dt, 'MM'))                             monthOfYear,
    TO_CHAR(dt, 'Month')                                     monthDesc,
    TO_NUMBER(TO_CHAR(dt, 'YYYY'))                           year,
    is_weekend(dt)                                           isWeekend,
    is_leapYear(dt)                                          isLeapYear
FROM
    TEMP_TIME;

SELECT * FROM "TIME" t;
```

> **Figura 11:** Vista tabla dimensión "Time"

---

#### 5.1.2. Dimensión "Competition"

La transformación inicia con la recopilación de información de continentes y países mediante la unión de dos archivos TSV (Continents y Countries), seguida por su unión con los datos de competiciones y la selección y eliminación de atributos no deseados. Posteriormente, dado que se trata de una SCD tipo 1, se buscan registros con el mismo identificador. Si existen, se actualizan; de lo contrario, se utiliza el paso "Add Sequence" para obtener una nueva clave sustituta para el nuevo registro.

> **Figura 12:** Transformación dimensión "Competition"

> **Figura 13:** Previsualización dimensión "Competition"

---

#### 5.1.3. Dimensión "Person"

La carga de datos comienza cargando el archivo TSV, seguida por el formateo del string de países para obtener el continente, convirtiéndolo de la forma `_Continente` a `Continente`. A continuación, se procede a ordenar los datos según el ID del país para realizar el join entre las dos tablas. Posteriormente, en el paso "Select values", se lleva a cabo la renombración y el descarte de atributos. Finalmente, los datos se cargan en la dimensión utilizando "Dimension lookup/update", ya que se trata de un SCD Tipo 2. Esto permite la actualización del registro en caso de existir previamente, así como el manejo de las versiones correspondientes. Una muestra de la dimensión poblada se puede observar en la Figura 15.

> **Figura 14:** Transformación dimensión "Person"

> **Figura 15:** Previsualización dimensión "Person"

---

#### 5.1.4. Dimensión "Event"

El proceso de carga de la dimensión "Event" se inicia con la lectura del archivo correspondiente, seguida de un lookup en la dimensión para identificar registros existentes o nuevos. En el primer caso, los registros simplemente se actualizan, dado que se trata de una SCD tipo 1. Si no se encuentran registros existentes, se genera una nueva surrogate key mediante el paso "Add Sequence", y luego se cargan los nuevos registros. La Figura 17 muestra la dimensión poblada.

> **Figura 16:** Transformación dimensión "Event"

> **Figura 17:** Previsualización dimensión "Event"

---

#### 5.1.5. Dimensión "Format"

La dimensión Format conserva todos sus atributos originales, además de una surrogate key, por lo que su proceso de carga consiste en tres pasos: lectura del archivo TSV, cálculo de la surrogate key y finalmente carga de los registros. Dado que es una dimensión estática, solo se cargan los registros una vez. La Figura 19 muestra todos los registros cargados en la dimensión.

> **Figura 18:** Transformación dimensión "Format"

> **Figura 19:** Previsualización dimensión "Format"

---

#### 5.1.6. Dimensión "RoundType"

Similar a la dimensión "Event", debido a ser una dimensión SCD tipo 1, se procede a cargar el archivo TSV, se realiza una búsqueda de registros que coincidan con su ID. En caso afirmativo, se actualizan los registros existentes; en el otro caso, se calcula la surrogate key y se cargan los nuevos registros. La Figura 21 muestra la dimensión poblada.

> **Figura 20:** Transformación dimensión "RoundType"

> **Figura 21:** Previsualización dimensión "RoundType"

---

#### 5.1.7. Tabla de hechos "Results"

Para la creación de la tabla de hechos, el primer JOIN es entre el archivo que contiene los resultados de todas las competencias realizadas y las dimensiones "Time" y "Competitions". Se puede apreciar en la Figura 22 que se carga un archivo Competitions ya que este contiene las fechas en que se celebraron las competencias (la dimensión no las tiene), el cual se le realiza tres **Stream lookups** para obtener las claves surrogadas de las fechas de inicio y de término, y de la `competitionId`.

> **Figura 22:** Carga dimensión "Time" y "Competitions"

Siguiendo con la Figura 23, se carga el archivo "Results" y ordena por `competitionId` para realizar un **Merge Join** con las dimensiones mencionadas con anterioridad y en el paso **Select values** se descartan las columnas que no se necesitan para la tabla de hechos (columnas de las dimensiones). Este ciclo se repite por cada ID y dimensión restantes de la tabla de resultados. Al finalizar el proceso, la tabla obtenida se sube a la tabla "Results" en la base de datos (Figura 24).

> **Figura 23:** Creación tabla de hechos "Results", parte 1

> **Figura 24:** Creación tabla de hechos "Results", parte 2

Y realizamos la consulta para visualizar nuestra tabla de hechos (Figura 25):

> **Figura 25:** Vista tabla de hechos "Results"

---

### 5.2. Definición del proceso de carga periódica

Para las dimensiones lentamente cambiantes (Competition, Person, Event y RoundType) se les asignó una secuencia a cada una en la base de datos Oracle para la asignación de surrogate keys en caso de adición de nuevos registros y al ser en su mayoría de tipo uno no requerían de pasos adicionales más que actualizar e insertar. Para la dimensión SCD de tipo dos (Person) se crean tres campos adicionales para mantener la fecha de validez y la versión que tiene, lo que sería equivalente a las veces que ha cambiado.

---

### 5.3. Definición de la periodicidad de las cargas

La WCA actualiza su base de datos al final de cada semana, tras las competiciones realizadas, lo que implica que el proceso de carga se llevará a cabo de forma **semanal**.

---

### 5.4. Consultas de prueba a DW

Una vez cargadas las dimensiones y la tabla de hechos, se realizaron algunas consultas para poner a prueba el data warehouse implementado y si es posible responder, o al menos realizar un acercamiento, a las preguntas planteadas al inicio del proyecto.

#### 5.4.1. Cantidad de competencias por cada evento a través de los años

```sql
SELECT t."YEAR", e.NAME, COUNT(DISTINCT r.FK_COMPETITION) AS num_competitions
FROM EVENT e
JOIN RESULTS r
    ON (r.FK_EVENT = e.SU_EVENT)
JOIN "TIME" t
    ON (r.START_DATE = t.TIMEKEY)
GROUP BY t."YEAR", e.NAME
ORDER BY t."YEAR" DESC;
```

> **Figura 26:** Consulta de prueba 1

---

#### 5.4.2. Competencias con mayor número de participantes

```sql
SELECT t."YEAR", c.NAME AS competition, COUNT(DISTINCT r.FK_PERSON) AS num_competitors
FROM COMPETITION c
JOIN RESULTS r
    ON (r.FK_COMPETITION = c.SU_COMPETITION)
JOIN "TIME" t
    ON (r.START_DATE = t.TIMEKEY)
GROUP BY t."YEAR", c.NAME
ORDER BY COUNT(DISTINCT r.FK_PERSON) DESC;
```

> **Figura 27:** Consulta de prueba 2

---

#### 5.4.3. Países con mayor cantidad de finalistas

```sql
SELECT p.COUNTRYNAME AS country, COUNT(DISTINCT r.FK_PERSON) AS num_finalist
FROM RESULTS r
JOIN PERSON p
    ON (r.FK_PERSON = p.SU_PERSON)
JOIN ROUNDTYPE r2
    ON (r.FK_ROUNDTYPE = r2.SU_ROUNDTYPE)
WHERE r2."FINAL" = 1
GROUP BY p.COUNTRYNAME
ORDER BY COUNT(DISTINCT r.FK_PERSON) DESC;
```

> **Figura 28:** Consulta de prueba 3

---

## 6. Conclusiones

Este informe presenta una exploración de la base de datos de la WCA, que abarca desde información básica sobre los participantes hasta datos complejos que detallan los resultados de cada competición. El análisis realizado en Python permitió evaluar la profundidad y confiabilidad de la base de datos. A través de la examinación de las tablas, se identificaron diversas preguntas de investigación que abordan aspectos clave de las competiciones de cubos Rubik, como tendencias históricas, rendimiento de los competidores y ubicación geográfica de los eventos.

Con base en este análisis, se procedió con el diseño multidimensional, siguiendo el enfoque de diseño estrella. Se omitieron tablas que podían derivarse de otras, como las que mantienen los récords y las ubicaciones, con el fin de simplificar el modelo y mejorar la eficiencia en el almacenamiento y recuperación de datos. Además, se tomaron decisiones estratégicas en relación con las Slowly Changing Dimensions (SCD). Dada la naturaleza de la información, que rara vez cambia, se identificó que la mayoría de las dimensiones podrían ser fácilmente de tipo 1. Sin embargo, se reconoció la importancia de incluir al menos una dimensión de tipo 2 para experimentar y aprender, a pesar de que en términos de análisis su cambio puede ser mínimo.

Finalizado el análisis se procede a implementar el diseño en una base de datos relacional con la herramienta Pentaho Data Integration [3], del cual se puede destacar su variedad de utilidades y facilidades que brinda para realizar el poblamiento inicial y designar los pasos para actualizar registros.

---

## Referencias

1. "World Cube Association." https://www.worldcubeassociation.org/, 2024. Accedido (25-03-2024).
2. "Matplotlib — Visualization with Python." https://matplotlib.org/, 2024. Accedido (30-03-2024).
3. "Pentaho Data Integration." https://www.hitachivantara.com/pentaho/pentaho-plus-platform/data-integration-analytics.html, 2024. Accedido (02-05-2024).
4. "pandas - Python Data Analysis Library." https://pandas.pydata.org/, 2024. Accedido (30-03-2024).
5. R. Valdivia, "Presentación Diseño Multidimensional." https://sisaca.uta.cl/wwwadc/public/archivos/wwwadc/cursos/2024-1/0001502/recursos/r-5.pdf, 2023. Accedido (01-05-2024).

---

*Preparado por F. Justo V., C. Valenzuela L.*
