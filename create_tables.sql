
CREATE TABLE cities (
    city_market_id INTEGER PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    state VARCHAR(2),
    full_city_name VARCHAR(200) NOT NULL
);

CREATE TABLE airports (
    airport_id INTEGER PRIMARY KEY,
    airport_code VARCHAR(3) NOT NULL,
    city_market_id INTEGER NOT NULL,
    FOREIGN KEY (city_market_id) REFERENCES cities(city_market_id)
);

CREATE TABLE carriers (
    carrier_id INTEGER PRIMARY KEY,
    carrier_code VARCHAR(2) NOT NULL UNIQUE,
    carrier_type VARCHAR(10) NOT NULL CHECK (carrier_type IN ('Legacy', 'Low-Cost'))
);

CREATE TABLE routes (
    route_id INTEGER PRIMARY KEY,
    origin_airport_id INTEGER NOT NULL,
    destination_airport_id INTEGER NOT NULL,
    distance_miles DECIMAL(8,2),
    FOREIGN KEY (origin_airport_id) REFERENCES airports(airport_id),
    FOREIGN KEY (destination_airport_id) REFERENCES airports(airport_id),
    UNIQUE(origin_airport_id, destination_airport_id)
);

CREATE TABLE flights (
    flight_id INTEGER PRIMARY KEY,
    route_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    passengers INTEGER,
    fare DECIMAL(10,2),
    source_record_id VARCHAR(50),
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

CREATE TABLE market_share (
    flight_id INTEGER NOT NULL,
    carrier_id INTEGER NOT NULL,
    market_share DECIMAL(5,2),
    fare DECIMAL(10,2),
    PRIMARY KEY (flight_id, carrier_id),
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    FOREIGN KEY (carrier_id) REFERENCES carriers(carrier_id)
);