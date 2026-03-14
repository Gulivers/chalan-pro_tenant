#!/bin/bash
# Activa HTTPS para chalanpro.com (landing).
# Ejecutar DESPUÉS de que haya pasado el rate limit de Let's Encrypt (ver mensaje "retry after").
# Uso: sudo bash /opt/chalanpro/scripts/enable_https_chalanpro_com.sh

set -e
PROJECT_ROOT="/opt/chalanpro"
CONF="${PROJECT_ROOT}/nginx/default.conf"

cd "$PROJECT_ROOT"

echo "[1/3] Obteniendo certificados Let's Encrypt para chalanpro.com y www.chalanpro.com..."
for i in $(seq 1 60); do
  if certbot certonly --webroot -w /var/www/certbot \
    -d chalanpro.com -d www.chalanpro.com \
    --non-interactive --agree-tos --email admin@chalanpro.com 2>&1; then
    break
  fi
  echo "Reintento en 60 s (rate limit o DNS)..."
  sleep 60
done
if [ ! -f /etc/letsencrypt/live/chalanpro.com/fullchain.pem ]; then
  echo "Error: no se obtuvieron los certificados. Revisa DNS (sin AAAA en @) y ejecuta de nuevo más tarde."
  exit 1
fi

echo "[2/3] Activando bloque HTTPS en nginx..."
# Descomentar solo el bloque server { ... } de chalanpro.com (líneas que empiezan por "# server {" hasta "# }")
sed -i '/^# server {$/,/^# }$/{
  s/^# }$/}/
  s/^# //
}' "$CONF"

echo "[3/3] Reiniciando nginx..."
docker compose -f docker-compose.yml restart nginx

echo "Listo. Prueba https://chalanpro.com y https://www.chalanpro.com"
