# 📊 Data - Directorio de Datos del News Summarizer

Almacena todos los datos financieros generados por el sistema, incluyendo precios actuales, datos históricos, análisis de correlación y métricas de volatilidad.

## 📁 Estructura del Directorio

```
data/
├── processed/              # Datos procesados y listos para análisis
│   ├── current_prices_*.csv      # Precios actuales con timestamp
│   ├── historical_*_*.csv        # Datos históricos por acción
│   ├── correlation_matrix_*.csv  # Matrices de correlación
│   ├── volatility_ranking_*.csv  # Rankings de volatilidad
│   ├── processing_info.json      # Metadatos de procesamiento
│   └── .gitkeep                 # Mantiene directorio en git
└── raw/                    # Datos en bruto (futuro uso)
    ├── creditcard.csv      # Datos de ejemplo (no relacionado)
    └── .gitkeep           # Mantiene directorio en git
```

## 📈 Tipos de Datos Generados

### 1. 💰 Precios Actuales (`current_prices_YYYYMMDD_HHMMSS.csv`)

**Contenido**: Snapshot de precios en tiempo real de todas las acciones monitoreadas

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `symbol` | Símbolo de la acción | SQM-B.SN |
| `name` | Nombre de la empresa | SQM |
| `current_price` | Precio actual en CLP | 44160.00 |
| `previous_price` | Precio del día anterior | 42954.00 |
| `change` | Cambio absoluto | 1206.00 |
| `change_percent` | Cambio porcentual | 2.81 |
| `volume` | Volumen de transacciones | 471364 |
| `market_cap` | Capitalización de mercado | 12255063179264 |
| `currency` | Moneda | CLP |
| `last_updated` | Timestamp de actualización | 2025-09-05 23:14:30 |

**📊 Métricas**: 9 acciones activas, actualización cada 5 minutos (durante mercado abierto)

### 2. 📈 Datos Históricos (`historical_[SYMBOL]_YYYYMMDD_HHMMSS.csv`)

**Contenido**: Series temporales completas con indicadores técnicos

| Categoría | Columnas | Descripción |
|-----------|----------|-------------|
| **OHLCV** | Open, High, Low, Close, Volume | Datos básicos de precio |
| **Medias Móviles** | SMA_20, SMA_50, EMA_12, EMA_26 | Medias simples y exponenciales |
| **MACD** | MACD, MACD_Signal, MACD_Histogram | Convergencia/Divergencia |
| **RSI** | RSI | Índice de Fuerza Relativa |
| **Bollinger** | BB_Upper, BB_Middle, BB_Lower | Bandas de volatilidad |
| **Volatilidad** | Daily_Return, Volatility | Retornos y volatilidad |
| **Metadatos** | symbol, name | Identificación de la acción |

**📊 Cobertura**: 248+ registros por acción (1 año de datos), 15+ indicadores por registro

### 3. 🔗 Matriz de Correlación (`correlation_matrix_YYYYMMDD_HHMMSS.csv`)

**Contenido**: Correlaciones entre las principales 6 acciones del mercado

```csv
,SQM,Falabella,Cencosud,Copec,CCU,Banco de Chile
SQM,1.0,0.264,-0.449,0.579,-0.297,-0.327
Falabella,0.264,1.0,0.620,0.323,-0.769,0.693
...
```

**📊 Interpretación**:
- **1.0**: Correlación perfecta positiva
- **0.0**: Sin correlación  
- **-1.0**: Correlación perfecta negativa
- **Rango útil**: |0.3| para correlaciones significativas

### 4. 📊 Ranking de Volatilidad (`volatility_ranking_YYYYMMDD_HHMMSS.csv`)

**Contenido**: Clasificación de acciones por nivel de riesgo/volatilidad

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `symbol` | Símbolo de la acción | SQM-B.SN |
| `name` | Nombre de empresa | SQM |
| `current_volatility` | Volatilidad actual (%) | 58.90 |
| `avg_volatility` | Volatilidad promedio (%) | 45.23 |
| `volatility_rank` | Clasificación | High/Medium/Low |

