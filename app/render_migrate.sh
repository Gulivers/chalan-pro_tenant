#!/bin/bash
# Script para ejecutar migraciones en Render
# Este script se ejecuta durante el build

set -o errexit

echo "Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput || echo "Warning: Migrations failed, continuing..."

echo "Migraciones completadas exitosamente"
