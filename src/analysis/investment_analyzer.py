"""
Módulo de análisis de inversiones basado en datos fundamentales
Implementa la lógica del notebook analyst_2.ipynb
"""

import pandas as pd
import numpy as np
import yfinance as yf
import time
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Importar configuración de acciones normalizada
try:
    from config.stocks_config import (
        ALL_CHILEAN_STOCKS,
        CHILEAN_STOCKS_BY_SECTOR,
        STOCK_NAMES,
        get_stock_name,
        get_sector_for_stock,
        DEFAULT_ANALYSIS_CONFIG
    )
    STOCKS_CONFIG_AVAILABLE = True
except ImportError:
    STOCKS_CONFIG_AVAILABLE = False
    logging.warning("Configuración de acciones no disponible")

# OpenAI import with error handling
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI no disponible. Análisis GPT deshabilitado.")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvestmentAnalyzer:
    """Analizador de inversiones para acciones chilenas"""
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.fundamental_data = None
        self.portfolio_weights = None
        
        # Usar configuración normalizada si está disponible
        if STOCKS_CONFIG_AVAILABLE:
            self.chilean_stocks = CHILEAN_STOCKS_BY_SECTOR
            self.all_tickers = ALL_CHILEAN_STOCKS
            logger.info(f"Usando configuración normalizada: {len(self.all_tickers)} acciones")
        else:
            # Fallback a la configuración original
            self.chilean_stocks = {
                # Banca
                "Banca": ["BSANTANDER.SN", "BCI.SN", "CHILE.SN", "BICECORP.SN", "ITAUCL.SN"],
                # Retail
                "Retail": ["FALABELLA.SN", "RIPLEY.SN", "CENCOSUD.SN", "FORUS.SN", "SMU.SN", "TRICOT.SN"],
                # Servicios
                "Servicios": ["ENELCHILE.SN", "COLBUN.SN", "AGUAS-A.SN", "GASCO.SN", "COPEC.SN", "ECL.SN"],
                # Embotellados
                "Embotellados": ["EMBONOR-B.SN", "CONCHATORO.SN", "CCU.SN"],
                # AFP
                "AFP": ["HABITAT.SN", "PROVIDA.SN", "PLANVITAL.SN"],
                # Inmobiliario
                "Inmobiliario": ["CENCOMALLS.SN", "MALLPLAZA.SN", "PARAUCO.SN"],
                # Aerolineas
                "Transporte": ["LTM.SN"],
                # Otros
                "Otros": ["CMPC.SN", "SQM-B.SN"]
            }
            
            # Obtener lista plana de todos los tickers
            self.all_tickers = []
            for sector_stocks in self.chilean_stocks.values():
                self.all_tickers.extend(sector_stocks)
            logger.info(f"Usando configuración por defecto: {len(self.all_tickers)} acciones")
    
    def get_fundamental_data(self, ticker: str) -> Optional[Dict]:
        """
        Obtiene datos fundamentales de una acción chilena desde Yahoo Finance
        Basado en la función obtener_datos_fundamentales del notebook
        """
        try:
            # logger.info(f"Obteniendo datos para {ticker}")
            time.sleep(1)  # Evitar rate limiting
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Histórico para cálculo de variaciones
            hist_6m = stock.history(period="6mo")
            hist_1m = stock.history(period="1mo")
            hist_1y = stock.history(period="1y")
            
            def calcular_variacion(hist):
                if len(hist) >= 2:
                    precio_inicial = hist["Close"].iloc[0]
                    precio_final = hist["Close"].iloc[-1]
                    return (precio_final - precio_inicial) / precio_inicial
                else:
                    return np.nan
            
            variacion_1m = calcular_variacion(hist_1m)
            variacion_6m = calcular_variacion(hist_6m)
            variacion_1y = calcular_variacion(hist_1y)
            
            # Análisis de dividendos
            dividendos = stock.dividends.tail(4)
            frecuencia = dividendos.index.to_series().diff().mean().days / 30 if not dividendos.empty else np.nan
            
            previous_close = info.get("previousClose", np.nan)
            dividend_yield = info.get("dividendYield", np.nan)
            
            # Calcular dividend per share
            div_share = (
                list(dividendos.values)[-1] / previous_close
                if dividend_yield and previous_close and not dividendos.empty
                else np.nan
            )            # Métricas de flujo de efectivo
            operating_cashflow = info.get("operatingCashflow", np.nan)
            total_debt = info.get("totalDebt", np.nan)
            cash_flow_to_debt_ratio = (
                operating_cashflow / total_debt
                if total_debt and not np.isnan(operating_cashflow)
                else np.nan
            )            # Volatilidad
            volatilidad = hist_6m["Close"].pct_change().std() * np.sqrt(252) if len(hist_6m) > 1 else np.nan
            
            datos = {
                "Ticker": ticker,
                "Empresa": info.get("shortName", ticker.replace(".SN", "")),
                "Sector": self.get_sector(ticker),
                "Valor_Accion": previous_close,
                "Precio_Actual": previous_close,  # Alias para compatibilidad
                "Variacion_1M": variacion_1m,
                "Variacion_6M": variacion_6m,
                "Variacion_1Y": variacion_1y,
                "Volatilidad": volatilidad,
                "Div_Share": div_share,
                "ROE": info.get("returnOnEquity", np.nan),
                "PE_Ratio": info.get("trailingPE", np.nan),
                "Margen_Beneficio": info.get("profitMargins", np.nan),
                "Deuda_Capital": info.get("debtToEquity", np.nan),
                "Crecimiento_Ingresos": info.get("revenueGrowth", np.nan),
                "Crecimiento_Beneficios": info.get("earningsGrowth", np.nan),
                "Operating_Cash_Flow": operating_cashflow,
                "Total_Debt": total_debt,
                "Cash_Flow_Debt_Ratio": cash_flow_to_debt_ratio,
                "Cash_Flow_to_Debt_Ratio": cash_flow_to_debt_ratio,  # Alias para compatibilidad
                "Beta": info.get("beta", np.nan),
                "Paga_Dividendos": "Sí" if dividend_yield else "No",
                "Ultimos_Dividendos": list(dividendos.values) if not dividendos.empty else [],
                "Frecuencia_Dividendos": frecuencia,
                "Dividend_Yield": dividend_yield,
                "Market_Cap": info.get("marketCap", np.nan),
                "Volume": info.get("volume", np.nan),
                "Avg_Volume": info.get("averageVolume", np.nan)
            }
            
            return datos
            
        except Exception as e:
            logger.error(f"Error obteniendo datos para {ticker}: {e}")
            return None
    
    def get_sector(self, ticker: str) -> str:
        """Obtiene el sector de un ticker"""
        if STOCKS_CONFIG_AVAILABLE:
            return get_sector_for_stock(ticker)
        else:
            # Fallback a búsqueda manual
            for sector, tickers in self.chilean_stocks.items():
                if ticker in tickers:
                    return sector
            return "Otros"
    
    def _get_risk_adjusted_weights(
        self, risk_level: str, dividend_preference: bool
    ) -> Dict[str, float]:
        """
        Obtiene pesos ajustados según nivel de riesgo y preferencias
        
        Args:
            risk_level: "conservador", "moderado", "agresivo"
            dividend_preference: Si priorizar dividendos
        """
        base_weights = {
            "ROE": 0.15,
            "PE_Ratio": 0.10,
            "Crecimiento_Ingresos": 0.10,
            "Crecimiento_Beneficios": 0.15,
            "Beta": 0.05,
            "Cash_Flow_Debt_Ratio": 0.15,
            "Dividend_Yield": 0.15,
            "Div_Share": 0.10,
            "Variacion_1M": 0.02,
            "Variacion_6M": 0.03,
            "Volatilidad": 0.00
        }
        
        # Ajustar según nivel de riesgo
        if risk_level.lower() == "conservador":
            # Conservador: Priorizar estabilidad y dividendos
            base_weights["Dividend_Yield"] = 0.25
            base_weights["Cash_Flow_Debt_Ratio"] = 0.20
            base_weights["Beta"] = 0.02  # Menos peso a beta alta
            base_weights["Volatilidad"] = 0.02  # Penalizar volatilidad
            base_weights["Crecimiento_Beneficios"] = 0.10
            base_weights["ROE"] = 0.15
            
        elif risk_level.lower() == "agresivo":
            # Agresivo: Priorizar crecimiento y retornos
            base_weights["Crecimiento_Beneficios"] = 0.25
            base_weights["Crecimiento_Ingresos"] = 0.15
            base_weights["Variacion_6M"] = 0.08
            base_weights["Variacion_1M"] = 0.05
            base_weights["ROE"] = 0.20
            base_weights["Dividend_Yield"] = 0.10
            
        # Ajustar según preferencia de dividendos
        if dividend_preference:
            base_weights["Dividend_Yield"] += 0.05
            base_weights["Div_Share"] += 0.03
            # Reducir otros pesos proporcionalmente
            base_weights["Crecimiento_Ingresos"] -= 0.03
            base_weights["Variacion_1M"] -= 0.02
            base_weights["Variacion_6M"] -= 0.03
        
        return base_weights
    
    def get_cache_info(self) -> Dict:
        """Obtiene información sobre los archivos de caché disponibles"""
        try:
            data_dir = Path("data/processed")
            if not data_dir.exists():
                return {"cache_available": False, "message": "Directorio de datos no existe"}
            
            today = datetime.now().strftime("%Y%m%d")
            today_files = list(data_dir.glob(f"fundamental_data_{today}_*.csv"))
            
            if today_files:
                latest_file = max(today_files, key=lambda x: x.stat().st_mtime)
                file_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
                
                return {
                    "cache_available": True,
                    "filename": latest_file.name,
                    "file_time": file_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "file_size": f"{latest_file.stat().st_size / 1024:.1f} KB",
                    "message": f"Datos del día disponibles desde {file_time.strftime('%H:%M')}"
                }
            else:
                return {
                    "cache_available": False,
                    "message": "No hay datos del día actual, se descargarán datos frescos"
                }
                
        except Exception as e:
            return {
                "cache_available": False,
                "message": f"Error verificando caché: {str(e)}"
            }

    def _cleanup_old_data_files(self, days_to_keep: int = 7):
        """Limpia archivos de datos fundamentales antiguos"""
        try:
            data_dir = Path("data/processed")
            if not data_dir.exists():
                return
            
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff_date.strftime("%Y%m%d")
            
            # Buscar archivos antiguos
            old_files = []
            for file in data_dir.glob("fundamental_data_*.csv"):
                # Extraer fecha del nombre del archivo
                try:
                    date_part = file.stem.split('_')[2]  # fundamental_data_YYYYMMDD_HHMMSS
                    if date_part < cutoff_str:
                        old_files.append(file)
                except (IndexError, ValueError):
                    continue
            
            # Eliminar archivos antiguos
            for file in old_files:
                try:
                    file.unlink()
                    logger.info(f"Archivo antiguo eliminado: {file.name}")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar {file.name}: {e}")
                    
        except Exception as e:
            logger.warning(f"Error en limpieza de archivos: {e}")

    def download_all_fundamental_data(self) -> pd.DataFrame:
        """Descarga datos fundamentales para todas las acciones con caché diario"""
        
        # Limpiar archivos antiguos primero
        self._cleanup_old_data_files()
        
        # Verificar si ya existen datos de hoy
        today = datetime.now().strftime("%Y%m%d")
        data_dir = Path("data/processed")
        
        # Buscar archivo de datos fundamentales de hoy
        existing_files = list(data_dir.glob(f"fundamental_data_{today}_*.csv"))
        
        if existing_files:
            # Usar el archivo más reciente del día
            latest_file = max(existing_files, key=lambda x: x.stat().st_mtime)
            logger.info(f"📁 Reutilizando datos del día: {latest_file.name}")
            
            try:
                df = pd.read_csv(latest_file)
                self.fundamental_data = df
                logger.info(f"✅ Datos cargados desde caché: {len(df)} empresas")
                return df
            except Exception as e:
                logger.warning(f"⚠️ Error cargando caché: {e}. Descargando...")
        
        # Si no hay datos del día o hubo error, descargar datos frescos
        logger.info("🔄 Descargando datos fundamentales para todas las acciones...")
        
        fundamental_data = []
        for ticker in self.all_tickers:
            data = self.get_fundamental_data(ticker)
            if data:
                fundamental_data.append(data)
        
        df = pd.DataFrame(fundamental_data)
        
        # Guardar datos con timestamp del día
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"data/processed/fundamental_data_{timestamp}.csv"
        df.to_csv(filepath, index=False)
        logger.info(f"💾 Datos guardados en: {filepath}")
        
        self.fundamental_data = df
        return df
    
    def calculate_portfolio_weights(
        self, df: pd.DataFrame, risk_level: str = "moderado",
        dividend_preference: bool = True
    ) -> pd.DataFrame:
        """
        Optimiza la asignación de activos basándose en datos fundamentales
        Basado en la función construir_portafolio del notebook
        
        Args:
            df: DataFrame con datos fundamentales
            risk_level: Nivel de riesgo ("conservador", "moderado", "agresivo")
            dividend_preference: Si priorizar empresas con dividendos
        """
        df_clean = df.copy()
        
        # Filtrar por preferencia de dividendos
        if dividend_preference:
            # Convertir a string para evitar problemas de comparación
            df_clean['Paga_Dividendos'] = df_clean['Paga_Dividendos'].astype(
                str
            )
            df_clean = df_clean[df_clean['Paga_Dividendos'] == 'Sí'].copy()
            if df_clean.empty:
                logger.warning(
                    "No hay empresas con dividendos, usando todas las empresas"
                )
                df_clean = df.copy()
        
        # Calcular dividend yield si falta
        df_clean['Dividend_Yield'] = df_clean.apply(
            lambda row: (
                row['Ultimos_Dividendos'][-1] / row['Valor_Accion']
                if (pd.isna(row['Dividend_Yield']) and
                    isinstance(row['Ultimos_Dividendos'], list) and
                    len(row['Ultimos_Dividendos']) > 0)
                else row['Dividend_Yield']
            ), axis=1
        )
        
        # Rellenar valores faltantes
        numeric_columns = [
            "ROE", "PE_Ratio", "Crecimiento_Ingresos", "Crecimiento_Beneficios", 
            "Beta", "Cash_Flow_Debt_Ratio", "Dividend_Yield", "Div_Share", 
            "Variacion_1M", "Variacion_6M", "Volatilidad"
        ]
        
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                df_clean[col] = df_clean[col].replace([np.inf, -np.inf], np.nan)
                df_clean[col] = df_clean[col].fillna(0)
        
        # Normalizar métricas
        columns_to_scale = [col for col in numeric_columns 
                           if col in df_clean.columns]
        
        # Ajustar pesos según nivel de riesgo
        pesos_dict = self._get_risk_adjusted_weights(risk_level, dividend_preference)
        
        if len(columns_to_scale) > 0:
            datos_normalizados = self.scaler.fit_transform(
                df_clean[columns_to_scale]
            )
            # Construir pesos solo para las columnas presentes
            pesos_multiplicadores = np.array([
                pesos_dict[col] for col in columns_to_scale
            ])
            pesos_multiplicadores = (pesos_multiplicadores / 
                                   pesos_multiplicadores.sum())
            puntajes = datos_normalizados @ pesos_multiplicadores
            
            # Crear DataFrame con resultados
            puntajes_df = pd.DataFrame({
                'Ticker': df_clean['Ticker'].values,
                'Empresa': df_clean['Empresa'].values,
                'Sector': df_clean['Sector'].values,
                'Puntaje': puntajes
            })
            
            # Normalizar pesos para que sumen 1
            puntajes_df['Peso_Asignado'] = puntajes_df['Puntaje'] / puntajes_df['Puntaje'].sum()
            
            # Guardar resultados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/processed/portfolio_weights_{timestamp}.csv"
            puntajes_df.to_csv(filepath, index=False)
            # logger.info(f"Pesos del portafolio guardados en {filepath}")
            
            self.portfolio_weights = puntajes_df
            return puntajes_df
        
        else:
            logger.error("No hay columnas válidas para el cálculo de pesos")
            # Crear un DataFrame básico con pesos iguales
            pesos_iguales = 1.0 / len(df_clean)
            puntajes_df = pd.DataFrame({
                'Ticker': df_clean['Ticker'].values,
                'Empresa': df_clean['Empresa'].values,
                'Sector': df_clean['Sector'].values,
                'Puntaje': [pesos_iguales] * len(df_clean),
                'Peso_Asignado': [pesos_iguales] * len(df_clean)
            })
            
            self.portfolio_weights = puntajes_df
            return puntajes_df
    
    def generate_investment_recommendations(self, 
                                          budget: float = 1000000,
                                          min_companies: int = 10,
                                          min_investment: float = 20000) -> Dict:
        """
        Genera recomendaciones de inversión basadas en el análisis
        """
        if self.fundamental_data is None or self.portfolio_weights is None:
            raise ValueError("Debe ejecutar el análisis completo primero")
        
        # Filtrar solo empresas que pagan dividendos
        # Asegurar que la columna sea string antes de la comparación
        self.fundamental_data['Paga_Dividendos'] = (
            self.fundamental_data['Paga_Dividendos'].astype(str)
        )
        dividend_companies = self.fundamental_data[
            self.fundamental_data['Paga_Dividendos'] == 'Sí'
        ].copy()
        
        if len(dividend_companies) == 0:
            raise ValueError("No se encontraron empresas que paguen dividendos")
        
        # Obtener pesos correspondientes
        weights = self.portfolio_weights[
            self.portfolio_weights['Ticker'].isin(dividend_companies['Ticker'])
        ].copy()
        
        # Validar y limpiar la columna Peso_Asignado antes del sort
        if not weights.empty:
            # Convertir a numérico y manejar errores
            weights['Peso_Asignado'] = pd.to_numeric(
                weights['Peso_Asignado'], errors='coerce'
            )
            # Eliminar filas con pesos inválidos
            weights = weights.dropna(subset=['Peso_Asignado'])
            
            if weights.empty:
                logger.error("Todos los pesos son inválidos después de limpieza")
                # Crear pesos iguales como fallback
                weights = self.portfolio_weights[
                    self.portfolio_weights['Ticker'].isin(dividend_companies['Ticker'])
                ].copy()
                equal_weight = 1.0 / len(weights) if not weights.empty else 0.0
                weights['Peso_Asignado'] = equal_weight
        
        # Ordenar por peso descendente
        weights = weights.sort_values('Peso_Asignado', ascending=False)
        
        # Seleccionar top empresas basado en min_companies
        num_companies = min(max(min_companies, 5), len(weights))  # Mínimo 5, máximo disponible
        top_companies = weights.head(num_companies).copy()
        
        # Calcular distribución proporcional al presupuesto real
        total_weight = top_companies['Peso_Asignado'].sum()
        
        # Calcular porcentajes normalizados
        top_companies['Porcentaje_Recomendado'] = (
            top_companies['Peso_Asignado'] / total_weight * 100
        )
        
        # Calcular montos de inversión basados en el presupuesto REAL
        top_companies['Monto_Inversion'] = (
            top_companies['Porcentaje_Recomendado'] / 100 * budget
        )
        
        # Redondear a miles más cercanos
        top_companies['Monto_Inversion'] = (
            top_companies['Monto_Inversion'] / 1000
        ).round() * 1000
        
        # Asegurar inversión mínima sin alterar el presupuesto total
        mask_low = top_companies['Monto_Inversion'] < min_investment
        if mask_low.any():
            # Redistribuir para mantener el presupuesto total
            low_count = mask_low.sum()
            high_companies = ~mask_low
            
            if high_companies.any():
                # Calcular déficit por inversiones bajas
                deficit = (min_investment * low_count) - top_companies.loc[mask_low, 'Monto_Inversion'].sum()
                remaining_budget = budget - (min_investment * low_count)
                
                # Asignar mínimo a las empresas bajas
                top_companies.loc[mask_low, 'Monto_Inversion'] = min_investment
                
                # Redistribuir el resto proporcionalmente
                if remaining_budget > 0 and high_companies.sum() > 0:
                    high_weights = top_companies.loc[high_companies, 'Peso_Asignado']
                    high_weights_normalized = high_weights / high_weights.sum()
                    top_companies.loc[high_companies, 'Monto_Inversion'] = (
                        high_weights_normalized * remaining_budget
                    ).round(-3)  # Redondear a miles
        
        # Ajustar para que sume exactamente el presupuesto
        current_total = top_companies['Monto_Inversion'].sum()
        if abs(current_total - budget) > 1:  # Si hay diferencia significativa
            # Ajustar la inversión más grande proporcionalmente
            max_idx = top_companies['Monto_Inversion'].idxmax()
            adjustment = budget - current_total
            top_companies.loc[max_idx, 'Monto_Inversion'] += adjustment
            top_companies.loc[max_idx, 'Monto_Inversion'] = max(
                top_companies.loc[max_idx, 'Monto_Inversion'], min_investment
            )
        
        # Recalcular porcentajes finales
        final_total = top_companies['Monto_Inversion'].sum()
        top_companies['Porcentaje_Recomendado'] = (
            top_companies['Monto_Inversion'] / final_total * 100
        )
        
        total_invested = final_total
        
        # Crear resumen final con datos CORREGIDOS
        recommendations = {
            'fecha_analisis': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'presupuesto_total': budget,
            'total_invertido': total_invested,
            'empresas_recomendadas': len(top_companies),
            'distribucion': top_companies.to_dict('records'),
            'resumen_sectores': {}
        }
        
        # Calcular resumen de sectores CORREGIDO
        for _, company in top_companies.iterrows():
            sector = company['Sector']
            monto = company['Monto_Inversion']
            porcentaje = company['Porcentaje_Recomendado']
            
            if sector not in recommendations['resumen_sectores']:
                recommendations['resumen_sectores'][sector] = {
                    'Monto_Inversion': 0,
                    'Porcentaje_Recomendado': 0
                }
            
            recommendations['resumen_sectores'][sector]['Monto_Inversion'] += monto
            recommendations['resumen_sectores'][sector]['Porcentaje_Recomendado'] += porcentaje
        
        # Guardar recomendaciones
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"data/processed/investment_recommendations_{timestamp}.csv"
        top_companies.to_csv(filepath, index=False)
        # logger.info(f"Recomendaciones guardadas en {filepath}")
        
        return recommendations
    
    def get_market_summary(self, df_fundamentals: pd.DataFrame = None) -> Dict:
        """
        Genera resumen del mercado
        Args:
            df_fundamentals: DataFrame opcional con datos fundamentales
        """
        # Usar df_fundamentals pasado como parámetro o self.fundamental_data
        if df_fundamentals is not None:
            df = df_fundamentals
        elif self.fundamental_data is not None:
            df = self.fundamental_data
        else:
            return {}
        
        # Asegurar conversión de tipos antes de operaciones matemáticas
        df_temp = df.copy()
        df_temp['Valor_Accion'] = pd.to_numeric(df_temp['Valor_Accion'], errors='coerce')
        df_temp['Variacion_6M'] = pd.to_numeric(df_temp['Variacion_6M'], errors='coerce')
        df_temp['Dividend_Yield'] = pd.to_numeric(df_temp['Dividend_Yield'], errors='coerce')
        
        summary = {
            'total_empresas': len(df),
            'empresas_con_dividendos': len(
                df[df['Paga_Dividendos'].astype(str) == 'Sí']
            ),
            'precio_promedio': df_temp['Valor_Accion'].mean() if df_temp['Valor_Accion'].notna().any() else 0,
            'variacion_promedio_6m': df_temp['Variacion_6M'].mean() * 100 if df_temp['Variacion_6M'].notna().any() else 0,
            'dividend_yield_promedio': df_temp[df_temp['Dividend_Yield'].notna()]['Dividend_Yield'].mean() if df_temp['Dividend_Yield'].notna().any() else 0,
            'sectores': df['Sector'].value_counts().to_dict() if 'Sector' in df.columns else {},
        }
        
        # Agregar top performers con validación de tipos
        try:
            # Asegurar que Variacion_6M sea numérico
            df_temp = df.copy()
            df_temp['Variacion_6M'] = pd.to_numeric(df_temp['Variacion_6M'], errors='coerce')
            summary['top_performers_6m'] = df_temp.nlargest(5, 'Variacion_6M')[['Empresa', 'Variacion_6M']].to_dict('records')
        except Exception as e:
            logger.warning(f"Error calculando top_performers_6m: {e}")
            summary['top_performers_6m'] = []
        
        try:
            # Asegurar que Dividend_Yield sea numérico
            df_temp = df.copy()
            df_temp['Dividend_Yield'] = pd.to_numeric(df_temp['Dividend_Yield'], errors='coerce')
            df_dividends = df_temp[df_temp['Dividend_Yield'].notna()]
            summary['mejores_dividendos'] = df_dividends.nlargest(5, 'Dividend_Yield')[
                ['Empresa', 'Dividend_Yield']
            ].to_dict('records')
        except Exception as e:
            logger.warning(f"Error calculando mejores_dividendos: {e}")
            summary['mejores_dividendos'] = []
        
        return summary
    
    def run_complete_analysis(self, budget: float = 1000000) -> Tuple[pd.DataFrame, Dict, Dict]:
        """
        Ejecuta el análisis completo
        Returns: (fundamental_data, recommendations, market_summary)
        """
        logger.info("Iniciando análisis completo...")
        
        # 1. Descargar datos fundamentales
        df_fundamentals = self.download_all_fundamental_data()
        
        # 2. Calcular pesos del portafolio
        weights = self.calculate_portfolio_weights(df_fundamentals)
        
        # 3. Configurar datos en la instancia para generate_investment_recommendations
        self.fundamental_data = df_fundamentals
        self.portfolio_weights = weights
        
        # 4. Generar recomendaciones
        recommendations = self.generate_investment_recommendations(budget)
        
        # 5. Generar resumen del mercado
        market_summary = self.get_market_summary()
        
        logger.info("Análisis completo finalizado")
        
        return {
            'fundamental_data': df_fundamentals,
            'recommendations': recommendations,
            'market_summary': market_summary
        }
    
    def business_analyst_gpt(self, df_fundamentals: pd.DataFrame) -> str:
        """
        Genera análisis financiero usando GPT
        Replica la función business_analyst del notebook
        """
        if not OPENAI_AVAILABLE:
            return self._generate_fallback_analysis(df_fundamentals)
        
        try:
            # Configurar cliente OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OPENAI_API_KEY no encontrada. Usando análisis fallback.")
                return self._generate_fallback_analysis(df_fundamentals)
            
            client = OpenAI(api_key=api_key)
            
            # Filtrar solo empresas que pagan dividendos
            mask = df_fundamentals["Paga_Dividendos"].astype(str) == "Sí"
            df_dividends = df_fundamentals.loc[mask, [
                "Empresa", "ROE", "Precio_Actual", "Variacion_1M", "Variacion_6M", 
                "PE_Ratio", "Margen_Beneficio", "Operating_Cash_Flow", "Total_Debt", 
                "Cash_Flow_to_Debt_Ratio", "Crecimiento_Ingresos", 
                "Crecimiento_Beneficios", "Beta", "Ultimos_Dividendos", 
                "Frecuencia_Dividendos"
            ]]
            
            # Crear prompt para GPT con formato Markdown
            task_prompt = f"""
            Eres un **analista financiero senior** especializado en la bolsa chilena. 
            Tu tarea es evaluar de manera **objetiva, breve y comparativa** los datos de las siguientes empresas:

            {df_dividends.to_string()}

            ### Instrucciones:
            - Usa formato **Markdown estructurado**, con los mismos títulos y subtítulos indicados abajo.
            - Escribe **frases cortas y claras** (máximo 2 líneas por punto).
            - Si un dato falta o no está en el dataframe, escribe **“No disponible”**.
            - No inventes información externa.
            - Limita la respuesta a **máximo 350 tokens**.

            ### Estructura esperada:

            ### 📈 Análisis de Datos Fundamentales
            - **Mejores ROE**: [empresa(s) con valores]
            - **Análisis P/E**: [comparación de ratios, alto vs bajo]

            ### 💹 Variación de Precios  
            - **Mejores performers 6M**: [empresas destacadas]
            - **Tendencias 1M**: [breve análisis corto plazo]

            ### 💰 Flujo de Efectivo
            - **Cash Flow operativo**: [evaluación]
            - **Endeudamiento**: [comparación ratios deuda/capital]

            ### ⚖️ Análisis de Riesgo
            - **Beta promedio**: [valor + interpretación riesgo]

            ### 💎 Dividendos
            - **Mejores yields**: [empresas con mayor rentabilidad]
            - **Frecuencia**: [regularidad de pagos]

            ### 🎯 Recomendaciones
            - **Top empresas**: [3–5 mejores opciones]
            - **Estrategia**: [sugerencia de diversificación breve]
            """
            
            # completion = client.chat.completions.create(
            #     model="gpt-5-mini",
            #     messages=[{"role": "user", "content": task_prompt}],
            #     max_completion_tokens=500,
            #     # temperature=0.7
            # )


            response = client.responses.create(
                model="gpt-5-mini",
                reasoning={"effort": "medium"},
                instructions="Eres un analista financiero senior especializado en la bolsa chilena y debes responder solo con el formato solicitado.",
                input=task_prompt,
                max_output_tokens=600,
            )
            
            gpt_response = response.output_text

            
            # return completion.choices[0].message.content
            return gpt_response
            
        except Exception as e:
            logger.error(f"Error en análisis GPT: {str(e)}")
            return self._generate_fallback_analysis(df_fundamentals)
    
    def financial_advisor_gpt(self, gpt_analysis: str, portfolio_weights: pd.DataFrame, 
                             budget: int, risk_level: str = "moderado", 
                             num_companies: int = 10) -> str:
        """
        Genera distribución de inversión usando GPT con perfil de riesgo personalizado
        
        Args:
            gpt_analysis: Análisis previo generado por business_analyst_gpt
            portfolio_weights: DataFrame con pesos calculados del portafolio
            budget: Presupuesto total para inversión
            risk_level: Nivel de riesgo ("conservador", "moderado", "agresivo")
            num_companies: Número de empresas deseadas en el portafolio
        """
        if not OPENAI_AVAILABLE:
            return self._generate_fallback_distribution(
                portfolio_weights, budget, risk_level, num_companies
            )
        
        try:
            # Configurar cliente OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("OPENAI_API_KEY no encontrada. Usando distribución fallback.")
                return self._generate_fallback_distribution(
                    portfolio_weights, budget, risk_level, num_companies
                )
            
            client = OpenAI(api_key=api_key)
            
            # Definir estrategias por perfil de riesgo
            risk_strategies = {
                "conservador": {
                    "description": "Perfil CONSERVADOR: Priorizar empresas estables con dividendos altos, menor volatilidad y beta baja. Concentrar en sectores defensivos (utilities, banca sólida).",
                    "min_dividend_focus": "70%",
                    "diversification": "máxima diversificación"
                },
                "moderado": {
                    "description": "Perfil MODERADO: Balance entre estabilidad y crecimiento. Combinar empresas maduras con dividendos y algunas de crecimiento.",
                    "min_dividend_focus": "50%",
                    "diversification": "diversificación equilibrada"
                },
                "agresivo": {
                    "description": "Perfil AGRESIVO: Priorizar empresas de alto crecimiento, mejor ROE y performance reciente. Tolerar mayor volatilidad por retornos superiores.",
                    "min_dividend_focus": "30%",
                    "diversification": "concentración en mejores performers"
                }
            }
            
            risk_strategy = risk_strategies.get(risk_level.lower(), risk_strategies["moderado"])
            
            # Crear prompt personalizado con perfil de riesgo
            task_prompt = f"""
            Eres un **asesor financiero experto en portafolios de la bolsa chilena**.
            Debes asignar **EXACTAMENTE** el presupuesto disponible conforme al perfil de riesgo, usando una distribución **ponderada, no equitativa**.

            IMPORTANTE: Realiza toda la clasificación y validación internamente. **NO muestres pasos intermedios, ni tablas de validación, ni listas de verificación**. Solo entrega la **salida final** en el formato exacto pedido.

            ### Perfil del Cliente
            - Nivel de Riesgo: {risk_level.upper()}
            - Estrategia: {risk_strategy['description']}
            - Número de empresas deseadas: {num_companies}
            - Enfoque en dividendos: {risk_strategy['min_dividend_focus']}
            - Diversificación: {risk_strategy['diversification']} (máx. 2 empresas por sector)

            ### Datos de entrada
            - Informe Financiero:
            {gpt_analysis}

            - Distribución de Pesos Calculados (obligatorio: columna 'ticker' y preferible 'sector', 'weight', 'roe', 'yield', 'perf_6m'):
            {portfolio_weights.to_string()}

            - Presupuesto total: ${budget:,}

            ### REGLAS OBLIGATORIAS (IMPRESCINDIBLES)
            1. TOTAL EXACTO: ${budget:,}.
            2. Exactamente {num_companies} empresas.
            3. **MÁXIMO 2 EMPRESAS POR SECTOR.** No se permite excepción bajo ninguna circunstancia. Si hay más, **descartar automáticamente las de menor score y reemplazar por tickers de otros sectores disponibles**.
            4. MÍNIMO POR EMPRESA: $20,000. **NO SE PERMITEN EXCEPCIONES.** Si algún ticker quedara por debajo, **reemplazar inmediatamente por otro ticker disponible** y ajustar los montos de los demás para cumplir TOTAL EXACTO.
            5. Montos en múltiplos de $1,000, respetando el mínimo.
            6. Solo usar tickers listados en "Distribución de Pesos Calculados".
            7. No mostrar validaciones ni pasos intermedios, solo la salida final.
            8. Si no es posible cumplir todas las reglas, devuelve únicamente:  
            `NO ES POSIBLE CUMPLIR RESTRICCIONES` (máx. 2 líneas explicando por qué).
            9. Responde en máximo 350–450 tokens.

            ### LÓGICA APLICADA (EJECUTAR INTERNAMENTE, NO MOSTRAR)
            1. Primero, filtrar candidatos por sector para **RESPETAR MÁXIMO 2 POR SECTOR**.
            2. Luego, ordenar por score (usar weight/roe/yield/perf_6m si existen).
            3. Seleccionar top {num_companies} dentro de las restricciones de sector.
            4. Asignar montos proporcionales al score, imponiendo mínimo $20,000 y redondeando a múltiplos de $1,000.
            5. Ajustar incrementalmente (± $1,000), respetando el mínimo por empresa, hasta que TOTAL == ${budget:,}.
            6. Reemplazar cualquier ticker que no cumpla límite de sector automáticamente.

            ### SALIDA (SOLO ESTO)
            ### 📊 Distribución de Inversión ({risk_level.capitalize()})
            - TICKER | SECTOR : $ [dinero]
            - ...

            **TOTAL: $ {budget:,}**

            ### 📝 Justificación (no tan extenso)
            - [Explicación de la coherencia con el perfil de riesgo con las empresas seleccionadas]
            - [Explicación de la diversificación lograda, sectores cubiertos, etc.]
            - [Explicación de empresas seleccionadas, fortalezas, enfoque en dividendos o crecimiento según perfil]

            """
            
            # completion = client.chat.completions.create(
            #     model="gpt-5-mini",
            #     messages=[{"role": "user", "content": task_prompt}],
            #     max_completion_tokens=600,
            #     # temperature=0.3
            # )
            
            # gpt_response = completion.choices[0].message.content

            response = client.responses.create(
                model="gpt-5-mini",
                reasoning={"effort": "medium"},
                instructions="Eres un asesor financiero senior especializado en la bolsa chilena y debes responder solo con el formato solicitado.",
                input=task_prompt,
                max_output_tokens=600,
            )
            
            gpt_response = response.output_text

            logger.info(f"Respuesta GPT cruda:\n{gpt_response[:500]}")
            
            # NUEVA FUNCIONALIDAD: Validar y corregir la suma automáticamente
            corrected_response = self._validate_and_fix_gpt_budget(gpt_response, budget)
            
            if not corrected_response or corrected_response == gpt_response:
                logger.warning("GPT no devolvió formato parseable, usando fallback")
                return self._generate_fallback_distribution(
                    portfolio_weights, budget, risk_level, num_companies
                )

            return corrected_response
            
        except Exception as e:
            logger.error(f"Error en asesoría GPT: {str(e)}")
            return self._generate_fallback_distribution(
                portfolio_weights, budget, risk_level, num_companies
            )
    
    def _validate_and_fix_gpt_budget(self, gpt_response: str, target_budget: int) -> str:
        """
        Valida y corrige automáticamente la distribución de GPT para que sume exactamente el presupuesto
        """
        import re
        
        try:
            # Extraer las líneas con inversiones usando regex
            investment_lines = []
            lines = gpt_response.split('\n')
            
            for line in lines:
                # Buscar líneas con formato: "- Empresa: $cantidad"
                match = re.search(r'- (.+?):\s*\$\s*([\d,]+)', line)
                if match:
                    company = match.group(1).strip()
                    amount_str = match.group(2).replace(',', '')
                    try:
                        amount = int(amount_str)
                        investment_lines.append({
                            'company': company, 
                            'amount': amount, 
                            'original_line': line
                        })
                    except ValueError:
                        continue
            
            if not investment_lines:
                logger.warning("No se pudieron extraer inversiones del GPT")
                return gpt_response
            
            # Calcular suma actual
            current_total = sum([inv['amount'] for inv in investment_lines])
            
            if current_total == target_budget:
                # Ya está correcto
                return gpt_response
            
            # Necesita corrección
            logger.info(f"Corrigiendo distribución GPT: ${current_total:,} -> ${target_budget:,}")
            
            # Calcular factor de corrección
            correction_factor = target_budget / current_total
            
            # Aplicar corrección proporcional
            corrected_investments = []
            running_total = 0
            
            for i, inv in enumerate(investment_lines):
                if i == len(investment_lines) - 1:
                    # Última empresa: ajustar para que la suma sea exacta
                    corrected_amount = target_budget - running_total
                else:
                    # Empresas anteriores: aplicar factor proporcional y redondear
                    corrected_amount = int((inv['amount'] * correction_factor) / 1000) * 1000
                    corrected_amount = max(corrected_amount, 20000)  # Mínimo $20,000
                
                corrected_investments.append({
                    'company': inv['company'],
                    'amount': corrected_amount
                })
                running_total += corrected_amount
            
            # Regenerar el texto corregido
            corrected_response = gpt_response
            
            # Reemplazar las líneas de inversión
            for inv, corrected_inv in zip(investment_lines, corrected_investments):
                old_line = inv['original_line']
                new_line = f"- {corrected_inv['company']}: ${corrected_inv['amount']:,}"
                corrected_response = corrected_response.replace(old_line, new_line)
            
            # Actualizar la línea TOTAL
            total_pattern = re.compile(r'TOTAL:\s*\$[\d,]+')
            corrected_response = total_pattern.sub(f'TOTAL: ${target_budget:,}', corrected_response)
            
            logger.info(f"✅ Distribución corregida: ${sum([c['amount'] for c in corrected_investments]):,}")
            
            return corrected_response
            
        except Exception as e:
            logger.error(f"Error corrigiendo distribución GPT: {e}")
            return gpt_response
    
    def _sync_recommendations_with_gpt(self, original_recommendations: Dict, 
                                      gpt_distribution: str, budget: int) -> Dict:
        """
        Sincroniza las recomendaciones con la distribución GPT para consistencia
        """
        import re
        
        try:
            # Extraer inversiones de la distribución GPT
            gpt_investments = []
            lines = gpt_distribution.split('\n')
            
            for line in lines:
                match = re.search(r'- (.+?):\s*\$\s*([\d,]+)', line)
                if match:
                    company_name = match.group(1).strip()
                    amount_str = match.group(2).replace(',', '')
                    try:
                        amount = int(amount_str)
                        gpt_investments.append({
                            'company_name': company_name,
                            'amount': amount
                        })
                    except ValueError:
                        continue
            
            if not gpt_investments:
                logger.warning("No se pudieron extraer inversiones GPT")
                return None
            
            # Crear nueva distribución basada en GPT
            new_distribution = []
            total_gpt = sum([inv['amount'] for inv in gpt_investments])
            
            # Mapear empresas GPT a datos originales
            original_companies = {item['Empresa']: item for item in original_recommendations['distribucion']}
            used_companies = set()  # Para evitar duplicados
            
            for gpt_inv in gpt_investments:
                # Buscar empresa correspondiente (fuzzy matching mejorado)
                matched_company = None
                gpt_name = gpt_inv['company_name'].upper().strip()
                
                # Buscar coincidencia exacta primero
                for orig_name, orig_data in original_companies.items():
                    if orig_name in used_companies:
                        continue  # Ya fue usada
                        
                    orig_name_clean = orig_name.upper().strip()
                    
                    # Matching más preciso
                    if (orig_name_clean == gpt_name or
                        gpt_name in orig_name_clean or 
                        orig_name_clean in gpt_name):
                        matched_company = orig_data
                        used_companies.add(orig_name)
                        break
                
                # Si no encuentra match exacto, buscar por palabras clave
                if not matched_company:
                    for orig_name, orig_data in original_companies.items():
                        if orig_name in used_companies:
                            continue
                            
                        orig_name_clean = orig_name.upper().strip()
                        gpt_words = [w for w in gpt_name.split() if len(w) > 3]
                        
                        if any(word in orig_name_clean for word in gpt_words):
                            matched_company = orig_data
                            used_companies.add(orig_name)
                            break
                
                if matched_company:
                    # Actualizar con datos GPT pero mantener estructura original
                    updated_company = matched_company.copy()
                    updated_company['Monto_Inversion'] = gpt_inv['amount']
                    updated_company['Porcentaje_Recomendado'] = (gpt_inv['amount'] / total_gpt) * 100
                    new_distribution.append(updated_company)
                else:
                    logger.warning(f"No se encontró match para empresa GPT: {gpt_inv['company_name']}")
            
            if len(new_distribution) == 0:
                logger.warning("No se pudo mapear ninguna empresa GPT")
                return None
            
            # Recalcular resumen de sectores
            new_sector_summary = {}
            for company in new_distribution:
                sector = company['Sector']
                if sector not in new_sector_summary:
                    new_sector_summary[sector] = {
                        'Monto_Inversion': 0,
                        'Porcentaje_Recomendado': 0
                    }
                new_sector_summary[sector]['Monto_Inversion'] += company['Monto_Inversion']
                new_sector_summary[sector]['Porcentaje_Recomendado'] += company['Porcentaje_Recomendado']
            
            # Crear nueva estructura de recomendaciones
            synced_recommendations = original_recommendations.copy()
            synced_recommendations.update({
                'total_invertido': total_gpt,
                'empresas_recomendadas': len(new_distribution),
                'distribucion': new_distribution,
                'resumen_sectores': new_sector_summary
            })
            
            logger.info(f"Sincronización GPT: {len(new_distribution)} empresas, ${total_gpt:,} total")
            return synced_recommendations
            
        except Exception as e:
            logger.error(f"Error sincronizando con GPT: {e}")
            return None
    
    
    
    def _generate_fallback_analysis(self, df_fundamentals: pd.DataFrame) -> str:
        """Genera análisis básico cuando GPT no está disponible"""
        
        # Filtrar valores no numéricos y NaN antes de hacer comparaciones
        df_numeric = df_fundamentals.copy()
        numeric_cols = ['ROE', 'Dividend_Yield', 'Variacion_6M', 'Beta']
        
        for col in numeric_cols:
            if col in df_numeric.columns:
                df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')
        
        # Asegurar que Empresa sea string para el join
        if 'Empresa' in df_numeric.columns:
            df_numeric['Empresa'] = df_numeric['Empresa'].astype(str)
        
        # Empresas con mejores métricas (solo si hay datos válidos)
        top_roe = []
        top_dividends = []
        top_performance = []
        
        if len(df_numeric) > 0 and 'ROE' in df_numeric.columns and df_numeric['ROE'].notna().any():
            top_roe = df_numeric.nlargest(3, 'ROE')['Empresa'].tolist()
        
        if len(df_numeric) > 0 and 'Dividend_Yield' in df_numeric.columns and df_numeric['Dividend_Yield'].notna().any():
            top_dividends = df_numeric.nlargest(3, 'Dividend_Yield')['Empresa'].tolist()
            
        if len(df_numeric) > 0 and 'Variacion_6M' in df_numeric.columns and df_numeric['Variacion_6M'].notna().any():
            top_performance = df_numeric.nlargest(3, 'Variacion_6M')['Empresa'].tolist()
        
        # Calcular métricas de forma segura
        roe_text = "Las empresas con mejor ROE son " + ', '.join(top_roe) if top_roe else "No hay datos ROE suficientes"
        roe_avg = df_numeric['ROE'].mean() if len(df_numeric) > 0 and 'ROE' in df_numeric.columns and df_numeric['ROE'].notna().any() else None
        roe_avg_text = f"{roe_avg:.2%}" if roe_avg is not None else "N/A"
        
        perf_text = "Mejores performers en 6M: " + ', '.join(top_performance) if top_performance else "No hay datos de variación suficientes"
        var_avg = df_numeric['Variacion_6M'].mean() if len(df_numeric) > 0 and 'Variacion_6M' in df_numeric.columns and df_numeric['Variacion_6M'].notna().any() else None
        var_avg_text = f"{var_avg:.2%}" if var_avg is not None else "N/A"
        
        beta_avg = df_numeric['Beta'].mean() if len(df_numeric) > 0 and 'Beta' in df_numeric.columns and df_numeric['Beta'].notna().any() else None
        beta_avg_text = f"{beta_avg:.2f}" if beta_avg is not None else "N/A"
        
        div_text = "Mejores dividendos: " + ', '.join(top_dividends) if top_dividends else "No hay datos de dividendos suficientes"
        
        # Corregir cálculo de dividend yield promedio - algunos valores ya vienen en porcentaje
        if len(df_numeric) > 0 and 'Dividend_Yield' in df_numeric.columns and df_numeric['Dividend_Yield'].notna().any():
            div_values = df_numeric['Dividend_Yield'].dropna()
            # Si los valores son muy grandes (>1), asumimos que ya están en porcentaje
            if div_values.max() > 1:
                div_avg = div_values.mean() / 100  # Convertir de porcentaje a decimal
            else:
                div_avg = div_values.mean()  # Ya está en decimal
        else:
            div_avg = None
        
        div_avg_text = f"{div_avg:.2%}" if div_avg is not None else "N/A"
        
        # Construir análisis usando concatenación de strings para evitar problemas con emojis en f-strings
        analysis_parts = [
            "### 📊 Informe Financiero (Análisis Automatizado)",
            "",
            "**📈 Análisis de Datos Fundamentales**",
            f"- {roe_text}",
            f"- **ROE promedio del mercado**: {roe_avg_text}",
            "",
            "**💹 Análisis de Variación de Precio**",
            f"- {perf_text}",
            f"- **Variación promedio 6M**: {var_avg_text}",
            "",
            "**💰 Análisis de Flujo de Efectivo**",
            "- Se priorizan empresas con cash flow positivo",
            "",
            "**⚖️ Análisis de Riesgo**",
            f"- **Beta promedio del mercado**: {beta_avg_text}",
            "",
            "**💎 Análisis de Dividendos**",
            f"- {div_text}",
            f"- **Dividend yield promedio**: {div_avg_text}",
            "",
            "**🎯 Evaluación General**",
            "- Diversificar entre sectores, priorizar dividendos estables",
            "",
            "*Análisis automatizado. Para análisis detallado configure OPENAI_API_KEY.*"
        ]
        
        analysis = "\n".join(analysis_parts)
        return analysis.strip()
    
    def _generate_fallback_distribution(self, portfolio_weights: pd.DataFrame, 
                                        budget: int, risk_level: str = "moderado", 
                                        num_companies: int = 10) -> str:
        """Genera distribución básica cuando GPT no está disponible"""
        
        distribution_text = f"### Distribución de Inversión (Automatizada - {risk_level.capitalize()})\n"
        total_invested = 0
        min_investment = 20000
        
        # Top empresas por peso con validación de tipos
        try:
            # Asegurar que Peso_Asignado sea numérico
            portfolio_weights_temp = portfolio_weights.copy()
            portfolio_weights_temp['Peso_Asignado'] = pd.to_numeric(
                portfolio_weights_temp['Peso_Asignado'], errors='coerce'
            )
            # Eliminar filas con pesos inválidos
            portfolio_weights_temp = portfolio_weights_temp.dropna(
                subset=['Peso_Asignado']
            )
            
            if portfolio_weights_temp.empty:
                # Si no hay datos válidos, crear distribución igual
                distribution_text += "- Error en datos de peso, distribución no disponible\n"
                return distribution_text
            
            # Usar el número de empresas especificado por el usuario
            top_companies = portfolio_weights_temp.nlargest(
                num_companies, 'Peso_Asignado'
            )
        except Exception as e:
            logger.error(f"Error en nlargest: {e}")
            distribution_text += "- Error en cálculo de distribución\n"
            return distribution_text
        
        for empresa, row in top_companies.iterrows():
            weight_ratio = (
                row['Peso_Asignado'] /
                portfolio_weights_temp['Peso_Asignado'].sum()
            )
            investment = max(
                int((budget * weight_ratio) / 1000) * 1000, min_investment
            )
            distribution_text += f"- {empresa}: ${investment:,}\n"
            total_invested += investment
        
        distribution_text += f"TOTAL: ${total_invested:,}\n\n"
        
        # Justificación personalizada según perfil de riesgo
        risk_justifications = {
            "conservador": [
                "- Enfoque en empresas estables con dividendos consistentes",
                "- Priorización de sectores defensivos y menor volatilidad",
                "- Diversificación máxima para reducir riesgo"
            ],
            "moderado": [
                "- Balance entre estabilidad y oportunidades de crecimiento",
                "- Combinación de empresas maduras y algunas con potencial",
                "- Diversificación equilibrada entre sectores"
            ],
            "agresivo": [
                "- Concentración en empresas de alto crecimiento y ROE superior",
                "- Mayor tolerancia a volatilidad por retornos potenciales",
                "- Enfoque en performance y métricas de crecimiento"
            ]
        }
        
        justification_lines = risk_justifications.get(
            risk_level.lower(), risk_justifications["moderado"]
        )
        
        distribution_text += f"""
        ### Justificación de Inversión (Perfil {risk_level.capitalize()})
        - Distribución automatizada para {num_companies} empresas seleccionadas
        {chr(10).join(justification_lines)}
        - Inversión mínima $20,000 por empresa
        - Análisis basado en datos fundamentales actualizados

        *Para asesoría IA personalizada configure OPENAI_API_KEY.*
        """
        
        return distribution_text
    
    def run_complete_analysis_with_gpt(self, budget: int = 5000000, 
                                      risk_level: str = "moderado",
                                      dividend_preference: bool = True,
                                      top_stocks_count: int = 5) -> Dict:
        """
        Ejecuta análisis completo incluyendo GPT con funcionalidad TOP X acciones
        Versión mejorada que analiza todas las acciones y selecciona las TOP X mejores
        """
        logger.info(f"Iniciando análisis completo con GPT - TOP {top_stocks_count} acciones")
        
        try:
            # 1. Obtener datos fundamentales de TODAS las acciones
            df_fundamentals = self.download_all_fundamental_data()
            logger.info(f"Datos obtenidos para {len(df_fundamentals)} acciones")
            
            # 2. Calcular pesos del portafolio para TODAS las acciones
            portfolio_weights = self.calculate_portfolio_weights(
                df_fundamentals, risk_level, dividend_preference
            )
            
            # 3. NUEVA FUNCIONALIDAD: Seleccionar TOP X acciones basado en puntajes
            if len(portfolio_weights) > top_stocks_count:
                # Ordenar por puntuación y seleccionar TOP X
                top_portfolio_weights = portfolio_weights.nlargest(
                    top_stocks_count, 'Puntaje'
                ).copy()
                
                # Filtrar datos fundamentales para TOP X acciones solamente
                top_tickers = top_portfolio_weights['Ticker'].tolist()
                df_fundamentals_filtered = df_fundamentals[
                    df_fundamentals['Ticker'].isin(top_tickers)
                ].copy()
                
                logger.info(f"Seleccionadas TOP {top_stocks_count} acciones: {top_tickers}")
            else:
                # Si hay pocas acciones disponibles, usar todas
                top_portfolio_weights = portfolio_weights
                df_fundamentals_filtered = df_fundamentals
                logger.info(f"Usando todas las {len(portfolio_weights)} acciones disponibles")
            
            # 4. Generar análisis con GPT (todas las acciones disponibles)
            gpt_analysis = self.business_analyst_gpt(df_fundamentals)
            
            # 5. Generar distribución con GPT (TODAS las acciones disponibles)
            gpt_distribution = self.financial_advisor_gpt(
                gpt_analysis, portfolio_weights, budget,
                risk_level, top_stocks_count
            )
            
            # 6. Generar recomendaciones concentradas en TOP X acciones
            self.fundamental_data = df_fundamentals_filtered
            self.portfolio_weights = top_portfolio_weights
            recommendations = self.generate_investment_recommendations(budget)
            
            # 7. COMENTADO TEMPORALMENTE: Parsear distribución GPT y actualizar recomendaciones
            # Para permitir ver la distribución original de GPT sin sincronización
            logger.info("📊 DISTRIBUCIÓN GPT ORIGINAL (sin sincronizar):")
            if gpt_distribution:
                logger.info(f"\n{gpt_distribution}")
            
            # SINCRONIZACIÓN DESHABILITADA TEMPORALMENTE PARA DEBUG
            # if gpt_distribution and not gpt_distribution.startswith('### Distribución de Inversión (Automatizada)'):
            #     updated_recommendations = self._sync_recommendations_with_gpt(
            #         recommendations, gpt_distribution, budget
            #     )
            #     if updated_recommendations:
            #         recommendations = updated_recommendations
            #         logger.info("✅ Recomendaciones sincronizadas con distribución GPT")
            
            # 8. Generar resumen del mercado (con todas las acciones para contexto)
            market_summary = self.get_market_summary(df_fundamentals)
            
            logger.info(f"Análisis completo con GPT finalizado - TOP {top_stocks_count} acciones seleccionadas")
            
            return {
                'fundamental_data': df_fundamentals_filtered,  # Solo TOP X
                'all_fundamental_data': df_fundamentals,       # Todas para contexto
                'recommendations': recommendations,  # Recomendaciones automáticas
                'market_summary': market_summary,
                'gpt_analysis': gpt_analysis,
                'gpt_distribution': gpt_distribution,  # Distribución GPT ORIGINAL
                'gpt_distribution_original': gpt_distribution,  # Copia para debug
                'portfolio_weights': top_portfolio_weights,
                'all_portfolio_weights': portfolio_weights,    # Todas para comparación
                'top_stocks_count': top_stocks_count,
                'total_stocks_analyzed': len(df_fundamentals),
                'sync_disabled': True  # Flag para indicar que sync está deshabilitado
            }
            
        except Exception as e:
            logger.error(f"Error en análisis completo con GPT: {str(e)}")
            # Fallback sin GPT, reutilizando datos descargados
            try:
                # Asegurarse de que tenemos los datos básicos necesarios
                if 'df_fundamentals' not in locals():
                    df_fundamentals = self.download_all_fundamental_data()
                if 'portfolio_weights' not in locals():
                    portfolio_weights = self.calculate_portfolio_weights(
                        df_fundamentals, risk_level, dividend_preference
                    )
                
                # Generar componentes faltantes
                self.fundamental_data = df_fundamentals
                self.portfolio_weights = portfolio_weights
                recommendations = self.generate_investment_recommendations(budget)
                market_summary = self.get_market_summary()
                fallback_analysis = self._generate_fallback_analysis(
                    df_fundamentals
                )
                
                return {
                    'fundamental_data': df_fundamentals,
                    'recommendations': recommendations,
                    'market_summary': market_summary,
                    'gpt_analysis': fallback_analysis,
                    'gpt_distribution': None,  # No hay distribución GPT
                    'portfolio_weights': portfolio_weights
                }
            except Exception as fallback_error:
                logger.error(f"Error en fallback: {str(fallback_error)}")
                # Si falla fallback, usar análisis completo como último recurso
                return self.run_complete_analysis(budget)


