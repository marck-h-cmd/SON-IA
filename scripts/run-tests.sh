#!/bin/bash
# ============================================
# SON-IA: Script para ejecutar tests
# ============================================

set -e

echo "🧪 SON-IA: Ejecutando tests..."
echo "================================"

cd backend
source venv/bin/activate 2>/dev/null || true

# Opciones
COVERAGE=${1:-false}
VERBOSE=${2:-false}

PYTEST_ARGS="-v"

if [ "$VERBOSE" = "true" ]; then
    PYTEST_ARGS="$PYTEST_ARGS -s"
fi

if [ "$COVERAGE" = "true" ]; then
    echo "📊 Ejecutando tests con coverage..."
    pytest $PYTEST_ARGS --cov=app --cov-report=html --cov-report=term
    echo "📊 Reporte HTML generado en: backend/htmlcov/index.html"
else
    echo "🧪 Ejecutando tests..."
    pytest $PYTEST_ARGS
fi

echo "✅ Tests completados!"