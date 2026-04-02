#!/bin/bash
# ============================================================================
# deploy-landing-vps.sh – Deploy mínimo de landing en VPS
# ============================================================================
# Objetivo:
#   Desplegar cambios de landing sin tocar backend/migraciones.
#
# Flujo:
#   1) (Opcional) Actualiza código de main (fetch + checkout + pull --ff-only)
#   2) Reinicia nginx para servir la última versión estática de landing/dist
#   3) Ejecuta smoke test HTTP(S) de la URL de landing
#
# Uso:
#   sudo /opt/chalanpro/scripts/deploy-landing-vps.sh
#   sudo /opt/chalanpro/scripts/deploy-landing-vps.sh --no-pull
#   sudo /opt/chalanpro/scripts/deploy-landing-vps.sh --url https://www.getjobrithm.com
# ============================================================================

set -euo pipefail

PROJECT_ROOT="/opt/chalanpro"
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
LOG_PREFIX="[deploy-landing-vps]"
LANDING_URL="https://getjobrithm.com"
DO_PULL=1

for arg in "$@"; do
    case "$arg" in
        --no-pull)
            DO_PULL=0
            ;;
        --url=*)
            LANDING_URL="${arg#*=}"
            ;;
        --url)
            echo "$LOG_PREFIX ERROR: Usa --url=https://dominio"
            exit 1
            ;;
        *)
            echo "$LOG_PREFIX ERROR: Opción no soportada: $arg"
            echo "$LOG_PREFIX Uso: $0 [--no-pull] [--url=https://dominio]"
            exit 1
            ;;
    esac
done

cd "$PROJECT_ROOT"

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "$LOG_PREFIX ERROR: No se encontró $COMPOSE_FILE"
    exit 1
fi

echo "$LOG_PREFIX Inicio: $(date -Iseconds)"

if [ "$DO_PULL" -eq 1 ]; then
    echo "$LOG_PREFIX Paso 1/3: actualizar main desde origin..."
    git fetch origin
    git checkout main
    git pull --ff-only origin main
else
    echo "$LOG_PREFIX Paso 1/3: omitido (--no-pull)"
fi

echo "$LOG_PREFIX Paso 2/3: reiniciar nginx..."
docker compose -f "$COMPOSE_FILE" restart nginx

echo "$LOG_PREFIX Paso 3/3: smoke test landing en $LANDING_URL ..."
# Reintentos para tolerar la ventana corta durante restart de nginx.
MAX_RETRIES=10
SLEEP_SECONDS=2
HTTP_CODE="000"
for attempt in $(seq 1 "$MAX_RETRIES"); do
    HTTP_CODE="$(curl -k -sS -o /dev/null -w "%{http_code}" "$LANDING_URL" || true)"
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
        echo "$LOG_PREFIX OK: landing respondió HTTP $HTTP_CODE (intento $attempt/$MAX_RETRIES)"
        break
    fi
    echo "$LOG_PREFIX Esperando disponibilidad... intento $attempt/$MAX_RETRIES (HTTP $HTTP_CODE)"
    sleep "$SLEEP_SECONDS"
done

if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "301" ] && [ "$HTTP_CODE" != "302" ]; then
    echo "$LOG_PREFIX ERROR: smoke test falló tras $MAX_RETRIES intentos (último HTTP $HTTP_CODE)"
    exit 1
fi

echo "$LOG_PREFIX Finalizado: $(date -Iseconds)"
echo "$LOG_PREFIX Check manual: curl -I $LANDING_URL"
