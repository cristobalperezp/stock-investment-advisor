#!/bin/bash

# 🏠 Price Predictor - Script de Inicio Rápido

echo "🏠 Price Predictor - Boston Housing"
echo "=================================="

# Verificar si estamos en el directorio correcto
if [ ! -f "config/config.yaml" ]; then
    echo "❌ Error: Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo ""
echo "🤖 Entrenando modelos..."
python src/models/train_models.py

echo ""
echo "🚀 Iniciando aplicación Streamlit..."
echo "   Accede a: http://localhost:8501"
echo ""

streamlit run src/ui/streamlit_app.py
