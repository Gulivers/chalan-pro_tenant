#!/bin/bash
# Script para mantener main local sincronizado con main remoto
# Uso: ./scripts/sync_main_with_remote.sh

set -e  # Salir si hay algún error

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/oliver/shared/projects/chalanpro"

echo -e "${GREEN}=== Sincronizando main local con main remoto ===${NC}"
echo ""

cd "$PROJECT_DIR"

# Verificar que estamos en un repositorio Git
if [ ! -d ".git" ]; then
    echo -e "${RED}✗ Error: No se encontró un repositorio Git${NC}"
    exit 1
fi

# Guardar la rama actual
CURRENT_BRANCH=$(git branch --show-current)
echo "Rama actual: $CURRENT_BRANCH"
echo ""

# Cambiar a main
echo -e "${YELLOW}[1/3] Cambiando a rama main...${NC}"
git checkout main

# Obtener últimos cambios del remoto
echo -e "${YELLOW}[2/3] Obteniendo cambios del remoto...${NC}"
git fetch origin main

# Verificar si hay diferencias
LOCAL_COMMIT=$(git rev-parse main)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo -e "${GREEN}✓ main local ya está sincronizado con origin/main${NC}"
    echo ""
    echo "Último commit: $(git log -1 --oneline)"
else
    echo -e "${YELLOW}[3/3] Sincronizando main local con origin/main...${NC}"
    echo "Commit local:  $(git log -1 --oneline main)"
    echo "Commit remoto: $(git log -1 --oneline origin/main)"
    echo ""
    
    # Verificar si hay cambios sin commitear
    if ! git diff-index --quiet HEAD --; then
        echo -e "${RED}⚠ Advertencia: Hay cambios sin commitear en main${NC}"
        echo "¿Deseas descartarlos y sincronizar con remoto? (s/N)"
        read -r response
        if [[ "$response" =~ ^[Ss]$ ]]; then
            git reset --hard origin/main
            echo -e "${GREEN}✓ main local sincronizado con origin/main (cambios locales descartados)${NC}"
        else
            echo "Operación cancelada. Guarda tus cambios antes de sincronizar."
            git checkout "$CURRENT_BRANCH" 2>/dev/null || true
            exit 1
        fi
    else
        # Sincronizar con remoto
        git reset --hard origin/main
        echo -e "${GREEN}✓ main local sincronizado con origin/main${NC}"
    fi
fi

# Volver a la rama original si no era main
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo ""
    echo -e "${YELLOW}Volviendo a la rama original: $CURRENT_BRANCH${NC}"
    git checkout "$CURRENT_BRANCH" 2>/dev/null || echo "No se pudo volver a $CURRENT_BRANCH"
fi

echo ""
echo -e "${GREEN}=== Sincronización completada ===${NC}"
echo ""
echo "Estado actual:"
git log --oneline -3

