import csv
import re
import sys
import os

def process_airports(csv_file_path):
    try:
        # Abrir y leer el archivo CSV
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')  # El CSV usa ';' como delimitador
            
            # Saltar la cabecera
            header = next(reader)
            
            # Obtener índices de las columnas de aeropuertos
            airportid1_idx = header.index('airportid_1')
            airportid2_idx = header.index('airportid_2')
            airport1_idx = header.index('airport_1')
            airport2_idx = header.index('airport_2')
            
            # Diccionario para almacenar aeropuertos únicos con su información
            # Clave: airportid, Valor: airport_name
            unique_airports = {}
            
            # Procesar cada fila
            for row in reader:
                if not row or len(row) < max(airportid1_idx, airportid2_idx, airport1_idx, airport2_idx) + 1:
                    continue
                    
                # Extraer identificadores y nombres de aeropuertos
                airportid1 = row[airportid1_idx].strip()
                airportid2 = row[airportid2_idx].strip()
                airport1 = row[airport1_idx].strip()
                airport2 = row[airport2_idx].strip()
                
                # Agregar aeropuertos al diccionario
                if airportid1 and airport1:
                    unique_airports[airportid1] = airport1
                if airportid2 and airport2:
                    unique_airports[airportid2] = airport2

        # Convertir a lista y ordenar alfabéticamente por código de aeropuerto
        airports_list = sorted(unique_airports.items())
        
        # Crear el archivo CSV de salida en la carpeta 'archive'
        output_path = os.path.join('archive', 'airport.csv')
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escribir la cabecera
            writer.writerow(['Codigo del aeropuerto', 'Nombre del aeropuerto'])
            
            # Escribir los datos
            for airport_id, airport_name in airports_list:
                writer.writerow([airport_id, airport_name])

        print(f"\nArchivo 'airport.csv' generado exitosamente en la carpeta 'archive'")
        print(f"Ruta completa: {os.path.abspath(output_path)}")
        print(f"Total de aeropuertos únicos procesados: {len(airports_list)}")
        
        # Mostrar algunos ejemplos de los datos procesados
        print("\nEjemplos de aeropuertos procesados:")
        print(f"{'Código':<8} {'Nombre':<50}")
        print("-" * 58)
        for airport_id, airport_name in airports_list[:10]:
            print(f"{airport_id:<8} {airport_name:<50}")
        if len(airports_list) > 10:
            print("...")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{csv_file_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")
        sys.exit(1)

def main():
    # Verificar que existe el directorio archive
    if not os.path.exists('archive'):
        print("Error: No se encontró el directorio 'archive'")
        sys.exit(1)
    
    # Ruta del archivo de entrada
    input_csv_path = os.path.join('archive', 'US Airline Flight Routes and Fares 1993-2024.csv')
    
    # Verificar que existe el archivo
    if not os.path.exists(input_csv_path):
        print(f"Error: No se encontró el archivo {input_csv_path}")
        sys.exit(1)
    
    # Procesar los aeropuertos
    print("Procesando aeropuertos...")
    process_airports(input_csv_path)

if __name__ == "__main__":
    main() 