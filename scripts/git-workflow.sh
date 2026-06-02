#!/bin/bash
# Git Workflow Helper - Chalan-Pro / Jobrithm (ubuntu-house)
#
# Flujo habitual:
#   - Desarrollo y commits en dev_local_inv-img
#   - prepare-deploy: sube dev → main + sincroniza develop (despliegue desde main en VPS)
#   - sync-all: trae main/develop/dev desde origin (sin subir)
#
# Uso: ./scripts/git-workflow.sh [comando]

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

DEV_BRANCH="dev_local_inv-img"
MAIN_BRANCH="main"
DEVELOP_BRANCH="develop"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

show_help() {
    echo -e "${BLUE}Git Workflow Helper - Chalan-Pro (ubuntu-house)${NC}"
    echo ""
    echo "Rama de trabajo: ${DEV_BRANCH}"
    echo "Producción (VPS): ${MAIN_BRANCH}  |  Integración: ${DEVELOP_BRANCH}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  status            - Estado de ramas y cambios locales"
    echo "  sync-all          - Traer del remoto: main, develop y ${DEV_BRANCH}"
    echo "  prepare-deploy    - Subir ${DEV_BRANCH} → main + sync develop (listo para VPS)"
    echo "                      Opcional: mensaje de commit si hay cambios sin commitear"
    echo "  sync-main         - Actualizar ${MAIN_BRANCH} local desde origin"
    echo "  sync-develop      - Actualizar ${DEVELOP_BRANCH} desde origin y mergear ${MAIN_BRANCH}"
    echo "  sync-dev          - Actualizar ${DEV_BRANCH} desde origin y mergear ${MAIN_BRANCH}"
    echo "  push-dev          - Push de ${DEV_BRANCH} a origin (sin tocar main)"
    echo "  merge-to-develop  - Mergear ${DEV_BRANCH} (o rama actual) → ${DEVELOP_BRANCH}"
    echo "  merge-to-main     - Mergear ${DEV_BRANCH} → ${MAIN_BRANCH} + sync ${DEVELOP_BRANCH}"
    echo "  create-feature    - Nueva rama feature/* desde ${DEVELOP_BRANCH}"
    echo "  setup             - Configurar ${MAIN_BRANCH}, ${DEVELOP_BRANCH} y ${DEV_BRANCH}"
    echo "  compare           - Comparar ${MAIN_BRANCH}, ${DEVELOP_BRANCH} y ${DEV_BRANCH}"
    echo ""
    echo "Ejemplos:"
    echo "  $0 prepare-deploy"
    echo "  $0 prepare-deploy \"feat(inventory): descripción\""
    echo "  $0 sync-all"
    echo ""
}

require_clean_or_confirm() {
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        return 0
    fi
    echo -e "${RED}⚠ Hay cambios sin commitear${NC}"
    git status --short
    read -p "¿Continuar de todos modos? (s/N): " -r
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Cancelado."
        exit 1
    fi
}

show_status() {
    echo -e "${BLUE}=== Estado actual (ubuntu-house) ===${NC}"
    echo ""
    echo -e "${YELLOW}Rama actual:${NC} $(git branch --show-current)"
    echo ""
    echo -e "${YELLOW}Ramas principales:${NC}"
    git branch -vv | grep -E "^\*|${MAIN_BRANCH}|${DEVELOP_BRANCH}|${DEV_BRANCH}" || git branch -vv
    echo ""
    for pair in "${MAIN_BRANCH}:origin/${MAIN_BRANCH}" "${DEVELOP_BRANCH}:origin/${DEVELOP_BRANCH}" "${DEV_BRANCH}:origin/${DEV_BRANCH}"; do
        local="${pair%%:*}"
        remote="${pair##*:}"
        if git show-ref --verify --quiet "refs/heads/$local" 2>/dev/null; then
            ahead=$(git rev-list --count "${remote}..${local}" 2>/dev/null || echo "?")
            behind=$(git rev-list --count "${local}..${remote}" 2>/dev/null || echo "?")
            echo "  $local: ↑$ahead ↓$behind respecto a $remote"
        fi
    done
    echo ""
    echo -e "${YELLOW}Últimos commits:${NC}"
    git log --oneline --graph -8 "${MAIN_BRANCH}" "${DEVELOP_BRANCH}" "${DEV_BRANCH}" 2>/dev/null || git log --oneline -5
    echo ""
    echo -e "${YELLOW}Cambios sin commit:${NC}"
    git status --short
}

