# 🏠 Price Predictor - California Housing

Sistema de predicción de precios de viviendas usando Machine Learning con MLflow tracking, optimización de hiperparámetros con Optuna, y aplicación web interactiva con Streamlit.

## 📋 Descripción del Proyecto

Este proyecto implementa un sistema completo de predicción de precios para el dataset California Housing, incluyendo:

- **3 Modelos de ML**: Random Forest, LightGBM, y Linear Regression
- **Optimización de hiperparámetros** con Optuna (3 hiperparámetros por modelo)
- **Tracking de experimentos** con MLflow
- **Aplicación web interactiva** con Streamlit
- **Pipeline completo** de preprocesamiento y evaluación

## 🛠️ Stack Tecnológico

- **🐍 Python**: Lenguaje principal
- **🤖 Scikit-learn**: Modelos de ML
- **⚡ LightGBM**: Gradient boosting
- **🎯 Optuna**: Optimización de hiperparámetros  
- **📊 MLflow**: Tracking y versionado de experimentos
- **🎨 Streamlit**: Aplicación web interactiva
- **📈 Plotly**: Visualizaciones interactivas
- **🔧 Pandas/NumPy**: Manipulación de datos

## 📂 Estructura del Proyecto

```
Price Predictor/
├── config/
│   └── config.yaml              # Configuración del proyecto
├── data/
│   ├── raw/                     # Datos originales
│   └── processed/               # Datos procesados
├── models/                      # Modelos entrenados
├── mlruns/                      # MLflow tracking
├── notebooks/                   # Jupyter notebooks (análisis)
├── src/
│   ├── data/
│   │   └── data_loader.py       # Carga y preprocesamiento
│   ├── models/
│   │   ├── model_trainer.py     # Entrenamiento y optimización
│   │   └── train_models.py      # Script principal
│   ├── ui/
│   │   └── streamlit_app.py     # Aplicación web
│   └── utils/
│       └── config.py            # Utilidades de configuración
├── tests/                       # Tests unitarios
├── requirements.txt             # Dependencias Python
├── environment.yml              # Ambiente Conda
└── README.md                    # Documentación
```

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
cd "Price Predictor"
```

### 2. Crear ambiente virtual

**Opción A: Con Conda (Recomendado)**
```bash
conda env create -f environment.yml
conda activate price-predictor
```

**Opción B: Con pip**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Verificar instalación
```bash
python -c "import sklearn, lightgbm, optuna, mlflow, streamlit; print('✅ Todas las dependencias instaladas')"
```

## 🏃‍♂️ Uso del Sistema

### 1. Entrenar Modelos
```bash
python src/models/train_models.py
```

Este comando:
- 📥 Descarga y preprocesa el dataset Boston Housing
- 🔍 Optimiza hiperparámetros con Optuna (50 trials por modelo)
- 🤖 Entrena Random Forest, LightGBM y Linear Regression
- 📊 Registra experimentos en MLflow
- 💾 Guarda el mejor modelo de cada tipo
- 📈 Genera reporte de comparación

### 2. Ejecutar Aplicación Web
```bash
streamlit run src/ui/streamlit_app.py
```

Acceder a: **http://localhost:8501**

### 3. Ver Experimentos MLflow
```bash
mlflow ui
```

Acceder a: **http://localhost:5000**

## 🎯 Características de la Aplicación

### 📊 Dashboard Interactivo
- **Inputs dinámicos** para las 8 características del dataset
- **Predicción en tiempo real** con el mejor modelo
- **Visualización gauge** del precio estimado
- **Gráfico de importancia** de features
- **Información contextual** de cada variable

### 🏠 Variables del Dataset
| Variable | Descripción |
|----------|-------------|
| **MedInc** | Ingreso mediano (en 10k USD) |
| **HouseAge** | Edad mediana de las casas |
| **AveRooms** | Promedio de habitaciones por hogar |
| **AveBedrms** | Promedio de dormitorios por hogar |
| **Population** | Población del grupo de bloques |
| **AveOccup** | Promedio de ocupantes por hogar |
| **Latitude** | Latitud geográfica |
| **Longitude** | Longitud geográfica |

## ⚙️ Configuración Avanzada

### Hiperparámetros Optimizados

**Random Forest:**
- `n_estimators`: 10-200
- `max_depth`: 5-20  
- `min_samples_split`: 2-10

**LightGBM:**
- `n_estimators`: 10-200
- `max_depth`: 3-10
- `learning_rate`: 0.01-0.3

**Linear Regression:**
- `fit_intercept`: True/False
- `copy_X`: True/False

### MLflow Tracking
Cada experimento registra:
- ✅ Hiperparámetros optimizados
- ✅ Métricas de validación y test
- ✅ Modelo serializado
- ✅ Artifacts y logs

## 📈 Métricas de Evaluación

- **RMSE** (Root Mean Square Error): Error cuadrático medio
- **MAE** (Mean Absolute Error): Error absoluto medio  
- **R²** (R-squared): Coeficiente de determinación

## 🔧 Desarrollo y Testing

### Ejecutar Tests
```bash
python -m pytest tests/ -v
```

### Estructura de Desarrollo
```bash
src/
├── data/           # Módulos de datos
├── models/         # Módulos de modelos
├── features/       # Feature engineering
├── ui/            # Interfaz de usuario
└── utils/         # Utilidades generales
```

## 🚨 Troubleshooting

### Problema: Error al cargar dataset
**Solución**: Usa California Housing dataset que está disponible:
```bash
# El código ya está actualizado para usar fetch_california_housing
```

### Problema: MLflow no encuentra experimentos
**Solución**: Verificar que existe el directorio `mlruns/`:
```bash
mkdir -p mlruns
```

### Problema: Streamlit no carga modelos
**Solución**: Ejecutar primero el entrenamiento:
```bash
python src/models/train_models.py
```

## 🎯 Roadmap y Mejoras

- [ ] **Validación cruzada** k-fold
- [ ] **Más modelos**: XGBoost, Neural Networks
- [ ] **Feature engineering** avanzado
- [ ] **Dockerización** del proyecto
- [ ] **CI/CD** con GitHub Actions
- [ ] **Deploy** en Streamlit Cloud
- [ ] **API REST** con FastAPI

## 🤝 Contribuciones

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📧 Contacto

**Desarrollador**: Tu Nombre  
**Email**: tu.email@ejemplo.com  
**LinkedIn**: [tu-perfil](https://linkedin.com/in/tu-perfil)

---

<div align="center">

**🏠 Price Predictor** | *Predicción inteligente de precios inmobiliarios*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)](https://streamlit.io/)
[![MLflow](https://img.shields.io/badge/MLflow-2.5+-green.svg)](https://mlflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>
