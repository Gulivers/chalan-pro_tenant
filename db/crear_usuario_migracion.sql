-- ============================================
-- Script para crear usuario de migración de datos
-- con todos los privilegios necesarios
-- ============================================

-- Opción 1: Crear un nuevo usuario con privilegios de superusuario
-- (Recomendado para migración de datos)
CREATE USER migracion_user WITH 
    PASSWORD 'migracion_password123'
    SUPERUSER
    CREATEDB
    CREATEROLE
    REPLICATION
    BYPASSRLS;

-- Conceder todos los privilegios sobre la base de datos
GRANT ALL PRIVILEGES ON DATABASE chalan_sch_txn TO migracion_user;

-- Conectarse a la base de datos para otorgar privilegios sobre el esquema
\c chalan_sch_txn

-- Conceder privilegios sobre el esquema public
GRANT ALL ON SCHEMA public TO migracion_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO migracion_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO migracion_user;

-- Conceder privilegios sobre todas las tablas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO migracion_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO migracion_user;

-- Otorgar privilegios de COPY (necesario para importar CSV)
ALTER USER migracion_user WITH SUPERUSER;

-- ============================================
-- Verificación de privilegios
-- ============================================
\du migracion_user

