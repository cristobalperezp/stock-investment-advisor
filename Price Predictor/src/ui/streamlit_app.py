"""
Aplicación Streamlit para predicción de precios de viviendas - California Housing
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import load_config


def load_model_and_scaler():
    """Carga el mejor modelo y el scaler"""
    try:
        # Buscar el mejor modelo basado en métricas guardadas
        model_paths = {
            'random_forest': 'models/random_forest_best_model.joblib',
            'lightgbm': 'models/lightgbm_best_model.joblib',
            'linear_regression': 'models/linear_regression_best_model.joblib'
        }
        
        # Por ahora, cargar el primero disponible
        # En producción, esto debería basarse en métricas
        model = None
        model_name = None
        
        for name, path in model_paths.items():
            try:
                model = joblib.load(path)
                model_name = name
                break
            except FileNotFoundError:
                continue
        
        if model is None:
            st.error("No se encontró ningún modelo entrenado")
            return None, None, None
            
        # Cargar scaler
        scaler = joblib.load('data/processed/scaler.joblib')
        
        return model, scaler, model_name
        
    except Exception as e:
        st.error(f"Error al cargar modelo: {e}")
        return None, None, None


def create_feature_inputs(config):
    """Crea inputs para las features del modelo"""
    
    st.header("Características de la Vivienda")
    
    # Crear dos columnas para organizar los inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Características Económicas")
        
        med_inc = st.slider(
            "💵 Ingresos Familiares Promedio",
            min_value=5000,
            max_value=150000,
            value=50000,
            step=1000,
            format="$%d",
            help="Ingreso mediano anual de las familias en la zona (en USD)"
        )
        
        house_age = st.slider(
            "🏘️ Antigüedad de las Viviendas",
            min_value=1,
            max_value=52,
            value=25,
            step=1,
            format="%d años",
            help="Edad promedio de las casas en la zona"
        )
        
        ave_rooms = st.slider(
            "🛏️ Habitaciones por Vivienda",
            min_value=2.0,
            max_value=20.0,
            value=6.0,
            step=0.1,
            format="%.1f habitaciones",
            help="Número promedio de habitaciones por casa"
        )
        
        ave_bedrms = st.slider(
            "🛌 Dormitorios por Vivienda",
            min_value=0.5,
            max_value=5.0,
            value=1.1,
            step=0.1,
            format="%.1f dormitorios",
            help="Número promedio de dormitorios por casa"
        )
    
    with col2:
        st.subheader("🏙️ Ubicación y Densidad")
        
        population = st.slider(
            "👥 Población de la Zona",
            min_value=100,
            max_value=35000,
            value=3000,
            step=100,
            format="%d habitantes",
            help="Número total de habitantes en el área"
        )
        
        ave_occup = st.slider(
            "🏠 Ocupantes por Vivienda",
            min_value=1.0,
            max_value=10.0,
            value=3.0,
            step=0.1,
            format="%.1f personas",
            help="Número promedio de personas que viven en cada casa"
        )
        
        latitude = st.slider(
            "📍 Ubicación Norte-Sur",
            min_value=32.5,
            max_value=41.95,
            value=34.2,
            step=0.01,
            format="%.2f°",
            help="Coordenada de ubicación (más alto = más al norte)"
        )
        
        longitude = st.slider(
            "📍 Ubicación Este-Oeste",
            min_value=-124.35,
            max_value=-114.31,
            value=-118.5,
            step=0.01,
            format="%.2f°",
            help="Coordenada de ubicación (menos negativo = más al este)"
        )
    
    # Crear DataFrame con los valores convertidos al formato original del modelo
    input_data = pd.DataFrame({
        'MedInc': [med_inc / 10000],  # Convertir de USD a decenas de miles de USD
        'HouseAge': [house_age],
        'AveRooms': [ave_rooms],
        'AveBedrms': [ave_bedrms],
        'Population': [population],
        'AveOccup': [ave_occup],
        'Latitude': [latitude],
        'Longitude': [longitude]
    })
    
    return input_data


def make_prediction(model, scaler, input_data):
    """Realiza la predicción"""
    try:
        # Escalar los datos
        input_scaled = scaler.transform(input_data)
        
        # Realizar predicción
        prediction = model.predict(input_scaled)[0]
        
        return prediction
        
    except Exception as e:
        st.error(f"Error al realizar predicción: {e}")
        return None


def create_feature_importance_chart(model, model_name):
    """Crea gráfico de importancia de features"""
    
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        
        # Nombres amigables para mostrar en el gráfico
        friendly_names = [
            '💵 Ingresos Familiares',
            '🏘️ Antigüedad Viviendas',
            '🛏️ Habitaciones/Casa',
            '🛌 Dormitorios/Casa',
            '👥 Población Zona',
            '🏠 Ocupantes/Casa',
            '📍 Ubicación Norte-Sur',
            '📍 Ubicación Este-Oeste'
        ]
        
        # Crear DataFrame para el gráfico
        importance_df = pd.DataFrame({
            'feature': friendly_names,
            'importance': importances
        }).sort_values('importance', ascending=True)
        
        # Crear gráfico
        fig = px.bar(
            importance_df,
            x='importance',
            y='feature',
            orientation='h',
            title=f'Importancia de Características',
            color='importance',
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_title="Importancia",
            yaxis_title="Características"
        )
        
        return fig
    
    return None


def create_prediction_gauge(prediction):
    """Crea un gauge para mostrar la predicción"""
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=prediction,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Precio Predicho (cientos de miles $)"},
        delta={'reference': 2.5},  # Precio promedio aproximado
        gauge={
            'axis': {'range': [None, 6]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 2], 'color': "lightgray"},
                {'range': [2, 3.5], 'color': "gray"},
                {'range': [3.5, 6], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 5
            }
        }
    ))
    
    fig.update_layout(height=400)
    return fig


def main():
    """Función principal de la aplicación"""
    
    st.set_page_config(
        page_title="Price Predictor - California Housing",
        page_icon="🏠",
        layout="wide"
    )
    
    # Título principal
    st.title("🏠 Predictor de Precios de Viviendas en California")
    st.markdown("""
    **Predicción inteligente de precios usando Machine Learning**
    
    Esta aplicación utiliza modelos avanzados de inteligencia artificial para predecir 
    el valor de viviendas en California basándose en características económicas, 
    demográficas y geográficas del área.
    """)
    
    # Cargar configuración
    try:
        config = load_config()
    except:
        st.error("Error al cargar configuración")
        return
    
    # Cargar modelo
    model, scaler, model_name = load_model_and_scaler()
    
    if model is None:
        st.warning("⚠️ No se encontró un modelo entrenado. Ejecuta primero el entrenamiento.")
        st.markdown("""
        Para entrenar los modelos, ejecuta:
        ```bash
        python src/models/train_models.py
        ```
        """)
        return
    

    
    # Sidebar con información
    with st.sidebar:
        st.header("ℹ️ Información del Sistema")
        st.markdown(f"""
        **🤖 Modelo Activo:** {model_name.replace('_', ' ').title()}
        
        **📊 Dataset:** Viviendas de California  
        **🎯 Predicción:** Valor medio de viviendas
        
        **✨ Características:**
        - 8 variables predictoras intuitivas
        - Datos económicos y demográficos
        - Entrenado con optimización avanzada
        - Interfaz amigable para el usuario
        """)
        
        if st.button("📈 Ver Estadísticas"):
            st.markdown("""
            **📊 Datos del Dataset:**
            - 🏘️ 20,640 áreas analizadas
            - 💰 Precio promedio: $200k
            - 📈 Rango: $14k - $500k
            - 📅 Época: Década de 1990
            - 🌎 Región: California, USA
            """)
    
    # Crear inputs para features
    input_data = create_feature_inputs(config)
    
    # Botón de predicción
    if st.button("🔮 Obtener Precio", type="primary"):
        prediction = make_prediction(model, scaler, input_data)
        
        if prediction is not None:
            # Convertir predicción a dólares para mostrar
            prediction_dollars = prediction * 100000  # Convertir a dólares
            
            # Mostrar predicción en columnas
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.header("📈 Resultado de la Estimación")
                
                # Gauge de predicción
                gauge_fig = create_prediction_gauge(prediction)
                st.plotly_chart(gauge_fig, use_container_width=True)
                
                # Información adicional
                st.info(f"""
                **💰 Precio Estimado: ${prediction_dollars:,.0f}**
                

                📊 Valor técnico: {prediction:.2f} (cientos de miles)
                
                *💡 Estimación basada en datos históricos de California (década de 1990).
                Los precios pueden variar según condiciones actuales del mercado.*
                """)
            
            with col2:
                # Gráfico de importancia de features (si disponible)
                importance_fig = create_feature_importance_chart(model, model_name)
                
                if importance_fig is not None:
                    st.header("📊 Importancia de Características")
                    st.plotly_chart(importance_fig, use_container_width=True)
                    st.caption("Este gráfico muestra qué características son más importantes para determinar el precio.")
                else:
                    st.header("📋 Datos de Entrada (Formato Técnico)")
                    st.dataframe(input_data.T, use_container_width=True)
                    st.caption("Valores internos utilizados por el modelo de machine learning.")
    
    # Información adicional
    st.markdown("---")
    st.markdown("""
    ### 💡 ¿Cómo funciona?
    
    1. **🎛️ Ajusta los parámetros** usando los controles deslizantes arriba
    2. **🔮 Presiona "Obtener Precio"** para obtener el precio estimado
    3. **📊 Analiza los resultados** y la importancia de cada característica
    4. **🔄 Experimenta** con diferentes valores para explorar el mercado
    
    **🧠 Tecnología:** Este predictor utiliza algoritmos de Machine Learning entrenados 
    con datos reales del mercado inmobiliario de California.
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        🏠 Predictor de Precios de Viviendas | Desarrollado con ❤️ usando Streamlit y Machine Learning
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
