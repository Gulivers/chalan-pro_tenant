#!/bin/bash
# Script para habilitar HTTPS después de obtener certificados SSL

set -e

echo "=== Habilitando HTTPS en Nginx ==="

NGINX_CONF="/opt/chalanpro/nginx/default.conf"
NGINX_HTTPS="/opt/chalanpro/nginx/default.conf.https"

# Verificar que los certificados existan
if [ ! -f "/etc/letsencrypt/live/chalanpro.net/fullchain.pem" ]; then
    echo "ERROR: No se encontraron certificados SSL."
    echo "Ejecuta primero: sudo bash /opt/chalanpro/init-certbot.sh"
    exit 1
fi

# Hacer backup de la configuración actual
cp "$NGINX_CONF" "$NGINX_CONF.backup.$(date +%Y%m%d_%H%M%S)"

# Reemplazar con la configuración HTTPS
cp "$NGINX_HTTPS" "$NGINX_CONF"

echo "✓ Configuración de HTTPS habilitada"

# Reiniciar Nginx
echo "Reiniciando Nginx..."
cd /opt/chalanpro
docker compose restart nginx

echo ""
echo "=== HTTPS habilitado correctamente ==="
echo "El sitio ahora está disponible en https://chalanpro.net"

