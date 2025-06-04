DROP TABLE IF EXISTS market_share CASCADE;

DROP TABLE IF EXISTS flights CASCADE;

DROP TABLE IF EXISTS routes CASCADE;

DROP TABLE IF EXISTS carriers CASCADE;

DROP TABLE IF EXISTS airports CASCADE;

DROP TABLE IF EXISTS cities CASCADE;


            CREATE TABLE cities (
                city_market_id INTEGER PRIMARY KEY,
                city_name VARCHAR(150) NOT NULL,
                state VARCHAR(5),
                full_city_name VARCHAR(255)
            );


            CREATE TABLE airports (
                airport_id VARCHAR(255) PRIMARY KEY, 
                airport_code VARCHAR(10) NOT NULL,    
                city_market_id INTEGER,
                FOREIGN KEY (city_market_id) REFERENCES cities(city_market_id) ON DELETE SET NULL
            );


            CREATE TABLE carriers (
                carrier_id INTEGER PRIMARY KEY,
                carrier_code VARCHAR(10) NOT NULL UNIQUE, 
                carrier_type VARCHAR(10) NOT NULL CHECK (carrier_type IN ('Legacy', 'Low-Cost'))
            );


            CREATE TABLE routes (
                route_id INTEGER PRIMARY KEY,
                origin_airport_id VARCHAR(255) NOT NULL, 
                destination_airport_id VARCHAR(255) NOT NULL, 
                distance_miles DECIMAL(10,2), -- Will be NULL due to source data
                FOREIGN KEY (origin_airport_id) REFERENCES airports(airport_id) ON DELETE CASCADE,
                FOREIGN KEY (destination_airport_id) REFERENCES airports(airport_id) ON DELETE CASCADE,
                UNIQUE(origin_airport_id, destination_airport_id)
            );


            CREATE TABLE flights (
                flight_id INTEGER PRIMARY KEY,
                route_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
                passengers VARCHAR(255), -- Changed from INTEGER to VARCHAR to hold raw codes
                fare DECIMAL(10,2),
                source_record_id VARCHAR(100), 
                FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE
            );


            CREATE TABLE market_share (
                market_share_id SERIAL PRIMARY KEY, 
                flight_id INTEGER NOT NULL,
                carrier_id INTEGER NOT NULL,
                market_share_type VARCHAR(10) NOT NULL, 
                market_share_percentage DECIMAL(10,2),
                fare_avg DECIMAL(10,2),
                FOREIGN KEY (flight_id) REFERENCES flights(flight_id) ON DELETE CASCADE,
                FOREIGN KEY (carrier_id) REFERENCES carriers(carrier_id) ON DELETE CASCADE,
                UNIQUE (flight_id, carrier_id, market_share_type) 
            );

