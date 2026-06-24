# Proyecto Inteligencia de Negocios 1/2025

**Universidad de Tarapacá**  
**Facultad de Ingeniería**  
**Departamento de Ingeniería en Computación e Informática**

*13 de marzo de 2025*

---

## 1. Datos Abiertos

El proyecto del curso de Inteligencia de Negocios se orienta al desarrollo de una solución datawarehouse que involucre el uso de datos abiertos como fuentes de datos. Un requerimiento relevante es que se debe contar con datos publicados a través de un rango de tiempo considerable (por ejemplo, tres o más años), de forma de realizar un análisis de la evolución de las características a considerar. Se espera, finalmente, que el análisis de los datos estudiados permita descubrir información relevante que se refleje en conclusiones de buen nivel.

Datos abiertos (open data) es una filosofía y práctica que persigue que determinados datos estén disponibles de forma libre a todo el mundo, sin restricciones de copyright, patentes u otros mecanismos de control.

Para este proyecto se decidio escoger la base de datos Global Terrorism Database (GTD)

## 2. Informes y Presentaciones

El proyecto se deberá realizar en cuatro fases considerando los siguientes aspectos:

### 2.1. Fase 0 — Fuentes de Datos (completada)

- **Introducción.** Contexto y planteamiento del problema, organizaciones involucradas.
- **Objetivos.** Objetivo general y específicos del proyecto.
- **Fuentes de Datos.** Descripción de la (o las) fuente(s) de dato(s), incluyendo documentos, tablas, atributos, valores admisibles. Análisis inicial vía R, Python Pandas, Excel, SPSS.
- **Preguntas de Investigación.**
- **Conclusiones.**

### 2.2. Fase I — Diseño Multidimensional (completada)

- Informe anterior corregido.
- **Diseño Multidimensional.** Diagrama del Esquema Estrella (o Copo de Nieve) de su solución DataMart.
  - Descripción de las dimensiones, sus atributos y su clave. Dimensiones SCD y estrategia de gestión. Jerarquías a ser consideradas.
  - Descripción de la tabla de hechos, sus atributos y sus claves. Granularidad. Identificación de Medidas.
- **Conclusiones.**

### 2.3. Fase II — Implementación del Datawarehouse y Proceso ETL

- Informe anterior corregido.
- Implementación del Datawarehouse en una base de datos relacional (Oracle).
- Descripción del Proceso de Extracción, Transformación y Carga (utilizando *Apache Hop*).
- Describir el proceso de poblamiento de las dimensiones y de la tabla de hechos, considerando:
  - Definición del proceso de carga inicial.
  - Definición del proceso de carga periódica.
  - Definición de la periodicidad de las cargas.
- Testing sobre la base de datos (consultas SQL considerando agrupamientos).
- **Conclusiones.**

### 2.4. Fase III — Integración con Herramientas OLAP y Análisis de Datos

- Informe anterior corregido.
- Procesamiento analítico utilizando la plataforma *Pentaho* (JPivot, Saiku, Pivot4j, Visualizer), *Apache Superset*, *PowerBI Desktop*.
- **Análisis de Datos:** Análisis de la información obtenida considerando diferentes miradas (agrupación de dimensiones). Contrastar lo obtenido con los objetivos y las preguntas de investigación.
- **Conclusiones.**

---

## 3. Referencias

- **HEFESTO - Data Warehousing** — https://sourceforge.net/projects/bihefesto/
