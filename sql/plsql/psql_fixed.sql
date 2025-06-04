-- Función 1 - Calcular promedio de tarifas por ruta
CREATE OR REPLACE FUNCTION calcular_tarifa_promedio(
    v_origin_city VARCHAR(150),
    v_destination_city VARCHAR(150)
)
RETURNS NUMERIC AS $$
DECLARE
    v_tarifa_promedio NUMERIC := 0;
BEGIN
    SELECT AVG(ms.fare_avg)
    INTO v_tarifa_promedio
    FROM routes r
    JOIN flights f ON r.route_id = f.route_id
    JOIN market_share ms ON f.flight_id = ms.flight_id
    JOIN airports a1 ON r.origin_airport_id = a1.airport_id
    JOIN airports a2 ON r.destination_airport_id = a2.airport_id
    JOIN cities c1 ON a1.city_market_id = c1.city_market_id
    JOIN cities c2 ON a2.city_market_id = c2.city_market_id
    WHERE c1.city_name = v_origin_city 
    AND c2.city_name = v_destination_city
    AND ms.fare_avg IS NOT NULL;

    -- Si no se encontraron datos, devolver 0
    IF v_tarifa_promedio IS NULL THEN
        v_tarifa_promedio := 0;
    END IF;

    RETURN v_tarifa_promedio;

EXCEPTION
    WHEN OTHERS THEN
        RETURN -1; -- Error
END;
$$ LANGUAGE plpgsql;

-- Función 2 - Calcular participación de mercado de una aerolínea
CREATE OR REPLACE FUNCTION calcular_participacion_mercado(
    v_carrier_code VARCHAR(10),
    v_year INTEGER,
    v_quarter INTEGER
)
RETURNS NUMERIC AS $$
DECLARE
    v_market_share NUMERIC := 0;
BEGIN
    SELECT AVG(ms.market_share_percentage)
    INTO v_market_share
    FROM market_share ms
    JOIN flights f ON ms.flight_id = f.flight_id
    JOIN carriers c ON ms.carrier_id = c.carrier_id
    WHERE c.carrier_code = v_carrier_code
    AND f.year = v_year
    AND f.quarter = v_quarter
    AND ms.market_share_percentage IS NOT NULL;

    -- Si no se encontraron datos, devolver 0
    IF v_market_share IS NULL THEN
        v_market_share := 0;
    END IF;

    RETURN v_market_share;

EXCEPTION
    WHEN OTHERS THEN
        RETURN -1; -- Error
END;
$$ LANGUAGE plpgsql;

-- Función 3 - Analizar evolución histórica de aerolínea (USA FOR LOOP)
CREATE OR REPLACE FUNCTION analizar_evolucion_aerolinea(
    v_carrier_code VARCHAR(10),
    v_year_inicio INTEGER,
    v_year_fin INTEGER
)
RETURNS TABLE (
    year_analizado INTEGER,
    participacion_promedio NUMERIC,
    total_vuelos BIGINT,
    tarifa_promedio NUMERIC,
    tendencia VARCHAR(20)
) AS $$
DECLARE
    v_year INTEGER;
    v_participacion_actual NUMERIC;
    v_participacion_anterior NUMERIC := 0;
    v_vuelos BIGINT;
    v_tarifa NUMERIC;
    v_tendencia VARCHAR(20);
