#!/bin/bash
# ============================================================================
# process_search_outbox_cron.sh – IndexOutbox para todos los tenants activos
# ============================================================================
# Ejecuta process_index_outbox_all dentro del contenedor backend vía docker compose.
# Diseñado para cron en el HOST (no dentro del contenedor).
#
# Producción (Hostinger VPS):
#   */3 * * * * root /opt/chalanpro/scripts/process_search_outbox_cron.sh
#
# Desarrollo (ubuntu-house):
#   ./scripts/process_search_outbox_cron.sh --dev
#   */3 * * * * oliver cd /home/oliver/shared/projects/chalanpro && ./scripts/process_search_outbox_cron.sh --dev
#
# Variables opcionales:
#   CHALANPRO_ROOT          Raíz del repo (default: padre de scripts/)
#   CHALANPRO_COMPOSE_FILE  docker-compose.yml | docker-compose.dev.yml
#   CHALANPRO_LOG_DIR       Directorio de logs (default VPS: /var/log/chalanpro)
#   SEARCH_OUTBOX_LIMIT     --limit del management command (default: 200)
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${CHALANPRO_ROOT:-$(dirname "$SCRIPT_DIR")}"
COMPOSE_FILE="${CHALANPRO_COMPOSE_FILE:-docker-compose.yml}"
LOG_DIR="${CHALANPRO_LOG_DIR:-/var/log/chalanpro}"
LIMIT="${SEARCH_OUTBOX_LIMIT:-200}"

if [[ "${1:-}" == "--dev" ]]; then
    COMPOSE_FILE="docker-compose.dev.yml"
    LOG_DIR="${CHALANPRO_LOG_DIR:-${PROJECT_ROOT}/logs}"
fi

LOG_FILE="${LOG_DIR}/search-outbox.log"
LOCK_FILE="${LOG_DIR}/search-outbox.lock"

mkdir -p "$LOG_DIR"

exec 200>"$LOCK_FILE"
if ! flock -n 200; then
    echo "$(date -Iseconds) [search-outbox] Skip: previous run still active" >>"$LOG_FILE"
    exit 0
fi

{
    echo "$(date -Iseconds) [search-outbox] Start root=${PROJECT_ROOT} compose=${COMPOSE_FILE} limit=${LIMIT}"
    cd "$PROJECT_ROOT"

    if [[ ! -f "$COMPOSE_FILE" ]]; then
        echo "$(date -Iseconds) [search-outbox] ERROR: compose file not found: ${PROJECT_ROOT}/${COMPOSE_FILE}"
        exit 1
    fi

    docker compose -f "$COMPOSE_FILE" exec -T backend \
        python manage.py process_index_outbox_all --limit "$LIMIT"

    echo "$(date -Iseconds) [search-outbox] Done"
} >>"$LOG_FILE" 2>&1
