-- Consulta 1 - Análisis de rutas por distancia y promedio de tarifas por trimestre
SELECT 
    CASE 
        WHEN r.distance_miles < 500 THEN 'Corta distancia (<500 millas)'
        WHEN r.distance_miles < 1000 THEN 'Media distancia (500-1000 millas)'
        ELSE 'Larga distancia (>1000 millas)'
    END categoria_distancia,
    f.year,
    f.quarter,
    COUNT(DISTINCT r.route_id) numero_rutas,
    ROUND(AVG(ms.fare_avg), 2) tarifa_promedio,
    ROUND(MAX(ms.fare_avg), 2) tarifa_maxima,
    ROUND(MIN(ms.fare_avg), 2) tarifa_minima
FROM routes r, flights f, market_share ms
WHERE r.route_id = f.route_id
AND f.flight_id = ms.flight_id
AND r.distance_miles IS NOT NULL
GROUP BY 
    CASE 
        WHEN r.distance_miles < 500 THEN 'Corta distancia (<500 millas)'
        WHEN r.distance_miles < 1000 THEN 'Media distancia (500-1000 millas)'
        ELSE 'Larga distancia (>1000 millas)'
    END,
    f.year,
    f.quarter
ORDER BY f.year, f.quarter, categoria_distancia;

-- Consulta 2 - Rutas con mayor competencia entre aerolíneas
SELECT 
    c1.city_name origen,
    c2.city_name destino,
    f.year,
    f.quarter,
    COUNT(DISTINCT ms.carrier_id) num_carriers,
    ROUND(AVG(ms.market_share_percentage), 2) participacion_promedio,
    ROUND(AVG(ms.fare_avg), 2) tarifa_promedio
FROM routes r, flights f, market_share ms, airports a1, airports a2, cities c1, cities c2
WHERE r.route_id = f.route_id
AND f.flight_id = ms.flight_id
AND r.origin_airport_id = a1.airport_id
AND r.destination_airport_id = a2.airport_id
AND a1.city_market_id = c1.city_market_id
AND a2.city_market_id = c2.city_market_id
GROUP BY c1.city_name, c2.city_name, f.year, f.quarter
HAVING COUNT(DISTINCT ms.carrier_id) >= 3  -- Rutas con competencia significativa
ORDER BY f.year, f.quarter, num_carriers DESC;

-- Consulta 3 - Aeropuertos con mayor número de conexiones y participación de aerolíneas legacy
SELECT 
    a.airport_code,
    c.city_name,
    c.state,
    COUNT(DISTINCT r.route_id) total_rutas,
    COUNT(DISTINCT CASE WHEN car.carrier_type = 'Legacy' THEN ms.carrier_id END) carriers_legacy,
    COUNT(DISTINCT CASE WHEN car.carrier_type = 'Low-Cost' THEN ms.carrier_id END) carriers_lowcost,
    ROUND(AVG(ms.fare_avg), 2) tarifa_promedio
FROM airports a, cities c, routes r, flights f, market_share ms, carriers car
WHERE a.city_market_id = c.city_market_id
AND (a.airport_id = r.origin_airport_id OR a.airport_id = r.destination_airport_id)
AND r.route_id = f.route_id
AND f.flight_id = ms.flight_id
AND ms.carrier_id = car.carrier_id
GROUP BY a.airport_code, c.city_name, c.state
HAVING COUNT(DISTINCT r.route_id) >= 5  -- Aeropuertos con al menos 5 rutas
ORDER BY total_rutas DESC;

-- Consulta 4 - Aerolíneas con mayor participación promedio en rutas de larga distancia durante verano
SELECT 
    car.carrier_code,
    car.carrier_type,
    f.year,
    ROUND(AVG(ms.market_share_percentage), 2) participacion_promedio,
    COUNT(DISTINCT f.flight_id) total_vuelos,
    ROUND(AVG(r.distance_miles), 2) distancia_promedio
FROM carriers car, market_share ms, flights f, routes r
WHERE car.carrier_id = ms.carrier_id
AND ms.flight_id = f.flight_id
AND f.route_id = r.route_id
AND r.distance_miles > 1000
AND f.quarter IN (2, 3)
AND ms.market_share_percentage IS NOT NULL
GROUP BY car.carrier_code, car.carrier_type, f.year
HAVING AVG(ms.market_share_percentage) >= 30
ORDER BY f.year, participacion_promedio DESC;

