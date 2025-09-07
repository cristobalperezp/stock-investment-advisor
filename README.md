# 📈 News Summarizer - Mercado Chileno

Dashboard interactivo
### Funcionalidades:
- **📈 Resumen del Mercado**: Ganadores/perdedores, tendencia general
- **💰 Precios en Tiempo Real**: Con cambios porcentuales coloreados
- **🎛️ Tickers Personalizados**: Agregar cualquier símbolo manualmente (AAPL, TSLA, etc.)
- **📊 Gráficos Interactivos**: Candlestick con indicadores técnicos
- **🎯 Señales Automáticas**: Recomendaciones basadas en RSI y medias móviles
- **🔗 Matriz de Correlación**: Heatmap para análisis de diversificación
- **📊 Ranking de Volatilidad**: Visualización interactiva por nivel de riesgolisis en tiempo real del mercado bursátil chileno con indicadores técnicos avanzados y visualizaciones profesionales.

## ✨ Características Destacadas

- 📊 **Dashboard en Tiempo Real** - Monitoreo de 9 acciones principales
- 📈 **15+ Indicadores Técnicos** - SMA, MACD, RSI, Bollinger Bands
- �� **Señales de Trading Automáticas** - Bullish/Bearish basadas en análisis técnico
- 🔗 **Análisis de Correlación** - Matrices interactivas entre acciones  
- 📊 **Visualizaciones Interactivas** - Plotly con gráficos de velas y heatmaps
- ⚡ **Cache Inteligente** - Optimizado para rendimiento
- 🎨 **Interfaz Multi-página** - Navegación profesional

## 🚀 Inicio Rápido

### 1. Instalación
```bash
# Instalar dependencias
pip install -r requirements.txt

# O instalar manualmente las principales:
pip install yfinance pandas numpy pyyaml streamlit plotly

# Verificar sistema
cd tests/
python3 check_system.py
```

### 2. Ejecutar
```bash
./run_app.sh  # Método automático
# O manual: streamlit run src/ui/streamlit_app.py
```

### 3. Acceso
Abrir: **http://localhost:8501**

### 4. Uso Avanzado - Tickers Personalizados
1. En el dashboard, busca la sección **"🎛️ Agregar Tickers Personalizados"** en la barra lateral
2. Selecciona el mercado (Chile .SN, US, Otro)
3. Ingresa el símbolo (ej: AAPL, TSLA, MSFT)
4. Haz clic en "Agregar Ticker"
5. El símbolo se integrará automáticamente en todos los análisis

## 🏢 Acciones Monitoreadas

| Empresa | Símbolo | Sector | Estado |
|---------|---------|--------|---------|
| SQM | SQM-B.SN | Materials | ✅ |
| Falabella | FALABELLA.SN | Retail | ✅ |
| Cencosud | CENCOSUD.SN | Retail | ✅ |
| Copec | COPEC.SN | Energy | ✅ |
| CCU | CCU.SN | Beverages | ✅ |
| Banco de Chile | CHILE.SN | Banking | ✅ |
| Enel Chile | ENELCHILE.SN | Utilities | ✅ |
| Colbún | COLBUN.SN | Utilities | ✅ |
| Aguas Andinas | AGUAS-A.SN | Utilities | ✅ |
| Banco Santander | BSANTANDER.SN | Banking | ✅ |

## 📊 Dashboard Principal

### Páginas Disponibles:
- **🏠 Principal**: Dashboard completo con precios y análisis
- **🔬 Análisis Avanzado**: Comparación entre múltiples acciones
- **📈 Resumen de Mercado**: Vista general y mapas de calor
- **⚙️ Configuración**: Personalización de indicadores

### Funcionalidades:
- **📈 Resumen del Mercado**: Ganadores/perdedores, tendencia general
- **💰 Precios en Tiempo Real**: Con cambios porcentuales coloreados
- **📊 Gráficos Interactivos**: Candlestick con indicadores técnicos
- **�� Señales Automáticas**: Recomendaciones basadas en RSI y medias móviles
- **🔗 Matriz de Correlación**: Heatmap para análisis de diversificación
- **📊 Ranking de Volatilidad**: Treemap interactivo por riesgo

## 📈 Indicadores Técnicos Implementados

### Medias Móviles
- **SMA 20/50**: Simples para tendencias
- **EMA 12/26**: Exponenciales para señales MACD

