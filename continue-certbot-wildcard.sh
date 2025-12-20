#!/bin/bash
# Script para continuar el proceso de Certbot después de agregar el registro TXT

set -e

DOMAIN="chalanpro.net"
TXT_RECORD_NAME="_acme-challenge.chalanpro.net"
EXPECTED_VALUE="W1buLdZdF5UJgjmbECt2OCd0vl9MfVfYlqcN5KLn_qA"

echo "=== Verificando registro TXT y continuando con Certbot ==="
echo ""
echo "Buscando registro TXT: $TXT_RECORD_NAME"
echo "Valor esperado: $EXPECTED_VALUE"
echo ""

# Esperar hasta que el registro TXT esté disponible
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo "Intento $ATTEMPT/$MAX_ATTEMPTS: Verificando registro TXT..."
    
    TXT_RECORDS=$(dig +short TXT $TXT_RECORD_NAME @8.8.8.8 2>/dev/null || echo "")
    
    if echo "$TXT_RECORDS" | grep -q "$EXPECTED_VALUE"; then
        echo "✓ Registro TXT encontrado y verificado!"
        echo ""
        break
    else
        if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
            echo "Registro TXT aún no encontrado, esperando 10 segundos..."
            sleep 10
        else
            echo ""
            echo "ERROR: No se encontró el registro TXT después de $MAX_ATTEMPTS intentos."
            echo "Por favor, verifica que:"
            echo "1. Agregaste el registro TXT en Hostinger"
            echo "2. El nombre es: _acme-challenge"
            echo "3. El valor es: $EXPECTED_VALUE"
            echo "4. Esperaste al menos 1-2 minutos para la propagación DNS"
            exit 1
        fi
    fi
done

echo "Continuando con Certbot..."
echo ""

# Continuar con Certbot (simular presionar Enter)
# Necesitamos ejecutar certbot de nuevo, pero esta vez con el registro ya verificado
# Como el proceso anterior falló, necesitamos iniciarlo de nuevo

sudo certbot certonly \
    --manual \
    --preferred-challenges dns \
    -d $DOMAIN \
    -d "*.chalanpro.net" \
    --email admin@chalanpro.net \
    --agree-tos \
    --manual-public-ip-logging-ok \
    --force-renewal <<EOF

EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Certificado obtenido exitosamente!"
    echo ""
    echo "Los certificados están en:"
    echo "  /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
    echo "  /etc/letsencrypt/live/$DOMAIN/privkey.pem"
    echo ""
    echo "Reiniciando Nginx..."
    cd /opt/chalanpro && docker compose restart nginx
    echo "✓ Nginx reiniciado"
    echo ""
    echo "=== Certificado SSL wildcard configurado correctamente ==="
else
    echo ""
    echo "ERROR: No se pudo obtener el certificado."
    echo "Verifica los logs: sudo tail -50 /var/log/letsencrypt/letsencrypt.log"
    exit 1
fi

