#!/bin/bash
# ============================================================================
# deploy-vps.sh – Deploy idempotente en VPS (Hostinger / Ubuntu 24.04)
# ============================================================================
# Uso: sudo /opt/chalanpro/scripts/deploy-vps.sh [--no-pull] [--no-build] [--no-migrate]
#
# Ejecutar desde el VPS. Por defecto:
#   - git pull origin main
#   - build de backend y frontend
#   - up de servicios en orden, migraciones, collectstatic, restart
#
# --no-pull    No hace git pull (útil si ya actualizaste el código)
# --no-build   No hace docker compose build (solo restart; útil para cambios solo en .env)
# --no-migrate No ejecuta migrate_schemas (cuando no hay cambios en modelos; ahorra tiempo y evita tocar schemas)
# ============================================================================

set -e

PROJECT_ROOT="/opt/chalanpro"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
LOG_PREFIX="[deploy-vps]"

# Opciones
DO_PULL=1
DO_BUILD=1
DO_MIGRATE=1
for arg in "$@"; do
    case "$arg" in
        --no-pull)   DO_PULL=0 ;;
        --no-build)  DO_BUILD=0 ;;
        --no-migrate) DO_MIGRATE=0 ;;
    esac
done

cd "$PROJECT_ROOT"

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "$LOG_PREFIX ERROR: No se encontró $COMPOSE_FILE"
    exit 1
fi

echo "$LOG_PREFIX Iniciando deploy en $(hostname) — $(date -Iseconds)"

# --- Git (solo main)
if [ "$DO_PULL" -eq 1 ]; then
    echo "$LOG_PREFIX Git fetch + checkout main + pull..."
    git fetch origin
    git checkout main
    git pull origin main
else
    echo "$LOG_PREFIX Omitting git pull (--no-pull)"
fi

# --- Build (opcional)
if [ "$DO_BUILD" -eq 1 ]; then
    echo "$LOG_PREFIX Building backend and frontend..."
    docker compose -f "$COMPOSE_FILE" build --no-cache backend frontend
fi

# --- Orden de arranque y migraciones
echo "$LOG_PREFIX Bringing up postgres..."
docker compose -f "$COMPOSE_FILE" up -d postgres

echo "$LOG_PREFIX Waiting for Postgres (15s)..."
sleep 15

echo "$LOG_PREFIX Bringing up backend..."
docker compose -f "$COMPOSE_FILE" up -d backend

if [ "$DO_MIGRATE" -eq 1 ]; then
    echo "$LOG_PREFIX Running migrations (multi-tenant: migrate_schemas)..."
    docker compose -f "$COMPOSE_FILE" exec -T backend python manage.py migrate_schemas
else
    echo "$LOG_PREFIX Omitting migrate_schemas (--no-migrate)"
fi

echo "$LOG_PREFIX Collectstatic..."
docker compose -f "$COMPOSE_FILE" exec -T backend python manage.py collectstatic --noinput

echo "$LOG_PREFIX Bringing up frontend (build may take a while)..."
docker compose -f "$COMPOSE_FILE" up -d frontend

echo "$LOG_PREFIX Waiting for frontend build (30s)..."
sleep 30

echo "$LOG_PREFIX Bringing up nginx..."
docker compose -f "$COMPOSE_FILE" up -d nginx

echo "$LOG_PREFIX Restarting backend, frontend, nginx..."
docker compose -f "$COMPOSE_FILE" restart backend frontend nginx

echo "$LOG_PREFIX Deploy finished — $(date -Iseconds)"
echo "$LOG_PREFIX Check: docker compose -f $COMPOSE_FILE ps"
