# Análisis de Rutas y Tarifas Aéreas en EE.UU. (1993-2024)

Este proyecto analiza un conjunto de datos históricos sobre rutas de vuelo y tarifas aéreas en Estados Unidos, abarcando el período de 1993 a 2024. El dataset incluye información sobre aerolíneas tradicionales y de bajo costo, permitiendo análisis detallados de precios, rutas y competencia en el mercado.

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.8 o superior
- Git
- Aproximadamente 1GB de espacio libre en disco (para el dataset y el entorno virtual)

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

## 📊 Uso de los Scripts

El proyecto incluye dos scripts principales para análisis de datos:

### 1. Análisis Básico (`analyze_csv.py`)

Proporciona un resumen rápido del dataset:

```bash
python analyze_csv.py
```

Este script muestra:

- Total de registros
- Período que abarca el dataset
- Número de rutas y aeropuertos únicos
- Estadísticas básicas de precios
- Top 5 rutas más frecuentes

### 2. Análisis Detallado (`detailed_analysis.py`)

Ofrece un análisis interactivo más profundo:

```bash
python detailed_analysis.py
```

Incluye las siguientes opciones de análisis:

1. **Análisis Temporal**: Tendencias anuales y trimestrales
2. **Análisis de Rutas**: Rutas más caras y más largas
3. **Análisis de Competencia**: Comparación entre aerolíneas tradicionales y de bajo costo
4. **Análisis Estacional**: Patrones trimestrales de precios y pasajeros

## 📁 Estructura del Proyecto

```text
.
├── README.md
├── requirements.txt
├── analyze_csv.py
├── detailed_analysis.py
└── archive/
    ├── US Airline Flight Routes and Fares 1993-2024.csv
    └── references.json
```

## 📖 Descripción de los Archivos

- `analyze_csv.py`: Script para análisis básico y rápido
- `detailed_analysis.py`: Script para análisis detallado e interactivo
- `requirements.txt`: Lista de dependencias de Python
- `references.json`: Documentación detallada de las columnas del dataset

## 🔧 Solución de Problemas Comunes

1. **Error al activar el entorno virtual**
   - Asegúrate de estar en el directorio correcto
   - En Windows, si hay problemas con la ejecución de scripts:

     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```

2. **Problemas de memoria**
   - El dataset es grande, asegúrate de tener al menos 8GB de RAM disponible
   - Si hay problemas, usa el parámetro `low_memory=True` en `pd.read_csv()`

3. **Errores de codificación**
   - Si hay problemas con caracteres especiales, verifica que los archivos estén en UTF-8
