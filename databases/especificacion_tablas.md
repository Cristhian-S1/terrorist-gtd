# Inteligencia de Negocios

---

## Figura 21. Diagrama estrella del Data Mart

*(Ver diagrama en el documento original — página 46)*

---

## 5.2. Descripción de las Dimensiones

### 5.2.1. Dimensión Tiempo

**Tabla 10. Descripción de la Dimensión Tiempo**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Tiempo | fecha_sk | number(38) | (12 dígitos: YYYYMMDDXXXX) | Surrogate key de la dimensión tiempo, es un entero con formato de fecha fija |
| | iyear | number(38) | | Año en que ocurrió el incidente. |
| | imonth | number(38) | (1-12; 0 si es desconocido) | Mes del incidente. |
| | iday | number(38) | (1-31; 0 si es desconocido) | Día del incidente. |

**Tipo de dimensión: SCD Tipo 1**

Se opta por este tipo debido a que los datos del año, el mes y el día de cada atentado, no se necesita agregar un nuevo registro, por lo que solo se debe sobreescribir el dato correspondiente y estos no cambian constantemente.

**Jerarquía**

El tiempo puede ordenarse jerárquicamente de la siguiente forma:

```
iyear => imonth => iday
```

---

### 5.2.2. Dimensión Lugar

**Tabla 11. Descripción de la Dimensión Lugar**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Lugar | lugar_sk | number(38) | | Surrogate key de la dimensión lugar |
| | valid | number(1) | | Indica validez de la versión |
| | valid_from | Date | | Indica la fecha cuando el registro comenzó a ser válido |
| | valid_to | Date | | Indica la fecha cuando el registro dejó de ser válido |
| | version | number(38) | | Indica la versión de la fila |
| | country | number(38) | | Indica el país donde ocurrió el incidente mediante un código siguiendo estándares internacionales |
| | country_txt | varchar2(255) | | País donde ocurrió el evento |
| | region | number(38) | {1-12} | Código de la región geográfica mayor |
| | region_txt | varchar2(255) | | Nombre de la región geográfica donde ocurrió el incidente terrorista |
| | provstate | varchar2(255) | | Nombre de la unidad administrativa subnacional de primer orden (provincia, estado, región) |
| | city | varchar2(255) | | Nombre de la ciudad, pueblo o aldea donde ocurrió el incidente. |

**Tipo de dimensión: SCD Tipo 2**

Se opta por este tipo debido a que los apartados de `valid_from` y `valid_to`, fueron los indicadores de la validez cuando el registro comenzó a ser válido y cuando no. Igualmente como el atributo de versión, en el cual si un país cambia una región, no se borra la historia, se debe realizar una nueva fila con una nueva versión y actualizar las fechas de valid. De forma que los atentados antiguos mantengan su integridad.

**Jerarquía**

La jerarquía permite tener el conocimiento de la ciudad en la que ocurrió el atentado, siendo esta una jerarquía estricta, debido a que una ciudad pertenece a una sola región y una sola ciudad pertenece a una sola provincia.

```
country => region => provstate => city
```

---

### 5.2.3. Dimensión Especificación Lugar

**Tabla 12. Descripción de la Dimensión Especificación Lugar**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Especificación Lugar | spec_lugar_sk | number(38) | {1-16} | Surrogate Key de la dimensión especificación lugar. |
| | vicinity | number(1) | {1, 0} U {-9} | Indica si el ataque ocurrió fuera de los límites de la ciudad. |
| | specify | number(38) | {1-5} U {-1} | Nivel de precisión de las coordenadas. |
| | specify_txt | varchar2(255) | | Descripción textual del nivel de precisión de las coordenadas. |

**Tipo de dimensión: SCD Tipo 1**

Se opta por este tipo debido a que los atributos de especificación geográfica no requieren el mantenimiento de un historial de cambios. Al presentarse una modificación, se procede a la actualización directa del registro.

**Jerarquía**

No aplica.

---

### 5.2.4. Dimensión Ataque

