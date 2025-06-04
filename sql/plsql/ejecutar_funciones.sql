-- ============================================================================
-- ARCHIVO PARA EJECUTAR FUNCIONES PL/PGSQL
-- Proyecto: Análisis de Rutas y Tarifas Aéreas en EE.UU. (1993-2024)
-- Base de Datos: PostgreSQL
-- ============================================================================

-- ============================================================================
-- CONSULTAS AUXILIARES PARA OBTENER DATOS VÁLIDOS
-- ============================================================================

-- Ver ciudades disponibles para usar en las funciones
SELECT DISTINCT city_name 
FROM cities 
WHERE city_name IS NOT NULL 
ORDER BY city_name 
LIMIT 15;

-- Ver códigos de aerolíneas disponibles
SELECT DISTINCT carrier_code, carrier_type 
FROM carriers 
ORDER BY carrier_code 
LIMIT 15;

-- Ver códigos de aeropuertos disponibles
SELECT DISTINCT airport_code, city_name, state 
FROM airports a 
JOIN cities c ON a.city_market_id = c.city_market_id 
ORDER BY airport_code 
LIMIT 15;

-- Ver años disponibles en el dataset
SELECT DISTINCT year 
FROM flights 
ORDER BY year;

-- Ver rutas más populares (útil para testing)
SELECT 
    c1.city_name as origen,
    c2.city_name as destino,
    COUNT(*) as frecuencia
FROM routes r
JOIN airports a1 ON r.origin_airport_id = a1.airport_id
JOIN airports a2 ON r.destination_airport_id = a2.airport_id
JOIN cities c1 ON a1.city_market_id = c1.city_market_id
JOIN cities c2 ON a2.city_market_id = c2.city_market_id
JOIN flights f ON r.route_id = f.route_id
WHERE f.year >= 2020
GROUP BY c1.city_name, c2.city_name
ORDER BY frecuencia DESC
LIMIT 10;

-- ============================================================================
-- FUNCIÓN 1: CALCULAR_TARIFA_PROMEDIO
-- Calcula el promedio de tarifas entre dos ciudades
-- ============================================================================

-- Ejemplo 1.1: Tarifa promedio entre ciudades principales
SELECT calcular_tarifa_promedio('New York City', 'Los Angeles') AS tarifa_promedio_nyc_la;

-- Ejemplo 1.2: Tarifa promedio entre otras ciudades
SELECT calcular_tarifa_promedio('Boston', 'Atlanta') AS tarifa_promedio_bos_atl;

-- Ejemplo 1.3: Tarifa promedio - ruta que podría no existir (retorna 0)
SELECT calcular_tarifa_promedio('Miami', 'Seattle') AS tarifa_promedio_no_existe;

-- Ejemplo 1.4: Comparar tarifas entre múltiples rutas
SELECT 
    'NYC-LA' as ruta,
    calcular_tarifa_promedio('New York City', 'Los Angeles') AS tarifa
UNION ALL
SELECT 
    'Boston-Atlanta' as ruta,
    calcular_tarifa_promedio('Boston', 'Atlanta') AS tarifa
UNION ALL
SELECT 
    'Chicago-Miami' as ruta,
    calcular_tarifa_promedio('Chicago', 'Miami') AS tarifa;

-- ============================================================================
-- FUNCIÓN 2: CALCULAR_PARTICIPACION_MERCADO
-- Calcula la participación de mercado de una aerolínea en un período específico
-- ============================================================================

-- Ejemplo 2.1: Participación de mercado de aerolínea específica
SELECT calcular_participacion_mercado('180', 2021, 3) AS participacion_aerolinea_180;

-- Ejemplo 2.2: Participación de mercado de otra aerolínea
SELECT calcular_participacion_mercado('19', 2021, 4) AS participacion_aerolinea_19;

-- Ejemplo 2.3: Comparar participación de mercado entre aerolíneas
SELECT 
    '180' as codigo_aerolinea,
    calcular_participacion_mercado('180', 2021, 3) AS participacion_mercado
UNION ALL
SELECT 
    '19' as codigo_aerolinea,
    calcular_participacion_mercado('19', 2021, 3) AS participacion_mercado
UNION ALL
SELECT 
    '204' as codigo_aerolinea,
    calcular_participacion_mercado('204', 2021, 3) AS participacion_mercado;

-- Ejemplo 2.4: Participación por trimestres de una aerolínea
SELECT 
    1 as trimestre,
    calcular_participacion_mercado('180', 2021, 1) AS participacion
UNION ALL
SELECT 
    2 as trimestre,
    calcular_participacion_mercado('180', 2021, 2) AS participacion
UNION ALL
SELECT 
    3 as trimestre,
    calcular_participacion_mercado('180', 2021, 3) AS participacion
UNION ALL
SELECT 
    4 as trimestre,
    calcular_participacion_mercado('180', 2021, 4) AS participacion;

-- ============================================================================
-- FUNCIÓN 3: ANALIZAR_EVOLUCION_AEROLINEA (USA FOR LOOP)
-- Analiza la evolución histórica de una aerolínea a través de los años
-- ============================================================================

