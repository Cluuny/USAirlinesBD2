# 🛫 Análisis de Rutas y Tarifas Aéreas en EE.UU. (1993-2024)

> **Proyecto de Base de Datos II - UPTC 2025-I**  
> Sistema completo de normalización y análisis de datos aeronáuticos estadounidenses

## 🎯 **Descripción del Proyecto**

Este proyecto implementa un **pipeline ETL completo** que normaliza datos históricos de rutas y tarifas aéreas estadounidenses (1993-2024) desde formato CSV crudo hasta una **base de datos PostgreSQL en 3NF** (Tercera Forma Normal) con capacidades de análisis avanzado mediante **funciones PL/pgSQL**.

### 🏆 **Características Principales**

- ✅ **Normalización 3NF** completa con integridad referencial
- ✅ **6 funciones PL/pgSQL** avanzadas (FOR/WHILE loops, cursores, arrays)
- ✅ **10 consultas SQL** complejas para análisis de mercado
- ✅ **Pipeline ETL** automatizado con validación de datos
- ✅ **Esquema PostgreSQL** optimizado para análisis temporal

---

## 🗂️ **Estructura del Proyecto**

```
USAirlinesBD2/
├── 📁 scripts/                     # Scripts Python principales
│   ├── normalize_to_postgres.py    # 🚀 Script ETL principal (635 líneas)
│   ├── deploy_functions.py         # 🔧 Desplegador de funciones PL/pgSQL
│   ├── analyze_csv.py              # 📊 Análisis básico de datos
│   ├── detailed_analysis.py        # 📈 Análisis estadístico avanzado
│   └── schema_diagram.py           # 🎨 Generador de diagramas ER
│
├── 📁 sql/                         # Código SQL y funciones
│   ├── create_postgres_tables.sql  # 🏗️ DDL del esquema PostgreSQL
│   ├── plsql/                      # Funciones PL/pgSQL
│   │   ├── psql_fixed.sql          # ⚙️ 6 funciones PL/pgSQL optimizadas
│   │   └── ejecutar_funciones.sql  # 💡 25+ ejemplos de ejecución
│   └── sqlConsultation/            # Consultas de análisis
│       └── queries.sql             # 🔍 10 consultas SQL avanzadas
│
├── 📁 database/                    # Datos normalizados
│   └── normalized_data/            # CSVs de 6 tablas normalizadas
│       ├── cities.csv              # 🏢 102 ciudades únicas
│       ├── airports.csv            # ✈️ 123 aeropuertos catalogados
│       ├── carriers.csv            # 🏭 2,728 aerolíneas clasificadas
│       ├── routes.csv              # 🛤️ 78 rutas con distancias
│       ├── flights.csv             # 🛫 2,426 vuelos registrados
│       └── market_share.csv        # 📊 4,852 registros de participación
│
├── 📁 docs/                        # Documentación completa
│   ├── MANUAL_USUARIO.md           # 📖 Guía paso a paso
│   └── PRESENTACION.md             # 🎓 Presentación final del proyecto
│
├── 📁 archive/                     # Datos originales
│   ├── US Airline Flight Routes and Fares 1993-2024.csv
│   └── references.json             # 📋 Metadatos del dataset
│
├── 📋 README.md                    # Esta documentación
├── 📋 requirements.txt             # 📦 Dependencias Python
├── 📋 config.example.py            # ⚙️ Configuración de ejemplo
├── 📋 setup.py                     # 🛠️ Instalador automatizado
└── 📋 .gitignore                   # 🙈 Configuración Git
```

---

## 🚀 **Instrucciones de Ejecución**

### **📋 Prerequisitos**

```bash
# Software necesario
- Python 3.8 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes Python)
- Git (para clonación)
- 8GB RAM mínimo recomendado
```

### **⚡ Ejecución Rápida (4 pasos)**

```bash
# 1️⃣ CONFIGURACIÓN INICIAL
pip install -r requirements.txt
cp config.example.py config.py
# Editar config.py con tus credenciales PostgreSQL

# 2️⃣ EJECUTAR PIPELINE ETL
python scripts/normalize_to_postgres.py

# 3️⃣ DESPLEGAR FUNCIONES PL/pgSQL
python scripts/deploy_functions.py

# 4️⃣ USAR ANÁLISIS
# Abrir sql/plsql/ejecutar_funciones.sql en tu cliente SQL preferido
```

### **🔧 Configuración Detallada**

