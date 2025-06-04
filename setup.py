#!/usr/bin/env python3
"""
Setup automatizado para USAirlinesBD2
Proyecto de Base de Datos II - UPTC 2025-I
"""

import os
import sys
import subprocess
import psycopg2
from pathlib import Path

# Configuración del proyecto
PROJECT_NAME = "USAirlinesBD2"
VERSION = "2.0.0"
AUTHOR = "Sebastián Cañón Castellanos"
DESCRIPTION = "Sistema completo de análisis de rutas y tarifas aéreas estadounidenses (1993-2024)"

def print_header():
    """Mostrar header del instalador"""
    print("=" * 80)
    print(f"🛫 INSTALADOR AUTOMATIZADO - {PROJECT_NAME} v{VERSION}")
    print("=" * 80)
    print(f"📋 {DESCRIPTION}")
    print(f"👨‍💻 Desarrollador: {AUTHOR}")
    print(f"🎓 UPTC 2025-I - Base de Datos II")
    print("=" * 80)

def check_python_version():
    """Verificar versión de Python"""
    print("\n🐍 Verificando versión de Python...")
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def check_postgresql():
    """Verificar disponibilidad de PostgreSQL"""
    print("\n🐘 Verificando PostgreSQL...")
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ {version}")
            return True
        else:
            print("❌ PostgreSQL no está en el PATH")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  PostgreSQL no detectado en el sistema")
        print("   Asegúrate de tener PostgreSQL instalado y configurado")
        return False

def install_dependencies():
    """Instalar dependencias de Python"""
    print("\n📦 Instalando dependencias de Python...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ Error: No se encontró requirements.txt")
        return False
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        print("✅ pip actualizado")
        
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencias instaladas exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def create_config():
    """Crear archivo de configuración"""
    print("\n⚙️  Configurando archivo de configuración...")
    
    config_example = Path("config.example.py")
    config_file = Path("config.py")
    
    if not config_example.exists():
        print("❌ Error: No se encontró config.example.py")
        return False
    
    if config_file.exists():
        print("✅ config.py ya existe - omitiendo")
        return True
    
    try:
        # Copiar archivo de ejemplo
        with open(config_example, 'r') as f:
            content = f.read()
        
        with open(config_file, 'w') as f:
            f.write(content)
        
        print("✅ config.py creado desde plantilla")
        print("📝 IMPORTANTE: Edita config.py con tus credenciales de PostgreSQL")
        return True
        
    except Exception as e:
        print(f"❌ Error creando config.py: {e}")
        return False

def verify_structure():
    """Verificar estructura del proyecto"""
    print("\n📁 Verificando estructura del proyecto...")
    
    required_dirs = ["scripts", "sql", "database", "docs"]
    required_files = [
        "scripts/normalize_to_postgres.py",
        "scripts/deploy_functions.py", 
        "sql/create_postgres_tables.sql",
        "sql/plsql/psql_fixed.sql",
        "sql/plsql/ejecutar_funciones.sql"
    ]
    
    missing = []
    
    # Verificar directorios
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing.append(f"📁 {dir_name}/")
    
    # Verificar archivos
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(f"📄 {file_path}")
    
    if missing:
        print("❌ Estructura incompleta. Archivos/carpetas faltantes:")
        for item in missing:
            print(f"   {item}")
        return False
    
    print("✅ Estructura del proyecto verificada")
    return True

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("\n🔗 Probando conexión a PostgreSQL...")
    
    try:
        # Intentar importar la configuración
        sys.path.append('.')
        import config
        
        conn = psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASS,
            port=config.DB_PORT
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✅ Conexión exitosa")
        print(f"   Servidor: {version.split(',')[0]}")
        return True
        
    except ImportError:
        print("⚠️  No se pudo importar config.py")
        print("   Configura tus credenciales en config.py")
        return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("   Verifica tus credenciales en config.py")
        return False

def show_next_steps():
    """Mostrar pasos siguientes"""
    print("\n" + "=" * 80)
    print("🎯 INSTALACIÓN COMPLETADA - PRÓXIMOS PASOS")
    print("=" * 80)
    
    print("\n📝 1. CONFIGURAR BASE DE DATOS:")
    print("   • Edita config.py con tus credenciales PostgreSQL")
    print("   • Asegúrate de que la base de datos existe")
    
    print("\n🚀 2. EJECUTAR PIPELINE ETL:")
    print("   python scripts/normalize_to_postgres.py")
    
    print("\n⚙️  3. DESPLEGAR FUNCIONES PL/pgSQL:")
    print("   python scripts/deploy_functions.py")
    
    print("\n📊 4. USAR ANÁLISIS:")
    print("   • Abrir sql/plsql/ejecutar_funciones.sql en tu cliente SQL")
    print("   • Revisar sql/sqlConsultation/queries.sql para consultas avanzadas")
    
    print("\n📚 5. DOCUMENTACIÓN:")
    print("   • README.md - Documentación completa")
    print("   • docs/MANUAL_USUARIO.md - Guía paso a paso")
    
    print("\n🔗 RECURSOS:")
    print(f"   • GitHub: https://github.com/Cluuny/{PROJECT_NAME}")
    print(f"   • Email: sebastian.ca0102@gmail.com")
    
    print("\n" + "=" * 80)
    print("✈️ ¡Proyecto listo para análisis de datos aeronáuticos! 🛬")
    print("=" * 80)

def main():
    """Función principal del instalador"""
    print_header()
    
    success = True
    steps = [
        ("Verificar Python", check_python_version),
        ("Verificar PostgreSQL", check_postgresql),
        ("Instalar dependencias", install_dependencies),
        ("Crear configuración", create_config),
        ("Verificar estructura", verify_structure),
        ("Probar conexión DB", test_database_connection)
    ]
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                success = False
                if step_name == "Probar conexión DB":
                    print("⚠️  Continuando sin verificar conexión...")
                    continue
                break
        except KeyboardInterrupt:
            print("\n\n❌ Instalación cancelada por el usuario")
            return False
        except Exception as e:
            print(f"\n❌ Error inesperado en {step_name}: {e}")
            success = False
            break
    
    if success:
        show_next_steps()
        return True
    else:
        print("\n❌ La instalación no se completó correctamente")
        print("   Revisa los errores y ejecuta nuevamente el instalador")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstalación cancelada por el usuario")
        sys.exit(1) 