sync_main() {
    echo -e "${BLUE}Sincronizando ${MAIN_BRANCH}...${NC}"
    require_clean_or_confirm
    local current
    current=$(git branch --show-current)
    git fetch origin
    git checkout "$MAIN_BRANCH"
    git pull --no-rebase origin "$MAIN_BRANCH"
    if [ -n "$current" ] && [ "$current" != "$MAIN_BRANCH" ]; then
        git checkout "$current" 2>/dev/null || true
    fi
    echo -e "${GREEN}✓ ${MAIN_BRANCH} sincronizado con origin${NC}"
}

sync_develop() {
    echo -e "${BLUE}Sincronizando ${DEVELOP_BRANCH}...${NC}"
    require_clean_or_confirm
    local current
    current=$(git branch --show-current)
    git fetch origin
    if ! git show-ref --verify --quiet "refs/heads/${DEVELOP_BRANCH}"; then
        echo -e "${YELLOW}Creando ${DEVELOP_BRANCH} desde ${MAIN_BRANCH}...${NC}"
        git checkout "$MAIN_BRANCH"
        git checkout -b "$DEVELOP_BRANCH"
        git push -u origin "$DEVELOP_BRANCH"
    else
        git checkout "$DEVELOP_BRANCH"
        git pull --no-rebase origin "$DEVELOP_BRANCH" 2>/dev/null || true
        git merge "$MAIN_BRANCH" -m "Merge ${MAIN_BRANCH}: sync local"
        echo -e "${GREEN}✓ ${DEVELOP_BRANCH} actualizado (incluye ${MAIN_BRANCH})${NC}"
    fi
    if [ -n "$current" ] && [ "$current" != "$(git branch --show-current)" ]; then
        git checkout "$current" 2>/dev/null || true
    fi
}

sync_dev() {
    echo -e "${BLUE}Sincronizando ${DEV_BRANCH}...${NC}"
    require_clean_or_confirm
    local current
    current=$(git branch --show-current)
    git fetch origin
    if ! git show-ref --verify --quiet "refs/heads/${DEV_BRANCH}"; then
        echo -e "${RED}Error: la rama ${DEV_BRANCH} no existe. Ejecuta: $0 setup${NC}"
        exit 1
    fi
    git checkout "$DEV_BRANCH"
    git pull --no-rebase origin "$DEV_BRANCH"
    git merge "$MAIN_BRANCH" -m "Merge ${MAIN_BRANCH}: sync local"
    echo -e "${GREEN}✓ ${DEV_BRANCH} actualizado${NC}"
    if [ -n "$current" ] && [ "$current" != "$DEV_BRANCH" ]; then
        git checkout "$current" 2>/dev/null || true
    fi
}

push_dev() {
    local current
    current=$(git branch --show-current)
    if [ "$current" != "$DEV_BRANCH" ]; then
        echo -e "${YELLOW}Cambiando a ${DEV_BRANCH}...${NC}"
        git checkout "$DEV_BRANCH"
    fi
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo -e "${RED}Hay cambios sin commitear. Haz commit antes del push.${NC}"
        exit 1
    fi
    git push origin "$DEV_BRANCH"
    echo -e "${GREEN}✓ origin/${DEV_BRANCH} actualizado${NC}"
}

create_feature() {
    read -p "Nombre de la feature (ej: schedule-fix): " feature_name
    if [ -z "$feature_name" ]; then
        echo -e "${RED}Error: debes indicar un nombre${NC}"
        exit 1
    fi
    sync_develop
    git checkout -b "feature/$feature_name"
    echo -e "${GREEN}✓ Rama feature/$feature_name creada desde ${DEVELOP_BRANCH}${NC}"
}

