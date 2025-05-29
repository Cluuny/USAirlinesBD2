import pandas as pd
import numpy as np

def analyze_csv():
    file_path = 'archive/US Airline Flight Routes and Fares 1993-2024.csv'
    print("Leyendo el archivo CSV...")
    
    try:
        df = pd.read_csv(file_path, 
                        sep=';',
                        encoding='utf-8',
                        on_bad_lines='skip')
        
        print("\n=== RESUMEN RÁPIDO DEL DATASET ===")
        print(f"Total de registros: {len(df):,}")
        print(f"Período: {df['Year'].min()} - {df['Year'].max()}")
        print(f"\nNúmero de rutas únicas: {df[['city1', 'city2']].drop_duplicates().shape[0]:,}")
        print(f"Número de aeropuertos únicos: {len(set(df['airport_1'].unique()) | set(df['airport_2'].unique())):,}")
        
        print("\n=== ESTADÍSTICAS DE PRECIOS ===")
        print(f"Tarifa promedio general: ${df['fare'].mean():.2f}")
        print(f"Tarifa mínima: ${df['fare'].min():.2f}")
        print(f"Tarifa máxima: ${df['fare'].max():.2f}")
        
        print("\n=== TOP 5 RUTAS MÁS FRECUENTES ===")
        top_routes = df.groupby(['city1', 'city2'])['passengers'].sum().sort_values(ascending=False).head()
        print(top_routes)
        
    except Exception as e:
        print(f"\nError al procesar el archivo: {str(e)}")

if __name__ == "__main__":
    analyze_csv() 