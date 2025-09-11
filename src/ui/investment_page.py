"""
Página de análisis de inversiones para News Summarizer
Incluye funcionalidades de análisis fundamentales y generación de portafolios
"""

import streamlit as st
import sys
import pandas as pd
import traceback
from datetime import datetime
from pathlib import Path

# Agregar el directorio src al path para importar módulos
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from analysis.investment_analyzer import InvestmentAnalyzer
from analysis.report_generator import generate_investment_report
from data_sources.yahoo_finance import YahooFinanceDataExtractor
from config.stocks_config import (
    ALL_CHILEAN_STOCKS, 
    CHILEAN_STOCKS_BY_SECTOR, 
    STOCK_NAMES,
    get_stock_name,
    get_sector_for_stock,
    DEFAULT_ANALYSIS_CONFIG
)


def show_investment_analysis():
    """Muestra la página de análisis de inversiones"""
    
    # Header
    st.markdown("""
    <h1 style="text-align: center; color: #1f77b4;">
        💼 Análisis de Inversión Chileno
    </h1>
    <p style="text-align: center; color: #666; font-size: 1.2em;">
        Análisis fundamentales y recomendaciones de portafolio
    </p>
    """, unsafe_allow_html=True)
    
    # Sección de configuración
    st.header("⚙️ Configuración de Análisis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        budget = st.number_input(
            "💰 Presupuesto de Inversión (CLP)",
            min_value=100000,
            max_value=100000000,
            value=5000000,
            step=100000,
            format="%d"
        )
        
        risk_level = st.selectbox(
            "📊 Nivel de Riesgo",
            ["Conservador", "Moderado", "Agresivo"],
            index=1,
            help="Conservador: Menor riesgo, menores retornos. "
                 "Agresivo: Mayor riesgo, mayores retornos potenciales."
        )
    
    with col2:
        investment_horizon = st.selectbox(
            "📅 Horizonte de Inversión",
            ["Corto plazo (3-12 meses)", "Mediano plazo (1-3 años)",
             "Largo plazo (3+ años)"],
            index=1
        )
        
        dividend_preference = st.checkbox(
            "💵 Preferir empresas con dividendos",
            value=True,
            help="Priorizar empresas que pagan dividendos regulares"
        )
    
    with col3:
        # Nueva funcionalidad: TOP X acciones
        top_stocks_count = st.selectbox(
            "🎯 TOP Acciones para Invertir",
            options=[3, 4, 5, 6, 7, 8, 10],
            index=2,  # Por defecto TOP 5
            help="Analizar todas las acciones disponibles y seleccionar solo las TOP X para invertir el presupuesto total"
        )
        
        st.markdown("**🎯 Estrategia:** Concentrar inversión en las mejores acciones")
        st.info(f"Se analizarán todas las {len(ALL_CHILEAN_STOCKS)} acciones chilenas disponibles y se invertirá el presupuesto total en las TOP {top_stocks_count} con mejor puntuación.")
    
    # Mostrar información de caché
    # with st.expander("📁 Estado del Caché de Datos"):
    #     try:
    #         temp_analyzer = InvestmentAnalyzer()
    #         cache_info = temp_analyzer.get_cache_info()
            
    #         if cache_info["cache_available"]:
    #             st.success(f"✅ {cache_info['message']}")
    #             # st.write(f"📄 **Archivo:** {cache_info['filename']}")
    #             st.write(f"🕐 **Última actualización:** {cache_info['file_time']}")
    #             st.write(f"📊 **Tamaño:** {cache_info['file_size']}")
    #             st.write("Los datos se reutilizarán automáticamente para análisis del mismo día.")
    #         else:
    #             st.warning(f"⚠️ {cache_info['message']}")
    #             st.write("Se descargarán datos frescos desde Yahoo Finance.")
    #     except Exception as e:
    #         st.error(f"Error verificando caché: {e}")
    
    # Expandir para mostrar acciones disponibles
    with st.expander(f"📋 Ver todas las acciones disponibles ({len(ALL_CHILEAN_STOCKS)} total)"):
        st.markdown("### 🏢 Acciones Chilenas Normalizadas")
        
        # Mostrar por sectores
        for sector, stocks in CHILEAN_STOCKS_BY_SECTOR.items():
            st.markdown(f"**{sector}** ({len(stocks)} acciones):")
            sector_names = []
            for stock in stocks:
                name = get_stock_name(stock)
                sector_names.append(f"• {stock} - {name}")
            st.markdown("  \n".join(sector_names))
            st.markdown("")  # Espacio entre sectores
    
    # Botón de análisis
    if st.button("🚀 Ejecutar Análisis TOP Acciones", type="primary", key="run_analysis"):
        with st.spinner(f"🔍 Analizando las TOP {top_stocks_count} acciones del mercado chileno..."):
            try:
                # Mostrar información de caché antes del análisis
                analyzer = InvestmentAnalyzer()
                cache_info = analyzer.get_cache_info()
                
                if cache_info["cache_available"]:
                    # st.info(f"📁 {cache_info['message']} - Archivo: {cache_info['filename']}")
                    pass
                else:
                    st.info(f"🔄 {cache_info['message']}")
                
                # Ejecutar análisis con configuración TOP X
                result = analyzer.run_complete_analysis_with_gpt(
                    budget=budget,
                    risk_level=risk_level.lower(),
                    dividend_preference=dividend_preference,
                    top_stocks_count=top_stocks_count  # Nueva funcionalidad
                )
                
                # Guardar resultados en session state
                st.session_state['analysis_result'] = result
                st.session_state['analysis_config'] = {
                    'budget': budget,
                    'risk_level': risk_level,
                    'investment_horizon': investment_horizon,
                    'dividend_preference': dividend_preference,
                    'top_stocks_count': top_stocks_count
                }
                
                st.success(f"✅ Análisis completado! Se seleccionaron las TOP {top_stocks_count} acciones de {len(ALL_CHILEAN_STOCKS)} analizadas.")
                
                # Mostrar si se usó GPT o análisis automático
                if 'gpt_analysis' in result and result['gpt_analysis']:
                    st.info("🤖 Análisis realizado con IA (GPT)")
                else:
                    st.warning("⚠️ Análisis automático (GPT no disponible)")
                
            except Exception as e:
                st.error(f"❌ Error en el análisis: {str(e)}")
                st.error("Detalles del error para debugging:")
                st.code(str(e))
    
    # Mostrar resultados si existen
    if 'analysis_result' in st.session_state:
        result = st.session_state['analysis_result']
        config = st.session_state['analysis_config']
        
        # Separador visual
        st.markdown("---")
        
        # Información del análisis
        st.header("📊 Resultados del Análisis TOP Acciones")
        
        # Mostrar información sobre la selección TOP X
        if 'top_stocks_count' in result and 'total_stocks_analyzed' in result:
            st.success(f"🎯 Se analizaron **{result['total_stocks_analyzed']} acciones chilenas** y se seleccionaron las **TOP {result['top_stocks_count']}** con mejor puntuación para concentrar la inversión.")
            
            # Mostrar qué acciones fueron seleccionadas
            if 'portfolio_weights' in result:
                selected_stocks = result['portfolio_weights']['Empresa'].tolist()
                selected_tickers = result['portfolio_weights']['Ticker'].tolist()
                
                st.info(f"**TOP {result['top_stocks_count']} Acciones Seleccionadas:** " + 
                       ", ".join([f"{empresa} ({ticker})" for empresa, ticker in zip(selected_stocks, selected_tickers)]))
        
        info_col1, info_col2, info_col3, info_col4, info_col5 = st.columns(5)
        
        with info_col1:
            st.metric(
                "💰 Presupuesto",
                f"${config['budget']:,}"
            )
        
        with info_col2:
            st.metric(
                "📊 Perfil de Riesgo",
                config['risk_level']
            )
        
        with info_col3:
            total_analyzed = result.get('total_stocks_analyzed', result['market_summary']['total_empresas'])
            st.metric(
                "🔍 Acciones Analizadas",
                total_analyzed
            )
        
        with info_col4:
            top_count = result.get('top_stocks_count', 'N/A')
            st.metric(
                "🎯 TOP Seleccionadas",
                top_count
            )
        
        with info_col5:
            st.metric(
                "💎 Recomendaciones Finales",
                result['recommendations']['empresas_recomendadas']
            )
        
        # Tabs para organizar contenido
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Distribución TOP", "🤖 Análisis GPT", "📊 Análisis Detallado",
            "📋 Tabla de Datos", "📄 Reporte Completo"
        ])
        
        with tab1:
            show_portfolio_distribution(result)
        
        with tab2:
            show_gpt_analysis(result)
        
        with tab3:
            show_detailed_analysis(result)
        
        with tab4:
            show_data_tables(result)
        
        with tab5:
            show_complete_report(result, config)


