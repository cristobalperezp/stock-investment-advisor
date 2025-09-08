"""
Módulo de configuración para el Stock Investment Advisor
Maneja la carga de configuraciones desde archivos YAML y variables de entorno
"""

import yaml
import os
from typing import Dict, Any, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """Gestor de configuración para el proyecto"""
    
    def __init__(self, config_path: str = None):
        """
        Inicializa el gestor de configuración
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        if config_path is None:
            # Buscar config.yaml en el directorio config/
            current_dir = Path(__file__).parent.parent.parent
            config_path = current_dir / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carga la configuración desde el archivo YAML
        
        Returns:
            Diccionario con la configuración
        """
        try:
            if not self.config_path.exists():
                logger.error(f"Archivo de configuración no encontrado: {self.config_path}")
                return {}
            
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            # Reemplazar variables de entorno
            config = self._replace_env_variables(config)
            
            logger.info(f"Configuración cargada desde: {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return {}
    
    def _replace_env_variables(self, obj: Any) -> Any:
        """
        Reemplaza variables de entorno en la configuración
        Formato: ${VARIABLE_NAME} o ${VARIABLE_NAME:default_value}
        
        Args:
            obj: Objeto a procesar
            
        Returns:
            Objeto con variables de entorno reemplazadas
        """
        if isinstance(obj, dict):
            return {key: self._replace_env_variables(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_env_variables(item) for item in obj]
        elif isinstance(obj, str):
            if obj.startswith('${') and obj.endswith('}'):
                # Extraer nombre de variable y valor por defecto
                var_expr = obj[2:-1]  # Remover ${ }
                if ':' in var_expr:
                    var_name, default_value = var_expr.split(':', 1)
                    return os.getenv(var_name, default_value)
                else:
                    return os.getenv(var_expr, obj)
            return obj
        else:
            return obj
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración usando notación de puntos
        
        Args:
            key: Clave en notación de puntos (ej: 'api.openai_api_key')
            default: Valor por defecto
            
        Returns:
            Valor de configuración
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_stock_symbols(self) -> List[str]:
        """
        Obtiene la lista de símbolos de acciones configurados
        
        Returns:
            Lista de símbolos de acciones
        """
        return self.get('stock_market.top_stocks', [])
    
    def get_api_keys(self) -> Dict[str, str]:
        """
        Obtiene las claves API configuradas
        
        Returns:
            Diccionario con claves API
        """
        return {
            'openai': self.get('api.openai_api_key', ''),
            'news_api': self.get('api.news_api_key', '')
        }
    
    def get_yahoo_finance_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración específica de Yahoo Finance
        
        Returns:
            Configuración de Yahoo Finance
        """
        return self.get('data_sources.yahoo_finance', {})
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de Streamlit
        
        Returns:
            Configuración de Streamlit
        """
        return self.get('ui.streamlit', {})
    
    def get_news_sources_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de fuentes de noticias
        
        Returns:
            Configuración de fuentes de noticias
        """
        return {
            'news_api': self.get('data_sources.news_api', {}),
            'chilean_sources': self.get('data_sources.chilean_sources', {})
        }
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de análisis
        
        Returns:
            Configuración de análisis
        """
        return self.get('analysis', {})
    
    def is_data_source_enabled(self, source: str) -> bool:
        """
        Verifica si una fuente de datos está habilitada
        
        Args:
            source: Nombre de la fuente de datos
            
        Returns:
            True si está habilitada
        """
        return self.get(f'data_sources.{source}.enabled', False)
    
    def get_stock_market_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración del mercado de valores
        
        Returns:
            Configuración del mercado de valores
        """
        return self.get('stock_market', {})


# Instancia global del gestor de configuración
config_manager = ConfigManager()


def get_config() -> ConfigManager:
    """
    Obtiene la instancia global del gestor de configuración
    
    Returns:
        Instancia de ConfigManager
    """
    return config_manager


def load_config(config_path: str = None) -> ConfigManager:
    """
    Carga una nueva instancia del gestor de configuración
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Nueva instancia de ConfigManager
    """
    return ConfigManager(config_path)


# Funciones de utilidad para acceso rápido
def get_stock_symbols() -> List[str]:
    """Obtiene símbolos de acciones configurados"""
    return config_manager.get_stock_symbols()


def get_api_keys() -> Dict[str, str]:
    """Obtiene claves API configuradas"""
    return config_manager.get_api_keys()


def is_yahoo_finance_enabled() -> bool:
    """Verifica si Yahoo Finance está habilitado"""
    return config_manager.is_data_source_enabled('yahoo_finance')


def get_streamlit_port() -> int:
    """Obtiene el puerto de Streamlit"""
    return config_manager.get('ui.streamlit.server_port', 8501)


def main():
    """Función para probar la configuración"""
    print("=== CONFIGURACIÓN DEL PROYECTO ===")
    
    # Probar carga de configuración
    print(f"Archivo de configuración: {config_manager.config_path}")
    print(f"Configuración cargada: {'✓' if config_manager.config else '✗'}")
    
    # Probar variables de entorno
    api_keys = get_api_keys()
    print(f"OpenAI API Key: {'✓' if api_keys['openai'] else '✗'}")
    print(f"News API Key: {'✓' if api_keys['news_api'] else '✗'}")
    
    # Probar símbolos de acciones
    symbols = get_stock_symbols()
    print(f"Símbolos configurados: {len(symbols)}")
    if symbols:
        print(f"Primeros 3: {symbols[:3]}")
    
    # Probar fuentes de datos
    print(f"Yahoo Finance habilitado: {'✓' if is_yahoo_finance_enabled() else '✗'}")
    
    # Configuración de Streamlit
    streamlit_config = config_manager.get_streamlit_config()
    print(f"Puerto Streamlit: {streamlit_config.get('server_port', 'No configurado')}")
    print(f"Layout: {streamlit_config.get('layout', 'No configurado')}")


if __name__ == "__main__":
    main()