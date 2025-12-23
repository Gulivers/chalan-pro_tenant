#!/bin/bash
# Script para crear backup completo del sistema y base de datos
# Uso: ./scripts/backup_completo.sh

set -e  # Salir si hay algún error

# Configuración
BACKUP_DIR="/home/oliver/shared/projects/backups"
DATE=$(date +%m-%d-%Y)
PROJECT_DIR="/home/oliver/shared/projects/chalanpro"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Iniciando backup completo ===${NC}"
echo "Fecha: $(date)"
echo ""

# Crear directorio de backups si no existe
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Creando directorio de backups: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    sudo chown oliver:oliver "$BACKUP_DIR" 2>/dev/null || true
    sudo chmod 755 "$BACKUP_DIR" 2>/dev/null || true
fi

# Backup del sistema
echo -e "${YELLOW}[1/2] Creando backup del sistema...${NC}"
cd /home/oliver/shared/projects
tar --exclude='chalanpro/app/vuefrontend/node_modules' \
    --exclude='chalanpro/*/node_modules' \
    --exclude='chalanpro/.git' \
    --exclude='chalanpro/*/__pycache__' \
    --exclude='chalanpro/*/*/__pycache__' \
    --exclude='chalanpro/*.pyc' \
    --exclude='chalanpro/postgres_data' \
    --exclude='chalanpro/*/dist' \
    -czf "$BACKUP_DIR/chalan_onboarding_local_$DATE.tar.gz" chalanpro

if [ $? -eq 0 ]; then
    SYSTEM_SIZE=$(du -h "$BACKUP_DIR/chalan_onboarding_local_$DATE.tar.gz" | cut -f1)
    echo -e "${GREEN}✓ Backup del sistema creado: chalan_onboarding_local_$DATE.tar.gz ($SYSTEM_SIZE)${NC}"
else
    echo "✗ Error al crear backup del sistema"
    exit 1
fi

# Backup de la base de datos
echo -e "${YELLOW}[2/2] Creando backup de la base de datos...${NC}"
cd "$PROJECT_DIR"

# Verificar que PostgreSQL esté corriendo
if ! docker compose -f docker-compose.dev.yml ps postgres | grep -q "Up"; then
    echo "Iniciando PostgreSQL..."
    docker compose -f docker-compose.dev.yml up -d postgres
    sleep 3
fi

# Crear backup de la base de datos
docker compose -f docker-compose.dev.yml exec -T postgres pg_dump -U chalanpro_user chalanpro > "$BACKUP_DIR/chalan_onboarding_local_db_$DATE.sql" 2>/dev/null

if [ $? -eq 0 ]; then
    DB_SIZE=$(du -h "$BACKUP_DIR/chalan_onboarding_local_db_$DATE.sql" | cut -f1)
    echo -e "${GREEN}✓ Backup de la base de datos creado: chalan_onboarding_local_db_$DATE.sql ($DB_SIZE)${NC}"
else
    echo "✗ Error al crear backup de la base de datos"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Backup completo finalizado ===${NC}"
echo "Backups creados en: $BACKUP_DIR"
echo ""
ls -lh "$BACKUP_DIR"/chalan_onboarding_local_*"$DATE"* 2>/dev/null || echo "No se encontraron archivos de backup"

