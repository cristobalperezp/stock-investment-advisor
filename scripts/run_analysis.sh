#!/bin/bash
# Ejecuta el análisis completo desde la terminal cargando variables desde .env

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ -f ".env" ]]; then
  # Exporta todo el contenido de .env para que python-dotenv y os.getenv lo usen
  set -a
  # shellcheck disable=SC1091
  source ".env"
  set +a
else
  echo "⚠️  Archivo .env no encontrado en $PROJECT_ROOT. Se usarán variables del entorno actual." >&2
fi

BUDGET="${1:-1000000}"
RISK_LEVEL="${2:-moderado}"
DIVIDEND_PREF="${3:-true}"
TOP_COUNT="${4:-10}"
DIVIDEND_PREF_LOWER="$(printf '%s' "$DIVIDEND_PREF" | tr '[:upper:]' '[:lower:]')"
if [[ "$DIVIDEND_PREF_LOWER" == "true" ]]; then
  DIVIDEND_FLAG="True"
else
  DIVIDEND_FLAG="False"
fi

echo "🚀 Ejecutando análisis con presupuesto $BUDGET CLP (riesgo: $RISK_LEVEL, dividendos: $DIVIDEND_PREF, top: $TOP_COUNT)"

PYTHONPATH="src" python3 - <<PY
from analysis.investment_analyzer import InvestmentAnalyzer

analyzer = InvestmentAnalyzer()
result = analyzer.run_complete_analysis_with_gpt(
    budget=int(${BUDGET}),
    risk_level="${RISK_LEVEL}",
    dividend_preference=${DIVIDEND_FLAG},
    top_stocks_count=int(${TOP_COUNT})
)

recs = result['recommendations']
print("\\n=== RECOMENDACIONES GENERADAS ===")
print(f"Fecha análisis: {recs['fecha_analisis']}")
print(f"Presupuesto: \${recs['presupuesto_total']:,}")
print(f"Total invertido: \${recs['total_invertido']:,}")
print(f"Empresas recomendadas: {recs['empresas_recomendadas']}")
for item in recs['distribucion']:
    print(f"- {item['Empresa']} ({item['Ticker']}): \${item['Monto_Inversion']:,} -> {item['Porcentaje_Recomendado']:.1f}%")

if result.get('gpt_analysis'):
    print("\\n=== RESUMEN GPT ===")
    print(result['gpt_analysis'][:800], "...")
PY
