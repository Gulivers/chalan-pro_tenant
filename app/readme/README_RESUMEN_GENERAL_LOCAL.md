# Configuración del Servidor Local de Desarrollo (ubuntu-house)

Este documento describe la configuración completa del servidor local de desarrollo para **JobRhythm** (repo técnico Chalan-Pro) en ubuntu-house.

## Sincronizar `main` desde remoto (JobRhythm) — ¿rompe el entorno local?

**Respuesta corta: no debería romper el stack local** si sigues usando `docker-compose.dev.yml` (no el de producción del VPS).

| Qué cambió en `main` | Impacto en ubuntu-house |
|----------------------|-------------------------|
| Marca JobRhythm (Vue, landing, textos) | Solo código; tras `git pull` y rebuild frontend/local `npm run serve` verás el nombre nuevo. |
| `nginx/legacy-redirects.conf` + `docker-compose.yml` prod | **No aplica** en local si no levantas el compose de producción. |
| `envs/backend.dev.example.env` | Plantilla actualizada; tu `envs/backend.dev.env` **no está en Git** — no se sobrescribe sola. |
| `TENANT_BASE_DOMAIN` por defecto `jobrhythm.net` en código | Afecta **nuevos** tenants si el `.env` local no define otra cosa. |

**Pasos recomendados tras `git pull origin main` en ubuntu-house:**

1. Actualizar plantilla y revisar tu env local (no reemplazar a ciegas si tienes datos de prueba):
   ```bash
   diff envs/backend.dev.example.env envs/backend.dev.env   # fusionar a mano
   ```
   Valores típicos de desarrollo:
   - `TENANT_BASE_DOMAIN=jobrhythm.net`
   - `ALLOWED_HOSTS` con `*.jobrhythm.net`, `jobrhythm.net`, `api.jobrhythm.net` (puedes **mantener** `*.chalanpro.net` en paralelo)
   - `FRONT_URL=http://192.168.0.105:8080` o `http://jobrhythm.net:8080`

2. Recrear backend para cargar env (igual que en VPS):
   ```bash
   docker compose -f docker-compose.dev.yml up -d --force-recreate backend
   ```

3. Actualizar `/etc/hosts` (solo ubuntu-house):
   ```bash
   sudo ./scripts/update_hosts.sh
   ```
   Acceso ejemplo: `http://test-dominio-local.jobrhythm.net:8080`

4. Tenants existentes en BD local con dominio `*.chalanpro.net` o `*.jobrithm.net` siguen funcionando por hostname; opcional: migrar dominios como en producción (`migrate_domains_to_jobrithm.py` con `--old-base` / `--new-base`).

5. Landing local (opcional): `cd landing && npm run build` — dominios reales de marketing no son necesarios en LAN.

**Producción (VPS):** despliegue desde rama `main` con `docker-compose.yml` y `scripts/deploy-vps.sh`.

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

Ver plantilla actual en `envs/backend.dev.example.env` (JobRhythm + compatibilidad `chalanpro.net` / `jobrithm.net`).

Ejemplo mínimo (copiar a `envs/backend.dev.env` y ajustar IP):

```bash
DEBUG=True
ALLOWED_HOSTS="192.168.0.105,192.168.0.248,localhost,127.0.0.1,api.jobrhythm.net,jobrhythm.net,*.jobrhythm.net,api.chalanpro.net,chalanpro.net,*.chalanpro.net,test-dominio-local.jobrhythm.net"
TENANT_BASE_DOMAIN=jobrhythm.net
FRONT_URL=http://192.168.0.105:8080
CSRF_TRUSTED_ORIGINS=http://192.168.0.105,http://192.168.0.105:8080,http://*.jobrhythm.net,http://*.jobrhythm.net:8080,http://*.chalanpro.net,http://*.chalanpro.net:8080
CORS_ALLOW_ALL_ORIGINS=True
```

**Puntos clave**:
- `DEBUG=True`: Habilita modo desarrollo y simplifica el stack de WebSocket
- `ALLOWED_HOSTS`: Incluye la IP local y dominios de tenant (`jobrhythm.net` recomendado; legacy opcional)
- `TENANT_BASE_DOMAIN`: Dominio base para **nuevos** tenants en onboarding local
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

### Credenciales de PostgreSQL

Para conectarte a PostgreSQL desde el host local o desde herramientas externas (como DBeaver, pgAdmin, etc.):

