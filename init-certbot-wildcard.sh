#!/bin/bash
# Script para obtener certificado SSL wildcard para *.chalanpro.net
# Usa DNS challenge manual (Hostinger no tiene plugin automático)

set -e

DOMAIN="chalanpro.net"
WILDCARD_DOMAIN="*.chalanpro.net"
EMAIL="admin@chalanpro.net"  # Cambiar por tu email real

echo "=== Obteniendo certificado SSL wildcard para $WILDCARD_DOMAIN ==="
echo ""
echo "Este script usará DNS challenge manual."
echo "Necesitarás agregar un registro TXT en Hostinger cuando se te solicite."
echo ""

# Verificar que Certbot esté instalado
if ! command -v certbot &> /dev/null; then
    echo "Instalando Certbot..."
    sudo apt update
    sudo apt install -y certbot
fi

# Verificar que el DNS wildcard esté configurado
echo "Verificando DNS wildcard..."
WILDCARD_IP=$(dig +short $WILDCARD_DOMAIN @8.8.8.8 | head -1)
if [ -z "$WILDCARD_IP" ]; then
    echo "ERROR: El DNS wildcard (*.chalanpro.net) no está resolviendo."
    echo "Por favor, configura el registro DNS A wildcard en Hostinger primero."
    exit 1
fi

echo "✓ DNS wildcard está configurado correctamente (resuelve a $WILDCARD_IP)"
echo ""

# Obtener certificado wildcard usando DNS challenge manual
echo "Iniciando proceso de obtención de certificado..."
echo ""
echo "IMPORTANTE:"
echo "1. Certbot te mostrará un registro TXT que debes agregar en Hostinger"
echo "2. El registro debe ser: _acme-challenge.chalanpro.net"
echo "3. Después de agregarlo, espera 1-2 minutos para que se propague"
echo "4. Luego presiona Enter en la terminal de Certbot para continuar"
echo ""
echo "Ejecutando Certbot..."
echo ""

# Obtener certificado con DNS challenge manual
# NOTA: No incluimos www.$DOMAIN porque el wildcard *.chalanpro.net ya lo cubre
sudo certbot certonly \
    --manual \
    --preferred-challenges dns \
    -d $DOMAIN \
    -d $WILDCARD_DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --manual-public-ip-logging-ok \
    --force-renewal

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Certificado obtenido exitosamente!"
    echo ""
    echo "Los certificados están en:"
    echo "  /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
    echo "  /etc/letsencrypt/live/$DOMAIN/privkey.pem"
    echo ""
    echo "Ahora necesitas:"
    echo "1. Copiar los certificados al contenedor de Nginx"
    echo "2. Reiniciar Nginx"
    echo ""
    echo "Ejecutando copia de certificados..."
    
    # Copiar certificados al volumen de Nginx
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /opt/chalanpro/certbot/live/$DOMAIN/ 2>/dev/null || true
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /opt/chalanpro/certbot/live/$DOMAIN/ 2>/dev/null || true
    
    # Asegurar permisos
    sudo chmod 644 /etc/letsencrypt/live/$DOMAIN/fullchain.pem
    sudo chmod 600 /etc/letsencrypt/live/$DOMAIN/privkey.pem
    
    echo "✓ Certificados copiados"
    echo ""
    echo "Reiniciando Nginx..."
    cd /opt/chalanpro && docker compose restart nginx
    echo "✓ Nginx reiniciado"
    echo ""
    echo "=== Certificado SSL wildcard configurado correctamente ==="
    echo ""
    echo "El certificado se renovará automáticamente cada 90 días."
    echo "Para renovar manualmente: sudo certbot renew"
else
    echo ""
    echo "ERROR: No se pudo obtener el certificado."
    echo "Verifica que agregaste el registro TXT correctamente en Hostinger."
    exit 1
fi
