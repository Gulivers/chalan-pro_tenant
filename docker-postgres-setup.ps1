# Script para configurar PostgreSQL 16 en Docker
# Chalan Inventory Transaction Database

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Configuracion de PostgreSQL 16 en Docker" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
Write-Host "Verificando Docker..." -ForegroundColor Yellow
try {
    docker --version | Out-Null
    Write-Host "[OK] Docker esta instalado" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker no esta disponible" -ForegroundColor Red
    Write-Host "Por favor, inicia Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# Verificar si Docker esta corriendo
Write-Host "Verificando si Docker esta corriendo..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker esta corriendo" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker no esta corriendo" -ForegroundColor Red
    Write-Host "Por favor, inicia Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# Detener y eliminar contenedor existente si existe
Write-Host "Verificando contenedores existentes..." -ForegroundColor Yellow
$existingContainer = docker ps -a --filter "name=chalan-postgres" --format "{{.Names}}"
if ($existingContainer -eq "chalan-postgres") {
    Write-Host "Contenedor existente encontrado, deteniendo..." -ForegroundColor Yellow
    docker stop chalan-postgres | Out-Null
    docker rm chalan-postgres | Out-Null
    Write-Host "[OK] Contenedor eliminado" -ForegroundColor Green
}

# Configuracion
$POSTGRES_USER = "postgres"
$POSTGRES_PASSWORD = "chalan2024"
$POSTGRES_DB = "chalan_inv_txn"
$PORT = "5432"

Write-Host ""
Write-Host "Configuracion:" -ForegroundColor Cyan
Write-Host "  Usuario: $POSTGRES_USER" -ForegroundColor White
Write-Host "  Contrasena: $POSTGRES_PASSWORD" -ForegroundColor White
Write-Host "  Base de datos: $POSTGRES_DB" -ForegroundColor White
Write-Host "  Puerto: $PORT" -ForegroundColor White
Write-Host ""

# Crear y ejecutar contenedor
Write-Host "Creando contenedor PostgreSQL 16..." -ForegroundColor Yellow

docker run `
    --name chalan-postgres `
    -e POSTGRES_USER=$POSTGRES_USER `
    -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD `
    -e POSTGRES_DB=$POSTGRES_DB `
    -p ${PORT}:5432 `
    -v chalan-postgres-data:/var/lib/postgresql/data `
    -d `
    postgres:16 `
    -c shared_buffers=256MB `
    -c max_connections=100 `
    -c effective_cache_size=1GB

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Contenedor creado exitosamente" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Error al crear el contenedor" -ForegroundColor Red
    exit 1
}

# Esperar a que PostgreSQL inicie
Write-Host ""
Write-Host "Esperando a que PostgreSQL inicie (esto puede tardar 10-15 segundos)..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

do {
    Start-Sleep -Seconds 1
    $attempt++
    $status = docker exec chalan-postgres pg_isready -U $POSTGRES_USER 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] PostgreSQL esta listo!" -ForegroundColor Green
        break
    }
    Write-Host "." -NoNewline -ForegroundColor Gray
} while ($attempt -lt $maxAttempts)

if ($attempt -ge $maxAttempts) {
    Write-Host ""
    Write-Host "[ERROR] PostgreSQL no inicio correctamente" -ForegroundColor Red
    Write-Host "Revisa los logs con: docker logs chalan-postgres" -ForegroundColor Yellow
    exit 1
}

# Mostrar informacion de conexion
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "PostgreSQL 16 esta listo para usar!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Cadena de conexion:" -ForegroundColor Cyan
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Puerto: $PORT" -ForegroundColor White
Write-Host "  Usuario: $POSTGRES_USER" -ForegroundColor White
Write-Host "  Contrasena: $POSTGRES_PASSWORD" -ForegroundColor White
Write-Host "  Base de datos: $POSTGRES_DB" -ForegroundColor White
Write-Host ""

Write-Host "Comandos utiles:" -ForegroundColor Cyan
Write-Host "  Conectar con psql: docker exec -it chalan-postgres psql -U postgres -d $POSTGRES_DB" -ForegroundColor Yellow
Write-Host "  Ver logs: docker logs chalan-postgres" -ForegroundColor Yellow
Write-Host "  Detener: docker stop chalan-postgres" -ForegroundColor Yellow
Write-Host "  Iniciar: docker start chalan-postgres" -ForegroundColor Yellow
Write-Host "  Eliminar: docker rm -f chalan-postgres" -ForegroundColor Yellow
Write-Host ""
