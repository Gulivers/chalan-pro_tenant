#!/usr/bin/env python
"""
Script para verificar qué base de datos está usando el backend Django
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.conf import settings
from django.db import connection

print("=" * 60)
print("VERIFICACIÓN DE BASE DE DATOS")
print("=" * 60)
print()

# Verificar variables de entorno
print("📋 Variables de Entorno:")
print(f"  DATABASE_URL: {os.environ.get('DATABASE_URL', 'NO DEFINIDA')}")
print(f"  POSTGRES_DB: {os.environ.get('POSTGRES_DB', 'NO DEFINIDA')}")
print(f"  POSTGRES_USER: {os.environ.get('POSTGRES_USER', 'NO DEFINIDA')}")
print(f"  POSTGRES_HOST: {os.environ.get('POSTGRES_HOST', 'NO DEFINIDA')}")
print()

# Verificar configuración de Django
print("⚙️  Configuración de Django (settings.py):")
db_config = settings.DATABASES['default']
print(f"  ENGINE: {db_config.get('ENGINE', 'NO DEFINIDO')}")
print(f"  NAME (Base de Datos): {db_config.get('NAME', 'NO DEFINIDO')}")
print(f"  USER: {db_config.get('USER', 'NO DEFINIDO')}")
print(f"  HOST: {db_config.get('HOST', 'NO DEFINIDO')}")
print(f"  PORT: {db_config.get('PORT', 'NO DEFINIDO')}")
print()

# Verificar conexión real
print("🔌 Conexión Real a la Base de Datos:")
try:
    with connection.cursor() as cursor:
        # Obtener información de la base de datos actual
        cursor.execute("SELECT current_database(), current_user, version();")
        db_info = cursor.fetchone()
        
        print(f"  ✅ Conectado exitosamente")
        print(f"  Base de Datos Actual: {db_info[0]}")
        print(f"  Usuario Actual: {db_info[1]}")
        print(f"  Versión PostgreSQL: {db_info[2].split(',')[0]}")
        print()
        
        # Listar todos los schemas disponibles
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schema_name;
        """)
        schemas = cursor.fetchall()
        
        print("📦 Schemas Disponibles en la Base de Datos:")
        for schema in schemas:
            schema_name = schema[0]
            # Verificar si tiene tablas
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = %s;
            """, [schema_name])
            table_count = cursor.fetchone()[0]
            print(f"  - {schema_name} ({table_count} tablas)")
        
        print()
        
        # Verificar si existe la tabla tenants_tenant en el schema public
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'tenants_tenant'
            );
        """)
        has_tenants_table = cursor.fetchone()[0]
        
        if has_tenants_table:
            print("✅ Tabla 'tenants_tenant' encontrada en schema 'public'")
            # Contar tenants
            cursor.execute("SELECT COUNT(*) FROM public.tenants_tenant;")
            tenant_count = cursor.fetchone()[0]
            print(f"   Total de tenants: {tenant_count}")
        else:
            print("❌ Tabla 'tenants_tenant' NO encontrada en schema 'public'")
        
except Exception as e:
    print(f"  ❌ Error al conectar: {str(e)}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)

