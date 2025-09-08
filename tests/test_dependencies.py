#!/usr/bin/env python3
"""
Script para verificar que todas las dependencias estén correctamente instaladas
"""

import sys
import importlib
from typing import List, Tuple

def test_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """
    Prueba importar un módulo específico
    """
    try:
        importlib.import_module(module_name)
        return True, f"✅ {package_name or module_name}"
    except ImportError as e:
        return False, f"❌ {package_name or module_name}: {e}"
    except Exception as e:
        return False, f"⚠️  {package_name or module_name}: {e}"

def main():
    """
    Verifica todas las dependencias principales
    """
    print("🧪 VERIFICACIÓN DE DEPENDENCIAS")
    print("=" * 50)
    
    # Lista de dependencias principales
    dependencies = [
        ("streamlit", "Streamlit"),
        ("pandas", "Pandas"), 
        ("numpy", "NumPy"),
        ("yfinance", "yFinance"),
        ("requests", "Requests"),
        ("openai", "OpenAI"),
        ("plotly", "Plotly"),
        ("matplotlib", "Matplotlib"),
        ("sklearn", "Scikit-learn"),
        ("joblib", "Joblib"),
        ("yaml", "PyYAML"),
        ("pathlib", "Pathlib"),
        ("json", "JSON (built-in)"),
        ("os", "OS (built-in)"),
        ("sys", "Sys (built-in)"),
        ("datetime", "Datetime (built-in)"),
        ("concurrent.futures", "Concurrent Futures"),
        ("email.mime.text", "Email MIME"),
        ("smtplib", "SMTP (built-in)"),
    ]
    
    # Dependencias opcionales/adicionales
    optional_dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("bs4", "Beautiful Soup 4"),  # beautifulsoup4 se importa como bs4
        ("aiohttp", "AioHTTP"),
        ("dotenv", "Python-dotenv"),
        ("jinja2", "Jinja2"),
    ]
    
    success_count = 0
    total_count = 0
    
    print("\n📦 DEPENDENCIAS PRINCIPALES:")
    print("-" * 30)
    
    for module, display_name in dependencies:
        success, message = test_import(module, display_name)
        print(message)
        if success:
            success_count += 1
        total_count += 1
    
    print(f"\n📦 DEPENDENCIAS OPCIONALES:")
    print("-" * 30)
    
    optional_success = 0
    for module, display_name in optional_dependencies:
        success, message = test_import(module, display_name)
        print(message)
        if success:
            optional_success += 1
    
    # Pruebas específicas
    print(f"\n🧪 PRUEBAS ESPECÍFICAS:")
    print("-" * 30)
    
    try:
        import pandas as pd
        df = pd.DataFrame({'test': [1, 2, 3]})
        print("✅ Pandas - Creación de DataFrame")
    except Exception as e:
        print(f"❌ Pandas - Creación de DataFrame: {e}")
    
    try:
        import numpy as np
        arr = np.array([1, 2, 3])
        print("✅ NumPy - Creación de arrays")
    except Exception as e:
        print(f"❌ NumPy - Creación de arrays: {e}")
    
    try:
        import plotly.graph_objects as go
        fig = go.Figure()
        print("✅ Plotly - Creación de gráficos")
    except Exception as e:
        print(f"❌ Plotly - Creación de gráficos: {e}")
    
    try:
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        print("✅ Scikit-learn - MinMaxScaler")
    except Exception as e:
        print(f"❌ Scikit-learn - MinMaxScaler: {e}")
    
    try:
        import yfinance as yf
        # Solo crear el objeto, no descargar datos
        ticker = yf.Ticker("AAPL")
        print("✅ yFinance - Creación de ticker")
    except Exception as e:
        print(f"❌ yFinance - Creación de ticker: {e}")
    
    # Resumen
    print(f"\n📊 RESUMEN:")
    print("=" * 30)
    print(f"✅ Dependencias principales: {success_count}/{total_count}")
    print(f"⚡ Dependencias opcionales: {optional_success}/{len(optional_dependencies)}")
    
    success_rate = (success_count / total_count) * 100
    if success_rate >= 90:
        print(f"🏆 ¡Excelente! {success_rate:.1f}% de las dependencias principales funcionan correctamente")
    elif success_rate >= 80:
        print(f"👍 Bien: {success_rate:.1f}% de las dependencias principales funcionan")
    else:
        print(f"⚠️  Atención: Solo {success_rate:.1f}% de las dependencias principales funcionan")
    
    # Información del sistema
    print(f"\n🖥️  INFORMACIÓN DEL SISTEMA:")
    print("-" * 30)
    print(f"Python: {sys.version}")
    print(f"Plataforma: {sys.platform}")
    print(f"Executable: {sys.executable}")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
