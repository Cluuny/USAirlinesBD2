import csv
import re
from collections import Counter
import sys
import os

def infer_state(city_name):
    # Diccionario de estados comunes y sus abreviaciones
    states = {
        'AL': ['Alabama'],
        'AK': ['Alaska'],
        'AZ': ['Arizona', 'Phoenix', 'Tucson'],
        'AR': ['Arkansas', 'Little Rock'],
        'CA': ['California', 'Los Angeles', 'San Francisco', 'San Diego', 'Sacramento', 'Fresno', 'Santa Barbara', 'Palm Springs', 'Santa Rosa'],
        'CO': ['Colorado', 'Denver', 'Colorado Springs'],
        'CT': ['Connecticut', 'Hartford'],
        'DE': ['Delaware'],
        'FL': ['Florida', 'Tampa', 'Miami', 'Orlando', 'Jacksonville', 'Fort Myers', 'Pensacola', 'Panama City', 'Key West', 'Sarasota'],
        'GA': ['Georgia', 'Atlanta', 'Savannah'],
        'HI': ['Hawaii'],
        'ID': ['Idaho', 'Boise'],
        'IL': ['Illinois', 'Chicago'],
        'IN': ['Indiana', 'Indianapolis'],
        'IA': ['Iowa', 'Des Moines', 'Cedar Rapids'],
        'KS': ['Kansas', 'Wichita'],
        'KY': ['Kentucky', 'Louisville'],
        'LA': ['Louisiana', 'New Orleans'],
        'ME': ['Maine'],
        'MD': ['Maryland'],
        'MA': ['Massachusetts', 'Boston', "Martha's Vineyard", 'Nantucket'],
        'MI': ['Michigan', 'Detroit', 'Grand Rapids', 'Traverse City'],
        'MN': ['Minnesota', 'Minneapolis'],
        'MS': ['Mississippi', 'Jackson'],
        'MO': ['Missouri', 'St. Louis', 'Kansas City'],
        'MT': ['Montana', 'Bozeman', 'Kalispell', 'Missoula'],
        'NE': ['Nebraska', 'Omaha'],
        'NV': ['Nevada', 'Las Vegas', 'Reno'],
        'NH': ['New Hampshire'],
        'NJ': ['New Jersey'],
        'NM': ['New Mexico', 'Albuquerque'],
        'NY': ['New York', 'New York City', 'Albany', 'Buffalo', 'Rochester', 'Syracuse'],
        'NC': ['North Carolina', 'Charlotte', 'Raleigh', 'Asheville', 'Wilmington'],
        'ND': ['North Dakota', 'Fargo', 'Bismarck'],
        'OH': ['Ohio', 'Cleveland', 'Columbus', 'Cincinnati'],
        'OK': ['Oklahoma', 'Oklahoma City', 'Tulsa'],
        'OR': ['Oregon', 'Portland', 'Eugene', 'Medford', 'Bend'],
        'PA': ['Pennsylvania', 'Philadelphia', 'Pittsburgh', 'Allentown'],
        'RI': ['Rhode Island'],
        'SC': ['South Carolina', 'Charleston', 'Myrtle Beach', 'Greenville'],
        'SD': ['South Dakota', 'Sioux Falls'],
        'TN': ['Tennessee', 'Nashville', 'Memphis', 'Knoxville'],
        'TX': ['Texas', 'Dallas', 'Houston', 'Austin', 'San Antonio', 'El Paso', 'Lubbock', 'Amarillo', 'Midland', 'Harlingen', 'Mission', 'McAllen'],
        'UT': ['Utah', 'Salt Lake City', 'Provo'],
        'VT': ['Vermont', 'Burlington'],
        'VA': ['Virginia', 'Norfolk', 'Richmond'],
        'WA': ['Washington', 'Seattle', 'Spokane'],
        'WV': ['West Virginia'],
        'WI': ['Wisconsin', 'Milwaukee', 'Madison'],
        'WY': ['Wyoming']
    }
    
    # Primero intentar encontrar el estado en el nombre de la ciudad
    if ',' in city_name:
        city_part, state_part = city_name.split(',', 1)
        state_part = state_part.strip()
        if len(state_part) == 2:  # Si es una abreviación de estado
            return state_part, city_part.strip()
        return state_part, city_part.strip()
    
    # Si no hay coma, buscar en el diccionario de estados
    city_clean = city_name.split('/')[0].strip()  # Tomar solo la primera ciudad en caso de ciudades múltiples
    
    for state_abbr, cities in states.items():
        for city in cities:
            if city.lower() in city_clean.lower() or city_clean.lower() in city.lower():
                return state_abbr, city_name
    
    return "N/A", city_name

def process_cities(csv_file_path):
    try:
        # Abrir y leer el archivo CSV
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            
            # Saltar la cabecera
            next(reader)
            
            # Set para almacenar ciudades únicas
            unique_cities = set()
            
            # Procesar cada fila
            for row in reader:
                if row and len(row) > 6:  # Verificar fila no vacía y que tenga suficientes columnas
                    # Extraer city1 y city2 (posiciones 5 y 6 en base 0)
                    city1 = row[5].strip()
                    city2 = row[6].strip()
                    
                    # Limpiar nombres de ciudades (eliminar texto entre paréntesis)
                    city1_clean = re.sub(r'\s*\(.*?\)', '', city1).strip()
                    city2_clean = re.sub(r'\s*\(.*?\)', '', city2).strip()
                    
                    # Agregar ciudades al set si no están vacías
                    if city1_clean:
                        unique_cities.add(city1_clean)
                    if city2_clean:
                        unique_cities.add(city2_clean)

        # Convertir a lista y ordenar alfabéticamente
        cities_list = sorted(list(unique_cities))
        
        # Verificar que existe el directorio 'archive'
        archive_dir = 'archive'
        if not os.path.exists(archive_dir):
            print(f"Error: No se encontró el directorio '{archive_dir}'")
            sys.exit(1)
        
        # Crear el archivo CSV de salida en la carpeta 'archive'
        output_path = os.path.join(archive_dir, 'cities.csv')
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escribir la cabecera
            writer.writerow(['id', 'city_name', 'city_state'])
            
            # Escribir los datos
            for idx, city in enumerate(cities_list, 1):
                state, city_name = infer_state(city)
                writer.writerow([idx, city_name, state])

        print(f"\nArchivo 'cities.csv' generado exitosamente en la carpeta '{archive_dir}'")
        print(f"Ruta completa: {os.path.abspath(output_path)}")
        print(f"Total de ciudades únicas procesadas: {len(cities_list)}")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{csv_file_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python city_filter.py <ruta_archivo_csv>")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    process_cities(csv_file_path)
