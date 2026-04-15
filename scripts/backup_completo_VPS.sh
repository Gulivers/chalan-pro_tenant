#!/bin/bash
# ============================================================================
# backup_completo_VPS.sh – Backup sistema + base de datos (todos los tenants)
# ============================================================================
# Uso: sudo /opt/chalanpro/scripts/backup_completo_VPS.sh [--retention N]
#
# Crea backup completo para rollback en caso de falla:
#   1. Sistema: código, config (nginx, envs), scripts (excluye postgres_data, node_modules, .git)
#   2. Base de datos: PostgreSQL completo con todos los schemas (public + tenants)
#
# Destino: /opt/backups/
# Nombres: chalanpro_vps_YYYYMMDD_HHMMSS.tar.gz, chalanpro_vps_db_YYYYMMDD_HHMMSS.sql
# (HHMMSS = hora local con date +%H%M%S)
#
# --retention N   Mantener solo los últimos N backups (por defecto: todos)
# ============================================================================

set -e

# Configuración VPS
BACKUP_DIR="/opt/backups"
PROJECT_DIR="/opt/chalanpro"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION=0  # 0 = sin límite

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Parsear argumentos
for arg in "$@"; do
    case "$arg" in
        --retention=*)
            RETENTION="${arg#*=}"
            ;;
        --retention)
            shift
            RETENTION="$1"
            ;;
    esac
done

echo -e "${GREEN}=== Backup completo Chalan-Pro VPS ===${NC}"
echo "Fecha: $(date -Iseconds)"
echo "Destino: $BACKUP_DIR"
echo ""

# Verificar que exista el proyecto
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: No existe $PROJECT_DIR${NC}"
    exit 1
fi

# Crear directorio de backups si no existe
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Creando directorio de backups: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    chmod 750 "$BACKUP_DIR"
fi

# --- 1. Backup del sistema ---
echo -e "${YELLOW}[1/2] Backup del sistema (código, config, scripts)...${NC}"
cd /opt

tar --exclude='chalanpro/app/vuefrontend/node_modules' \
    --exclude='chalanpro/node_modules' \
    --exclude='chalanpro/*/node_modules' \
    --exclude='chalanpro/.git' \
    --exclude='chalanpro/*/__pycache__' \
    --exclude='chalanpro/*/*/__pycache__' \
    --exclude='chalanpro/*/*/*/__pycache__' \
    --exclude='chalanpro/*.pyc' \
    --exclude='chalanpro/postgres_data' \
    --exclude='chalanpro/app/vuefrontend/dist' \
    --exclude='chalanpro/.cursor' \
    -czf "$BACKUP_DIR/chalanpro_vps_${TIMESTAMP}.tar.gz" chalanpro

if [ $? -eq 0 ]; then
    SYSTEM_SIZE=$(du -h "$BACKUP_DIR/chalanpro_vps_${TIMESTAMP}.tar.gz" | cut -f1)
    echo -e "${GREEN}✓ Sistema: chalanpro_vps_${TIMESTAMP}.tar.gz ($SYSTEM_SIZE)${NC}"
else
    echo -e "${RED}✗ Error al crear backup del sistema${NC}"
    exit 1
fi

# --- 2. Backup de la base de datos (todos los schemas/tenants) ---
echo -e "${YELLOW}[2/2] Backup de la base de datos (public + todos los tenants)...${NC}"
cd "$PROJECT_DIR"

# Verificar que PostgreSQL esté corriendo
if ! docker compose -f "$COMPOSE_FILE" ps postgres 2>/dev/null | grep -q "Up"; then
    echo "Iniciando PostgreSQL..."
    docker compose -f "$COMPOSE_FILE" up -d postgres
    sleep 10
fi

# pg_dump completo: incluye public + todos los schemas de tenants
# --no-owner: evita errores de permisos al restaurar
# --clean --if-exists: útil para restore (DROP antes de CREATE)
docker compose -f "$COMPOSE_FILE" exec -T postgres \
    pg_dump -U chalanpro_user -d chalanpro \
    --no-owner \
    --clean \
    --if-exists \
    > "$BACKUP_DIR/chalanpro_vps_db_${TIMESTAMP}.sql" 2>/dev/null

if [ $? -eq 0 ]; then
    DB_SIZE=$(du -h "$BACKUP_DIR/chalanpro_vps_db_${TIMESTAMP}.sql" | cut -f1)
    echo -e "${GREEN}✓ Base de datos: chalanpro_vps_db_${TIMESTAMP}.sql ($DB_SIZE)${NC}"
else
    echo -e "${RED}✗ Error al crear backup de la base de datos${NC}"
    exit 1
fi

# --- 3. Retención (opcional) ---
if [ "$RETENTION" -gt 0 ] 2>/dev/null; then
    echo ""
    echo -e "${YELLOW}Limpiando backups antiguos (retención: $RETENTION)...${NC}"
    # Mantener los N más recientes por tipo
    ls -t "$BACKUP_DIR"/chalanpro_vps_*.tar.gz 2>/dev/null | tail -n +$((RETENTION + 1)) | xargs -r rm -v
    ls -t "$BACKUP_DIR"/chalanpro_vps_db_*.sql 2>/dev/null | tail -n +$((RETENTION + 1)) | xargs -r rm -v
fi

echo ""
echo -e "${GREEN}=== Backup completo finalizado ===${NC}"
echo "Archivos en $BACKUP_DIR:"
ls -lh "$BACKUP_DIR"/chalanpro_vps_*"${TIMESTAMP}"* 2>/dev/null || true
echo ""
echo "Para restaurar: sudo /opt/chalanpro/scripts/restore_backup_VPS.sh ${TIMESTAMP}"
