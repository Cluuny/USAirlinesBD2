import csv
import sys
import os

def process_carriers(csv_file_path):
    try:
        # Abrir y leer el archivo CSV
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')  # El CSV usa ';' como delimitador
            
            # Saltar la cabecera
            header = next(reader)
            
            # Obtener índices de las columnas de aerolíneas
            carrier_lg_idx = header.index('carrier_lg')
            carrier_low_idx = header.index('carrier_low')
            
            # Set para almacenar códigos de aerolíneas únicos
            unique_carriers = set()
            
            # Procesar cada fila
            for row in reader:
                if not row or len(row) < max(carrier_lg_idx, carrier_low_idx) + 1:
                    continue
                    
                # Extraer códigos de aerolíneas
                carrier_lg = row[carrier_lg_idx].strip()
                carrier_low = row[carrier_low_idx].strip()
                
                # Agregar aerolíneas al set si no están vacías
                if carrier_lg:
                    unique_carriers.add(carrier_lg)
                if carrier_low:
                    unique_carriers.add(carrier_low)

        # Convertir a lista y ordenar alfabéticamente por código de aerolínea
        carriers_list = sorted(list(unique_carriers))
        
        # Diccionario con nombres completos de aerolíneas comunes
        carrier_names = {
            'AA': 'American Airlines',
            'AS': 'Alaska Airlines',
            'B6': 'JetBlue Airways',
            'DL': 'Delta Air Lines',
            'F9': 'Frontier Airlines',
            'G4': 'Allegiant Air',
            'NK': 'Spirit Airlines',
            'UA': 'United Airlines',
            'WN': 'Southwest Airlines',
            'YX': 'Republic Airways',
            'OO': 'SkyWest Airlines',
            'MQ': 'Envoy Air',
            'YV': 'Mesa Airlines',
            '9E': 'Endeavor Air',
            'EV': 'ExpressJet',
            'OH': 'PSA Airlines',
            'QX': 'Horizon Air',
            'CP': 'Compass Airlines',
            'ZW': 'Air Wisconsin',
            'PT': 'Piedmont Airlines',
            'C5': 'Commutair',
            'HA': 'Hawaiian Airlines',
            'VX': 'Virgin America',
            'US': 'US Airways',
            'HP': 'America West Airlines',
            'TW': 'Trans World Airlines',
            'CO': 'Continental Airlines',
            'NW': 'Northwest Airlines',
            'FL': 'AirTran Airways',
            'WP': 'Island Air',
            'PW': 'Precision Air',
            'RP': 'Chautauqua Airlines',
            'XE': 'ExpressJet Airlines',
            'RU': 'Shuttle America',
            'S5': 'Safari Airlines',
            'TZ': 'ATA Airlines',
            'ML': 'Midwest Airlines',
            'I9': 'Cape Air',
            '2A': 'Tame EP',
            '3M': 'Silver Airways',
            '5Y': 'Atlas Air',
            '8V': 'Astral Aviation',
            'A3': 'Aegean Airlines',
            'AC': 'Air Canada',
            'AF': 'Air France',
            'AI': 'Air India',
            'AM': 'Aeromexico',
            'AR': 'Aerolineas Argentinas',
            'AV': 'Avianca',
            'AZ': 'ITA Airways',
            'BA': 'British Airways',
            'BR': 'EVA Air',
            'CI': 'China Airlines',
            'CX': 'Cathay Pacific',
            'EI': 'Aer Lingus',
            'EK': 'Emirates',
            'ET': 'Ethiopian Airlines',
            'EY': 'Etihad Airways',
            'FI': 'Icelandair',
            'GF': 'Gulf Air',
            'IB': 'Iberia',
            'JL': 'Japan Airlines',
            'KE': 'Korean Air',
            'KL': 'KLM',
            'LH': 'Lufthansa',
            'LX': 'Swiss International Air Lines',
            'MS': 'EgyptAir',
            'NH': 'All Nippon Airways',
            'NZ': 'Air New Zealand',
            'OS': 'Austrian Airlines',
            'OZ': 'Asiana Airlines',
            'PR': 'Philippine Airlines',
            'QF': 'Qantas',
            'QR': 'Qatar Airways',
            'RJ': 'Royal Jordanian',
            'SA': 'South African Airways',
            'SK': 'SAS',
            'SN': 'Brussels Airlines',
            'SQ': 'Singapore Airlines',
            'SV': 'Saudi Arabian Airlines',
            'TG': 'Thai Airways',
            'TK': 'Turkish Airlines',
            'TP': 'TAP Air Portugal',
            'VS': 'Virgin Atlantic'
        }
        
        # Crear el archivo CSV de salida en la carpeta 'archive'
        output_path = os.path.join('archive', 'carriers.csv')
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escribir la cabecera
            writer.writerow(['Codigo de aereolinea', 'Nombre de aereolinea'])
            
            # Escribir los datos
            for carrier_code in carriers_list:
                carrier_name = carrier_names.get(carrier_code, f"Aerolínea {carrier_code}")
                writer.writerow([carrier_code, carrier_name])

        print(f"\nArchivo 'carriers.csv' generado exitosamente en la carpeta 'archive'")
        print(f"Ruta completa: {os.path.abspath(output_path)}")
        print(f"Total de aerolíneas únicas procesadas: {len(carriers_list)}")
        
        # Mostrar algunos ejemplos de los datos procesados
        print("\nEjemplos de aerolíneas procesadas:")
        print(f"{'Código':<8} {'Nombre':<50}")
        print("-" * 58)
        for carrier_code in carriers_list[:15]:
            carrier_name = carrier_names.get(carrier_code, f"Aerolínea {carrier_code}")
            print(f"{carrier_code:<8} {carrier_name:<50}")
        if len(carriers_list) > 15:
            print("...")
        
        # Mostrar códigos no identificados
        unknown_codes = [code for code in carriers_list if code not in carrier_names]
        if unknown_codes:
            print(f"\nCódigos de aerolíneas no identificados: {len(unknown_codes)}")
            print("Códigos:", ", ".join(unknown_codes[:10]))
            if len(unknown_codes) > 10:
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
    
    # Ruta del archivo de entrada - usar el archivo normalizado
    input_csv_path = os.path.join('archive', 'US_Airlines_Normalized.csv')
    
    # Verificar que existe el archivo
    if not os.path.exists(input_csv_path):
        print(f"Error: No se encontró el archivo {input_csv_path}")
        sys.exit(1)
    
    # Procesar las aerolíneas
    print("Procesando aerolíneas...")
    process_carriers(input_csv_path)

if __name__ == "__main__":
    main() 