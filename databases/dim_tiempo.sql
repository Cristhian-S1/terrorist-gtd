-- ============================================================
-- GTD Data Warehouse - DIM_TIEMPO (Static Dimension)
-- Populate with dates 1970-01-01 to 2025-12-31
-- ============================================================

CREATE OR REPLACE PROCEDURE GENERAR_RANGO_TIEMPO AS
    FECHA_INICIO DATE := TO_DATE('01-01-1970', 'DD-MM-YYYY');
    FECHA_FIN    DATE := TO_DATE('01-01-2026', 'DD-MM-YYYY');
    V_TIEMPO_SK  NUMBER;
    V_AGNO       NUMBER;
    V_MES        NUMBER;
    V_DIA        NUMBER;
BEGIN
    WHILE FECHA_INICIO <= FECHA_FIN LOOP
        V_TIEMPO_SK := TO_NUMBER(TO_CHAR(FECHA_INICIO, 'YYYYMMDD'));
        V_AGNO      := TO_NUMBER(TO_CHAR(FECHA_INICIO, 'YYYY'));
        V_MES       := TO_NUMBER(TO_CHAR(FECHA_INICIO, 'MM'));
        V_DIA       := TO_NUMBER(TO_CHAR(FECHA_INICIO, 'DD'));
        INSERT INTO DIM_TIEMPO (TIEMPO_SK, IYEAR, IMONTH, IDAY)
        VALUES (V_TIEMPO_SK, V_AGNO, V_MES, V_DIA);
        FECHA_INICIO := FECHA_INICIO + 1;
    END LOOP;
    COMMIT;
END;
/

BEGIN
    GENERAR_RANGO_TIEMPO;
END;
/
