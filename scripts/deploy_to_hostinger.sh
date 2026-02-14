#!/bin/bash
# Despliegue en VPS Hostinger: pull de main y reinicio de servicios.
# Ejecutar desde local después de: git push origin main
# Uso: ./scripts/deploy_to_hostinger.sh [--migrate]

set -e

VPS_USER="${VPS_USER:-ubuntu}"
VPS_HOST="${VPS_HOST:-72.60.168.62}"
VPS_PATH="${VPS_PATH:-/opt/chalanpro}"
SSH_TARGET="${VPS_USER}@${VPS_HOST}"

RUN_MIGRATE=false
for arg in "$@"; do
    if [ "$arg" = "--migrate" ]; then
        RUN_MIGRATE=true
        break
    fi
done

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}=== Despliegue en VPS Hostinger ===${NC}"
echo "  SSH: $SSH_TARGET"
echo "  Ruta: $VPS_PATH"
echo ""

# Comprobar que main local está actualizado (aviso)
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    CURRENT=$(git branch --show-current 2>/dev/null || true)
    if [ -n "$CURRENT" ] && [ "$CURRENT" != "main" ]; then
        echo -e "${YELLOW}⚠ Rama actual: $CURRENT. Asegúrate de haber hecho push de main.${NC}"
    fi
    git fetch origin main 2>/dev/null || true
    LOCAL=$(git rev-parse main 2>/dev/null || true)
    REMOTE=$(git rev-parse origin/main 2>/dev/null || true)
    if [ -n "$LOCAL" ] && [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
        echo -e "${YELLOW}⚠ main local ($LOCAL) no coincide con origin/main ($REMOTE).${NC}"
        echo "  Considera: git checkout main && git pull origin main && git push origin main"
        read -p "¿Continuar con el despliegue igualmente? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Despliegue cancelado."
            exit 0
        fi
    fi
fi

echo -e "${GREEN}[1/3] Conectando al VPS y actualizando código...${NC}"
ssh "$SSH_TARGET" "cd $VPS_PATH && git fetch origin && git checkout main && git pull origin main"

echo -e "${GREEN}[2/3] Reiniciando servicios...${NC}"
ssh "$SSH_TARGET" "cd $VPS_PATH && docker compose restart backend frontend nginx"

if [ "$RUN_MIGRATE" = true ]; then
    echo -e "${GREEN}[3/3] Ejecutando migraciones...${NC}"
    ssh "$SSH_TARGET" "cd $VPS_PATH && docker compose exec -T backend python manage.py migrate --noinput"
else
    echo -e "${YELLOW}[3/3] Migraciones omitidas (usa --migrate si hay nuevas migraciones).${NC}"
fi

echo ""
echo -e "${GREEN}=== Despliegue completado ===${NC}"
echo "Comprobar en el VPS: docker compose ps"
echo "URLs: https://chalanpro.net | https://api.chalanpro.net"
