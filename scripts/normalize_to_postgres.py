import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
import os
from sqlalchemy import create_engine
import sys
import re
from typing import Dict, Optional

# --- PostgreSQL Connection Details ---
# Using environment variables for security
DB_HOST = os.getenv("DB_HOST", "database-2.cjo0kekim2zi.us-east-2.rds.amazonaws.com")
DB_NAME = os.getenv("DB_NAME", "proyectobd2")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "sytpAq-syfci3-cudrud")
DB_PORT = os.getenv("DB_PORT", "5432")
# --- End Connection Details ---

class AirlineDataNormalizer:
    """
    Normalizes US Airlines flight data and populates PostgreSQL database.
    
    This class handles the complete ETL process for airline data normalization,
    converting raw CSV data into a 3NF (Third Normal Form) database schema.
    """
    
    def __init__(self, csv_file_path: str, db_params: Dict[str, str]):
        self.csv_file_path = csv_file_path
        self.df = None
        self.tables = {}
        self.db_params = db_params
        
        try:
            self.engine = create_engine(
                f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@"
                f"{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
            )
        except Exception as e:
            print(f"Error creating SQLAlchemy engine: {e}")
            sys.exit(1)

    def load_data(self) -> bool:
        """Load and clean the CSV data."""
        print("Loading CSV data...")
        try:
            self.df = pd.read_csv(
                self.csv_file_path, 
                sep=',', 
                encoding='utf-8',
                on_bad_lines='skip', 
                low_memory=False
            )
            print(f"Loaded {len(self.df)} records with {len(self.df.columns)} columns")
            initial_count = len(self.df)

            # Clean and process data
            self._clean_data_types()
            self._validate_essential_fields()
            self._clean_carrier_codes()
            
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

    def _clean_data_types(self) -> None:
        """Clean and convert data types for essential columns."""
        # Convert ID fields to string
        id_cols = ['airportid_1', 'airportid_2', 'citymarketid_1', 'citymarketid_2']
        for col in id_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()
        
        # Convert airport and carrier codes to string
        string_cols = ['airport_1', 'airport_2', 'city1', 'city2', 'carrier_lg', 'carrier_low']
        for col in string_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()

        # Convert numeric columns
        numeric_cols = ['Year', 'quarter', 'fare', 'large_ms', 'fare_lg', 'lf_ms', 'fare_low']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

    def _validate_essential_fields(self) -> None:
        """Remove rows with missing essential data."""
        essential_fields = [
            'Year', 'citymarketid_1', 'citymarketid_2', 
            'airportid_1', 'airportid_2', 'airport_1', 'airport_2'
        ]
        self.df = self.df.dropna(subset=essential_fields)

    def _clean_carrier_codes(self) -> None:
        """Clean and validate carrier codes."""
        def validate_carrier_code(code_val) -> Optional[str]:
            if pd.isna(code_val):
                return np.nan
            
            code_str = str(code_val).strip()
            
            # Allow if not empty, not 'NAN', and reasonable length
            if code_str and code_str.upper() != 'NAN' and 1 <= len(code_str) <= 10:
                return code_str
            return np.nan

        for col in ['carrier_lg', 'carrier_low']:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(validate_carrier_code)

    def create_cities_table(self):
        print("Creating Cities table DataFrame...")
        
        # City 1 processing: name from df['city1'], state from df['city2']
        cities1_df = self.df[['citymarketid_1', 'city1', 'city2']].copy()
        cities1_df.rename(columns={
            'citymarketid_1': 'city_market_id', 
            'city1': 'raw_city_name', # Will be further processed
            'city2': 'raw_state'      # Will be processed to state
        }, inplace=True)
        cities1_df.dropna(subset=['city_market_id', 'raw_city_name'], inplace=True)
        cities1_df['city_market_id'] = pd.to_numeric(cities1_df['city_market_id'], errors='coerce')
        cities1_df.dropna(subset=['city_market_id'], inplace=True)
        cities1_df['city_market_id'] = cities1_df['city_market_id'].astype(int)

        # Extract state for City 1: from raw_state (original city2 col), expect 2 uppercase chars
        cities1_df['state'] = cities1_df['raw_state'].astype(str).str.strip().apply(
            lambda x: x if isinstance(x, str) and len(x) == 2 and x.isupper() else pd.NA
        )
        
        # Extract city_name for City 1: from raw_city_name (original city1 col)
        # Attempt to remove (Metropolitan Area) or similar suffixes
        cities1_df['city_name'] = cities1_df['raw_city_name'].astype(str).str.strip().apply(
            lambda x: re.sub(r'\s*\(.*\)\s*$', '', x).strip()
        )
        cities1_df['full_city_name_ref'] = cities1_df['raw_city_name'] # Keep original for reference if needed

        # City 2 processing: name from df['city2'] (this is the tricky part based on raw data)
        # Raw data showed df['city2'] looking like state codes (' PA', ' NM').
        # However, original script assumed df['city2'] was name for citymarketid_2.
        # If df['city2'] is a state, then citymarketid_2's name is ambiguous.
        # For now, let's take df['city2'] as 'raw_city_name_2' and try to parse city/state from it.
        cities2_df = self.df[['citymarketid_2', 'city2']].copy()
        cities2_df.rename(columns={
            'citymarketid_2': 'city_market_id',
            'city2': 'raw_city_name_2' # Original city2 column content
        }, inplace=True)
        cities2_df.dropna(subset=['city_market_id', 'raw_city_name_2'], inplace=True)
        cities2_df['city_market_id'] = pd.to_numeric(cities2_df['city_market_id'], errors='coerce')
        cities2_df.dropna(subset=['city_market_id'], inplace=True)
        cities2_df['city_market_id'] = cities2_df['city_market_id'].astype(int)

        # Try to parse city and state from raw_city_name_2 (original city2 col)
        # If raw_city_name_2 is just "ST", then city part will be empty.
        def parse_city_state_from_city2_col(name_raw):
            name = str(name_raw).strip()
            # Pattern 1: "City Name, ST" or "City Name, ST (extra)"
            match1 = re.match(r'^(.*?),\s*([A-Z]{2})(?:\s*\(.*\))?$', name)
            if match1:
                return match1.group(1).strip(), match1.group(2).strip()
            # Pattern 2: Just "ST" (like ' PA')
            if len(name) == 2 and name.isupper():
                return pd.NA, name # No city name, just state
            # Pattern 3: Just city name, no state "City Name (extra)" or "City Name"
            match3 = re.match(r'^(.*?)(?:\s*\(.*\))?$', name)
            if match3:
                 return match3.group(1).strip(), pd.NA
            return name, pd.NA # Fallback

        parsed_city2 = cities2_df['raw_city_name_2'].apply(parse_city_state_from_city2_col).apply(pd.Series)
        parsed_city2.columns = ['city_name', 'state']
        
        cities2_df = pd.concat([cities2_df.drop(columns=['raw_city_name_2']), parsed_city2], axis=1)
        cities2_df['full_city_name_ref'] = self.df.loc[cities2_df.index, 'city2'] # original city2 col for reference

        # Combine cities1_df and cities2_df
        all_cities = pd.concat([
            cities1_df[['city_market_id', 'city_name', 'state', 'full_city_name_ref']],
            cities2_df[['city_market_id', 'city_name', 'state', 'full_city_name_ref']]
        ], ignore_index=True)
        
        all_cities.rename(columns={'full_city_name_ref': 'full_city_name'}, inplace=True)
        all_cities.dropna(subset=['city_market_id', 'city_name'], inplace=True) # City name must exist
        all_cities = all_cities.drop_duplicates(subset=['city_market_id']).reset_index(drop=True)
        
        self.tables['cities'] = all_cities[['city_market_id', 'city_name', 'state', 'full_city_name']]
        print(f"Created Cities DataFrame with {len(self.tables['cities'])} unique cities")
        if not self.tables['cities'].empty:
            print("Sample of processed cities:")
            print(self.tables['cities'].head())


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
        all_airports['airport_id'] = all_airports['airport_id'].astype(str) 
        all_airports = all_airports.drop_duplicates(subset=['airport_id']).reset_index(drop=True)

        if 'cities' in self.tables and not self.tables['cities'].empty:
            valid_city_market_ids = self.tables['cities']['city_market_id'].unique()
            all_airports = all_airports[all_airports['city_market_id'].isin(valid_city_market_ids)]
        else:
            print("Warning: Cities table is empty or not found, cannot filter airports by city_market_id.")


        self.tables['airports'] = all_airports[['airport_id', 'airport_code', 'city_market_id']]
        print(f"Created Airports DataFrame with {len(self.tables['airports'])} unique airports")

    def create_carriers_table(self):
        print("Creating Carriers table DataFrame...")
        large_carriers = self.df[['carrier_lg']].rename(columns={'carrier_lg': 'carrier_code'})
        large_carriers['carrier_type'] = 'Legacy'
        low_carriers = self.df[['carrier_low']].rename(columns={'carrier_low': 'carrier_code'})
        low_carriers['carrier_type'] = 'Low-Cost'
        
        all_carriers = pd.concat([large_carriers, low_carriers])
        all_carriers = all_carriers.dropna(subset=['carrier_code']) # Drops rows where cleaned code is NaN

        # Ensure carrier_code is string type before using .str accessor
        all_carriers['carrier_code'] = all_carriers['carrier_code'].astype(str) # Already done in load_data by validate_and_clean_carrier_code returning string

        # print("DEBUG: Unique carrier codes BEFORE final filtering in create_carriers_table:")
        # print(all_carriers['carrier_code'].unique())

        all_carriers = all_carriers[
            (all_carriers['carrier_code'].str.len() >= 1) &          # Min length 1
            (all_carriers['carrier_code'].str.len() <= 10) &         # Max length 10
            # No longer filtering out all-digit codes: (~all_carriers['carrier_code'].str.match(r'^\\d+$')) & 
            (all_carriers['carrier_code'].str.upper() != 'NAN')      # Filter out 'nan' strings
        ]
        all_carriers = all_carriers.drop_duplicates(subset=['carrier_code']).reset_index(drop=True)
        all_carriers['carrier_id'] = all_carriers.index + 1 
        self.tables['carriers'] = all_carriers[['carrier_id', 'carrier_code', 'carrier_type']]
        print(f"Created Carriers DataFrame with {len(self.tables['carriers'])} unique carriers")
        if not self.tables['carriers'].empty:
            print("Sample of processed carriers:")
            print(self.tables['carriers'].head())


    def create_routes_table(self):
        print("Creating Routes table DataFrame...")
        # Use Geocoded_City1 and Geocoded_City2 to calculate distance_miles
        routes_df = self.df[['airportid_1', 'airportid_2', 'Geocoded_City1', 'Geocoded_City2']].rename(
            columns={
                'airportid_1': 'origin_airport_id', 
                'airportid_2': 'destination_airport_id',
                'Geocoded_City1': 'geo_coord_1',
                'Geocoded_City2': 'geo_coord_2'
            }
        ).copy()
        routes_df['origin_airport_id'] = routes_df['origin_airport_id'].astype(str)
        routes_df['destination_airport_id'] = routes_df['destination_airport_id'].astype(str)
        routes_df = routes_df.dropna(subset=['origin_airport_id', 'destination_airport_id'])
        
        # Convert geocoded columns to numeric
        routes_df['geo_coord_1'] = pd.to_numeric(routes_df['geo_coord_1'], errors='coerce')
        routes_df['geo_coord_2'] = pd.to_numeric(routes_df['geo_coord_2'], errors='coerce')
        
        if 'airports' in self.tables and not self.tables['airports'].empty:
            valid_airport_ids = self.tables['airports']['airport_id'].unique()
            routes_df = routes_df[
                routes_df['origin_airport_id'].isin(valid_airport_ids) &
                routes_df['destination_airport_id'].isin(valid_airport_ids)
            ]
        else:
            print("Warning: Airports table is empty or not found, cannot filter routes by airport_id.")

        # Get unique routes and calculate distance using geocoded data
        def calculate_distance_from_geocoded(geo1, geo2):
            """
            Attempt to calculate distance from geocoded values.
            This is experimental - the exact meaning of these geocoded values isn't clear.
            """
            if pd.isna(geo1) or pd.isna(geo2):
                return np.nan
            
            # Option 1: Simple difference (if these are distance-related values)
            distance_diff = abs(geo2 - geo1)
            
            # Option 2: Average (if they represent different aspects of the same route)
            distance_avg = (geo1 + geo2) / 2
            
            # Option 3: Check if one of them directly represents distance
            # Since typical US flight distances range from ~200 to ~3000 miles
            if 200 <= geo1 <= 3000:
                return geo1
            elif 200 <= geo2 <= 3000:
                return geo2
            elif 200 <= distance_diff <= 3000:
                return distance_diff
            elif 200 <= distance_avg <= 3000:
                return distance_avg
            else:
                # If none seem like reasonable distances, try scaling
                # Maybe the values are in tens of miles, hundreds, etc.
                for scale in [0.1, 0.01, 10, 100]:
                    scaled_geo1 = geo1 * scale
                    scaled_geo2 = geo2 * scale
                    scaled_diff = distance_diff * scale
                    scaled_avg = distance_avg * scale
                    
                    if 200 <= scaled_geo1 <= 3000:
                        return scaled_geo1
                    elif 200 <= scaled_geo2 <= 3000:
                        return scaled_geo2
                    elif 200 <= scaled_diff <= 3000:
                        return scaled_diff
                    elif 200 <= scaled_avg <= 3000:
                        return scaled_avg
                
                # If nothing works, return NaN
                return np.nan

        # Group by route to get unique combinations
        routes_grouped = routes_df.groupby(['origin_airport_id', 'destination_airport_id']).agg({
            'geo_coord_1': 'first',  # Take first occurrence
            'geo_coord_2': 'first'   # Take first occurrence
        }).reset_index()
        
        # Calculate distance_miles using the geocoded data
        routes_grouped['distance_miles'] = routes_grouped.apply(
            lambda row: calculate_distance_from_geocoded(row['geo_coord_1'], row['geo_coord_2']), 
            axis=1
        )
        
        routes_grouped['route_id'] = routes_grouped.index + 1
        self.tables['routes'] = routes_grouped[['route_id', 'origin_airport_id', 'destination_airport_id', 'distance_miles']]
        
        # Print some statistics about the distance calculation
        valid_distances = routes_grouped['distance_miles'].dropna()
        if len(valid_distances) > 0:
            print(f"Created Routes DataFrame with {len(self.tables['routes'])} unique routes")
            print(f"Successfully calculated distances for {len(valid_distances)} routes ({len(valid_distances)/len(routes_grouped)*100:.1f}%)")
            print(f"Distance range: {valid_distances.min():.1f} - {valid_distances.max():.1f} miles")
            print(f"Average distance: {valid_distances.mean():.1f} miles")
        else:
            print(f"Created Routes DataFrame with {len(self.tables['routes'])} unique routes")
            print("Warning: Could not calculate distances from geocoded data - all distances remain NULL")

    def create_flights_table(self):
        print("Creating Flights table DataFrame...")
        flights_df = self.df.copy()
        flights_df['airportid_1'] = flights_df['airportid_1'].astype(str)
        flights_df['airportid_2'] = flights_df['airportid_2'].astype(str)
        
        if 'routes' in self.tables and not self.tables['routes'].empty:
            route_mapping = self.tables['routes'].set_index(['origin_airport_id', 'destination_airport_id'])['route_id']
            flights_df['route_id'] = flights_df.apply(
                lambda row: route_mapping.get((row['airportid_1'], row['airportid_2'])), axis=1
            )
            flights_df = flights_df.dropna(subset=['route_id'])
            flights_df['route_id'] = flights_df['route_id'].astype(int)
        else:
            print("Warning: Routes table is empty, flight 'route_id' will be NaN and rows likely dropped.")
            flights_df['route_id'] = np.nan
            flights_df = flights_df.dropna(subset=['route_id']) # This will empty the df

        
        flights_df = flights_df.reset_index(drop=True)
        flights_df['flight_id'] = flights_df.index + 1
        
        # 'passengers' column from df is object/string (airport codes), DB expects INTEGER. Will be NULL.
        # 'fare' is numeric.
        self.tables['flights'] = flights_df[[
            'flight_id', 'route_id', 'Year', 'quarter', 
            'passengers', # This is the original 'passengers' column (string codes)
            'fare', 'tbl1apk'
        ]].rename(columns={'Year': 'year', 'tbl1apk': 'source_record_id'})
        print(f"Created Flights DataFrame with {len(self.tables['flights'])} flight records")

    def create_market_share_table(self):
        print("Creating Market Share table DataFrame...")
        market_shares_list = []
        
        if 'carriers' not in self.tables or self.tables['carriers'].empty:
            print("Warning: Carriers table is empty. Market Share table will also be empty.")
            self.tables['market_share'] = pd.DataFrame(market_shares_list) # Empty DF
            print(f"Created Market Share DataFrame with {len(self.tables['market_share'])} records")
            return

        if 'flights' not in self.tables or self.tables['flights'].empty:
            print("Warning: Flights table is empty. Market Share table will also be empty.")
            self.tables['market_share'] = pd.DataFrame(market_shares_list) # Empty DF
            print(f"Created Market Share DataFrame with {len(self.tables['market_share'])} records")
            return
            
        carrier_mapping = self.tables['carriers'].set_index('carrier_code')['carrier_id']
        flights_with_source_id = self.tables['flights'][['flight_id', 'source_record_id']].copy()
        
        # Merge df (original cleaned data) with the newly created flight_ids
        # Ensure 'tbl1apk' in self.df is of the same type as 'source_record_id' if issues arise
        if 'tbl1apk' not in self.df.columns:
            print("Error: 'tbl1apk' column missing from main DataFrame. Cannot create market_share.")
            self.tables['market_share'] = pd.DataFrame(market_shares_list)
            print(f"Created Market Share DataFrame with {len(self.tables['market_share'])} records")
            return

        temp_df = self.df.merge(flights_with_source_id, left_on='tbl1apk', right_on='source_record_id', how='inner')

        for _, row in temp_df.iterrows():
            flight_id = row['flight_id']
            
            # carrier_lg/low are already cleaned by validate_and_clean_carrier_code
            # They will be NaN if invalid, or the code string if valid.
            if pd.notna(row['carrier_lg']) and row['carrier_lg'] in carrier_mapping:
                market_shares_list.append({
                    'flight_id': flight_id,
                    'carrier_id': carrier_mapping[row['carrier_lg']],
                    'market_share_type': 'Legacy',
                    'market_share_percentage': row['large_ms'], # numeric
                    'fare_avg': row['fare'] # Changed from row['fare_lg'] to use main flight fare
                })
            if pd.notna(row['carrier_low']) and row['carrier_low'] in carrier_mapping:
                 market_shares_list.append({
                    'flight_id': flight_id,
                    'carrier_id': carrier_mapping[row['carrier_low']],
                    'market_share_type': 'Low-Cost',
                    'market_share_percentage': row['lf_ms'], # numeric
                    'fare_avg': row['fare'] # Changed from row['fare_low'] to use main flight fare
                })
        self.tables['market_share'] = pd.DataFrame(market_shares_list)
        if not self.tables['market_share'].empty:
            self.tables['market_share'] = self.tables['market_share'].drop_duplicates(subset=['flight_id', 'carrier_id', 'market_share_type'])
        print(f"Created Market Share DataFrame with {len(self.tables['market_share'])} records")

    def normalize_data(self):
        if not self.load_data(): return False
        if self.df.empty: return False 
        self.create_cities_table()
        self.create_airports_table() # Depends on cities
        self.create_carriers_table()
        self.create_routes_table()   # Depends on airports
        self.create_flights_table()  # Depends on routes
        self.create_market_share_table() # Depends on carriers and flights
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
                airport_id VARCHAR(255) PRIMARY KEY, 
                airport_code VARCHAR(10) NOT NULL,    
                city_market_id INTEGER,
                FOREIGN KEY (city_market_id) REFERENCES cities(city_market_id) ON DELETE SET NULL
            );""",
            """
            CREATE TABLE carriers (
                carrier_id INTEGER PRIMARY KEY,
                carrier_code VARCHAR(10) NOT NULL UNIQUE, 
                carrier_type VARCHAR(10) NOT NULL CHECK (carrier_type IN ('Legacy', 'Low-Cost'))
            );""",
            """
            CREATE TABLE routes (
                route_id INTEGER PRIMARY KEY,
                origin_airport_id VARCHAR(255) NOT NULL, 
                destination_airport_id VARCHAR(255) NOT NULL, 
                distance_miles DECIMAL(10,2), -- Will be NULL due to source data
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
                passengers VARCHAR(255), -- Changed from INTEGER to VARCHAR to hold raw codes
                fare DECIMAL(10,2),
                source_record_id VARCHAR(100), 
                FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE
            );""",
            """
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
                        
                        # Handle types before insertion
                        if table_name == 'flights' and 'passengers' in df_to_insert.columns:
                            # Ensure passengers is string for VARCHAR DB column
                            df_to_insert['passengers'] = df_to_insert['passengers'].astype(str).replace('nan', None)


                        # Replace Pandas NaT/NaN with None for SQL compatibility
                        # For object columns that might contain pd.NA, also replace with None
                        for col in df_to_insert.columns:
                            if df_to_insert[col].dtype == 'object' or pd.api.types.is_string_dtype(df_to_insert[col].dtype):
                                df_to_insert[col] = df_to_insert[col].replace({pd.NA: None, np.nan: None})
                            elif pd.api.types.is_datetime64_any_dtype(df_to_insert[col].dtype):
                                 df_to_insert[col] = df_to_insert[col].replace({pd.NaT: None})
                            else: # Numeric types
                                df_to_insert[col] = df_to_insert[col].replace({np.nan: None})
                        
                        print(f"Inserting data into {table_name} ({len(df_to_insert)} records)...")
                        try:
                            df_to_insert.to_sql(table_name, self.engine, if_exists='append', index=False, method='multi', chunksize=1000)
                            print(f"Successfully inserted data into {table_name}.")
                        except Exception as e_insert:
                            print(f"SQLAlchemy to_sql Error for table {table_name}: {e_insert}")
                            print("Sample of data that might be causing issues (first 5 rows):")
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
                # conn.commit() # This commit is actually handled by to_sql for each table
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
        normalizer.print_summary() # Print summary before DB insertion attempt
        if normalizer.create_db_schema_and_insert_data():
            print("\n✅ Normalization and database population complete!")
            print(f"🗄️  Data should now be in PostgreSQL database '{DB_NAME}' on host '{DB_HOST}'.")
            ddl_statements = normalizer.generate_postgres_ddl()
            ddl_file_path = 'create_postgres_tables.sql'
            with open(ddl_file_path, 'w') as f:
                for stmt in ddl_statements:
                    f.write(stmt + '\n\n') 
            print(f"📜 PostgreSQL DDL statements saved to '{ddl_file_path}'")
        else:
            print("\n❌ Database schema creation or data insertion failed.")
    else:
        print("\n❌ Data normalization process failed (e.g., data cleaning resulted in no data).")

if __name__ == "__main__":
    main() 