**📊 Clasificación**:
- 🔴 **High**: > 30% anualizada
- 🟡 **Medium**: 15-30% anualizada  
- 🟢 **Low**: < 15% anualizada

## ⏰ Sistema de Timestamps

### Formato de Archivos
```
[tipo_datos]_[simbolo_opcional]_YYYYMMDD_HHMMSS.csv
```

### Ejemplos Reales
- `current_prices_20250905_231429.csv` - Precios del 5 sept 2025 a las 23:14:29
- `historical_SQM_B_20250905_231429.csv` - Histórico de SQM del mismo momento
- `correlation_matrix_20250905_231429.csv` - Correlaciones del mismo momento

### 🔄 Frecuencia de Actualización
- **Precios actuales**: Cada 5 minutos (horario bursátil)
- **Datos históricos**: Cada 1 hora
- **Correlaciones**: Cada 1 hora
- **Volatilidad**: Cada 30 minutos

## 📊 Estadísticas de Datos

### 📈 Volumen de Datos Actual
```
📁 Archivos CSV activos: 12
├── 📄 current_prices: 1 archivo (~1 KB)
├── 📈 historical_data: 9 archivos (~2.5 MB total)
├── 🔗 correlation_matrix: 1 archivo (~1 KB)  
└── 📊 volatility_ranking: 1 archivo (~1 KB)

📊 Total de registros: ~2,232 (248 registros × 9 acciones)
💾 Espacio ocupado: ~2.5 MB
🔄 Actualización: Automática durante ejecución
```

### 📅 Cobertura Temporal
- **Datos históricos**: 1 año completo por acción
- **Frecuencia**: Diaria (días bursátiles)
- **Período cubierto**: Septiembre 2024 - Septiembre 2025
- **Días incluidos**: ~248 días bursátiles por acción

## 🛠️ Uso de los Datos

### 📊 Carga en Python
```python
import pandas as pd

# Cargar precios actuales
current = pd.read_csv('data/processed/current_prices_20250905_231429.csv')

# Cargar datos históricos de SQM
sqm_hist = pd.read_csv('data/processed/historical_SQM_B_20250905_231429.csv', 
                       index_col=0, parse_dates=True)

# Cargar matriz de correlación  
corr_matrix = pd.read_csv('data/processed/correlation_matrix_20250905_231429.csv',
                          index_col=0)
```

### 📈 Análisis Típicos
```python
# Análisis de volatilidad
vol_data = pd.read_csv('data/processed/volatility_ranking_20250905_231429.csv')
high_vol_stocks = vol_data[vol_data['volatility_rank'] == 'High']

# Análisis de correlación
corr_matrix = pd.read_csv('correlation_matrix.csv', index_col=0)
strong_correlations = corr_matrix[abs(corr_matrix) > 0.7]

# Análisis técnico
sqm = pd.read_csv('historical_SQM_B.csv', index_col=0, parse_dates=True)
buy_signals = sqm[(sqm['RSI'] < 30) & (sqm['Close'] > sqm['SMA_20'])]
```

## 🗂️ Gestión de Archivos

### 🔄 Rotación Automática
- Los archivos antiguos se mantienen para análisis histórico
- Nuevos archivos se generan cada ejecución del sistema
- Nombres únicos garantizan no sobreescritura

### 📦 Backup y Archivado
```bash
# Backup manual de datos importantes
cp data/processed/current_prices_*.csv backup/
cp data/processed/historical_*.csv backup/

# Limpiar archivos antiguos (opcional)
find data/processed -name "*.csv" -mtime +7 -delete  # Archivos > 7 días
```

### 💾 Optimización de Espacio
- Formato CSV para compatibilidad universal
- Compresión automática en archivos grandes (futuro)
- Índices temporales para consultas rápidas

---

📊 **Los datos se actualizan automáticamente durante el funcionamiento del sistema**  
📈 **Para datos más recientes, ejecutar `python3 src/data_sources/yahoo_finance.py`**
🔄 **Sistema optimizado para análisis en tiempo real y investigación histórica**
