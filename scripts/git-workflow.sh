#!/bin/bash
# Script de ayuda para Git Workflow - Chalan-Pro
# Uso: ./scripts/git-workflow.sh [comando]

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR/app"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de ayuda
show_help() {
    echo -e "${BLUE}Git Workflow Helper - Chalan-Pro${NC}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  status          - Mostrar estado actual de ramas"
    echo "  sync-main       - Sincronizar main con origin/main"
    echo "  sync-develop    - Sincronizar develop con origin/develop"
    echo "  create-feature  - Crear nueva rama de feature desde develop"
    echo "  merge-to-develop - Mergear rama actual a develop"
    echo "  merge-to-main   - Mergear develop a main (solo después de pruebas)"
    echo "  setup           - Configurar ramas iniciales (develop, ubuntu_house)"
    echo "  compare         - Comparar ramas (main vs develop)"
    echo ""
}

show_status() {
    echo -e "${BLUE}=== Estado Actual ===${NC}"
    echo ""
    echo -e "${YELLOW}Rama actual:${NC}"
    git branch --show-current
    echo ""
    echo -e "${YELLOW}Estado de ramas:${NC}"
    git branch -vv
    echo ""
    echo -e "${YELLOW}Commits no sincronizados:${NC}"
    git log --oneline --graph --all --decorate -10
    echo ""
    echo -e "${YELLOW}Archivos sin commit:${NC}"
    git status --short
}

sync_main() {
    echo -e "${BLUE}Sincronizando main...${NC}"
    git checkout main
    git fetch origin
    git pull origin main
    echo -e "${GREEN}✓ Main sincronizado${NC}"
}

sync_develop() {
    echo -e "${BLUE}Sincronizando develop...${NC}"
    if ! git show-ref --verify --quiet refs/heads/develop; then
        echo -e "${YELLOW}La rama develop no existe. Creándola desde main...${NC}"
        git checkout main
        git checkout -b develop
        git push -u origin develop
    else
        git checkout develop
        git fetch origin
        if git show-ref --verify --quiet refs/remotes/origin/develop; then
            git pull origin develop
        else
            echo -e "${YELLOW}develop no existe en remoto. Creándola...${NC}"
            git push -u origin develop
        fi
    fi
    echo -e "${GREEN}✓ Develop sincronizado${NC}"
}

create_feature() {
    read -p "Nombre de la feature (sin espacios, ej: schedule-fix): " feature_name
    if [ -z "$feature_name" ]; then
        echo -e "${RED}Error: Debes proporcionar un nombre${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Creando feature branch: feature/$feature_name${NC}"
    sync_develop
    git checkout -b "feature/$feature_name"
    echo -e "${GREEN}✓ Rama feature/$feature_name creada${NC}"
    echo -e "${YELLOW}Ahora puedes hacer tus cambios y commits${NC}"
}

merge_to_develop() {
    current_branch=$(git branch --show-current)
    if [ "$current_branch" = "main" ]; then
        echo -e "${RED}Error: No puedes mergear main directamente a develop${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}Mergeando $current_branch a develop...${NC}"
    sync_develop
    git merge "$current_branch" --no-ff
    echo -e "${GREEN}✓ Merge completado${NC}"
    read -p "¿Hacer push a origin/develop? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin develop
        echo -e "${GREEN}✓ Push completado${NC}"
    fi
}

merge_to_main() {
    echo -e "${YELLOW}⚠️  ADVERTENCIA: Esto mergeará develop a main${NC}"
    echo -e "${YELLOW}⚠️  Asegúrate de haber probado todo en ubuntu-house${NC}"
    read -p "¿Continuar? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelado"
        exit 0
    fi
    
    echo -e "${BLUE}Mergeando develop a main...${NC}"
    sync_main
    sync_develop
    git checkout main
    git merge develop --no-ff
    echo -e "${GREEN}✓ Merge completado${NC}"
    echo -e "${YELLOW}Revisa los cambios antes de hacer push:${NC}"
    git log --oneline -5
    read -p "¿Hacer push a origin/main? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        echo -e "${GREEN}✓ Push a main completado${NC}"
        echo -e "${YELLOW}⚠️  Recuerda hacer pull en el VPS Hostinger${NC}"
    fi
}

setup_branches() {
    echo -e "${BLUE}Configurando ramas iniciales...${NC}"
    
    # Sincronizar main
    sync_main
    
    # Crear/actualizar develop
    sync_develop
    
    # Crear/actualizar ubuntu_house
    if ! git show-ref --verify --quiet refs/heads/ubuntu_house; then
        echo -e "${BLUE}Creando rama ubuntu_house...${NC}"
        git checkout -b ubuntu_house
        echo -e "${GREEN}✓ Rama ubuntu_house creada${NC}"
    else
        echo -e "${BLUE}Actualizando rama ubuntu_house...${NC}"
        git checkout ubuntu_house
        if git show-ref --verify --quiet refs/remotes/origin/ubuntu_house; then
            git pull origin ubuntu_house
        fi
    fi
    
    echo -e "${GREEN}✓ Setup completado${NC}"
    echo ""
    echo -e "${YELLOW}Ramas configuradas:${NC}"
    git branch -a | grep -E "(main|develop|ubuntu_house)"
}

compare_branches() {
    echo -e "${BLUE}Comparando main y develop...${NC}"
    echo ""
    echo -e "${YELLOW}Commits en develop que no están en main:${NC}"
    git log main..develop --oneline || echo "No hay diferencias"
    echo ""
    echo -e "${YELLOW}Commits en main que no están en develop:${NC}"
    git log develop..main --oneline || echo "No hay diferencias"
    echo ""
    echo -e "${YELLOW}Archivos diferentes:${NC}"
    git diff --name-status main..develop || echo "No hay diferencias"
}

# Main
case "${1:-help}" in
    status)
        show_status
        ;;
    sync-main)
        sync_main
        ;;
    sync-develop)
        sync_develop
        ;;
    create-feature)
        create_feature
        ;;
    merge-to-develop)
        merge_to_develop
        ;;
    merge-to-main)
        merge_to_main
        ;;
    setup)
        setup_branches
        ;;
    compare)
        compare_branches
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Comando desconocido: $1${NC}"
        show_help
        exit 1
        ;;
esac

