import csv
import re
import sys
import os

def load_airport_ids(airports_csv_path):
    """Carga el mapeo de códigos de aeropuertos a nombres desde el archivo airport.csv"""
    airport_mapping = {}
    try:
        with open(airports_csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Mapear código de aeropuerto a nombre (aunque no lo usaremos, lo mantenemos para referencia)
                airport_mapping[row['Codigo del aeropuerto']] = row['Nombre del aeropuerto']
        return airport_mapping
    except Exception as e:
        print(f"Error al cargar el archivo de aeropuertos: {str(e)}")
        sys.exit(1)

def load_carrier_ids(carriers_csv_path):
    """Carga el mapeo de códigos de aerolíneas a IDs desde el archivo carriers.csv"""
    carrier_mapping = {}
    try:
        with open(carriers_csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for idx, row in enumerate(reader, 1):
                # Mapear código de aerolínea a ID (índice basado en 1)
                carrier_code = row['Codigo de aereolinea']
                carrier_mapping[carrier_code] = str(idx)
        return carrier_mapping
    except Exception as e:
        print(f"Error al cargar el archivo de aerolíneas: {str(e)}")
        sys.exit(1)

def load_city_ids(cities_csv_path):
    """Carga el mapeo de nombres de ciudades a IDs desde el archivo cities.csv"""
    city_mapping = {}
    try:
        with open(cities_csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Guardamos el nombre original de cities.csv
                city_name = row['city_name']
                city_id = row['id']
                
                # Mapear el nombre exacto
                city_mapping[city_name] = city_id
                
                # También mapear una versión limpia (sin paréntesis)
                city_name_clean = re.sub(r'\s*\(.*?\)', '', city_name).strip()
                city_mapping[city_name_clean] = city_id
                
                # Si contiene "/", mapear cada parte individualmente
                if '/' in city_name_clean:
                    for part in city_name_clean.split('/'):
                        part_clean = part.strip()
                        if part_clean:
                            city_mapping[part_clean] = city_id
                
                # Crear variaciones adicionales para nombres comunes
                # Por ejemplo, "New York City" también se puede encontrar como "New York"
                if city_name_clean == "New York City":
                    city_mapping["New York"] = city_id
                elif city_name_clean == "Washington":
                    city_mapping["Washington, DC"] = city_id
                    city_mapping["Washington DC"] = city_id
                elif "Minneapolis/St. Paul" in city_name_clean:
                    city_mapping["Minneapolis"] = city_id
                    city_mapping["St. Paul"] = city_id
                    city_mapping["Minneapolis/St Paul"] = city_id
                elif "Dallas/Fort Worth" in city_name_clean:
                    city_mapping["Dallas"] = city_id
                    city_mapping["Fort Worth"] = city_id
                    city_mapping["Dallas/Fort Worth"] = city_id
                    
        return city_mapping
    except Exception as e:
        print(f"Error al cargar el archivo de ciudades: {str(e)}")
        sys.exit(1)

def clean_city_name(city_name):
    """Limpia el nombre de la ciudad eliminando texto entre paréntesis y estado"""
    # Primero eliminar texto entre paréntesis
    clean = re.sub(r'\s*\(.*?\)', '', city_name).strip()
    
    # Si tiene coma, tomar solo la parte antes de la coma (quitar el estado)
    if ',' in clean:
        clean = clean.split(',')[0].strip()
    
    return clean

def process_airlines_data(input_csv_path, airport_mapping, carrier_mapping, city_mapping):
    """Procesa el archivo de aerolíneas y crea una nueva versión con IDs de ciudades, aerolíneas y sin nombres de aeropuertos"""
    output_csv_path = os.path.join('archive', 'US_Airlines_Final_Normalized.csv')
    not_found_cities = set()
    not_found_carriers = set()
    
    try:
        # Leer el archivo de entrada y crear el archivo de salida
        with open(input_csv_path, 'r', encoding='utf-8') as infile, \
             open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.reader(infile, delimiter=';')  # El CSV usa ';' como delimitador
            writer = csv.writer(outfile, delimiter=';')  # Mantener el mismo delimitador
            
            # Leer la cabecera
            header = next(reader)
            
            # Índices para las columnas que necesitamos
            city1_idx = header.index('city1_id')
            city2_idx = header.index('city2_id')
            carrier_lg_idx = header.index('carrier_lg')
            carrier_low_idx = header.index('carrier_low')
            
            # Crear nueva cabecera reemplazando las columnas de aerolíneas
            new_header = []
            columns_to_keep = []
            
            for idx, col in enumerate(header):
                new_header.append(col)
                columns_to_keep.append(idx)
                if col == 'carrier_lg':
                    new_header[-1] = 'carrier_lg_id'  # Cambiar nombre a carrier_lg_id
                elif col == 'carrier_low':
                    new_header[-1] = 'carrier_low_id'  # Cambiar nombre a carrier_low_id
            
            writer.writerow(new_header)
            
            # Procesar cada fila
            rows_processed = 0
            for row in reader:
                if not row:  # Saltar filas vacías
                    continue
                    
                # Procesar aerolíneas
                carrier_lg = row[carrier_lg_idx].strip()
                carrier_low = row[carrier_low_idx].strip()
                
                carrier_lg_id = carrier_mapping.get(carrier_lg)
                carrier_low_id = carrier_mapping.get(carrier_low)
                
                # Registrar aerolíneas no encontradas
                if not carrier_lg_id and carrier_lg:
                    not_found_carriers.add(carrier_lg)
                if not carrier_low_id and carrier_low:
                    not_found_carriers.add(carrier_low)
                
                # Crear nueva fila reemplazando los códigos de aerolíneas con IDs
                new_row = []
                for idx in columns_to_keep:
                    if idx == carrier_lg_idx:
                        new_row.append(carrier_lg_id if carrier_lg_id else 'NULL')
                    elif idx == carrier_low_idx:
                        new_row.append(carrier_low_id if carrier_low_id else 'NULL')
                    else:
                        new_row.append(row[idx])
                
                writer.writerow(new_row)
                
                rows_processed += 1
                if rows_processed % 10000 == 0:  # Mostrar progreso cada 10000 filas
                    print(f"Procesadas {rows_processed} filas...")
        
        # Mostrar resumen
        print(f"\nArchivo generado exitosamente: {output_csv_path}")
        print(f"Total de filas procesadas: {rows_processed}")
        
        # Mostrar aerolíneas no encontradas
        if not_found_carriers:
            print("\nAdvertencia: Las siguientes aerolíneas no fueron encontradas en carriers.csv:")
            for carrier in sorted(list(not_found_carriers)[:20]):  # Mostrar solo las primeras 20
                print(f"- {carrier}")
            if len(not_found_carriers) > 20:
                print(f"... y {len(not_found_carriers) - 20} más")
            print(f"\nTotal de aerolíneas no encontradas: {len(not_found_carriers)}")
        else:
            print("\n✓ Todas las aerolíneas fueron encontradas en carriers.csv")
            
    except Exception as e:
        print(f"Error al procesar el archivo de aerolíneas: {str(e)}")
        sys.exit(1)

def main():
    # Verificar que existe el directorio archive
    if not os.path.exists('archive'):
        print("Error: No se encontró el directorio 'archive'")
        sys.exit(1)
    
    # Rutas de los archivos
    airports_csv_path = os.path.join('archive', 'airport.csv')
    carriers_csv_path = os.path.join('archive', 'carriers.csv')  # Nuevo archivo de aerolíneas
    cities_csv_path = os.path.join('archive', 'cities.csv')
    airlines_csv_path = os.path.join('archive', 'US_Airlines_Normalized.csv')  # Usar el archivo ya normalizado
    
    # Verificar que existen los archivos necesarios
    required_files = [airports_csv_path, carriers_csv_path, cities_csv_path, airlines_csv_path]
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"Error: No se encontró el archivo {file_path}")
            sys.exit(1)
    
    # Cargar los mapeos
    print("Cargando mapeo de aeropuertos...")
    airport_mapping = load_airport_ids(airports_csv_path)
    print(f"Se cargaron {len(airport_mapping)} referencias de aeropuertos")
    
    print("\nCargando mapeo de aerolíneas...")
    carrier_mapping = load_carrier_ids(carriers_csv_path)
    print(f"Se cargaron {len(carrier_mapping)} referencias de aerolíneas")
    
    print("\nCargando mapeo de ciudades...")
    city_mapping = load_city_ids(cities_csv_path)
    print(f"Se cargaron {len(city_mapping)} referencias de ciudades")
    
    # Procesar el archivo de aerolíneas
    print("\nProcesando archivo de aerolíneas...")
    print("- Ciudades ya normalizadas (usando IDs)")
    print("- Reemplazando códigos de aerolíneas con IDs")
    print("- Columnas de aeropuertos ya normalizadas (solo IDs)")
    
    process_airlines_data(airlines_csv_path, airport_mapping, carrier_mapping, city_mapping)

if __name__ == "__main__":
    main() 