BEGIN
    -- FOR LOOP para iterar sobre cada año en el rango
    FOR v_year IN v_year_inicio..v_year_fin LOOP
        
        -- Obtener datos del año actual
        SELECT 
            AVG(ms.market_share_percentage),
            COUNT(DISTINCT f.flight_id),
            AVG(ms.fare_avg)
        INTO v_participacion_actual, v_vuelos, v_tarifa
        FROM market_share ms
        JOIN flights f ON ms.flight_id = f.flight_id
        JOIN carriers c ON ms.carrier_id = c.carrier_id
        WHERE c.carrier_code = v_carrier_code
        AND f.year = v_year
        AND ms.market_share_percentage IS NOT NULL
        AND ms.fare_avg IS NOT NULL;

        -- Determinar tendencia comparando con año anterior
        IF v_year = v_year_inicio THEN
            v_tendencia := 'INICIAL';
        ELSIF COALESCE(v_participacion_actual, 0) > COALESCE(v_participacion_anterior, 0) THEN
            v_tendencia := 'CRECIMIENTO';
        ELSIF COALESCE(v_participacion_actual, 0) < COALESCE(v_participacion_anterior, 0) THEN
            v_tendencia := 'DECLIVE';
        ELSE
            v_tendencia := 'ESTABLE';
        END IF;

        -- Retornar fila solo si hay datos
        IF COALESCE(v_vuelos, 0) > 0 THEN
            RETURN QUERY
            SELECT 
                v_year,
                ROUND(COALESCE(v_participacion_actual, 0), 2),
                COALESCE(v_vuelos, 0),
                ROUND(COALESCE(v_tarifa, 0), 2),
                v_tendencia;
        END IF;

        -- Guardar participación actual para próxima iteración
        v_participacion_anterior := v_participacion_actual;
        
    END LOOP;

    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Función 4 - Obtener aerolínea dominante por ruta
