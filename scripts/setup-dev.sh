#!/bin/bash
# ============================================
# SON-IA: Script de configuración de desarrollo
# ============================================

set -e

echo "🚀 SON-IA: Configurando entorno de desarrollo..."
echo "================================================"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Verificar Python
echo -e "\n${YELLOW}📌 Verificando Python 3.11+...${NC}"
if command -v python3.11 &> /dev/null; then
    PYTHON=python3.11
elif command -v python3 &> /dev/null; then
    PYTHON=python3
else
    echo -e "${RED}❌ Python 3 no encontrado. Instálalo primero.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python: $($PYTHON --version)${NC}"

# 2. Crear entorno virtual
echo -e "\n${YELLOW}📌 Creando entorno virtual...${NC}"
cd backend
$PYTHON -m venv venv
source venv/bin/activate
echo -e "${GREEN}✅ Entorno virtual creado${NC}"

# 3. Instalar dependencias
echo -e "\n${YELLOW}📌 Instalando dependencias Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencias instaladas${NC}"

# 4. Configurar variables de entorno
echo -e "\n${YELLOW}📌 Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Archivo .env creado desde .env.example${NC}"
    echo -e "${YELLOW}⚠️  Edita .env con tus claves API reales${NC}"
else
    echo -e "${GREEN}✅ Archivo .env ya existe${NC}"
fi

# 5. Inicializar base de datos
echo -e "\n${YELLOW}📌 Inicializando base de datos...${NC}"
python ../scripts/seed-database.py 2>/dev/null || echo -e "${YELLOW}⚠️  Seed database omitido (requiere PostgreSQL)${NC}"

# 6. Entrenar modelos (opcional)
echo -e "\n${YELLOW}📌 ¿Entrenar modelos ML? (s/n)${NC}"
read -r train_models
if [ "$train_models" = "s" ]; then
    echo "Entrenando modelos..."
    python app/training/train_score_confianza.py
    python app/training/train_prediccion_pago.py
    echo -e "${GREEN}✅ Modelos entrenados${NC}"
fi

cd ..

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}✅ SON-IA Backend configurado exitosamente!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "\nPara iniciar el servidor:"
echo -e "  cd backend && source venv/bin/activate"
echo -e "  uvicorn app.main:app --reload --port 8000"
echo -e "\nAcceder a:"
echo -e "  API:        http://localhost:8000"
echo -e "  Docs:       http://localhost:8000/api/docs"
echo -e "  Health:     http://localhost:8000/api/v1/health"