-- Ejemplo 3.1: Evolución de aerolínea principal
SELECT * FROM analizar_evolucion_aerolinea('180', 2021, 2022)
ORDER BY year_analizado;

-- Ejemplo 3.2: Evolución de otra aerolínea
SELECT * FROM analizar_evolucion_aerolinea('19', 2021, 2022)
ORDER BY year_analizado;

-- Ejemplo 3.3: Evolución con rango de años más amplio
SELECT * FROM analizar_evolucion_aerolinea('180', 2020, 2022)
ORDER BY year_analizado;

-- Ejemplo 3.4: Comparar evolución de múltiples aerolíneas
SELECT 
    '180' as aerolinea,
    year_analizado,
    participacion_promedio,
    total_vuelos,
    tarifa_promedio,
    tendencia
FROM analizar_evolucion_aerolinea('180', 2021, 2022)
UNION ALL
SELECT 
    '19' as aerolinea,
    year_analizado,
    participacion_promedio,
    total_vuelos,
    tarifa_promedio,
    tendencia
FROM analizar_evolucion_aerolinea('19', 2021, 2022)
ORDER BY aerolinea, year_analizado;

-- ============================================================================
-- FUNCIÓN 4: OBTENER_AEROLINEA_DOMINANTE
-- Obtiene la aerolínea dominante en una ruta específica
-- ============================================================================

-- Ejemplo 4.1: Aerolínea dominante en ruta principal
SELECT * FROM obtener_aerolinea_dominante('New York City', 'Los Angeles');

-- Ejemplo 4.2: Aerolínea dominante en ruta específica con año
SELECT * FROM obtener_aerolinea_dominante('Boston', 'Atlanta', 2021);

-- Ejemplo 4.3: Aerolínea dominante en otra ruta
SELECT * FROM obtener_aerolinea_dominante('Chicago', 'Miami');

-- Ejemplo 4.4: Comparar aerolíneas dominantes en múltiples rutas
SELECT 
    'NYC-LA' as ruta,
    codigo_aerolinea,
    tipo_aerolinea,
    participacion_maxima,
    total_vuelos,
    tarifa_promedio
FROM obtener_aerolinea_dominante('New York City', 'Los Angeles')
UNION ALL
SELECT 
    'Boston-Atlanta' as ruta,
    codigo_aerolinea,
    tipo_aerolinea,
    participacion_maxima,
    total_vuelos,
    tarifa_promedio
FROM obtener_aerolinea_dominante('Boston', 'Atlanta');

-- Ejemplo 4.5: Aerolínea dominante por año específico
SELECT 
    2021 as año,
    codigo_aerolinea,
    tipo_aerolinea,
    participacion_maxima
FROM obtener_aerolinea_dominante('New York City', 'Los Angeles', 2021)
UNION ALL
SELECT 
    2022 as año,
    codigo_aerolinea,
    tipo_aerolinea,
    participacion_maxima
FROM obtener_aerolinea_dominante('New York City', 'Los Angeles', 2022);

-- ============================================================================
-- FUNCIÓN 5: ANALIZAR_COMPETENCIA_AEROPUERTO (USA WHILE LOOP Y CURSORES)
-- Analiza la competencia en un aeropuerto específico
-- ============================================================================

-- Ejemplo 5.1: Análisis de competencia en aeropuerto principal
SELECT * FROM analizar_competencia_aeropuerto('ATL', 2021);

-- Ejemplo 5.2: Análisis de competencia en otro aeropuerto
SELECT * FROM analizar_competencia_aeropuerto('LAX', 2021);

-- Ejemplo 5.3: Análisis de competencia en aeropuerto menor
SELECT * FROM analizar_competencia_aeropuerto('BOS', 2021);

-- Ejemplo 5.4: Comparar competencia entre aeropuertos
SELECT 
    'ATL' as aeropuerto,
    total_carriers,
    carrier_dominante,
    participacion_dominante,
    nivel_competencia,
    total_rutas
FROM analizar_competencia_aeropuerto('ATL', 2021)
UNION ALL
SELECT 
    'LAX' as aeropuerto,
    total_carriers,
    carrier_dominante,
    participacion_dominante,
    nivel_competencia,
    total_rutas
FROM analizar_competencia_aeropuerto('LAX', 2021)
UNION ALL
SELECT 
    'BOS' as aeropuerto,
    total_carriers,
    carrier_dominante,
    participacion_dominante,
    nivel_competencia,
    total_rutas
FROM analizar_competencia_aeropuerto('BOS', 2021);

-- Ejemplo 5.5: Análisis de competencia por diferentes años
SELECT 
    2021 as año,
    total_carriers,
    carrier_dominante,
    nivel_competencia
FROM analizar_competencia_aeropuerto('ATL', 2021)
UNION ALL
SELECT 
    2022 as año,
    total_carriers,
    carrier_dominante,
    nivel_competencia
FROM analizar_competencia_aeropuerto('ATL', 2022);

-- ============================================================================
-- FUNCIÓN 6: CALCULAR_INDICE_ESTACIONALIDAD (USA CASE AVANZADO)
-- Calcula el índice de estacionalidad de precios en una ruta
-- ============================================================================

