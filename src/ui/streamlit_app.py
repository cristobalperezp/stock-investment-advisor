"""
Aplicación principal de Streamlit para el Stock Investment Advisor
Dashboard interactivo para análisis del mercado chileno con tickers personalizados
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Agregar el directorio src al path para importar módulos
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from data_sources.yahoo_finance import YahooFinanceDataExtractor
from utils.config import get_config
from ui.pages import PAGES, show_advanced_analytics, show_market_overview, show_settings
from ui.investment_page import show_investment_analysis

# Configuración de la página
st.set_page_config(
    page_title="Stock Investment Advisor - Mercado Chileno",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .positive {
        color: #00C851;
        font-weight: bold;
    }
    .negative {
        color: #FF4444;
        font-weight: bold;
    }
    .custom-ticker {
        background-color: #e3f2fd;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_market_data(custom_tickers=None):
    """Carga datos del mercado con cache, incluyendo tickers personalizados"""
    extractor = YahooFinanceDataExtractor()
    
    # Combinar tickers predeterminados con personalizados
    if custom_tickers:
        default_symbols = extractor.default_stocks
        combined_symbols = list(set(default_symbols + custom_tickers))
        
        # Usar los símbolos combinados para obtener datos
        market_summary = extractor.get_market_summary()
        current_prices = extractor.get_current_prices(combined_symbols)
        movers = extractor.get_market_movers(limit=10)
        volatility = extractor.get_volatility_ranking(custom_symbols=combined_symbols)
    else:
        market_summary = extractor.get_market_summary()
        current_prices = extractor.get_current_prices()
        movers = extractor.get_market_movers(limit=5)
        volatility = extractor.get_volatility_ranking()
    
    return market_summary, current_prices, movers, volatility


def get_all_symbols(custom_tickers=None):
    """Obtiene todos los símbolos (predeterminados + personalizados)"""
    extractor = YahooFinanceDataExtractor()
    default_symbols = extractor.default_stocks
    
    if custom_tickers:
        return list(set(default_symbols + custom_tickers))
    return default_symbols


@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_historical_data(symbols, period="6mo"):
    """Carga datos históricos con cache"""
    extractor = YahooFinanceDataExtractor()
    return extractor.get_multiple_historical_data(symbols, period)


@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_correlation_matrix(custom_tickers=None):
    """Carga matriz de correlación con cache"""
    extractor = YahooFinanceDataExtractor()
    
    if custom_tickers:
        combined_symbols = get_all_symbols(custom_tickers)
        return extractor.get_correlation_matrix(combined_symbols)
    
    return extractor.get_correlation_matrix()


def validate_ticker(ticker):
    """Valida un ticker usando yfinance"""
    try:
        import yfinance as yf
        test_ticker = yf.Ticker(ticker)
        test_data = test_ticker.history(period="5d")
        return not test_data.empty
    except:
        return False


def create_price_chart(hist_data, symbol):
    """Crea gráfico de precio con indicadores técnicos"""
    if hist_data.empty:
        return None
        
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=('Precio y Medias Móviles', 'MACD', 'RSI'),
        vertical_spacing=0.05,
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}], 
               [{"secondary_y": False}]]
    )
    
    # Gráfico de precios y medias móviles
    fig.add_trace(
        go.Candlestick(
            x=hist_data.index,
            open=hist_data['Open'],
            high=hist_data['High'],
            low=hist_data['Low'],
            close=hist_data['Close'],
            name="Precio"
        ),
        row=1, col=1
    )
    
    if 'SMA_20' in hist_data.columns:
        fig.add_trace(
            go.Scatter(
                x=hist_data.index,
                y=hist_data['SMA_20'],
                name='SMA 20',
                line=dict(color='orange', width=2)
            ),
            row=1, col=1
        )
    
    if 'SMA_50' in hist_data.columns:
        fig.add_trace(
            go.Scatter(
                x=hist_data.index,
                y=hist_data['SMA_50'],
                name='SMA 50',
                line=dict(color='red', width=2)
            ),
            row=1, col=1
        )
    
    # MACD
    if 'MACD' in hist_data.columns:
        fig.add_trace(
            go.Scatter(
                x=hist_data.index,
                y=hist_data['MACD'],
                name='MACD',
                line=dict(color='blue')
            ),
            row=2, col=1
        )
        
        if 'MACD_Signal' in hist_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=hist_data.index,
                    y=hist_data['MACD_Signal'],
                    name='MACD Signal',
                    line=dict(color='red')
                ),
                row=2, col=1
            )
    
    # RSI
    if 'RSI' in hist_data.columns:
        fig.add_trace(
            go.Scatter(
                x=hist_data.index,
                y=hist_data['RSI'],
                name='RSI',
                line=dict(color='purple')
            ),
            row=3, col=1
        )
        
        # Líneas de RSI (30 y 70)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    
    fig.update_layout(
        title=f"Análisis Técnico - {symbol}",
        height=800,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    return fig


def create_correlation_heatmap(corr_matrix):
    """Crea heatmap de correlación"""
    if corr_matrix.empty:
        return None
    
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        aspect="auto",
        color_continuous_scale='RdBu_r',
        title="Matriz de Correlación - Acciones Monitoreadas"
    )
    
    fig.update_layout(
        title_font_size=16,
        height=600
    )
    
    return fig


def create_volatility_chart(volatility_data):
    """Crea gráfico de volatilidad"""
    if volatility_data.empty:
        return None
    
    try:
        # Crear gráfico de barras horizontal (más confiable que treemap)
        fig = px.bar(
            volatility_data.sort_values('current_volatility', ascending=True),
            x='current_volatility',
            y='name',
            color='current_volatility',
            color_continuous_scale='RdYlBu_r',
            orientation='h',
            title='📊 Ranking de Volatilidad por Acción',
            labels={
                'current_volatility': 'Volatilidad (%)',
                'name': 'Acción'
            }
        )
        
        fig.update_layout(
            height=500,
            font_size=11,
            title_font_size=16,
            margin=dict(l=150, r=50, t=60, b=50),
            showlegend=False
        )
        
        # Personalizar hover
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>" +
                         "Volatilidad: %{x:.1f}%<br>" +
                         "<extra></extra>"
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creando gráfico de volatilidad: {e}")
        return None


def display_trading_signals(symbol):
    """Muestra señales de trading para un símbolo específico"""
    st.subheader("🎯 Señales de Trading")
    
    try:
        extractor = YahooFinanceDataExtractor()
        signals = extractor.get_trading_signals(symbol)  # Pasar el símbolo directamente
        
        if 'error' not in signals:
            signal_list = signals.get('signals', [])
            
            if signal_list:
                for signal in signal_list:
                    signal_type = signal.get('type', 'Neutral')
                    indicator = signal.get('indicator', 'Desconocido')
                    strength = signal.get('strength', 'Moderada')
                    
                    if signal_type == 'Bullish':
                        st.success(f"🟢 **{signal_type}** - {indicator} (Fuerza: {strength})")
                    elif signal_type == 'Bearish':
                        st.error(f"🔴 **{signal_type}** - {indicator} (Fuerza: {strength})")
                    else:
                        st.info(f"🟡 **{signal_type}** - {indicator}")
            else:
                st.info("🟡 **Neutral** - Sin señales claras disponibles")
        else:
            st.warning(f"⚠️ {signals.get('error', 'Error desconocido')}")
    except Exception as e:
        st.error(f"Error al obtener señales: {str(e)}")


def main():
    """Función principal de la aplicación Streamlit"""
    
    # Inicializar session state para tickers personalizados
    if 'custom_tickers' not in st.session_state:
        st.session_state.custom_tickers = []
    
    # Header principal
    st.markdown(
        '<h1 class="main-header">📈 Stock Investment Advisor - Mercado Chileno</h1>',
        unsafe_allow_html=True
    )
    
    # Sidebar - Navegación entre páginas
    st.sidebar.header("🧭 Navegación")
    page_options = [
        "📊 Dashboard Principal",
        "💼 Análisis de Inversión",
        "📈 Análisis Avanzado",
        "🏛️ Resumen del Mercado",
        "⚙️ Configuración"
    ]
    
    selected_page = st.sidebar.selectbox(
        "Selecciona una página:",
        page_options
    )
    
    # Sección para agregar tickers personalizados
    st.sidebar.markdown("---")
    st.sidebar.header("📈 Tickers Personalizados")
    
    # Input para nuevo ticker
    with st.sidebar.expander("➕ Agregar Nuevo Ticker"):
        new_ticker = st.text_input(
            "Símbolo del ticker:",
            placeholder="Ej: AAPL, TSLA, MSFT",
            help="Ingrese el símbolo del ticker"
        )
        
        # Selector de mercado
        market_options = {
            "🇨🇱 Chile (.SN)": ".SN",
            "🇺🇸 Estados Unidos": "",
            "🌍 Otro": ""
        }
        
        selected_market = st.selectbox(
            "Mercado:",
            list(market_options.keys())
        )
        
        market_suffix = market_options[selected_market]
        
        # Botones para agregar/limpiar
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Agregar", key="add_ticker"):
                if new_ticker.strip():
                    formatted_ticker = new_ticker.upper().strip()
                    
                    if market_suffix and not formatted_ticker.endswith(market_suffix):
                        formatted_ticker += market_suffix
                    
                    if formatted_ticker not in st.session_state.custom_tickers:
                        if validate_ticker(formatted_ticker):
                            st.session_state.custom_tickers.append(formatted_ticker)
                            st.success(f"✅ {formatted_ticker} agregado")
                            st.rerun()
                        else:
                            st.error(f"❌ Ticker inválido: {formatted_ticker}")
                    else:
                        st.warning(f"⚠️ {formatted_ticker} ya existe")
                else:
                    st.warning("⚠️ Ingrese un símbolo válido")
        
        with col2:
            if st.button("🗑️ Limpiar Todo", key="clear_all"):
                st.session_state.custom_tickers = []
                st.success("✅ Lista limpiada")
                st.rerun()
    
    # Mostrar lista de tickers personalizados
    if st.session_state.custom_tickers:
        st.sidebar.subheader("🎯 Lista de Tickers:")
        for i, ticker in enumerate(st.session_state.custom_tickers):
            col_ticker, col_remove = st.sidebar.columns([3, 1])
            with col_ticker:
                st.markdown(f'<div class="custom-ticker">📊 {ticker}</div>', 
                           unsafe_allow_html=True)
            with col_remove:
                if st.button("❌", key=f"remove_{i}", help=f"Eliminar {ticker}"):
                    st.session_state.custom_tickers.remove(ticker)
                    st.success(f"✅ {ticker} eliminado")
                    st.rerun()
    
    # Mostrar página seleccionada
    if selected_page == "💼 Análisis de Inversión":
        show_investment_analysis()
        return
    elif selected_page == "📈 Análisis Avanzado":
        show_advanced_analytics()
        return
    elif selected_page == "🏛️ Resumen del Mercado":
        show_market_overview()
        return
    elif selected_page == "⚙️ Configuración":
        show_settings()
        return
    
    # Dashboard Principal (página por defecto)
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Configuración")
    
    # Selector de período
    period_options = {
        "1 semana": "5d",
        "1 mes": "1mo",
        "3 meses": "3mo",
        "6 meses": "6mo",
        "1 año": "1y"
    }
    selected_period = st.sidebar.selectbox(
        "Período de análisis:",
        list(period_options.keys()),
        index=2
    )
    period = period_options[selected_period]
    
    # Selector de acción para análisis detallado
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
    
    # Agregar tickers personalizados a las opciones
    if st.session_state.custom_tickers:
        for ticker in st.session_state.custom_tickers:
            display_name = f"📈 {ticker}"
            stock_options[display_name] = ticker
    
    selected_stock = st.sidebar.selectbox(
        "Acción para análisis detallado:",
        list(stock_options.keys()),
        index=0
    )
    stock_symbol = stock_options[selected_stock]
    
    # Botón de actualización
    if st.sidebar.button("🔄 Actualizar Datos", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Información de estado
    current_time = datetime.now().strftime('%H:%M:%S')
    st.sidebar.info(f"Última actualización: {current_time}")
    
    if st.session_state.custom_tickers:
        count = len(st.session_state.custom_tickers)
        st.sidebar.success(f"✅ {count} tickers personalizados activos")
    
    # Cargar datos (incluyendo tickers personalizados)
    with st.spinner("Cargando datos del mercado..."):
        market_summary, current_prices, movers, volatility = load_market_data(
            st.session_state.custom_tickers
        )
    
    # Sección 1: Resumen del Mercado
    st.header("📊 Resumen del Mercado")
    
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
        trend_emoji = ("🟢" if trend == "Alcista" 
                      else "🔴" if trend == "Bajista" else "🟡")
        st.metric("Tendencia", f"{trend_emoji} {trend}")
    
    # Sección 2: Top Performers
    st.header("🏆 Top Performers del Día")
    
    if movers and isinstance(movers, dict):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Mejores")
            gainers = movers.get('gainers', pd.DataFrame())
            if not gainers.empty:
                for _, row in gainers.iterrows():
                    st.write(f"**{row['name']}**: +{row['change_percent']:.2f}%")
            else:
                st.write("Sin datos disponibles")
        
        with col2:
            st.subheader("📉 Peores")
            losers = movers.get('losers', pd.DataFrame())
            if not losers.empty:
                for _, row in losers.iterrows():
                    st.write(f"**{row['name']}**: {row['change_percent']:.2f}%")
            else:
                st.write("Sin datos disponibles")
    
    # Sección 3: Tabla de Precios en Tiempo Real
    st.header("💰 Precios en Tiempo Real")
    
    if not current_prices.empty:
        # Separar datos si hay tickers personalizados
        if st.session_state.custom_tickers:
            custom_mask = current_prices['symbol'].isin(st.session_state.custom_tickers)
            custom_data = current_prices[custom_mask]
            default_data = current_prices[~custom_mask]
            
            if not custom_data.empty:
                st.subheader("📈 Tickers Personalizados")
                custom_df = custom_data[['name', 'current_price', 'change_percent', 'volume']].copy()
                custom_df['current_price'] = custom_df['current_price'].apply(lambda x: f"${x:,.2f}")
                custom_df['change_percent'] = custom_df['change_percent'].apply(lambda x: f"{x:.2f}%")
                custom_df['volume'] = custom_df['volume'].apply(lambda x: f"{x:,}")
                custom_df.columns = ['Empresa', 'Precio Actual', 'Cambio %', 'Volumen']
                st.dataframe(custom_df, width="stretch", hide_index=True)
                
                st.subheader("🏢 Acciones Principales Chilenas")
                display_df = default_data[['name', 'current_price', 'change_percent', 'volume']].copy()
            else:
                display_df = current_prices[['name', 'current_price', 'change_percent', 'volume']].copy()
        else:
            display_df = current_prices[['name', 'current_price', 'change_percent', 'volume']].copy()
        
        # Formatear la tabla principal
        display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:,.2f}")
        display_df['change_percent'] = display_df['change_percent'].apply(lambda x: f"{x:.2f}%")
        display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,}")
        display_df.columns = ['Empresa', 'Precio Actual', 'Cambio %', 'Volumen']
        
        st.dataframe(display_df, width="stretch", hide_index=True)
    
    # Sección 4: Análisis Técnico Detallado
    st.header(f"📈 Análisis Técnico - {selected_stock}")
    
    with st.spinner(f"Cargando datos históricos de {selected_stock}..."):
        historical_data = load_historical_data([stock_symbol], period)
    
    if stock_symbol in historical_data:
        hist_data = historical_data[stock_symbol]
        
        # Gráfico de precios
        price_chart = create_price_chart(hist_data, selected_stock)
        if price_chart:
            st.plotly_chart(price_chart, width="stretch")
        
        # Señales de trading
        display_trading_signals(stock_symbol)
    else:
        st.error(f"No se pudieron cargar datos para {selected_stock}")
    
    # Sección 5: Análisis de Correlación
    st.header("🔗 Análisis de Correlación")
    
    with st.spinner("Calculando matriz de correlación..."):
        correlation_matrix = load_correlation_matrix(st.session_state.custom_tickers)
    
    if not correlation_matrix.empty:
        corr_chart = create_correlation_heatmap(correlation_matrix)
        if corr_chart:
            st.plotly_chart(corr_chart, width="stretch")
        
        # Mostrar información adicional si hay tickers personalizados
        if st.session_state.custom_tickers:
            count = len(st.session_state.custom_tickers)
            st.info(f"📊 Matriz incluye {count} tickers personalizados")
        
        st.write("**Interpretación:**")
        st.write("- 🟦 **Azul**: Correlación positiva fuerte")
        st.write("- 🟥 **Rojo**: Correlación negativa fuerte")
        st.write("- ⚪ **Blanco**: Sin correlación significativa")
    
    # Sección 6: Análisis de Volatilidad
    st.header("📊 Análisis de Volatilidad")
    
    if not volatility.empty:
        # Mostrar tabla de datos primero (siempre funciona)
        st.subheader("📋 Datos de Volatilidad")
        volatility_display = volatility.copy()
        volatility_display['current_volatility'] = volatility_display['current_volatility'].apply(lambda x: f"{x:.1f}%")
        volatility_display['avg_volatility'] = volatility_display['avg_volatility'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(
            volatility_display[['name', 'current_volatility', 'avg_volatility', 'volatility_rank']],
            column_config={
                'name': 'Empresa',
                'current_volatility': 'Volatilidad Actual',
                'avg_volatility': 'Volatilidad Promedio',
                'volatility_rank': 'Clasificación'
            },
            width="stretch",
            hide_index=True
        )
        
        # Intentar mostrar gráfico
        st.subheader("📊 Gráfico de Volatilidad")
        vol_chart = create_volatility_chart(volatility)
        
        if vol_chart:
            st.plotly_chart(vol_chart, width="stretch")
        else:
            st.warning("⚠️ No se pudo generar el gráfico. Los datos están disponibles en la tabla superior.")
        
        st.write("**Interpretación de Volatilidad:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            high_vol = volatility[volatility['volatility_rank'] == 'High']
            st.error(f"🔴 **Alta Volatilidad** ({len(high_vol)} acciones)")
            if not high_vol.empty:
                for _, row in high_vol.iterrows():
                    st.write(f"• {row['name']}: {row['current_volatility']:.1f}%")
        
        with col2:
            medium_vol = volatility[volatility['volatility_rank'] == 'Medium']
            st.warning(f"🟡 **Volatilidad Media** ({len(medium_vol)} acciones)")
            if not medium_vol.empty:
                for _, row in medium_vol.iterrows():
                    st.write(f"• {row['name']}: {row['current_volatility']:.1f}%")
        
        with col3:
            low_vol = volatility[volatility['volatility_rank'] == 'Low']
            st.success(f"🟢 **Baja Volatilidad** ({len(low_vol)} acciones)")
            if not low_vol.empty:
                for _, row in low_vol.iterrows():
                    st.write(f"• {row['name']}: {row['current_volatility']:.1f}%")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "📊 **Stock Investment Advisor** - Análisis del Mercado Chileno | "
        "Datos proporcionados por Yahoo Finance"
    )


if __name__ == "__main__":
    main()
