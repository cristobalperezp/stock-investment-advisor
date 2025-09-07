"""
Dataset de ejemplo para California Housing
"""
import pandas as pd
import numpy as np
from sklearn.datasets import make_regression
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def create_california_housing_sample() -> pd.DataFrame:
    """
    Crea un dataset de ejemplo similar a California Housing
    
    Returns:
        DataFrame con datos simulados
    """
    logger.info("Creando dataset de ejemplo California Housing...")
    
    np.random.seed(42)
    n_samples = 20640
    
    # Generar features sintéticas con nombres del dataset original
    X, y = make_regression(
        n_samples=n_samples,
        n_features=8,
        noise=0.1,
        random_state=42
    )
    
    # Crear DataFrame con nombres de features reales
    feature_names = [
        'MedInc', 'HouseAge', 'AveRooms', 'AveBedrms',
        'Population', 'AveOccup', 'Latitude', 'Longitude'
    ]
    
    df = pd.DataFrame(X, columns=feature_names)
    
    # Ajustar valores para que sean realistas
    df['MedInc'] = np.abs(df['MedInc']) * 2 + 1  # Ingreso: 1-15
    df['HouseAge'] = np.abs(df['HouseAge']) * 10 + 5  # Edad: 5-52
    df['AveRooms'] = np.abs(df['AveRooms']) * 2 + 3  # Habitaciones: 3-20
    df['AveBedrms'] = np.abs(df['AveBedrms']) * 0.5 + 0.8  # Dormitorios: 0.8-5
    df['Population'] = np.abs(df['Population']) * 1000 + 500  # Población: 500-5000
    df['AveOccup'] = np.abs(df['AveOccup']) * 1 + 2  # Ocupantes: 2-8
    df['Latitude'] = df['Latitude'] * 2 + 35  # Latitud: 32-38
    df['Longitude'] = df['Longitude'] * 3 - 120  # Longitud: -125 a -115
    
    # Target: precios de casa (en cientos de miles)
    df['MedHouseVal'] = np.abs(y) * 0.5 + 1  # Precio: 1-5 (en cientos de miles)
    
    logger.info(f"Dataset creado: {df.shape[0]} filas, {df.shape[1]} columnas")
    
    return df
