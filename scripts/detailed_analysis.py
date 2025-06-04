import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    """Carga y preprocesa el dataset."""
    file_path = 'archive/US Airline Flight Routes and Fares 1993-2024.csv'
    try:
        df = pd.read_csv(file_path, sep=',', encoding='utf-8', on_bad_lines='skip', low_memory=False)
        print(f"Dataset cargado exitosamente: {len(df)} registros, {len(df.columns)} columnas")
        return df
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return None

def analyze_temporal_trends(df):
    """Analiza tendencias temporales en precios y pasajeros."""
    print("\n=== ANÁLISIS TEMPORAL ===")
    
    # Tendencias anuales
    yearly_stats = df.groupby('Year').agg({
        'fare': ['mean', 'std'],
        'passengers': 'sum',
        'nsmiles': 'mean'
    }).round(2)
    
    print("\nEstadísticas anuales:")
    print(yearly_stats)
    
    # Análisis por trimestre
    quarterly_stats = df.groupby(['Year', 'quarter'])['fare'].mean().unstack()
    print("\nTarifas promedio por trimestre:")
    print(quarterly_stats.tail())

def analyze_route_statistics(df):
    """Analiza estadísticas de rutas y distancias."""
    print("\n=== ANÁLISIS DE RUTAS ===")
    
    # Rutas más caras
    print("\nTop 5 rutas más caras (promedio):")
    expensive_routes = df.groupby(['city1', 'city2'])['fare'].agg(['mean', 'count']).sort_values('mean', ascending=False)
    print(expensive_routes[expensive_routes['count'] > 100].head())  # Filtramos rutas con más de 100 vuelos
    
    # Análisis de distancia vs precio
    distance_price_corr = df['nsmiles'].corr(df['fare'])
    print(f"\nCorrelación entre distancia y precio: {distance_price_corr:.3f}")
    
    # Rutas más largas
    print("\nTop 5 rutas más largas:")
    longest_routes = df.groupby(['city1', 'city2'])['nsmiles'].mean().sort_values(ascending=False).head()
    print(longest_routes)

def analyze_carrier_competition(df):
    """Analiza la competencia entre aerolíneas tradicionales y de bajo costo."""
    print("\n=== ANÁLISIS DE COMPETENCIA ===")
    
    # Diferencia de precios entre aerolíneas tradicionales y de bajo costo
    df['price_difference'] = df['fare_lg'] - df['fare_low']
    
    print("\nEstadísticas de diferencia de precios (tradicional vs bajo costo):")
    print(df['price_difference'].describe())
    
    # Market share promedio
    print("\nCuota de mercado promedio:")
    print(f"Aerolíneas tradicionales: {df['large_ms'].mean():.2f}%")
    print(f"Aerolíneas de bajo costo: {df['lf_ms'].mean():.2f}%")
    
    # Rutas con mayor competencia
    high_competition = df[
        (df['large_ms'] > 0) & 
        (df['lf_ms'] > 0)
    ].groupby(['city1', 'city2']).size().sort_values(ascending=False)
    
    print("\nTop 5 rutas con mayor competencia:")
    print(high_competition.head())

def analyze_seasonal_patterns(df):
    """Analiza patrones estacionales en precios y pasajeros."""
    print("\n=== ANÁLISIS ESTACIONAL ===")
    
    seasonal_stats = df.groupby('quarter').agg({
        'fare': ['mean', 'std'],
        'passengers': 'sum'
    }).round(2)
    
    print("\nEstadísticas por trimestre:")
    print(seasonal_stats)
    
    # Identificar trimestre más caro y más barato
    avg_quarterly_fare = df.groupby('quarter')['fare'].mean()
    print(f"\nTrimestre más caro: Q{avg_quarterly_fare.idxmax()} (${avg_quarterly_fare.max():.2f})")
    print(f"Trimestre más barato: Q{avg_quarterly_fare.idxmin()} (${avg_quarterly_fare.min():.2f})")

def main():
    print("Cargando datos...")
    df = load_data()
    
    if df is None:
        print("No se pudieron cargar los datos. Saliendo...")
        return
    
    while True:
        print("\n=== MENÚ DE ANÁLISIS ===")
        print("1. Análisis temporal")
        print("2. Análisis de rutas")
        print("3. Análisis de competencia")
        print("4. Análisis estacional")
        print("5. Todos los análisis")
        print("6. Salir")
        
        choice = input("\nSeleccione una opción (1-6): ")
        
        if choice == '1':
            analyze_temporal_trends(df)
        elif choice == '2':
            analyze_route_statistics(df)
        elif choice == '3':
            analyze_carrier_competition(df)
        elif choice == '4':
            analyze_seasonal_patterns(df)
        elif choice == '5':
            analyze_temporal_trends(df)
            analyze_route_statistics(df)
            analyze_carrier_competition(df)
            analyze_seasonal_patterns(df)
        elif choice == '6':
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main() 