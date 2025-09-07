"""
Módulo para obtener datos financieros desde Yahoo Finance
Incluye precios, indicadores técnicos, y datos fundamentales
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suprimir advertencias de yfinance
warnings.filterwarnings('ignore', category=FutureWarning)


class YahooFinanceDataExtractor:
    """
    Extractor de datos financieros desde Yahoo Finance
    Optimizado para acciones del mercado chileno
    """
    
    def __init__(self):
        self.default_stocks = [
            "SQM-B.SN",    # SQM
            "FALABELLA.SN", # Falabella  
            "CENCOSUD.SN",  # Cencosud
            "COPEC.SN",     # Copec
            "CCU.SN",       # CCU
            "CHILE.SN",     # Banco de Chile
            "BSANTANDER.SN", # Santander
            "ENELCHILE.SN", # Enel Chile
            "COLBUN.SN",    # Colbún
            "AGUAS-A.SN"    # Aguas Andinas
        ]
        
        # Mapeo de símbolos a nombres
        self.stock_names = {
            "SQM-B.SN": "SQM",
            "FALABELLA.SN": "Falabella",
            "CENCOSUD.SN": "Cencosud", 
            "COPEC.SN": "Copec",
            "CCU.SN": "CCU",
            "CHILE.SN": "Banco de Chile",
            "BSANTANDER.SN": "Santander",
            "ENELCHILE.SN": "Enel Chile",
            "COLBUN.SN": "Colbún",
            "AGUAS-A.SN": "Aguas Andinas"
        }
    
    def get_current_prices(self, symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Obtiene precios actuales de las acciones
        
        Args:
            symbols: Lista de símbolos de acciones
            
        Returns:
            DataFrame con precios actuales
        """
        if symbols is None:
            symbols = self.default_stocks
            
        logger.info(f"Obteniendo precios actuales para {len(symbols)} acciones...")
        
        data_list = []
        
        def get_single_price(symbol):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="2d")
                
                if hist.empty:
                    logger.warning(f"No hay datos para {symbol}")
                    return None
                
                current_price = hist['Close'].iloc[-1]
                previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                change = current_price - previous_price
                change_pct = (change / previous_price) * 100 if previous_price != 0 else 0
                
                return {
                    'symbol': symbol,
                    'name': self.stock_names.get(symbol, symbol),
                    'current_price': round(current_price, 2),
                    'previous_price': round(previous_price, 2),
                    'change': round(change, 2),
                    'change_percent': round(change_pct, 2),
                    'volume': hist['Volume'].iloc[-1] if 'Volume' in hist else 0,
                    'market_cap': info.get('marketCap', 'N/A'),
                    'currency': info.get('currency', 'CLP'),
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            except Exception as e:
                logger.error(f"Error obteniendo datos de {symbol}: {e}")
                return None
        
        # Usar ThreadPoolExecutor para obtener datos en paralelo
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(get_single_price, symbol): symbol for symbol in symbols}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    data_list.append(result)
        
        df = pd.DataFrame(data_list)
        logger.info(f"Datos obtenidos para {len(df)} acciones")
        
        return df.sort_values('change_percent', ascending=False)
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Obtiene datos históricos de una acción
        
        Args:
            symbol: Símbolo de la acción
            period: Período de datos (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame con datos históricos
        """
        try:
            logger.info(f"Obteniendo datos históricos de {symbol} para período {period}")
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                logger.warning(f"No hay datos históricos para {symbol}")
                return pd.DataFrame()
            
            # Calcular indicadores técnicos básicos
            hist = self._add_technical_indicators(hist)
            
            # Añadir información adicional
            hist['symbol'] = symbol
            hist['name'] = self.stock_names.get(symbol, symbol)
            
            logger.info(f"Datos históricos obtenidos: {len(hist)} registros")
            return hist
            
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos de {symbol}: {e}")
            return pd.DataFrame()
    
    def get_multiple_historical_data(self, symbols: Optional[List[str]] = None, 
                                   period: str = "3mo") -> Dict[str, pd.DataFrame]:
        """
        Obtiene datos históricos de múltiples acciones
        
        Args:
            symbols: Lista de símbolos
            period: Período de datos
            
        Returns:
            Diccionario con DataFrames de datos históricos
        """
        if symbols is None:
            symbols = self.default_stocks
            
        logger.info(f"Obteniendo datos históricos de {len(symbols)} acciones")
        
        historical_data = {}
        
        def get_single_historical(symbol):
            return symbol, self.get_historical_data(symbol, period)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(get_single_historical, symbol): symbol for symbol in symbols}
            
            for future in as_completed(futures):
                symbol, data = future.result()
                if not data.empty:
                    historical_data[symbol] = data
        
        return historical_data
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Añade indicadores técnicos básicos al DataFrame
        
        Args:
            df: DataFrame con datos de precios
            
        Returns:
            DataFrame con indicadores técnicos
        """
        try:
            # Moving Averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['EMA_12'] = df['Close'].ewm(span=12).mean()
            df['EMA_26'] = df['Close'].ewm(span=26).mean()
            
            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            
            # Volatilidad
            df['Daily_Return'] = df['Close'].pct_change()
            df['Volatility'] = df['Daily_Return'].rolling(window=20).std() * np.sqrt(252)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculando indicadores técnicos: {e}")
            return df
    
    def get_market_summary(self) -> Dict:
        """
        Obtiene un resumen del mercado chileno
        
        Returns:
            Diccionario con resumen del mercado
        """
        logger.info("Generando resumen del mercado...")
        
        current_data = self.get_current_prices()
        
        if current_data.empty:
            return {"error": "No se pudieron obtener datos del mercado"}
        
        # Estadísticas del mercado
        total_stocks = len(current_data)
        gainers = len(current_data[current_data['change_percent'] > 0])
        losers = len(current_data[current_data['change_percent'] < 0])
        unchanged = total_stocks - gainers - losers
        
        # Top performers
        top_gainer = current_data.iloc[0] if not current_data.empty else None
        top_loser = current_data.iloc[-1] if not current_data.empty else None
        
        # Volumen total (donde esté disponible)
        total_volume = current_data['volume'].sum()
        
        summary = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_stocks': total_stocks,
            'gainers': gainers,
            'losers': losers, 
            'unchanged': unchanged,
            'total_volume': int(total_volume),
            'top_gainer': {
                'name': top_gainer['name'] if top_gainer is not None else 'N/A',
                'symbol': top_gainer['symbol'] if top_gainer is not None else 'N/A',
                'change_percent': top_gainer['change_percent'] if top_gainer is not None else 0
            } if top_gainer is not None else None,
            'top_loser': {
                'name': top_loser['name'] if top_loser is not None else 'N/A', 
                'symbol': top_loser['symbol'] if top_loser is not None else 'N/A',
                'change_percent': top_loser['change_percent'] if top_loser is not None else 0
            } if top_loser is not None else None,
            'market_trend': 'Alcista' if gainers > losers else 'Bajista' if losers > gainers else 'Neutral'
        }
        
        logger.info("Resumen del mercado generado exitosamente")
        return summary
    
    def get_market_movers(self, limit: int = 5) -> Dict[str, pd.DataFrame]:
        """
        Obtiene las acciones con mayor movimiento (ganadores y perdedores)
        
        Args:
            limit: Número de acciones por categoría
            
        Returns:
            Diccionario con ganadores y perdedores
        """
        logger.info(f"Obteniendo top {limit} ganadores y perdedores...")
        
        current_data = self.get_current_prices()
        
        if current_data.empty:
            return {"gainers": pd.DataFrame(), "losers": pd.DataFrame()}
        
        # Ordenar por cambio porcentual
        gainers = current_data[current_data['change_percent'] > 0].head(limit)
        losers = current_data[current_data['change_percent'] < 0].tail(limit)
        
        return {
            'gainers': gainers[['name', 'symbol', 'current_price', 'change_percent', 'volume']],
            'losers': losers[['name', 'symbol', 'current_price', 'change_percent', 'volume']]
        }
    
    def get_correlation_matrix(self, symbols: Optional[List[str]] = None, period: str = "6mo") -> pd.DataFrame:
        """
        Calcula matriz de correlación entre acciones
        
        Args:
            symbols: Lista de símbolos
            period: Período de datos
            
        Returns:
            DataFrame con matriz de correlación
        """
        if symbols is None:
            symbols = self.default_stocks[:6]  # Limitar para mejor visualización
            
        logger.info(f"Calculando matriz de correlación para {len(symbols)} acciones")
        
        # Obtener datos históricos
        prices_data = {}
        for symbol in symbols:
            hist = self.get_historical_data(symbol, period)
            if not hist.empty:
                prices_data[self.stock_names.get(symbol, symbol)] = hist['Close']
        
        if not prices_data:
            return pd.DataFrame()
        
        # Crear DataFrame y calcular correlación
        prices_df = pd.DataFrame(prices_data)
        correlation_matrix = prices_df.corr()
        
        return correlation_matrix
    
    def get_sector_performance(self) -> Dict[str, Dict]:
        """
        Obtiene rendimiento por sector
        
        Returns:
            Diccionario con rendimiento por sector
        """
        logger.info("Calculando rendimiento por sectores...")
        
        current_data = self.get_current_prices()
        
        if current_data.empty:
            return {}
        
        sector_data = {}
        
        # Obtener información sectorial para cada acción
        for _, row in current_data.iterrows():
            company_info = self.get_company_info(row['symbol'])
            sector = company_info.get('sector', 'Unknown')
            
            if sector not in sector_data:
                sector_data[sector] = {
                    'companies': [],
                    'total_change': 0,
                    'count': 0,
                    'avg_change': 0
                }
            
            sector_data[sector]['companies'].append({
                'name': row['name'],
                'change_percent': row['change_percent']
            })
            sector_data[sector]['total_change'] += row['change_percent']
            sector_data[sector]['count'] += 1
        
        # Calcular promedios
        for sector in sector_data:
            if sector_data[sector]['count'] > 0:
                sector_data[sector]['avg_change'] = (
                    sector_data[sector]['total_change'] / sector_data[sector]['count']
                )
        
        return sector_data
    
    def get_volatility_ranking(self, period: str = "1mo", custom_symbols: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Obtiene ranking de volatilidad de las acciones
        
        Args:
            period: Período para calcular volatilidad
            custom_symbols: Lista de símbolos personalizados (opcional)
            
        Returns:
            DataFrame con ranking de volatilidad
        """
        symbols = custom_symbols if custom_symbols else self.default_stocks
        logger.info(f"Calculando ranking de volatilidad para período {period}")
        
        volatility_data = []
        
        for symbol in symbols:
            hist = self.get_historical_data(symbol, period)
            if not hist.empty and 'Volatility' in hist.columns:
                current_volatility = hist['Volatility'].iloc[-1]
                avg_volatility = hist['Volatility'].mean()
                
                volatility_data.append({
                    'symbol': symbol,
                    'name': self.stock_names.get(symbol, symbol),
                    'current_volatility': round(current_volatility * 100, 2),
                    'avg_volatility': round(avg_volatility * 100, 2),
                    'volatility_rank': 'High' if current_volatility > 0.3 else 'Medium' if current_volatility > 0.15 else 'Low'
                })
        
        df = pd.DataFrame(volatility_data)
        return df.sort_values('current_volatility', ascending=False)
    
    def get_trading_signals(self, symbol: str, period: str = "3mo") -> Dict:
        """
        Genera señales de trading básicas basadas en indicadores técnicos
        
        Args:
            symbol: Símbolo de la acción
            period: Período de datos
            
        Returns:
            Diccionario con señales de trading
        """
        logger.info(f"Generando señales de trading para {symbol}")
        
        hist = self.get_historical_data(symbol, period)
        
        if hist.empty:
            return {'symbol': symbol, 'error': 'No data available'}
        
        latest = hist.iloc[-1]
        signals = {
            'symbol': symbol,
            'name': self.stock_names.get(symbol, symbol),
            'last_price': round(latest['Close'], 2),
            'signals': []
        }
        
        # Señal de Media Móvil
        if 'SMA_20' in hist.columns and 'SMA_50' in hist.columns:
            if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
                signals['signals'].append({'type': 'Bullish', 'indicator': 'Moving Average', 'strength': 'Strong'})
            elif latest['Close'] > latest['SMA_20']:
                signals['signals'].append({'type': 'Bullish', 'indicator': 'Moving Average', 'strength': 'Moderate'})
            elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
                signals['signals'].append({'type': 'Bearish', 'indicator': 'Moving Average', 'strength': 'Strong'})
        
        # Señal RSI
        if 'RSI' in hist.columns:
            rsi = latest['RSI']
            if rsi > 70:
                signals['signals'].append({'type': 'Bearish', 'indicator': 'RSI', 'strength': 'Overbought', 'value': round(rsi, 2)})
            elif rsi < 30:
                signals['signals'].append({'type': 'Bullish', 'indicator': 'RSI', 'strength': 'Oversold', 'value': round(rsi, 2)})
        
        # Señal MACD
        if 'MACD' in hist.columns and 'MACD_Signal' in hist.columns:
            if latest['MACD'] > latest['MACD_Signal']:
                signals['signals'].append({'type': 'Bullish', 'indicator': 'MACD', 'strength': 'Positive Crossover'})
            else:
                signals['signals'].append({'type': 'Bearish', 'indicator': 'MACD', 'strength': 'Negative Crossover'})
        
        # Señal Bollinger Bands
        if all(col in hist.columns for col in ['BB_Upper', 'BB_Lower']):
            if latest['Close'] > latest['BB_Upper']:
                signals['signals'].append({'type': 'Bearish', 'indicator': 'Bollinger Bands', 'strength': 'Above Upper Band'})
            elif latest['Close'] < latest['BB_Lower']:
                signals['signals'].append({'type': 'Bullish', 'indicator': 'Bollinger Bands', 'strength': 'Below Lower Band'})
        
        return signals

    def save_data_to_csv(self, output_dir: str = "data/processed") -> Dict[str, str]:
        """
        Guarda todos los datos en archivos CSV para análisis posterior
        
        Args:
            output_dir: Directorio de salida
            
        Returns:
            Diccionario con rutas de archivos guardados
        """
        from pathlib import Path
        import os
        
        # Crear directorio si no existe
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Precios actuales
            current_prices = self.get_current_prices()
            if not current_prices.empty:
                filename = f"current_prices_{timestamp}.csv"
                filepath = output_path / filename
                current_prices.to_csv(filepath, index=False)
                saved_files['current_prices'] = str(filepath)
            
            # Datos históricos de acciones principales
            historical_data = self.get_multiple_historical_data(period="1y")
            for symbol, data in historical_data.items():
                if not data.empty:
                    clean_symbol = symbol.replace('.SN', '').replace('-', '_')
                    filename = f"historical_{clean_symbol}_{timestamp}.csv"
                    filepath = output_path / filename
                    data.to_csv(filepath)
                    saved_files[f'historical_{clean_symbol}'] = str(filepath)
            
            # Matriz de correlación
            correlation = self.get_correlation_matrix()
            if not correlation.empty:
                filename = f"correlation_matrix_{timestamp}.csv"
                filepath = output_path / filename
                correlation.to_csv(filepath)
                saved_files['correlation_matrix'] = str(filepath)
            
            # Ranking de volatilidad
            volatility = self.get_volatility_ranking()
            if not volatility.empty:
                filename = f"volatility_ranking_{timestamp}.csv"
                filepath = output_path / filename
                volatility.to_csv(filepath, index=False)
                saved_files['volatility_ranking'] = str(filepath)
            
            logger.info(f"Datos guardados en {len(saved_files)} archivos en {output_path}")
            
        except Exception as e:
            logger.error(f"Error guardando datos: {e}")
        
        return saved_files

    def get_company_info(self, symbol: str) -> Dict:
        """
        Obtiene información detallada de una empresa
        
        Args:
            symbol: Símbolo de la acción
            
        Returns:
            Diccionario con información de la empresa
        """
        try:
            logger.info(f"Obteniendo información de {symbol}")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Datos básicos
            company_data = {
                'symbol': symbol,
                'name': self.stock_names.get(symbol, info.get('longName', symbol)),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'enterprise_value': info.get('enterpriseValue', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'pb_ratio': info.get('priceToBook', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                'eps': info.get('trailingEps', 'N/A'),
                'revenue': info.get('totalRevenue', 'N/A'),
                'profit_margin': info.get('profitMargins', 'N/A'),
                'debt_to_equity': info.get('debtToEquity', 'N/A'),
                'roe': info.get('returnOnEquity', 'N/A'),
                'currency': info.get('currency', 'CLP'),
                'exchange': info.get('exchange', 'SNL'),
                'website': info.get('website', 'N/A'),
                'business_summary': info.get('longBusinessSummary', 'N/A')
            }
            
            logger.info(f"Información de {symbol} obtenida exitosamente")
            return company_data
            
        except Exception as e:
            logger.error(f"Error obteniendo información de {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}
        """
        Obtiene información detallada de una empresa
        
        Args:
            symbol: Símbolo de la acción
            
        Returns:
            Diccionario con información de la empresa
        """
        try:
            logger.info(f"Obteniendo información de {symbol}")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Datos básicos
            company_data = {
                'symbol': symbol,
                'name': self.stock_names.get(symbol, info.get('longName', symbol)),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'enterprise_value': info.get('enterpriseValue', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'pb_ratio': info.get('priceToBook', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                'eps': info.get('trailingEps', 'N/A'),
                'revenue': info.get('totalRevenue', 'N/A'),
                'profit_margin': info.get('profitMargins', 'N/A'),
                'debt_to_equity': info.get('debtToEquity', 'N/A'),
                'roe': info.get('returnOnEquity', 'N/A'),
                'currency': info.get('currency', 'CLP'),
                'exchange': info.get('exchange', 'SNL'),
                'website': info.get('website', 'N/A'),
                'business_summary': info.get('longBusinessSummary', 'N/A')
            }
            
            logger.info(f"Información de {symbol} obtenida exitosamente")
            return company_data
            
        except Exception as e:
            logger.error(f"Error obteniendo información de {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

# Función de utilidad para ejecutar el módulo directamente
def main():
    """Función principal para probar el módulo"""
    extractor = YahooFinanceDataExtractor()
    
    print("=== RESUMEN DEL MERCADO ===")
    market_summary = extractor.get_market_summary()
    print(f"Acciones analizadas: {market_summary['total_stocks']}")
    print(f"Subiendo: {market_summary['gainers']}")
    print(f"Bajando: {market_summary['losers']}")
    print(f"Tendencia: {market_summary['market_trend']}")
    
    if market_summary['top_gainer']:
        print(f"Mayor subida: {market_summary['top_gainer']['name']} ({market_summary['top_gainer']['change_percent']:.2f}%)")
    
    print("\n=== TOP 3 GANADORES Y PERDEDORES ===")
    movers = extractor.get_market_movers(limit=3)
    
    print("\nGanadores:")
    if not movers['gainers'].empty:
        for _, row in movers['gainers'].iterrows():
            print(f"  {row['name']}: +{row['change_percent']:.2f}%")
    
    print("\nPerdedores:")
    if not movers['losers'].empty:
        for _, row in movers['losers'].iterrows():
            print(f"  {row['name']}: {row['change_percent']:.2f}%")
    
    print("\n=== RANKING DE VOLATILIDAD ===")
    volatility = extractor.get_volatility_ranking()
    if not volatility.empty:
        print(volatility[['name', 'current_volatility', 'volatility_rank']].head().to_string(index=False))
    
    print("\n=== SEÑALES DE TRADING (SQM) ===")
    signals = extractor.get_trading_signals("SQM-B.SN")
    if 'signals' in signals:
        print(f"Precio actual: ${signals['last_price']}")
        for signal in signals['signals']:
            print(f"  {signal['type']} - {signal['indicator']}: {signal['strength']}")
    
    print("\n=== GUARDANDO DATOS ===")
    saved_files = extractor.save_data_to_csv()
    print(f"Archivos guardados: {len(saved_files)}")
    for file_type, filepath in saved_files.items():
        print(f"  {file_type}: {filepath}")


if __name__ == "__main__":
    main()