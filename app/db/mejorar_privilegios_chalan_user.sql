-- ============================================
-- Script para mejorar privilegios de chalan_user
-- (Si prefieres usar el usuario existente)
-- ============================================

-- Conceder privilegios de superusuario temporalmente para migración
ALTER USER chalan_user WITH SUPERUSER;

-- O si prefieres mantenerlo sin superusuario, otorgar privilegios específicos:
-- GRANT ALL PRIVILEGES ON DATABASE chalan_sch_txn TO chalan_user;
-- \c chalan_sch_txn
-- GRANT ALL ON SCHEMA public TO chalan_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chalan_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chalan_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO chalan_user;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO chalan_user;

-- Verificación
\du chalan_user

