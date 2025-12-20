-- ============================================
-- Script para RESETEAR contraseñas de usuarios PostgreSQL
-- Ejecutar desde Docker con: docker exec -i chalan_postgres psql -U postgres < resetear_passwords.sql
-- ============================================

-- Resetear contraseña de chalan_user
ALTER USER chalan_user WITH PASSWORD 'chalan_password';

-- Resetear contraseña de migracion_user
ALTER USER migracion_user WITH PASSWORD 'migracion_password123';

-- Verificar usuarios
\du chalan_user
\du migracion_user

-- Mensaje de confirmación
SELECT 'Contraseñas reseteadas correctamente' as mensaje;

