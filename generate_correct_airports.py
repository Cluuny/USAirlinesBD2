import csv
import re
import os

def generate_airports():
    input_file = os.path.join('archive', 'US Airline Flight Routes and Fares 1993-2024.csv')
    output_file = os.path.join('archive', 'airports.csv')
    
    unique_airports = {}
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Leer cabecera
        
        # Encontrar índices
        airport1_idx = header.index('airport_1')
        airport2_idx = header.index('airport_2')
        city1_idx = header.index('city1')
        city2_idx = header.index('city2')
        
        print(f"airport_1 está en índice: {airport1_idx}")
        print(f"airport_2 está en índice: {airport2_idx}")
        
        for row in reader:
            if not row:
                continue
                
            # Obtener códigos IATA reales y ciudades
            airport1_code = row[airport1_idx].strip()
            airport2_code = row[airport2_idx].strip()
            city1 = re.sub(r'\s*\(.*?\)', '', row[city1_idx]).strip()
            city2 = re.sub(r'\s*\(.*?\)', '', row[city2_idx]).strip()
            
            # Agregar al diccionario
            if airport1_code:
                unique_airports[airport1_code] = city1
            if airport2_code:
                unique_airports[airport2_code] = city2
    
    # Ordenar y escribir archivo
    airports_list = sorted(unique_airports.items())
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'iata_code', 'city'])
        for idx, (code, city) in enumerate(airports_list, 1):
            writer.writerow([idx, code, city])
    
    print(f"Archivo generado: {output_file}")
    print(f"Total aeropuertos: {len(airports_list)}")
    print("Primeros 10 aeropuertos:")
    for idx, (code, city) in enumerate(airports_list[:10], 1):
        print(f"  {idx}: {code} - {city}")

if __name__ == "__main__":
    generate_airports() 