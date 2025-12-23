# Configuración del Servidor Local de Desarrollo (ubuntu-house)

Este documento describe la configuración completa del servidor local de desarrollo para Chalan-Pro en ubuntu-house.

## 📋 Tabla de Contenidos

1. [Arquitectura General](#arquitectura-general)
2. [Configuración del Backend](#configuración-del-backend)
3. [Configuración del Frontend](#configuración-del-frontend)
4. [Configuración de Docker Compose](#configuración-de-docker-compose)
5. [Configuración Multi-Tenant](#configuración-multi-tenant)
6. [WebSockets con Daphne](#websockets-con-daphne)
7. [Flujo de Peticiones](#flujo-de-peticiones)
8. [Archivos de Configuración Clave](#archivos-de-configuración-clave)
9. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura General

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                    Servidor ubuntu-house                     │
│                     (192.168.0.105)                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend (npm run serve)                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Puerto: 8080                                         │   │
│  │ Host: 0.0.0.0                                        │   │
│  │ URL: http://192.168.0.105:8080                      │   │
│  │                                                       │   │
│  │ Proxy Webpack:                                       │   │
│  │   /api/* → http://localhost:8000                    │   │
│  │   /admin/* → http://localhost:8000                  │   │
│  │   /static/* → http://localhost:8000                 │   │
│  │   /media/* → http://localhost:8000                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Backend (Daphne + Django)                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Puerto: 8000                                         │   │
│  │ Host: 0.0.0.0                                        │   │
│  │ URL: http://192.168.0.105:8000                      │   │
│  │                                                       │   │
│  │ Servidor: Daphne (ASGI)                              │   │
│  │ Aplicación: project.asgi:application                 │   │
│  │                                                       │   │
│  │ WebSocket: ws://test-dominio-local.chalanpro.net:8000│  │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  PostgreSQL                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Puerto: 5432                                         │   │
│  │ Base de datos: chalanpro                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Puertos Utilizados

- **8080**: Frontend (npm run serve con hot-reload)
- **8000**: Backend (Daphne + Django)
- **5432**: PostgreSQL
- **5050**: PgAdmin (opcional)
- **80**: Nginx (opcional, para servir archivos estáticos)

---

## 🔧 Configuración del Backend

### Servidor ASGI con Daphne

El backend utiliza **Daphne** (no Gunicorn) para soportar WebSockets y conexiones ASGI.

#### Archivo: `docker-compose.dev.yml`

```yaml
backend:
  command: >
    sh -c "python manage.py collectstatic --noinput &&
           daphne -b 0.0.0.0 -p 8000 project.asgi:application"
```

**Importante**: 
- Usa `daphne` en lugar de `gunicorn` para soportar WebSockets
- Escucha en `0.0.0.0:8000` para aceptar conexiones desde cualquier interfaz
- La aplicación ASGI está en `project.asgi:application`

### Configuración ASGI (`app/project/asgi.py`)

```python
# Para desarrollo local, simplificar el stack de WebSocket
# En producción, usar TenantASGIMiddleware para multi-tenant
if settings.DEBUG:
    # Desarrollo local: stack simple sin middleware de tenant (más fácil de debuggear)
    websocket_stack = AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    )
else:
    # Producción: stack completo con middleware de tenant
    websocket_stack = TenantASGIMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
    )

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": websocket_stack,
})
```

**Características**:
- En desarrollo local (`DEBUG=True`): Stack simple sin middleware de tenant para facilitar debugging
- En producción (`DEBUG=False`): Stack completo con `TenantASGIMiddleware` para multi-tenant
- Soporta tanto HTTP como WebSocket

### Routing de WebSocket (`app/appschedule/routing.py`)

```python
websocket_urlpatterns = [
    re_path(r"^ws/calendar-updates/$", consumers.EventConsumer.as_asgi()),
    re_path(r"^ws/schedule/event/(?P<pk>\d+)/$", consumers.EventNoteConsumer.as_asgi()),
    re_path(r"^ws/schedule/event/(?P<event_id>\d+)/chat/$", consumers.EventChatConsumer.as_asgi()),
    re_path(r'^ws/schedule/unread/user/(?P<user_id>\d+)/$', UnreadNotificationConsumer.as_asgi()),
]
```

**Nota importante**: En Channels, el path **NO incluye el slash inicial**. Por ejemplo:
- Path recibido: `ws/calendar-updates/`
- Patrón regex: `^ws/calendar-updates/$`

### Variables de Entorno (`envs/backend.dev.env`)

```bash
DEBUG=True
ALLOWED_HOSTS="192.168.0.105,192.168.0.248,localhost,127.0.0.1,api.chalanpro.net,chalanpro.net,*.chalanpro.net"
TENANT_BASE_DOMAIN=chalanpro.net
FRONT_URL=http://192.168.0.105:8080
CSRF_TRUSTED_ORIGINS=http://192.168.0.105,http://192.168.0.105:8080,http://*.chalanpro.net,http://*.chalanpro.net:8080
CORS_ALLOW_ALL_ORIGINS=True
```

**Puntos clave**:
- `DEBUG=True`: Habilita modo desarrollo y simplifica el stack de WebSocket
- `ALLOWED_HOSTS`: Incluye la IP local y dominios de tenant
- `TENANT_BASE_DOMAIN`: Dominio base para multi-tenant
- `FRONT_URL`: URL del frontend para redirecciones

---

## 🎨 Configuración del Frontend

### Servidor de Desarrollo (`npm run serve`)

El frontend se ejecuta con `npm run serve` desde `app/vuefrontend/` para tener hot-reload.

#### Comando

```bash
cd /home/oliver/shared/projects/chalanpro/app/vuefrontend
npm run serve
```

### Configuración Vue CLI (`app/vuefrontend/vue.config.js`)

#### DevServer

```javascript
devServer: {
  host: '0.0.0.0',
  port: 8080,
  allowedHosts: 'all', // Permite cualquier dominio en desarrollo local
  client: {
    webSocketURL: 'auto://0.0.0.0:0/ws'
  },
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      ws: true,
      onProxyReq: (proxyReq, req, res) => {
        const host = req.headers.host;
        if (host) {
          const hostWithoutPort = host.split(':')[0];
          proxyReq.setHeader('Host', hostWithoutPort);
        }
      },
    },
    // ... más proxies para /admin, /static, /media, /ws
  },
}
```

**Características importantes**:
- `host: '0.0.0.0'`: Permite acceso desde cualquier interfaz de red
- `allowedHosts: 'all'`: Permite cualquier dominio (necesario para multi-tenant)
- `onProxyReq`: Preserva el header `Host` sin el puerto para que `django-tenants` identifique correctamente el tenant

### Resolución de URLs (`app/vuefrontend/src/main.js`)

#### API Base URL

```javascript
const resolveApiBaseUrl = () => {
  // En desarrollo local con npm run serve, usar ruta relativa para que el proxy funcione
  if (isLocalLikeHost(hostname) || isDevPort) {
    // Retornar '/' para que las peticiones pasen por el proxy de vue.config.js
    return '/';
  }
  // ... resto de la lógica para producción
};
```

**Importante**: En desarrollo local, retorna `'/'` (ruta relativa) para que todas las peticiones pasen por el proxy de webpack.

#### WebSocket Base URL

```javascript
const resolveWsBaseUrl = (apiUrl) => {
  // En desarrollo local con npm run serve, conectar directamente al backend
  // para WebSockets (el proxy de webpack tiene problemas con WebSockets)
  if (isLocalLikeHost(hostname) || isDevPort) {
    // Conectar directamente al backend en el puerto 8000
    // Usar el hostname actual para mantener el dominio del tenant
    return ensureTrailingSlash(`ws://${hostname}:8000`);
  }
  // ... resto de la lógica para producción
};
```

**Importante**: 
- En desarrollo local, el WebSocket se conecta **directamente** al backend en el puerto 8000
- NO pasa por el proxy de webpack (tiene problemas con WebSockets)
- Usa el hostname actual (ej: `test-dominio-local.chalanpro.net`) para mantener el dominio del tenant

### Construcción de URLs WebSocket (`app/vuefrontend/src/mixins/appMixin.js`)

```javascript
buildWsUrl(path = '') {
  const base = this.getWsBaseUrl();
  return `${stripTrailingSlash(base)}/${stripLeadingSlash(path)}`;
}
```

**Ejemplo de uso**:
```javascript
this.wsUrl = this.buildWsUrl('ws/calendar-updates/');
// Resultado: ws://test-dominio-local.chalanpro.net:8000/ws/calendar-updates/
```

---

## 🐳 Configuración de Docker Compose

### Archivo: `docker-compose.dev.yml`

#### Servicios Principales

1. **PostgreSQL**: Base de datos
2. **Backend**: Django + Daphne en puerto 8000
3. **Frontend-dev**: Opcional, para ejecutar `npm run serve` en Docker
4. **Nginx**: Opcional, para servir archivos estáticos
5. **PgAdmin**: Opcional, para administrar PostgreSQL

#### Backend Service

```yaml
backend:
  build:
    context: ./app
    dockerfile: Dockerfile.backend
  env_file:
    - ./envs/backend.dev.env
  volumes:
    - ./app:/app  # Montaje para desarrollo (hot-reload de código)
  ports:
    - "8000:8000"
  command: >
    sh -c "python manage.py collectstatic --noinput &&
           daphne -b 0.0.0.0 -p 8000 project.asgi:application"
```

**Características**:
- Volumen montado para desarrollo: cambios en el código se reflejan inmediatamente
- Puerto 8000 expuesto para acceso desde el host
- Comando usa Daphne (no Gunicorn)

---

## 🏢 Configuración Multi-Tenant

### Dominios Locales

Para desarrollo local, los dominios de tenant se resuelven mediante `/etc/hosts`:

```bash
# /etc/hosts
192.168.0.105 chalanpro.net
192.168.0.105 api.chalanpro.net
192.168.0.105 test-dominio-local.chalanpro.net
192.168.0.105 test-ii-dominio-local.chalanpro.net
# ... más dominios según sea necesario
```

### Script para Actualizar `/etc/hosts`

El script `scripts/update_hosts.sh` actualiza automáticamente `/etc/hosts` con los dominios necesarios.

**Uso**:
```bash
sudo ./scripts/update_hosts.sh
```

### Identificación de Tenant

En desarrollo local:
- El frontend accede mediante `http://test-dominio-local.chalanpro.net:8080`
- El proxy de webpack preserva el header `Host` sin el puerto
- Django recibe el header `Host: test-dominio-local.chalanpro.net`
- `django-tenants` identifica el tenant basándose en el dominio

### WebSocket Multi-Tenant

Para WebSockets:
- El frontend se conecta a `ws://test-dominio-local.chalanpro.net:8000/ws/calendar-updates/`
- El hostname se mantiene para que `django-tenants` identifique el tenant
- En desarrollo local, el middleware de tenant está deshabilitado (`DEBUG=True`)

---

## 🔌 WebSockets con Daphne

### Configuración

1. **Backend usa Daphne** (no Gunicorn) para soportar ASGI y WebSockets
2. **ASGI Application** configurada en `project.asgi:application`
3. **Routing de WebSocket** en `appschedule/routing.py`
4. **Frontend se conecta directamente** al backend (no pasa por proxy)

### Flujo de Conexión WebSocket

```
Frontend (Browser)
  ↓
new WebSocket('ws://test-dominio-local.chalanpro.net:8000/ws/calendar-updates/')
  ↓
Daphne (puerto 8000)
  ↓
ProtocolTypeRouter (identifica tipo: websocket)
  ↓
AuthMiddlewareStack (autenticación)
  ↓
URLRouter (routing.websocket_urlpatterns)
  ↓
EventConsumer (consumer del WebSocket)
```

### URLs de WebSocket Disponibles

- `ws://test-dominio-local.chalanpro.net:8000/ws/calendar-updates/`
- `ws://test-dominio-local.chalanpro.net:8000/ws/schedule/event/{pk}/`
- `ws://test-dominio-local.chalanpro.net:8000/ws/schedule/event/{event_id}/chat/`
- `ws://test-dominio-local.chalanpro.net:8000/ws/schedule/unread/user/{user_id}/`

### Debugging WebSocket

Si hay problemas con WebSocket:

1. Verificar que Daphne esté corriendo:
   ```bash
   docker compose -f docker-compose.dev.yml logs backend | grep -i daphne
   ```

2. Verificar que el puerto 8000 esté abierto:
   ```bash
   docker compose -f docker-compose.dev.yml exec backend python -c "import socket; s = socket.socket(); s.connect(('localhost', 8000)); print('Puerto abierto')"
   ```

3. Verificar logs del backend:
   ```bash
   docker compose -f docker-compose.dev.yml logs backend --tail=50 | grep -E "ws|websocket|ValueError"
   ```

---

## 🔄 Flujo de Peticiones

### Peticiones HTTP (API)

```
Browser
  ↓
http://test-dominio-local.chalanpro.net:8080/api/crews/
  ↓
Vue Dev Server (puerto 8080)
  ↓
Proxy Webpack (/api → http://localhost:8000)
  ↓
Daphne (puerto 8000)
  ↓
Django (HTTP handler)
  ↓
Response
```

### Peticiones WebSocket

```
Browser
  ↓
ws://test-dominio-local.chalanpro.net:8000/ws/calendar-updates/
  ↓
Daphne (puerto 8000) - Conexión directa (NO pasa por proxy)
  ↓
ProtocolTypeRouter (identifica: websocket)
  ↓
AuthMiddlewareStack
  ↓
URLRouter
  ↓
EventConsumer
```

**Importante**: El WebSocket NO pasa por el proxy de webpack, se conecta directamente al backend.

---

## 📁 Archivos de Configuración Clave

### Backend

- `docker-compose.dev.yml`: Configuración de servicios Docker
- `app/project/asgi.py`: Configuración ASGI y WebSocket
- `app/appschedule/routing.py`: Rutas de WebSocket
- `app/project/middleware/tenant_asgi.py`: Middleware de tenant para WebSocket (solo producción)
- `envs/backend.dev.env`: Variables de entorno del backend

### Frontend

- `app/vuefrontend/vue.config.js`: Configuración del servidor de desarrollo y proxy
- `app/vuefrontend/src/main.js`: Resolución de URLs base (API y WebSocket)
- `app/vuefrontend/src/mixins/appMixin.js`: Helpers para construir URLs WebSocket

### Scripts

- `scripts/update_hosts.sh`: Actualiza `/etc/hosts` con dominios de tenant

---

## 🔍 Troubleshooting

### Problema: "Invalid Host header"

**Solución**: Verificar que `allowedHosts: 'all'` esté configurado en `vue.config.js`

### Problema: WebSocket no se conecta

**Verificaciones**:
1. ¿Daphne está corriendo? Verificar logs: `docker compose -f docker-compose.dev.yml logs backend`
2. ¿El puerto 8000 está abierto? Verificar con `ss -tuln | grep 8000`
3. ¿El dominio está en `/etc/hosts`? Verificar con `cat /etc/hosts | grep chalanpro`
4. ¿El routing está correcto? Verificar `app/appschedule/routing.py`

### Problema: "Not Found: /ws"

**Causa**: El path que llega es 'ws' en lugar de 'ws/calendar-updates/'

**Solución**: Verificar cómo se construye la URL en `buildWsUrl()` y que el path sea correcto

### Problema: API retorna 404

**Verificaciones**:
1. ¿El proxy está configurado correctamente en `vue.config.js`?
2. ¿El `baseURL` de Axios es `'/'` en desarrollo local?
3. ¿El backend está corriendo en el puerto 8000?

### Problema: Tenant no se identifica correctamente

**Verificaciones**:
1. ¿El dominio está en `/etc/hosts`?
2. ¿El header `Host` se está preservando en el proxy? Verificar `onProxyReq` en `vue.config.js`
3. ¿El dominio está en `ALLOWED_HOSTS` en `backend.dev.env`?

### Problema: Cambios en el código no se reflejan

**Solución**: 
- Backend: El volumen está montado, los cambios deberían reflejarse automáticamente
- Frontend: Si usas `npm run serve`, tiene hot-reload automático

---

## 🚀 Comandos Útiles

### Iniciar Servicios

```bash
# Backend y PostgreSQL
cd /home/oliver/shared/projects/chalanpro
docker compose -f docker-compose.dev.yml up -d postgres backend

# Frontend (en otra terminal)
cd /home/oliver/shared/projects/chalanpro/app/vuefrontend
npm run serve
```

### Ver Logs

```bash
# Backend
docker compose -f docker-compose.dev.yml logs -f backend

# Todos los servicios
docker compose -f docker-compose.dev.yml logs -f
```

### Reiniciar Servicios

```bash
# Backend
docker compose -f docker-compose.dev.yml restart backend

# Todos los servicios
docker compose -f docker-compose.dev.yml restart
```

### Actualizar Dominios en /etc/hosts

```bash
sudo ./scripts/update_hosts.sh
```

### Verificar Estado de Servicios

```bash
docker compose -f docker-compose.dev.yml ps
```

---

## 💾 Backups

### Backup del Sistema (Código y Archivos)

Crea un backup comprimido del proyecto completo, excluyendo directorios innecesarios como `node_modules`, `.git`, `__pycache__`, etc.

#### Comando

```bash
cd /home/oliver/shared/projects
tar --exclude='chalanpro/app/vuefrontend/node_modules' \
    --exclude='chalanpro/*/node_modules' \
    --exclude='chalanpro/.git' \
    --exclude='chalanpro/*/__pycache__' \
    --exclude='chalanpro/*/*/__pycache__' \
    --exclude='chalanpro/*.pyc' \
    --exclude='chalanpro/postgres_data' \
    --exclude='chalanpro/*/dist' \
    -czf /home/oliver/shared/projects/backups/chalan_onboarding_local_$(date +%m-%d-%Y).tar.gz chalanpro
```

#### Ejecución

```bash
# Asegurarse de que el directorio de backups existe y tiene permisos correctos
mkdir -p /home/oliver/shared/projects/backups
sudo chown oliver:oliver /home/oliver/shared/projects/backups
sudo chmod 755 /home/oliver/shared/projects/backups

# Ejecutar el backup
cd /home/oliver/shared/projects
tar --exclude='chalanpro/app/vuefrontend/node_modules' \
    --exclude='chalanpro/*/node_modules' \
    --exclude='chalanpro/.git' \
    --exclude='chalanpro/*/__pycache__' \
    --exclude='chalanpro/*/*/__pycache__' \
    --exclude='chalanpro/*.pyc' \
    --exclude='chalanpro/postgres_data' \
    --exclude='chalanpro/*/dist' \
    -czf /home/oliver/shared/projects/backups/chalan_onboarding_local_$(date +%m-%d-%Y).tar.gz chalanpro
```

#### Directorios Excluidos

- `node_modules`: Dependencias de Node.js (se pueden reinstalar con `npm install`)
- `.git`: Repositorio Git (se puede clonar nuevamente)
- `__pycache__`: Caché de Python (se regenera automáticamente)
- `*.pyc`: Archivos compilados de Python (se regeneran automáticamente)
- `postgres_data`: Datos de PostgreSQL (se hace backup por separado)
- `dist`: Archivos compilados del frontend (se pueden regenerar)

#### Verificar Backup Creado

```bash
ls -lh /home/oliver/shared/projects/backups/chalan_onboarding_local_*.tar.gz
```

### Backup de la Base de Datos

Crea un dump SQL de la base de datos PostgreSQL.

#### Comando

```bash
cd /home/oliver/shared/projects/chalanpro
docker compose -f docker-compose.dev.yml exec -T postgres pg_dump -U chalanpro_user chalanpro > /home/oliver/shared/projects/backups/chalan_onboarding_local_db_$(date +%m-%d-%Y).sql
```

#### Ejecución

```bash
# Asegurarse de que el directorio de backups existe
mkdir -p /home/oliver/shared/projects/backups

# Ejecutar el backup de la base de datos
cd /home/oliver/shared/projects/chalanpro
docker compose -f docker-compose.dev.yml exec -T postgres pg_dump -U chalanpro_user chalanpro > /home/oliver/shared/projects/backups/chalan_onboarding_local_db_$(date +%m-%d-%Y).sql
```

#### Verificar Backup Creado

```bash
ls -lh /home/oliver/shared/projects/backups/chalan_onboarding_local_db_*.sql
```

#### Restaurar Base de Datos desde Backup

```bash
# Detener el servicio backend si está corriendo
cd /home/oliver/shared/projects/chalanpro
docker compose -f docker-compose.dev.yml stop backend

# Restaurar el backup
docker compose -f docker-compose.dev.yml exec -T postgres psql -U chalanpro_user chalanpro < /home/oliver/shared/projects/backups/chalan_onboarding_local_db_MM-DD-YYYY.sql

# Reiniciar el servicio backend
docker compose -f docker-compose.dev.yml start backend
```

### Backup Completo (Sistema + Base de Datos)

Para hacer un backup completo del sistema y la base de datos en un solo paso:

```bash
#!/bin/bash
# Script para backup completo

BACKUP_DIR="/home/oliver/shared/projects/backups"
DATE=$(date +%m-%d-%Y)
PROJECT_DIR="/home/oliver/shared/projects/chalanpro"

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

# Backup del sistema
echo "Creando backup del sistema..."
cd /home/oliver/shared/projects
tar --exclude='chalanpro/app/vuefrontend/node_modules' \
    --exclude='chalanpro/*/node_modules' \
    --exclude='chalanpro/.git' \
    --exclude='chalanpro/*/__pycache__' \
    --exclude='chalanpro/*/*/__pycache__' \
    --exclude='chalanpro/*.pyc' \
    --exclude='chalanpro/postgres_data' \
    --exclude='chalanpro/*/dist' \
    -czf $BACKUP_DIR/chalan_onboarding_local_$DATE.tar.gz chalanpro

# Backup de la base de datos
echo "Creando backup de la base de datos..."
cd $PROJECT_DIR
docker compose -f docker-compose.dev.yml exec -T postgres pg_dump -U chalanpro_user chalanpro > $BACKUP_DIR/chalan_onboarding_local_db_$DATE.sql

echo "✓ Backups completados:"
ls -lh $BACKUP_DIR/chalan_onboarding_local_*$DATE*
```

**Guardar como**: `scripts/backup_completo.sh`

**Ejecutar**:
```bash
chmod +x scripts/backup_completo.sh
./scripts/backup_completo.sh
```

---

## 🔄 Flujo de Trabajo Git

### Objetivo

Mantener `main` local siempre sincronizado con `main` remoto, trabajar en `dev_local`, y actualizar producción de forma controlada.

### Flujo Completo

```
1. main local = main remoto (siempre sincronizados)
   ↓
2. Programar en dev_local (commits pequeños y frecuentes)
   ↓
3. Pasar cambios de dev_local → main local (merge)
   ↓
4. Pasar cambios de main local → main remoto (GitHub) (push)
   ↓
5. Pasar cambios de main remoto → main del VPS (Hostinger - Producción) (pull)
```

### Pasos Detallados

#### 1. Sincronizar main local con main remoto

**Antes de empezar a trabajar, siempre sincronizar:**

```bash
# Opción A: Usar el script (recomendado)
./scripts/sync_main_with_remote.sh

# Opción B: Manualmente
git checkout main
git fetch origin main
git reset --hard origin/main
```

**Script disponible**: `scripts/sync_main_with_remote.sh`

#### 2. Trabajar en dev_local

```bash
# Cambiar a dev_local
git checkout dev_local

# Hacer cambios, commits pequeños y frecuentes
# ... editar archivos ...
git add .
git commit -m "Descripción clara del cambio"
```

#### 3. Pasar cambios de dev_local a main local

```bash
# Cambiar a main
git checkout main

# Asegurarse de que main está actualizado con remoto
./scripts/sync_main_with_remote.sh  # o manualmente

# Fusionar dev_local en main
git merge dev_local

# O si prefieres un merge con mensaje:
git merge --no-ff dev_local -m "Merge dev_local: descripción de cambios"
```

**¿Qué hace `git merge dev_local`?**
- Fusiona **solo los commits** que están en `dev_local` y **NO están en `main`**
- No copia todo el contenido, solo aplica los cambios (diffs) de los commits nuevos según `git status`
- Si hay conflictos, Git te avisará y tendrás que resolverlos manualmente
- Para ver qué commits se van a fusionar antes de hacer merge: `git log main..dev_local --oneline`

#### 4. Pasar cambios de main local a main remoto (GitHub)

```bash
# Ya estás en main (del paso anterior)
git push origin main
```

#### 5. Pasar cambios de main remoto a main del VPS (Hostinger - Producción)

**En el servidor VPS de Hostinger:**

```bash
# Conectarse al VPS
ssh usuario@hostinger-vps

# Ir al directorio del proyecto
cd /ruta/al/proyecto/chalanpro

# Actualizar desde el remoto
git fetch origin main
git checkout main
git pull origin main  # o git reset --hard origin/main para forzar sincronización

# Reiniciar servicios si es necesario
docker compose restart  # o el comando que uses en producción
```

### Comandos Rápidos

```bash
# Sincronizar main local con remoto
./scripts/sync_main_with_remote.sh

# Ver estado de las ramas
git branch -vv

# Ver diferencias entre ramas
git log main..dev_local --oneline  # Ver commits en dev_local que no están en main
git log dev_local..main --oneline   # Ver commits en main que no están en dev_local

# Ver historial gráfico
git log --oneline --graph --all --decorate -10
```

### Revertir Cambios (Si algo se rompe)

Si algo sale mal y necesitas restablecer el estado anterior:

#### Revertir main local

```bash
# Si aún no has hecho push al remoto, puedes resetear main local
git checkout main
git reset --hard origin/main  # Restaura main local al estado del remoto

# O si quieres volver a un commit específico:
git reset --hard <commit-hash>  # Reemplaza <commit-hash> con el hash del commit deseado
```

#### Revertir main remoto (GitHub)

```bash
# Si ya hiciste push pero quieres revertir el último commit en el remoto:
git checkout main
git revert HEAD  # Crea un commit que revierte los cambios
git push origin main

# O si quieres eliminar completamente el último commit (⚠️ CUIDADO):
git reset --hard HEAD~1  # Elimina el último commit localmente
git push origin main --force  # ⚠️ FORCE PUSH - solo si estás seguro
```

#### Revertir main del VPS (Hostinger - Producción)

**En el servidor VPS:**

```bash
# Conectarse al VPS
ssh usuario@hostinger-vps
cd /ruta/al/proyecto/chalanpro

# Opción 1: Volver al estado del remoto (recomendado)
git fetch origin main
git checkout main
git reset --hard origin/main

# Opción 2: Volver a un commit específico
git reset --hard <commit-hash>

# Opción 3: Revertir el último commit (mantiene historial)
git revert HEAD
git push origin main  # Si tienes permisos de push desde VPS

# Después de revertir, reiniciar servicios
docker compose restart  # o el comando que uses
```

#### Ver Historial de Commits (Para encontrar el commit al que volver)

```bash
# Ver historial completo
git log --oneline -20

# Ver historial con fechas
git log --oneline --date=short --format="%h %ad %s" -20

# Ver diferencias entre commits
git diff <commit-hash-1>..<commit-hash-2>
```

### Recomendaciones

1. **Siempre sincronizar main antes de empezar a trabajar**: Usa `./scripts/sync_main_with_remote.sh`
2. **Commits pequeños y frecuentes**: Facilita el debugging y el rollback si es necesario
3. **Verificar antes de mergear**: Asegúrate de que main esté actualizado antes de hacer merge
4. **En producción (VPS)**: Siempre hacer `git pull` o `git reset --hard origin/main` para estar seguro
5. **Antes de hacer push importante**: Considera crear un tag para poder volver fácilmente: `git tag -a v1.0.0 -m "Versión estable antes de cambios"`

¿git merge dev_local copia todo dev_local a main o solo los cambios según git status?
Solo los cambios (diffs) de los commits nuevos
No copia todo el contenido
Aplica únicamente las diferencias entre main y dev_local
Es equivalente a aplicar los cambios que muestra git status entre las dos rama

### Scripts Disponibles

- `scripts/sync_main_with_remote.sh`: Sincroniza main local con main remoto
- `scripts/backup_completo.sh`: Crea backup completo del sistema y base de datos

---

## 📝 Notas Importantes

1. **Daphne vs Gunicorn**: En desarrollo local, siempre usar Daphne para soportar WebSockets. Gunicorn solo soporta WSGI (HTTP), no ASGI (WebSocket).

2. **Proxy de Webpack**: Las peticiones HTTP pasan por el proxy, pero los WebSockets se conectan directamente al backend.

3. **Multi-Tenant en Desarrollo**: En desarrollo local (`DEBUG=True`), el middleware de tenant está deshabilitado para facilitar debugging. En producción, se habilita automáticamente.

4. **Hostname en WebSocket**: El WebSocket debe usar el hostname completo del tenant (ej: `test-dominio-local.chalanpro.net`) para que `django-tenants` lo identifique correctamente.

5. **Puertos**: 
   - Frontend: 8080 (npm run serve)
   - Backend: 8000 (Daphne)
   - PostgreSQL: 5432

6. **Hot Reload**: 
   - Frontend: Automático con `npm run serve`
   - Backend: Los cambios se reflejan automáticamente porque el código está montado como volumen

---

## 🔗 Referencias

- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Daphne Documentation](https://github.com/django/daphne)
- [Vue CLI DevServer Proxy](https://cli.vuejs.org/config/#devserver-proxy)
- [django-tenants Documentation](https://django-tenants.readthedocs.io/)

---

**Última actualización**: Diciembre 2024
**Servidor**: ubuntu-house (192.168.0.105)
**Entorno**: Desarrollo Local

