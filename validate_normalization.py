import csv
import sys
import os

def load_reference_tables():
    """Carga todas las tablas de referencia"""
    reference_data = {}
    
    # Cargar ciudades
    cities_file = os.path.join('archive', 'cities.csv')
    with open(cities_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        cities = {row['id']: row['city_name'] for row in reader}
        reference_data['cities'] = cities
    
    # Cargar aeropuertos
    airports_file = os.path.join('archive', 'airport.csv')
    with open(airports_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        airports = {row['Codigo del aeropuerto']: row['Nombre del aeropuerto'] for row in reader}
        reference_data['airports'] = airports
    
    # Cargar aerolíneas
    carriers_file = os.path.join('archive', 'carriers.csv')
    with open(carriers_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        carriers = {}
        for idx, row in enumerate(reader, 1):
            carriers[str(idx)] = row['Codigo de aereolinea']
        reference_data['carriers'] = carriers
    
    return reference_data

def validate_normalization():
    """Valida la integridad referencial del archivo normalizado"""
    print("🔍 VALIDACIÓN DE NORMALIZACIÓN - US_Airlines_Final_Normalized.csv")
    print("=" * 70)
    
    # Cargar tablas de referencia
    try:
        ref_data = load_reference_tables()
        print(f"✅ Tablas de referencia cargadas:")
        print(f"   - Ciudades: {len(ref_data['cities'])} registros")
        print(f"   - Aeropuertos: {len(ref_data['airports'])} registros")
        print(f"   - Aerolíneas: {len(ref_data['carriers'])} registros")
        print()
    except Exception as e:
        print(f"❌ Error cargando tablas de referencia: {e}")
        return False
    
    # Validar archivo normalizado
    normalized_file = os.path.join('archive', 'US_Airlines_Final_Normalized.csv')
    
    errors = {
        'city_ids': set(),
        'airport_ids': set(),
        'carrier_ids': set(),
        'missing_values': 0,
        'total_rows': 0
    }
    
    try:
        with open(normalized_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            header = next(reader)
            
            # Obtener índices de columnas
            city1_idx = header.index('city1_id')
            city2_idx = header.index('city2_id')
            airportid1_idx = header.index('airportid_1')
            airportid2_idx = header.index('airportid_2')
            carrier_lg_idx = header.index('carrier_lg_id')
            carrier_low_idx = header.index('carrier_low_id')
            
            print("🔍 Validando integridad referencial...")
            
            for row_num, row in enumerate(reader, 2):  # Start from row 2 (skip header)
                if not row:
                    continue
                    
                errors['total_rows'] += 1
                
                # Validar city_ids
                city1_id = row[city1_idx].strip()
                city2_id = row[city2_idx].strip()
                
                if city1_id and city1_id != 'NULL' and city1_id not in ref_data['cities']:
                    errors['city_ids'].add(city1_id)
                if city2_id and city2_id != 'NULL' and city2_id not in ref_data['cities']:
                    errors['city_ids'].add(city2_id)
                    
                # Validar airport_ids
                airport1_id = row[airportid1_idx].strip()
                airport2_id = row[airportid2_idx].strip()
                
                if airport1_id and airport1_id != 'NULL' and airport1_id not in ref_data['airports']:
                    errors['airport_ids'].add(airport1_id)
                if airport2_id and airport2_id != 'NULL' and airport2_id not in ref_data['airports']:
                    errors['airport_ids'].add(airport2_id)
                    
                # Validar carrier_ids
                carrier_lg_id = row[carrier_lg_idx].strip()
                carrier_low_id = row[carrier_low_idx].strip()
                
                if carrier_lg_id and carrier_lg_id != 'NULL' and carrier_lg_id not in ref_data['carriers']:
                    errors['carrier_ids'].add(carrier_lg_id)
                if carrier_low_id and carrier_low_id != 'NULL' and carrier_low_id not in ref_data['carriers']:
                    errors['carrier_ids'].add(carrier_low_id)
                    
                # Contar valores NULL/vacíos
                if not city1_id or city1_id == 'NULL' or not city2_id or city2_id == 'NULL':
                    errors['missing_values'] += 1
                if not airport1_id or airport1_id == 'NULL' or not airport2_id or airport2_id == 'NULL':
                    errors['missing_values'] += 1
                if not carrier_lg_id or carrier_lg_id == 'NULL' or not carrier_low_id or carrier_low_id == 'NULL':
                    errors['missing_values'] += 1
                    
                # Mostrar progreso cada 1000 filas
                if row_num % 1000 == 0:
                    print(f"   Procesadas {row_num-1} filas...")
    
    except Exception as e:
        print(f"❌ Error procesando archivo normalizado: {e}")
        return False
    
    # Mostrar resultados
    print("\n" + "="*70)
    print("📊 RESULTADOS DE LA VALIDACIÓN")
    print("="*70)
    
    print(f"Total de filas procesadas: {errors['total_rows']:,}")
    
    # Validar ciudades
    if errors['city_ids']:
        print(f"\n❌ IDs de ciudades inválidos encontrados: {len(errors['city_ids'])}")
        print("   Primeros 10:", list(errors['city_ids'])[:10])
    else:
        print("\n✅ Todos los IDs de ciudades son válidos")
    
    # Validar aeropuertos
    if errors['airport_ids']:
        print(f"\n❌ IDs de aeropuertos inválidos encontrados: {len(errors['airport_ids'])}")
        print("   Primeros 10:", list(errors['airport_ids'])[:10])
    else:
        print("\n✅ Todos los IDs de aeropuertos son válidos")
    
    # Validar aerolíneas
    if errors['carrier_ids']:
        print(f"\n❌ IDs de aerolíneas inválidos encontrados: {len(errors['carrier_ids'])}")
        print("   Primeros 10:", list(errors['carrier_ids'])[:10])
    else:
        print("\n✅ Todos los IDs de aerolíneas son válidos")
    
    # Mostrar resumen de normalización
    print(f"\n📈 ESTADÍSTICAS DE NORMALIZACIÓN:")
    print(f"   - Valores NULL/vacíos: {errors['missing_values']:,}")
    
    # Verificar estructura normalizada
    print(f"\n🗂️ ESTRUCTURA NORMALIZADA:")
    
    # Verificar que no existan nombres de texto
    has_text_names = False
    with open(normalized_file, 'r', encoding='utf-8') as file:
        header = next(csv.reader(file, delimiter=';'))
        excluded_columns = ['airport_1', 'airport_2', 'city1', 'city2', 'carrier_lg', 'carrier_low']
        
        for col in excluded_columns:
            if col in header:
                has_text_names = True
                print(f"   ❌ Columna de texto encontrada: {col}")
    
    if not has_text_names:
        print("   ✅ No se encontraron columnas de nombres de texto")
        print("   ✅ Solo se usan IDs numéricos para referencias")
    
    # Verificar columnas esperadas
    expected_id_columns = ['city1_id', 'city2_id', 'airportid_1', 'airportid_2', 'carrier_lg_id', 'carrier_low_id']
    with open(normalized_file, 'r', encoding='utf-8') as file:
        header = next(csv.reader(file, delimiter=';'))
        
        for col in expected_id_columns:
            if col in header:
                print(f"   ✅ Columna normalizada: {col}")
            else:
                print(f"   ❌ Columna faltante: {col}")
    
    # Resultado final
    total_errors = len(errors['city_ids']) + len(errors['airport_ids']) + len(errors['carrier_ids'])
    
    print("\n" + "="*70)
    if total_errors == 0:
        print("🎉 ¡NORMALIZACIÓN COMPLETAMENTE EXITOSA!")
        print("✅ Todos los datos mantienen integridad referencial")
        print("✅ El archivo está listo para usar en una base de datos relacional")
        return True
    else:
        print("⚠️ NORMALIZACIÓN PARCIAL - Se encontraron algunos problemas")
        print(f"Total de errores de integridad referencial: {total_errors}")
        return False

def main():
    # Verificar que existen todos los archivos
    required_files = [
        'archive/US_Airlines_Final_Normalized.csv',
        'archive/cities.csv',
        'archive/airport.csv',
        'archive/carriers.csv'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Error: No se encontró el archivo {file_path}")
            sys.exit(1)
    
    # Ejecutar validación
    validate_normalization()

if __name__ == "__main__":
    main() 