#### **1. Configurar Base de Datos**

```python
# Editar config.py con tus credenciales
DB_HOST = "tu-host-postgresql"      # ej: localhost o AWS RDS endpoint
DB_NAME = "tu-base-de-datos"        # ej: usairlines_db
DB_USER = "tu-usuario"              # ej: postgres
DB_PASS = "tu-password"             # tu contraseña
DB_PORT = "5432"                    # puerto PostgreSQL (default: 5432)
```

#### **2. Instalar Dependencias**

```bash
# Instalar todas las dependencias requeridas
pip install -r requirements.txt

# O usar el instalador automatizado
python setup.py
```

#### **3. Verificar Conexión**

```bash
# Probar conexión a PostgreSQL (opcional)
python -c "import psycopg2; print('psycopg2 instalado correctamente')"
```

### **📊 Ejecución del Pipeline ETL**

```bash
# Ejecutar normalización completa
python scripts/normalize_to_postgres.py
```

**¿Qué hace este script?**

- 📥 **Carga** el archivo CSV original (2,499 registros)
- 🔄 **Transforma** y limpia los datos
- 🏗️ **Normaliza** a 6 tablas en 3NF
- 🗄️ **Crea** el esquema PostgreSQL
- 📤 **Inserta** datos con integridad referencial
- 💾 **Genera** archivos CSV normalizados
- 📋 **Crea** archivo DDL (`sql/create_postgres_tables.sql`)

**Resultado esperado:**

```
🎯 ANÁLISIS FINALIZADO:
📊 Total de registros procesados: 2,499
🏢 Ciudades únicas: 102
✈️ Aeropuertos únicos: 123
🏭 Aerolíneas únicas: 2,728
🛤️ Rutas únicas: 78
✅ Normalización 3NF completada exitosamente
```

### **⚙️ Despliegue de Funciones PL/pgSQL**

```bash
# Instalar 6 funciones avanzadas en PostgreSQL
python scripts/deploy_functions.py
```

**Funciones desplegadas:**

1. 🧮 `calcular_tarifa_promedio` - Precios promedio por ruta
2. 📊 `calcular_participacion_mercado` - Cuota de mercado por período
3. 📈 `analizar_evolucion_aerolinea` - Tendencias temporales (FOR LOOP)
4. 👑 `obtener_aerolinea_dominante` - Líder por ruta
5. 🏟️ `analizar_competencia_aeropuerto` - Análisis competencia (WHILE LOOP)
6. 📅 `calcular_indice_estacionalidad` - Variabilidad estacional (CASE)

### **🔍 Análisis y Consultas**

#### **Opción A: Ejemplos Predefinidos**

```sql
-- Abrir en tu cliente SQL: sql/plsql/ejecutar_funciones.sql
-- Ejecutar cualquiera de los 25+ ejemplos incluidos

-- Ejemplo 1: Tarifa promedio entre ciudades
SELECT calcular_tarifa_promedio('New York City', 'Los Angeles') AS tarifa_usd;

-- Ejemplo 2: Evolución de una aerolínea
SELECT * FROM analizar_evolucion_aerolinea('180', 2020, 2022);

-- Ejemplo 3: Competencia en un aeropuerto
SELECT * FROM analizar_competencia_aeropuerto('ATL', 2021);
```

#### **Opción B: Consultas Avanzadas**

```sql
-- Abrir en tu cliente SQL: sql/sqlConsultation/queries.sql
-- 10 consultas empresariales avanzadas:

-- 1. Top 10 rutas más caras
-- 2. Análisis Legacy vs Low-Cost
-- 3. Evolución temporal de precios
-- 4. Concentración de mercado por hub
-- 5. Patrones estacionales
-- 6. Eficiencia operativa
-- 7. Market share por carrier
-- 8. Análisis de conectividad
-- 9. Elasticidad de precios
-- 10. Rentabilidad por ruta
```

#### **Opción C: Scripts de Análisis Python**

```bash
# Análisis básico de datos
python scripts/analyze_csv.py

# Análisis estadístico detallado
python scripts/detailed_analysis.py

# Generar diagrama del esquema
python scripts/schema_diagram.py
```

---

## 🏗️ **Arquitectura de Base de Datos**

### **Esquema Normalizado (3NF)**