-- Consulta 5 - Rutas más caras por año y trimestre
SELECT 
    c1.city_name origen,
    c2.city_name destino,
    f.year,
    f.quarter,
    ROUND(ms.fare_avg, 2) tarifa,
    r.distance_miles distancia
FROM flights f, market_share ms, routes r, airports a1, airports a2, cities c1, cities c2
WHERE f.flight_id = ms.flight_id
AND f.route_id = r.route_id
AND r.origin_airport_id = a1.airport_id
AND r.destination_airport_id = a2.airport_id
AND a1.city_market_id = c1.city_market_id
AND a2.city_market_id = c2.city_market_id
AND f.year >= 2020
AND ms.fare_avg IS NOT NULL
AND r.distance_miles IS NOT NULL
GROUP BY c1.city_name, c2.city_name, f.year, f.quarter, ms.fare_avg, r.distance_miles
HAVING ms.fare_avg >= 500  -- Tarifas altas
ORDER BY f.year, f.quarter, ms.fare_avg DESC;

-- Consulta 6 - Aerolíneas de bajo costo con mayor participación por año
SELECT 
    car.carrier_code,
    f.year,
    COUNT(DISTINCT f.flight_id) total_vuelos,
    ROUND(AVG(ms.market_share_percentage), 2) participacion_promedio,
    ROUND(AVG(ms.fare_avg), 2) tarifa_promedio
FROM carriers car, market_share ms, flights f
WHERE car.carrier_id = ms.carrier_id
AND ms.flight_id = f.flight_id
AND car.carrier_type = 'Low-Cost'
AND ms.market_share_percentage IS NOT NULL
AND ms.fare_avg IS NOT NULL
GROUP BY car.carrier_code, f.year
HAVING COUNT(DISTINCT f.flight_id) >= 10
AND AVG(ms.market_share_percentage) >= 20
ORDER BY f.year, participacion_promedio DESC;

-- Consulta 7 - Análisis de evolución de precios por estado y tipo de aerolínea
SELECT 
    c.state,
    car.carrier_type,
    f.year,
    COUNT(DISTINCT f.flight_id) total_vuelos,
    ROUND(AVG(ms.fare_avg), 2) tarifa_promedio,
    ROUND(STDDEV(ms.fare_avg), 2) desviacion_tarifa,
    ROUND(MIN(ms.fare_avg), 2) tarifa_minima,
    ROUND(MAX(ms.fare_avg), 2) tarifa_maxima,
    ROUND(AVG(ms.market_share_percentage), 2) participacion_promedio
FROM cities c, airports a, routes r, flights f, market_share ms, carriers car
WHERE c.city_market_id = a.city_market_id
AND (a.airport_id = r.origin_airport_id OR a.airport_id = r.destination_airport_id)
AND r.route_id = f.route_id
AND f.flight_id = ms.flight_id
AND ms.carrier_id = car.carrier_id
AND c.state IS NOT NULL
AND ms.fare_avg IS NOT NULL
AND f.year >= 2015
GROUP BY c.state, car.carrier_type, f.year
HAVING COUNT(DISTINCT f.flight_id) >= 15
AND AVG(ms.fare_avg) BETWEEN 100 AND 800
ORDER BY c.state, car.carrier_type, f.year;

-- Consulta 8 - Rutas con mayor variabilidad de precios y competencia estacional
SELECT 
    c1.city_name origen,
    c1.state estado_origen,
    c2.city_name destino,
    c2.state estado_destino,
    f.year,
    COUNT(DISTINCT f.quarter) trimestres_activos,
    COUNT(DISTINCT ms.carrier_id) num_competidores,
    ROUND(AVG(ms.fare_avg), 2) tarifa_promedio_anual,
    ROUND(STDDEV(ms.fare_avg), 2) variabilidad_precios,
    ROUND(MAX(ms.fare_avg) - MIN(ms.fare_avg), 2) rango_precios,
    ROUND(AVG(r.distance_miles), 2) distancia_promedio
