# 📈 News Summarizer - Dashboard Streamlit

## 🚀 Aplicación Interactiva del Mercado Chileno

Dashboard profesional para análisis en tiempo real de las principales acciones de la Bolsa de Santiago con indicadores técnicos avanzados, visualizaciones interactivas y sistema de navegación multi-página.

**🌐 Acceso Directo**: http://localhost:8501

## ✨ Características Principales

### 📊 Dashboard Principal
- **📈 Resumen del mercado** en tiempo real con métricas clave
- **🏆 Top performers** del día (ganadores y perdedores)
- **💰 Tabla de precios actuales** con cambios porcentuales y volúmenes
- **📊 Análisis técnico detallado** con gráficos de velas japonesas
- **🎯 Señales de trading** automáticas basadas en indicadores técnicos
- **🔗 Matriz de correlación** interactiva con heatmap
- **📊 Análisis de volatilidad** con rankings y clasificación de riesgo

### 🔬 Análisis Avanzado
- **📈 Comparación múltiple** de acciones seleccionadas
- **📊 Rendimiento normalizado** con gráficos base 100
- **🎯 Señales de trading múltiples** para análisis comparativo
- **📊 Gráficos interactivos** con zoom y navegación temporal

### 🏛️ Resumen del Mercado  
- **🏢 Rendimiento por sector** con análisis agregado
- **🌡️ Mapa de calor interactivo** por volumen y rendimiento
- **📊 Métricas del mercado** consolidadas
- **📈 Treemaps dinámicos** para visualización de datos

### ⚙️ Configuración
- **🎨 Personalización de dashboard**: temas, períodos, layout
- **📈 Configuración de indicadores** técnicos avanzada
- **🚨 Sistema de alertas** con umbrales configurables
- **ℹ️ Información del sistema** y métricas de rendimiento

## 📈 Indicadores Técnicos Implementados

### 📊 Medias Móviles
- **SMA 20**: Media móvil simple de 20 períodos (línea naranja)
- **SMA 50**: Media móvil simple de 50 períodos (línea roja)  
- **EMA 12**: Media móvil exponencial rápida de 12 períodos
- **EMA 26**: Media móvil exponencial lenta de 26 períodos

### 🎯 Osciladores y Momentum
- **MACD**: Convergencia/Divergencia de medias móviles
  - Línea MACD (azul)
  - Línea de señal (roja)
  - Histograma de diferencias
- **RSI**: Índice de Fuerza Relativa (14 períodos)
  - Niveles: Sobrecompra (70+), Sobreventa (30-)
  - Líneas de referencia automáticas

### 📈 Bandas y Volatilidad
- **Bollinger Bands**: Sistema de bandas de volatilidad
  - Banda superior (Media + 2 desviaciones)
  - Banda media (SMA 20 períodos)
  - Banda inferior (Media - 2 desviaciones)
- **Volatilidad Histórica**: Anualizada con ventana de 20 días
- **Retornos Diarios**: Calculados automáticamente

### 🎯 Sistema de Señales Automáticas

#### 🟢 Señales Bullish (Compra)
- **Moving Average Strong**: Precio > SMA20 > SMA50
- **Moving Average Moderate**: Precio > SMA20
- **RSI Oversold**: RSI < 30 (oportunidad de compra)
- **MACD Positive**: Línea MACD > Línea de señal
- **Bollinger Lower**: Precio < Banda inferior

#### 🔴 Señales Bearish (Venta)  
- **Moving Average Strong**: Precio < SMA20 < SMA50
- **RSI Overbought**: RSI > 70 (zona de sobrecompra)
- **MACD Negative**: Línea MACD < Línea de señal
- **Bollinger Upper**: Precio > Banda superior

### 📊 Análisis de Correlación
- **Matriz 6×6**: Principales 6 acciones del mercado
- **Escala de colores**:
  - 🟦 **Azul intenso**: Correlación positiva fuerte (0.7 - 1.0)
  - 🟦 **Azul claro**: Correlación positiva moderada (0.3 - 0.7)
  - ⚪ **Blanco**: Sin correlación significativa (-0.3 - 0.3)
  - 🟥 **Rojo claro**: Correlación negativa moderada (-0.7 - -0.3)
  - 🟥 **Rojo intenso**: Correlación negativa fuerte (-1.0 - -0.7)