def show_portfolio_distribution(result):
    """Muestra la distribución del portafolio"""
    st.subheader("🥧 Distribución del Portafolio")
    
    try:
        # Verificar datos necesarios
        if not result or 'fundamental_data' not in result:
            st.error("❌ No hay datos fundamentales para generar gráficos")
            return
        
        if 'recommendations' not in result:
            st.error("❌ No hay recomendaciones para mostrar distribución")
            return
        
        if 'market_summary' not in result:
            st.error("❌ No hay resumen de mercado disponible")
            return
        
        # Generar reporte con gráficos
        with st.spinner("Generando gráficos de distribución..."):
            report = generate_investment_report(
                result['fundamental_data'],
                result['recommendations'],
                result['market_summary']
            )
        
        # Mostrar gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                st.plotly_chart(
                    report['graficos']['distribucion_portafolio'],
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error en gráfico de portafolio: {str(e)}")
        
        with col2:
            try:
                st.plotly_chart(
                    report['graficos']['distribucion_sectores'],
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error en gráfico de sectores: {str(e)}")
        
        # Resumen de la distribución
        st.subheader("📋 Resumen de la Distribución")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_invertido = result['recommendations'].get('total_invertido', 0)
            empresas_recomendadas = result['recommendations'].get('empresas_recomendadas', 0)
            st.info(f"""
            **💰 Total a Invertir**
            ${total_invertido:,}
            
            **📈 Número de Empresas**
            {empresas_recomendadas}
            """)
        
        with col2:
            # Top 3 inversiones
            distribucion = result['recommendations'].get('distribucion', [])
            if len(distribucion) > 0:
                top_3 = distribucion[:3]
                top_text = "**🏆 Top 3 Inversiones**\n"
                for i, company in enumerate(top_3, 1):
                    empresa = company.get('Empresa', 'N/A')
                    monto = company.get('Monto_Inversion', 0)
                    top_text += f"{i}. {empresa}: ${monto:,}\n"
                
                st.success(top_text)
            else:
                st.warning("No hay datos de distribución disponibles")
        
        with col3:
            # Sectores principales
            sectores = result['recommendations'].get('resumen_sectores', {})
            if sectores:
                sector_text = "**🏢 Sectores Principales**\n"
                for sector, data in list(sectores.items())[:3]:
                    porcentaje = data.get('Porcentaje_Recomendado', 0)
                    sector_text += f"• {sector}: {porcentaje:.1f}%\n"
                
                st.warning(sector_text)
            else:
                st.warning("No hay datos de sectores disponibles")
    
    except Exception as e:
        st.error(f"❌ Error mostrando distribución del portafolio: {str(e)}")
        
        # Mostrar información básica como fallback
        st.warning("⚠️ Mostrando información básica disponible...")
        
        if 'recommendations' in result:
            recomendaciones = result['recommendations']
            
            st.markdown("### 📊 Información Básica Disponible")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total a Invertir", f"${recomendaciones.get('total_invertido', 0):,}")
                st.metric("Empresas Recomendadas", recomendaciones.get('empresas_recomendadas', 0))
            
            with col2:
                st.metric("Presupuesto Total", f"${recomendaciones.get('presupuesto_total', 0):,}")
            
            # Mostrar tabla básica de distribución si está disponible
            if 'distribucion' in recomendaciones:
                st.markdown("### 📋 Distribución Básica")
                
                df_basic = pd.DataFrame(recomendaciones['distribucion'])
                if not df_basic.empty:
                    # Mostrar solo columnas esenciales
                    display_cols = ['Empresa', 'Monto_Inversion', 'Porcentaje_Recomendado', 'Sector']
                    available_cols = [col for col in display_cols if col in df_basic.columns]
                    
                    if available_cols:
                        st.dataframe(df_basic[available_cols], use_container_width=True)
                    else:
                        st.dataframe(df_basic, use_container_width=True)
        else:
            st.error("No hay datos de recomendaciones disponibles")


def show_gpt_analysis(result):
    """Muestra los análisis específicos de GPT"""
    # Verificar si hay análisis GPT disponible
    if 'gpt_analysis' in result and result['gpt_analysis'] and not result['gpt_analysis'].startswith('### 📊 Informe Financiero (Análisis Automatizado)'):
        st.success("✅ Análisis realizado con inteligencia artificial")
        
        # Análisis del Business Analyst GPT
        st.markdown("#### 📊 Informe Financiero (IA)")
        
        # Mostrar el análisis GPT en un contenedor especial
        with st.container():
            analysis_text = result['gpt_analysis']
            if analysis_text:
                st.markdown(analysis_text)
            else:
                st.warning("⚠️ Análisis GPT vacío")
        
        # Separador
        st.markdown("---")
        
        # Distribución del Financial Advisor GPT
        if 'gpt_distribution' in result and result['gpt_distribution'] and not result['gpt_distribution'].startswith('### Distribución de Inversión (Automatizada)'):
            st.markdown("#### 💼 Distribución de Inversión (IA)")
            
            with st.container():
                distribution_text = result['gpt_distribution']
                if distribution_text:
                    st.markdown(distribution_text)
                else:
                    st.warning("⚠️ Distribución GPT vacía")
        
        # Comparación con análisis automático
        st.markdown("---")
        st.markdown("### 🔄 Comparación: IA vs Automático")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🤖 Recomendación IA:**")
            if 'gpt_distribution' in result and result['gpt_distribution'] and not result['gpt_distribution'].startswith('### Distribución de Inversión (Automatizada)'):
                # Extraer información básica de la distribución GPT
                gpt_text = result['gpt_distribution']
                if gpt_text and "TOTAL:" in gpt_text:
                    # Buscar líneas que contienen "TOTAL:" y extraer solo esas
                    lines = gpt_text.split('\n')
                    total_lines = [line.strip() for line in lines if 'TOTAL:' in line.upper()]
                    if total_lines:
                        st.info(total_lines[0])
                
                # Contar empresas mencionadas de forma más precisa
                if gpt_text:
                    # Contar líneas que empiezan con "- " y contienen "$"
                    investment_lines = [line for line in gpt_text.split('\n') if line.strip().startswith('- ') and '$' in line]
                    empresa_count = len(investment_lines)
                    st.metric("Empresas sugeridas (IA)", empresa_count)
                else:
                    st.metric("Empresas sugeridas (IA)", "N/A")
            else:
                st.warning("Análisis GPT no disponible - usando análisis automático")
                st.metric("Empresas sugeridas (IA)", "N/A")
        
        with col2:
            st.markdown("**⚙️ Recomendación Automática:**")
            auto_total = result['recommendations']['total_invertido']
            auto_companies = result['recommendations']['empresas_recomendadas']
            
            st.info(f"TOTAL: ${auto_total:,}")
            st.metric("Empresas sugeridas (Auto)", auto_companies)
        
        # Insight sobre las diferencias
        st.markdown("### 🔍 Insights y Diferencias")
        st.info("""
        **🤖 Análisis IA**: Considera factores cualitativos, contexto de mercado y 
        puede hacer recomendaciones más sofisticadas basadas en análisis narrativo.
        
        **⚙️ Análisis Automático**: Basado puramente en métricas cuantitativas 
        y algoritmos de optimización matemática.
        
        **💡 Recomendación**: Use el análisis IA como guía principal y el automático 
        como validación cuantitativa.
        """)
    
    else:
        # Sin análisis GPT disponible
        st.warning("⚠️ Análisis GPT no disponible")
        
        st.markdown("""
        ### 🔧 Para habilitar análisis con IA:
        
        1. **Obtenga una API Key de OpenAI:**
           - Visite [platform.openai.com](https://platform.openai.com/)
           - Cree una cuenta y genere una API key
        
        2. **Configure la variable de entorno:**
           ```bash
           export OPENAI_API_KEY="su_api_key_aqui"
           ```
        
        3. **Reinicie la aplicación**
        
        ### 🎯 Beneficios del análisis IA:
        - **Análisis cualitativo**: Interpretación contextual de los datos
        - **Recomendaciones personalizadas**: Considera preferencias específicas
        - **Explicaciones detalladas**: Justificaciones claras de las decisiones
        - **Adaptabilidad**: Se ajusta a diferentes perfiles de riesgo
        """)
        
        # Mostrar análisis automático como alternativa
        st.markdown("---")
        st.markdown("### ⚙️ Análisis Automático Disponible")
        
        # Mostrar algunos insights automáticos
        market_summary = result['market_summary']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "📊 Empresas Analizadas", 
                market_summary['total_empresas']
            )
        
        with col2:
            st.metric(
                "💎 Con Dividendos", 
                market_summary['empresas_con_dividendos']
            )
        
        with col3:
            st.metric(
                "📈 Var. Promedio 6M", 
                f"{market_summary['variacion_promedio_6m']:.1f}%"
            )
        
        # Top performers automático
        if 'top_performers_6m' in market_summary:
            st.markdown("**🏆 Top 3 Performers Automático (6M):**")
            for i, performer in enumerate(market_summary['top_performers_6m'][:3], 1):
                st.write(f"{i}. {performer['Empresa']}: {performer['Variacion_6M']*100:.1f}%")


