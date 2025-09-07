#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotly.express as px
from data_sources.yahoo_finance import YahooFinanceDataExtractor

def test_volatility_chart():
    print("🔍 Probando gráfico de volatilidad...")
    
    extractor = YahooFinanceDataExtractor()
    volatility = extractor.get_volatility_ranking()
    
    print(f"Datos de volatilidad:")
    print(volatility)
    print()
    
    if not volatility.empty:
        print("Creando gráfico de treemap...")
        try:
            fig = px.treemap(
                volatility,
                values='current_volatility',
                names='name',
                color='current_volatility',
                color_continuous_scale='RdYlGn_r',
                title='Mapa de Volatilidad por Acción'
            )
            
            fig.update_layout(height=500)
            print("✅ Gráfico creado exitosamente!")
            print(f"Figura tipo: {type(fig)}")
            
            # Guardar como HTML para revisar
            fig.write_html("test_volatility_chart.html")
            print("📄 Gráfico guardado como 'test_volatility_chart.html'")
            
        except Exception as e:
            print(f"❌ Error creando gráfico: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ No hay datos de volatilidad")

if __name__ == "__main__":
    test_volatility_chart()
