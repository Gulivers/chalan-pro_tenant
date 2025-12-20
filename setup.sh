#!/bin/bash
# Script de inicialización completo para Chalan-Pro

set -e

echo "=== Configurando Chalan-Pro en producción ==="

# Verificar que estamos en el directorio correcto
if [ ! -f "/opt/chalanpro/docker-compose.yml" ]; then
    echo "ERROR: No se encontró docker-compose.yml en /opt/chalanpro"
    exit 1
fi

cd /opt/chalanpro

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker no está instalado"
    exit 1
fi

# Crear directorios necesarios
echo "Creando directorios..."
mkdir -p postgres_data
mkdir -p app/staticfiles
mkdir -p app/media
mkdir -p nginx
sudo mkdir -p /var/www/certbot
sudo chown -R $USER:$USER /var/www/certbot

# Construir y levantar contenedores
echo "Construyendo imágenes Docker..."
docker compose build

echo "Iniciando contenedores..."
docker compose up -d postgres

# Esperar a que PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
sleep 10

# Iniciar backend
echo "Iniciando backend..."
docker compose up -d backend

# Esperar un poco para que el backend se inicie
sleep 5

# Ejecutar migraciones
echo "Ejecutando migraciones de Django..."
docker compose exec -T backend python manage.py migrate

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
docker compose exec -T backend python manage.py collectstatic --noinput

# Construir frontend
echo "Construyendo frontend..."
docker compose up -d frontend

# Esperar a que el frontend construya
sleep 10

# Iniciar Nginx
echo "Iniciando Nginx..."
docker compose up -d nginx

echo ""
echo "=== Configuración completada ==="
echo ""
echo "Próximos pasos:"
echo "1. Configura los registros DNS para chalanpro.net apuntando a este servidor"
echo "2. Ejecuta: sudo bash /opt/chalanpro/init-certbot.sh"
echo "3. Verifica que todo funcione: docker compose ps"
echo ""
echo "Para ver los logs:"
echo "  docker compose logs -f"

