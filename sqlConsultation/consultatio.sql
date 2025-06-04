--Consulta 1 - Top 5 rutas más transitadas por número de pasajeros:
SELECT 
    c1.city_name AS origin_city,
    c2.city_name AS destination_city,
    r.distance_miles,
    COUNT(f.flight_id) as total_flights,
    ROUND(AVG(f.fare), 2) as avg_fare
FROM flights f
JOIN routes r ON f.route_id = r.route_id
JOIN airports a1 ON r.origin_airport_id = a1.airport_id
JOIN airports a2 ON r.destination_airport_id = a2.airport_id
JOIN cities c1 ON a1.city_market_id = c1.city_market_id
JOIN cities c2 ON a2.city_market_id = c2.city_market_id
GROUP BY c1.city_name, c2.city_name, r.distance_miles
ORDER BY total_flights DESC
LIMIT 5;
--------------------------------------------------
--Consulta 2 - Análisis de participación de mercado por tipo de aerolínea:
SELECT 
    c.carrier_type,
    f.year,
    f.quarter,
    COUNT(DISTINCT ms.carrier_id) as num_carriers,
    ROUND(AVG(ms.market_share_percentage), 2) as avg_market_share,
    ROUND(AVG(ms.fare_avg), 2) as avg_fare
FROM market_share ms
JOIN flights f ON ms.flight_id = f.flight_id
JOIN carriers c ON ms.carrier_id = c.carrier_id
GROUP BY c.carrier_type, f.year, f.quarter
ORDER BY f.year, f.quarter, c.carrier_type;