merge_to_develop() {
    local source="${1:-$DEV_BRANCH}"
    local current
    current=$(git branch --show-current)

    if [ "$current" = "$MAIN_BRANCH" ] || [ "$current" = "$DEVELOP_BRANCH" ]; then
        echo -e "${YELLOW}Usando rama fuente: ${source}${NC}"
    elif [ "$current" != "$DEV_BRANCH" ] && [[ "$current" != feature/* ]]; then
        read -p "¿Mergear rama actual ($current) a ${DEVELOP_BRANCH}? (s/N): " -r
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            source="$current"
        fi
    else
        source="${current:-$DEV_BRANCH}"
    fi

    echo -e "${BLUE}Mergeando ${source} → ${DEVELOP_BRANCH}...${NC}"
    require_clean_or_confirm
    sync_develop
    git checkout "$DEVELOP_BRANCH"
    git merge "$source" --no-ff -m "Merge ${source}: integración develop"
    echo -e "${GREEN}✓ Merge completado${NC}"
    read -p "¿Push a origin/${DEVELOP_BRANCH}? (s/n): " -r
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        git push origin "$DEVELOP_BRANCH"
        echo -e "${GREEN}✓ Push completado${NC}"
    fi
    git checkout "$DEV_BRANCH" 2>/dev/null || true
}

merge_to_main() {
    local source="${1:-$DEV_BRANCH}"
    echo -e "${YELLOW}⚠️  Mergeará ${source} → ${MAIN_BRANCH} (producción / VPS)${NC}"
    echo -e "${YELLOW}⚠️  Prueba antes en ubuntu-house${NC}"
    read -p "¿Continuar? (s/N): " -r
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Cancelado"
        exit 0
    fi

    require_clean_or_confirm
    local current
    current=$(git branch --show-current)

    if ! git diff-index --quiet HEAD -- 2>/dev/null && [ "$current" = "$DEV_BRANCH" ]; then
        echo -e "${RED}Commitea en ${DEV_BRANCH} antes, o usa: $0 prepare-deploy \"mensaje\"${NC}"
        exit 1
    fi

    git fetch origin
    git checkout "$MAIN_BRANCH"
    git pull --no-rebase origin "$MAIN_BRANCH"
    git merge "$source" --no-ff -m "Merge ${source}: release a producción"
    echo -e "${GREEN}✓ Merge en ${MAIN_BRANCH} local${NC}"
    git log --oneline -3
    read -p "¿Push a origin/${MAIN_BRANCH}? (s/N): " -r
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        git push origin "$MAIN_BRANCH"
        echo -e "${GREEN}✓ origin/${MAIN_BRANCH} actualizado${NC}"
        if git show-ref --verify --quiet "refs/heads/${DEVELOP_BRANCH}"; then
            git checkout "$DEVELOP_BRANCH"
            git pull --no-rebase origin "$DEVELOP_BRANCH" 2>/dev/null || true
            git merge "$MAIN_BRANCH" -m "Merge ${MAIN_BRANCH}: sync post-release"
            read -p "¿Push a origin/${DEVELOP_BRANCH}? (s/n): " -r
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                git push origin "$DEVELOP_BRANCH"
            fi
        fi
        echo -e "${YELLOW}VPS: cd /opt/chalanpro && sudo ./scripts/deploy-vps.sh${NC}"
    fi
    git checkout "$DEV_BRANCH" 2>/dev/null || git checkout "$current" 2>/dev/null || true
}

setup_branches() {
    echo -e "${BLUE}Configurando ramas (${MAIN_BRANCH}, ${DEVELOP_BRANCH}, ${DEV_BRANCH})...${NC}"
    local current
    current=$(git branch --show-current)
    git fetch origin

    git checkout "$MAIN_BRANCH"
    git pull --no-rebase origin "$MAIN_BRANCH"
    echo -e "${GREEN}✓ ${MAIN_BRANCH}${NC}"

    if ! git show-ref --verify --quiet "refs/heads/${DEVELOP_BRANCH}"; then
        git checkout -b "$DEVELOP_BRANCH"
        git push -u origin "$DEVELOP_BRANCH"
    else
        git checkout "$DEVELOP_BRANCH"
        git pull --no-rebase origin "$DEVELOP_BRANCH" 2>/dev/null || true
        git merge "$MAIN_BRANCH" -m "Merge ${MAIN_BRANCH}: setup" || true
    fi
    echo -e "${GREEN}✓ ${DEVELOP_BRANCH}${NC}"

    if ! git show-ref --verify --quiet "refs/heads/${DEV_BRANCH}"; then
        git checkout -b "$DEV_BRANCH" "$DEVELOP_BRANCH"
        git push -u origin "$DEV_BRANCH"
    else
        git checkout "$DEV_BRANCH"
        git pull --no-rebase origin "$DEV_BRANCH" 2>/dev/null || true
        git merge "$MAIN_BRANCH" -m "Merge ${MAIN_BRANCH}: setup" || true
    fi
    echo -e "${GREEN}✓ ${DEV_BRANCH}${NC}"

    if [ -n "$current" ]; then
        git checkout "$current" 2>/dev/null || git checkout "$DEV_BRANCH"
    fi
    echo ""
    git branch -vv | grep -E "^\*|${MAIN_BRANCH}|${DEVELOP_BRANCH}|${DEV_BRANCH}" || true
}

compare_branches() {
    echo -e "${BLUE}Comparación de ramas${NC}"
    echo ""
    echo -e "${YELLOW}${DEVELOP_BRANCH} no está en ${MAIN_BRANCH}:${NC}"
    git log "${MAIN_BRANCH}..${DEVELOP_BRANCH}" --oneline 2>/dev/null | head -5 || echo "  (ninguno o ramas iguales)"
    echo ""
    echo -e "${YELLOW}${MAIN_BRANCH} no está en ${DEVELOP_BRANCH}:${NC}"
    git log "${DEVELOP_BRANCH}..${MAIN_BRANCH}" --oneline 2>/dev/null | head -5 || echo "  (ninguno o ramas iguales)"
    echo ""
    echo -e "${YELLOW}${DEV_BRANCH} no está en ${MAIN_BRANCH}:${NC}"
    git log "${MAIN_BRANCH}..${DEV_BRANCH}" --oneline 2>/dev/null | head -10 || echo "  (ninguno)"
    echo ""
    echo -e "${YELLOW}${MAIN_BRANCH} no está en ${DEV_BRANCH}:${NC}"
    git log "${DEV_BRANCH}..${MAIN_BRANCH}" --oneline 2>/dev/null | head -5 || echo "  (ninguno)"
}

sync_all() {
    if [ -x "$REPO_DIR/scripts/sync_local_branches.sh" ]; then
        exec "$REPO_DIR/scripts/sync_local_branches.sh"
    fi
    echo -e "${RED}No se encontró scripts/sync_local_branches.sh${NC}"
    exit 1
}

prepare_deploy() {
    if [ -x "$REPO_DIR/scripts/sync_local_prepare_deploy.sh" ]; then
        shift
        exec "$REPO_DIR/scripts/sync_local_prepare_deploy.sh" "$@"
    fi
    echo -e "${RED}No se encontró scripts/sync_local_prepare_deploy.sh${NC}"
    echo "Copia o recrea el script en ubuntu-house (está en .gitignore, solo local)."
    exit 1
}

case "${1:-help}" in
    status)
        show_status
        ;;
    sync-all)
        sync_all
        ;;
    prepare-deploy)
        prepare_deploy "$@"
        ;;
    sync-main)
        sync_main
        ;;
    sync-develop)
        sync_develop
        ;;
    sync-dev)
        sync_dev
        ;;
    push-dev)
        push_dev
        ;;
    create-feature)
        create_feature
        ;;
    merge-to-develop)
        merge_to_develop "${2:-}"
        ;;
    merge-to-main)
        merge_to_main "${2:-}"
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
