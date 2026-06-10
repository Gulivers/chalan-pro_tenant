#!/bin/bash
# ============================================================================
# run_search_eval.sh – Golden queries / search_eval para un tenant
# ============================================================================
# Uso (ubuntu-house):
#   ./scripts/run_search_eval.sh --dev test_dominio_local
#   ./scripts/run_search_eval.sh --dev test_dominio_local --fail-under 0.95
#
# Actualizar baseline tras cambios intencionados en datos o lógica:
#   ./scripts/run_search_eval.sh --dev test_dominio_local --update-baseline
#
# Variables:
#   CHALANPRO_ROOT, CHALANPRO_COMPOSE_FILE (igual que process_search_outbox_cron.sh)
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${CHALANPRO_ROOT:-$(dirname "$SCRIPT_DIR")}"
COMPOSE_FILE="${CHALANPRO_COMPOSE_FILE:-docker-compose.yml}"

DEV_MODE=false
UPDATE_BASELINE=false
FAIL_UNDER=""
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dev)
            DEV_MODE=true
            COMPOSE_FILE="docker-compose.dev.yml"
            shift
            ;;
        --update-baseline)
            UPDATE_BASELINE=true
            shift
            ;;
        --fail-under)
            FAIL_UNDER="$2"
            shift 2
            ;;
        --schema)
            SCHEMA="$2"
            shift 2
            ;;
        *)
            if [[ -z "${SCHEMA:-}" ]]; then
                SCHEMA="$1"
            else
                EXTRA_ARGS+=("$1")
            fi
            shift
            ;;
    esac
done

if [[ -z "${SCHEMA:-}" ]]; then
    echo "Usage: $0 [--dev] [--update-baseline] [--fail-under 0.95] SCHEMA" >&2
    exit 1
fi

cd "$PROJECT_ROOT"

CMD=(docker compose -f "$COMPOSE_FILE" exec -T backend
    python manage.py search_eval --schema "$SCHEMA")

if [[ -n "$FAIL_UNDER" ]]; then
    CMD+=(--fail-under "$FAIL_UNDER")
fi
if [[ "$UPDATE_BASELINE" == true ]]; then
    CMD+=(--update-baseline)
fi
CMD+=("${EXTRA_ARGS[@]}")

echo "[search-eval] schema=${SCHEMA} compose=${COMPOSE_FILE}"
"${CMD[@]}"