FROM cities c1, cities c2, airports a1, airports a2, routes r, flights f, market_share ms
WHERE c1.city_market_id = a1.city_market_id
AND c2.city_market_id = a2.city_market_id
AND a1.airport_id = r.origin_airport_id
AND a2.airport_id = r.destination_airport_id
AND r.route_id = f.route_id
AND f.flight_id = ms.flight_id
AND ms.fare_avg IS NOT NULL
AND r.distance_miles IS NOT NULL
AND f.year >= 2018
GROUP BY c1.city_name, c1.state, c2.city_name, c2.state, f.year
HAVING COUNT(DISTINCT f.quarter) >= 3
AND COUNT(DISTINCT ms.carrier_id) >= 2
AND STDDEV(ms.fare_avg) > 50
ORDER BY f.year, variabilidad_precios DESC, num_competidores DESC;

-- Consulta 9 - Análisis de concentración de mercado por aeropuerto hub
SELECT 
    a.airport_code,
    c.city_name,
    c.state,
    f.year,
    COUNT(DISTINCT r.route_id) total_rutas,
    COUNT(DISTINCT ms.carrier_id) total_carriers,
    ROUND(AVG(ms.market_share_percentage), 2) participacion_promedio,
    ROUND(MAX(ms.market_share_percentage), 2) participacion_maxima,
    car_dominante.carrier_code carrier_dominante,
    car_dominante.carrier_type tipo_dominante,
    CASE 
        WHEN MAX(ms.market_share_percentage) > 50 THEN 'Monopolio'
        WHEN MAX(ms.market_share_percentage) > 30 THEN 'Dominante'
        ELSE 'Competitivo'
    END nivel_concentracion
FROM airports a, cities c, routes r, flights f, market_share ms,
     carriers car_dominante
WHERE a.city_market_id = c.city_market_id
AND a.airport_id = r.origin_airport_id
AND r.route_id = f.route_id
AND f.flight_id = ms.flight_id
AND ms.carrier_id = car_dominante.carrier_id
AND ms.market_share_percentage = (
    SELECT MAX(ms2.market_share_percentage)
    FROM market_share ms2, flights f2, routes r2
    WHERE ms2.flight_id = f2.flight_id
    AND f2.route_id = r2.route_id
    AND r2.origin_airport_id = a.airport_id
    AND f2.year = f.year
)
GROUP BY a.airport_code, c.city_name, c.state, f.year, 
         car_dominante.carrier_code, car_dominante.carrier_type
HAVING COUNT(DISTINCT r.route_id) >= 8
ORDER BY f.year, nivel_concentracion, participacion_maxima DESC;

-- Consulta 10 - Análisis de rentabilidad y eficiencia por distancia y tipo de carrier
SELECT 
    car.carrier_type,
    CASE 
        WHEN r.distance_miles < 300 THEN 'Regional (<300 mi)'
        WHEN r.distance_miles < 800 THEN 'Doméstico corto (300-800 mi)'
        WHEN r.distance_miles < 1500 THEN 'Doméstico medio (800-1500 mi)'
        ELSE 'Doméstico largo (>1500 mi)'
    END categoria_ruta,
    f.year,
    COUNT(DISTINCT f.flight_id) total_vuelos,
    ROUND(AVG(ms.fare_avg), 2) tarifa_promedio,
    ROUND(AVG(r.distance_miles), 2) distancia_promedio,
    ROUND(AVG(ms.fare_avg / r.distance_miles), 4) tarifa_por_milla,
    ROUND(AVG(ms.market_share_percentage), 2) participacion_promedio,
    ROUND(SUM(ms.fare_avg * ms.market_share_percentage / 100), 2) ingresos_ponderados
FROM carriers car, market_share ms, flights f, routes r
WHERE car.carrier_id = ms.carrier_id
AND ms.flight_id = f.flight_id
AND f.route_id = r.route_id
AND r.distance_miles IS NOT NULL
AND ms.fare_avg IS NOT NULL
AND ms.market_share_percentage IS NOT NULL
AND r.distance_miles > 0
AND f.year >= 2020
GROUP BY car.carrier_type, 
         CASE 
             WHEN r.distance_miles < 300 THEN 'Regional (<300 mi)'
             WHEN r.distance_miles < 800 THEN 'Doméstico corto (300-800 mi)'
             WHEN r.distance_miles < 1500 THEN 'Doméstico medio (800-1500 mi)'
             ELSE 'Doméstico largo (>1500 mi)'
         END,
         f.year
HAVING COUNT(DISTINCT f.flight_id) >= 20
ORDER BY f.year, car.carrier_type, tarifa_por_milla DESC;