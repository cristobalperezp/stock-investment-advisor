#!/usr/bin/env python3
"""
Script para probar el sistema de caché completo en todas las funcionalidades
"""

import sys
import time
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from data_sources.yahoo_finance import YahooFinanceDataExtractor


def test_cache_performance():
    """Prueba el rendimiento del sistema de caché completo"""
    print("🧪 PRUEBA DEL SISTEMA DE CACHÉ COMPLETO")
    print("=" * 60)
    
    extractor = YahooFinanceDataExtractor()
    
    # Información inicial del caché
    print("\n📋 Estado inicial del caché:")
    cache_info = extractor.get_cache_info()
    print(f"  📁 Archivos: {cache_info.get('total_files', 0)}")
    print(f"  💽 Tamaño: {cache_info.get('total_size_mb', 0):.1f} MB")
    
    # Lista de funciones a probar
    test_functions = [
        ("Precios Actuales", lambda: extractor.get_current_prices()),
        ("Resumen del Mercado", lambda: extractor.get_market_summary()),
        ("Rendimiento Sectorial", lambda: extractor.get_sector_performance()),
        ("Datos Históricos Múltiples", 
         lambda: extractor.get_multiple_historical_data(period="3mo")),
    ]
    
    results = {}
    
    # Primera ejecución (descarga datos)
    print("\n🔄 PRIMERA EJECUCIÓN (descarga datos):")
    print("-" * 40)
    
    for name, func in test_functions:
        print(f"📡 Ejecutando {name}...")
        start_time = time.time()
        
        try:
            result = func()
            execution_time = time.time() - start_time
            
            # Determinar el tamaño/cantidad de datos
            if hasattr(result, 'shape'):
                data_info = f"{result.shape[0]} filas"
            elif isinstance(result, dict):
                if 'total_stocks' in result:
                    data_info = f"{result['total_stocks']} acciones"
                elif len(result) > 0 and hasattr(list(result.values())[0], 'shape'):
                    data_info = f"{len(result)} series históricas"
                else:
                    data_info = f"{len(result)} elementos"
            else:
                data_info = "datos obtenidos"
            
            results[name] = {
                'first_run': execution_time,
                'data_info': data_info,
                'success': True
            }
            
            print(f"  ✅ {name}: {execution_time:.2f}s ({data_info})")
            
        except Exception as e:
            print(f"  ❌ {name}: Error - {e}")
            results[name] = {'first_run': 0, 'success': False, 'error': str(e)}
    
    # Pausa breve
    time.sleep(1)
    
    # Segunda ejecución (desde caché)
    print("\n⚡ SEGUNDA EJECUCIÓN (desde caché):")
    print("-" * 40)
    
    for name, func in test_functions:
        if not results[name]['success']:
            continue
            
        print(f"💾 Ejecutando {name}...")
        start_time = time.time()
        
        try:
            result = func()
            execution_time = time.time() - start_time
            results[name]['second_run'] = execution_time
            
            print(f"  ✅ {name}: {execution_time:.3f}s (desde caché)")
            
        except Exception as e:
            print(f"  ❌ {name}: Error en caché - {e}")
            results[name]['cache_error'] = str(e)
    
    # Análisis de resultados
    print("\n📊 ANÁLISIS DE RENDIMIENTO:")
    print("=" * 60)
    
    total_improvement = 0
    successful_tests = 0
    
    for name, data in results.items():
        if not data['success']:
            print(f"❌ {name}: Falló - {data.get('error', 'Error desconocido')}")
            continue
        
        first_time = data['first_run']
        second_time = data.get('second_run', first_time)
        
        if second_time < first_time:
            improvement = ((first_time - second_time) / first_time) * 100
            total_improvement += improvement
            successful_tests += 1
            
            print(f"⚡ {name}:")
            print(f"   🕐 Primera vez: {first_time:.2f}s")
            print(f"   ⚡ Con caché: {second_time:.3f}s")
            print(f"   📈 Mejora: {improvement:.1f}%")
            print(f"   📊 Datos: {data['data_info']}")
        else:
            print(f"⚠️  {name}: Sin mejora significativa")
        
        print()
    
    # Resumen final
    if successful_tests > 0:
        avg_improvement = total_improvement / successful_tests
        print(f"🎯 RESUMEN FINAL:")
        print(f"   ✅ Pruebas exitosas: {successful_tests}/{len(test_functions)}")
        print(f"   📈 Mejora promedio: {avg_improvement:.1f}%")
        
        # Estado final del caché
        final_cache_info = extractor.get_cache_info()
        print(f"   📁 Archivos de caché: {final_cache_info.get('total_files', 0)}")
        print(f"   💽 Tamaño total: {final_cache_info.get('total_size_mb', 0):.1f} MB")
        
        if avg_improvement > 30:
            print("🏆 ¡Sistema de caché funcionando EXCELENTEMENTE!")
        elif avg_improvement > 10:
            print("👍 Sistema de caché funcionando correctamente")
        else:
            print("⚠️  Sistema de caché con mejoras menores")
    else:
        print("❌ No se pudieron completar las pruebas exitosamente")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_cache_performance()
