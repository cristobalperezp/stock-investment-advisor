#!/usr/bin/env python3
"""
Script de prueba para verificar si se han resuelto los errores de comparación de tipos
"""

import sys
import os
import pandas as pd

# Añadir el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analysis.investment_analyzer import InvestmentAnalyzer
from utils.config import load_config

def test_type_errors():
    """Prueba las funciones que anteriormente daban errores de comparación de tipos"""
    print("=== INICIANDO PRUEBAS DE ERRORES DE TIPO ===")
    
    try:
        # Cargar configuración
        config = load_config()
        print("✓ Configuración cargada")
        
        # Crear analyzer
        analyzer = InvestmentAnalyzer()
        print("✓ InvestmentAnalyzer creado")
        
        # Crear datos de prueba con tipos mixtos para simular el problema
        test_data = pd.DataFrame({
            'Empresa': ['SQM-B.SN', 'FALABELLA.SN', 'CENCOSUD.SN', 'COPEC.SN', 'CCU.SN'],
            'Ticker': ['SQM-B.SN', 'FALABELLA.SN', 'CENCOSUD.SN', 'COPEC.SN', 'CCU.SN'],
            'Valor_Accion': [15000, '18000', 22000, '25000', 30000],  # Tipos mixtos
            'Monto_Inversion': ['50000', 75000, '100000', 125000, '150000'],  # Tipos mixtos
            'Peso_Asignado': [0.15, '0.20', 0.25, '0.30', 0.10],  # Tipos mixtos
            'Paga_Dividendos': ['Sí', 'No', 'Sí', 'Sí', 'No'],
            'ROE': ['0.15', 0.10, '0.08', 0.12, '0.20'],  # Tipos mixtos
            'Dividend_Yield': [0.05, '0.03', 0.04, '0.06', 0.02],
            'Variacion_6M': ['0.10', -0.05, '0.15', 0.20, '-0.08'],
            'Beta': [1.2, '1.5', 0.8, '1.1', 1.3],
            'PE_Ratio': ['15.5', 12.0, '18.2', 10.5, '22.1'],
            'Margen_Beneficio': [0.12, '0.08', 0.15, '0.10', 0.18]
        })
        
        print("✓ Datos de prueba creados con tipos mixtos")
        
        # Configurar datos en el analyzer
        analyzer.fundamental_data = test_data
        
        # Crear portfolio_weights con las columnas correctas
        portfolio_weights_data = pd.DataFrame({
            'Ticker': ['SQM-B.SN', 'FALABELLA.SN', 'CENCOSUD.SN', 'COPEC.SN', 'CCU.SN'],
            'Empresa': ['SQM-B.SN', 'FALABELLA.SN', 'CENCOSUD.SN', 'COPEC.SN', 'CCU.SN'],
            'Sector': ['Minería', 'Retail', 'Retail', 'Energía', 'Bebidas'],
            'Peso_Asignado': [0.15, '0.20', 0.25, '0.30', 0.10],  # Tipos mixtos
            'Puntaje': [0.8, '0.9', 0.85, '0.95', 0.75]  # Tipos mixtos
        })
        analyzer.portfolio_weights = portfolio_weights_data
        
        print("✓ Datos configurados en analyzer")
        
        # Test 1: generate_investment_recommendations (línea 403 original)
        print("\n--- Test 1: generate_investment_recommendations ---")
        try:
            recommendations = analyzer.generate_investment_recommendations(budget=1000000)
            print("✓ generate_investment_recommendations ejecutado sin errores")
        except Exception as e:
            print(f"✗ Error en generate_investment_recommendations: {e}")
        
        # Test 2: get_market_summary (líneas 452-453 originales)
        print("\n--- Test 2: get_market_summary ---")
        try:
            analyzer.fundamental_data = test_data  # Reconfigurar
            summary = analyzer.get_market_summary()
            print("✓ get_market_summary ejecutado sin errores")
        except Exception as e:
            print(f"✗ Error en get_market_summary: {e}")
        
        # Test 3: _generate_fallback_distribution (línea 708 original)
        print("\n--- Test 3: _generate_fallback_distribution ---")
        try:
            portfolio_weights = test_data[['Empresa', 'Peso_Asignado']].set_index('Empresa')
            fallback_dist = analyzer._generate_fallback_distribution(portfolio_weights, 1000000)
            print("✓ _generate_fallback_distribution ejecutado sin errores")
        except Exception as e:
            print(f"✗ Error en _generate_fallback_distribution: {e}")
        
        # Test 4: _generate_fallback_analysis
        print("\n--- Test 4: _generate_fallback_analysis ---")
        try:
            fallback_analysis = analyzer._generate_fallback_analysis(test_data)
            print("✓ _generate_fallback_analysis ejecutado sin errores")
        except Exception as e:
            print(f"✗ Error en _generate_fallback_analysis: {e}")
        
        print("\n=== TODAS LAS PRUEBAS COMPLETADAS ===")
        
    except Exception as e:
        print(f"✗ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_type_errors()