**Tabla 13. Descripción de la Dimensión Ataque**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Ataque | ataque_sk | number(38) | {1-185} | Surrogate Key de la dimensión ataque |
| | attacktype1 | number(38) | {1,9} | Código numérico que identifica el método principal de ataque según la jerarquía de la GTD. |
| | attacktype1_txt | varchar2(255) | | Descripción textual del método de ataque |
| | attacktype2 | number(38) | {1,9} U {-1} | Código numérico del segundo método de ataque si el incidente involucró una secuencia de eventos. |
| | attacktype2_txt | varchar2(255) | | Descripción textual del segundo método de ataque. |
| | attacktype3 | number(38) | {1,7} U {-1} | Código numérico del tercer método de ataque en incidentes complejos. |
| | attacktype3_txt | varchar2(255) | | Descripción textual del tercer método de ataque. |
| | success | number(1) | {0,1} | Define el éxito según los efectos tangibles del ataque. |
| | suicide | number(1) | {0,1} | Indica si existe evidencia de que el perpetrador no pretendía escapar con vida del ataque. |

**Tipo de dimensión: SCD Tipo 1**

Se opta por este tipo debido a que las características y atributos no cambian con el tiempo, pero si se llega a encontrar un error, puede ser que se descubrió un error en el registro original; solo se sobreescribe el dato incorrecto por el correcto.

**Jerarquía**

No aplica, debido a que no posee ningún nivel que pertenezca a otro.

---

### 5.2.5. Dimensión Armas

**Tabla 14. Descripción de la Dimensión Armas**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Armas | armas_sk | number(38) | {1-62} | Surrogate Key de la dimensión armas |
| | weaptype | number(38) | {1-3} U {5-13} U {-1} | Código numérico (1-13) de la categoría del arma principal utilizada. |
| | weaptype_txt | varchar2(255) | | Descripción textual de la categoría del arma principal (ej. Firearms). |
| | weapsubtype | number(38) | {1-24} U {26-31} U {-1} | Código numérico del subtipo específico del arma principal. |
| | weapsubtype_txt | varchar2(255) | | Descripción textual del subtipo de arma (ej. Automatic Rifle). |

**Tipo de dimensión: SCD Tipo 1**

Se opta por este tipo debido a que los atributos de las armas son estáticos. En caso de detectarse discrepancias o errores en el registro original, se procede a la corrección directa del dato para mantener la integridad de la información actual sin generar registros históricos adicionales.

**Jerarquía**

La jerarquía permite obtener la categoría general del arma con el subtipo específico.

```
weaptype => weapsubtype
```

---

### 5.2.6. Dimensión Detalles

**Tabla 15. Descripción de la Dimensión Detalles**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Detalles | detalle_sk | number(38) | {1-49} | Surrogate Key de la dimensión detalles |
| | crit1 | number(38) | {0,1} | Indica si el incidente tuvo como objetivo alcanzar una meta política, económica, religiosa o social. |
| | crit2 | number(38) | {0,1} | Indica si hubo evidencia de una intención de coaccionar, intimidar o enviar un mensaje a una audiencia más amplia que las víctimas directas. |
| | crit3 | number(38) | {0,1} | Indica si la acción estuvo fuera del contexto de las actividades de guerra legítimas (viola el derecho internacional humanitario). |
| | doubtterr | number(38) | {0,1}, {-9} | Indica si existe alguna duda sobre si el incidente es realmente un acto de terrorismo según la definición de la GTD. |
| | alternative | number(38) | {1-5} U {-1} | Describe la naturaleza de la duda o proporciona una clasificación alternativa para el incidente si no es puramente terrorismo. |
| | alternative_txt | varchar2(255) | | Identifica la categorización más probable del incidente, aparte del terrorismo. |
| | multiple | number(1) | {0,1} | Indica si el incidente forma parte de una serie de ataques múltiples conectados que ocurrieron en un periodo corto y la misma zona. |

**Tipo de dimensión: Junk Dimension**

Se agrupan banderas binarias de baja cardinalidad sobre los criterios de clasificación terrorista, los cuales son `crit1`, `crit2`, `crit3`, `doubtterr`, `multiple`, ya que las 49 filas son combinaciones pre-calculadas.

**Jerarquía**

