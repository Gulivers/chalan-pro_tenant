# Script para probar la conexión a PostgreSQL en Docker

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Prueba de Conexión a PostgreSQL" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$CONTAINER_NAME = "chalan-postgres"

# 1. Verificar que el contenedor existe
Write-Host "1. Verificando contenedor..." -ForegroundColor Yellow
$containerExists = docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | Select-Object -First 1

if ($containerExists -eq $CONTAINER_NAME) {
    Write-Host "   ✓ Contenedor encontrado" -ForegroundColor Green
} else {
    Write-Host "   ✗ Contenedor no encontrado" -ForegroundColor Red
    Write-Host "   Ejecuta: .\docker-postgres-setup.ps1" -ForegroundColor Yellow
    exit 1
}

# 2. Verificar que está corriendo
Write-Host "2. Verificando estado..." -ForegroundColor Yellow
$isRunning = docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | Select-Object -First 1

if ($isRunning -eq $CONTAINER_NAME) {
    Write-Host "   ✓ Contenedor está corriendo" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Contenedor no está corriendo" -ForegroundColor Yellow
    Write-Host "   Intentando iniciar..." -ForegroundColor Yellow
    docker start $CONTAINER_NAME | Out-Null
    Start-Sleep -Seconds 5
    
    $isRunningNow = docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | Select-Object -First 1
    if ($isRunningNow -eq $CONTAINER_NAME) {
        Write-Host "   ✓ Contenedor iniciado" -ForegroundColor Green
    } else {
        Write-Host "   ✗ No se pudo iniciar el contenedor" -ForegroundColor Red
        Write-Host "   Ver logs: docker logs $CONTAINER_NAME" -ForegroundColor Yellow
        exit 1
    }
}

# 3. Verificar que PostgreSQL responde
Write-Host "3. Verificando que PostgreSQL responde..." -ForegroundColor Yellow
$pgReady = docker exec $CONTAINER_NAME pg_isready -U postgres 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ PostgreSQL está listo" -ForegroundColor Green
} else {
    Write-Host "   ✗ PostgreSQL no responde" -ForegroundColor Red
    Write-Host "   Esperando 5 segundos más..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    $pgReadyAgain = docker exec $CONTAINER_NAME pg_isready -U postgres 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ PostgreSQL está listo" -ForegroundColor Green
    } else {
        Write-Host "   ✗ PostgreSQL aún no responde" -ForegroundColor Red
        exit 1
    }
}

# 4. Probar conexión
Write-Host "4. Probando conexión..." -ForegroundColor Yellow
$connectionTest = docker exec $CONTAINER_NAME psql -U postgres -d chalan_inv_txn -c "SELECT version();" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ Conexión exitosa" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Información de PostgreSQL:" -ForegroundColor Cyan
    $version = docker exec $CONTAINER_NAME psql -U postgres -d chalan_inv_txn -t -c "SELECT version();" 2>&1
    Write-Host "   $version" -ForegroundColor White
} else {
    Write-Host "   ✗ Error de conexión" -ForegroundColor Red
    Write-Host "   $connectionTest" -ForegroundColor Yellow
    exit 1
}

# 5. Verificar puerto
Write-Host "5. Verificando puerto 5432..." -ForegroundColor Yellow
$portTest = netstat -ano | findstr ":5432" | findstr "LISTENING"

if ($portTest) {
    Write-Host "   ✓ Puerto 5432 está en uso" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Puerto 5432 no está escuchando" -ForegroundColor Yellow
    Write-Host "   Esto puede ser normal si Docker usa un método diferente de networking" -ForegroundColor Yellow
}

# Resumen
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "✓ PostgreSQL está funcionando correctamente" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Puedes conectarte con:" -ForegroundColor Cyan
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Puerto: 5432" -ForegroundColor White
Write-Host "  Usuario: postgres" -ForegroundColor White
Write-Host "  Base de datos: chalan_inv_txn" -ForegroundColor White
Write-Host ""
Write-Host "O usando el comando:" -ForegroundColor Cyan
Write-Host "  docker exec -it chalan-postgres psql -U postgres -d chalan_inv_txn" -ForegroundColor Yellow
Write-Host ""

