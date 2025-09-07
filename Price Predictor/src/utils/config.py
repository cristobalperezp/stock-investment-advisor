"""
Utilidades generales para el proyecto Price Predictor
"""
import yaml
import os
from pathlib import Path
import logging
from typing import Dict, Any

def setup_logging(log_level: str = "INFO") -> None:
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Carga la configuración desde un archivo YAML
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Diccionario con la configuración
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error al leer el archivo de configuración: {e}")

def get_project_root() -> Path:
    """
    Obtiene la ruta raíz del proyecto
    
    Returns:
        Path: Ruta raíz del proyecto
    """
    return Path(__file__).parent.parent.parent

def ensure_directory_exists(directory_path: str) -> None:
    """
    Asegura que un directorio exista, creándolo si es necesario
    
    Args:
        directory_path: Ruta del directorio
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def get_model_path(model_name: str) -> str:
    """
    Obtiene la ruta para guardar un modelo
    
    Args:
        model_name: Nombre del modelo
        
    Returns:
        Ruta del archivo del modelo
    """
    return f"models/{model_name}_best_model.joblib"