No aplica, debido a que los campos de crit1 al 3, doubtterr y multiple son indicadores independientes entre ellos. No representan un nivel de detalle.

---

### 5.2.7. Dimensión Detalles Adicionales

**Tabla 16. Descripción de la Dimensión Detalles Adicionales**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Detalles adicionales | detalles_a_sk | number(38) | {1-11} | Surrogate Key de la dimensión detalles adicionales |
| | int_log | number(38) | {0,1} U {-9} | Indica si el incidente fue de carácter logístico internacional |
| | int_log_txt | varchar(255) | | Información textual del atributo int_log |
| | int_misc | number(38) | {0,1} U {-9} | Indica si existen otros factores misceláneos que sugieran una dimensión internacional en el ataque. |
| | int_misc_txt | varchar(255) | | Información textual del atributo int_misc |
| | int_any | number(38) | {0,1} U {-9} | Variable resumen que indica si el incidente tiene cualquier dimensión internacional basada en los tres criterios anteriores |
| | int_any_txt | varchar(255) | | Información textual del atributo int_any |

**Tipo de dimensión: Junk Dimension**

Se agrupan los tres indicadores ternarios de dimensión internacional del ataque, donde solo 11 combinaciones son posibles.

**Jerarquía**

No aplica. Debido a que los indicadores, los que son considerados como booleanos, describen diferentes facetas de la logística del ataque, por lo que simplemente se usan para filtrar o agrupar, no para navegar de un nivel superior a uno inferior.

---

### 5.2.8. Dimensión Grupo Perpetrador

**Tabla 17. Descripción de la Dimensión Perpetrador**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Perpetrador | grupo_sk | number(38) | | Surrogate Key de la dimensión grupo |
| | compclaim | number(1) | {-1-1} U {-9} | Indica si hubo atribuciones de responsabilidad contradictorias por parte de diferentes grupos. |
| | motive | CLOB | | Descripción detallada de la motivación específica o el objetivo político/social perseguido con el ataque. |

**Tipo de dimensión: SCD Tipo 1**

Esta dimensión está conectada directamente a la tabla de hechos y contiene la motivación narrativa, además de contener la información de si hubo atribuciones contradictorias.

**Jerarquía**

No aplica. Debido a que los atributos `compclaim` y `motive` describen independientemente el mismo evento o grupo, por lo que no existe una relación para navegar de un nivel superior a inferior.

---

### 5.2.9. Dimensión Grupo BT Perpetrador

**Tabla 18. Descripción de la Dimensión BT Perpetrador**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| BT Perpetrador | grupo_fk | number(38) | | Indica al grupo que se relaciona una instancia de participación del perpetrador especificado en este registro |
| | perp_fk | number(38) | | Indica el perpetrador que participa en el evento terrorista dentro de la instancia de grupo especificada en este registro |
| | guncertain | number(1) | {-1,1} | Indica si la información reportada por las fuentes sobre el/los grupo(s) perpetrador(es) se basa en especulaciones o en dudosas atribuciones de responsabilidad. |
| | claimed | number(1) | {-1, 1} U {-9} | Indica si un grupo o individuo se atribuyó la responsabilidad del ataque. |
| | mcr_fk | number(38) | {1-11} | Referencia al modo utilizado en la reclamación de responsabilidad usada sobre el perpetrado. |

**Tipo de dimensión: SCD Tipo 1**

Debido a que la participación de un grupo en un evento específico del pasado —si reclamaron o no la autoría— es un dato histórico que no cambia. Además, si este se llegara a cambiar en un futuro, simplemente se sobreescribe.

**Jerarquía**

No aplica. Debido a que sus campos, llaves foráneas, apuntan a otras tablas, y sus atributos son indicadores booleanos sobre si los grupos reclamaron la autoría del ataque.

---

### 5.2.10. Dimensión Perpetrador

**Tabla 19. Descripción de la Dimensión Perpetrador**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Perpetrador | perp_sk | number(38) | | Surrogate Key de la dimensión perpetrador |
| | gname | varchar2(512) | | Nombre del grupo u organización que llevó a cabo el incidente. |
| | gsubname | varchar2(512) | | Subunidad, facción o nombre específico de la célula del grupo responsable. |

