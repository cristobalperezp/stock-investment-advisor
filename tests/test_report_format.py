#!/usr/bin/env python3
"""
Script para probar el formato del reporte completo
"""

import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / 'src'
sys.path.append(str(src_path))

from analysis.investment_analyzer import InvestmentAnalyzer
from analysis.report_generator import generate_investment_report

def test_report_format():
    print("🧪 Probando formato del reporte completo...")
    
    try:
        # Ejecutar un análisis simple
        analyzer = InvestmentAnalyzer()
        result = analyzer.run_complete_analysis_with_gpt(
            budget=5000000,
            risk_level='moderado',
            dividend_preference=True,
            top_stocks_count=3  # Solo 3 para prueba rápida
        )
        
        print(f"✅ Análisis completado. TOP {result['top_stocks_count']} acciones seleccionadas")
        
        # Generar reporte
        report = generate_investment_report(
            result['fundamental_data'],
            result['recommendations'],
            result['market_summary']
        )
        
        # Mostrar el texto del análisis
        analysis_text = report['texto_analisis']
        
        print("\n" + "="*80)
        print("📄 CONTENIDO DEL REPORTE (texto_analisis):")
        print("="*80)
        print(repr(analysis_text[:500]))  # Primeros 500 caracteres con repr para ver caracteres especiales
        print("\n" + "="*80)
        print("📄 CONTENIDO RENDERIZADO:")
        print("="*80)
        print(analysis_text[:1000])  # Primeros 1000 caracteres normales
        print("="*80)
        
        # Verificar si tiene formato Markdown
        has_markdown = any(marker in analysis_text for marker in ['##', '###', '**', '- **'])
        print(f"\n🔍 Contiene formato Markdown: {'✅ SÍ' if has_markdown else '❌ NO'}")
        
        if has_markdown:
            print("🎯 El texto tiene formato Markdown correcto")
        else:
            print("⚠️ El texto NO tiene formato Markdown")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_report_format()