CREATE OR REPLACE FUNCTION obtener_aerolinea_dominante(
    v_origin_city VARCHAR(150),
    v_destination_city VARCHAR(150),
    v_year INTEGER DEFAULT NULL
)
RETURNS TABLE (
    codigo_aerolinea VARCHAR(10),
    tipo_aerolinea VARCHAR(10),
    participacion_maxima NUMERIC,
    total_vuelos BIGINT,
    tarifa_promedio NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.carrier_code,
        c.carrier_type,
        ROUND(AVG(ms.market_share_percentage), 2),
        COUNT(DISTINCT f.flight_id),
        ROUND(AVG(ms.fare_avg), 2)
    FROM routes r
    JOIN flights f ON r.route_id = f.route_id
    JOIN market_share ms ON f.flight_id = ms.flight_id
    JOIN carriers c ON ms.carrier_id = c.carrier_id
    JOIN airports a1 ON r.origin_airport_id = a1.airport_id
    JOIN airports a2 ON r.destination_airport_id = a2.airport_id
    JOIN cities c1 ON a1.city_market_id = c1.city_market_id
    JOIN cities c2 ON a2.city_market_id = c2.city_market_id
    WHERE c1.city_name = v_origin_city 
    AND c2.city_name = v_destination_city
    AND ms.market_share_percentage IS NOT NULL
    AND ms.fare_avg IS NOT NULL
    AND (v_year IS NULL OR f.year = v_year)
    GROUP BY c.carrier_code, c.carrier_type
    ORDER BY AVG(ms.market_share_percentage) DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Función 5 - Analizar competencia por aeropuerto (usa WHILE LOOP y manejo de cursores)
CREATE OR REPLACE FUNCTION analizar_competencia_aeropuerto(
    v_airport_code VARCHAR(10),
    v_year_objetivo INTEGER
)
RETURNS TABLE (
    tipo_analisis VARCHAR(50),
    total_carriers INTEGER,
    carrier_dominante VARCHAR(10),
    participacion_dominante NUMERIC,
    nivel_competencia VARCHAR(20),
    total_rutas INTEGER,
    tarifa_promedio_aeropuerto NUMERIC
) AS $$
DECLARE
    v_contador INTEGER := 0;
    v_total_carriers INTEGER := 0;
    v_max_participacion NUMERIC := 0;
    v_carrier_dom VARCHAR(10);
    v_nivel_comp VARCHAR(20);
    v_total_rutas INTEGER := 0;
    v_tarifa_prom NUMERIC := 0;
    
    -- Cursor para iterar sobre carriers en el aeropuerto
    carrier_cursor CURSOR FOR
        SELECT DISTINCT c.carrier_code, AVG(ms.market_share_percentage) as avg_share
        FROM carriers c
        JOIN market_share ms ON c.carrier_id = ms.carrier_id
        JOIN flights f ON ms.flight_id = f.flight_id
        JOIN routes r ON f.route_id = r.route_id
        JOIN airports a ON (r.origin_airport_id = a.airport_id OR r.destination_airport_id = a.airport_id)
        WHERE a.airport_code = v_airport_code
        AND f.year = v_year_objetivo
        AND ms.market_share_percentage IS NOT NULL
        GROUP BY c.carrier_code
        ORDER BY avg_share DESC;
    
    carrier_rec RECORD;
BEGIN
    -- Obtener estadísticas generales del aeropuerto
    SELECT 
        COUNT(DISTINCT c.carrier_code),
        COUNT(DISTINCT r.route_id),
        AVG(ms.fare_avg)
    INTO v_total_carriers, v_total_rutas, v_tarifa_prom
    FROM carriers c
    JOIN market_share ms ON c.carrier_id = ms.carrier_id
    JOIN flights f ON ms.flight_id = f.flight_id
    JOIN routes r ON f.route_id = r.route_id
    JOIN airports a ON (r.origin_airport_id = a.airport_id OR r.destination_airport_id = a.airport_id)
    WHERE a.airport_code = v_airport_code
    AND f.year = v_year_objetivo
    AND ms.market_share_percentage IS NOT NULL;

    -- WHILE LOOP con cursor para encontrar carrier dominante
    OPEN carrier_cursor;
    v_contador := 0;
    
    WHILE v_contador < 1 LOOP
        FETCH carrier_cursor INTO carrier_rec;
        
        IF FOUND THEN
            v_carrier_dom := carrier_rec.carrier_code;
            v_max_participacion := carrier_rec.avg_share;
            v_contador := v_contador + 1;
        ELSE
            EXIT; -- Salir si no hay más registros
        END IF;
    END LOOP;
    
    CLOSE carrier_cursor;

    -- Determinar nivel de competencia
    IF v_max_participacion > 60 THEN
        v_nivel_comp := 'MONOPOLIO';
    ELSIF v_max_participacion > 40 THEN
        v_nivel_comp := 'DOMINANTE';
    ELSIF v_max_participacion > 25 THEN
        v_nivel_comp := 'COMPETITIVO';
    ELSE
        v_nivel_comp := 'FRAGMENTADO';
    END IF;

    -- Retornar resultado
    RETURN QUERY
    SELECT 
        'Análisis Competencia'::VARCHAR(50),
        COALESCE(v_total_carriers, 0),
        COALESCE(v_carrier_dom, 'N/A')::VARCHAR(10),
        ROUND(COALESCE(v_max_participacion, 0), 2),
        v_nivel_comp,
        COALESCE(v_total_rutas, 0),
        ROUND(COALESCE(v_tarifa_prom, 0), 2);

    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Función 6 - Calcular índice de estacionalidad de precios (usa variables individuales en lugar de arrays)
CREATE OR REPLACE FUNCTION calcular_indice_estacionalidad(
    v_origin_city VARCHAR(150),
    v_destination_city VARCHAR(150),
    v_year_base INTEGER
)
RETURNS TABLE (
    quarter_analizado INTEGER,
    tarifa_quarter NUMERIC,
    tarifa_anual_promedio NUMERIC,
    indice_estacional NUMERIC,
    interpretacion VARCHAR(30),
    volumen_vuelos INTEGER,
    variacion_porcentual NUMERIC
) AS $$
DECLARE
    v_tarifa_anual NUMERIC := 0;
    v_quarter INTEGER;
    v_tarifa_q NUMERIC;
    v_vuelos_q INTEGER;
    v_indice NUMERIC;
    v_interpretacion VARCHAR(30);
    v_variacion NUMERIC;
BEGIN
    -- Calcular tarifa anual promedio
    SELECT AVG(ms.fare_avg)
    INTO v_tarifa_anual
    FROM routes r
    JOIN flights f ON r.route_id = f.route_id
    JOIN market_share ms ON f.flight_id = ms.flight_id
    JOIN airports a1 ON r.origin_airport_id = a1.airport_id
    JOIN airports a2 ON r.destination_airport_id = a2.airport_id
    JOIN cities c1 ON a1.city_market_id = c1.city_market_id
    JOIN cities c2 ON a2.city_market_id = c2.city_market_id
    WHERE c1.city_name = v_origin_city 
    AND c2.city_name = v_destination_city
    AND f.year = v_year_base
    AND ms.fare_avg IS NOT NULL;

    -- FOR LOOP para calcular por cada trimestre (1-4)
    FOR v_quarter IN 1..4 LOOP
        -- Obtener tarifa y volumen del trimestre
        SELECT 
            AVG(ms.fare_avg),
            COUNT(DISTINCT f.flight_id)
        INTO v_tarifa_q, v_vuelos_q
        FROM routes r
        JOIN flights f ON r.route_id = f.route_id
        JOIN market_share ms ON f.flight_id = ms.flight_id
        JOIN airports a1 ON r.origin_airport_id = a1.airport_id
        JOIN airports a2 ON r.destination_airport_id = a2.airport_id
        JOIN cities c1 ON a1.city_market_id = c1.city_market_id
        JOIN cities c2 ON a2.city_market_id = c2.city_market_id
        WHERE c1.city_name = v_origin_city 
        AND c2.city_name = v_destination_city
        AND f.year = v_year_base
        AND f.quarter = v_quarter
        AND ms.fare_avg IS NOT NULL;

        -- Calcular índice estacional (tarifa_trimestre / tarifa_anual)
        IF v_tarifa_anual > 0 AND v_tarifa_q IS NOT NULL THEN
            v_indice := v_tarifa_q / v_tarifa_anual;
            v_variacion := ((v_tarifa_q - v_tarifa_anual) / v_tarifa_anual) * 100;
        ELSE
            v_indice := 0;
            v_variacion := 0;
        END IF;

        -- Interpretar el índice usando CASE avanzado
        v_interpretacion := 
            CASE 
                WHEN v_indice = 0 THEN 'SIN DATOS'
                WHEN v_indice >= 1.2 THEN 'MUY ALTA ESTACIONALIDAD'
                WHEN v_indice >= 1.1 THEN 'ALTA ESTACIONALIDAD'
                WHEN v_indice >= 1.05 THEN 'ESTACIONALIDAD MODERADA'
                WHEN v_indice >= 0.95 THEN 'PRECIO NORMAL'
                WHEN v_indice >= 0.8 THEN 'PRECIO BAJO'
                ELSE 'PRECIO MUY BAJO'
            END;

        -- Retornar fila para cada trimestre
        RETURN QUERY
        SELECT 
            v_quarter,
            ROUND(COALESCE(v_tarifa_q, 0), 2),
            ROUND(COALESCE(v_tarifa_anual, 0), 2),
            ROUND(v_indice, 3),
            v_interpretacion,
            COALESCE(v_vuelos_q, 0),
            ROUND(v_variacion, 2);
    END LOOP;

    RETURN;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- EJEMPLOS DE USO
-- ============================================================================

-- Ejemplo 1: Calcular tarifa promedio
SELECT calcular_tarifa_promedio('Boston', 'New York City') AS tarifa_promedio;

-- Ejemplo 2: Calcular participación de mercado
SELECT calcular_participacion_mercado('180', 2021, 3) AS participacion_mercado;

-- Ejemplo 3: USAR FOR LOOP - Analizar evolución de aerolínea a través de los años
SELECT * FROM analizar_evolucion_aerolinea('180', 2020, 2023);

-- Ejemplo 4: Obtener aerolínea dominante en una ruta
SELECT * FROM obtener_aerolinea_dominante('Boston', 'Atlanta');

-- Ejemplo 5: Obtener aerolínea dominante en ruta específica y año específico
SELECT * FROM obtener_aerolinea_dominante('New York City', 'Los Angeles', 2021);

-- Ejemplo 6: USAR WHILE LOOP Y CURSORES - Analizar competencia en aeropuerto
SELECT * FROM analizar_competencia_aeropuerto('ATL', 2021);

-- Ejemplo 7: USAR CASE AVANZADO - Calcular índice de estacionalidad
SELECT * FROM calcular_indice_estacionalidad('New York City', 'Los Angeles', 2021); 