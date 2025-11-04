# Comandos Rápidos - PostgreSQL en Docker

## Primer Uso

### 1. Permitir ejecución de scripts (una sola vez)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Crear contenedor PostgreSQL
```powershell
.\docker-postgres-setup.ps1
```

### 3. Verificar conexión
```powershell
.\test-postgres-connection.ps1
```

## Comandos Diarios

### Ver estado del contenedor
```powershell
.\docker-postgres-manage.ps1 -Action status
```

### Iniciar PostgreSQL
```powershell
.\docker-postgres-manage.ps1 -Action start
```

### Detener PostgreSQL
```powershell
.\docker-postgres-manage.ps1 -Action stop
```

### Conectar con psql
```powershell
.\docker-postgres-manage.ps1 -Action connect
```

### Ver logs
```powershell
.\docker-postgres-manage.ps1 -Action logs
```

## Comandos Docker Directos

### Ver todos los contenedores
```powershell
docker ps -a
```

### Ver solo contenedor de PostgreSQL
```powershell
docker ps -a | findstr chalan-postgres
```

### Ejecutar SQL directamente
```powershell
docker exec -i chalan-postgres psql -U postgres -d chalan_inv_txn -c "SELECT version();"
```

### Conectar interactivamente
```powershell
docker exec -it chalan-postgres psql -U postgres -d chalan_inv_txn
```

### Ver logs en tiempo real
```powershell
docker logs -f chalan-postgres
```

## Información de Conexión

```
Host: localhost
Puerto: 5432
Usuario: postgres
Contraseña: chalan2024
Base de datos: chalan_inv_txn
```

## Si algo falla

### Ver logs del contenedor
```powershell
docker logs chalan-postgres
```

### Reiniciar PostgreSQL
```powershell
.\docker-postgres-manage.ps1 -Action restart
```

### Eliminar y recrear (CUIDADO: elimina datos)
```powershell
docker rm -f chalan-postgres
.\docker-postgres-setup.ps1
```

### Ver uso de disco
```powershell
docker system df
```

## Backup

### Crear backup
```powershell
docker exec chalan-postgres pg_dump -U postgres chalan_inv_txn > backup_$(Get-Date -Format "yyyyMMdd").sql
```

### Restaurar backup
```powershell
docker exec -i chalan-postgres psql -U postgres -d chalan_inv_txn < backup_yyyyMMdd.sql
```

Comandos utiles:
  Conectar con psql: docker exec -it chalan-postgres psql -U postgres -d chalan_inv_txn
  Ver logs: docker logs chalan-postgres
  Detener: docker stop chalan-postgres
  Iniciar: docker start chalan-postgres
  Eliminar: docker rm -f chalan-postgres

