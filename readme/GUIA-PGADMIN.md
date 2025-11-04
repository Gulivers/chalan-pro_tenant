# Guía: Conectar pgAdmin a PostgreSQL en Docker

## Método 1: Usar pgAdmin en Docker (Recomendado)

### Paso 1: Detener el contenedor individual

Si ya tienes PostgreSQL corriendo con el script individual, deténlo:

```powershell
docker stop chalan-postgres
docker rm chalan-postgres
```

### Paso 2: Iniciar con Docker Compose

Ejecuta este comando en tu terminal:

```powershell
docker-compose -f docker-compose-local.yml up -d
```

Este comando:
- Crea el contenedor de PostgreSQL (chalan-postgres)
- Crea el contenedor de pgAdmin (chalan-pgadmin)
- Los conecta entre sí
- Los pone a correr en segundo plano

### Paso 3: Acceder a pgAdmin

1. Abre tu navegador web
2. Ve a: `http://localhost:5050`
3. **Email:** `admin@chalan.com`
4. **Contraseña:** `chalan2024`

### Paso 4: Conectar pgAdmin a PostgreSQL

Una vez dentro de pgAdmin:

1. **Clic derecho en "Servers"** → **Register** → **Server**
2. En la pestaña **General**:
   - **Name:** Chalan PostgreSQL
3. En la pestaña **Connection**:
   - **Host name/address:** `chalan-postgres` (nombre del contenedor)
   - **Port:** `5432`
   - **Maintenance database:** `postgres`
   - **Username:** `postgres`
   - **Password:** `chalan2024`
   - ✅ **Marcar:** "Save password"
4. Clic en **Save**

¡Listo! Ya puedes navegar por tu base de datos.

## Método 2: Instalar pgAdmin en Windows

### Paso 1: Descargar e Instalar pgAdmin

1. Ve a: https://www.pgadmin.org/download/pgadmin-4-windows/
2. Descarga el instalador
3. Instálalo en tu Windows

### Paso 2: Configurar la Conexión

1. Abre pgAdmin
2. Crea una nueva contraseña maestra (la primera vez)
3. **Clic derecho en "Servers"** → **Register** → **Server**
4. En la pestaña **General**:
   - **Name:** Chalan PostgreSQL
5. En la pestaña **Connection**:
   - **Host name/address:** `localhost`
   - **Port:** `5432`
   - **Maintenance database:** `chalan_inv_txn`
   - **Username:** `postgres`
   - **Password:** `chalan2024`
   - ✅ **Marcar:** "Save password"
6. Clic en **Save**

## Gestión de los Contenedores

### Iniciar servicios
```powershell
docker-compose -f docker-compose-local.yml up -d
```

### Ver estado
```powershell
docker-compose -f docker-compose-local.yml ps
```

### Detener servicios
```powershell
docker-compose -f docker-compose-local.yml stop
```

### Iniciar servicios detenidos
```powershell
docker-compose -f docker-compose-local.yml start
```

### Detener y eliminar contenedores
```powershell
docker-compose -f docker-compose-local.yml down
```

### Ver logs de pgAdmin
```powershell
docker logs chalan-pgadmin
```

### Ver logs de PostgreSQL
```powershell
docker logs chalan-postgres
```

### Ver logs de ambos en tiempo real
```powershell
docker-compose -f docker-compose-local.yml logs -f
```

## Resumen de Accesos

### pgAdmin (Docker)
- **URL:** http://localhost:5050
- **Email:** admin@chalan.com
- **Contraseña:** chalan2024

### PostgreSQL
- **Host:** localhost (desde pgAdmin de Windows) o chalan-postgres (desde pgAdmin de Docker)
- **Puerto:** 5432
- **Database:** chalan_inv_txn
- **Usuario:** postgres
- **Contraseña:** chalan2024

## Solución de Problemas

### "No puedo conectarme desde pgAdmin de Windows"

**Problema:** El contenedor está en otra red Docker.

**Solución:** Usa el host `localhost` y asegúrate de que el puerto esté mapeado:
```powershell
docker ps | findstr 5432
```

Deberías ver: `0.0.0.0:5432->5432/tcp`

### "No puedo conectarme desde pgAdmin de Docker"

**Problema:** Usaste `localhost` en lugar del nombre del contenedor.

**Solución:** Usa `chalan-postgres` como host (nombre del contenedor).

### "pgAdmin no carga en el navegador"

**Problema:** El contenedor no está corriendo.

**Solución:**
```powershell
docker-compose -f docker-compose-local.yml up -d
docker logs chalan-pgadmin
```

### "No veo la base de datos chalan_inv_txn"

**Problema:** La base de datos no se creó automáticamente.

**Solución:** Crea la base de datos manualmente:
1. En pgAdmin, conecta a la base de datos `postgres`
2. Clic derecho en "Databases" → **Create** → **Database**
3. **Name:** chalan_inv_txn
4. **Owner:** postgres
5. Clic en **Save**

## Ventajas de Cada Método

### pgAdmin en Docker ✅
- ✅ No instala nada en tu Windows
- ✅ Mismo entorno siempre
- ✅ Fácil de eliminar
- ✅ Versión actualizada
- ❌ Necesitas Docker corriendo

### pgAdmin en Windows ✅
- ✅ No depende de Docker
- ✅ Más rápido (nativo)
- ✅ Puede usar más de una conexión
- ❌ Instala en tu sistema
- ❌ Necesitas actualizarlo manualmente

## Próximos Pasos

Una vez conectado a pgAdmin, puedes:

1. **Ver tablas:** Navega por Schemas → public → Tables
2. **Ejecutar queries:** Usa la pestaña Query Tool
3. **Ver datos:** Clic derecho en tabla → View/Edit Data
4. **Crear backups:** Clic derecho en database → Backup
5. **Restaurar backups:** Clic derecho en database → Restore

## Archivos de Configuración

- `docker-compose-local.yml` - Configuración de PostgreSQL y pgAdmin
- `docker-postgres-setup.ps1` - Script para PostgreSQL solo
- `docker-postgres-manage.ps1` - Gestión de PostgreSQL solo

## Nota Importante

Si usas `docker-compose-local.yml`, los scripts individuales (`docker-postgres-setup.ps1`) no funcionarán porque Docker Compose gestiona los contenedores de forma diferente.

Para volver a usar los scripts individuales:
```powershell
docker-compose -f docker-compose-local.yml down
.\docker-postgres-setup.ps1
```

