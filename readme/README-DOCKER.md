# PostgreSQL 16 en Docker - Guía de Uso

Esta guía te muestra cómo usar PostgreSQL 16 en Docker Desktop para Windows 10.

## Prerrequisitos

- ✅ Docker Desktop instalado y funcionando
- ✅ PowerShell de Windows

## Pasos de Instalación

### 1. Verificar Docker Desktop

Asegúrate de que Docker Desktop esté corriendo. Verifica buscando el ícono de Docker en la barra de tareas de Windows (barco en un contenedor).

Si no está corriendo:
1. Abre Docker Desktop desde el menú de inicio
2. Espera a que inicie (el ícono de la barra de tareas se volverá estable)

### 2. Ejecutar el Script de Configuración

Abre PowerShell en modo Administrador en la carpeta del proyecto y ejecuta:

```powershell
.\docker-postgres-setup.ps1
```

Este script:
- ✅ Verifica que Docker esté corriendo
- ✅ Elimina contenedores anteriores si existen
- ✅ Crea un nuevo contenedor con PostgreSQL 16
- ✅ Configura la base de datos `chalan_inv_txn`
- ✅ Persiste los datos en un volumen de Docker

## Configuración por Defecto

- **Usuario:** `postgres`
- **Contraseña:** `chalan2024`
- **Base de datos:** `chalan_inv_txn`
- **Puerto:** `5432`

## Gestión del Contenedor

Usa el script de gestión para administrar el contenedor:

```powershell
# Ver estado del contenedor
.\docker-postgres-manage.ps1 -Action status

# Iniciar contenedor
.\docker-postgres-manage.ps1 -Action start

# Detener contenedor
.\docker-postgres-manage.ps1 -Action stop

# Reiniciar contenedor
.\docker-postgres-manage.ps1 -Action restart

# Ver logs en tiempo real
.\docker-postgres-manage.ps1 -Action logs

# Conectar con psql
.\docker-postgres-manage.ps1 -Action connect

# Crear backup de la base de datos
.\docker-postgres-manage.ps1 -Action backup

# Eliminar contenedor (los datos se mantienen en el volumen)
.\docker-postgres-manage.ps1 -Action remove
```

## Conexión desde la Aplicación

Usa esta cadena de conexión en tu aplicación:

```
Host: localhost
Puerto: 5432
Usuario: postgres
Contraseña: chalan2024
Base de datos: chalan_inv_txn
```

### Ejemplo con psql (si tienes el cliente instalado)

```bash
psql -h localhost -p 5432 -U postgres -d chalan_inv_txn
```

### Ejemplo con conexión directa al contenedor

```bash
docker exec -it chalan-postgres psql -U postgres -d chalan_inv_txn
```

## Comandos Docker Útiles (Manual)

Si prefieres usar Docker directamente:

```bash
# Ver estado del contenedor
docker ps -a | findstr chalan-postgres

# Ver logs
docker logs chalan-postgres

# Iniciar contenedor
docker start chalan-postgres

# Detener contenedor
docker stop chalan-postgres

# Reiniciar contenedor
docker restart chalan-postgres

# Ejecutar SQL directamente
docker exec -i chalan-postgres psql -U postgres -d chalan_inv_txn -c "SELECT version();"

# Crear backup manual
docker exec chalan-postgres pg_dump -U postgres chalan_inv_txn > backup.sql

# Restaurar backup
docker exec -i chalan-postgres psql -U postgres -d chalan_inv_txn < backup.sql
```

## Persistencia de Datos

Los datos se guardan en un volumen de Docker llamado `chalan-postgres-data`. Esto significa que:
- ✅ Los datos persisten aunque elimines el contenedor
- ✅ Los datos persisten aunque reinicies Docker Desktop
- ✅ Puedes eliminar el contenedor y recrearlo sin perder datos

### Ver el tamaño del volumen:
```bash
docker system df -v | findstr chalan-postgres-data
```

### Eliminar el volumen (CUIDADO: esto elimina TODOS los datos):
```bash
docker volume rm chalan-postgres-data
```

## Solución de Problemas

### Contenedor no inicia

```bash
# Ver logs detallados
docker logs chalan-postgres

# Verificar espacio en disco
docker system df

# Reiniciar Docker Desktop
```

### Puerto 5432 ya está en uso

Si tienes PostgreSQL instalado localmente, puede estar usando el puerto 5432. Tienes dos opciones:

**Opción 1:** Detener el servicio de PostgreSQL local
```powershell
Stop-Service -Name "postgresql-x64-18" -ErrorAction SilentlyContinue
```

**Opción 2:** Cambiar el puerto del contenedor Docker

Edita `docker-postgres-setup.ps1` y cambia la línea:
```powershell
-p ${PORT}:5432 `
```

Por ejemplo, para usar el puerto 5433:
```powershell
-p 5433:5432 `
```

Y actualiza la cadena de conexión de tu aplicación para usar el puerto 5433.

### Contenedor desaparece al reiniciar Windows

Por defecto, Docker Desktop debe iniciarse automáticamente. Si no lo hace:

1. Abre Docker Desktop
2. Ve a Settings (Configuración) > General
3. Marca "Start Docker Desktop when you log in"

### Error de permisos en Windows

Si tienes problemas de permisos con los scripts de PowerShell:

```powershell
# Ejecuta esto en PowerShell como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Desinstalación

Para eliminar completamente PostgreSQL Docker:

```powershell
# Detener y eliminar contenedor
.\docker-postgres-manage.ps1 -Action remove

# Eliminar volumen (opcional - elimina todos los datos)
docker volume rm chalan-postgres-data

# Eliminar imagen de PostgreSQL (opcional)
docker rmi postgres:16
```

## Ventajas de PostgreSQL en Docker

- ✅ **Fácil de instalar:** No hay problemas con configuración de Windows
- ✅ **Versión específica:** Siempre usas PostgreSQL 16
- ✅ **Aislamiento:** No interfiere con otras instalaciones
- ✅ **Portable:** Mismo entorno en desarrollo y producción
- ✅ **Fácil de limpiar:** Eliminas el contenedor sin dejar rastros
- ✅ **Persistencia:** Los datos se mantienen en volúmenes de Docker

## Próximos Pasos

Una vez que PostgreSQL esté corriendo, puedes:
1. Crear las tablas de tu base de datos
2. Ejecutar migraciones
3. Poblar con datos de prueba
4. Conectar tu aplicación

## Recursos Adicionales

- [Documentación oficial de PostgreSQL](https://www.postgresql.org/docs/)
- [Documentación de Docker para PostgreSQL](https://hub.docker.com/_/postgres)
- [Docker Desktop para Windows](https://docs.docker.com/desktop/install/windows-install/)

