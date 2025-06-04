import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
import os
from sqlalchemy import create_engine
import sys

# --- AWS RDS PostgreSQL Connection Details ---
# IMPORTANT: For production, use environment variables or a secrets manager for credentials.
DB_HOST = "database-2.cjo0kekim2zi.us-east-2.rds.amazonaws.com"
DB_NAME = "proyectobd2"
DB_USER = "postgres"
DB_PASS = "sytpAq-syfci3-cudrud" 
DB_PORT = "5432"
# --- End Connection Details ---

class AirlineDataNormalizer:
    def __init__(self, csv_file_path, db_params):
        self.csv_file_path = csv_file_path
        self.df = None
        self.tables = {}
        self.db_params = db_params
        try:
            self.engine = create_engine(
                f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
            )
        except Exception as e:
            print(f"Error creating SQLAlchemy engine: {e}")
            sys.exit(1)

    def load_data(self):
        print("Loading CSV data...")
        try:
            self.df = pd.read_csv(self.csv_file_path, sep=',', encoding='utf-8',
                                on_bad_lines='skip', low_memory=False)
            print(f"Loaded {len(self.df)} records with {len(self.df.columns)} columns")
            initial_count = len(self.df)

            # Explicitly type critical ID fields as string first to handle mixed types
            id_cols_to_str = ['airportid_1', 'airportid_2', 'citymarketid_1', 'citymarketid_2']
            for col in id_cols_to_str:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str).str.strip()
            
            self.df['airport_1'] = self.df['airport_1'].astype(str).str.strip()
            self.df['airport_2'] = self.df['airport_2'].astype(str).str.strip()
            self.df['carrier_lg'] = self.df['carrier_lg'].astype(str).str.strip()
            self.df['carrier_low'] = self.df['carrier_low'].astype(str).str.strip()

            numeric_cols = ['Year', 'quarter', 'nsmiles', 'passengers', 'fare',
                            'large_ms', 'fare_lg', 'lf_ms', 'fare_low']
            for col in numeric_cols:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # Drop rows if essential IDs for linking are missing AFTER type conversion
            self.df = self.df.dropna(subset=['Year', 'citymarketid_1', 'citymarketid_2', 
                                             'airportid_1', 'airportid_2', 'airport_1', 'airport_2'])

            # Filter out records where passenger data looks like concatenated airport codes
            # This regex looks for 3 or more uppercase letters, typical for airport codes
            if 'passengers' in self.df.columns:
                 self.df = self.df[~self.df['passengers'].astype(str).str.match(r'^[A-Z]{3,}[A-Z]*$')]

            # Filter invalid carrier codes (not 2 chars, or purely numeric, or 'nan')
            def is_valid_carrier(series):
                return (
                    (series.str.len() >= 2) &
                    (~series.str.match(r'^\d+$')) & 
                    (series.str.upper() != 'NAN') &
                    (series.notna())
                )
            self.df = self.df[is_valid_carrier(self.df['carrier_lg'])]
            self.df = self.df[is_valid_carrier(self.df['carrier_low'])]
            
            print(f"After cleaning: {len(self.df)} records ({initial_count - len(self.df)} removed)")
            if self.df.empty:
                print("No data left after cleaning. Halting.")
                return False
            return True

        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_cities_table(self):
        print("Creating Cities table DataFrame...")
        cities_1 = self.df[['citymarketid_1', 'city1']].rename(
            columns={'citymarketid_1': 'city_market_id', 'city1': 'full_city_name'}
        )
        cities_2 = self.df[['citymarketid_2', 'city2']].rename(
            columns={'citymarketid_2': 'city_market_id', 'city2': 'full_city_name'}
        )
        all_cities = pd.concat([cities_1, cities_2])
        all_cities['city_market_id'] = pd.to_numeric(all_cities['city_market_id'], errors='coerce')
        all_cities = all_cities.dropna(subset=['city_market_id', 'full_city_name'])
        all_cities['city_market_id'] = all_cities['city_market_id'].astype(int)
        all_cities = all_cities.drop_duplicates(subset=['city_market_id']).reset_index(drop=True)

        all_cities_split = all_cities['full_city_name'].str.extract(r'^(.*?)(?:,\s*([A-Z]{2}))?(?:\s*\(.*\))?$')
        all_cities['city_name'] = all_cities_split[0].str.strip()
        all_cities['state'] = all_cities_split[1].str.strip()
        
        self.tables['cities'] = all_cities[['city_market_id', 'city_name', 'state', 'full_city_name']]
        print(f"Created Cities DataFrame with {len(self.tables['cities'])} unique cities")

    def create_airports_table(self):
        print("Creating Airports table DataFrame...")
        airports_1 = self.df[['airportid_1', 'airport_1', 'citymarketid_1']].rename(
            columns={'airportid_1': 'airport_id', 'airport_1': 'airport_code', 'citymarketid_1': 'city_market_id'}
        )
        airports_2 = self.df[['airportid_2', 'airport_2', 'citymarketid_2']].rename(
            columns={'airportid_2': 'airport_id', 'airport_2': 'airport_code', 'citymarketid_2': 'city_market_id'}
        )
        all_airports = pd.concat([airports_1, airports_2])
        all_airports['city_market_id'] = pd.to_numeric(all_airports['city_market_id'], errors='coerce')
        all_airports = all_airports.dropna(subset=['airport_id', 'airport_code', 'city_market_id'])
        all_airports['city_market_id'] = all_airports['city_market_id'].astype(int)
        all_airports['airport_id'] = all_airports['airport_id'].astype(str) # Ensure airport_id is string
        all_airports = all_airports.drop_duplicates(subset=['airport_id']).reset_index(drop=True)

        valid_city_market_ids = self.tables['cities']['city_market_id'].unique()
        all_airports = all_airports[all_airports['city_market_id'].isin(valid_city_market_ids)]

        self.tables['airports'] = all_airports[['airport_id', 'airport_code', 'city_market_id']]
        print(f"Created Airports DataFrame with {len(self.tables['airports'])} unique airports")

    def create_carriers_table(self):
        print("Creating Carriers table DataFrame...")
        large_carriers = self.df[['carrier_lg']].rename(columns={'carrier_lg': 'carrier_code'})
        large_carriers['carrier_type'] = 'Legacy'
        low_carriers = self.df[['carrier_low']].rename(columns={'carrier_low': 'carrier_code'})
        low_carriers['carrier_type'] = 'Low-Cost'
        
        all_carriers = pd.concat([large_carriers, low_carriers])
        all_carriers = all_carriers.dropna(subset=['carrier_code'])
        all_carriers = all_carriers[
            (all_carriers['carrier_code'].str.len() >= 2) &
            (~all_carriers['carrier_code'].str.match(r'^\d+$')) & 
            (all_carriers['carrier_code'].str.upper() != 'NAN')
        ]
        all_carriers = all_carriers.drop_duplicates(subset=['carrier_code']).reset_index(drop=True)
        all_carriers['carrier_id'] = all_carriers.index + 1 # Simple integer ID
        self.tables['carriers'] = all_carriers[['carrier_id', 'carrier_code', 'carrier_type']]
        print(f"Created Carriers DataFrame with {len(self.tables['carriers'])} unique carriers")

    def create_routes_table(self):
        print("Creating Routes table DataFrame...")
        routes_df = self.df[['airportid_1', 'airportid_2', 'nsmiles']].rename(
            columns={'airportid_1': 'origin_airport_id', 'airportid_2': 'destination_airport_id', 'nsmiles': 'distance_miles'}
        ).copy() # Use .copy() to avoid SettingWithCopyWarning
        routes_df['origin_airport_id'] = routes_df['origin_airport_id'].astype(str)
        routes_df['destination_airport_id'] = routes_df['destination_airport_id'].astype(str)
        routes_df = routes_df.dropna(subset=['origin_airport_id', 'destination_airport_id'])
        
        valid_airport_ids = self.tables['airports']['airport_id'].unique()
        routes_df = routes_df[
            routes_df['origin_airport_id'].isin(valid_airport_ids) &
            routes_df['destination_airport_id'].isin(valid_airport_ids)
        ]

        routes_grouped = routes_df.groupby(['origin_airport_id', 'destination_airport_id']).agg(
            distance_miles=('distance_miles', lambda x: x.mode()[0] if not x.mode().empty and pd.notna(x.mode()[0]) else x.mean())
        ).reset_index()
        routes_grouped['route_id'] = routes_grouped.index + 1
        self.tables['routes'] = routes_grouped[['route_id', 'origin_airport_id', 'destination_airport_id', 'distance_miles']]
        print(f"Created Routes DataFrame with {len(self.tables['routes'])} unique routes")

    def create_flights_table(self):
        print("Creating Flights table DataFrame...")
        flights_df = self.df.copy()
        flights_df['airportid_1'] = flights_df['airportid_1'].astype(str)
        flights_df['airportid_2'] = flights_df['airportid_2'].astype(str)
        
        route_mapping = self.tables['routes'].set_index(['origin_airport_id', 'destination_airport_id'])['route_id']
        
        flights_df['route_id'] = flights_df.apply(
            lambda row: route_mapping.get((row['airportid_1'], row['airportid_2'])), axis=1
        )
        flights_df = flights_df.dropna(subset=['route_id'])
        flights_df['route_id'] = flights_df['route_id'].astype(int)
        
        flights_df = flights_df.reset_index(drop=True)
        flights_df['flight_id'] = flights_df.index + 1
        
        self.tables['flights'] = flights_df[[
            'flight_id', 'route_id', 'Year', 'quarter', 'passengers', 'fare', 'tbl1apk'
        ]].rename(columns={'Year': 'year', 'tbl1apk': 'source_record_id'})
        print(f"Created Flights DataFrame with {len(self.tables['flights'])} flight records")

    def create_market_share_table(self):
        print("Creating Market Share table DataFrame...")
        market_shares_list = []
        carrier_mapping = self.tables['carriers'].set_index('carrier_code')['carrier_id']
        
        flights_with_source_id = self.tables['flights'][['flight_id', 'source_record_id']].copy()
        # Merge df (original cleaned data) with the newly created flight_ids
        temp_df = self.df.merge(flights_with_source_id, left_on='tbl1apk', right_on='source_record_id', how='inner')

        for _, row in temp_df.iterrows():
            flight_id = row['flight_id']
            
            if pd.notna(row['carrier_lg']) and row['carrier_lg'] in carrier_mapping:
                market_shares_list.append({
                    'flight_id': flight_id,
                    'carrier_id': carrier_mapping[row['carrier_lg']],
                    'market_share_type': 'Legacy',
                    'market_share_percentage': row['large_ms'],
                    'fare_avg': row['fare_lg']
                })
            if pd.notna(row['carrier_low']) and row['carrier_low'] in carrier_mapping:
                 market_shares_list.append({
                    'flight_id': flight_id,
                    'carrier_id': carrier_mapping[row['carrier_low']],
                    'market_share_type': 'Low-Cost',
                    'market_share_percentage': row['lf_ms'],
                    'fare_avg': row['fare_low']
                })
        self.tables['market_share'] = pd.DataFrame(market_shares_list)
        if not self.tables['market_share'].empty:
            self.tables['market_share'] = self.tables['market_share'].drop_duplicates(subset=['flight_id', 'carrier_id', 'market_share_type'])
        print(f"Created Market Share DataFrame with {len(self.tables['market_share'])} records")

    def normalize_data(self):
        if not self.load_data(): return False
        if self.df.empty: return False # Check if load_data resulted in empty df
        self.create_cities_table()
        self.create_airports_table()
        self.create_carriers_table()
        self.create_routes_table()
        self.create_flights_table()
        self.create_market_share_table()
        return True

    def generate_postgres_ddl(self):
        # DDL statements: Drop tables if they exist, then create them.
        # CASCADE will drop dependent objects like views or foreign key constraints.
        ddl = [
            "DROP TABLE IF EXISTS market_share CASCADE;",
            "DROP TABLE IF EXISTS flights CASCADE;",
            "DROP TABLE IF EXISTS routes CASCADE;",
            "DROP TABLE IF EXISTS carriers CASCADE;",
            "DROP TABLE IF EXISTS airports CASCADE;",
            "DROP TABLE IF EXISTS cities CASCADE;",
            """
            CREATE TABLE cities (
                city_market_id INTEGER PRIMARY KEY,
                city_name VARCHAR(150) NOT NULL,
                state VARCHAR(5),
                full_city_name VARCHAR(255)
            );""",
            """
            CREATE TABLE airports (
                airport_id VARCHAR(255) PRIMARY KEY, -- Changed from INTEGER to VARCHAR to match data
                airport_code VARCHAR(10) NOT NULL,    -- Increased size for airport_code flexibility
                city_market_id INTEGER,
                FOREIGN KEY (city_market_id) REFERENCES cities(city_market_id) ON DELETE SET NULL
            );""",
            """
            CREATE TABLE carriers (
                carrier_id INTEGER PRIMARY KEY,
                carrier_code VARCHAR(10) NOT NULL UNIQUE, -- Increased size
                carrier_type VARCHAR(10) NOT NULL CHECK (carrier_type IN ('Legacy', 'Low-Cost'))
            );""",
            """
            CREATE TABLE routes (
                route_id INTEGER PRIMARY KEY,
                origin_airport_id VARCHAR(255) NOT NULL, -- Changed from INTEGER to VARCHAR
                destination_airport_id VARCHAR(255) NOT NULL, -- Changed from INTEGER to VARCHAR
                distance_miles DECIMAL(10,2),
                FOREIGN KEY (origin_airport_id) REFERENCES airports(airport_id) ON DELETE CASCADE,
                FOREIGN KEY (destination_airport_id) REFERENCES airports(airport_id) ON DELETE CASCADE,
                UNIQUE(origin_airport_id, destination_airport_id)
            );""",
            """
            CREATE TABLE flights (
                flight_id INTEGER PRIMARY KEY,
                route_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
                passengers INTEGER,
                fare DECIMAL(10,2),
                source_record_id VARCHAR(100), -- Original record key from CSV
                FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE
            );""",
            """
            CREATE TABLE market_share (
                market_share_id SERIAL PRIMARY KEY, -- Surrogate key for this table
                flight_id INTEGER NOT NULL,
                carrier_id INTEGER NOT NULL,
                market_share_type VARCHAR(10) NOT NULL, -- 'Legacy' or 'Low-Cost'
                market_share_percentage DECIMAL(10,2),
                fare_avg DECIMAL(10,2),
                FOREIGN KEY (flight_id) REFERENCES flights(flight_id) ON DELETE CASCADE,
                FOREIGN KEY (carrier_id) REFERENCES carriers(carrier_id) ON DELETE CASCADE,
                UNIQUE (flight_id, carrier_id, market_share_type) -- Ensure one entry per type for a flight/carrier combo
            );"""
        ]
        return ddl

    def create_db_schema_and_insert_data(self):
        print(f"Connecting to PostgreSQL: dbname='{self.db_params['dbname']}' host='{self.db_params['host']}'")
        ddl_statements = self.generate_postgres_ddl()
        try:
            with psycopg2.connect(**self.db_params) as conn:
                with conn.cursor() as cur:
                    print("Dropping and Creating tables...")
                    for statement in ddl_statements:
                        cur.execute(statement)
                    conn.commit()
                    print("Tables created successfully.")

                print("Inserting data into tables using SQLAlchemy engine...")
                table_order = ['cities', 'airports', 'carriers', 'routes', 'flights', 'market_share']
                for table_name in table_order:
                    if table_name in self.tables and not self.tables[table_name].empty:
                        df_to_insert = self.tables[table_name].copy()
                        # Replace Pandas NaT/NaN with None for SQL compatibility
                        df_to_insert = df_to_insert.replace({pd.NaT: None, np.nan: None})
                        print(f"Inserting data into {table_name} ({len(df_to_insert)} records)...")
                        try:
                            df_to_insert.to_sql(table_name, self.engine, if_exists='append', index=False, method='multi', chunksize=1000)
                            print(f"Successfully inserted data into {table_name}.")
                        except Exception as e_insert:
                            print(f"SQLAlchemy to_sql Error for table {table_name}: {e_insert}")
                            print("Sample of data that might be causing issues:")
                            print(df_to_insert.head())
                            # Attempt to get more detailed error from Psycopg2 if possible
                            if hasattr(e_insert, 'orig') and e_insert.orig:
                                print(f"Original Psycopg2 error: {e_insert.orig}")
                            conn.rollback() 
                            return False 
                    elif table_name not in self.tables:
                        print(f"Table DataFrame '{table_name}' not found. Skipping.")
                    else: # Table is empty
                        print(f"Table DataFrame '{table_name}' is empty. Skipping insertion.")
                conn.commit() # This commit is actually handled by to_sql for each table with a transaction
                print("All data insertion processes attempted.")
                return True
        except psycopg2.Error as e_conn:
            print(f"PostgreSQL Connection/Execution Error: {e_conn}")
            if hasattr(e_conn, 'pgcode'): print(f"PGCODE: {e_conn.pgcode}")
            if hasattr(e_conn, 'pgerror'): print(f"PGERROR: {e_conn.pgerror}")
            return False
        except Exception as e_generic:
            print(f"An unexpected error occurred during DB operations: {e_generic}")
            import traceback
            traceback.print_exc()
            return False

    def print_summary(self):
        print("\n" + "="*60)
        print("NORMALIZED DATA SUMMARY (Pandas DataFrames)")
        print("="*60)
        for table_name, table_df in self.tables.items():
            print(f"\n{table_name.upper()} TABLE:")
            print(f"  Records: {len(table_df):,}")
            print(f"  Columns: {list(table_df.columns)}")
            if not table_df.empty:
                try:
                    print(f"  Sample: {dict(table_df.iloc[0])}")
                except IndexError:
                    print("  Sample: DataFrame is not empty but could not get first row.")
            else:
                print("  Sample: DataFrame is empty.")

