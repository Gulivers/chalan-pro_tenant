#!/bin/bash
# Script de inicio para Render
# Ejecuta migraciones y luego inicia el servidor

set -o errexit

echo "Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput

echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput || echo "skip collectstatic"

echo "Iniciando servidor Daphne..."
exec daphne -b 0.0.0.0 -p $PORT project.asgi:application
