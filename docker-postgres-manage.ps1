# Script de gestión para PostgreSQL Docker
# Chalan Inventory Transaction

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "logs", "status", "connect", "backup", "remove")]
    [string]$Action = "status"
)

$CONTAINER_NAME = "chalan-postgres"

function Show-ContainerStatus {
    Write-Host "Estado del contenedor:" -ForegroundColor Cyan
    docker ps -a --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

function Start-Container {
    Write-Host "Iniciando contenedor $CONTAINER_NAME..." -ForegroundColor Yellow
    docker start $CONTAINER_NAME
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Contenedor iniciado" -ForegroundColor Green
        Start-Sleep -Seconds 3
        Show-ContainerStatus
    } else {
        Write-Host "[ERROR] Error al iniciar el contenedor" -ForegroundColor Red
    }
}

function Stop-Container {
    Write-Host "Deteniendo contenedor $CONTAINER_NAME..." -ForegroundColor Yellow
    docker stop $CONTAINER_NAME
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Contenedor detenido" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Error al detener el contenedor" -ForegroundColor Red
    }
}

function Restart-Container {
    Write-Host "Reiniciando contenedor $CONTAINER_NAME..." -ForegroundColor Yellow
    docker restart $CONTAINER_NAME
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Contenedor reiniciado" -ForegroundColor Green
        Start-Sleep -Seconds 3
        Show-ContainerStatus
    } else {
        Write-Host "[ERROR] Error al reiniciar el contenedor" -ForegroundColor Red
    }
}

function Show-Logs {
    Write-Host "Mostrando logs (ultimas 50 lineas):" -ForegroundColor Cyan
    docker logs --tail 50 -f $CONTAINER_NAME
}

function Connect-Postgres {
    Write-Host "Conectando a PostgreSQL..." -ForegroundColor Cyan
    docker exec -it $CONTAINER_NAME psql -U postgres -d chalan_inv_txn
}

function Backup-Database {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "chalan_postgres_backup_$timestamp.sql"
    
    Write-Host "Creando backup: $backupFile..." -ForegroundColor Yellow
    docker exec $CONTAINER_NAME pg_dump -U postgres chalan_inv_txn > $backupFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Backup creado exitosamente: $backupFile" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Error al crear el backup" -ForegroundColor Red
    }
}

function Remove-Container {
    Write-Host "Esta accion eliminara el contenedor y TODOS los datos." -ForegroundColor Red
    Write-Host "Los datos persistidos en el volumen se mantendran." -ForegroundColor Yellow
    $confirmation = Read-Host "Estas seguro? (escribe 'SI' para confirmar)"
    
    if ($confirmation -eq "SI") {
        Write-Host "Eliminando contenedor..." -ForegroundColor Yellow
        docker rm -f $CONTAINER_NAME
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Contenedor eliminado" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Error al eliminar el contenedor" -ForegroundColor Red
        }
    } else {
        Write-Host "Operacion cancelada" -ForegroundColor Yellow
    }
}

# Ejecutar acción
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Gestion de PostgreSQL Docker" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

switch ($Action) {
    "start" { Start-Container }
    "stop" { Stop-Container }
    "restart" { Restart-Container }
    "logs" { Show-Logs }
    "status" { Show-ContainerStatus }
    "connect" { Connect-Postgres }
    "backup" { Backup-Database }
    "remove" { Remove-Container }
    default { 
        Write-Host "Accion no reconocida" -ForegroundColor Red
        Write-Host ""
        Write-Host "Uso: .\docker-postgres-manage.ps1 -Action accion" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Acciones disponibles:" -ForegroundColor Cyan
        Write-Host "  start   - Iniciar contenedor" -ForegroundColor White
        Write-Host "  stop    - Detener contenedor" -ForegroundColor White
        Write-Host "  restart - Reiniciar contenedor" -ForegroundColor White
        Write-Host "  logs    - Ver logs" -ForegroundColor White
        Write-Host "  status  - Ver estado (por defecto)" -ForegroundColor White
        Write-Host "  connect - Conectar con psql" -ForegroundColor White
        Write-Host "  backup  - Crear backup de la BD" -ForegroundColor White
        Write-Host "  remove  - Eliminar contenedor" -ForegroundColor White
    }
}