def main():
    db_connection_params = {
        "host": DB_HOST,
        "dbname": DB_NAME,
        "user": DB_USER,
        "password": DB_PASS,
        "port": DB_PORT,
    }
    print("Starting airline data normalization and database population process for PostgreSQL...")
    print("WARNING: This script will DROP and RECREATE tables in the specified database.")
    
    normalizer = AirlineDataNormalizer(
        csv_file_path='archive/US Airline Flight Routes and Fares 1993-2024.csv',
        db_params=db_connection_params
    )

    if normalizer.normalize_data():
        normalizer.print_summary()
        if normalizer.create_db_schema_and_insert_data():
            print("\n✅ Normalization and database population complete!")
            print(f"🗄️  Data should now be in PostgreSQL database '{DB_NAME}' on host '{DB_HOST}'.")
            ddl_statements = normalizer.generate_postgres_ddl()
            ddl_file_path = 'create_postgres_tables.sql'
            with open(ddl_file_path, 'w') as f:
                for stmt in ddl_statements:
                    f.write(stmt + '\n\n') # Add double newline for better readability
            print(f"📜 PostgreSQL DDL statements saved to '{ddl_file_path}'")
        else:
            print("\n❌ Database schema creation or data insertion failed.")
    else:
        print("\n❌ Data normalization process failed (e.g., data cleaning resulted in no data).")

if __name__ == "__main__":
    main() 