**Conexión desde el host (fuera de Docker)**:
```
Host: localhost (o 127.0.0.1)
Puerto: 5432
Base de datos: chalanpro
Usuario: chalanpro_user
Contraseña: 2hSGqPHiNhaktRS_lxY3CprmDBYtHJxsIxWZhe-iqd4
```

**Conexión desde dentro de Docker (desde el contenedor backend)**:
```
Host: postgres (nombre del servicio en docker-compose)
Puerto: 5432
Base de datos: chalanpro
Usuario: chalanpro_user
Contraseña: 2hSGqPHiNhaktRS_lxY3CprmDBYtHJxsIxWZhe-iqd4
```

**String de conexión (Connection String)**:
```
postgres://chalanpro_user:2hSGqPHiNhaktRS_lxY3CprmDBYtHJxsIxWZhe-iqd4@localhost:5432/chalanpro
```

**Ejemplos de conexión**:

1. **Desde la línea de comandos (psql)**:
```bash
# Desde el host
psql -h localhost -p 5432 -U chalanpro_user -d chalanpro

# Desde dentro del contenedor de postgres
docker compose -f docker-compose.dev.yml exec postgres psql -U chalanpro_user -d chalanpro
```

2. **Desde Python (psycopg2)**:
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="chalanpro",
    user="chalanpro_user",
    password="2hSGqPHiNhaktRS_lxY3CprmDBYtHJxsIxWZhe-iqd4"
)
```

3. **Desde Django (settings.py)**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'chalanpro',
        'USER': 'chalanpro_user',
        'PASSWORD': '2hSGqPHiNhaktRS_lxY3CprmDBYtHJxsIxWZhe-iqd4',
        'HOST': 'postgres',  # Desde dentro de Docker
        # 'HOST': 'localhost',  # Desde el host
        'PORT': '5432',
    }
}
```

**Nota**: Las credenciales están definidas en `envs/postgres.env` y `envs/backend.dev.env`.

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

### Admin Django (schema `public` — Tenants, Billing)

El admin de **Planes / Suscripciones / appbilling** y **Tenants** no usa el subdominio del tenant de prueba. Usa el dominio **API** en el **puerto 8000** (backend), no el 8080 del frontend:

| URL | Uso |
|-----|-----|
| `http://api.chalanpro.net:8000/admin/` | Admin global (legacy chalanpro en hosts) |
| `http://api.jobrhythm.net:8000/admin/` | Admin global (recomendado con marca JobRhythm) |

Si el navegador no abre o devuelve error 500, en la base local suele faltar el registro del tenant `public`:

```bash
docker compose -f docker-compose.dev.yml exec backend python manage.py setup_public_domains
docker compose -f docker-compose.dev.yml restart backend
```

`setup_public_domains` crea el tenant `public` si no existe y registra `api.jobrhythm.net`, `api.chalanpro.net`, etc. en `tenants_domain`.

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
docker compose -f docker-compose.dev.yml logs --tail=50 backend

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

### Migraciones de Base de Datos

Para crear y ejecutar migraciones de Django dentro del contenedor de Docker:

#### Crear Migraciones

```bash
# Crear migraciones para todos los cambios detectados en los modelos
docker compose -f docker-compose.dev.yml exec backend python manage.py makemigrations

# Crear migraciones para una app específica
docker compose -f docker-compose.dev.yml exec backend python manage.py makemigrations appschedule
```

#### Ejecutar Migraciones

```bash
# Aplicar todas las migraciones pendientes
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate

# Aplicar migraciones para una app específica
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate appschedule
```

#### Ver Estado de las Migraciones

```bash
# Ver qué migraciones están aplicadas y cuáles faltan
docker compose -f docker-compose.dev.yml exec backend python manage.py showmigrations
```

#### Comandos Útiles Adicionales

```bash
# Crear una migración vacía (para migraciones de datos personalizadas)
docker compose -f docker-compose.dev.yml exec backend python manage.py makemigrations --empty appschedule

# Verificar si hay migraciones pendientes sin aplicarlas
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate --plan

# Revertir la última migración (cuidado: puede afectar datos)
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate appschedule <nombre_app> <numero_migracion_anterior>
```

**Nota importante**: Asegúrate de que el contenedor `backend` esté ejecutándose antes de ejecutar los comandos de migración. Si el contenedor no está corriendo, puedes iniciarlo primero:

```bash
docker compose -f docker-compose.dev.yml up -d backend
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

