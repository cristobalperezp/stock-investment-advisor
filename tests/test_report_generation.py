#!/usr/bin/env python3
"""
Script de diagnóstico para probar el generador de reportes
"""

import sys
import os
import pandas as pd

# Añadir el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analysis.investment_analyzer import InvestmentAnalyzer
from analysis.report_generator import generate_investment_report

def test_report_generation():
    """Prueba la generación de reportes"""
    print("=== INICIANDO PRUEBA DE GENERACIÓN DE REPORTES ===")
    
    try:
        # Crear analyzer
        analyzer = InvestmentAnalyzer()
        print("✓ InvestmentAnalyzer creado")
        
        # Ejecutar análisis simple
        result = analyzer.run_complete_analysis(budget=1000000)
        print("✓ Análisis completado")
        print(f"  - Datos fundamentales: {len(result['fundamental_data'])} empresas")
        print(f"  - Recomendaciones: {result['recommendations']['empresas_recomendadas']} empresas")
        print(f"  - Total empresas en mercado: {result['market_summary']['total_empresas']}")
        
        # Intentar generar reporte
        print("\n--- Generando reporte ---")
        report = generate_investment_report(
            result['fundamental_data'],
            result['recommendations'],
            result['market_summary']
        )
        print("✓ Reporte generado exitosamente")
        
        # Verificar componentes del reporte
        print("\n--- Verificando componentes ---")
        print(f"✓ Fecha: {report['fecha']}")
        print(f"✓ Texto de análisis: {len(report['texto_analisis'])} caracteres")
        print(f"✓ Gráficos disponibles: {list(report['graficos'].keys())}")
        
        # Probar cada gráfico
        for chart_name, chart in report['graficos'].items():
            try:
                # Intentar acceder a propiedades básicas del gráfico
                chart_data = chart.data
                chart_layout = chart.layout
                print(f"✓ Gráfico '{chart_name}': OK")
            except Exception as e:
                print(f"✗ Error en gráfico '{chart_name}': {e}")
        
        print("\n=== PRUEBA COMPLETADA EXITOSAMENTE ===")
        return True
        
    except Exception as e:
        print(f"✗ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_report_generation()
