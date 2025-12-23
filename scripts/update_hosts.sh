#!/bin/bash
# ============================================================================
# Script para actualizar /etc/hosts con dominios de tenants activos
# ============================================================================
# 
# PROPÓSITO: SOLO para desarrollo local (ubuntu-house)
# - Actualiza /etc/hosts en el servidor de desarrollo local
# - Hace que los dominios apunten a la IP local (192.168.0.105)
# - Permite probar tenants localmente sin afectar producción
#
# DÓNDE SE EJECUTA:
# - Servidor: ubuntu-house (192.168.0.105)
# - Ubicación: ~/shared/projects/chalanpro/scripts/update_hosts.sh
# - Comando: sudo ./scripts/update_hosts.sh
#
# CUÁNDO USAR:
# - Después de crear un nuevo tenant en desarrollo local
# - Cuando necesites actualizar los dominios en /etc/hosts
#
# NO SE USA EN:
# - VPS de producción (72.60.168.62) - Los dominios ya están en DNS
# - Máquinas cliente (192.168.0.248) - Solo en el servidor de desarrollo
#
# ============================================================================

HOST_IP="192.168.0.105"  # IP del servidor de desarrollo local (ubuntu-house)
HOSTS_FILE="/etc/hosts"
TEMP_FILE=$(mktemp)

# Dominios base que siempre deben estar
BASE_DOMAINS=(
    "chalanpro.net"
    "api.chalanpro.net"
)

# Obtener dominios de tenants desde la base de datos
echo "Obteniendo dominios de tenants activos..."
TENANT_DOMAINS=$(cd /home/oliver/shared/projects/chalanpro && docker compose -f docker-compose.dev.yml exec -T backend python manage.py shell -c "
from tenants.models import Domain
domains = Domain.objects.filter(tenant__is_active=True).values_list('domain', flat=True).distinct()
print(' '.join(sorted(domains)))
" 2>/dev/null | tail -1)

# Copiar líneas que no son de chalanpro (eliminar todas las líneas relacionadas)
echo "Preservando líneas existentes..."
# Eliminar líneas con chalanpro, Chalan-Pro, y formato IP antiguo (subdomain.192.168.0.105)
grep -v "chalanpro\|Chalan-Pro\|\.192\.168\.0\.105" "$HOSTS_FILE" > "$TEMP_FILE" 2>/dev/null || cat "$HOSTS_FILE" | grep -v "chalanpro\|Chalan-Pro\|\.192\.168\.0\.105" > "$TEMP_FILE"

# Agregar dominios base
echo "" >> "$TEMP_FILE"
echo "# Chalan-Pro - Dominios base" >> "$TEMP_FILE"
for domain in "${BASE_DOMAINS[@]}"; do
    echo "$HOST_IP $domain" >> "$TEMP_FILE"
done

# Agregar dominios de tenants
if [ -n "$TENANT_DOMAINS" ]; then
    echo "" >> "$TEMP_FILE"
    echo "# Chalan-Pro - Dominios de tenants" >> "$TEMP_FILE"
    for domain in $TENANT_DOMAINS; do
        echo "$HOST_IP $domain" >> "$TEMP_FILE"
    done
fi

# Reemplazar /etc/hosts
sudo cp "$TEMP_FILE" "$HOSTS_FILE"
rm "$TEMP_FILE"

echo "✓ /etc/hosts actualizado"
echo ""
echo "Dominios agregados:"
echo "  Base: ${BASE_DOMAINS[*]}"
if [ -n "$TENANT_DOMAINS" ]; then
    echo "  Tenants: $TENANT_DOMAINS"
else
    echo "  Tenants: (ninguno activo)"
fi