def run_investment_analysis(
    budget: float = 1000000
) -> Tuple[pd.DataFrame, Dict, Dict]:
    """Función conveniente para ejecutar el análisis completo"""
    analyzer = InvestmentAnalyzer()
    return analyzer.run_complete_analysis(budget)


if __name__ == "__main__":
    # Ejemplo de uso
    analyzer = InvestmentAnalyzer()
    fundamentals, recommendations, summary = analyzer.run_complete_analysis(
        1000000
    )
    
    print("\n=== RESUMEN DEL MERCADO ===")
    print(f"Total empresas analizadas: {summary['total_empresas']}")
    print(f"Empresas con dividendos: {summary['empresas_con_dividendos']}")
    print(f"Variación promedio 6M: {summary['variacion_promedio_6m']:.2f}%")
    
    print("\n=== RECOMENDACIONES DE INVERSIÓN ===")
    print(f"Presupuesto: ${recommendations['presupuesto_total']:,.0f}")
    print(f"Total invertido: ${recommendations['total_invertido']:,.0f}")
    print(f"Empresas recomendadas: {recommendations['empresas_recomendadas']}")
    
    for company in recommendations['distribucion'][:5]:
        company_name = company['Empresa']
        investment = company['Monto_Inversion']
        percentage = company['Porcentaje_Recomendado']
        print(f"- {company_name}: ${investment:,.0f} ({percentage:.1f}%)")
