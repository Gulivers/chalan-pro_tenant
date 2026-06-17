#!/bin/bash
# ============================================================================
# reindex_search_after_chunk_change.sh – Reindex + outbox tras cambios en chunk/metadata
# ============================================================================
# Ejecutar cuando cambie app/appsearch/services/chunk.py o campos indexados.
#
# ubuntu-house (un tenant):
#   ./scripts/reindex_search_after_chunk_change.sh --dev --schema test_dominio_local
#
# ubuntu-house (todos los tenants activos):
#   ./scripts/reindex_search_after_chunk_change.sh --dev --all-tenants
#
# Producción (VPS):
#   ./scripts/reindex_search_after_chunk_change.sh --schema MI_SCHEMA
#   ./scripts/reindex_search_after_chunk_change.sh --all-tenants
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${CHALANPRO_ROOT:-$(dirname "$SCRIPT_DIR")}"
COMPOSE_FILE="${CHALANPRO_COMPOSE_FILE:-docker-compose.yml}"
SCHEMA=""
ALL_TENANTS=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dev)
            COMPOSE_FILE="docker-compose.dev.yml"
            shift
            ;;
        --schema)
            SCHEMA="$2"
            shift 2
            ;;
        --all-tenants)
            ALL_TENANTS=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

if [[ "$ALL_TENANTS" != true && -z "$SCHEMA" ]]; then
    echo "Usage: $0 [--dev] (--schema NAME | --all-tenants)" >&2
    exit 1
fi

cd "$PROJECT_ROOT"

dc() {
    docker compose -f "$COMPOSE_FILE" exec -T backend "$@"
}

echo "[search-reindex] compose=${COMPOSE_FILE} processing outbox first..."
dc python manage.py process_index_outbox_all --limit 500

if [[ "$ALL_TENANTS" == true ]]; then
    echo "[search-reindex] reindex all active tenants..."
    dc python manage.py reindex_document_lines
else
    echo "[search-reindex] reindex schema=${SCHEMA}..."
    dc python manage.py reindex_document_lines --schema "$SCHEMA"
fi

echo "[search-reindex] Done."