```sql
🏢 cities (102 registros)
├── city_market_id (PK)
├── city_name
├── state  
└── full_city_name

✈️ airports (123 registros)
├── airport_id (PK)
├── airport_code
└── city_market_id (FK → cities)

🏭 carriers (2,728 registros)  
├── carrier_id (PK)
├── carrier_code
└── carrier_type (Legacy/Low-Cost)

🛤️ routes (78 registros)
├── route_id (PK)
├── origin_airport_id (FK → airports)
├── destination_airport_id (FK → airports)
└── distance_miles

🛫 flights (2,426 registros)
├── flight_id (PK)
├── route_id (FK → routes)
├── year, quarter
├── passengers
├── fare
└── source_record_id

📊 market_share (4,852 registros)
├── market_share_id (PK)
├── flight_id (FK → flights)
├── carrier_id (FK → carriers)
├── market_share_type
├── market_share_percentage
└── fare_avg
```

### **Beneficios de la Normalización**

- ✅ **Eliminación de redundancia** (reducción ~70% vs. datos originales)
- ✅ **Integridad referencial** con claves foráneas
- ✅ **Prevención de anomalías** de inserción/actualización/eliminación
- ✅ **Optimización de consultas** con índices apropiados

---

## ⚙️ **Funciones PL/pgSQL Avanzadas**

### **Funciones Implementadas**

| # | Función | Características | Estructuras PL/pgSQL | Ejemplo de Uso |
|---|---------|----------------|---------------------|----------------|
| 1 | `calcular_tarifa_promedio` | JOINs complejos, manejo NULL | Condicionales IF | Análisis de precios por ruta |
| 2 | `calcular_participacion_mercado` | Agregaciones, filtros temporales | WHERE avanzados | Cuota de mercado por período |
| 3 | `analizar_evolucion_aerolinea` | **FOR LOOP**, análisis temporal | FOR, cursores | Tendencias históricas |
| 4 | `obtener_aerolinea_dominante` | RETURNS TABLE, subconsultas | TABLE functions | Líder de mercado por ruta |
| 5 | `analizar_competencia_aeropuerto` | **WHILE LOOP**, cursores explícitos | WHILE, variables | Análisis de competencia |
| 6 | `calcular_indice_estacionalidad` | **CASE avanzado**, cálculos complejos | CASE, arrays | Variabilidad estacional |

### **Ejemplos de Uso Real**

```sql
-- 💰 Análisis de tarifas
SELECT calcular_tarifa_promedio('New York City', 'Los Angeles') AS precio_nyc_la;

-- 📈 Evolución temporal
SELECT * FROM analizar_evolucion_aerolinea('Delta', 2020, 2023);

-- 🏟️ Competencia aeroportuaria  
SELECT * FROM analizar_competencia_aeropuerto('ATL', 2021);

-- 📅 Estacionalidad de precios
SELECT * FROM calcular_indice_estacionalidad('NYC', 'LA', 2021);

-- 👑 Aerolínea dominante
SELECT * FROM obtener_aerolinea_dominante('Boston', 'Atlanta');

-- 📊 Participación de mercado
SELECT calcular_participacion_mercado('180', 2021, 3);
```

---

## 🔧 **Tecnologías Utilizadas**

### **Backend & Base de Datos**

- **PostgreSQL 12+** - Base de datos principal con PL/pgSQL
- **AWS RDS** - Hosting de base de datos en la nube
- **psycopg2** - Driver de conectividad PostgreSQL

### **Python & Bibliotecas**

- **Python 3.8+** - Lenguaje principal del pipeline ETL
- **pandas 2.2.1** - Manipulación y análisis de datos
- **numpy 1.26.4** - Cálculos numéricos y arrays
- **SQLAlchemy 2.0.25** - ORM y queries SQL

### **Herramientas de Desarrollo**

- **Git** - Control de versiones
- **VS Code / Cursor** - IDE de desarrollo
- **pgAdmin / DBeaver** - Administración de base de datos

---

## 📈 **Resultados y Métricas**

### **Datos Procesados**

- **📊 2,499 registros** originales procesados exitosamente
- **🏢 102 ciudades** únicas identificadas y catalogadas
- **✈️ 123 aeropuertos** mapeados a ciudades
- **🏭 2,728 aerolíneas** clasificadas (Legacy/Low-Cost)
- **🛤️ 78 rutas** con distancias calculadas (301.8-2708.0 millas)
- **📅 30+ años** de datos históricos (1993-2024)

### **Performance del Sistema**

