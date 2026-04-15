#!/bin/bash
# ============================================================================
# restore_backup_VPS.sh – Restaurar backup para rollback (sistema + base de datos)
# ============================================================================
# Uso: sudo /opt/chalanpro/scripts/restore_backup_VPS.sh TIMESTAMP [--sistema-only] [--db-only]
#
# Restaura un backup creado por backup_completo_VPS.sh.
# TIMESTAMP: formato YYYYMMDD_HHMMSS (ej: 20250219_024500)
#
# --sistema-only   Solo restaura el tar (código/config), no la base de datos
# --db-only        Solo restaura la base de datos, no el sistema
#
# IMPORTANTE: Detiene servicios, restaura y reinicia. Hacer backup antes de restaurar.
# ============================================================================

set -e

BACKUP_DIR="/opt/backups"
PROJECT_DIR="/opt/chalanpro"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Argumentos
TIMESTAMP="$1"
RESTORE_SISTEMA=1
RESTORE_DB=1

for arg in "$@"; do
    case "$arg" in
        --sistema-only) RESTORE_DB=0 ;;
        --db-only)     RESTORE_SISTEMA=0 ;;
    esac
done

if [ -z "$TIMESTAMP" ]; then
    echo -e "${RED}Uso: $0 TIMESTAMP [--sistema-only] [--db-only]${NC}"
    echo "Ejemplo: $0 20250219_024500"
    echo ""
    echo "Backups disponibles:"
    ls -1 "$BACKUP_DIR"/chalanpro_vps_*.tar.gz 2>/dev/null | sed 's/.*chalanpro_vps_\([0-9_]*\)\.tar\.gz/  \1/' | sort -u || echo "  (ninguno)"
    exit 1
fi

TAR_FILE="$BACKUP_DIR/chalanpro_vps_${TIMESTAMP}.tar.gz"
SQL_FILE="$BACKUP_DIR/chalanpro_vps_db_${TIMESTAMP}.sql"

if [ "$RESTORE_SISTEMA" -eq 1 ] && [ ! -f "$TAR_FILE" ]; then
    echo -e "${RED}Error: No existe $TAR_FILE${NC}"
    exit 1
fi

if [ "$RESTORE_DB" -eq 1 ] && [ ! -f "$SQL_FILE" ]; then
    echo -e "${RED}Error: No existe $SQL_FILE${NC}"
    exit 1
fi

echo -e "${YELLOW}=== Restaurar backup Chalan-Pro VPS ===${NC}"
echo "Timestamp: $TIMESTAMP"
echo "Sistema: $([ "$RESTORE_SISTEMA" -eq 1 ] && echo 'Sí' || echo 'No')"
echo "Base de datos: $([ "$RESTORE_DB" -eq 1 ] && echo 'Sí' || echo 'No')"
echo ""
read -p "¿Continuar? (s/N): " -r
if [[ ! $REPLY =~ ^[sS]$ ]]; then
    echo "Cancelado."
    exit 0
fi

cd "$PROJECT_DIR"

# --- Detener servicios ---
echo -e "${YELLOW}Deteniendo servicios...${NC}"
docker compose -f "$COMPOSE_FILE" stop backend frontend nginx 2>/dev/null || true

# --- Restaurar sistema ---
if [ "$RESTORE_SISTEMA" -eq 1 ]; then
    echo -e "${YELLOW}Restaurando sistema desde $TAR_FILE...${NC}"
    cd /opt
    tar -xzf "$TAR_FILE"
    echo -e "${GREEN}✓ Sistema restaurado${NC}"
fi

cd "$PROJECT_DIR"

# --- Restaurar base de datos ---
if [ "$RESTORE_DB" -eq 1 ]; then
    echo -e "${YELLOW}Restaurando base de datos (public + tenants)...${NC}"
    # Asegurar que postgres está up
    docker compose -f "$COMPOSE_FILE" up -d postgres
    sleep 5
    # Restaurar (backend detenido = sin conexiones activas a chalanpro)
    docker compose -f "$COMPOSE_FILE" exec -i postgres psql -U chalanpro_user -d chalanpro < "$SQL_FILE"
    echo -e "${GREEN}✓ Base de datos restaurada${NC}"
fi

# --- Reiniciar servicios ---
echo -e "${YELLOW}Reiniciando servicios...${NC}"
docker compose -f "$COMPOSE_FILE" up -d backend frontend nginx
echo "Esperando arranque (30s)..."
sleep 30

echo ""
echo -e "${GREEN}=== Restauración completada ===${NC}"
echo "Verificar: docker compose -f $COMPOSE_FILE ps"
echo "Logs: docker compose -f $COMPOSE_FILE logs -f backend nginx"
