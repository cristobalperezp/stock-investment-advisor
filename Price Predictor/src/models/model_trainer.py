"""
Módulo de modelos de Machine Learning para predicción de precios
"""
import mlflow
import mlflow.sklearn
import optuna
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from typing import Dict, Any, Tuple, Optional
import logging
import joblib

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Clase para entrenar y optimizar modelos de ML"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models = {
            'random_forest': RandomForestRegressor,
            'lightgbm': LGBMRegressor,
            'linear_regression': LinearRegression
        }
        
        # Configurar MLflow
        mlflow.set_experiment(config['mlflow']['experiment_name'])
    
    def create_model(self, model_name: str, **params) -> object:
        """
        Crea una instancia del modelo especificado
        
        Args:
            model_name: Nombre del modelo
            **params: Parámetros del modelo
            
        Returns:
            Instancia del modelo
        """
        if model_name not in self.models:
            raise ValueError(f"Modelo {model_name} no soportado")
        
        model_class = self.models[model_name]
        
        # Parámetros específicos para cada modelo
        if model_name == 'random_forest':
            params.setdefault('random_state', 42)
            params.setdefault('n_jobs', -1)
        elif model_name == 'lightgbm':
            params.setdefault('random_state', 42)
            params.setdefault('verbosity', -1)
        elif model_name == 'linear_regression':
            # LinearRegression no tiene random_state
            pass
        
        return model_class(**params)
    
    def evaluate_model(
        self, 
        model: object, 
        X_val: pd.DataFrame, 
        y_val: pd.Series
    ) -> Dict[str, float]:
        """
        Evalúa un modelo y retorna métricas
        
        Args:
            model: Modelo entrenado
            X_val: Features de validación
            y_val: Target de validación
            
        Returns:
            Diccionario con métricas
        """
        y_pred = model.predict(X_val)
        
        metrics = {
            'mse': mean_squared_error(y_val, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_val, y_pred)),
            'mae': mean_absolute_error(y_val, y_pred),
            'r2': r2_score(y_val, y_pred)
        }
        
        return metrics
    
    def objective_function(
        self, 
        trial: optuna.Trial, 
        model_name: str, 
        X_train: pd.DataFrame, 
        y_train: pd.Series,
        X_val: pd.DataFrame, 
        y_val: pd.Series
    ) -> float:
        """
        Función objetivo para la optimización con Optuna
        
        Args:
            trial: Trial de Optuna
            model_name: Nombre del modelo
            X_train, y_train: Datos de entrenamiento
            X_val, y_val: Datos de validación
            
        Returns:
            Valor de la métrica a optimizar (RMSE)
        """
        # Obtener configuración de hiperparámetros
        model_config = self.config['models'][model_name]
        hyperparams = model_config['hyperparameters']
        
        params = {}
        
        if model_name == 'random_forest':
            params = {
                'n_estimators': trial.suggest_int(
                    'n_estimators', 
                    hyperparams['n_estimators'][0], 
                    hyperparams['n_estimators'][1]
                ),
                'max_depth': trial.suggest_int(
                    'max_depth', 
                    hyperparams['max_depth'][0], 
                    hyperparams['max_depth'][1]
                ),
                'min_samples_split': trial.suggest_int(
                    'min_samples_split', 
                    hyperparams['min_samples_split'][0], 
                    hyperparams['min_samples_split'][1]
                )
            }
        
        elif model_name == 'lightgbm':
            params = {
                'n_estimators': trial.suggest_int(
                    'n_estimators', 
                    hyperparams['n_estimators'][0], 
                    hyperparams['n_estimators'][1]
                ),
                'max_depth': trial.suggest_int(
                    'max_depth', 
                    hyperparams['max_depth'][0], 
                    hyperparams['max_depth'][1]
                ),
                'learning_rate': trial.suggest_float(
                    'learning_rate', 
                    hyperparams['learning_rate'][0], 
                    hyperparams['learning_rate'][1]
                )
            }
        
        elif model_name == 'linear_regression':
            params = {
                'fit_intercept': trial.suggest_categorical(
                    'fit_intercept', 
                    hyperparams['fit_intercept']
                ),
                'copy_X': trial.suggest_categorical(
                    'copy_X', 
                    hyperparams['copy_X']
                ),
                'positive': trial.suggest_categorical(
                    'positive',
                    hyperparams['positive']
                )
            }
        
        # Crear y entrenar modelo
        model = self.create_model(model_name, **params)
        model.fit(X_train, y_train)
        
        # Evaluar modelo
        metrics = self.evaluate_model(model, X_val, y_val)
        
        return metrics['rmse']
    
    def optimize_hyperparameters(
        self, 
        model_name: str,
        X_train: pd.DataFrame, 
        y_train: pd.Series,
        X_val: pd.DataFrame, 
        y_val: pd.Series,
        n_trials: int = None
    ) -> Tuple[Dict[str, Any], float]:
        """
        Optimiza hiperparámetros usando Optuna
        
        Args:
            model_name: Nombre del modelo
            X_train, y_train: Datos de entrenamiento
            X_val, y_val: Datos de validación
            n_trials: Número de trials (opcional)
            
        Returns:
            Tupla con mejores parámetros y mejor score
        """
        logger.info(f"Optimizando hiperparámetros para {model_name}...")
        
        if n_trials is None:
            n_trials = self.config['optuna']['n_trials']
        
        # Crear estudio de Optuna
        study = optuna.create_study(
            direction=self.config['optuna']['direction'],
            study_name=f"{self.config['optuna']['study_name']}_{model_name}"
        )
        
        # Optimizar
        study.optimize(
            lambda trial: self.objective_function(
                trial, model_name, X_train, y_train, X_val, y_val
            ),
            n_trials=n_trials,
            show_progress_bar=True
        )
        
        best_params = study.best_params
        best_score = study.best_value
        
        logger.info(f"Mejores parámetros para {model_name}: {best_params}")
        logger.info(f"Mejor RMSE: {best_score:.4f}")
        
        return best_params, best_score
    
    def train_and_evaluate_model(
        self,
        model_name: str,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        optimize: bool = True
    ) -> Dict[str, Any]:
        """
        Entrena y evalúa un modelo completo
        
        Args:
            model_name: Nombre del modelo
            X_train, y_train: Datos de entrenamiento
            X_val, y_val: Datos de validación  
            X_test, y_test: Datos de prueba
            optimize: Si optimizar hiperparámetros
            
        Returns:
            Diccionario con resultados del modelo
        """
        with mlflow.start_run(run_name=f"{model_name}_experiment"):
            # Log parámetros del experimento
            mlflow.log_param("model_type", model_name)
            mlflow.log_param("optimize_hyperparams", optimize)
            
            if optimize:
                # Optimizar hiperparámetros
                best_params, best_val_score = self.optimize_hyperparameters(
                    model_name, X_train, y_train, X_val, y_val
                )
                
                # Log mejores parámetros
                for param, value in best_params.items():
                    mlflow.log_param(f"best_{param}", value)
                    
                mlflow.log_metric("best_val_rmse", best_val_score)
            else:
                # Usar parámetros por defecto
                best_params = {}
            
            # Entrenar modelo final
            logger.info(f"Entrenando modelo final {model_name}...")
            final_model = self.create_model(model_name, **best_params)
            final_model.fit(X_train, y_train)
            
            # Evaluar en validación
            val_metrics = self.evaluate_model(final_model, X_val, y_val)
            
            # Evaluar en test
            test_metrics = self.evaluate_model(final_model, X_test, y_test)
            
            # Log métricas
            for metric_name, value in val_metrics.items():
                mlflow.log_metric(f"val_{metric_name}", value)
                
            for metric_name, value in test_metrics.items():
                mlflow.log_metric(f"test_{metric_name}", value)
            
            # Guardar modelo
            model_path = f"models/{model_name}_best_model.joblib"
            joblib.dump(final_model, model_path)
            mlflow.log_artifact(model_path)
            
            # Crear ejemplo de entrada para la firma del modelo
            input_example = X_train.head(5)  # Primeras 5 filas como ejemplo
            
            # Log modelo en MLflow con ejemplo de entrada
            mlflow.sklearn.log_model(
                final_model,
                f"{model_name}_model",
                input_example=input_example
            )
            
            logger.info(f"Modelo {model_name} entrenado y guardado")
            logger.info(f"Test RMSE: {test_metrics['rmse']:.4f}")
            logger.info(f"Test R²: {test_metrics['r2']:.4f}")
            
            return {
                'model_name': model_name,
                'model': final_model,
                'best_params': best_params if optimize else {},
                'val_metrics': val_metrics,
                'test_metrics': test_metrics,
                'model_path': model_path
            }
