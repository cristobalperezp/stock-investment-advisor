# 🏗️ Source Code - News Summarizer

Código fuente principal del News Summarizer, organizado en módulos especializados para extracción de datos, interfaces de usuario y utilidades del sistema.

## 📁 Estructura del Código Fuente

```
src/
├── data_sources/          # 📊 Extracción de datos financieros
│   ├── __init__.py            # Configuración del módulo
│   └── yahoo_finance.py       # Módulo completo de Yahoo Finance API
│
├── ui/                    # 🖥️ Interfaces de usuario
│   ├── __init__.py            # Configuración UI con Streamlit/FastAPI
│   ├── streamlit_app.py       # Dashboard principal Streamlit
│   ├── pages.py              # Páginas adicionales (Análisis, Config)  
│   └── README.md             # Documentación específica de UI
│
└── utils/                 # 🔧 Utilidades del sistema
    ├── __init__.py            # Configuración de utilidades
    └── config.py             # Gestor de configuración YAML
```

## 📊 Módulo: data_sources

### 🎯 Propósito
Extrae y procesa datos financieros desde fuentes externas, principalmente Yahoo Finance, transformándolos en formatos listos para análisis y visualización.

### 📈 `yahoo_finance.py` - Extractor Principal
**Clase Principal**: `YahooFinanceDataExtractor`

#### 🔧 Métodos Principales

| Método | Descripción | Retorno | Uso |
|--------|-------------|---------|-----|
| `get_current_prices()` | Precios actuales de todas las acciones | DataFrame | Dashboard en tiempo real |
| `get_historical_data(symbol, period)` | Datos históricos con indicadores técnicos | DataFrame | Gráficos de análisis técnico |
| `get_multiple_historical_data()` | Datos históricos paralelos | Dict[DataFrame] | Comparaciones múltiples |
| `get_market_summary()` | Resumen del estado del mercado | Dict | Métricas principales |
| `get_market_movers(limit)` | Top ganadores y perdedores | Dict[DataFrame] | Rankings de rendimiento |
| `get_correlation_matrix()` | Matriz de correlaciones | DataFrame | Análisis de diversificación |
| `get_volatility_ranking()` | Ranking de volatilidad | DataFrame | Análisis de riesgo |
| `get_trading_signals(symbol)` | Señales automáticas de trading | Dict | Decisiones de compra/venta |
| `get_sector_performance()` | Rendimiento por sectores | Dict | Análisis macro |
| `save_data_to_csv()` | Exportar datos a archivos CSV | Dict | Persistencia de datos |

#### 🎯 Características Técnicas
- **⚡ Concurrencia**: ThreadPoolExecutor para consultas paralelas
- **🛡️ Error Handling**: Manejo robusto de errores de red y datos faltantes
- **📊 Indicadores Técnicos**: 15+ indicadores calculados automáticamente
- **💾 Cache**: Optimizado para uso con Streamlit cache
- **📝 Logging**: Sistema completo de logs para debugging

#### 📈 Indicadores Implementados
```python
# Medias móviles
df['SMA_20'] = df['Close'].rolling(window=20).mean()
df['SMA_50'] = df['Close'].rolling(window=50).mean()
df['EMA_12'] = df['Close'].ewm(span=12).mean()
df['EMA_26'] = df['Close'].ewm(span=26).mean()

# MACD
df['MACD'] = df['EMA_12'] - df['EMA_26']
df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()

# RSI, Bollinger Bands, Volatilidad
# ... (ver implementación completa)
```

## 🖥️ Módulo: ui

### 🎯 Propósito
Interfaces de usuario interactivas para visualización y análisis de datos financieros con navegación multi-página y gráficos profesionales.

### 📊 `streamlit_app.py` - Dashboard Principal
**Función Principal**: `main()`

#### 🏠 Dashboard Principal
- **📈 Resumen del mercado**: 4 métricas clave en tiempo real
- **🏆 Top performers**: Ganadores y perdedores del día  
- **💰 Tabla de precios**: DataFrames formateados con colores
- **📊 Análisis técnico**: Gráficos de velas con indicadores superpuestos
- **🎯 Señales de trading**: Sistema automático de señales
- **🔗 Análisis de correlación**: Heatmaps interactivos
- **📊 Volatilidad**: Rankings con clasificación por riesgo

#### 🎨 Funciones de Visualización
| Función | Propósito | Tecnología |
|---------|-----------|------------|
| `create_price_chart()` | Gráficos de velas + indicadores | Plotly Candlestick |
| `create_correlation_heatmap()` | Matriz de correlación | Plotly Heatmap |
| `create_volatility_chart()` | Ranking de volatilidad | Plotly Bar Chart |
| `display_trading_signals()` | Señales coloreadas | Streamlit Success/Error |

### 📑 `pages.py` - Páginas Adicionales

#### 🔬 Análisis Avanzado (`show_advanced_analytics()`)
- **📈 Comparación múltiple**: Selección de acciones para comparar
- **📊 Rendimiento normalizado**: Gráficos base 100
- **🎯 Señales múltiples**: Trading signals para múltiples acciones

#### 🏛️ Resumen del Mercado (`show_market_overview()`)
- **🏢 Análisis sectorial**: Rendimiento por industria
- **🌡️ Mapa de calor**: Treemaps interactivos
- **📊 Métricas agregadas**: Estadísticas consolidadas