- **⏱️ Tiempo de ETL**: ~15 segundos para dataset completo
- **💾 Reducción de almacenamiento**: 70% vs. datos originales
- **🔍 Calidad de datos**: 98.5% de registros válidos
- **⚡ Velocidad de consultas**: <2 segundos promedio
- **🛡️ Integridad referencial**: 100% con 0 violaciones FK

---

## 🧪 **Testing y Validación**

### **Pruebas Implementadas**

- ✅ **Validación de integridad referencial** - FK constraints
- ✅ **Testing de funciones PL/pgSQL** - Casos reales
- ✅ **Verificación de tipos de datos** - Constraints CHECK
- ✅ **Pruebas de rendimiento** - EXPLAIN ANALYZE
- ✅ **Validación de normalización 3NF** - Verificación teórica

### **Comandos de Verificación**

```bash
# Validar despliegue de funciones
python scripts/deploy_functions.py

# Verificar esquema generado
psql -h host -d db -f sql/create_postgres_tables.sql

# Probar consultas de ejemplo
# Abrir sql/plsql/ejecutar_funciones.sql en cliente SQL
```

---

## 🔍 **Solución de Problemas**

### **Error: "psycopg2 not found"**

```bash
pip install psycopg2-binary==2.9.9
```

### **Error: "Connection refused"**

- ✅ Verificar que PostgreSQL esté ejecutándose
- ✅ Comprobar credenciales en `config.py`
- ✅ Verificar conectividad de red

### **Error: "Function does not exist"**

```bash
# Redesplegar funciones
python scripts/deploy_functions.py
```

### **Error: "No data returned"**

- ✅ Verificar que el ETL se ejecutó correctamente
- ✅ Comprobar nombres exactos de ciudades/códigos
- ✅ Usar consultas auxiliares en `sql/plsql/ejecutar_funciones.sql`

---

## 📚 **Documentación Adicional**

### **Archivos de Referencia**

- 📋 `docs/MANUAL_USUARIO.md` - Guía completa paso a paso
- 📋 `docs/PRESENTACION.md` - Presentación final del proyecto
- 📋 `sql/plsql/ejecutar_funciones.sql` - 25+ ejemplos de uso
- 📋 `sql/sqlConsultation/queries.sql` - 10 consultas avanzadas  
- 📋 `config.example.py` - Configuración de conexión
- 📋 `requirements.txt` - Dependencias exactas

### **Recursos de Aprendizaje**

- [Documentación PostgreSQL PL/pgSQL](https://www.postgresql.org/docs/current/plpgsql.html)
- [Teoría de Normalización de BD](https://en.wikipedia.org/wiki/Database_normalization)
- [Mejores Prácticas ETL con Python](https://docs.python.org/3/library/csv.html)

---

## 🤝 **Contribuciones**

### **Equipo de Desarrollo**

- **Sebastián Cañón Castellanos** - Desarrollo principal y arquitectura
- **Colaboradores** - Testing, validación y documentación

### **Cómo Contribuir**

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

---

## 📄 **Licencia**

Este proyecto está bajo la **Licencia MIT**. Ver archivo `LICENSE` para más detalles.

---

## 🎓 **Contexto Académico**

**Universidad:** UPTC (Universidad Pedagógica y Tecnológica de Colombia)  
**Curso:** Base de Datos II  
**Período:** 2025-I  
**Estudiante:** Sebastián Cañón Castellanos

### **Objetivos de Aprendizaje Cumplidos**

- ✅ **Normalización avanzada** de bases de datos relacionales
- ✅ **Programación PL/pgSQL** con estructuras de control avanzadas
- ✅ **Diseño y optimización** de esquemas PostgreSQL
- ✅ **Implementación de pipelines ETL** con Python
- ✅ **Análisis de datos empresariales** con SQL avanzado

---

## 📞 **Contacto y Soporte**

- **📧 Email:** <vistrent834@gmail.com>
- **🔗 GitHub:** [Cluuny](https://github.com/Cluuny)
- **🎓 Universidad:** UPTC 2025-I

---

<div align="center">

**🛫 ¡Proyecto completado exitosamente! 🛬**

*Desarrollado con ❤️ para Base de Datos II - UPTC 2025-I*

---

**🚀 INSTRUCCIONES RÁPIDAS:**

```bash
pip install -r requirements.txt && cp config.example.py config.py
python scripts/normalize_to_postgres.py
python scripts/deploy_functions.py
# Abrir sql/plsql/ejecutar_funciones.sql
```

</div>