def show_detailed_analysis(result):
    """Muestra análisis detallado con gráficos avanzados"""
    st.subheader("📊 Análisis Detallado")
    
    # Generar reporte
    report = generate_investment_report(
        result['fundamental_data'],
        result['recommendations'],
        result['market_summary']
    )
    
    # Métricas comparativas
    st.plotly_chart(
        report['graficos']['metricas_comparativas'],
        width="stretch"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance temporal
        st.plotly_chart(
            report['graficos']['performance_temporal'],
            width="stretch"
        )
    
    with col2:
        # Análisis riesgo-retorno
        st.plotly_chart(
            report['graficos']['riesgo_retorno'],
            width="stretch"
        )
    
    # Análisis de sectores
    st.subheader("🏢 Análisis por Sectores")
    
    sectors_df = pd.DataFrame([
        {
            'Sector': sector,
            'Monto_Inversion': data['Monto_Inversion'],
            'Porcentaje': data['Porcentaje_Recomendado'],
            'Empresas': len([c for c in result['recommendations']['distribucion'] 
                           if c['Sector'] == sector])
        }
        for sector, data in result['recommendations']['resumen_sectores'].items()
    ])
    
    st.dataframe(
        sectors_df,
        column_config={
            'Sector': 'Sector',
            'Monto_Inversion': st.column_config.NumberColumn(
                'Inversión (CLP)',
                format='$%d'
            ),
            'Porcentaje': st.column_config.NumberColumn(
                'Porcentaje (%)',
                format='%.1f%%'
            ),
            'Empresas': 'Número de Empresas'
        },
        hide_index=True,
        width="stretch"
    )


def show_data_tables(result):
    """Muestra tablas de datos detalladas"""
    st.subheader("📋 Datos Detallados")
    
    # Tabla de recomendaciones
    st.subheader("💎 Recomendaciones de Inversión")
    
    recommendations_df = pd.DataFrame(result['recommendations']['distribucion'])
    
    # Formatear columnas
    display_df = recommendations_df.copy()
    display_df['Monto_Inversion'] = display_df['Monto_Inversion'].apply(
        lambda x: f"${x:,.0f}"
    )
    display_df['Porcentaje_Recomendado'] = display_df['Porcentaje_Recomendado'].apply(
        lambda x: f"{x:.2f}%"
    )
    display_df['Puntaje'] = display_df['Puntaje'].apply(
        lambda x: f"{x:.4f}"
    )
    
    # Explicación del Score
    st.info("""
    **📊 ¿Qué significa el Score?**
    
    El **Score** es un puntaje normalizado (0.0 - 1.0) que evalúa cada empresa basándose en múltiples factores fundamentales:
    
    - **📈 ROE (Rentabilidad sobre Patrimonio)**: 15% del puntaje
    - **💰 P/E Ratio (Precio/Ganancias)**: 10% del puntaje  
    - **📊 Crecimiento de Ingresos**: 10% del puntaje
    - **💎 Dividend Yield**: 15% del puntaje
    - **🏦 Cash Flow vs Deuda**: 15% del puntaje
    - **📈 Variaciones de Precio (1M y 6M)**: 5% del puntaje
    - **⚖️ Otros factores de riesgo**: 30% del puntaje
    
    **🎯 Interpretación:**
    - Score > 0.7: Empresa excelente
    - Score 0.5-0.7: Empresa buena 
    - Score 0.3-0.5: Empresa regular
    - Score < 0.3: Empresa con riesgo alto
    """)
    
    st.dataframe(
        display_df,
        column_config={
            'Empresa': 'Empresa',
            'Ticker': 'Ticker',
            'Sector': 'Sector',
            'Monto_Inversion': 'Inversión',
            'Porcentaje_Recomendado': 'Porcentaje',
            'Puntaje': 'Score (0.0-1.0)'
        },
        hide_index=True,
        width="stretch"
    )
    
    # Tabla de datos fundamentales (empresas recomendadas)
    st.subheader("📊 Datos Fundamentales - Empresas Recomendadas")
    
    recommended_tickers = [item['Ticker'] for item in result['recommendations']['distribucion']]
    fundamental_subset = result['fundamental_data'][
        result['fundamental_data']['Ticker'].isin(recommended_tickers)
    ].copy()
    
    # Formatear datos fundamentales para mostrar
    display_cols = [
        'Empresa', 'Ticker', 'Precio_Actual', 'PE_Ratio', 
        'ROE', 'Dividend_Yield', 'Variacion_6M', 'Volatilidad'
    ]
    
    fundamental_display = fundamental_subset[display_cols].copy()
    
    # Aplicar formato
    for col in ['ROE', 'Dividend_Yield', 'Variacion_6M', 'Volatilidad']:
        if col in fundamental_display.columns:
            # Convertir a numérico antes de formatear
            fundamental_display[col] = pd.to_numeric(
                fundamental_display[col], errors='coerce'
            ).apply(
                lambda x: f"{x*100:.2f}%" if pd.notna(x) else "N/A"
            )
    
    # Formatear Precio_Actual
    fundamental_display['Precio_Actual'] = pd.to_numeric(
        fundamental_display['Precio_Actual'], errors='coerce'
    ).apply(
        lambda x: f"${x:.2f}" if pd.notna(x) else "N/A"
    )
    
    # Convertir PE_Ratio a numérico antes de formatear
    fundamental_display['PE_Ratio'] = pd.to_numeric(
        fundamental_display['PE_Ratio'], errors='coerce'
    ).apply(
        lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
    )
    
    st.dataframe(
        fundamental_display,
        column_config={
            'Empresa': 'Empresa',
            'Ticker': 'Ticker',
            'Precio_Actual': 'Precio Actual',
            'PE_Ratio': 'P/E Ratio',
            'ROE': 'ROE',
            'Dividend_Yield': 'Dividend Yield',
            'Variacion_6M': 'Variación 6M',
            'Volatilidad': 'Volatilidad'
        },
        hide_index=True,
        width="stretch"
    )


def show_complete_report(result, config):
    """Muestra reporte completo en formato texto"""
    
    try:
        # Verificar que tenemos los datos necesarios
        if not result or 'fundamental_data' not in result:
            st.error("❌ No hay datos fundamentales disponibles para generar el reporte")
            return
        
        if 'recommendations' not in result:
            st.error("❌ No hay recomendaciones disponibles para generar el reporte")
            return
        
        if 'market_summary' not in result:
            st.error("❌ No hay resumen de mercado disponible para generar el reporte")
            return
        
        # Mostrar información de debug
        with st.expander("🔧 Información de Debug"):
            st.write(f"Datos fundamentales: {len(result['fundamental_data'])} empresas")
            st.write(f"Recomendaciones: {result['recommendations'].get('empresas_recomendadas', 'N/A')} empresas")
            st.write(f"Total empresas en mercado: {result['market_summary'].get('total_empresas', 'N/A')}")
        
        # Intentar generar reporte
        with st.spinner("Generando reporte completo..."):
            report = generate_investment_report(
                result['fundamental_data'],
                result['recommendations'],
                result['market_summary']
            )
        
        st.success("✅ Reporte generado exitosamente")
        
        # Mostrar análisis textual con formato Markdown limpio
        st.markdown("#### 📊 Análisis Completo de Inversión")
        analysis_text = report['texto_analisis']
        if analysis_text:
            # Mostrar directamente sin alteraciones ya que el formato es correcto
            st.markdown(analysis_text)
        else:
            st.warning("⚠️ No hay análisis textual disponible")
        
        # Botón para descargar reporte
        report_data = {
            'fecha_analisis': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'configuracion': config,
            'recomendaciones': result['recommendations'],
            'resumen_mercado': result['market_summary']
        }
        
        # Convertir a texto para descarga
        report_text = f"""
        REPORTE DE ANÁLISIS DE INVERSIÓN
        =================================
        Fecha: {report_data['fecha_analisis']}
        Presupuesto: ${config['budget']:,}
        Perfil de Riesgo: {config['risk_level']}

        {report['texto_analisis']}

        CONFIGURACIÓN DETALLADA:
        - Horizonte de Inversión: {config['investment_horizon']}
        - Preferencia por Dividendos: {'Sí' if config['dividend_preference'] else 'No'}

        DATOS TÉCNICOS:
        - Total empresas analizadas: {result['market_summary']['total_empresas']}
        - Empresas recomendadas: {result['recommendations']['empresas_recomendadas']}
        - Total a invertir: ${result['recommendations']['total_invertido']:,}
        """
        
        st.download_button(
            label="📥 Descargar Reporte Completo",
            data=report_text,
            file_name=f"reporte_inversion_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"❌ Error generando el reporte completo: {str(e)}")
        
        # Mostrar información de debug adicional
        with st.expander("🐛 Debug - Información del error"):
            st.code(str(e))
            import traceback
            st.code(traceback.format_exc())
        
        # Intentar mostrar reporte básico como fallback
        st.warning("⚠️ Generando reporte básico como alternativa...")
        
        try:
            basic_report_text = f"""
            ## 📊 Reporte Básico de Análisis - {datetime.now().strftime('%d/%m/%Y')}

            ### 🎯 Resumen Ejecutivo
            - **Fecha del análisis**: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            - **Presupuesto**: ${config['budget']:,}
            - **Perfil de riesgo**: {config['risk_level']}
            - **Horizonte de inversión**: {config['investment_horizon']}
            - **Preferencia por dividendos**: {'Sí' if config['dividend_preference'] else 'No'}

            ### 📈 Resultados
            - **Empresas analizadas**: {result['market_summary'].get('total_empresas', 'N/A')}
            - **Empresas recomendadas**: {result['recommendations'].get('empresas_recomendadas', 'N/A')}
            - **Total a invertir**: ${result['recommendations'].get('total_invertido', 0):,}

            ### 💎 Top 5 Recomendaciones
            """
            
            # Agregar top 5 recomendaciones si están disponibles
            if 'distribucion' in result['recommendations']:
                for i, company in enumerate(result['recommendations']['distribucion'][:5], 1):
                    basic_report_text += f"""
                    **{i}. {company.get('Empresa', 'N/A')} ({company.get('Sector', 'N/A')})**
                    - Inversión: ${company.get('Monto_Inversion', 0):,}
                    - Porcentaje: {company.get('Porcentaje_Recomendado', 0):.1f}%
                    """
            
            basic_report_text += f"""
            ### ⚠️ Disclaimer
            - Este análisis se basa en datos históricos y no constituye asesoría financiera
            - Se recomienda consultar con un asesor financiero profesional
            - Los mercados pueden ser volátiles y los resultados pasados no garantizan rendimientos futuros
            
            ---
            *Reporte generado automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}*
            """
            
            st.markdown(basic_report_text)
            
            # Botón de descarga para reporte básico
            st.download_button(
                label="📥 Descargar Reporte Básico",
                data=basic_report_text,
                file_name=f"reporte_basico_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
            
        except Exception as fallback_error:
            st.error(f"❌ Error generando reporte básico: {str(fallback_error)}")
    
    # Información adicional (siempre mostrar)
    st.info("""
    **💡 Nota sobre el Análisis:**
    - Este análisis se basa en datos históricos y fundamentales
    - Las recomendaciones no constituyen asesoría financiera profesional
    - Se recomienda diversificar y consultar con un asesor financiero
    - Los mercados pueden ser volátiles y los resultados pasados no garantizan rendimientos futuros
    """)


# Función auxiliar para la página principal
def get_investment_analysis_summary():
    """Obtiene resumen rápido para mostrar en otras páginas"""
    if 'analysis_result' in st.session_state:
        result = st.session_state['analysis_result']
        return {
            'empresas_analizadas': result['market_summary']['total_empresas'],
            'recomendaciones': result['recommendations']['empresas_recomendadas'],
            'presupuesto': st.session_state['analysis_config']['budget']
        }
    return None


if __name__ == "__main__":
    # Para testing independiente
    show_investment_analysis()
