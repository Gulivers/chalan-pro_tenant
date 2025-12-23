# 📋 Plan: Clonar Repositorio a Ubuntu-House (Desarrollo Local)

## 🎯 Objetivo

Clonar el repositorio desde GitHub a `ubuntu-house` (entorno local) y configurarlo para desarrollo, asegurando que:
- ✅ Los cambios de código se sincronicen entre VPS y local vía GitHub
- ✅ Las configuraciones específicas de cada servidor NO se sincronicen
- ✅ PostgreSQL se conserve (aunque no hay datos críticos)
- ✅ Se limpien configuraciones viejas y obsoletas en local
- ✅ El entorno local use `docker-compose.dev.yml` y el VPS use `docker-compose.yml`
- ⚠️ **NO se harán cambios al repositorio sin consultar primero**

## 📍 Repositorio

**GitHub**: https://github.com/Gulivers/chalan-pro_tenant.git

## 📍 Estructura Esperada

### En VPS (Hostinger - Producción)
```
/opt/chalanpro/
├── .git/                    ← Repositorio Git (sincronizado con GitHub)
├── .gitignore              ← Configurado para VPS
├── docker-compose.yml      ← Producción (con SSL/HTTPS)
├── docker-compose.dev.yml  ← No se usa en VPS
├── nginx/
│   ├── default.conf        ← Producción (HTTPS)
│   └── default.dev.conf    ← Desarrollo
├── envs/
│   ├── backend.env         ← Producción (NO en Git)
│   ├── backend.dev.env     ← Desarrollo (NO en Git)
│   ├── postgres.env        ← Producción (NO en Git)
│   ├── pgadmin.env         ← Producción (NO en Git)
│   └── *.example.env       ← Templates (SÍ en Git)
├── scripts/
├── postgres_data/          ← Datos PostgreSQL (NO en Git)
└── app/                    ← Código de la aplicación
```

### En Ubuntu-House (Local - Desarrollo)
```
/home/oliver/shared/projects/chalanpro/
├── .git/                    ← Clonado desde GitHub
├── .gitignore              ← Heredado del repo (no se modifica)
├── docker-compose.yml      ← Producción (no se usa localmente)
├── docker-compose.dev.yml  ← Desarrollo (se usa localmente)
├── nginx/
│   ├── default.conf        ← Producción (no se usa)
│   └── default.dev.conf    ← Desarrollo (se usa)
├── envs/
│   ├── backend.env         ← Local (NO en Git, diferente al VPS)
│   ├── backend.dev.env     ← Local (NO en Git)
│   ├── postgres.env        ← Local (NO en Git)
│   ├── pgadmin.env         ← Local (NO en Git)
│   └── *.example.env       ← Templates (SÍ en Git)
├── scripts/
├── postgres_data/          ← Datos PostgreSQL local (NO en Git)
└── app/                    ← Código de la aplicación
```

## 🔧 Pasos del Plan

### FASE 1: Preparar Directorio Local

#### Paso 1.1: Verificar/Preparar Directorio de Trabajo

```bash
# En ubuntu-house
cd /home/oliver/shared/projects

# Si ya existe chalanpro, hacer backup
if [ -d "chalanpro" ]; then
    echo "⚠️ Directorio chalanpro ya existe"
    echo "Haciendo backup..."
    mv chalanpro chalanpro.backup.$(date +%Y%m%d_%H%M%S)
    echo "✓ Backup creado: chalanpro.backup.$(date +%Y%m%d_%H%M%S)"
fi
```

### FASE 2: Clonar Repositorio desde GitHub

#### Paso 2.1: Clonar Repositorio

```bash
# En ubuntu-house
cd /home/oliver/shared/projects

# Clonar desde GitHub
git clone https://github.com/Gulivers/chalan-pro_tenant.git chalanpro

cd chalanpro

# Verificar rama actual
git branch
git status

# Verificar estructura clonada
ls -la
ls -la app/
ls -la envs/
ls -la nginx/
```

