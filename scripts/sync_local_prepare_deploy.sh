#!/bin/bash
# =============================================================================
# prepare_deploy.sh - Preparar despliegue: subir cambios locales a main remoto
# =============================================================================
#
# QUÉ HACE:
#   Toma los cambios hechos en ubuntu-house (rama dev_local_inv-img), los
#   mergea en main, sube main al remoto (GitHub) y deja develop y
#   dev_local_inv-img sincronizados. Listo para que ejecutes el deploy en
#   el VPS Hostinger.
#
# CÓMO USAR:
#   ./scripts/sync_local_prepare_deploy.sh
#   ./scripts/sync_local_prepare_deploy.sh "feat: mi mensaje"     # solo mensaje (rama por defecto)
#   ./scripts/sync_local_prepare_deploy.sh develop "feat: foo"    # rama + mensaje
#
# FLUJO:
#   0. Si hay cambios sin commitear: git add . + git commit (automático)
#   1. Fetch + pull origin/main (traer últimos cambios del remoto)
#   2. Merge dev_local_inv-img → main
#   3. Push main → origin/main (sube a GitHub)
#   4. Merge main → develop, push develop
#   5. Merge main → dev_local_inv-img, push dev_local_inv-img
#
# DESPUÉS:
#   En el VPS Hostinger ejecuta:
#     cd /opt/chalanpro && sudo ./scripts/deploy-vps.sh
#
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

DEFAULT_MSG="chore: preparar deploy VPS"
# Si solo hay 1 arg y contiene ":" → es mensaje (rama por defecto)
if [ -n "$1" ] && [ -z "$2" ] && [[ "$1" == *":"* ]]; then
    SOURCE_BRANCH="dev_local_inv-img"
    COMMIT_MSG="$1"
else
    SOURCE_BRANCH="${1:-dev_local_inv-img}"
    COMMIT_MSG="${2:-$DEFAULT_MSG}"
fi
CURRENT_BRANCH=$(git branch --show-current)

echo -e "${BLUE}=== Preparar despliegue (ubuntu-house → main remoto) ===${NC}"
echo ""
echo "Rama con cambios: $SOURCE_BRANCH"
echo "Rama actual:      $CURRENT_BRANCH"
echo ""

# Verificar que la rama fuente existe
if ! git show-ref --verify --quiet refs/heads/"$SOURCE_BRANCH"; then
    echo -e "${RED}✗ La rama $SOURCE_BRANCH no existe${NC}"
    exit 1
fi

# Si hay cambios sin commitear, hacer commit automático
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "${YELLOW}[0/5] Hay cambios sin commitear. Haciendo commit automático...${NC}"
    git add .
    git commit -m "$COMMIT_MSG"
    echo -e "${GREEN}✓ Commit realizado: $COMMIT_MSG${NC}"
    echo ""
fi

# Confirmación
echo -e "${YELLOW}Se mergeará $SOURCE_BRANCH en main y se subirá a origin/main${NC}"
echo -e "${YELLOW}Luego podrás ejecutar deploy-vps.sh en el VPS Hostinger${NC}"
echo ""
read -p "¿Continuar? (s/N): " -r
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Cancelado."
    exit 0
fi
echo ""

# 1. Fetch y actualizar main
echo -e "${YELLOW}[1/5] Fetch + pull origin/main...${NC}"
git fetch origin
git checkout main
git pull origin main
echo -e "${GREEN}✓ main actualizado con remoto${NC}"
echo ""

# 2. Merge rama fuente en main
echo -e "${YELLOW}[2/5] Merge $SOURCE_BRANCH → main...${NC}"
git merge "$SOURCE_BRANCH" -m "Merge $SOURCE_BRANCH: preparar deploy VPS"
echo -e "${GREEN}✓ main actualizado con cambios de $SOURCE_BRANCH${NC}"
echo ""

# 3. Push main a origin
echo -e "${YELLOW}[3/5] Push main → origin/main...${NC}"
git push origin main
echo -e "${GREEN}✓ main subido a GitHub${NC}"
echo ""

# 4. Actualizar develop
echo -e "${YELLOW}[4/5] Actualizar develop...${NC}"
if git show-ref --verify --quiet refs/heads/develop; then
    git checkout develop
    git pull origin develop 2>/dev/null || true
    git merge main -m "Merge main: sync pre-deploy"
    git push origin develop
    echo -e "${GREEN}✓ develop actualizado y subido${NC}"
else
    echo -e "${YELLOW}  (rama develop no existe, omitiendo)${NC}"
fi
echo ""

# 5. Actualizar dev_local_inv-img (sincronizar con main)
echo -e "${YELLOW}[5/5] Sincronizar $SOURCE_BRANCH con main...${NC}"
git checkout "$SOURCE_BRANCH"
git merge main -m "Merge main: sync post-deploy"
git push origin "$SOURCE_BRANCH"
echo -e "${GREEN}✓ $SOURCE_BRANCH sincronizado y subido${NC}"
echo ""

# Volver a la rama original
if [ -n "$CURRENT_BRANCH" ] && [ "$CURRENT_BRANCH" != "$(git branch --show-current)" ]; then
    git checkout "$CURRENT_BRANCH"
fi

echo ""
echo -e "${GREEN}=== Listo para desplegar ===${NC}"
echo ""
echo "En el VPS Hostinger ejecuta:"
echo -e "  ${YELLOW}cd /opt/chalanpro && sudo ./scripts/deploy-vps.sh${NC}"
echo ""
echo "Últimos commits en main:"
git log --oneline -5 main