**Tipo de dimensión: SCD Tipo 1 y Outrigger**

Los nombres de grupos terroristas son estables y es referenciada por la dimensión de grupo de perpetradores.

**Jerarquía**

El grupo principal apunta a la subunidad específica.

```
gname => gsubname
```

---

### 5.2.11. Dimensión Mode For Claim Responsability

**Tabla 20. Descripción de la Dimensión Mode For Claim Responsability**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| MCR | mcr_sk | number(38) | {1-11} | Surrogate Key de la dimensión mcr |
| | claimmode | number(38) | {1-10} U {-1} | Método o vía utilizada para realizar la atribución del ataque. |
| | claimmode_txt | varchar2(255) | | Detalle textual del atributo claimmode |

**Tipo de dimensión: Estática y Outrigger**

Es referenciada por la dimensión de grupo de perpetradores y es un catálogo fijo de modos de reclamación.

**Jerarquía**

No aplica.

---

### 5.2.12. Dimensión Objetivo

**Tabla 21. Descripción de la Dimensión Objetivo**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Objetivo | objetivo_sk | number | | Surrogate Key de la dimensión objetivo |
| | targtype | number | number(38,0) | Código de la categoría del objetivo principal (1-22). |
| | targtype_txt | varchar2 | varchar2(255) | Descripción del objetivo (ej. Police, Government). |
| | targsubtype | number | number(38,0) | Código del subtipo de objetivo principal. |
| | targsubtype_txt | varchar2 | varchar2(255) | Descripción del subtipo (ej. Police Checkpoint). |
| | corp1 | varchar2 | varchar2(255) | Nombre de la entidad o corporación principal. |
| | target1 | varchar2 | varchar2(512) | Persona o instalación específica atacada. |
| | natlty1 | number | number(38,0) | Código de nacionalidad de la víctima principal. |
| | natlty1_txt | varchar2 | varchar2(255) | Nombre de la nacionalidad principal. |

**Tipo de dimensión: SCD Tipo 1**

La tabla de hechos referencia hasta 3 objetivos (`fk_obj1`, `fk_obj2`, `fk_obj3`), pero cada registro de objetivo es una clasificación estable.

**Jerarquía**

```
targtype => targsubtype
```

---

### 5.2.13. Dimensión Impacto

**Tabla 23. Descripción de la Dimensión Impacto**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Impacto | impacto_sk | number(38) | {1-37} | Surrogate Key de la dimensión impacto |
| | property | number(38) | {0,1} U {-9} | Indica si existe evidencia de daños a la propiedad como resultado del incidente. |
| | propextent | number(38) | {-1,2,3,4,7} | Si el campo "Property Damage?" es "Yes", describe la magnitud de los daños materiales causados. |
| | propextent_txt | varchar2(255) | | Descripción textual de la magnitud de los daños materiales causados. |
| | ishostkid | number(38) | {0,1} U {-9} | Aparece "Yes" si hay evidencia de que se tomaron rehenes o se realizó un secuestro en el incidente. |
| | hostkidoutcome | number(38) | {1-7} U {-1} | Resultado final para los rehenes o víctimas del secuestro. |
| | hostkidoutcome_txt | varchar2(255) | | Descripción textual del resultado final para los rehenes o víctimas del secuestro. |

**Tipo de dimensión: Junk Dimension**

Agrupa indicadores de baja cardinalidad sobre daño material y resultado de rehenes; existen 37 filas pre-calculadas.

**Jerarquía**

No aplica. Esto debido a que no se poseen campos que dependan de otros.

---

## 5.3. Descripción de la Tabla de Hechos

La tabla de hechos presentada en este modelo es de tipo **event fact**, está representa eventos o sucesos ocurridos en el mundo contemporáneo. En este caso, los eventos modelados son los ataques terroristas ocurridos alrededor del mundo.

**Tabla 24. Tabla de Hechos Incidente Terrorista**

