# Resumen de Gestión: PostgreSQL con Docker (2 modos)

Este resumen te permite gestionar tu base de datos con dos enfoques y cambiar entre ellos de forma segura.

- Modo A: Scripts (solo PostgreSQL)
- Modo B: Docker Compose (PostgreSQL + pgAdmin)

Importante: No mezcles ambos modos al mismo tiempo.

---

## Modo A — Scripts (solo PostgreSQL)

Archivos usados:
- `docker-postgres-setup.ps1`
- `docker-postgres-manage.ps1`
- `test-postgres-connection.ps1` (opcional)

### Crear/levantar PostgreSQL
```powershell
.\docker-postgres-setup.ps1
```

### Comandos de gestión
```powershell
# Ver estado
.\docker-postgres-manage.ps1 -Action status

# Iniciar / Detener / Reiniciar
.\docker-postgres-manage.ps1 -Action start
.\docker-postgres-manage.ps1 -Action stop
.\docker-postgres-manage.ps1 -Action restart

# Logs
.\docker-postgres-manage.ps1 -Action logs

# Conectar (psql dentro del contenedor)
.\docker-postgres-manage.ps1 -Action connect

# Backup (archivo .sql en el directorio actual)
.\docker-postgres-manage.ps1 -Action backup
```

### Eliminar contenedor (mantiene datos en el volumen)
```powershell
.\docker-postgres-manage.ps1 -Action remove
```

### Consola psql (Modo A) — comandos compactos
```powershell
# Abrir consola psql dentro del contenedor
docker exec -it chalan-postgres psql -U postgres -d chalan_inv_txn
# Probar conexión rápida (devuelve versión)
docker exec chalan-postgres psql -U postgres -d chalan_inv_txn -c "SELECT version();"
# Listar bases de datos
docker exec chalan-postgres psql -U postgres -d postgres -c "\l"
# Listar tablas del esquema public
docker exec chalan-postgres psql -U postgres -d chalan_inv_txn -c "\dt"
# Crear base de datos (si la necesitas)
docker exec chalan-postgres psql -U postgres -d postgres -c "CREATE DATABASE chalan_inv_txn;"
# Crear rol/usuario (ejemplo)
docker exec chalan-postgres psql -U postgres -d postgres -c "CREATE ROLE appuser WITH LOGIN PASSWORD 'appPass';"
# Asignar privilegios al rol (ejemplo)
docker exec chalan-postgres psql -U postgres -d chalan_inv_txn -c "GRANT ALL PRIVILEGES ON DATABASE chalan_inv_txn TO appuser;"
```

---

## Modo B — Docker Compose (PostgreSQL + pgAdmin)

Archivo usado:
- `docker-compose-local.yml`

### Levantar servicios (PostgreSQL + pgAdmin)
```powershell
docker-compose -f docker-compose-local.yml up -d
```

### Ver estado / logs / gestión
```powershell
# Estado
docker-compose -f docker-compose-local.yml ps

# Logs (todos / servicio puntual)
docker-compose -f docker-compose-local.yml logs -f
docker-compose -f docker-compose-local.yml logs postgres
docker-compose -f docker-compose-local.yml logs pgadmin

# Detener / Iniciar / Reiniciar
docker-compose -f docker-compose-local.yml stop
docker-compose -f docker-compose-local.yml start
docker-compose -f docker-compose-local.yml restart

# Bajar servicios (mantiene datos)
docker-compose -f docker-compose-local.yml down

# Bajar servicios y eliminar datos (CUIDADO)
docker-compose -f docker-compose-local.yml down -v
```

### Acceso pgAdmin
- URL: `http://localhost:5050`
- Email: `admin@chalan.com`
- Password: `chalan2024`

En pgAdmin, registrar servidor con:
- Host: `chalan-postgres`
- Port: `5432`
- Database: `postgres`
- User: `postgres`
- Password: `chalan2024`

### Consola psql (Modo B Docker Compose (PostgreSQL + pgAdmin)) — comandos compactos
```powershell
# Abrir consola psql dentro del contenedor (via compose)
docker-compose -f docker-compose-local.yml exec postgres psql -U postgres -d chalan_inv_txn
# Probar conexión rápida (versión)
docker-compose -f docker-compose-local.yml exec postgres psql -U postgres -d chalan_inv_txn -c "SELECT version();"
# Listar bases de datos
docker-compose -f docker-compose-local.yml exec postgres psql -U postgres -d postgres -c "\\l"
# Listar tablas del esquema public
docker-compose -f docker-compose-local.yml exec postgres psql -U postgres -d chalan_inv_txn -c "\\dt"
# Crear base de datos (si la necesitas)
docker-compose -f docker-compose-local.yml exec postgres psql -U postgres -d postgres -c "CREATE DATABASE chalan_inv_txn;"
# Crear rol/usuario (ejemplo)
docker-compose -f docker-compose-local.yml exec postgres psql -U postgres -d postgres -c "CREATE ROLE appuser WITH LOGIN PASSWORD 'appPass';"
# Asignar privilegios al rol (ejemplo)
docker-compose -f docker-compose-local.yml exec postgres psql -U postgres -d chalan_inv_txn -c "GRANT ALL PRIVILEGES ON DATABASE chalan_inv_txn TO appuser;"
```

---

## Cómo cambiar entre modos (Switch)

Nunca ejecutes ambos a la vez. Sigue estos pasos:

### De Modo A (scripts) → Modo B (compose)
```powershell
# Detener y eliminar el contenedor del modo scripts (si existe)
docker stop chalan-postgres 2>$null
docker rm chalan-postgres 2>$null

# Levantar compose (PostgreSQL + pgAdmin)
docker-compose -f docker-compose-local.yml up -d
```

### De Modo B (compose) → Modo A (scripts)
```powershell
# Bajar servicios de compose (mantiene datos)
docker-compose -f docker-compose-local.yml down

# Levantar por scripts
.\docker-postgres-setup.ps1
```

Notas:
- Ambos modos usan el mismo volumen `chalan-postgres-data` por defecto, por lo que los datos persisten al cambiar.
- Usa `down -v` solo si quieres eliminar datos.

---

## Cheatsheet rápido

```powershell
# Modo A: scripts
.\docker-postgres-setup.ps1
.\docker-postgres-manage.ps1 -Action status
.\docker-postgres-manage.ps1 -Action connect

# Modo B: compose
docker-compose -f docker-compose-local.yml up -d
start http://localhost:5050

# Switch A → B
docker stop chalan-postgres 2>$null; docker rm chalan-postgres 2>$null
docker-compose -f docker-compose-local.yml up -d

# Switch B → A
docker-compose -f docker-compose-local.yml down
.\docker-postgres-setup.ps1
```

---

## Info de conexión (común a ambos)
```
Host (Windows/externo): localhost
Host (desde pgAdmin en Docker): chalan-postgres
Port: 5432
DB: chalan_inv_txn (o postgres para mantenimiento)
User: postgres
Pass: chalan2024
```

---

Para más detalle: `readme/GUIA-PGADMIN.md`, `readme/COMANDOS-RAPIDOS.md` y `readme/DOCKER-COMPOSE-VS-SCRIPTS.md`.


Aplica los cambios:
docker compose -f docker-compose.local.yml down
docker compose -f docker-compose.local.yml up -d --build
docker compose -f docker-compose.local.yml logs -f frontend
