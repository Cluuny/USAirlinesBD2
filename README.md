# Análisis de Rutas y Tarifas Aéreas en EE.UU. (1993-2024)

Este proyecto analiza un conjunto de datos históricos sobre rutas de vuelo y tarifas aéreas en Estados Unidos, abarcando el período de 1993 a 2024. El dataset incluye información sobre aerolíneas tradicionales y de bajo costo, permitiendo análisis detallados de precios, rutas y competencia en el mercado.

## 🏗️ Arquitectura del Proyecto

El proyecto implementa una **base de datos normalizada en 3NF (Tercera Forma Normal)** con las siguientes tablas:

- **`cities`** - Información de ciudades y estados
- **`airports`** - Aeropuertos vinculados a ciudades  
- **`carriers`** - Aerolíneas clasificadas (Legacy/Low-Cost)
- **`routes`** - Rutas únicas entre aeropuertos
- **`flights`** - Vuelos específicos por ruta y período
- **`market_share`** - Participación de mercado por aerolínea

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.8 o superior
- PostgreSQL 12 o superior
- Git
- Aproximadamente 1GB de espacio libre en disco

### Configuración del Entorno

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/Cluuny/USAirlinesBD2.git
   cd USAirlinesBD2
   ```

2. **Crear y activar el entorno virtual**

   En Windows:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

   En macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**

   Copia `config.example.py` a `config.py` y actualiza con tus credenciales:
   ```bash
   cp config.example.py config.py
   ```

   O configura variables de entorno:
   ```bash
   export DB_HOST=your-database-host
   export DB_NAME=your-database-name
   export DB_USER=your-username
   export DB_PASS=your-password
   export DB_PORT=5432
   ```

## 📊 Uso de los Scripts

### 1. Normalización de Datos (`normalize_to_postgres.py`)

Script principal para normalizar datos y poblar PostgreSQL:

```bash
python normalize_to_postgres.py
```

Este script:
- Carga y limpia los datos del CSV
- Normaliza la estructura a 3NF
- Crea las tablas en PostgreSQL
- Inserta los datos normalizados
- Genera el archivo DDL (`create_postgres_tables.sql`)

### 2. Análisis Básico (`analyze_csv.py`)

Proporciona un resumen rápido del dataset:

```bash
python analyze_csv.py
```

### 3. Análisis Detallado (`detailed_analysis.py`)

Ofrece análisis interactivo más profundo:

```bash
python detailed_analysis.py
```

### 4. Visualización del Esquema (`schema_diagram.py`)

Genera un diagrama visual del esquema de base de datos:

```bash
python schema_diagram.py
```

## 📁 Estructura del Proyecto

```text
USAirlinesBD2/
├── README.md                      # Documentación principal
├── requirements.txt               # Dependencias Python
├── config.example.py             # Configuración de ejemplo
├── .gitignore                    # Archivos ignorados por Git
│
├── archive/                      # Datos originales
│   ├── US Airline Flight Routes and Fares 1993-2024.csv
│   ├── US_Airline_Flight_Routes_and_Fares_1993_2024__2.xlsx
│   └── references.json
│
├── normalized_data/              # Datos normalizados (CSV)
│   ├── cities.csv
│   ├── airports.csv
│   ├── carriers.csv
│   ├── routes.csv
│   ├── flights.csv
│   └── market_share.csv
│
├── normalize_to_postgres.py      # Script principal de normalización
├── analyze_csv.py               # Análisis básico de datos
├── detailed_analysis.py         # Análisis detallado e interactivo
├── schema_diagram.py            # Generador de diagrama del esquema
└── create_postgres_tables.sql   # DDL generado automáticamente
```

## 🔧 Funcionalidades Principales

### Normalización 3NF
- ✅ **1NF**: Todos los atributos son atómicos
- ✅ **2NF**: No hay dependencias parciales
- ✅ **3NF**: No hay dependencias transitivas

### Beneficios
- Elimina redundancia de datos
- Previene anomalías de actualización
- Mejora la integridad de datos
- Facilita consultas complejas

### Características Técnicas
- **ETL completo**: Extracción, transformación y carga
- **Validación de datos**: Limpieza automática de inconsistencias
- **Integridad referencial**: Claves foráneas y restricciones
- **Escalabilidad**: Optimizado para grandes volúmenes de datos

## 🛠️ Solución de Problemas

1. **Error de conexión PostgreSQL**
   - Verifica las credenciales en `config.py`
   - Asegúrate de que PostgreSQL esté ejecutándose
   - Confirma que la base de datos existe

2. **Problemas de memoria**
   - El dataset es grande, asegúrate de tener al menos 8GB RAM
   - Ajusta `BATCH_SIZE` en la configuración si es necesario

3. **Errores de codificación**
   - Verifica que los archivos CSV estén en UTF-8

4. **Dependencias faltantes**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## 📈 Análisis Disponibles

1. **Análisis Temporal**: Tendencias anuales y trimestrales
2. **Análisis de Rutas**: Rutas más caras y populares
3. **Análisis de Competencia**: Comparación Legacy vs Low-Cost
4. **Análisis Estacional**: Patrones por trimestre
5. **Market Share**: Participación de mercado por aerolínea

## 🔒 Seguridad

- Las credenciales se manejan mediante variables de entorno
- Los archivos de configuración están excluidos del control de versiones
- Se utilizan conexiones seguras a la base de datos

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea tu rama de características (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si tienes problemas o preguntas, por favor abre un issue en GitHub.