| Dimensión | Atributo | Tipo | Valores Admitidos | Descripción |
|-----------|----------|------|-------------------|-------------|
| Incidente Terrorista | event_id | number(38) | (12 dígitos: YYYYMMDDXXXX) | Identificador único del evento |
| | latitude | float(126) | | Coordenadas de latitud basadas en estándares WGS1984 de la ciudad en la que ocurrió el evento |
| | longitude | float(126) | | Coordenadas de la longitud basada en estándares WGS1984 de la ciudad en la que ocurrió el evento |
| | extend | number(1) | {0,1} | Indica si el incidente se extendió por más de 24 horas. |
| | nperps | number(38) | | Número total de perpetradores que participaron en el incidente. |
| | nperpcap | number(38) | | Número de perpetradores que fueron capturados o detenidos tras el ataque. |
| | individual | number(38) | {0,1} | Indica si el ataque fue perpetrado por un individuo o por varios individuos |
| | nkill | number(38) | | Número total de muertes confirmadas en el incidente, incluyendo víctimas y atacantes. |
| | nkillus | number(38) | | Número de ciudadanos estadounidenses que murieron como resultado del incidente, incluyendo tanto a víctimas como a perpetradores. |
| | nkillter | number(38) | | Número total de muertes confirmadas de perpetradores en el incidente. |
| | nwound | number(38) | | Número total de heridos no fatales confirmados en el incidente. |
| | nwoundus | number(38) | | Número de ciudadanos estadounidenses que sufrieron heridas no fatales confirmadas en el incidente, incluyendo tanto a víctimas como a perpetradores. |
| | nwoundte | number(38) | | Número de perpetradores que sufrieron heridas no fatales confirmadas en el incidente. |
| | propvalue | float(126) | | Valor estimado de los daños a la propiedad. |
| | nhostkid | number(38) | | Número total de rehenes o víctimas de secuestro en el incidente. |
| | nhostkidus | number(38) | | Número de ciudadanos estadounidenses tomados como rehenes o secuestrados. |
| | nhours | number(38) | | Número de horas que los rehenes estuvieron retenidos |
| | ndays | number(38) | | Número de días que los rehenes estuvieron retenidos. |
| | ransomamt | float(126) | | Monto exacto del rescate solicitado en dólares estadounidenses. |
| | ransomamtus | float(126) | | Monto del rescate solicitado específicamente a fuentes o ciudadanos de EE. UU. |
| | ransompaid | float(126) | | Monto exacto del rescate que fue finalmente pagado. |
| | ransompaidus | float(126) | | Monto del rescate pagado por fuentes o ciudadanos de EE. UU. |
| | nreleased | number(38) | | Número de rehenes que fueron liberados sanos y salvos (o que escaparon/fueron rescatados). |
| | fk_detalles | number(38) | {1-23} U {25-49} | Referencia a la clave primaria de la dimensión detalles. |
| | fk_fecha_ini | number(38) | | Referencia a la tabla de dimensión de tiempo, fecha_sk |
| | fk_fecha_res | number(38) | | Referencia a la dimensión de tiempo, fecha_sk |
| | fk_lugar | number(38) | | Referencia a la dimensión de lugar, su clave primaria lugar_sk. |
| | fk_lugar_spec | number(38) | {1-16} | Referencia a la dimensión de especificación del lugar. |
| | fk_ataque | number(38) | | Referencia a la dimensión de ataque, clave primaria ataque_sk. |
| | fk_arma1 | number(38) | | Referencia a la dimensión arma. |
| | fk_arma2 | number(38) | | Referencia a la dimensión arma. |
| | fk_arma3 | number(38) | | Referencia a la dimensión arma |
| | fk_obj1 | number(38) | | Referencia a la dimensión de objetivo, objetivo_sk. |
| | fk_perpg | number(38) | | Referencia a la dimensión grupo perpetrador |
| | fk_impacto | number(38) | {1-37} | Referencia a la dimensión impacto. |
| | fk_detalles_adicionales | number(38) | {1-11} | Referencia a la dimensión detalles adicionales. |
| | fk_arma4 | number(38) | | Referencia a la dimensión arma. |
| | fk_obj2 | float(126) | | Referencia a la dimensión objetivo. |
| | fk_obj3 | float(126) | | Referencia a la dimensión objetivo |
