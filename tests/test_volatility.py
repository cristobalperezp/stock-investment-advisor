#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_sources.yahoo_finance import YahooFinanceDataExtractor

def test_volatility():
    print("🔍 Probando función de volatilidad...")
    
    extractor = YahooFinanceDataExtractor()
    
    # Probar con un símbolo específico primero
    print("\n1. Probando datos históricos de una acción:")
    hist_data = extractor.get_historical_data("SQM-B.SN", "1mo")
    print(f"   Shape: {hist_data.shape}")
    print(f"   Columns: {hist_data.columns.tolist()}")
    print(f"   Tiene Volatility?: {'Volatility' in hist_data.columns}")
    
    if 'Volatility' in hist_data.columns:
        print(f"   Volatility values (last 5): {hist_data['Volatility'].tail().tolist()}")
    
    print("\n2. Probando función de volatilidad completa:")
    volatility = extractor.get_volatility_ranking()
    print(f"   Shape: {volatility.shape}")
    print(f"   Columns: {volatility.columns.tolist()}")
    print(f"   Empty?: {volatility.empty}")
    
    if not volatility.empty:
        print(f"   First 3 rows:")
        print(volatility.head(3))
    else:
        print("   ❌ DataFrame está vacío!")

if __name__ == "__main__":
    test_volatility()
