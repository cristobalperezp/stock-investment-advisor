#!/usr/bin/env python3
"""
Script para probar el sistema de caché inteligente con acciones nuevas
Demuestra cómo se agregan nuevas acciones al caché existente sin redescargar todo
"""

import sys
import time
from pathlib import Path

# Agregar el directorio src al path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

from data_sources.yahoo_finance import YahooFinanceDataExtractor


def test_incremental_cache():
    """Prueba el sistema de caché incremental"""
    print("🧪 PRUEBA DEL CACHÉ INTELIGENTE CON NUEVAS ACCIONES")
    print("=" * 65)
    
    extractor = YahooFinanceDataExtractor()
    
    # Limpiar caché previo para la demostración
    cache_dir = extractor.cache_dir
    for cache_file in cache_dir.glob("current_prices_*_20250908.csv"):
        cache_file.unlink()
        print(f"🗑️  Limpiado: {cache_file.name}")
    
    # Conjunto inicial de acciones (3 acciones principales)
    initial_stocks = ["SQM-B.SN", "FALABELLA.SN", "CHILE.SN"]
    
    print(f"\n📊 FASE 1: Cargando acciones iniciales")
    print(f"Acciones: {[extractor.stock_names.get(s, s) for s in initial_stocks]}")
    print("-" * 50)
    
    start_time = time.time()
    initial_data = extractor.get_current_prices(initial_stocks, use_cache=True)
    phase1_time = time.time() - start_time
    
    print(f"✅ Datos iniciales obtenidos: {len(initial_data)} acciones en {phase1_time:.2f}s")
    print(f"📝 Acciones cargadas: {list(initial_data['name'])}")
    
    # Verificar caché
    cache_info = extractor.get_cache_info()
    print(f"💾 Estado del caché: {cache_info.get('total_files', 0)} archivos")
    
    # Pausa
    time.sleep(1)
    
    # Agregar nuevas acciones al conjunto existente
    new_stocks = ["COPEC.SN", "CCU.SN"]
    expanded_stocks = initial_stocks + new_stocks
    
    print(f"\n⚡ FASE 2: Agregando nuevas acciones")
    print(f"Nuevas acciones: {[extractor.stock_names.get(s, s) for s in new_stocks]}")
    print(f"Total acciones: {[extractor.stock_names.get(s, s) for s in expanded_stocks]}")
    print("-" * 50)
    
    start_time = time.time()
    expanded_data = extractor.get_current_prices(expanded_stocks, use_cache=True)
    phase2_time = time.time() - start_time
    
    print(f"✅ Datos expandidos obtenidos: {len(expanded_data)} acciones en {phase2_time:.2f}s")
    print(f"📝 Acciones finales: {list(expanded_data['name'])}")
    
    # Verificar que se mantuvieron los datos originales
    original_symbols = set(initial_data['symbol'])
    final_symbols = set(expanded_data['symbol'])
    maintained_symbols = original_symbols & final_symbols
    
    print(f"🔄 Acciones mantenidas desde caché: {len(maintained_symbols)}/{len(original_symbols)}")
    
    # Prueba de consistencia de datos
    print(f"\n🔍 VERIFICACIÓN DE CONSISTENCIA:")
    print("-" * 40)
    
    consistent_data = True
    for symbol in maintained_symbols:
        initial_price = initial_data[initial_data['symbol'] == symbol]['current_price'].iloc[0]
        final_price = expanded_data[expanded_data['symbol'] == symbol]['current_price'].iloc[0]
        
        if abs(initial_price - final_price) < 0.01:  # Tolerancia mínima
            status = "✅"
        else:
            status = "❌"
            consistent_data = False
        
        stock_name = extractor.stock_names.get(symbol, symbol)
        print(f"{status} {stock_name}: ${initial_price:.2f} → ${final_price:.2f}")
    
    # Fase 3: Agregar muchas acciones nuevas
    print(f"\n🚀 FASE 3: Agregando conjunto grande de acciones")
    print("-" * 50)
    
    all_stocks = extractor.default_stocks  # Todas las acciones disponibles
    print(f"Total de acciones por cargar: {len(all_stocks)}")
    print(f"Acciones ya en caché: {len(expanded_stocks)}")
    print(f"Acciones nuevas por descargar: {len(all_stocks) - len(expanded_stocks)}")
    
    start_time = time.time()
    all_data = extractor.get_current_prices(all_stocks, use_cache=True)
    phase3_time = time.time() - start_time
    
    print(f"✅ Conjunto completo obtenido: {len(all_data)} acciones en {phase3_time:.2f}s")
    
    # Análisis final
    print(f"\n📈 ANÁLISIS DE RENDIMIENTO:")
    print("=" * 50)
    
    print(f"⏱️  TIEMPOS DE EJECUCIÓN:")
    print(f"   Fase 1 (3 acciones nuevas): {phase1_time:.2f}s")
    print(f"   Fase 2 (2 acciones nuevas): {phase2_time:.2f}s")
    print(f"   Fase 3 ({len(all_stocks)-len(expanded_stocks)} acciones nuevas): {phase3_time:.2f}s")
    
    # Calcular eficiencia
    if phase1_time > 0:
        efficiency_phase2 = ((phase1_time - phase2_time) / phase1_time) * 100
        time_per_new_stock_phase2 = phase2_time / len(new_stocks) if new_stocks else 0
        time_per_new_stock_phase3 = phase3_time / (len(all_stocks) - len(expanded_stocks))
        
        print(f"\n📊 MÉTRICAS DE EFICIENCIA:")
        print(f"   Mejora en Fase 2: {efficiency_phase2:.1f}%")
        print(f"   Tiempo/acción nueva (Fase 2): {time_per_new_stock_phase2:.2f}s")
        print(f"   Tiempo/acción nueva (Fase 3): {time_per_new_stock_phase3:.2f}s")
        
        print(f"\n🔍 CONSISTENCIA DE DATOS:")
        if consistent_data:
            print("   ✅ Todos los datos mantenidos correctamente")
        else:
            print("   ⚠️  Se detectaron inconsistencias en los datos")
    
    # Estado final del caché
    final_cache_info = extractor.get_cache_info()
    print(f"\n💾 ESTADO FINAL DEL CACHÉ:")
    print(f"   📁 Archivos: {final_cache_info.get('total_files', 0)}")
    print(f"   💽 Tamaño total: {final_cache_info.get('total_size_mb', 0):.1f} MB")
    
    # Mostrar archivos de caché
    if final_cache_info.get('files'):
        print(f"   📄 Archivos recientes:")
        for file_info in final_cache_info['files'][:3]:
            print(f"      • {file_info['filename']} ({file_info['size_mb']:.1f} MB)")
    
    print(f"\n🎯 CONCLUSIÓN:")
    if phase2_time < phase1_time and phase3_time < (phase1_time * 2):
        print("🏆 ¡Sistema de caché inteligente funcionando PERFECTAMENTE!")
        print("   ✨ Nuevas acciones se agregan eficientemente al caché existente")
        print("   🔄 Los datos previamente descargados se reutilizan correctamente")
    else:
        print("⚠️  El sistema de caché necesita optimización")
    
    print("=" * 65)


