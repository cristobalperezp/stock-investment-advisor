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
from pathlib import Path
import json
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suprimir advertencias de yfinance
warnings.filterwarnings('ignore', category=FutureWarning)


class YahooFinanceDataExtractor:
    """
    Extractor de datos financieros desde Yahoo Finance
    Optimizado para acciones del mercado chileno con sistema de caché diario
    """
    
    def __init__(self):
        self.default_stocks = [
            "SQM-B.SN",      # SQM
            "FALABELLA.SN",  # Falabella
            "CENCOSUD.SN",   # Cencosud
            "COPEC.SN",      # Copec
            "CCU.SN",        # CCU
            "CHILE.SN",      # Banco de Chile
            "BSANTANDER.SN",  # Santander
            "ENELCHILE.SN",  # Enel Chile
            "COLBUN.SN",     # Colbún
            "AGUAS-A.SN"     # Aguas Andinas
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
        
        # Configuración de caché
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cleanup_old_cache_files()
    
    def _cleanup_old_cache_files(self):
        """Limpia archivos de caché antiguos (más de 7 días)"""
        try:
            if not self.cache_dir.exists():
                return
            
            current_time = time.time()
            for cache_file in self.cache_dir.glob("*.csv"):
                if current_time - cache_file.stat().st_mtime > 7 * 24 * 3600:
                    cache_file.unlink()
                    logger.info(f"Archivo de caché eliminado: {cache_file.name}")
        except Exception as e:
            logger.warning(f"Error limpiando caché: {e}")
    
    def _get_cache_filename(self, data_type: str, symbols: str = "default") -> str:
        """Genera nombre de archivo de caché basado en fecha y tipo de datos"""
        today = datetime.now().strftime('%Y%m%d')
        return f"{data_type}_{symbols}_{today}.csv"
    
    def _load_from_cache(self, cache_filename: str) -> Optional[pd.DataFrame]:
        """Carga datos desde el caché si existe"""
        cache_path = self.cache_dir / cache_filename
        if cache_path.exists():
            try:
                logger.info(f"Cargando desde caché: {cache_filename}")
                return pd.read_csv(cache_path, index_col=0, parse_dates=True)
            except Exception as e:
                logger.warning(f"Error cargando caché {cache_filename}: {e}")
        return None
    
    def _save_to_cache(self, data: pd.DataFrame, cache_filename: str):
        """Guarda datos en el caché"""
        try:
            cache_path = self.cache_dir / cache_filename
            data.to_csv(cache_path)
            logger.info(f"Datos guardados en caché: {cache_filename}")
        except Exception as e:
            logger.warning(f"Error guardando en caché {cache_filename}: {e}")
    
    def get_cache_info(self) -> Dict:
        """Obtiene información sobre el estado del caché"""
        try:
            cache_files = list(self.cache_dir.glob("*.csv"))
            total_size = sum(f.stat().st_size for f in cache_files) / (1024 * 1024)
            
            files_info = []
            for cache_file in sorted(cache_files, key=lambda f: f.stat().st_mtime, reverse=True):
                stat = cache_file.stat()
                files_info.append({
                    'filename': cache_file.name,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return {
                'cache_directory': str(self.cache_dir),
                'total_files': len(cache_files),
                'total_size_mb': round(total_size, 2),
                'files': files_info[:10]  # Mostrar solo los 10 más recientes
            }
        except Exception as e:
            logger.error(f"Error obteniendo información de caché: {e}")
            return {'error': str(e)}
    
    def get_current_prices(self, symbols: Optional[List[str]] = None,
                          use_cache: bool = True) -> pd.DataFrame:
        """
        Obtiene precios actuales de las acciones con sistema de caché inteligente
        
        Args:
            symbols: Lista de símbolos de acciones
            use_cache: Si usar el sistema de caché diario
            
        Returns:
            DataFrame con precios actuales
        """
        if symbols is None:
            symbols = self.default_stocks
        
        if not use_cache:
            # Descargar todo sin caché
            logger.info(f"Descargando precios actuales para {len(symbols)} acciones...")
            return self._download_all_prices(symbols, use_cache=False)
        
        # Buscar caché existente y determinar qué acciones faltan
        cached_data, missing_symbols = self._get_cached_prices_and_missing(symbols)
        
        if not missing_symbols:
            # Todas las acciones están en caché
            logger.info(f"Todos los precios cargados desde caché ({len(symbols)} acciones)")
            return cached_data[cached_data['symbol'].isin(symbols)].reset_index(drop=True)
        
        # Descargar solo las acciones faltantes
        if cached_data is not None and len(missing_symbols) < len(symbols):
            logger.info(f"Caché parcial encontrado. Descargando {len(missing_symbols)} acciones nuevas...")
            new_data = self._download_all_prices(missing_symbols, use_cache=False)
            
            if not new_data.empty:
                # Combinar datos existentes con nuevos
                combined_data = pd.concat([cached_data, new_data], ignore_index=True)
                
                # Guardar caché actualizado con todas las acciones
                all_symbols_str = "_".join(sorted(list(set(symbols + list(cached_data['symbol'])))))
                new_cache_filename = self._get_cache_filename("current_prices", all_symbols_str)
                self._save_to_cache(combined_data, new_cache_filename)
                
                # Retornar solo las acciones solicitadas
                return combined_data[combined_data['symbol'].isin(symbols)].reset_index(drop=True)
        
        # Si no hay caché útil, descargar todo
        logger.info(f"Descargando precios actuales para {len(symbols)} acciones...")
        return self._download_all_prices(symbols, use_cache=True)
    
    def _get_cached_prices_and_missing(self, requested_symbols: List[str]) -> tuple:
        """
        Busca en el caché y determina qué acciones faltan
        
        Returns:
            tuple: (cached_dataframe, missing_symbols_list)
        """
        cache_files = list(self.cache_dir.glob("current_prices_*_20250908.csv"))
        
        best_match = None
        best_coverage = 0
        
        for cache_file in cache_files:
            try:
                cached_df = pd.read_csv(cache_file, index_col=0)
                if 'symbol' in cached_df.columns:
                    cached_symbols = set(cached_df['symbol'].tolist())
                    coverage = len(set(requested_symbols) & cached_symbols)
                    
                    if coverage > best_coverage:
                        best_coverage = coverage
                        best_match = cached_df
                        
            except Exception as e:
                logger.warning(f"Error leyendo caché {cache_file.name}: {e}")
                continue
        
        if best_match is not None:
            cached_symbols = set(best_match['symbol'].tolist())
            missing_symbols = [s for s in requested_symbols if s not in cached_symbols]
            logger.info(f"Caché encontrado: {len(cached_symbols)} acciones, faltan {len(missing_symbols)}")
            return best_match, missing_symbols
        
        return None, requested_symbols
    
    def _download_all_prices(self, symbols: List[str], use_cache: bool = True) -> pd.DataFrame:
        """
        Descarga precios para todas las acciones especificadas
        """
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
        
        # Guardar en caché para futuros usos
        if use_cache and not df.empty:
            symbols_str = "_".join(sorted(symbols))
            cache_filename = self._get_cache_filename("current_prices", symbols_str)
            self._save_to_cache(df, cache_filename)
        
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
                                     period: str = "3mo",
                                     use_cache: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Obtiene datos históricos de múltiples acciones con caché inteligente
        
        Args:
            symbols: Lista de símbolos
            period: Período de datos
            use_cache: Si usar el sistema de caché diario
            
        Returns:
            Diccionario con DataFrames de datos históricos
        """
        if symbols is None:
            symbols = self.default_stocks
        
        if not use_cache:
            # Descargar todo sin caché
            return self._download_all_historical(symbols, period, use_cache=False)
        
        # Buscar caché existente y determinar qué acciones faltan
        cached_data, missing_symbols = self._get_cached_historical_and_missing(symbols, period)
        
        if not missing_symbols:
            # Todas las acciones están en caché
            logger.info(f"Todos los datos históricos cargados desde caché ({len(symbols)} acciones)")
            return {k: v for k, v in cached_data.items() if k in symbols}
        
        # Descargar solo las acciones faltantes
        if cached_data and len(missing_symbols) < len(symbols):
            logger.info(f"Caché histórico parcial encontrado. Descargando {len(missing_symbols)} acciones nuevas...")
            new_data = self._download_all_historical(missing_symbols, period, use_cache=False)
            
            if new_data:
                # Combinar datos existentes con nuevos
                combined_data = {**cached_data, **new_data}
                
                # Guardar caché actualizado
                all_symbols_str = "_".join(sorted(list(set(symbols + list(cached_data.keys())))))
                cache_filename = self._get_cache_filename(f"historical_{period}", all_symbols_str)
                self._save_historical_cache(combined_data, cache_filename)
                
                # Retornar solo las acciones solicitadas
                return {k: v for k, v in combined_data.items() if k in symbols}
        
        # Si no hay caché útil, descargar todo
        return self._download_all_historical(symbols, period, use_cache=True)
    
    def _get_cached_historical_and_missing(self, requested_symbols: List[str], period: str) -> tuple:
        """
        Busca en el caché histórico y determina qué acciones faltan
        """
        cache_pattern = f"historical_{period}_*_20250908.csv"
        cache_files = list(self.cache_dir.glob(cache_pattern))
        
        best_match = None
        best_coverage = 0
        
        for cache_file in cache_files:
            try:
                import pickle
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                
                if isinstance(cached_data, dict):
                    cached_symbols = set(cached_data.keys())
                    coverage = len(set(requested_symbols) & cached_symbols)
                    
                    if coverage > best_coverage:
                        best_coverage = coverage
                        best_match = cached_data
                        
            except Exception as e:
                logger.warning(f"Error leyendo caché histórico {cache_file.name}: {e}")
                continue
        
        if best_match is not None:
            cached_symbols = set(best_match.keys())
            missing_symbols = [s for s in requested_symbols if s not in cached_symbols]
            logger.info(f"Caché histórico encontrado: {len(cached_symbols)} acciones, faltan {len(missing_symbols)}")
            return best_match, missing_symbols
        
        return {}, requested_symbols
    
    def _download_all_historical(self, symbols: List[str], period: str, use_cache: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Descarga datos históricos para todas las acciones especificadas
        """
        logger.info(f"Descargando datos históricos de {len(symbols)} acciones")
        
        historical_data = {}
        
        def get_single_historical(symbol):
            return symbol, self.get_historical_data(symbol, period)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(get_single_historical, symbol): symbol
                      for symbol in symbols}
            
            for future in as_completed(futures):
                symbol, data = future.result()
                if not data.empty:
                    historical_data[symbol] = data
        
        # Guardar en caché
        if use_cache and historical_data:
            symbols_str = "_".join(sorted(symbols))
            cache_filename = self._get_cache_filename(f"historical_{period}", symbols_str)
            self._save_historical_cache(historical_data, cache_filename)
        
        return historical_data
    
    def _save_historical_cache(self, data: Dict[str, pd.DataFrame], cache_filename: str):
        """
        Guarda datos históricos en el caché usando pickle
        """
        try:
            cache_path = self.cache_dir / cache_filename
            import pickle
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Datos históricos guardados en caché: {cache_filename}")
        except Exception as e:
            logger.warning(f"Error guardando caché histórico: {e}")

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
    
    def get_market_summary(self, use_cache: bool = True) -> Dict:
        """
        Obtiene un resumen del mercado chileno con caché
        
        Args:
            use_cache: Si usar el sistema de caché diario
            
        Returns:
            Diccionario con resumen del mercado
        """
        cache_filename = self._get_cache_filename("market_summary", "default")
        
        # Intentar cargar desde caché
        if use_cache:
            cache_path = self.cache_dir / cache_filename.replace('.csv', '.json')
            if cache_path.exists():
                try:
                    logger.info("Cargando resumen del mercado desde caché")
                    import json
                    with open(cache_path, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"Error cargando caché de resumen: {e}")
        
        logger.info("Generando resumen del mercado...")
        
        current_data = self.get_current_prices(use_cache=use_cache)
        
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
        
        # Guardar en caché
        if use_cache:
            try:
                cache_path = self.cache_dir / cache_filename.replace('.csv', '.json')
                import json
                with open(cache_path, 'w') as f:
                    json.dump(summary, f)
                logger.info(f"Resumen del mercado guardado en caché")
            except Exception as e:
                logger.warning(f"Error guardando caché de resumen: {e}")
        
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
    
    def get_sector_performance(self, use_cache: bool = True) -> Dict[str, Dict]:
        """
        Obtiene rendimiento por sector con caché
        
        Args:
            use_cache: Si usar el sistema de caché diario
            
        Returns:
            Diccionario con rendimiento por sector
        """
        cache_filename = self._get_cache_filename("sector_performance", "default")
        
        # Intentar cargar desde caché
        if use_cache:
            cache_path = self.cache_dir / cache_filename.replace('.csv', '.json')
            if cache_path.exists():
                try:
                    logger.info("Cargando rendimiento sectorial desde caché")
                    with open(cache_path, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"Error cargando caché sectorial: {e}")
        
        logger.info("Calculando rendimiento por sectores...")
        
        current_data = self.get_current_prices(use_cache=use_cache)
        
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
        
        # Guardar en caché
        if use_cache and sector_data:
            try:
                cache_path = self.cache_dir / cache_filename.replace('.csv', '.json')
                with open(cache_path, 'w') as f:
                    json.dump(sector_data, f)
                logger.info("Rendimiento sectorial guardado en caché")
            except Exception as e:
                logger.warning(f"Error guardando caché sectorial: {e}")
        
        return sector_data
        
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
                'name': self.stock_names.get(
                    symbol, info.get('longName', symbol)
                ),
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
        print(
            f"Mayor subida: {market_summary['top_gainer']['name']} "
            f"({market_summary['top_gainer']['change_percent']:.2f}%)"
        )
    
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
        print(
            volatility[[
                'name', 'current_volatility', 'volatility_rank'
            ]].head().to_string(index=False)
        )
    
    print("\n=== SEÑALES DE TRADING (SQM) ===")
    signals = extractor.get_trading_signals("SQM-B.SN")
    if 'signals' in signals:
        print(f"Precio actual: ${signals['last_price']}")
        for signal in signals['signals']:
            print(
                f"  {signal['type']} - {signal['indicator']}: "
                f"{signal['strength']}"
            )
    
    print("\n=== GUARDANDO DATOS ===")
    saved_files = extractor.save_data_to_csv()
    print(f"Archivos guardados: {len(saved_files)}")
    for file_type, filepath in saved_files.items():
        print(f"  {file_type}: {filepath}")


  
if __name__ == "__main__":
    main()
