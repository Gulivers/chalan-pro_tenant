#!/bin/bash
# Script para inicializar Certbot y obtener certificados SSL para api.chalanpro.net

set -e

DOMAIN="api.chalanpro.net"
EMAIL="admin@chalanpro.net"  # Cambiar por tu email real

echo "=== Inicializando Certbot para $DOMAIN ==="

# Crear directorio para ACME challenges
sudo mkdir -p /var/www/certbot

# Asegurar permisos
sudo chown -R $USER:$USER /var/www/certbot

# Instalar Certbot si no está instalado
if ! command -v certbot &> /dev/null; then
    echo "Instalando Certbot..."
    sudo apt update
    sudo apt install -y certbot
fi

# Verificar que Nginx esté corriendo
echo "Verificando que Nginx esté corriendo..."
if ! docker ps | grep -q chalanpro_nginx; then
    echo "ERROR: Nginx debe estar corriendo para obtener certificados."
    echo "Ejecuta primero: cd /opt/chalanpro && docker compose up -d nginx"
    exit 1
fi

# Obtener certificados (solo para api.chalanpro.net, sin www)
echo "Obteniendo certificados SSL para $DOMAIN..."
sudo certbot certonly --webroot \
    -w /var/www/certbot \
    -d $DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive \
    --force-renewal

if [ $? -eq 0 ]; then
    echo "✓ Certificados obtenidos exitosamente!"
    echo "Reiniciando Nginx para cargar los certificados..."
    docker compose -f /opt/chalanpro/docker-compose.yml restart nginx
    echo "✓ Nginx reiniciado"
    
    # Configurar renovación automática
    echo "Configurando renovación automática..."
    sudo certbot renew --dry-run
    
    echo ""
    echo "=== Certificados SSL configurados correctamente ==="
    echo "Los certificados se renovarán automáticamente cada 90 días."
else
    echo "ERROR: No se pudieron obtener los certificados."
    exit 1
fi