### Osciladores  
- **MACD**: Línea, señal e histograma
- **RSI 14**: Con niveles 30/70 para sobrecompra/sobreventa

### Bandas y Volatilidad
- **Bollinger Bands**: 20 períodos, 2 desviaciones
- **Volatilidad**: Anualizada histórica

### Señales de Trading
- 🟢 **Bullish**: SMA 20 > SMA 50 y RSI < 70
- 🔴 **Bearish**: SMA 20 < SMA 50 y RSI > 30
- 🟡 **Neutral**: Condiciones intermedias

## 📁 Estructura del Proyecto

```
News Summarizer/
├── src/                                 # Código fuente principal
│   ├── data_sources/yahoo_finance.py   # Extractor de datos de Yahoo Finance
│   ├── ui/streamlit_app.py             # Dashboard principal Streamlit  
│   ├── ui/pages.py                     # Páginas adicionales del dashboard
│   └── utils/config.py                 # Utilidades de configuración
├── tests/                              # Scripts de prueba y verificación
│   ├── check_system.py                 # Verificador del sistema
│   ├── test_volatility.py              # Pruebas de volatilidad
│   └── test_chart.py                   # Pruebas de gráficos
├── config/config.yaml                  # Configuración principal YAML
├── data/processed/                     # Datos procesados (12 CSV)
├── run_app.sh                          # Script de ejecución
└── README.md                           # Este archivo
```

## 📊 Datos Generados

### En Tiempo Real:
- Precios actuales con cambios porcentuales
- Volúmenes de transacciones  
- Tendencia general del mercado

### Históricos:
- **1 año** de historia (248+ registros por acción)
- **OHLCV** completo más 15 indicadores técnicos
- **Correlaciones** y análisis de volatilidad

### Archivos CSV:
- `current_prices_[timestamp].csv`
- `historical_[SYMBOL]_[timestamp].csv` (9 archivos)
- `correlation_matrix_[timestamp].csv`
- `volatility_ranking_[timestamp].csv`

## ⚡ Rendimiento

- **Dashboard inicial**: < 5 segundos
- **Gráficos**: < 2 segundos  
- **Actualización completa**: < 10 segundos
- **Cache**: 5 min (tiempo real), 1 hora (históricos)

## 🛠️ Stack Tecnológico

- **🎨 Frontend**: Streamlit (Dashboard interactivo)
- **📊 Visualizaciones**: Plotly (Gráficos profesionales)
- **🔧 Backend**: Python modular con arquitectura limpia
- **📈 API de Datos**: Yahoo Finance (yfinance)
- **🧮 Análisis**: pandas + numpy para cálculos financieros
- **⚙️ Configuración**: YAML + variables de entorno
- **🗃️ Datos**: CSV para persistencia local

## 🔧 Troubleshooting

### Problemas Comunes:

**1. Error de instalación**
```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# O instalar individualmente
pip install yfinance pandas numpy pyyaml streamlit plotly
```

**2. Puerto ocupado**  
```bash
streamlit run src/ui/streamlit_app.py --server.port 8502
```

**3. Sin datos**
- Verificar conexión a internet
- Ejecutar en horario bursátil (9:30-16:00 CLT)
- Usar botón "Actualizar Datos" en la aplicación

**4. Verificar sistema**
```bash
cd tests/
python3 check_system.py
```

### Errores Conocidos:
- **Fines de semana**: Sin actualizaciones (mercado cerrado)

## 🎯 Roadmap y Mejoras

- [ ] **GPT:** análisis de indicadores con motor GPT para generar recomendaciones.
- [ ] **Dockerización** del proyecto
- [ ] **Deploy** en Streamlit Cloud

## Contribuciones

1. Fork el proyecto
2. Crear rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am 'Agrega funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`  
5. Pull Request

## 📞 Soporte

### Documentación:
- `tests/README.md` - Pruebas y verificaciones
- `src/ui/README.md` - Interface y componentes
- `data/README.md` - Estructura de datos
- `src/README.md` - Código fuente

## 📄 Licencia

**MIT License** - Uso libre comercial y personal

### Créditos:
- **Datos**: Yahoo Finance
- **Visualizaciones**: Plotly + Streamlit
- **Mercado**: Bolsa de Santiago

## 📧 Contacto

**Desarrollador**: Cristóbal Pérez P.  
**Email**: cristobal.perez.p99@gmail.com  
**LinkedIn**: [Cristóbal Pérez P.](https://www.linkedin.com/in/cristobal-perez-palma/)
