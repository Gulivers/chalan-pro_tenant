#!/bin/bash
# Renovación/obtención automática de wildcard con DNS-01 (Hostinger API).
# Uso:
#   export HOSTINGER_API_TOKEN="tu_token"
#   sudo -E /opt/chalanpro/scripts/renew_wildcard_certbot_auto_domain.sh --domain jobrithm.net --email admin@jobrithm.net

set -euo pipefail

DOMAIN=""
EMAIL=""
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AUTH_HOOK="${SCRIPT_DIR}/certbot_hostinger_auth.py"
CLEANUP_HOOK="${SCRIPT_DIR}/certbot_hostinger_cleanup.py"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain)
      DOMAIN="$2"
      shift 2
      ;;
    --email)
      EMAIL="$2"
      shift 2
      ;;
    *)
      echo "Parámetro no reconocido: $1"
      exit 1
      ;;
  esac
done

if [[ -z "${DOMAIN}" || -z "${EMAIL}" ]]; then
  echo "Uso: $0 --domain <dominio> --email <email>"
  exit 1
fi

if [[ -z "${HOSTINGER_API_TOKEN:-}" && -z "${BEARER_TOKEN:-}" ]]; then
  echo "Define HOSTINGER_API_TOKEN o BEARER_TOKEN antes de ejecutar este script."
  exit 1
fi

if [[ ! -f "$AUTH_HOOK" || ! -f "$CLEANUP_HOOK" ]]; then
  echo "No se encuentran los hooks en $SCRIPT_DIR"
  exit 1
fi

sudo -E certbot certonly \
  --manual \
  --preferred-challenges dns \
  -d "$DOMAIN" \
  -d "*.$DOMAIN" \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  --manual-auth-hook "$AUTH_HOOK" \
  --manual-cleanup-hook "$CLEANUP_HOOK" \
  --force-renewal

echo ""
echo "✓ Certificado emitido/renovado para $DOMAIN y *.$DOMAIN"
echo "Reiniciando nginx..."
cd /opt/chalanpro && docker compose restart nginx
echo "✓ Listo."