### 📊 Clasificación de Volatilidad
- 🔴 **Alta Volatilidad**: > 30% anualizada (alto riesgo/oportunidad)
- 🟡 **Volatilidad Media**: 15% - 30% anualizada (riesgo moderado)  
- 🟢 **Baja Volatilidad**: < 15% anualizada (menor riesgo)

## 🏢 Acciones Monitoreadas (Estado Actual)

| # | Empresa | Símbolo | Sector | Estado | Última Actualización |
|---|---------|---------|--------|--------|---------------------|
| 1 | **SQM** | SQM-B.SN | Basic Materials | ✅ Activo | Tiempo real |
| 2 | **Falabella** | FALABELLA.SN | Consumer Cyclical | ✅ Activo | Tiempo real |
| 3 | **Cencosud** | CENCOSUD.SN | Consumer Staples | ✅ Activo | Tiempo real |
| 4 | **Copec** | COPEC.SN | Energy | ✅ Activo | Tiempo real |
| 5 | **CCU** | CCU.SN | Consumer Staples | ✅ Activo | Tiempo real |
| 6 | **Banco de Chile** | CHILE.SN | Financial Services | ✅ Activo | Tiempo real |
| 7 | **Enel Chile** | ENELCHILE.SN | Utilities | ✅ Activo | Tiempo real |
| 8 | **Colbún** | COLBUN.SN | Utilities | ✅ Activo | Tiempo real |
| 9 | **Aguas Andinas** | AGUAS-A.SN | Utilities | ✅ Activo | Tiempo real |
| ~~10~~ | ~~**Santander**~~ | ~~SANTANDER.SN~~ | ~~Financial~~ | ❌ Delistado | N/A |

**📊 Cobertura Actual**: 9/10 acciones operativas (**90% disponibilidad**)

### 🎯 Métricas por Acción
Cada acción incluye:
- **Precio actual** con cambio porcentual del día
- **Volumen** de transacciones
- **Market Cap** y datos fundamentales
- **248+ registros históricos** (1 año de datos)
- **15+ indicadores técnicos** calculados
- **Señales de trading** automáticas actualizadas

## 🎯 Funcionalidades Interactivas Detalladas

### � Navegación y Controles

#### 🧭 Navegación Multi-Página
```
📊 Dashboard Principal  ← Página por defecto
├── 🔬 Análisis Avanzado
├── 🏛️ Resumen del Mercado  
└── ⚙️ Configuración
```

#### ⚙️ Controles del Sidebar
- **📅 Período de análisis**: 1d, 1w, 1m, 3m, 6m, 1y
- **📈 Selección de acciones**: Para análisis individual detallado
- **🔄 Actualización manual**: Botón para forzar refresh de datos
- **ℹ️ Estado del sistema**: Última actualización y timestamp

#### 📊 Gráficos Interactivos
- **🔍 Zoom y Pan**: Click y drag para explorar datos
- **📍 Hover tooltips**: Información detallada al pasar el mouse
- **🎛️ Controles de plotly**: Zoom, reset, download PNG
- **📏 Crossfilter**: Selección de rangos temporales
- **🖱️ Leyenda interactiva**: Click para ocultar/mostrar series

### 🎨 Sistema de Colores y UI