#### Paso 2.2: Verificar que NO hay Archivos Sensibles

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar que NO hay archivos .env (deben estar en .gitignore)
ls envs/*.env 2>/dev/null && echo "⚠️ ERROR: Archivos .env presentes en repo" || echo "✓ No hay .env (correcto)"

# Verificar que postgres_data no está en el repo
ls postgres_data/ 2>/dev/null && echo "⚠️ ERROR: postgres_data presente en repo" || echo "✓ No hay postgres_data (correcto)"
```

#### Paso 2.3: Verificar .gitignore

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar que .gitignore existe y está configurado
cat .gitignore | head -20

# Verificar que .env está en .gitignore
grep -E "\.env$|envs/\*\.env" .gitignore && echo "✓ .env está en .gitignore" || echo "⚠️ .env NO está en .gitignore"

# Verificar que postgres_data está en .gitignore
grep "postgres_data" .gitignore && echo "✓ postgres_data está en .gitignore" || echo "⚠️ postgres_data NO está en .gitignore"
```

### FASE 3: Configuración Local (Ubuntu-House)

#### Paso 3.1: Crear Archivos .env Locales desde Templates

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar qué templates existen
ls -la envs/*.example.env envs/*.dev.example.env 2>/dev/null

# Crear backend.dev.env desde template
if [ -f "envs/backend.dev.example.env" ]; then
    cp envs/backend.dev.example.env envs/backend.dev.env
    echo "✓ Creado envs/backend.dev.env"
else
    echo "⚠️ No existe template backend.dev.example.env"
    echo "Creando archivo básico..."
    cat > envs/backend.dev.env << 'EOF'
DEBUG=True
DJANGO_SECRET_KEY=changeme-dev-secret-key-local-ubuntu-house
ALLOWED_HOSTS="192.168.0.105,192.168.0.248,localhost,127.0.0.1,*.chalanpro.net"

DATABASE_URL=postgres://chalanpro_user:password@postgres:5432/chalanpro

CORS_ALLOW_ALL_ORIGINS=True
TENANT_BASE_DOMAIN=chalanpro.net

CSRF_TRUSTED_ORIGINS=http://192.168.0.105,http://192.168.0.248:8080,http://192.168.0.248:8000,http://localhost:8080,http://127.0.0.1:8080,http://localhost:8000,http://127.0.0.1:8000

FRONT_URL=http://192.168.0.105
EOF
    echo "✓ Creado envs/backend.dev.env básico"
fi

# Crear postgres.env desde template (si existe)
if [ -f "envs/postgres.example.env" ]; then
    cp envs/postgres.example.env envs/postgres.env
    echo "✓ Creado envs/postgres.env"
else
    echo "⚠️ No existe template postgres.example.env"
    echo "Creando archivo básico..."
    cat > envs/postgres.env << 'EOF'
POSTGRES_USER=chalanpro_user
POSTGRES_PASSWORD=password_local_ubuntu_house
POSTGRES_DB=chalanpro
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
EOF
    echo "✓ Creado envs/postgres.env básico"
fi

# Crear pgadmin.env desde template (si existe)
if [ -f "envs/pgadmin.example.env" ]; then
    cp envs/pgadmin.example.env envs/pgadmin.env
    echo "✓ Creado envs/pgadmin.env"
else
    echo "⚠️ No existe template pgadmin.example.env"
    echo "Creando archivo básico..."
    cat > envs/pgadmin.env << 'EOF'
PGADMIN_DEFAULT_EMAIL=admin@chalanpro.local
PGADMIN_DEFAULT_PASSWORD=admin_local_ubuntu_house
PGADMIN_CONFIG_SERVER_MODE=False
PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED=False
EOF
    echo "✓ Creado envs/pgadmin.env básico"
fi
```

#### Paso 3.2: Configurar backend.dev.env para Local

Editar `envs/backend.dev.env` con valores locales específicos:

```bash
# En ubuntu-house
nano envs/backend.dev.env
# O usar tu editor preferido: code, vim, etc.
```

**Configuración sugerida para local** (ajustar según tu entorno):

```env
DEBUG=True
DJANGO_SECRET_KEY=changeme-dev-secret-key-local-ubuntu-house-$(date +%s)
ALLOWED_HOSTS="192.168.0.105,192.168.0.248,localhost,127.0.0.1,*.chalanpro.net"

DATABASE_URL=postgres://chalanpro_user:password_local_ubuntu_house@postgres:5432/chalanpro

CORS_ALLOW_ALL_ORIGINS=True
TENANT_BASE_DOMAIN=chalanpro.net

CSRF_TRUSTED_ORIGINS=http://192.168.0.105,http://192.168.0.248:8080,http://192.168.0.248:8000,http://localhost:8080,http://127.0.0.1:8080,http://localhost:8000,http://127.0.0.1:8000

FRONT_URL=http://192.168.0.105
```

**Nota**: 
- Ajustar IPs (`192.168.0.105`, `192.168.0.248`) según tu configuración local
- Usar contraseñas diferentes a las del VPS
- El `DJANGO_SECRET_KEY` debe ser único para local

#### Paso 3.3: Configurar postgres.env para Local

Editar `envs/postgres.env` con valores locales:

```bash
# En ubuntu-house
nano envs/postgres.env
```

**Configuración sugerida**:

```env
POSTGRES_USER=chalanpro_user
POSTGRES_PASSWORD=password_local_ubuntu_house
POSTGRES_DB=chalanpro
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

**Nota**: Usar contraseñas diferentes a las del VPS para evitar conflictos.

#### Paso 3.4: Verificar nginx/default.dev.conf para Local

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar que existe
ls -la nginx/default.dev.conf

# Ver contenido
cat nginx/default.dev.conf
```

Asegurar que `server_name` incluya las IPs locales:

```nginx
server_name 192.168.0.105 192.168.0.248 localhost *.chalanpro.net _;
```

Si necesitas ajustar las IPs, puedes editar el archivo (pero **NO hacer commit** sin consultar).

#### Paso 3.5: Configurar /etc/hosts para Dominios Locales

```bash
# En ubuntu-house
sudo nano /etc/hosts
```

Agregar (ajustar IPs según corresponda):

```
192.168.0.105  chalanpro.net
192.168.0.105  api.chalanpro.net
192.168.0.105  tenant1.chalanpro.net
# Agregar más tenants según necesidad
```

**Nota**: Ajustar la IP (`192.168.0.105`) según tu configuración local.

### FASE 4: Limpieza de Archivos Viejos (Solo Local)

#### Paso 4.1: Identificar Archivos a Eliminar

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Buscar archivos docker-compose viejos en app/
find app/ -name "docker-compose*.yml" -type f

# Buscar otros archivos de configuración viejos
ls -la app/docker-compose*.yml 2>/dev/null
ls -la app/docker-compose*.ps1 2>/dev/null
ls -la app/docker-postgres*.ps1 2>/dev/null
ls -la app/test-postgres*.ps1 2>/dev/null
```

#### Paso 4.2: Eliminar Archivos Obsoletos (Solo Local, NO en Git)

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar que los archivos existen antes de eliminar
if [ -f "app/docker-compose-local.yml" ]; then
    rm -f app/docker-compose-local.yml
    echo "✓ Eliminado app/docker-compose-local.yml"
fi

if [ -f "app/docker-compose.local.yml" ]; then
    rm -f app/docker-compose.local.yml
    echo "✓ Eliminado app/docker-compose.local.yml"
fi

if [ -f "app/docker-compose.stage.yml" ]; then
    rm -f app/docker-compose.stage.yml
    echo "✓ Eliminado app/docker-compose.stage.yml"
fi

# Eliminar scripts PowerShell (si no se usan en Linux)
if [ -f "app/docker-postgres-manage.ps1" ]; then
    rm -f app/docker-postgres-manage.ps1
    echo "✓ Eliminado app/docker-postgres-manage.ps1"
fi

if [ -f "app/docker-postgres-setup.ps1" ]; then
    rm -f app/docker-postgres-setup.ps1
    echo "✓ Eliminado app/docker-postgres-setup.ps1"
fi

if [ -f "app/test-postgres-connection.ps1" ]; then
    rm -f app/test-postgres-connection.ps1
    echo "✓ Eliminado app/test-postgres-connection.ps1"
fi

# Verificar que se eliminaron
echo ""
echo "Verificando archivos eliminados..."
ls -la app/docker-compose*.yml 2>/dev/null || echo "✓ No hay archivos docker-compose viejos en app/"
ls -la app/*.ps1 2>/dev/null || echo "✓ No hay scripts PowerShell en app/"
```

**⚠️ IMPORTANTE**: Estos archivos se eliminan solo localmente. Si están en el repositorio Git, se pueden eliminar del repo más adelante (con tu aprobación).

#### Paso 4.3: Verificar que Archivos Eliminados NO Están en Git

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar estado de Git
git status

# Verificar que los archivos eliminados no aparecen como cambios
git status | grep -E "docker-compose-local|docker-compose.local|docker-compose.stage|\.ps1" && echo "⚠️ Archivos aún en Git" || echo "✓ Archivos no están en Git o ya fueron eliminados del repo"
```

### FASE 5: Configurar PostgreSQL Local

#### Paso 5.1: Verificar Volumen de PostgreSQL

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar que postgres_data existe (o se creará al levantar)
ls -la postgres_data/ 2>/dev/null || echo "✓ postgres_data se creará al iniciar PostgreSQL"

# Si existe y quieres empezar limpio (opcional, solo si no hay datos importantes)
# rm -rf postgres_data/
# echo "✓ postgres_data eliminado (se recreará limpio)"
```

#### Paso 5.2: Iniciar Servicios con Docker Compose Dev

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar que docker-compose.dev.yml existe
ls -la docker-compose.dev.yml

# Levantar servicios en modo desarrollo
docker compose -f docker-compose.dev.yml up -d postgres

# Esperar a que PostgreSQL esté listo
echo "Esperando a que PostgreSQL esté listo..."
sleep 15

# Verificar que PostgreSQL está corriendo
docker compose -f docker-compose.dev.yml ps postgres

# Verificar logs
docker compose -f docker-compose.dev.yml logs postgres | tail -30
```

#### Paso 5.3: Ejecutar Migraciones (si es necesario)

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Levantar backend temporalmente para migraciones
docker compose -f docker-compose.dev.yml up -d backend

# Esperar a que backend esté listo
echo "Esperando a que backend esté listo..."
sleep 15

# Verificar que backend está corriendo
docker compose -f docker-compose.dev.yml ps backend

# Ejecutar migraciones
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate

# Verificar que las migraciones se ejecutaron
docker compose -f docker-compose.dev.yml exec backend python manage.py showmigrations | tail -20
```

### FASE 6: Verificación Final

#### Paso 6.1: Verificar Estructura de Archivos

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar estructura
tree -L 2 -I 'node_modules|__pycache__|*.pyc|postgres_data|.git' 2>/dev/null || ls -la

# Verificar que .env están presentes pero NO en Git
echo ""
echo "Verificando archivos .env..."
ls envs/*.env && echo "✓ Archivos .env presentes localmente"
git status | grep "\.env$" && echo "⚠️ ERROR: .env en Git" || echo "✓ .env NO en Git (correcto)"

# Verificar que postgres_data NO está en Git
echo ""
echo "Verificando postgres_data..."
git status | grep "postgres_data" && echo "⚠️ ERROR: postgres_data en Git" || echo "✓ postgres_data NO en Git (correcto)"
```

#### Paso 6.2: Verificar Configuración Git

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar rama
git branch

# Verificar estado
git status

# Verificar remoto
git remote -v

# Verificar que el remoto apunta a GitHub
git remote get-url origin
```

#### Paso 6.3: Probar Servicios

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Levantar todos los servicios en modo desarrollo
docker compose -f docker-compose.dev.yml up -d

# Esperar a que los servicios estén listos
echo "Esperando a que los servicios estén listos..."
sleep 20

# Verificar que todos los servicios están corriendo
docker compose -f docker-compose.dev.yml ps

# Verificar logs
docker compose -f docker-compose.dev.yml logs --tail=50
```

#### Paso 6.4: Probar Acceso Web

```bash
# En ubuntu-house
# Probar acceso a:
# - http://192.168.0.105 (frontend)
# - http://192.168.0.105/api/ (backend API)
# - http://192.168.0.105/ws/ (websocket)
# - http://192.168.0.105:5050 (pgadmin)

# Probar con curl
curl -I http://192.168.0.105
curl -I http://192.168.0.105/api/
```

### FASE 7: Configurar Workflow de Sincronización

#### Paso 7.1: Crear Rama Local de Desarrollo (Opcional)

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar ramas disponibles
git branch -a

# Crear rama local para desarrollo (opcional)
# git checkout -b ubuntu_house

# O usar develop si existe
# git checkout develop
# git pull origin develop

# O trabajar directamente en main (según tu preferencia)
git checkout main
```

#### Paso 7.2: Documentar Configuración Local (Opcional)

Crear archivo `LOCAL_SETUP.md` (NO en Git, solo local):

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

cat > LOCAL_SETUP.md << 'EOF'
# Configuración Local - Ubuntu-House

## Archivos .env Locales
- `envs/backend.dev.env`: Configuración backend local
- `envs/postgres.env`: Configuración PostgreSQL local
- `envs/pgadmin.env`: Configuración PgAdmin local

## IPs y Dominios Locales
- IP Principal: 192.168.0.105
- Dominio: chalanpro.net (configurado en /etc/hosts)

## Comandos Útiles

# Levantar servicios
docker compose -f docker-compose.dev.yml up -d

# Ver logs
docker compose -f docker-compose.dev.yml logs -f

# Detener servicios
docker compose -f docker-compose.dev.yml down

# Reiniciar servicios
docker compose -f docker-compose.dev.yml restart

# Desarrollo frontend con hot-reload
cd app/vuefrontend && npm run serve

# O usar el servicio frontend-dev
docker compose -f docker-compose.dev.yml --profile dev up frontend-dev
EOF

echo "✓ Creado LOCAL_SETUP.md (solo local, no en Git)"
```

**Nota**: Este archivo es solo para referencia local, no se sube a Git.

## ✅ Checklist de Verificación

### En Ubuntu-House (Local)
- [ ] Repositorio clonado desde GitHub correctamente
- [ ] Archivos `.env` locales creados (NO en Git)
- [ ] `backend.dev.env` configurado con valores locales
- [ ] `postgres.env` configurado con valores locales
- [ ] `pgadmin.env` configurado con valores locales
- [ ] `/etc/hosts` configurado para dominios locales
- [ ] Archivos docker-compose viejos eliminados localmente
- [ ] PostgreSQL funcionando
- [ ] Migraciones ejecutadas
- [ ] Servicios Docker levantados correctamente
- [ ] Acceso web funcionando
- [ ] WebSocket funcionando
- [ ] Git remoto configurado correctamente (GitHub)

## 🚨 Precauciones Importantes

### ⚠️ NUNCA Hacer Push de (sin consultar):

1. **Archivos `.env`** con secretos
   - `envs/backend.env`
   - `envs/backend.dev.env`
   - `envs/postgres.env`
   - `envs/pgadmin.env`

2. **Datos de base de datos**
   - `postgres_data/`
   - `pgadmin_data/`

3. **Configuraciones locales específicas**
   - Cambios en `nginx/default.dev.conf` con IPs locales
   - Cualquier archivo con información local específica

4. **Archivos temporales o de desarrollo**
   - `LOCAL_SETUP.md` (si se crea)
   - Cualquier archivo de prueba

### ✅ SÍ Se Pueden Hacer Push de (después de consultar):

1. **Código de la aplicación**
   - Cambios en `app/` (código, features, fixes)

2. **Configuraciones compartidas** (después de revisar)
   - Cambios en `docker-compose.yml` o `docker-compose.dev.yml`
   - Cambios en `nginx/default.conf` o `nginx/default.dev.conf`
   - Scripts de utilidad en `scripts/`

3. **Templates de configuración**
   - Actualizaciones a `envs/*.example.env`

### 📝 Workflow de Sincronización

1. **Desarrollo en Local (ubuntu-house)**
   ```bash
   # Hacer cambios en código
   git add app/
   git commit -m "feat: nueva funcionalidad"
   
   # ⚠️ NO hacer push todavía - consultar primero
   # git push origin <rama>
   ```

2. **Antes de Hacer Push**
   - ✅ Verificar que NO hay archivos `.env` en staging
   - ✅ Verificar que NO hay `postgres_data/` en staging
   - ✅ Revisar cambios con `git status` y `git diff`
   - ✅ Consultar antes de hacer push

3. **Después de Aprobación**
   ```bash
   # Push a GitHub
   git push origin <rama>
   ```

4. **Actualizar VPS desde GitHub** (se hace en VPS, no aquí)
   ```bash
   # En VPS (no ejecutar en local)
   # cd /opt/chalanpro
   # git pull origin main
   # docker compose restart backend frontend
   ```

## 📝 Notas Adicionales

### Diferencia entre VPS y Local

| Aspecto | VPS (Hostinger) | Ubuntu-House (Local) |
|---------|----------------|---------------------|
| Docker Compose | `docker-compose.yml` | `docker-compose.dev.yml` |
| Nginx Config | `nginx/default.conf` | `nginx/default.dev.conf` |
| Backend Env | `envs/backend.env` | `envs/backend.dev.env` |
| SSL/HTTPS | ✅ Sí (Let's Encrypt) | ❌ No (solo HTTP) |
| Dominio | chalanpro.net (real) | chalanpro.net (local via /etc/hosts) |
| PostgreSQL | Datos de producción | Datos de desarrollo |
| Repositorio | Sincronizado con GitHub | Clonado desde GitHub |

### Comandos Útiles

#### En Local (Ubuntu-House)
```bash
# Desarrollo frontend con hot-reload
cd app/vuefrontend && npm run serve

# O usar el servicio frontend-dev
docker compose -f docker-compose.dev.yml --profile dev up frontend-dev

# Ver logs en tiempo real
docker compose -f docker-compose.dev.yml logs -f backend

# Acceder a PostgreSQL
docker compose -f docker-compose.dev.yml exec postgres psql -U chalanpro_user -d chalanpro

# Verificar estado de Git
git status
git diff

# Ver qué archivos están siendo rastreados
git ls-files | grep -E "\.env$|postgres_data"
```

### Verificación Antes de Push

```bash
# En ubuntu-house
cd /home/oliver/shared/projects/chalanpro

# Verificar que NO hay archivos sensibles en staging
git status
git diff --cached --name-only | grep -E "\.env$|postgres_data" && echo "⚠️ ERROR: Archivos sensibles en staging!" || echo "✓ No hay archivos sensibles"

# Verificar que .gitignore funciona
git check-ignore envs/backend.dev.env && echo "✓ .env ignorado correctamente" || echo "⚠️ .env NO está siendo ignorado"
git check-ignore postgres_data/ && echo "✓ postgres_data ignorado correctamente" || echo "⚠️ postgres_data NO está siendo ignorado"
```

---

## 🎯 Resumen para el Agente

**Tarea principal**: Clonar repositorio desde GitHub a ubuntu-house y configurarlo para desarrollo local, asegurando que las configuraciones específicas de cada servidor NO se sincronicen.

**Repositorio**: https://github.com/Gulivers/chalan-pro_tenant.git

**Archivos críticos a NO sincronizar**:
- `envs/*.env` (solo templates `.example.env` en Git)
- `postgres_data/`
- Configuraciones locales específicas

**Archivos a sincronizar** (después de consultar):
- Todo el código en `app/`
- Configuraciones Docker Compose (después de revisar)
- Configuraciones Nginx (después de revisar)
- Scripts de utilidad general

**⚠️ IMPORTANTE**: NO hacer push al repositorio sin consultar primero al usuario.

**Prioridad**: Alta - Esto permitirá desarrollo local sin afectar producción.

**Riesgo**: Bajo - Solo se trabaja en local, no se afecta el VPS.