#### ⚙️ Configuración (`show_settings()`)
- **🎨 Personalización**: Temas, períodos, layout
- **📈 Indicadores técnicos**: Parámetros configurables
- **🚨 Sistema de alertas**: Umbrales personalizables
- **ℹ️ Info del sistema**: Estado y métricas

## 🔧 Módulo: utils

### 🎯 Propósito
Utilidades transversales del sistema, principalmente gestión de configuración y funciones auxiliares.

### ⚙️ `config.py` - Gestor de Configuración
**Clase Principal**: `ConfigManager`

#### 🔧 Funcionalidades
- **📝 Carga YAML**: Parsing de config.yaml con validación
- **🌐 Variables de entorno**: Reemplazo de ${VAR} con valores reales
- **🎯 Acceso por puntos**: Notación `api.openai_api_key` para navegar config
- **⚡ Cache**: Configuración cargada una vez y reutilizada
- **🛡️ Defaults**: Valores por defecto para configuraciones faltantes

#### 📊 Métodos Principales
```python
config = ConfigManager()

# Acceso general
config.get('stock_market.top_stocks')

# Acceso especializado  
config.get_stock_symbols()           # Lista de símbolos
config.get_api_keys()               # Diccionario de API keys
config.get_streamlit_config()       # Config específica de Streamlit
config.is_data_source_enabled()     # Verificar fuentes habilitadas
```

## 🏗️ Arquitectura del Sistema

### 🔄 Flujo de Datos
```
Yahoo Finance API
       ↓
YahooFinanceDataExtractor
       ↓  
Data Processing + Technical Indicators
       ↓
Streamlit Cache Layer
       ↓
UI Components (Charts, Tables, Metrics)
       ↓
Interactive Dashboard
```

### ⚡ Sistema de Cache
```python
@st.cache_data(ttl=300)    # 5 min - datos en tiempo real
def load_market_data():
    # Precios actuales, movers, volatilidad

@st.cache_data(ttl=3600)   # 1 hora - datos históricos  
def load_historical_data():
    # Datos históricos, correlaciones
```

### 🧵 Concurrencia y Rendimiento
```python
# Consultas paralelas para múltiples acciones
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(get_single_price, symbol): symbol 
               for symbol in symbols}
    
    for future in as_completed(futures):
        result = future.result()
        # Procesar resultado
```

## 🔧 Patrones de Desarrollo

### 🏗️ Estructura de Clases
- **Singleton Pattern**: ConfigManager para configuración global
- **Factory Pattern**: Creación de gráficos según tipo de datos
- **Observer Pattern**: Cache invalidation en Streamlit
- **Strategy Pattern**: Diferentes estrategias de carga de datos

### 📝 Convenciones de Código
- **🐍 PEP 8**: Estilo Python estándar
- **📚 Docstrings**: Documentación completa de funciones
- **🏷️ Type Hints**: Tipos explícitos para mejor IDE support
- **🛡️ Error Handling**: Try/except con logging detallado
- **📊 Logging**: Niveles INFO/WARNING/ERROR apropiados

### 🧪 Testing Patterns
```python
# Ejemplo de test típico
def test_market_summary():
    extractor = YahooFinanceDataExtractor()
    summary = extractor.get_market_summary()
    
    assert 'total_stocks' in summary
    assert summary['total_stocks'] > 0
    assert 'market_trend' in summary
    assert summary['market_trend'] in ['Alcista', 'Bajista', 'Neutral']
```

## 🚀 Guía de Desarrollo

### 🔧 Agregar Nueva Funcionalidad

#### 1. Nuevo Indicador Técnico
```python
# En yahoo_finance.py, método _add_technical_indicators()
def _add_technical_indicators(self, df):
    # ... indicadores existentes ...
    
    # Nuevo indicador (ejemplo: Williams %R)
    high_14 = df['High'].rolling(window=14).max()
    low_14 = df['Low'].rolling(window=14).min()
    df['Williams_R'] = -100 * (high_14 - df['Close']) / (high_14 - low_14)
    
    return df
```

#### 2. Nueva Página en UI
```python
# En pages.py
def show_new_analysis():
    st.title("🔬 Nuevo Análisis")
    # Implementación de la página
    
# En PAGES dictionary
PAGES = {
    # ... páginas existentes ...
    "🔬 Nuevo Análisis": show_new_analysis
}
```

#### 3. Nueva Configuración  
```yaml
# En config.yaml
new_feature:
  enabled: true
  parameters:
    param1: value1
    param2: value2
```

### 📊 Debugging y Profiling
```python
# Logging para debugging
import logging
logger = logging.getLogger(__name__)

def debug_function():
    logger.info("Iniciando función")
    logger.debug(f"Variable state: {variable}")
    logger.warning("Condición inusual detectada")
```

### 🎯 Optimización de Performance
- **⚡ Caching**: Usar decoradores @st.cache_data apropiadamente  
- **🧵 Threading**: ThreadPoolExecutor para operaciones I/O
- **📊 Vectorización**: pandas/numpy para operaciones masivas
- **💾 Memoria**: Evitar copias innecesarias de DataFrames grandes

---

🏗️ **Arquitectura modular diseñada para escalabilidad y mantenibilidad**  
📊 **Código optimizado para análisis financiero en tiempo real**  
🎯 **Patrones de desarrollo que facilitan extensiones futuras**
