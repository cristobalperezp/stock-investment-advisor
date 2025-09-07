"""
Script principal para entrenar y comparar modelos
"""
import sys
from pathlib import Path
import pandas as pd
import logging

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import load_config, setup_logging, ensure_directory_exists
from data.data_loader import (
    load_california_housing_data,
    preprocess_data,
    split_data,
    scale_features,
    save_processed_data
)
from models.model_trainer import ModelTrainer


def main():
    """Función principal"""
    
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Iniciando entrenamiento de modelos...")
    
    # Cargar configuración
    try:
        config = load_config()
        logger.info("✅ Configuración cargada")
    except Exception as e:
        logger.error(f"❌ Error al cargar configuración: {e}")
        return
    
    # Asegurar que existan los directorios
    ensure_directory_exists("data/processed")
    ensure_directory_exists("data/raw") 
    ensure_directory_exists("models")
    ensure_directory_exists("mlruns")
    
    # 1. Cargar datos
    logger.info("📊 Cargando datos...")
    try:
        df = load_california_housing_data()
        
        # Guardar datos raw
        df.to_csv("data/raw/california_housing.csv", index=False)
        logger.info("✅ Datos guardados en data/raw/")
        
    except Exception as e:
        logger.error(f"❌ Error al cargar datos: {e}")
        return
    
    # 2. Preprocesar datos
    logger.info("🔧 Preprocesando datos...")
    try:
        df_processed = preprocess_data(df, config)
        logger.info("✅ Preprocesamiento completado")
    except Exception as e:
        logger.error(f"❌ Error en preprocesamiento: {e}")
        return
    
    # 3. Dividir datos
    logger.info("✂️ Dividiendo datos...")
    try:
        X_train, X_val, X_test, y_train, y_val, y_test = split_data(
            df_processed, config
        )
        logger.info("✅ División completada")
    except Exception as e:
        logger.error(f"❌ Error al dividir datos: {e}")
        return
    
    # 4. Escalar features
    logger.info("⚖️ Escalando features...")
    try:
        X_train_scaled, X_val_scaled, X_test_scaled, scaler = scale_features(
            X_train, X_val, X_test, scaler_type="standard"
        )
        logger.info("✅ Escalado completado")
    except Exception as e:
        logger.error(f"❌ Error al escalar features: {e}")
        return
    
    # 5. Guardar datos procesados
    logger.info("💾 Guardando datos procesados...")
    try:
        save_processed_data(
            X_train_scaled, X_val_scaled, X_test_scaled,
            y_train, y_val, y_test, scaler
        )
        logger.info("✅ Datos procesados guardados")
    except Exception as e:
        logger.error(f"❌ Error al guardar datos: {e}")
        return
    
    # 6. Entrenar modelos
    logger.info("🤖 Iniciando entrenamiento de modelos...")
    
    trainer = ModelTrainer(config)
    results = {}
    
    models_to_train = ['random_forest', 'lightgbm', 'linear_regression']
    
    for model_name in models_to_train:
        logger.info(f"🎯 Entrenando {model_name}...")
        
        try:
            result = trainer.train_and_evaluate_model(
                model_name=model_name,
                X_train=X_train_scaled,
                y_train=y_train,
                X_val=X_val_scaled,
                y_val=y_val,
                X_test=X_test_scaled,
                y_test=y_test,
                optimize=True
            )
            
            results[model_name] = result
            logger.info(f"✅ {model_name} entrenado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error entrenando {model_name}: {e}")
            continue
    
    # 7. Comparar resultados
    logger.info("📈 Comparando resultados...")
    
    comparison_data = []
    for model_name, result in results.items():
        test_metrics = result['test_metrics']
        comparison_data.append({
            'Model': model_name,
            'Test_RMSE': test_metrics['rmse'],
            'Test_MAE': test_metrics['mae'],
            'Test_R2': test_metrics['r2']
        })
    
    # Crear DataFrame de comparación
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df = comparison_df.sort_values('Test_RMSE')  # Ordenar por RMSE
    
    # Guardar comparación
    comparison_df.to_csv("models/model_comparison.csv", index=False)
    
    # Mostrar resultados
    logger.info("🏆 RESULTADOS FINALES:")
    logger.info("\n" + comparison_df.to_string(index=False))
    
    # Identificar mejor modelo
    best_model_name = comparison_df.iloc[0]['Model']
    best_rmse = comparison_df.iloc[0]['Test_RMSE']
    best_r2 = comparison_df.iloc[0]['Test_R2']
    
    logger.info(f"\n🥇 MEJOR MODELO: {best_model_name}")
    logger.info(f"   RMSE: {best_rmse:.4f}")
    logger.info(f"   R²: {best_r2:.4f}")
    
    # Guardar información del mejor modelo
    best_model_info = {
        'best_model': best_model_name,
        'test_rmse': best_rmse,
        'test_r2': best_r2,
        'all_results': comparison_df.to_dict('records')
    }
    
    import json
    with open("models/best_model_info.json", 'w') as f:
        json.dump(best_model_info, f, indent=2)
    
    logger.info("✅ Entrenamiento completado exitosamente!")
    logger.info("🚀 Puedes ejecutar la app Streamlit con:")
    logger.info("   streamlit run src/ui/streamlit_app.py")


if __name__ == "__main__":
    main()