#### 🎨 Paleta de Colores
- **🟢 Verde (#00C851)**: Alzas, señales positivas, baja volatilidad
- **🔴 Rojo (#ff4444)**: Bajas, señales negativas, alta volatilidad  
- **🔵 Azul (#1f77b4)**: Elementos principales, correlaciones positivas
- **🟡 Amarillo**: Volatilidad media, advertencias
- **⚪ Gris (#666)**: Elementos neutrales, sin correlación

#### 📐 Layout Responsive  
- **🖥️ Desktop**: Layout amplio con 4 columnas para métricas
- **📱 Mobile**: Layout adaptativo con navegación colapsible
- **📊 Gráficos**: Se ajustan automáticamente al ancho del contenedor
- **📋 Tablas**: Scroll horizontal en pantallas pequeñas

### ⚡ Sistema de Cache y Rendimiento

#### 🚀 Cache Inteligente
```python
@st.cache_data(ttl=300)   # Datos de mercado: 5 minutos
@st.cache_data(ttl=3600)  # Datos históricos: 1 hora
```

#### 📊 Optimizaciones
- **🔄 Carga paralela**: ThreadPoolExecutor para múltiples acciones
- **📦 Cache por niveles**: Diferentes TTL según tipo de dato
- **⚡ Lazy loading**: Carga solo cuando se necesita
- **🎯 Memoización**: Funciones pesadas con decorador cache

## 🚀 Guía de Ejecución Paso a Paso

### 📋 Prerequisitos
- Python 3.10+ instalado
- Conexión estable a internet
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

### � Método 1: Ejecución Automática (Recomendado)
```bash
# Desde el directorio raíz del proyecto
./run_app.sh
```
**✅ Ventajas**: Script optimizado con configuración automática

### 💻 Método 2: Comando Streamlit Directo
```bash
streamlit run src/ui/streamlit_app.py \
    --server.port 8501 \
    --server.headless false \
    --theme.base "light"
```

### 🐍 Método 3: Con Python
```bash
python3 -m streamlit run src/ui/streamlit_app.py --server.port 8501
```

### 🌐 Acceso a la Aplicación
Después de ejecutar cualquier método:
```
🚀 Iniciando News Summarizer - Mercado Chileno...
📊 Dashboard interactivo disponible en: http://localhost:8501

  Local URL: http://localhost:8501      ← Clic aquí
  Network URL: http://192.168.1.139:8501
```

### 🔍 Verificación del Sistema
```bash
# Verificar que todo esté funcionando antes de ejecutar
python3 check_system.py
```

## 📊 Métricas de Rendimiento de la UI

### ⚡ Tiempos de Carga
- **🚀 Inicio de aplicación**: 3-5 segundos
- **📊 Dashboard inicial**: < 5 segundos  
- **📈 Gráficos técnicos**: 1-3 segundos
- **🔄 Actualización de datos**: 5-10 segundos
- **🔗 Cambio de página**: < 1 segundo

### 💾 Uso de Memoria
- **📊 Aplicación base**: ~50-80 MB
- **📈 Con todos los gráficos**: ~150-200 MB
- **🔄 Cache de datos**: ~20-30 MB adicionales
- **📱 Total recomendado**: 4GB RAM disponible

### 🌐 Compatibilidad de Navegadores
| Navegador | Versión Mínima | Estado | Notas |
|-----------|----------------|--------|--------|
| Chrome | 80+ | ✅ Óptimo | Recomendado |
| Firefox | 75+ | ✅ Óptimo | Compatible completo |
| Safari | 13+ | ✅ Bueno | Puede tener lag en gráficos |
| Edge | 80+ | ✅ Óptimo | Basado en Chromium |
| Opera | 70+ | ⚠️ Básico | Funcional, no optimizado |

## 🎯 Funcionalidades Interactivas

### 📊 Gráficos
- **Gráficos de velas** con zoom y pan
- **Indicadores técnicos** superpuestos
- **Gráficos de volumen**
- **Heatmaps de correlación**
- **Treemaps** de rendimiento

### 🔧 Controles
- **Selector de período**: 1d, 1w, 1m, 3m, 6m, 1y
- **Selector de acciones** múltiple
- **Filtros de volatilidad**
- **Configuración de indicadores**

### 📱 Responsivo
- **Layout adaptativo** para diferentes pantallas
- **Sidebar colapsible**
- **Métricas en cards** responsivas

## 🔄 Actualización de Datos

### Automática
- **Cache inteligente**: 5 minutos para datos de mercado
- **Cache extendido**: 1 hora para datos históricos
- **Actualización en tiempo real** durante horarios de mercado

### Manual
- Botón **"🔄 Actualizar Datos"** en sidebar
- **Ctrl+F5** para forzar recarga completa

## 🎨 Personalización

### Temas Disponibles
- ☀️ **Light Theme** (por defecto)
- 🌙 **Dark Theme**
- 🔧 **Auto Theme**

### Colores
- 🟢 **Verde**: Alzas y señales positivas
- 🔴 **Rojo**: Bajas y señales negativas  
- 🔵 **Azul**: Elementos neutrales
- 🟡 **Amarillo**: Advertencias

## 📊 Métricas de Rendimiento

### Datos Procesados
- **9 acciones** principales
- **248 registros** históricos por acción (1 año)
- **15+ indicadores** técnicos por acción
- **Matriz 6x6** de correlaciones

### Tiempo de Carga
- **Dashboard inicial**: < 5 segundos
- **Gráficos interactivos**: < 2 segundos
- **Actualización de datos**: < 10 segundos

## 🛡️ Manejo de Errores

- **Reconexión automática** en caso de fallos de red
- **Mensajes informativos** para datos faltantes
- **Fallbacks** para acciones sin datos
- **Logs detallados** para debugging

## 🔮 Funcionalidades Avanzadas

### Señales de Trading
```
🟢 Bullish - Moving Average: Strong
🔴 Bearish - MACD: Negative Crossover  
🟡 Neutral - RSI: Normal Range
```

### Análisis de Correlación
- **Correlación positiva fuerte**: > 0.7 (azul)
- **Correlación negativa fuerte**: < -0.7 (rojo)
- **Sin correlación**: -0.3 a 0.3 (blanco)

### Clasificación de Volatilidad
- 🔴 **Alta**: > 30% anual
- 🟡 **Media**: 15% - 30% anual  
- 🟢 **Baja**: < 15% anual

## �️ Manejo de Errores y Troubleshooting

### 🚨 Errores Conocidos y Soluciones

#### 1. 🔄 ModuleNotFoundError
```python
ModuleNotFoundError: No module named 'streamlit'
```
**🔧 Solución**:
```bash
pip install streamlit plotly yfinance pandas numpy pyyaml
```

#### 2. 📊 Error de Datos - SANTANDER.SN
```
ERROR: $SANTANDER.SN: possibly delisted; no price data found
```
**✅ Estado**: Normal - Se ignora automáticamente (9/10 acciones funcionales)

#### 3. 🌐 Error de Conexión
```
WARNING: No hay datos para [SYMBOL]
```
**🔧 Soluciones**:
- Verificar conexión a internet
- Reintentar en horario bursátil (9:30-16:00 CLT)
- Usar botón "🔄 Actualizar Datos"

#### 4. ⚠️ Advertencias de Streamlit
```
Please replace `use_container_width` with `width`
```
**ℹ️ Estado**: Cosmético - No afecta funcionalidad

#### 5. � Puerto en Uso
```
OSError: [Errno 48] Address already in use
```
**🔧 Solución**:
```bash
# Terminar procesos Streamlit existentes
pkill -f streamlit

# O usar puerto alternativo
streamlit run src/ui/streamlit_app.py --server.port 8502
```

### 🐛 Logs y Debugging

#### 📋 Niveles de Log
- **INFO**: Operaciones normales (carga de datos, generación de gráficos)
- **WARNING**: Problemas menores (acciones sin datos)
- **ERROR**: Errores que requieren atención

#### 🔍 Interpretación de Logs
```bash
INFO:data_sources.yahoo_finance:Datos obtenidos para 9 acciones
# ✅ Normal: 9 de 10 acciones funcionando

WARNING:data_sources.yahoo_finance:No hay datos para SANTANDER.SN  
# ⚠️ Esperado: Acción conocida como problemática

INFO:utils.config:Configuración cargada desde: /path/to/config.yaml
# ✅ Normal: Sistema configurado correctamente
```

## 🔮 Funcionalidades Avanzadas y Tips

### 🎯 Uso Óptimo del Dashboard

#### 📊 Para Análisis Técnico
1. **Seleccionar acción** de interés en sidebar
2. **Ajustar período** según estrategia (1m para swing, 6m para tendencias)
3. **Interpretar señales** de trading en conjunto
4. **Usar correlaciones** para diversificación

#### 📈 Para Análisis Fundamental  
1. Ir a **🏛️ Resumen del Mercado**
2. Analizar **rendimiento sectorial**
3. Comparar **métricas de volatilidad**
4. Usar **mapas de calor** para oportunidades

#### 🔬 Para Análisis Comparativo
1. Acceder a **🔬 Análisis Avanzado**
2. **Seleccionar múltiples acciones**
3. Comparar **rendimiento normalizado**
4. Analizar **señales simultáneas**

### 🎨 Personalización Avanzada

#### ⚙️ Configuración de Parámetros
- **SMA**: Ajustar períodos según estrategia (20/50 por defecto)
- **RSI**: Modificar niveles de sobrecompra/sobreventa (70/30)
- **Volatilidad**: Cambiar ventana de cálculo (20 días)

#### 🎛️ Controles de Visualización
- **Zoom**: Click y arrastrar en gráficos para enfoque temporal
- **Reset**: Doble click para volver a vista completa  
- **Download**: Botón camera para exportar gráficos como PNG
- **Fullscreen**: Expandir gráficos para análisis detallado

¡Disfruta explorando el mercado chileno con esta poderosa herramienta de análisis! 📈🇨🇱
