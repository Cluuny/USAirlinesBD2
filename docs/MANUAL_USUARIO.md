# 📖 Manual de Usuario - USAirlinesBD2

> **Guía completa para usar el sistema de análisis de rutas y tarifas aéreas**

---

## 🎯 **Introducción**

Este manual te guiará paso a paso para ejecutar y utilizar el sistema de análisis de rutas y tarifas aéreas estadounidenses. El proyecto incluye normalización de datos, funciones PL/pgSQL avanzadas y consultas de análisis empresarial.

---

## ⚡ **Ejecución Rápida (5 pasos)**

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar base de datos
cp config.example.py config.py
# Editar config.py con tus credenciales

# 3. Ejecutar normalización ETL
python scripts/normalize_to_postgres.py

# 4. Desplegar funciones PL/pgSQL
python scripts/deploy_functions.py

# 5. Usar consultas de análisis
# Abrir sql/plsql/ejecutar_funciones.sql en tu cliente SQL
```

---

## 🗂️ **Guía de Archivos Principales**

| Archivo | Ubicación | Propósito | Cuándo Usarlo |
|---------|-----------|-----------|---------------|
| `normalize_to_postgres.py` | `scripts/` | ETL principal | Primera ejecución |
| `deploy_functions.py` | `scripts/` | Instalar funciones | Después del ETL |
| `ejecutar_funciones.sql` | `sql/plsql/` | Ejemplos de uso | Para análisis |
| `queries.sql` | `sql/sqlConsultation/` | Consultas SQL | Análisis avanzado |
| `create_postgres_tables.sql` | `sql/` | DDL del esquema | Referencia |

---

## 🚀 **Proceso Paso a Paso**

### **Paso 1: Configuración Inicial**

#### Configurar Base de Datos
```python
# Editar config.py con tus credenciales
DB_HOST = "tu-host-postgresql"
DB_NAME = "tu-base-de-datos"
DB_USER = "tu-usuario"
DB_PASS = "tu-password"
DB_PORT = "5432"
```

#### Instalar Dependencias
```bash
pip install -r requirements.txt
```

### **Paso 2: Ejecutar Pipeline ETL**

```bash
# Normalizar datos y crear tablas
python scripts/normalize_to_postgres.py
```

**¿Qué hace este script?**
- ✅ Lee CSV original de 2,499 registros
- ✅ Normaliza a 6 tablas en 3NF
- ✅ Crea esquema PostgreSQL
- ✅ Inserta datos con integridad referencial
- ✅ Genera archivos CSV normalizados

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

### **Paso 3: Desplegar Funciones PL/pgSQL**

```bash
# Instalar 6 funciones avanzadas
python scripts/deploy_functions.py
```

**Funciones instaladas:**
1. `calcular_tarifa_promedio` - Precios promedio por ruta
2. `calcular_participacion_mercado` - Cuota de mercado
3. `analizar_evolucion_aerolinea` - Tendencias temporales
4. `obtener_aerolinea_dominante` - Líder por ruta
5. `analizar_competencia_aeropuerto` - Análisis de competencia
6. `calcular_indice_estacionalidad` - Variabilidad estacional

### **Paso 4: Ejecutar Análisis**

#### Opción A: Usar Ejemplos Predefinidos
```sql
-- Abrir sql/plsql/ejecutar_funciones.sql
-- Ejecutar cualquier consulta de ejemplo

-- Ejemplo: Tarifa promedio NYC-LA
SELECT calcular_tarifa_promedio('New York City', 'Los Angeles');

-- Ejemplo: Evolución de aerolínea
SELECT * FROM analizar_evolucion_aerolinea('180', 2020, 2022);
```

#### Opción B: Consultas SQL Avanzadas
```sql
-- Abrir sql/sqlConsultation/queries.sql
-- Ejecutar análisis empresariales avanzados

-- Top 10 rutas más caras
-- Análisis de competencia Legacy vs Low-Cost
-- Patrones estacionales
-- Concentración de mercado
```

---

## 💡 **Ejemplos de Uso Prácticos**

### **Análisis de Precios**
```sql
-- ¿Cuál es la tarifa promedio NYC-LA?
SELECT calcular_tarifa_promedio('New York City', 'Los Angeles') AS tarifa_usd;

