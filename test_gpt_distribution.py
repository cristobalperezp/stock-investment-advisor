#!/usr/bin/env python3
"""
Script de prueba para verificar que la distribución GPT se muestra correctamente
sin sincronización automática
"""

import sys
import os
from pathlib import Path

from dotenv import load_dotenv

# Configurar paths del proyecto para imports absolutos
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Asegurar que la ejecución use la raíz del proyecto y que existan directorios requeridos
if Path.cwd() != ROOT_DIR:
    os.chdir(ROOT_DIR)

(ROOT_DIR / "data" / "processed").mkdir(parents=True, exist_ok=True)

# Cargar variables de entorno (incluye OPENAI_API_KEY) desde .env si existe
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=False)

from src.analysis.investment_analyzer import InvestmentAnalyzer

def test_gpt_distribution():
    """Test básico de la distribución GPT"""
    
    print("🧪 TEST: Distribución GPT sin sincronización")
    print("=" * 50)
    
    try:
        # Crear analizador
        analyzer = InvestmentAnalyzer()
        
        # Verificar si OpenAI está disponible
        if not os.getenv('OPENAI_API_KEY'):
            print("❌ OPENAI_API_KEY no encontrada")
            print("💡 Configure la variable de entorno para probar GPT")
            return False
        
        print("✅ OpenAI API Key encontrada")
        
        # Refrescar datos fundamentales antes de generar recomendaciones
        print("📥 Actualizando datos fundamentales de las acciones...")
        fresh_data = analyzer.download_all_fundamental_data()
        print(f"✅ Datos actualizados para {len(fresh_data)} acciones\n")
        
        # Ejecutar análisis con GPT
        print("🔄 Ejecutando análisis con GPT...")
        result = analyzer.run_complete_analysis_with_gpt(
            budget=220000,  # Presupuesto pequeño para prueba rápida
            risk_level="agresivo",
            dividend_preference=True,
            top_stocks_count=6  # 7 empresas para test
        )
        
        # Verificar resultados
        print("\n📊 RESULTADOS DEL TEST:")
        print(f"- Empresas analizadas: {result.get('total_stocks_analyzed', 'N/A')}")
        print(f"- TOP seleccionadas: {result.get('top_stocks_count', 'N/A')}")
        print(f"- Sincronización deshabilitada: {result.get('sync_disabled', False)}")
        
        # Verificar distribución GPT
        if 'gpt_distribution' in result and result['gpt_distribution']:
            print("\n✅ DISTRIBUCIÓN GPT ENCONTRADA:")
            print("-" * 40)
            print(result['gpt_distribution'])
            print("-" * 40)
            
            # Verificar que no es la versión automática
            if not result['gpt_distribution'].startswith('### Distribución de Inversión (Automatizada)'):
                print("✅ Distribución GPT es original (no automática)")
                
                # Analizar distribución para verificar diversificación
                lines = result['gpt_distribution'].split('\n')
                investment_lines = [line for line in lines if line.strip().startswith('- ') and '$' in line]
                
                print(f"\n📈 ANÁLISIS DE DIVERSIFICACIÓN:")
                print(f"- Empresas en distribución GPT: {len(investment_lines)}")
                
                # Contar sectores
                sectors_found = {}
                for line in investment_lines:
                    if 'HABITAT.SN' in line or 'PROVIDA.SN' in line or 'PLANVITAL.SN' in line:
                        sectors_found['AFP'] = sectors_found.get('AFP', 0) + 1
                    elif 'LTM.SN' in line:
                        sectors_found['Transporte'] = sectors_found.get('Transporte', 0) + 1
                    elif 'MALLPLAZA.SN' in line:
                        sectors_found['Inmobiliario'] = sectors_found.get('Inmobiliario', 0) + 1
                    elif 'BICECORP.SN' in line:
                        sectors_found['Banca'] = sectors_found.get('Banca', 0) + 1
                    elif 'FALABELLA.SN' in line:
                        sectors_found['Retail'] = sectors_found.get('Retail', 0) + 1
                
                print("- Distribución por sectores:")
                violation_found = False
                for sector, count in sectors_found.items():
                    status = "❌" if count > 2 else "✅"
                    print(f"  {status} {sector}: {count} empresa(s)")
                    if count > 2:
                        violation_found = True
                
                if violation_found:
                    print("\n🔴 PROBLEMA DETECTADO: GPT no respeta la regla de máximo 2 empresas por sector")
                    print("💡 NECESARIO: Mejorar el prompt de GPT para cumplir restricciones de diversificación")
                else:
                    print("\n🟢 DIVERSIFICACIÓN CORRECTA: GPT respeta las reglas")
                
                return True
            else:
                print("❌ Distribución parece ser automática, no GPT")
                return False
        else:
            print("❌ No se encontró distribución GPT")
            return False
    
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gpt_distribution()
    
    if success:
        print("\n🎉 TEST EXITOSO: Distribución GPT funcionando correctamente")
        print("🚀 Ahora puede usar la aplicación y ver la distribución GPT en la tab '🦾 Análisis GPT'")
    else:
        print("\n⚠️ TEST FALLÓ: Revisar configuración o logs")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Ejecutar la aplicación Streamlit")
    print("2. Ir a la tab '🦾 Análisis GPT'")
    print("3. Verificar que se muestra la distribución GPT sin modo debug")
    print("4. Mejorar el prompt si GPT no respeta las reglas de diversificación")
