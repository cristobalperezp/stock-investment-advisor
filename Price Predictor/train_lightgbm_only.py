"""
Script para entrenar solo LightGBM y probar las correcciones
"""
import sys
from pathlib import Path
import pandas as pd
import logging
import joblib

# Agregar src al path
sys.path.append(str(Path(__file__) / "src"))
sys.path.append("src")

from src.utils.config import load_config, setup_logging
from src.models.model_trainer import ModelTrainer

def main():
    """Función principal para entrenar solo LightGBM"""
    
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Iniciando entrenamiento de LightGBM...")
    
    # Cargar configuración
    config = load_config()
    
    # Cargar datos procesados
    logger.info("📊 Cargando datos procesados...")
    
    X_train = pd.read_csv("data/processed/X_train.csv")
    X_val = pd.read_csv("data/processed/X_val.csv") 
    X_test = pd.read_csv("data/processed/X_test.csv")
    y_train = pd.read_csv("data/processed/y_train.csv").iloc[:, 0]
    y_val = pd.read_csv("data/processed/y_val.csv").iloc[:, 0]
    y_test = pd.read_csv("data/processed/y_test.csv").iloc[:, 0]
    
    logger.info("✅ Datos cargados")
    
    # Entrenar LightGBM
    trainer = ModelTrainer(config)
    
    logger.info("🎯 Entrenando LightGBM...")
    
    try:
        result = trainer.train_and_evaluate_model(
            model_name='lightgbm',
            X_train=X_train,
            y_train=y_train,
            X_val=X_val,
            y_val=y_val,
            X_test=X_test,
            y_test=y_test,
            optimize=True
        )
        
        logger.info("✅ LightGBM entrenado exitosamente!")
        logger.info(f"   Test RMSE: {result['test_metrics']['rmse']:.4f}")
        logger.info(f"   Test R²: {result['test_metrics']['r2']:.4f}")
        
    except Exception as e:
        logger.error(f"❌ Error entrenando LightGBM: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
