import pandas as pd
import numpy as np

def analyze_csv():
    file_path = 'archive/US Airline Flight Routes and Fares 1993-2024.csv'
    print("Leyendo el archivo CSV...")
    
    try:
        # Try different encoding and parsing options
        df = pd.read_csv(file_path, 
                        sep=',',  # Changed from ';' to ',' based on CSV inspection
                        encoding='utf-8',
                        on_bad_lines='skip',
                        low_memory=False)
        
        print(f"\n=== INFORMACIÓN BÁSICA ===")
        print(f"Número de columnas: {len(df.columns)}")
        print(f"Columnas encontradas: {list(df.columns)}")
        print(f"Primeras 3 filas:")
        print(df.head(3))
        
        print("\n=== RESUMEN RÁPIDO DEL DATASET ===")
        print(f"Total de registros: {len(df):,}")
        
        # Check if Year column exists
        if 'Year' in df.columns:
            print(f"Período: {df['Year'].min()} - {df['Year'].max()}")
        else:
            print("Columna 'Year' no encontrada")
            
        # Check for route information
        if 'city1' in df.columns and 'city2' in df.columns:
            print(f"\nNúmero de rutas únicas: {df[['city1', 'city2']].drop_duplicates().shape[0]:,}")
        
        if 'airport_1' in df.columns and 'airport_2' in df.columns:
            unique_airports = set(df['airport_1'].dropna().unique()) | set(df['airport_2'].dropna().unique())
            print(f"Número de aeropuertos únicos: {len(unique_airports):,}")
        
        # Check for fare information
        if 'fare' in df.columns:
            print("\n=== ESTADÍSTICAS DE PRECIOS ===")
            fare_data = df['fare'].dropna()
            if len(fare_data) > 0:
                print(f"Tarifa promedio general: ${fare_data.mean():.2f}")
                print(f"Tarifa mínima: ${fare_data.min():.2f}")
                print(f"Tarifa máxima: ${fare_data.max():.2f}")
            else:
                print("No se encontraron datos válidos de tarifas")
        
        # Check for passenger information
        if 'passengers' in df.columns and 'city1' in df.columns and 'city2' in df.columns:
            print("\n=== TOP 5 RUTAS MÁS FRECUENTES ===")
            passenger_data = df[df['passengers'].notna()]
            if len(passenger_data) > 0:
                top_routes = passenger_data.groupby(['city1', 'city2'])['passengers'].sum().sort_values(ascending=False).head()
                print(top_routes)
            else:
                print("No se encontraron datos válidos de pasajeros")
        
        # Show data types
        print(f"\n=== TIPOS DE DATOS ===")
        print(df.dtypes)
        
    except Exception as e:
        print(f"\nError al procesar el archivo: {str(e)}")
        # Try to get more specific error information
        import traceback
        print("\nDetalle del error:")
        traceback.print_exc()

if __name__ == "__main__":
    analyze_csv() 