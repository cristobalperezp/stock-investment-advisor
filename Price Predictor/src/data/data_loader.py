"""
Módulo para carga y procesamiento de datos del California Housing dataset
"""
import pandas as pd
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_california_housing_data() -> pd.DataFrame:
    """
    Carga el dataset de California Housing
    
    Returns:
        DataFrame con los datos del California Housing
    """
    logger.info("Cargando dataset California Housing...")
    
    try:
        # Intentar cargar desde sklearn
        from sklearn.datasets import fetch_california_housing
        california = fetch_california_housing()
        
        # Crear DataFrame
        df = pd.DataFrame(california.data, columns=california.feature_names)
        df['MedHouseVal'] = california.target
        
        logger.info(f"Dataset cargado desde sklearn: {df.shape[0]} filas, {df.shape[1]} columnas")
        
    except Exception as e:
        logger.warning(f"No se pudo cargar desde sklearn: {e}")
        logger.info("Usando dataset de ejemplo...")
        
        # Usar dataset de ejemplo
        from .sample_data import create_california_housing_sample
        df = create_california_housing_sample()
    
    return df


def preprocess_data(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Preprocesa los datos del dataset
    
    Args:
        df: DataFrame con los datos
        config: Configuración del proyecto
        
    Returns:
        DataFrame preprocesado
    """
    logger.info("Iniciando preprocesamiento de datos...")
    
    df_processed = df.copy()
    
    # Verificar valores nulos
    null_counts = df_processed.isnull().sum()
    if null_counts.sum() > 0:
        logger.warning(f"Se encontraron {null_counts.sum()} valores nulos")
        df_processed = df_processed.dropna()
    
    # Verificar outliers extremos usando IQR
    numerical_features = config['features']['numerical']
    
    for feature in numerical_features:
        if feature in df_processed.columns:
            Q1 = df_processed[feature].quantile(0.25)
            Q3 = df_processed[feature].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df_processed[
                (df_processed[feature] < lower_bound) | 
                (df_processed[feature] > upper_bound)
            ].shape[0]
            
            if outliers > 0:
                logger.info(f"Feature {feature}: {outliers} outliers detectados")
    
    logger.info("Preprocesamiento completado")
    return df_processed


def split_data(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, 
    pd.Series, pd.Series, pd.Series
]:
    """
    Divide los datos en conjuntos de entrenamiento, validación y prueba
    
    Args:
        df: DataFrame con los datos
        config: Configuración del proyecto
        
    Returns:
        Tupla con X_train, X_val, X_test, y_train, y_val, y_test
    """
    logger.info("Dividiendo datos en conjuntos train/val/test...")
    
    target = config['features']['target']
    test_size = config['data']['test_size']
    val_size = config['data']['val_size']
    random_state = config['data']['random_state']
    
    # Separar features y target
    X = df.drop(target, axis=1)
    y = df[target]
    
    # Primera división: train+val / test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=None
    )
    
    # Segunda división: train / val
    val_size_adjusted = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_size_adjusted, 
        random_state=random_state, stratify=None
    )
    
    logger.info(f"División completada:")
    logger.info(f"  Train: {X_train.shape[0]} muestras")
    logger.info(f"  Validation: {X_val.shape[0]} muestras")
    logger.info(f"  Test: {X_test.shape[0]} muestras")
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def scale_features(
    X_train: pd.DataFrame, 
    X_val: pd.DataFrame, 
    X_test: pd.DataFrame,
    scaler_type: str = "standard"
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, object]:
    """
    Escala las features numéricas
    
    Args:
        X_train, X_val, X_test: DataFrames con features
        scaler_type: Tipo de escalador ('standard' o 'robust')
        
    Returns:
        Tupla con X_train_scaled, X_val_scaled, X_test_scaled, scaler
    """
    logger.info(f"Escalando features usando {scaler_type} scaler...")
    
    if scaler_type == "standard":
        scaler = StandardScaler()
    elif scaler_type == "robust":
        scaler = RobustScaler()
    else:
        raise ValueError("scaler_type debe ser 'standard' o 'robust'")
    
    # Ajustar el escalador solo con datos de entrenamiento
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns,
        index=X_train.index
    )
    
    # Transformar validación y test
    X_val_scaled = pd.DataFrame(
        scaler.transform(X_val),
        columns=X_val.columns,
        index=X_val.index
    )
    
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns,
        index=X_test.index
    )
    
    logger.info("Escalado de features completado")
    
    return X_train_scaled, X_val_scaled, X_test_scaled, scaler


def save_processed_data(
    X_train: pd.DataFrame, X_val: pd.DataFrame, X_test: pd.DataFrame,
    y_train: pd.Series, y_val: pd.Series, y_test: pd.Series,
    scaler: object, output_dir: str = "data/processed"
) -> None:
    """
    Guarda los datos procesados
    
    Args:
        X_train, X_val, X_test: DataFrames con features
        y_train, y_val, y_test: Series con targets
        scaler: Objeto escalador
        output_dir: Directorio de salida
    """
    logger.info(f"Guardando datos procesados en {output_dir}...")
    
    # Guardar features
    X_train.to_csv(f"{output_dir}/X_train.csv", index=False)
    X_val.to_csv(f"{output_dir}/X_val.csv", index=False)
    X_test.to_csv(f"{output_dir}/X_test.csv", index=False)
    
    # Guardar targets
    y_train.to_csv(f"{output_dir}/y_train.csv", index=False)
    y_val.to_csv(f"{output_dir}/y_val.csv", index=False)
    y_test.to_csv(f"{output_dir}/y_test.csv", index=False)
    
    # Guardar scaler
    import joblib
    joblib.dump(scaler, f"{output_dir}/scaler.joblib")
    
    logger.info("Datos guardados exitosamente")
