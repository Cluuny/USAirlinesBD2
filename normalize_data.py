import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import os

class AirlineDataNormalizer:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.df = None
        self.tables = {}
        
    def load_data(self):
        """Load and clean the CSV data."""
        print("Loading CSV data...")
        try:
            self.df = pd.read_csv(self.csv_file_path, sep=',', encoding='utf-8', 
                                on_bad_lines='skip', low_memory=False)
            print(f"Loaded {len(self.df)} records with {len(self.df.columns)} columns")
            
            # Clean data - remove obviously corrupted records
            initial_count = len(self.df)
            
            # Filter out records with corrupted passenger data (those with concatenated airport codes)
            self.df = self.df[self.df['passengers'].astype(str).str.len() < 10]
            
            # Convert specific columns to proper types
            # Keep airport codes as strings
            self.df['airport_1'] = self.df['airport_1'].astype(str)
            self.df['airport_2'] = self.df['airport_2'].astype(str)
            
            # Keep carrier codes as strings  
            self.df['carrier_lg'] = self.df['carrier_lg'].astype(str)
            self.df['carrier_low'] = self.df['carrier_low'].astype(str)
            
            # Convert numeric columns
            numeric_columns = ['Year', 'quarter', 'nsmiles', 'passengers', 'fare', 
                             'large_ms', 'fare_lg', 'lf_ms', 'fare_low']
            
            for col in numeric_columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # Remove rows with critical missing data
            self.df = self.df.dropna(subset=['Year', 'city1', 'city2', 'airport_1', 'airport_2'])
            
            # Filter out invalid carrier codes (numeric or single characters)
            self.df = self.df[
                (self.df['carrier_lg'].str.len() >= 2) & 
                (self.df['carrier_low'].str.len() >= 2) &
                (~self.df['carrier_lg'].str.isdigit()) &
                (~self.df['carrier_low'].str.isdigit())
            ]
            
            print(f"After cleaning: {len(self.df)} records ({initial_count - len(self.df)} removed)")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def create_cities_table(self):
        """Create normalized Cities table."""
        print("Creating Cities table...")
        
        # Extract unique cities from both origin and destination
        cities_1 = self.df[['citymarketid_1', 'city1']].rename(columns={
            'citymarketid_1': 'city_market_id', 'city1': 'city_name'
        })
        cities_2 = self.df[['citymarketid_2', 'city2']].rename(columns={
            'citymarketid_2': 'city_market_id', 'city2': 'city_name'
        })
        
        # Combine and get unique cities
        all_cities = pd.concat([cities_1, cities_2]).drop_duplicates()
        all_cities = all_cities.dropna()
        
        # Extract state from city name
        all_cities['state'] = all_cities['city_name'].str.extract(r', ([A-Z]{2})(?:\s|$)')
        all_cities['city_name_clean'] = all_cities['city_name'].str.replace(r', [A-Z]{2}.*$', '', regex=True)
        
        # Create final cities table
        self.tables['cities'] = all_cities[['city_market_id', 'city_name_clean', 'state', 'city_name']].rename(columns={
            'city_name_clean': 'city_name',
            'city_name': 'full_city_name'
        }).reset_index(drop=True)
        
        print(f"Created Cities table with {len(self.tables['cities'])} unique cities")
    
    def create_airports_table(self):
        """Create normalized Airports table."""
        print("Creating Airports table...")
        
        # Extract unique airports from both origin and destination
        airports_1 = self.df[['airportid_1', 'airport_1', 'citymarketid_1']].rename(columns={
            'airportid_1': 'airport_id', 'airport_1': 'airport_code', 'citymarketid_1': 'city_market_id'
        })
        airports_2 = self.df[['airportid_2', 'airport_2', 'citymarketid_2']].rename(columns={
            'airportid_2': 'airport_id', 'airport_2': 'airport_code', 'citymarketid_2': 'city_market_id'
        })
        
        # Combine and get unique airports
        all_airports = pd.concat([airports_1, airports_2]).drop_duplicates()
        all_airports = all_airports.dropna()
        
        self.tables['airports'] = all_airports.reset_index(drop=True)
        
        print(f"Created Airports table with {len(self.tables['airports'])} unique airports")
    
    def create_carriers_table(self):
        """Create normalized Carriers table."""
        print("Creating Carriers table...")
        
        # Extract unique carriers from both large and low-cost carrier columns
        large_carriers = self.df[['carrier_lg']].rename(columns={'carrier_lg': 'carrier_code'})
        large_carriers['carrier_type'] = 'Legacy'
        
        low_carriers = self.df[['carrier_low']].rename(columns={'carrier_low': 'carrier_code'})
        low_carriers['carrier_type'] = 'Low-Cost'
        
        # Combine and get unique carriers
        all_carriers = pd.concat([large_carriers, low_carriers]).drop_duplicates()
        all_carriers = all_carriers.dropna()
        
        # Filter out invalid carrier codes
        all_carriers = all_carriers[
            (all_carriers['carrier_code'].str.len() >= 2) & 
            (~all_carriers['carrier_code'].str.isdigit()) &
            (all_carriers['carrier_code'] != 'nan')
        ]
        
        # Add carrier ID
        all_carriers = all_carriers.reset_index(drop=True)
        all_carriers['carrier_id'] = all_carriers.index + 1
        
        self.tables['carriers'] = all_carriers[['carrier_id', 'carrier_code', 'carrier_type']]
        
        print(f"Created Carriers table with {len(self.tables['carriers'])} unique carriers")
    
    def create_routes_table(self):
        """Create normalized Routes table."""
        print("Creating Routes table...")
        
        # Create unique routes
        routes = self.df[['airportid_1', 'airportid_2', 'nsmiles']].rename(columns={
            'airportid_1': 'origin_airport_id',
            'airportid_2': 'destination_airport_id',
            'nsmiles': 'distance_miles'
        })
        
        # Get unique routes (same route might have multiple distance values, take the mode)
        routes_grouped = routes.groupby(['origin_airport_id', 'destination_airport_id']).agg({
            'distance_miles': lambda x: x.mode().iloc[0] if not x.mode().empty else x.mean()
        }).reset_index()
        
        # Add route ID
        routes_grouped['route_id'] = routes_grouped.index + 1
        
        self.tables['routes'] = routes_grouped[['route_id', 'origin_airport_id', 'destination_airport_id', 'distance_miles']]
        
        print(f"Created Routes table with {len(self.tables['routes'])} unique routes")
    
    def create_flights_table(self):
        """Create normalized Flights table."""
        print("Creating Flights table...")
        
        # Create a mapping from airport pairs to route IDs
        route_mapping = {}
        for _, route in self.tables['routes'].iterrows():
            key = (route['origin_airport_id'], route['destination_airport_id'])
            route_mapping[key] = route['route_id']
        
        # Create flights table
        flights = self.df.copy()
        
        # Map to route IDs
        flights['route_id'] = flights.apply(
            lambda row: route_mapping.get((row['airportid_1'], row['airportid_2']), None), 
            axis=1
        )
        
        # Filter out flights without valid route mapping
        flights = flights.dropna(subset=['route_id'])
        
        # Create flight ID
        flights = flights.reset_index(drop=True)
        flights['flight_id'] = flights.index + 1
        
        # Select relevant columns
        self.tables['flights'] = flights[[
            'flight_id', 'route_id', 'Year', 'quarter', 'passengers', 'fare', 'tbl1apk'
        ]].rename(columns={
            'Year': 'year',
            'tbl1apk': 'source_record_id'
        })
        
        print(f"Created Flights table with {len(self.tables['flights'])} flight records")
    
    def create_market_share_table(self):
        """Create normalized Market Share table."""
        print("Creating Market Share table...")
        
        # Create carrier mapping
        carrier_mapping = {}
        for _, carrier in self.tables['carriers'].iterrows():
            carrier_mapping[carrier['carrier_code']] = carrier['carrier_id']
        
        market_shares = []
        
        # Process each flight record
        for _, flight in self.df.iterrows():
            flight_id = self.tables['flights'][
                self.tables['flights']['source_record_id'] == flight['tbl1apk']
            ]['flight_id'].iloc[0] if not self.tables['flights'][
                self.tables['flights']['source_record_id'] == flight['tbl1apk']
            ].empty else None
            
            if flight_id is None:
                continue
            
            # Add large carrier market share
            if pd.notna(flight['carrier_lg']) and flight['carrier_lg'] in carrier_mapping:
                market_shares.append({
                    'flight_id': flight_id,
                    'carrier_id': carrier_mapping[flight['carrier_lg']],
                    'market_share': flight['large_ms'],
                    'fare': flight['fare_lg']
                })
            
            # Add low-cost carrier market share
            if pd.notna(flight['carrier_low']) and flight['carrier_low'] in carrier_mapping:
                market_shares.append({
                    'flight_id': flight_id,
                    'carrier_id': carrier_mapping[flight['carrier_low']],
                    'market_share': flight['lf_ms'],
                    'fare': flight['fare_low']
                })
        
        self.tables['market_share'] = pd.DataFrame(market_shares)
        
        print(f"Created Market Share table with {len(self.tables['market_share'])} records")
    
    def normalize_data(self):
        """Execute the full normalization process."""
        if not self.load_data():
            return False
        
        self.create_cities_table()
        self.create_airports_table()
        self.create_carriers_table()
        self.create_routes_table()
        self.create_flights_table()
        self.create_market_share_table()
        
        return True
    
    def generate_sql_ddl(self):
        """Generate SQL DDL statements for table creation."""
        ddl_statements = []
        
        # Cities table
        ddl_statements.append("""
CREATE TABLE cities (
    city_market_id INTEGER PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    state VARCHAR(2),
    full_city_name VARCHAR(200) NOT NULL
);""")
        
        # Airports table
        ddl_statements.append("""
CREATE TABLE airports (
    airport_id INTEGER PRIMARY KEY,
    airport_code VARCHAR(3) NOT NULL,
    city_market_id INTEGER NOT NULL,
    FOREIGN KEY (city_market_id) REFERENCES cities(city_market_id)
);""")
        
        # Carriers table
        ddl_statements.append("""
CREATE TABLE carriers (
    carrier_id INTEGER PRIMARY KEY,
    carrier_code VARCHAR(2) NOT NULL UNIQUE,
    carrier_type VARCHAR(10) NOT NULL CHECK (carrier_type IN ('Legacy', 'Low-Cost'))
);""")
        
        # Routes table
        ddl_statements.append("""
CREATE TABLE routes (
    route_id INTEGER PRIMARY KEY,
    origin_airport_id INTEGER NOT NULL,
    destination_airport_id INTEGER NOT NULL,
    distance_miles DECIMAL(8,2),
    FOREIGN KEY (origin_airport_id) REFERENCES airports(airport_id),
    FOREIGN KEY (destination_airport_id) REFERENCES airports(airport_id),
    UNIQUE(origin_airport_id, destination_airport_id)
);""")
        
        # Flights table
        ddl_statements.append("""
CREATE TABLE flights (
    flight_id INTEGER PRIMARY KEY,
    route_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    passengers INTEGER,
    fare DECIMAL(10,2),
    source_record_id VARCHAR(50),
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);""")
        
        # Market Share table
        ddl_statements.append("""
CREATE TABLE market_share (
    flight_id INTEGER NOT NULL,
    carrier_id INTEGER NOT NULL,
    market_share DECIMAL(5,2),
    fare DECIMAL(10,2),
    PRIMARY KEY (flight_id, carrier_id),
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    FOREIGN KEY (carrier_id) REFERENCES carriers(carrier_id)
);""")
        
        return ddl_statements
    
    def save_normalized_data(self, output_dir='normalized_data'):
        """Save normalized tables as CSV files."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for table_name, table_df in self.tables.items():
            file_path = os.path.join(output_dir, f"{table_name}.csv")
            table_df.to_csv(file_path, index=False)
            print(f"Saved {table_name} table to {file_path}")
    
    def create_sqlite_database(self, db_name='airline_normalized.db'):
        """Create SQLite database with normalized data."""
        print(f"Creating SQLite database: {db_name}")
        
        # Remove existing database
        if os.path.exists(db_name):
            os.remove(db_name)
        
        conn = sqlite3.connect(db_name)
        
        try:
            # Create tables
            ddl_statements = self.generate_sql_ddl()
            for ddl in ddl_statements:
                conn.execute(ddl)
            
            # Insert data
            for table_name, table_df in self.tables.items():
                table_df.to_sql(table_name, conn, if_exists='append', index=False)
                print(f"Inserted {len(table_df)} records into {table_name}")
            
            conn.commit()
            print(f"Successfully created normalized database: {db_name}")
            
        except Exception as e:
            print(f"Error creating database: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def print_summary(self):
        """Print summary of normalized tables."""
        print("\n" + "="*60)
        print("NORMALIZATION SUMMARY")
        print("="*60)
        
        for table_name, table_df in self.tables.items():
            print(f"\n{table_name.upper()} TABLE:")
            print(f"  Records: {len(table_df):,}")
            print(f"  Columns: {list(table_df.columns)}")
            if len(table_df) > 0:
                print(f"  Sample: {dict(table_df.iloc[0])}")

def main():
    # Initialize normalizer
    normalizer = AirlineDataNormalizer('archive/US Airline Flight Routes and Fares 1993-2024.csv')
    
    # Execute normalization
    if normalizer.normalize_data():
        # Print summary
        normalizer.print_summary()
        
        # Save DDL statements
        ddl_statements = normalizer.generate_sql_ddl()
        with open('create_tables.sql', 'w') as f:
            f.write('\n'.join(ddl_statements))
        print(f"\nSQL DDL saved to create_tables.sql")
        
        # Save normalized data as CSV files
        normalizer.save_normalized_data()
        
        # Create SQLite database
        normalizer.create_sqlite_database()
        
        print(f"\n✅ Normalization complete! Database is ready for production use.")
        print(f"📁 Normalized CSV files saved in 'normalized_data/' directory")
        print(f"🗄️  SQLite database created: 'airline_normalized.db'")
        print(f"📜 SQL DDL statements saved to 'create_tables.sql'")
    else:
        print("❌ Normalization failed!")

if __name__ == "__main__":
    main() 