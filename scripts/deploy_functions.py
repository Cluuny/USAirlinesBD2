#!/usr/bin/env python3
"""
Despliegue automatizado de funciones PL/pgSQL para USAirlinesBD2
Proyecto de Base de Datos II - UPTC 2025-I
"""

import psycopg2
import os
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar config
sys.path.append(str(Path(__file__).parent.parent))

# Configuración de la base de datos
DB_HOST = os.getenv("DB_HOST", "database-2.cjo0kekim2zi.us-east-2.rds.amazonaws.com")
DB_NAME = os.getenv("DB_NAME", "proyectobd2")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "sytpAq-syfci3-cudrud")
DB_PORT = os.getenv("DB_PORT", "5432")

# Ruta actualizada para los archivos SQL
SQL_FUNCTIONS_FILE = Path(__file__).parent.parent / "sql" / "plsql" / "psql_fixed.sql"

def deploy_functions():
    """Despliega las funciones PL/pgSQL en PostgreSQL"""
    
    print("🚀 Desplegando funciones PL/pgSQL...")
    print("=" * 60)
    
    # Verificar que el archivo existe
    if not SQL_FUNCTIONS_FILE.exists():
        print(f"❌ Error: No se encontró el archivo {SQL_FUNCTIONS_FILE}")
        print("   Estructura esperada: sql/plsql/psql_fixed.sql")
        return False
    
    try:
        # Conectar a PostgreSQL
        print(f"🔗 Conectando a {DB_HOST}:{DB_PORT}/{DB_NAME}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        
        cursor = conn.cursor()
        print("✅ Conexión establecida")
        
        # Leer archivo SQL
        print(f"📂 Leyendo funciones desde {SQL_FUNCTIONS_FILE.name}...")
        with open(SQL_FUNCTIONS_FILE, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Ejecutar las funciones
        print("⚙️  Ejecutando script SQL...")
        cursor.execute(sql_content)
        conn.commit()
        
        # Verificar funciones instaladas
        print("🔍 Verificando funciones instaladas...")
        cursor.execute("""
            SELECT routine_name, routine_type
            FROM information_schema.routines 
            WHERE routine_schema = 'public' 
            AND routine_type = 'FUNCTION'
            AND (routine_name LIKE 'calcular%' OR routine_name LIKE 'analizar%' OR routine_name LIKE 'obtener%')
            ORDER BY routine_name;
        """)
        
        functions = cursor.fetchall()
        
        if functions:
            print(f"✅ {len(functions)} funciones PL/pgSQL instaladas correctamente:")
            for func_name, func_type in functions:
                print(f"   📋 {func_name} ({func_type})")
        else:
            print("⚠️  No se encontraron funciones instaladas")
            return False
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 DESPLIEGUE COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print("\n📋 Funciones disponibles:")
        
        function_descriptions = [
            "calcular_tarifa_promedio - Calcula tarifas promedio entre ciudades",
            "calcular_participacion_mercado - Analiza cuota de mercado por aerolínea",
            "analizar_evolucion_aerolinea - Estudia evolución temporal (FOR LOOP)",
            "obtener_aerolinea_dominante - Identifica líder por ruta", 
            "analizar_competencia_aeropuerto - Análisis de competencia (WHILE LOOP)",
            "calcular_indice_estacionalidad - Variabilidad estacional (CASE avanzado)"
        ]
        
        for desc in function_descriptions:
            print(f"   🔧 {desc}")
        
        print(f"\n💡 Ejemplos de uso disponibles en:")
        print(f"   📄 sql/plsql/ejecutar_funciones.sql")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_sample_function():
    """Prueba una función de ejemplo para verificar el despliegue"""
    
    print("\n🧪 Probando función de ejemplo...")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        
        cursor = conn.cursor()
        
        # Probar función simple
        cursor.execute("SELECT calcular_tarifa_promedio('New York City', 'Los Angeles') AS test_result;")
        result = cursor.fetchone()
        
        if result and result[0] is not None:
            print(f"✅ Función de prueba ejecutada: Tarifa NYC-LA = ${result[0]}")
        else:
            print("✅ Función ejecutada (sin datos para esa ruta)")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"⚠️  Error en prueba: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 80)
    print("🛫 DESPLEGADOR DE FUNCIONES PL/PGSQL - USAirlinesBD2")
    print("=" * 80)
    print("🎓 Proyecto de Base de Datos II - UPTC 2025-I")
    print("👨‍💻 Desarrollador: Sebastián Cañón Castellanos")
    print("=" * 80)
    
    # Verificar configuración
    try:
        import config
        print("✅ Configuración importada desde config.py")
        
        # Usar configuración del archivo si está disponible
        global DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT
        DB_HOST = getattr(config, 'DB_HOST', DB_HOST)
        DB_NAME = getattr(config, 'DB_NAME', DB_NAME)
        DB_USER = getattr(config, 'DB_USER', DB_USER)
        DB_PASS = getattr(config, 'DB_PASS', DB_PASS)
        DB_PORT = getattr(config, 'DB_PORT', DB_PORT)
        
    except ImportError:
        print("⚠️  config.py no encontrado, usando variables de entorno")
    
    # Ejecutar despliegue
    success = deploy_functions()
    
    if success:
        # Prueba opcional
        test_sample_function()
        
        print(f"\n🎯 PRÓXIMOS PASOS:")
        print(f"   1. Abrir tu cliente SQL favorito")
        print(f"   2. Conectar a la base de datos {DB_NAME}")
        print(f"   3. Ejecutar ejemplos desde sql/plsql/ejecutar_funciones.sql")
        print(f"   4. Revisar consultas avanzadas en sql/sqlConsultation/queries.sql")
        
    else:
        print("\n❌ El despliegue no se completó correctamente")
        print("   Revisa los errores y ejecuta nuevamente")
    
    return success

if __name__ == "__main__":
    main() 