-- ¿Qué aerolínea domina la ruta Boston-Atlanta?
SELECT * FROM obtener_aerolinea_dominante('Boston', 'Atlanta');
```

### **Análisis de Mercado**
```sql
-- ¿Cómo evolucionó Delta Airlines 2020-2022?
SELECT * FROM analizar_evolucion_aerolinea('180', 2020, 2022);

-- ¿Qué nivel de competencia hay en aeropuerto ATL?
SELECT * FROM analizar_competencia_aeropuerto('ATL', 2021);
```

### **Análisis Estacional**
```sql
-- ¿Hay estacionalidad en precios NYC-LA?
SELECT * FROM calcular_indice_estacionalidad('New York City', 'Los Angeles', 2021);
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
- ✅ Usar consultas auxiliares en `ejecutar_funciones.sql`

---

## 📊 **Interpretación de Resultados**

### **Tarifas**
- Valores en USD
- `NULL` o `0` = No hay datos para esa ruta

### **Participación de Mercado**
- Valores de 0-100 (porcentaje)
- Mayor valor = Mayor dominancia

### **Tendencias**
- `CRECIMIENTO` = Aerolínea expandiéndose
- `DECLIVE` = Aerolínea perdiendo mercado
- `ESTABLE` = Sin cambios significativos
- `INICIAL` = Datos insuficientes

### **Competencia**
- `MONOPOLIO` = 1 aerolínea dominante (>80%)
- `DOMINANTE` = 1 aerolínea líder (60-80%)
- `COMPETITIVO` = Múltiples competidores
- `FRAGMENTADO` = Muy disperso

### **Estacionalidad**
- Índice `1.0` = Normal
- Índice `>1.0` = Precios altos
- Índice `<1.0` = Precios bajos

---

## 🎯 **Casos de Uso Empresariales**

### **Para Aerolíneas**
```sql
-- ¿En qué rutas tengo ventaja competitiva?
SELECT * FROM obtener_aerolinea_dominante('ciudad1', 'ciudad2');

-- ¿Cómo es mi evolución temporal?
SELECT * FROM analizar_evolucion_aerolinea('mi_codigo', 2020, 2023);
```

### **Para Aeropuertos**
```sql
-- ¿Qué nivel de competencia tengo?
SELECT * FROM analizar_competencia_aeropuerto('MI_CODIGO', 2021);
```

### **Para Analistas**
```sql
-- ¿Qué rutas son más rentables?
SELECT calcular_tarifa_promedio(origen, destino) FROM rutas_populares;

-- ¿Hay patrones estacionales?
SELECT * FROM calcular_indice_estacionalidad('NYC', 'LA', 2021);
```

---

## 📈 **Optimizaciones y Tips**

### **Performance**
- Las consultas están optimizadas con índices
- Para datasets grandes, considera limitar por año
- Usa parámetros específicos para mejores resultados

### **Datos de Calidad**
- Usa nombres exactos de ciudades (case-sensitive)
- Códigos de aerolíneas son numéricos como string
- Años disponibles: consulta `SELECT DISTINCT year FROM flights`

### **Mejores Prácticas**
1. Ejecutar ETL solo una vez por dataset
2. Redesplegar funciones tras cambios de esquema
3. Usar consultas auxiliares para validar parámetros
4. Ejecutar ejemplos antes de crear consultas custom

---

## 📞 **Soporte**

### **Recursos Disponibles**
- 📋 `sql/plsql/ejecutar_funciones.sql` - 25+ ejemplos listos
- 📋 `sql/sqlConsultation/queries.sql` - 10 consultas avanzadas
- 📋 `README.md` - Documentación técnica completa

### **Contacto**
- **GitHub:** [Issues en el repositorio](https://github.com/usuario/USAirlinesBD2/issues)
- **Email:** sebastian.ca0102@gmail.com

---

<div align="center">

**✈️ ¡Listo para analizar el mercado aéreo estadounidense! 🛬**

*Manual actualizado para la versión reorganizada del proyecto*

</div> 