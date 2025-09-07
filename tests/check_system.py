#!/usr/bin/env python3
"""
Script de verificación rápida para el News Summarizer
Verifica que todos los componentes estén funcionando correctamente
"""

import sys
from pathlib import Path
import importlib

# Agregar el directorio src al path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

def check_imports():
    """Verifica que todas las librerías necesarias estén instaladas"""
    print("🔍 Verificando imports...")
    
    required_modules = [
        'yfinance',
        'pandas', 
        'numpy',
        'yaml',
        'streamlit',
        'plotly'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            missing_modules.append(module)
    
    return missing_modules

def check_data_source():
    """Verifica que el módulo de datos funcione"""
    print("\n📊 Verificando fuente de datos...")
    
    try:
        from data_sources.yahoo_finance import YahooFinanceDataExtractor
        
        extractor = YahooFinanceDataExtractor()
        
        # Probar obtener un resumen rápido
        summary = extractor.get_market_summary()
        
        if summary and 'total_stocks' in summary:
            print(f"  ✅ Datos del mercado: {summary['total_stocks']} acciones")
            print(f"  ✅ Tendencia: {summary.get('market_trend', 'Unknown')}")
            return True
        else:
            print("  ❌ Error obteniendo datos del mercado")
            return False
            
    except Exception as e:
        print(f"  ❌ Error en fuente de datos: {e}")
        return False

def check_config():
    """Verifica que la configuración se cargue correctamente"""
    print("\n⚙️ Verificando configuración...")
    
    try:
        from utils.config import get_config
        
        config = get_config()
        
        # Verificar elementos clave
        symbols = config.get_stock_symbols()
        streamlit_config = config.get_streamlit_config()
        
        if symbols:
            print(f"  ✅ Símbolos de acciones: {len(symbols)} configurados")
        else:
            print("  ❌ No hay símbolos configurados")
            
        if streamlit_config:
            print(f"  ✅ Puerto Streamlit: {streamlit_config.get('server_port', 'No configurado')}")
        else:
            print("  ❌ Configuración de Streamlit no encontrada")
            
        return bool(symbols and streamlit_config)
        
    except Exception as e:
        print(f"  ❌ Error en configuración: {e}")
        return False

def check_files():
    """Verifica que los archivos necesarios existan"""
    print("📁 Verificando archivos...")
    
    # Archivos principales del proyecto (rutas desde el directorio padre)
    required_files = [
        "../config/config.yaml",
        "../src/data_sources/yahoo_finance.py", 
        "../src/utils/config.py",
        "../src/ui/streamlit_app.py",
        "../src/ui/pages.py",
        "../requirements.txt",
        "../run_app.sh"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    return missing_files

def main():
    """Función principal de verificación"""
    print("🚀 VERIFICACIÓN DEL SISTEMA - News Summarizer")
    print("=" * 50)
    
    # Verificar imports
    missing_modules = check_imports()
    
    # Verificar archivos
    missing_files = check_files()
    
    # Verificar configuración
    config_ok = check_config()
    
    # Verificar fuente de datos
    data_ok = check_data_source()
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    if missing_modules:
        print(f"❌ Módulos faltantes: {', '.join(missing_modules)}")
        print("   Ejecuta: pip install " + " ".join(missing_modules))
    else:
        print("✅ Todos los módulos están instalados")
    
    if missing_files:
        print(f"❌ Archivos faltantes: {len(missing_files)}")
        for file in missing_files:
            print(f"   - {file}")
    else:
        print("✅ Todos los archivos están presentes")
    
    if config_ok:
        print("✅ Configuración cargada correctamente")
    else:
        print("❌ Problemas con la configuración")
    
    if data_ok:
        print("✅ Fuente de datos funcionando")
    else:
        print("❌ Problemas con la fuente de datos")
    
    # Verificación final
    all_ok = not missing_modules and not missing_files and config_ok and data_ok
    
    print("\n" + "=" * 50)
    if all_ok:
        print("🎉 SISTEMA LISTO PARA USAR")
        print("\nPara ejecutar la aplicación:")
        print("  ./run_app.sh")
        print("  O visita: http://localhost:8501")
    else:
        print("⚠️  SISTEMA REQUIERE ATENCIÓN")
        print("\nRevisa los errores anteriores antes de continuar")
    
    print("=" * 50)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    exit(main())
