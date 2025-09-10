#!/usr/bin/env python3
"""
Script para probar la generación de reportes PDF sin enviar email
"""

import os
import sys
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, 'src')

from automation.monthly_report import run_monthly_analysis, generate_monthly_report

def test_pdf_generation():
    """Prueba solo la generación del PDF"""
    print("=" * 60)
    print("🧪 PRUEBA DE GENERACIÓN DE REPORTE PDF")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    try:
        # 1. Ejecutar análisis
        print("🔄 Paso 1: Ejecutando análisis de mercado...")
        result, config = run_monthly_analysis()
        
        # 2. Generar solo el reporte PDF
        print("🔄 Paso 2: Generando reporte PDF...")
        report_content, pdf_filename = generate_monthly_report(result, config)
        
        # 3. Mostrar resultado
        print("\n" + "=" * 60)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print(f"📊 Empresas analizadas: {result['market_summary']['total_empresas']}")
        print(f"🎯 Recomendaciones: {result['recommendations']['empresas_recomendadas']}")
        print(f"📄 Archivo PDF generado: {pdf_filename}")
        
        # Verificar que el archivo existe
        if os.path.exists(pdf_filename):
            file_size = os.path.getsize(pdf_filename)
            print(f"💾 Tamaño del archivo: {file_size:,} bytes")
            print(f"📂 Ubicación: {os.path.abspath(pdf_filename)}")
        else:
            print("❌ El archivo PDF no fue encontrado")
        
        print(f"⏰ Completado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Mostrar preview del contenido del email
        print("\n" + "-" * 60)
        print("📧 PREVIEW DEL CONTENIDO DEL EMAIL:")
        print("-" * 60)
        print(report_content)
        
    except Exception as e:
        print("\n❌ ERROR EN LA PRUEBA:")
        print(f"   {str(e)}")
        print("\nDetalles para debugging:")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_pdf_generation()
