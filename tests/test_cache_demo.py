#!/usr/bin/env python3
"""
Demostración del sistema de caché diario para datos fundamentales
"""

import sys
sys.path.append('src')

from analysis.investment_analyzer import InvestmentAnalyzer
import time

def main():
    print("🔍 DEMOSTRACIÓN DEL SISTEMA DE CACHÉ DIARIO")
    print("=" * 50)
    
    analyzer = InvestmentAnalyzer()
    
    # Verificar estado del caché
    cache_info = analyzer.get_cache_info()
    print("\n📁 Estado inicial del caché:")
    for key, value in cache_info.items():
        print(f"   {key}: {value}")
    
    print("\n🔄 Ejecutando primera descarga de datos...")
    start_time = time.time()
    df1 = analyzer.download_all_fundamental_data()
    first_duration = time.time() - start_time
    print(f"   ✅ Primera ejecución completada en {first_duration:.2f} segundos")
    print(f"   📊 Datos obtenidos: {len(df1)} empresas")
    
    print("\n🔄 Ejecutando segunda descarga (debería usar caché)...")
    start_time = time.time()
    df2 = analyzer.download_all_fundamental_data()
    second_duration = time.time() - start_time
    print(f"   ✅ Segunda ejecución completada en {second_duration:.2f} segundos")
    print(f"   📊 Datos obtenidos: {len(df2)} empresas")
    
    # Verificar estado final del caché
    cache_info = analyzer.get_cache_info()
    print("\n📁 Estado final del caché:")
    for key, value in cache_info.items():
        print(f"   {key}: {value}")
    
    # Mostrar diferencia de tiempo
    time_saved = first_duration - second_duration
    print(f"\n⚡ Tiempo ahorrado con caché: {time_saved:.2f} segundos")
    print(f"📈 Mejora de velocidad: {(time_saved/first_duration)*100:.1f}%")
    
    # Verificar que los datos son idénticos
    if df1.equals(df2):
        print("✅ Los datos son idénticos - caché funcionando correctamente")
    else:
        print("❌ Los datos difieren - posible problema con el caché")

if __name__ == "__main__":
    main()
