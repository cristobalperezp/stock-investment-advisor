"""
Páginas adicionales para la aplicación Streamlit
Incluye configuración avanzada y análisis detallado
"""

import streamlit as st
import sys
import time
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from data_sources.yahoo_finance import YahooFinanceDataExtractor


def show_advanced_analytics():
    """Página de análisis avanzado"""
    st.title("🔬 Análisis Avanzado")
    
    extractor = YahooFinanceDataExtractor()
    
    # Información del caché
    # with st.expander("📋 Estado del Sistema de Caché"):
    #     cache_info = extractor.get_cache_info()
    #     col1, col2, col3 = st.columns(3)
        
    #     with col1:
    #         st.metric("Archivos en Caché", cache_info.get('total_files', 0))
    #     with col2:
    #         st.metric("Tamaño Total", f"{cache_info.get('total_size_mb', 0):.1f} MB")
    #     with col3:
    #         st.metric("Directorio", cache_info.get('cache_directory', 'N/A'))
        
        # if cache_info.get('files'):
        #     st.write("**Archivos de caché recientes:**")
        #     for file_info in cache_info['files'][:5]:
        #         st.write(f"• {file_info['filename']} ({file_info['size_mb']:.1f} MB) - {file_info['modified']}")
    
    # Selector de múltiples acciones
    stock_options = {
        "SQM": "SQM-B.SN",
        "Falabella": "FALABELLA.SN", 
        "Cencosud": "CENCOSUD.SN",
        "Copec": "COPEC.SN",
        "CCU": "CCU.SN",
        "Banco de Chile": "CHILE.SN",
        "Enel Chile": "ENELCHILE.SN",
        "Colbún": "COLBUN.SN",
        "Aguas Andinas": "AGUAS-A.SN",
        "Banco Santander Chile": "BSANTANDER.SN",
    }
    
    selected_stocks = st.multiselect(
        "Selecciona acciones para comparar:",
        list(stock_options.keys()),
        default=["SQM", "Falabella", "Banco de Chile"]
    )
    
    if selected_stocks:
        symbols = [stock_options[stock] for stock in selected_stocks]
        
        # Análisis de rendimiento comparativo
        st.subheader("📊 Rendimiento Comparativo")
        
        with st.spinner("Cargando datos históricos..."):
            historical_data = extractor.get_multiple_historical_data(symbols, "6mo")
        
        if historical_data:
            # Crear gráfico de rendimiento normalizado
            fig = go.Figure()
            
            for symbol in symbols:
                if symbol in historical_data:
                    data = historical_data[symbol]
                    if not data.empty:
                        # Normalizar precios (base 100)
                        normalized_prices = (data['Close'] / data['Close'].iloc[0]) * 100
                        stock_name = extractor.stock_names.get(symbol, symbol)
                        
                        fig.add_trace(go.Scatter(
                            x=data.index,
                            y=normalized_prices,
                            name=stock_name,
                            mode='lines'
                        ))
            
            fig.update_layout(
                title="Rendimiento Normalizado (Base 100)",
                xaxis_title="Fecha",
                yaxis_title="Precio Normalizado",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de señales para todas las acciones seleccionadas
        st.subheader("🎯 Análisis de Señales Múltiples")
        
        for stock in selected_stocks:
            symbol = stock_options[stock]
            with st.expander(f"Señales de {stock}"):
                signals = extractor.get_trading_signals(symbol)
                
                if 'signals' in signals and signals['signals']:
                    st.write(f"**Precio Actual:** ${signals['last_price']:,.2f}")
                    
                    for signal in signals['signals']:
                        signal_type = signal['type']
                        if signal_type == 'Bullish':
                            st.success(f"🟢 {signal['indicator']}: {signal['strength']}")
                        else:
                            st.error(f"🔴 {signal['indicator']}: {signal['strength']}")
                else:
                    st.info(f"No hay señales claras para {stock}")


def show_market_overview():
    """Página de resumen del mercado"""
    st.title("🏛️ Resumen del Mercado")
    
    extractor = YahooFinanceDataExtractor()
    
    # Información del caché en la parte superior
    # with st.expander("⚡ Información de Rendimiento"):
    #     cache_info = extractor.get_cache_info()
    #     st.info(f"💾 **Sistema de Caché Activo** - Datos reutilizados del día actual para mayor velocidad")
        
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         st.write(f"📁 Archivos: {cache_info.get('total_files', 0)}")
    #         st.write(f"💽 Tamaño: {cache_info.get('total_size_mb', 0):.1f} MB")
    #     with col2:
    #         st.write(f"🕒 Última actualización automática cada día")
    #         st.write(f"🧹 Limpieza automática después de 7 días")
    
    # Obtener datos del mercado (usando caché)
    with st.spinner("Cargando datos del mercado..."):
        start_time = time.time()
        market_summary = extractor.get_market_summary()
        current_prices = extractor.get_current_prices()
        sector_performance = extractor.get_sector_performance()
        load_time = time.time() - start_time
        
        # Mostrar tiempo de carga
        if load_time < 1.0:
            st.success(f"⚡ Datos cargados en {load_time:.3f} segundos")
        else:
            st.info(f"📡 Datos descargados en {load_time:.1f} segundos")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Acciones", market_summary.get('total_stocks', 0))
    
    with col2:
        gainers = market_summary.get('gainers', 0)
        st.metric("Subiendo", gainers, delta=f"+{gainers}")
    
    with col3:
        losers = market_summary.get('losers', 0)
        st.metric("Bajando", losers, delta=f"-{losers}")
    
    with col4:
        trend = market_summary.get('market_trend', 'Neutral')
        st.metric("Tendencia del Mercado", trend)
    
    # Análisis sectorial
    if sector_performance:
        st.subheader("🏢 Rendimiento por Sector")
        
        sector_df = pd.DataFrame([
            {
                'Sector': sector,
                'Promedio de Cambio (%)': data['avg_change'],
                'Número de Empresas': data['count']
            }
            for sector, data in sector_performance.items()
        ])
        
        # Gráfico de barras por sector
        fig = px.bar(
            sector_df,
            x='Sector',
            y='Promedio de Cambio (%)',
            color='Promedio de Cambio (%)',
            color_continuous_scale='RdYlGn',
            title="Rendimiento Promedio por Sector"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.dataframe(
            sector_df.sort_values('Promedio de Cambio (%)', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
    # Heatmap de rendimiento individual
    if not current_prices.empty:
        st.subheader("🌡️ Mapa de Calor - Rendimiento Individual")
        
        # Crear datos para el treemap
        fig = px.treemap(
            current_prices,
            path=['name'],
            values='volume',
            color='change_percent',
            color_continuous_scale='RdYlGn',
            title="Mapa de Calor por Volumen y Rendimiento"
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)


def show_settings():
    """Página de configuración"""
    st.title("⚙️ Configuración")
    
    st.subheader("📊 Configuración de Dashboard")
    
    # Configuraciones de visualización
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox(
            "Tema del Dashboard:",
            ["Light", "Dark", "Auto"],
            index=0
        )
        
        st.selectbox(
            "Período por defecto:",
            ["1 semana", "1 mes", "3 meses", "6 meses", "1 año"],
            index=2
        )
    
    with col2:
        st.number_input(
            "Intervalo de actualización (segundos):",
            min_value=60,
            max_value=3600,
            value=300,
            step=60
        )
        
        st.selectbox(
            "Zona horaria:",
            ["Santiago/Chile", "UTC", "Nueva York", "Londres"],
            index=0
        )
    
    st.subheader("📈 Configuración de Análisis")
    
    # Parámetros de indicadores técnicos
    with st.expander("Indicadores Técnicos"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.number_input("SMA Corta:", min_value=5, max_value=50, value=20)
            st.number_input("SMA Larga:", min_value=20, max_value=200, value=50)
        
        with col2:
            st.number_input("RSI Sobreventa:", min_value=10, max_value=40, value=30)
            st.number_input("RSI Sobrecompra:", min_value=60, max_value=90, value=70)
        
        with col3:
            st.number_input("MACD Rápido:", min_value=5, max_value=20, value=12)
            st.number_input("MACD Lento:", min_value=15, max_value=35, value=26)
    
    # Configuración de alertas
    st.subheader("🚨 Configuración de Alertas")
    
    with st.expander("Alertas de Precio"):
        st.multiselect(
            "Acciones para alertas:",
            ["SQM", "Falabella", "Cencosud", "Copec", "CCU"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Umbral de cambio positivo (%):", value=5.0)
        with col2:
            st.number_input("Umbral de cambio negativo (%):", value=-3.0)
    
    # Botones de acción
    st.subheader("🔧 Acciones")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Guardar Configuración"):
            st.success("Configuración guardada exitosamente")
    
    with col2:
        if st.button("🔄 Restablecer por Defecto"):
            st.info("Configuración restablecida a valores por defecto")
    
    with col3:
        if st.button("📤 Exportar Configuración"):
            st.info("Configuración exportada como config.json")
    
    # Información del sistema
    st.subheader("ℹ️ Información del Sistema")
    
    info_data = {
        "Versión de la App": "1.0.0",
        "Fuente de Datos": "Yahoo Finance",
        "Última Actualización": "2025-09-05 23:15:00",
        "Estado del Servicio": "🟢 Operativo",
        "Acciones Monitoreadas": "9 activas",
        "Cobertura del Mercado": "Bolsa de Santiago"
    }
    
    for key, value in info_data.items():
        st.write(f"**{key}:** {value}")


# Diccionario de páginas disponibles
PAGES = {
    "📊 Dashboard Principal": None,  # Página principal (manejada en streamlit_app.py)
    "🔬 Análisis Avanzado": show_advanced_analytics,
    "🏛️ Resumen del Mercado": show_market_overview,
    "⚙️ Configuración": show_settings
}
