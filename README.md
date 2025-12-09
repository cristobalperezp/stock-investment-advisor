# 📈 Stock Investment Advisor - Mercado Chileno

Dashboard interactivo para análisis integral del mercado bursátil chileno con análisis técnico, fundamental y reportes automáticos. Sistema completo con cache inteligente, visualizaciones profesionales y automatización via GitHub Actions.

Link al sitio: [Visitar la App](https://gpt-investment-advisor.streamlit.app/)

## 📋 Descripción del Proyecto

Este proyecto implementa un sistema completo de análisis bursátil chileno, incluyendo:

- **Dashboard Interactivo** con Streamlit multi-página
- **Análisis Técnico** con 15+ indicadores (MACD, RSI, Bollinger, SMA/EMA)
- **Análisis Fundamental** con 20+ ratios financieros
- **Sistema de Cache Inteligente** optimizado para horario bursátil
- **Reportes Automáticos** mensuales por email
- **50+ Acciones Chilenas** monitoreadas por sectores
- **Tickers Personalizados** para cualquier mercado
- **Automatización GitHub Actions** para análisis recurrentes

## 🛠️ Stack Tecnológico

- **🎨 Frontend**: Streamlit 1.49+ (Dashboard web interactivo)
- **📊 Visualizaciones**: Plotly (Gráficos financieros profesionales) 
- **🐍 Backend**: Python 3.12+ con arquitectura modular
- **📈 Datos Financieros**: Yahoo Finance API (yfinance 0.2.65+)
- **🧮 Análisis Numérico**: pandas 2.3+, numpy 1.26+, scikit-learn 1.5+
- **🤖 IA (Opcional)**: OpenAI GPT-3.5/4 para análisis de sentimiento
- **⚙️ Configuración**: YAML + variables de entorno
- **💾 Persistencia**: CSV optimizado con sistema de cache TTL
- **📧 Automatización**: SMTP + GitHub Actions para reportes
- **🔧 Testing**: pytest + scripts de verificación

## 📂 Estructura del Proyecto

```
News Summarizer/
├── .github/
│   └── workflows/
│       └── monthly_investment_analysis.yml   # GitHub Actions automatización
├── config/
│   └── config.yaml                           # Configuración principal
├── data/
│   ├── cache/                                # Cache diario (precios/históricos)
│   │   ├── current_prices_[tickers]_[date].csv
│   │   ├── historical_[period]_[tickers]_[date].csv
│   │   ├── market_summary_[date].json
│   │   └── sector_performance_[date].json
│   ├── processed/                            # Datos analizados
│   │   ├── correlation_matrix_[timestamp].csv
│   │   ├── fundamental_data_[timestamp].csv
│   │   └── volatility_ranking_[timestamp].csv
│   └── raw/                                  # Datos originales
├── docs/                                     # Documentación
├── outputs/
│   └── reports/                              # Reportes automáticos HTML
├── src/
│   ├── analysis/
│   │   ├── investment_analyzer.py            # Análisis fundamental completo
│   │   └── report_generator.py               # Generación de reportes
│   ├── automation/
│   │   └── monthly_report.py                 # Automatización mensual
│   ├── config/
│   │   └── stocks_config.py                  # Configuración 50+ acciones
│   ├── data_sources/
│   │   └── yahoo_finance.py                  # API Yahoo Finance + cache
│   ├── ui/
│   │   ├── streamlit_app.py                  # Dashboard principal
│   │   ├── pages.py                          # Análisis avanzado
│   │   └── investment_page.py                # Página análisis inversión
│   └── utils/
│       └── config.py                         # Utilidades configuración
├── tests/
│   ├── check_system.py                       # Verificador sistema
│   ├── test_cache_demo.py                    # Tests cache
│   ├── test_incremental_cache.py             # Tests cache incremental
│   └── test_*.py                             # Tests específicos
├── requirements.txt                          # Dependencias Python 3.12
├── environment.yml                           # Ambiente Conda
├── run_app.sh                                # Script ejecución automática
└── test_dependencies.py                     # Verificador dependencias
```

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
cd "stock-investment-advisor"
# O desde el repositorio completo:
# git clone https://github.com/usuario/stock-investment-advisor
# cd stock-investment-advisor
```

### 2. Crear ambiente virtual

**Opción A: Con Conda (Recomendado)**
```bash
conda env create -f environment.yml
conda activate stock-investment-advisor
```

**Opción B: Con pip**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Verificar instalación
```bash
python test_dependencies.py
# Debe mostrar: ✅ 19/19 dependencias principales funcionando
```

### 4. Configuración Opcional (Avanzada)
```bash
# Variables de entorno para funcionalidades completas
export OPENAI_API_KEY="tu-api-key"           # Análisis GPT
export NEWS_API_KEY="tu-news-api-key"        # Noticias (futuro)
export SMTP_SERVER="smtp.gmail.com"          # Reportes email
export SENDER_EMAIL="tu-email@gmail.com"
export SENDER_PASSWORD="tu-app-password"
export RECIPIENT_EMAIL="destino@email.com"
```

## 🏃‍♂️ Uso del Sistema

### 1. Ejecutar Dashboard Principal
```bash
# Método automático (recomendado)
./run_app.sh

# Método manual
streamlit run src/ui/streamlit_app.py
```

Acceder a: **http://localhost:8501**

### 1.1 Ejecutar análisis rápido desde la terminal
El script `scripts/run_analysis.sh` carga automáticamente el `.env`, ejecuta el análisis TOP acciones y muestra las recomendaciones en consola:

```bash
chmod +x scripts/run_analysis.sh  # una sola vez
./scripts/run_analysis.sh [presupuesto] [riesgo] [dividendos] [top]
```

Ejemplo:

```bash
./scripts/run_analysis.sh 5000000 agresivo true 5
```

Argumentos (opcionales):
- `presupuesto`: CLP totales a invertir (default `1000000`)
- `riesgo`: `conservador | moderado | agresivo` (default `moderado`)
- `dividendos`: `true | false` para priorizar pagos (default `true`)
- `top`: número de acciones finales (default `10`)

El script guarda/actualiza los CSV en `data/processed/` igual que la app y requiere conexión a internet para bajar datos frescos de Yahoo Finance.

### 2. Ejecutar Análisis Manual
```bash
# Análisis fundamental completo
python -c "from src.analysis.investment_analyzer import InvestmentAnalyzer; analyzer = InvestmentAnalyzer(); print('✅ Análisis disponible')"

# Generar reporte manual
python src/automation/monthly_report.py
```

### 3. Ver Cache del Sistema
```bash
ls -la data/cache/
# current_prices_*.csv - Precios actuales (TTL: 5min)
# historical_*.csv - Datos históricos (TTL: 1h)  
# market_summary_*.json - Resumen mercado
# sector_performance_*.json - Performance sectores
```

### 4. Verificar Sistema Completo
```bash
cd tests/
python check_system.py
```

## 🎯 Características de la Aplicación

### 📊 Dashboard Principal (`streamlit_app.py`)
- **Sidebar Interactivo**: Navegación entre páginas y configuraciones
- **Precios en Tiempo Real**: Tabla con variaciones porcentuales coloreadas
- **Gráficos Candlestick**: OHLCV con indicadores técnicos superpuestos
- **Métricas Financieras**: Market cap, P/E, dividend yield, ratios clave
- **Señales de Trading**: Bull/Bear/Neutral automáticas
- **Tickers Personalizados**: Agregar AAPL, TSLA, etc. dinámicamente
- **Selector de Período**: 1mo, 3mo, 6mo, 1y, 2y para análisis histórico

### 🔬 Análisis Avanzado (`pages.py`)
- **Comparación Multi-acción**: Rendimiento normalizado simultáneo
- **Correlaciones Interactivas**: Heatmaps entre acciones seleccionadas
- **Volatilidad por Sectores**: Rankings con métricas de riesgo
- **Análisis Técnico Masivo**: Señales para múltiples acciones
- **Filtros Dinámicos**: Por sector, capitalización, dividend yield

### 💡 Análisis de Inversión (`investment_page.py`)
- **Scoring Fundamental**: 0-10 basado en 20+ ratios financieros
- **Recomendaciones Automáticas**: COMPRA/MANTENER/VENDER/SIN_REC
- **Diversificación**: Análisis por sectores y correlaciones
- **Rankings Dinámicos**: Mejores oportunidades según criterios
- **Portfolio Builder**: Construcción de portafolios balanceados

### ⚙️ Configuración y Cache
- **Gestión de Cache**: Limpieza automática y manual
- **Parámetros Técnicos**: Configuración períodos indicadores
- **Estado del Sistema**: Monitoreo performance y estadísticas

## 📈 Análisis Implementados

### Análisis Técnico Completo
| Indicador | Períodos | Uso |
|-----------|----------|-----|
| **SMA** | 20, 50, 200 | Tendencias mediano/largo plazo |
| **EMA** | 12, 26 | Señales MACD responsivas |
| **MACD** | 12,26,9 | Momentum y cambios tendencia |
| **RSI** | 14 | Sobrecompra/sobreventa (30/70) |
| **Bollinger** | 20,2 | Volatilidad y niveles soporte/resistencia |
| **Volumen** | Variable | Confirmación señales y liquidez |

### Análisis Fundamental (`investment_analyzer.py`)
**Ratios de Valuación:**
- P/E (Price/Earnings), P/B (Price/Book), EV/EBITDA, PEG

**Ratios de Rentabilidad:**
- ROE (Return on Equity), ROA (Return on Assets), Margen Operativo

**Ratios de Liquidez:**
- Current Ratio, Quick Ratio, Cash Ratio

**Ratios de Endeudamiento:**
- Debt/Equity, Debt/Assets, Interest Coverage

**Métricas de Dividendos:**
- Dividend Yield, Payout Ratio, Crecimiento Dividendos

### Sistema de Scoring y Recomendaciones
- 🟢 **COMPRA** (8-10): Fundamentales sólidos + técnicos alcistas
- 🟡 **MANTENER** (6-7): Métricas balanceadas, sin señales claras
- 🔴 **VENDER** (0-5): Fundamentales débiles + técnicos bajistas  
- ⚪ **SIN RECOMENDACIÓN**: Datos insuficientes o contradictorios

## 🏢 Mercado Monitoreado

### Acciones Principales (Dashboard)
| Empresa | Símbolo | Sector | Market Cap |
|---------|---------|--------|------------|
| LATAM Airlines | LTM.SN | Transport | ~$15B CLP |
| SQM | SQM-B.SN | Materials | ~$12B CLP |
| Falabella | FALABELLA.SN | Retail | ~$8B CLP |
| Cencosud | CENCOSUD.SN | Retail | ~$6B CLP |
| Copec | COPEC.SN | Energy | ~$9B CLP |
| CCU | CCU.SN | Beverages | ~$4B CLP |
| Banco de Chile | CHILE.SN | Banking | ~$11B CLP |
| Banco Santander | BSANTANDER.SN | Banking | ~$8B CLP |
| Enel Chile | ENELCHILE.SN | Utilities | ~$5B CLP |
| AFP Habitat | HABITAT.SN | AFP | ~$1B CLP |

### Análisis Extendido por Sectores (20+ Acciones)
**Configuración en `src/config/stocks_config.py`:**
- 🏦 **Banca** (5): BSANTANDER.SN, BCI.SN, CHILE.SN, BICECORP.SN, ITAUCL.SN
- 🛒 **Retail** (6): FALABELLA.SN, RIPLEY.SN, CENCOSUD.SN, FORUS.SN, SMU.SN, TRICOT.SN  
- ⚡ **Utilities** (5): ENELCHILE.SN, COLBUN.SN, AGUAS-A.SN, GASCO.SN, ECL.SN
- 🍺 **Bebidas** (3): CCU.SN, CONCHATORO.SN, EMBONOR-B.SN
- 🏠 **Inmobiliario** (3): PARAUCO.SN, MALLPLAZA.SN, CENCOMALLS.SN
- 🚚 **Transporte** (1): LTM.SN
- 🏭 **Materiales** (2): CMPC.SN, SQM-B.SN
- 💰 **AFP** (3): HABITAT.SN, PROVIDA.SN, PLANVITAL.SN

## ⚡ Sistema de Cache Inteligente

### Cache por Tipo de Datos
```bash
# Precios actuales (actualización cada 5 min en horario bursátil)
data/cache/current_prices_[tickers]_20250908.csv

# Datos históricos (cache 1 hora para estabilidad)
data/cache/historical_[period]_[tickers]_20250908.csv

# Summaries del mercado (cache diario)
data/cache/market_summary_default_20250908.json
data/cache/sector_performance_default_20250908.json
```

### Optimización Automática
- **TTL Inteligente**: 5min (precios), 1h (históricos), 24h (fundamentales)
- **Cache Incremental**: Solo descarga acciones faltantes
- **Limpieza Automática**: Archivos > 7 días eliminados
- **Performance**: 90%+ cache hit durante horario bursátil chileno

### Estadísticas Reales
- **Tiempo de carga inicial**: 3-5 segundos (sin cache)
- **Tiempo con cache hit**: 0.5-1 segundo (96%+ mejora)
- **Horario optimizado**: 9:30-16:00 CLT (mercado chileno)

## 🚀 Automatización - GitHub Actions

### Workflow Mensual (`monthly_investment_analysis.yml`)
```yaml
name: 📊 Análisis Mensual de Inversión
on:
  schedule:
    - cron: '0 9 1 * *'  # 1er día mes, 9:00 AM UTC
  workflow_dispatch:     # Manual trigger
```

### Pipeline Automático
1. **Setup**: Python 3.12 + dependencias (`requirements.txt`)
2. **Análisis**: Ejecuta `src/automation/monthly_report.py`
3. **Procesamiento**: Análisis fundamental + técnico 50+ acciones  
4. **Reporte**: Genera HTML profesional con gráficos
5. **Email**: Envía reporte vía SMTP a lista distribución
6. **Storage**: Guarda en `outputs/reports/reporte_[fecha].html`

### Configuración Secrets GitHub
```bash
OPENAI_API_KEY="sk-..."              # GPT analysis (opcional)
SMTP_SERVER="smtp.gmail.com"        # Email server
SMTP_PORT="587"                      # Port
SENDER_EMAIL="origen@gmail.com"      # From email  
SENDER_PASSWORD="app_password"       # Gmail App Password
RECIPIENT_EMAIL="destino@email.com"  # To email
```

### Ejecución Manual Local
```bash
# Generar reporte mensual completo
python src/automation/monthly_report.py

# Ver reportes generados
open outputs/reports/
```

## 🔧 Testing y Verificación

### Suite de Tests Completa
```bash
# Verificar todas las dependencias (principal)
python test_dependencies.py

# Test sistema completo
cd tests/ && python check_system.py

# Tests específicos cache
python tests/test_cache_demo.py
python tests/test_incremental_cache.py

# Tests generación reportes  
python tests/test_report_generation.py
```

### Benchmarks de Performance
```bash
# Test cache system performance
python tests/test_full_cache_system.py
# Resultado esperado: 96.6%+ mejora con cache

# Test volatility analysis
python tests/test_volatility.py

# Test chart generation
python tests/test_chart.py
```

## 🚨 Troubleshooting

### Problema: Error instalación dependencias
**Solución**: Verificar Python 3.12+ y reinstalar:
```bash
python --version  # Debe ser 3.12+
pip install --upgrade --force-reinstall -r requirements.txt
python test_dependencies.py  # Verificar 19/19 ✅
```

### Problema: Dashboard no carga datos
**Solución**: Verificar conexión Yahoo Finance:
```bash
# Probar conexión API
python -c "import yfinance as yf; data=yf.download('SQM-B.SN', period='1d'); print('✅ API OK' if not data.empty else '❌ API Error')"

# Limpiar cache si necesario
rm -rf data/cache/* && ./run_app.sh
```

### Problema: Puerto 8501 ocupado
**Solución**: Usar puerto alternativo:
```bash
streamlit run src/ui/streamlit_app.py --server.port 8502
# O modificar run_app.sh
```

### Problema: Análisis fundamental lento
**Solución**: Rate limiting Yahoo Finance:
```bash
# El sistema ya incluye time.sleep(1) entre requests
# Para análisis masivo, usar cache o ejecutar fuera horario peak
```

### Problema: GitHub Actions falla
**Solución**: Verificar secrets y permisos:
```bash
# En GitHub repo > Settings > Secrets and Variables > Actions
# Verificar todas las variables SMTP_* están configuradas
```

## 📊 Métricas y KPIs

### Métricas Técnicas
- **RSI**: Sobrecompra >70, Sobreventa <30
- **MACD**: Señal compra (línea > señal), venta (línea < señal)  
- **Bollinger**: Precio cerca banda superior (sobrecompra), inferior (sobreventa)
- **Volumen**: Confirmación señales técnicas

### Métricas Fundamentales  
- **P/E**: < 15 (barato), 15-25 (justo), >25 (caro)
- **ROE**: >15% (excelente), 10-15% (bueno), <10% (débil)
- **Debt/Equity**: <0.3 (conservador), 0.3-0.6 (moderado), >0.6 (agresivo)
- **Dividend Yield**: >4% (alto), 2-4% (moderado), <2% (bajo)

## 🎯 Roadmap y Mejoras

- [ ] **Análisis de Noticias**: Integración NewsAPI + sentiment analysis
- [ ] **Machine Learning**: Modelos predictivos con scikit-learn
- [ ] **Docker Deploy**: Containerización completa

## 🤝 Contribuciones

### Configuración Desarrollo
```bash
# 1. Fork y clonar
git clone https://github.com/tu-usuario/stock-investment-advisor
cd stock-investment-advisor

# 2. Crear rama feature
git checkout -b feature/nueva-funcionalidad

# 3. Setup desarrollo
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install black flake8 pytest  # Dev tools

# 4. Ejecutar tests antes cambios
python test_dependencies.py
cd tests/ && python check_system.py

# 5. Hacer cambios y formatear
black src/
flake8 src/ --max-line-length=88

# 6. Test después cambios
python -m pytest tests/ -v

# 7. Commit y push
git commit -m 'Add: nueva funcionalidad XYZ'
git push origin feature/nueva-funcionalidad
```

### Guidelines Contribución
- **Código**: Seguir PEP 8, usar type hints, documentar funciones
- **UI**: Mantener consistencia Streamlit, componentes reutilizables
- **Performance**: Cache agresivo, lazy loading, optimización consultas
- **Tests**: Cobertura >80%, tests unitarios + integración
- **Documentación**: README actualizado, docstrings completos

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Ver `LICENSE` para más detalles.

## 📧 Contacto

**Desarrollador**: Cristóbal Pérez P.  
**Email**: cristobal.perez.p99@gmail.com  
**LinkedIn**: [Cristóbal Pérez P.](https://www.linkedin.com/in/cristobal-perez-palma/)


