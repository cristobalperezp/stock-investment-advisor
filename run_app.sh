#!/bin/bash
# Script para lanzar la aplicación Streamlit del Stock Investment Advisor

echo "🚀 Iniciando Stock Investment Advisor - Mercado Chileno..."
echo "📊 Dashboard interactivo disponible en: http://localhost:8501"
echo ""

cd "$(dirname "$0")"

# Ejecutar Streamlit
/usr/local/bin/python3 -m streamlit run src/ui/streamlit_app.py \
    --server.port 8501 \
    --server.headless false \
    --browser.gatherUsageStats false \
    --theme.base "light" \
    --theme.primaryColor "#1f77b4"
