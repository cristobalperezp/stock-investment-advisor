# Tests

Esta carpeta contiene las pruebas y scripts de verificación para el proyecto Stock Investment Advisor.

## Archivos de Prueba

### `check_system.py`
Script de verificación rápida que valida:
- Imports de librerías necesarias
- Funcionamiento del extractor de datos de Yahoo Finance
- Configuración del sistema
- Conectividad con fuentes de datos

**Uso:**
```bash
cd tests/
python check_system.py
```

### `test_volatility.py`
Pruebas específicas para la funcionalidad de cálculo de volatilidad:
- Verificación de datos históricos
- Cálculo de indicadores de volatilidad
- Validación de datos de salida

**Uso:**
```bash
cd tests/
python test_volatility.py
```

### `test_chart.py`
Pruebas para la generación de gráficos de volatilidad:
- Creación de gráficos Plotly
- Validación de datos de entrada
- Generación de archivos HTML de prueba

**Uso:**
```bash
cd tests/
python test_chart.py
```

## Estructura de Pruebas

Los archivos de prueba están organizados para:
1. **Verificar dependencias** y configuración del sistema
2. **Probar componentes individuales** del análisis financiero
3. **Validar la generación de visualizaciones**

## Ejecutar Todas las Pruebas

Para ejecutar todas las verificaciones:

```bash
# Desde el directorio raíz del proyecto
cd tests/

# Verificación general del sistema
python check_system.py

# Pruebas específicas
python test_volatility.py
python test_chart.py
```

## Notas

- Los archivos de prueba requieren que el entorno Python esté configurado
- Asegúrate de tener instaladas todas las dependencias (`pip install -r requirements.txt`)
- Los archivos utilizan paths relativos para encontrar el código fuente en `../src/`