def test_historical_incremental_cache():
    """Prueba el caché incremental para datos históricos"""
    print("\n🧪 PRUEBA DEL CACHÉ INCREMENTAL - DATOS HISTÓRICOS")
    print("=" * 65)
    
    extractor = YahooFinanceDataExtractor()
    
    # Limpiar caché histórico previo
    cache_dir = extractor.cache_dir
    for cache_file in cache_dir.glob("historical_*_20250908.csv"):
        cache_file.unlink()
        print(f"🗑️  Limpiado caché histórico: {cache_file.name}")
    
    # Conjunto inicial
    initial_stocks = ["SQM-B.SN", "FALABELLA.SN", "CHILE.SN"]
    print(f"\n📈 Cargando datos históricos iniciales:")
    print(f"Acciones: {[extractor.stock_names.get(s, s) for s in initial_stocks]}")
    
    start_time = time.time()
    initial_hist = extractor.get_multiple_historical_data(initial_stocks, period="1mo", use_cache=True)
    time1 = time.time() - start_time
    
    print(f"✅ Datos históricos iniciales: {len(initial_hist)} acciones en {time1:.2f}s")
    
    # Agregar nuevas acciones
    new_stocks = ["COPEC.SN", "CCU.SN"]
    expanded_stocks = initial_stocks + new_stocks
    
    print(f"\n⚡ Agregando nuevas acciones históricas:")
    print(f"Nuevas: {[extractor.stock_names.get(s, s) for s in new_stocks]}")
    
    start_time = time.time()
    expanded_hist = extractor.get_multiple_historical_data(expanded_stocks, period="1mo", use_cache=True)
    time2 = time.time() - start_time
    
    print(f"✅ Datos históricos expandidos: {len(expanded_hist)} acciones en {time2:.2f}s")
    
    # Verificar consistencia
    consistent = True
    for symbol in initial_stocks:
        if symbol in initial_hist and symbol in expanded_hist:
            if not initial_hist[symbol].equals(expanded_hist[symbol]):
                consistent = False
                break
    
    print(f"\n📊 Resultados de datos históricos:")
    print(f"   ⏱️  Tiempo inicial: {time1:.2f}s")
    print(f"   ⏱️  Tiempo incremental: {time2:.2f}s")
    print(f"   🔍 Consistencia: {'✅ Correcta' if consistent else '❌ Inconsistente'}")
    
    if time2 < time1:
        improvement = ((time1 - time2) / time1) * 100
        print(f"   📈 Mejora: {improvement:.1f}%")
        print("🏆 ¡Caché incremental histórico funcionando correctamente!")
    else:
        print("⚠️  Caché incremental histórico necesita optimización")


if __name__ == "__main__":
    test_incremental_cache()
    test_historical_incremental_cache()