-- Ejemplo 6.1: Índice de estacionalidad en ruta principal
SELECT * FROM calcular_indice_estacionalidad('New York City', 'Los Angeles', 2021)
ORDER BY quarter_analizado;

-- Ejemplo 6.2: Índice de estacionalidad en otra ruta
SELECT * FROM calcular_indice_estacionalidad('Boston', 'Atlanta', 2021)
ORDER BY quarter_analizado;

-- Ejemplo 6.3: Índice de estacionalidad en año diferente
SELECT * FROM calcular_indice_estacionalidad('New York City', 'Los Angeles', 2022)
ORDER BY quarter_analizado;

-- Ejemplo 6.4: Comparar estacionalidad entre rutas
SELECT 
    'NYC-LA' as ruta,
    quarter_analizado,
    tarifa_quarter,
    indice_estacional,
    interpretacion,
    variacion_porcentual
FROM calcular_indice_estacionalidad('New York City', 'Los Angeles', 2021)
UNION ALL
SELECT 
    'Boston-Atlanta' as ruta,
    quarter_analizado,
    tarifa_quarter,
    indice_estacional,
    interpretacion,
    variacion_porcentual
FROM calcular_indice_estacionalidad('Boston', 'Atlanta', 2021)
ORDER BY ruta, quarter_analizado;

-- Ejemplo 6.5: Resumen de estacionalidad (solo trimestres con alta variación)
SELECT 
    quarter_analizado,
    tarifa_quarter,
    indice_estacional,
    interpretacion,
    variacion_porcentual
FROM calcular_indice_estacionalidad('New York City', 'Los Angeles', 2021)
WHERE ABS(variacion_porcentual) > 5
ORDER BY ABS(variacion_porcentual) DESC;

-- ============================================================================
-- EJEMPLOS COMBINADOS - ANÁLISIS INTEGRAL
-- ============================================================================

-- Análisis Completo de una Ruta Específica
SELECT 
    'ANÁLISIS COMPLETO: NYC - Los Angeles' as analisis,
    NULL::NUMERIC as valor,
    NULL as detalle
UNION ALL
SELECT 
    'Tarifa Promedio',
    calcular_tarifa_promedio('New York City', 'Los Angeles'),
    'USD'
UNION ALL
SELECT 
    'Aerolínea Dominante',
    participacion_maxima,
    codigo_aerolinea
FROM obtener_aerolinea_dominante('New York City', 'Los Angeles');

-- Comparativo de Competencia entre Aeropuertos Principales
SELECT 
    'COMPETENCIA AEROPORTUARIA 2021' as titulo,
    NULL::INTEGER as total_carriers,
    NULL as aeropuerto,
    NULL as nivel_competencia
UNION ALL
SELECT 
    'ATL (Atlanta)',
    total_carriers,
    carrier_dominante,
    nivel_competencia
FROM analizar_competencia_aeropuerto('ATL', 2021)
UNION ALL
SELECT 
    'LAX (Los Angeles)',
    total_carriers,
    carrier_dominante,
    nivel_competencia
FROM analizar_competencia_aeropuerto('LAX', 2021);

-- ============================================================================
-- CONSULTAS DE VALIDACIÓN
-- ============================================================================

-- Verificar que las funciones están instaladas correctamente
SELECT 
    routine_name as nombre_funcion,
    routine_type as tipo,
    'INSTALLED' as estado
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_type = 'FUNCTION'
AND (routine_name LIKE 'calcular%' OR routine_name LIKE 'analizar%' OR routine_name LIKE 'obtener%')
ORDER BY routine_name;

-- ============================================================================
-- NOTAS DE USO
-- ============================================================================

/*
INSTRUCCIONES DE USO:

1. ANTES DE EJECUTAR:
   - Asegúrate de que las funciones están desplegadas en PostgreSQL
   - Ejecuta: python deploy_functions.py
   - Verifica conexión a la base de datos

2. EJECUTAR CONSULTAS:
   - Puedes ejecutar estas consultas individualmente
   - O ejecutar secciones completas
   - Modifica ciudades/aerolíneas/años según tus datos

3. PARÁMETROS VÁLIDOS:
   - Ciudades: Usar nombres exactos de la tabla cities
   - Aerolíneas: Usar códigos exactos de la tabla carriers
   - Años: Usar años disponibles en la tabla flights
   - Aeropuertos: Usar códigos exactos de la tabla airports

4. INTERPRETACIÓN DE RESULTADOS:
   - Tarifas en USD
   - Participación de mercado en porcentaje
   - Tendencias: INICIAL, CRECIMIENTO, DECLIVE, ESTABLE
   - Competencia: MONOPOLIO, DOMINANTE, COMPETITIVO, FRAGMENTADO
   - Estacionalidad: Índice 1.0 = normal, >1.0 = alto, <1.0 = bajo

5. SOLUCIÓN DE PROBLEMAS:
   - Si una función retorna 0 o NULL, verifica que los parámetros existan
   - Si hay errores, revisa la sintaxis de las ciudades/códigos
   - Para debugging, usa las consultas auxiliares al inicio del archivo
*/ 