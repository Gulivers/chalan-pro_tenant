# Chalan-Pro - Documentación General del Sistema

## 📑 Índice

- [📋 Resumen Ejecutivo](#-resumen-ejecutivo)
- [1. Arquitectura del Servidor](#1-arquitectura-del-servidor)
  - [1.1 Diagrama de Contenedores y Servicios](#11-diagrama-de-contenedores-y-servicios)
  - [1.2 Descripción de Servicios](#12-descripción-de-servicios)
  - [1.3 Flujo de Peticiones](#13-flujo-de-peticiones)
- [2. Estructura General del Proyecto](#2-estructura-general-del-proyecto)
  - [2.1 Diagrama de Estructura de Archivos](#21-diagrama-de-estructura-de-archivos)
  - [2.2 Descripción de Archivos Clave](#22-descripción-de-archivos-clave)
    - [Backend (Django)](#backend-django)
    - [Frontend (Vue.js)](#frontend-vuejs)
    - [Infraestructura](#infraestructura)
- [2.1 Flujo del Proceso de Creación de Tenant](#21-flujo-del-proceso-de-creación-de-tenant)
  - [2.1.1 Diagrama de Flujo](#211-diagrama-de-flujo)
  - [2.1.2 Puntos Clave del Flujo](#212-puntos-clave-del-flujo)
- [2.2 Configuraciones para Dominio, Tenant y DNS](#22-configuraciones-para-dominio-tenant-y-dns)
  - [2.2.1 Configuración de DNS en Hostinger](#221-configuración-de-dns-en-hostinger)
  - [2.2.2 Configuración de Certificados SSL](#222-configuración-de-certificados-ssl)
  - [2.2.3 Configuración de Tenant en Django](#223-configuración-de-tenant-en-django)
  - [2.2.4 Estructura de Dominios en Base de Datos](#224-estructura-de-dominios-en-base-de-datos)
- [3. Comandos Rápidos - PostgreSQL en Docker](#3-comandos-rápidos---postgresql-en-docker)
  - [3.1 Conexión a PostgreSQL](#31-conexión-a-postgresql)
  - [3.2 Consultas Útiles](#32-consultas-útiles)
  - [3.3 Backup y Restauración](#33-backup-y-restauración)
  - [3.4 Gestión de Tenants](#34-gestión-de-tenants)
- [4. Cómo Desplegar Cambios](#4-cómo-desplegar-cambios)
  - [4.1 Desplegar Cambios en el Backend](#41-desplegar-cambios-en-el-backend)
  - [4.2 Desplegar Cambios en el Frontend](#42-desplegar-cambios-en-el-frontend)
  - [4.3 Desplegar Cambios en Ambos (Backend + Frontend)](#43-desplegar-cambios-en-ambos-backend--frontend)
- [4.1 Estructura de Branches de Git](#41-estructura-de-branches-de-git)
  - [4.1.1 Branches Actuales](#411-branches-actuales)
  - [4.1.2 Actualizar Branch Main con Últimos Cambios](#412-actualizar-branch-main-con-últimos-cambios)
  - [4.1.3 Verificar Estado del Repositorio](#413-verificar-estado-del-repositorio)
  - [4.1.4 Workflow Recomendado](#414-workflow-recomendado)
- [5. Host y Credenciales PostgreSQL](#5-host-y-credenciales-postgresql)
  - [5.1 Información de Conexión](#51-información-de-conexión)
  - [5.2 Conexión desde el Servidor](#52-conexión-desde-el-servidor)
  - [5.3 Conexión Externa (desde otra máquina)](#53-conexión-externa-desde-otra-máquina)
  - [5.4 Conexión desde pgAdmin](#54-conexión-desde-pgadmin)
- [6. Seguridad del Servidor](#6-seguridad-del-servidor)
  - [6.1 Estado Actual de Seguridad](#61-estado-actual-de-seguridad)
  - [6.2 Mejoras Recomendadas](#62-mejoras-recomendadas)
    - [🔴 Prioridad Alta](#-prioridad-alta)
    - [🟡 Prioridad Media](#-prioridad-media)
    - [🟢 Prioridad Baja](#-prioridad-baja)
  - [6.3 Configuración Actual de Headers de Seguridad](#63-configuración-actual-de-headers-de-seguridad)
  - [6.4 Checklist de Seguridad](#64-checklist-de-seguridad)
- [7. URLs del Sistema](#7-urls-del-sistema)
  - [7.1 URLs de Producción](#71-urls-de-producción)
  - [7.2 Credenciales de Acceso](#72-credenciales-de-acceso)
- [8. Comandos Útiles Adicionales](#8-comandos-útiles-adicionales)
  - [8.1 Gestión de Contenedores](#81-gestión-de-contenedores)
  - [8.2 Django Management](#82-django-management)
  - [8.3 Certificados SSL](#83-certificados-ssl)
- [9. Inventory Master Data Setup](#9-inventory-master-data-setup)
  - [9.1 Resumen de la Implementación](#91-resumen-de-la-implementación)
  - [9.2 Componentes del Sistema](#92-componentes-del-sistema)
  - [9.3 Flujo de Uso](#93-flujo-de-uso)
  - [9.4 Comandos de Gestión](#94-comandos-de-gestión)
  - [9.5 Generar el Fixture JSON de Datos Maestros](#95-generar-el-fixture-json-de-datos-maestros)
- [10. Troubleshooting](#10-troubleshooting)
  - [9.1 El Frontend No Carga](#91-el-frontend-no-carga)
  - [9.2 El Backend No Responde](#92-el-backend-no-responde)
  - [9.3 Problemas con Multi-Tenant](#93-problemas-con-multi-tenant)
  - [9.4 Certificados SSL No Se Generan](#94-certificados-ssl-no-se-generan)
  - [9.5 Errores 502 Bad Gateway](#95-errores-502-bad-gateway)
  - [9.6 Problemas con WebSocket](#96-problemas-con-websocket)
- [10.5 Errores 502 Bad Gateway](#105-errores-502-bad-gateway)
- [10.6 Problemas con WebSocket](#106-problemas-con-websocket)
- [11. Contacto y Soporte](#11-contacto-y-soporte)

---

## 📋 Resumen Ejecutivo

Sistema multi-tenant Django con frontend Vue.js desplegado en VPS Hostinger con Ubuntu 24.04 LTS. La plataforma permite la creación dinámica de tenants mediante un proceso de onboarding, donde cada tenant obtiene su propio subdominio y schema de base de datos aislado.

**IP del Servidor:** `72.60.168.62`  
**Dominio Base:** `chalanpro.net`  
**Repositorio Git:** `https://github.com/Gulivers/chalan-pro_tenant.git`

---

## 1. Arquitectura del Servidor

### 1.1 Diagrama de Contenedores y Servicios

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERNET                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐        ┌─────▼─────┐      ┌─────▼─────┐
   │  DNS    │        │   DNS     │      │   DNS     │
   │  @      │        │   api     │      │   *.      │
   │chalanpro│        │chalanpro  │      │chalanpro  │
   │  .net   │        │  .net     │      │  .net     │
   └────┬────┘        └─────┬─────┘      └─────┬─────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │   NGINX        │
                    │  (Puerto 80/443)│
                    │  Reverse Proxy │
                    │  SSL/TLS       │
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐        ┌─────▼─────┐      ┌─────▼─────┐
   │ Frontend│        │  Backend  │      │ PostgreSQL│
   │ Vue.js  │        │  Django   │      │    15     │
   │         │        │ Daphne    │      │           │
   │  Build  │        │ (ASGI)    │      │  :5432    │
   │  Static │        │  :8000    │      │           │
   │         │        │ WebSocket │      │           │
   └─────────┘        └─────┬─────┘      └─────┬─────┘
                            │                   │
                            │                   │
                    ┌───────▼───────────────────▼───────┐
                    │      Docker Network               │
                    │    (chalanpro_network)            │
                    └───────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   pgAdmin      │
                    │   (Puerto 5050)│
                    │   Web UI       │
                    └────────────────┘
```

### 1.2 Descripción de Servicios

| Servicio       | Contenedor           | Puerto         | Descripción                                                   |
| -------------- | -------------------- | -------------- | ------------------------------------------------------------- |
| **Nginx**      | `chalanpro_nginx`    | 80, 443        | Reverse proxy, SSL/TLS termination, enrutamiento de requests  |
| **Backend**    | `chalanpro_backend`  | 8000 (interno) | API Django REST + Admin, Daphne (ASGI) para soporte WebSocket |
| **Frontend**   | `chalanpro_frontend` | -              | Build de Vue.js, archivos estáticos servidos por Nginx        |
| **PostgreSQL** | `chalanpro_postgres` | 5432           | Base de datos multi-tenant con schemas aislados               |
| **pgAdmin**    | `chalanpro_pgadmin`  | 5050           | Interfaz web para administración de PostgreSQL                |

### 1.3 Flujo de Peticiones

1. **Frontend (chalanpro.net, www.chalanpro.net):**
   - Cliente → Nginx (443) → Archivos estáticos Vue.js
   - `/api/*` → Nginx → Backend (8000)

2. **API/Admin (api.chalanpro.net):**
   - Cliente → Nginx (443) → Backend (8000)
   - Rutas: `/api/*`, `/admin/*`

3. **Tenants (\*.chalanpro.net):**
   - Cliente → Nginx (443) → Archivos estáticos Vue.js
   - `/api/*` → Nginx → Backend (8000) → Middleware detecta tenant → Schema específico

4. **WebSocket (Actualizaciones en tiempo real):**
   - Cliente → Nginx (443) → `/ws/*` → Backend Daphne (8000)
   - Middleware `TenantASGIMiddleware` identifica tenant desde hostname
   - Configura schema del tenant → Conexión WebSocket establecida
   - Rutas WebSocket:
     - `/ws/calendar-updates/` - Actualizaciones del calendario
     - `/ws/schedule/event/{id}/` - Notas de eventos
     - `/ws/schedule/event/{id}/chat/` - Chat de eventos
     - `/ws/schedule/unread/user/{id}/` - Notificaciones no leídas

---

## 2. Estructura General del Proyecto

### 2.1 Diagrama de Estructura de Archivos

```
/opt/chalanpro/
│
├── .git/                                  # Repositorio Git (movido a la raíz - Diciembre 2024)
│
├── app/                                    # Código de la aplicación (subdirectorio)
│   ├── manage.py                          # Script de gestión de Django
│   ├── requirements.txt                   # Dependencias Python del backend
│   ├── Dockerfile.backend                 # Imagen Docker para backend Django
│   │
│   ├── project/                           # Configuración principal de Django
│   │   ├── settings.py                    # Configuración Django (ALLOWED_HOSTS, CSRF, etc.)
│   │   ├── urls.py                        # URLs principales (tenant-specific)
│   │   ├── urls_public.py                 # URLs para schema público (onboarding, admin global)
│   │   ├── wsgi.py                        # WSGI application (legacy, no usado)
│   │   ├── asgi.py                        # ASGI application para Daphne (WebSocket)
│   │   │
│   │   └── middleware/                    # Middlewares personalizados
│   │       ├── tenant_hostname.py         # Normaliza hostname (remueve puerto)
│   │       ├── dynamic_allowed_hosts.py   # Actualiza ALLOWED_HOSTS dinámicamente
│   │       ├── dynamic_csrf.py            # Actualiza CSRF_TRUSTED_ORIGINS dinámicamente
│   │       └── tenant_asgi.py             # Middleware ASGI para identificar tenant en WebSocket
│   │
│   ├── tenants/                           # App de gestión multi-tenant
│   │   ├── models.py                      # Modelos Tenant y Domain
│   │   ├── views.py                       # Vista create_tenant_onboarding()
│   │   ├── urls.py                        # Rutas de onboarding
│   │   ├── apps.py                        # TenantsConfig.ready() - carga dominios al inicio
│   │   └── management/                    # Comandos de gestión
│   │       └── commands/
│   │           ├── create_tenant.py       # Crear tenant manualmente
│   │           └── list_tenants.py        # Listar tenants
│   │
│   ├── vuefrontend/                       # Frontend Vue.js
│   │   ├── src/
│   │   │   ├── router/                    # Vue Router (rutas públicas/privadas)
│   │   │   ├── components/                # Componentes Vue
│   │   │   │   └── layout/
│   │   │   │       ├── NavbarComponent.vue
│   │   │   │       └── NavbarMessagesDropdown.vue
│   │   │   ├── views/                     # Vistas (OnboardingView, LoginView, etc.)
│   │   │   ├── stores/                    # Pinia stores (auth, chat)
│   │   │   └── utils/
│   │   │       └── axiosConfig.js         # Interceptor Axios (manejo de 401, CSRF)
│   │   ├── dist/                          # Build de producción (generado)
│   │   └── Dockerfile.frontend            # Imagen Docker para build del frontend
│   │
│   ├── appinventory/                      # App de inventario
│   ├── appschedule/                       # App de programación
│   ├── apptransactions/                   # App de transacciones
│   ├── ctrctsapp/                         # App de contratos
│   ├── crewsapp/                          # App de equipos
│   └── auditapp/                          # App de auditoría
│
├── envs/                                  # Variables de entorno
│   ├── backend.env                        # Configuración Django (DEBUG, SECRET_KEY, ALLOWED_HOSTS, etc.)
│   ├── postgres.env                       # Credenciales PostgreSQL
│   └── pgadmin.env                        # Credenciales pgAdmin
│
├── nginx/                                 # Configuración Nginx
│   └── default.conf                       # Configuración de servidores virtuales (HTTP/HTTPS)
│
├── postgres_data/                         # Datos persistentes de PostgreSQL (volumen Docker)
│
├── certbot/                               # Certificados SSL (Let's Encrypt)
│
├── docker-compose.yml                     # Orquestación de contenedores Docker (producción)
│
├── .gitignore                             # Reglas de Git (excluye .env, postgres_data, etc.)
│
├── setup.sh                               # Script de inicialización del sistema
├── init-certbot.sh                        # Script para certificados SSL (dominio principal)
├── init-certbot-api.sh                    # Script para certificados SSL (api.chalanpro.net)
├── init-certbot-wildcard.sh               # Script para certificado SSL wildcard (*.chalanpro.net)
└── enable-https.sh                        # Script para habilitar HTTPS en Nginx
```

**Nota importante sobre la estructura del repositorio:**

- El repositorio Git (`.git/`) está ubicado en la raíz `/opt/chalanpro/` (desde Diciembre 2024)
- Esto permite incluir toda la configuración de infraestructura (Docker, Nginx, scripts) en el repositorio
- El código de la aplicación está en el subdirectorio `app/`
- Cualquier desarrollador que clone el repo tendrá todo lo necesario para levantar el stack completo

### 2.2 Descripción de Archivos Clave

#### Backend (Django)

- **`project/settings.py`**: Configuración central de Django. Define `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `TENANT_BASE_DOMAIN`, middlewares, y configuración de base de datos multi-tenant.

- **`project/middleware/tenant_hostname.py`**: Normaliza el hostname removiendo el puerto antes de que django-tenants lo procese. Ejemplo: `tenant.chalanpro.net:8000` → `tenant.chalanpro.net`.

- **`project/middleware/dynamic_allowed_hosts.py`**: Actualiza `ALLOWED_HOSTS` dinámicamente cada 5 minutos consultando los dominios activos de tenants en la BD. Permite que nuevos tenants sean reconocidos sin reiniciar el servidor.

- **`project/middleware/dynamic_csrf.py`**: Actualiza `CSRF_TRUSTED_ORIGINS` dinámicamente cada 5 minutos. Agrega orígenes HTTPS para todos los dominios de tenants activos.

- **`tenants/models.py`**: Define los modelos `Tenant` (schema_name, is_active, etc.) y `Domain` (domain, tenant FK). Base del sistema multi-tenant.

- **`tenants/views.py`**: Contiene `create_tenant_onboarding()` que procesa el formulario de onboarding, crea el tenant, schema, dominio, y ejecuta migraciones.

- **`tenants/apps.py`**: `TenantsConfig.ready()` se ejecuta al iniciar Django y carga todos los dominios activos en `CSRF_TRUSTED_ORIGINS` (carga inicial).

#### Frontend (Vue.js)

- **`vuefrontend/src/router/index.js`**: Configuración de rutas Vue Router. Define rutas públicas (`/onboarding`, `/login`) con `meta: { hideNavbar: true }` y rutas protegidas que requieren autenticación.

- **`vuefrontend/src/utils/axiosConfig.js`**: Interceptor de Axios que:
  - Agrega token de autenticación a las peticiones
  - Maneja errores 401 (redirige a login, excepto en rutas públicas)
  - Identifica endpoints opcionales (`/api/unread-chat-counts/`, `/api/user_detail/`) que pueden devolver 401 sin causar redirección

- **`vuefrontend/src/components/layout/NavbarComponent.vue`**: Barra de navegación principal. Se oculta en rutas con `meta.hideNavbar: true`.

- **`vuefrontend/src/components/layout/NavbarMessagesDropdown.vue`**: Componente de mensajes. Verifica si debe mostrarse antes de hacer llamadas API para evitar 401 en rutas públicas.

#### Infraestructura

- **`docker-compose.yml`**: Define los 5 servicios (postgres, backend, frontend, nginx, pgadmin), volúmenes, redes, y dependencias.

- **`nginx/default.conf`**: Configuración de Nginx con:
  - Redirección HTTP → HTTPS
  - Servidor para `chalanpro.net` (frontend)
  - Servidor para `api.chalanpro.net` (API/Admin)
  - Servidor wildcard `*.chalanpro.net` (tenants)
  - Headers de seguridad (HSTS, X-Frame-Options, etc.)
  - **Resolución DNS dinámica**: Configurado con `resolver 127.0.0.11 valid=10s` y variables `$backend_upstream` para evitar errores 502 cuando el backend cambia de IP. Esto fuerza a Nginx a re-resolver el nombre del servicio `backend` en cada petición, evitando problemas de caché DNS cuando los contenedores se reinician.

- **`envs/backend.env`**: Variables de entorno del backend:
  - `DEBUG=False`
  - `ALLOWED_HOSTS` (incluye wildcard `*.chalanpro.net`)
  - `CSRF_TRUSTED_ORIGINS` (incluye wildcard `https://*.chalanpro.net`)
  - `TENANT_BASE_DOMAIN=chalanpro.net`

---

## 2.1 Flujo del Proceso de Creación de Tenant

### 2.1.1 Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USUARIO ACCEDE A ONBOARDING                                  │
│    URL: https://www.chalanpro.net/onboarding                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. FRONTEND (Vue.js)                                            │
│    - Router detecta ruta pública (/onboarding)                  │
│    - Navbar se oculta (meta.hideNavbar: true)                   │
│    - Usuario completa formulario (nombre, email, etc.)          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. PETICIÓN HTTP POST                                           │
│    POST /api/onboarding/                                        │
│    Body: { name, email, ... }                                   │
│    Host: www.chalanpro.net                                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. NGINX                                                        │
│    - Recibe petición en puerto 443                              │
│    - Proxy a backend:8000                                       │
│    - Pasa header Host: www.chalanpro.net                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. MIDDLEWARE STACK (Django)                                    │
│    ┌─────────────────────────────────────────────┐              │
│    │ TenantHostnameNormalizerMiddleware          │              │
│    │ - Normaliza hostname (remueve puerto)       │              │
│    └─────────────────────────────────────────────┘              │
│    ┌─────────────────────────────────────────────┐              │
│    │ DynamicAllowedHostsMiddleware               │              │
│    │ - Consulta BD: dominios activos             │              │
│    │ - Actualiza ALLOWED_HOSTS dinámicamente     │              │
│    └─────────────────────────────────────────────┘              │
│    ┌─────────────────────────────────────────────┐              │
│    │ TenantMainMiddleware (django-tenants)       │              │
│    │ - Detecta tenant por hostname               │              │
│    │ - www.chalanpro.net → schema 'public'       │              │
│    └─────────────────────────────────────────────┘              │
│    ┌─────────────────────────────────────────────┐              │
│    │ DynamicCSRFMiddleware                       │              │
│    │ - Consulta BD: dominios activos             │              │
│    │ - Actualiza CSRF_TRUSTED_ORIGINS            │              │
│    └─────────────────────────────────────────────┘              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. VISTA: create_tenant_onboarding()                            │
│    (tenants/views.py)                                           │
│    - Valida datos del formulario                                │
│    - Genera schema_name único (ej: "chalan-onboarding")         │
│    - Genera dominio único (ej: "chalan-onboarding.chalanpro.net")│
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. CREACIÓN DEL TENANT                                          │
│    - Tenant.objects.create(                                     │
│        name="Chalan Onboarding",                                │
│        schema_name="chalan-onboarding",                         │
│        ...                                                      │
│      )                                                          │
│    - django-tenants crea automáticamente el schema en PostgreSQL│
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. CREACIÓN DEL DOMINIO                                         │
│    - Domain.objects.create(                                     │
│        domain="chalan-onboarding.chalanpro.net",                │
│        tenant=tenant,                                           │
│        is_primary=True                                          │
│      )                                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. EJECUCIÓN DE MIGRACIONES                                     │
│    - migrate_schemas --schema chalan-onboarding                 │
│    - Crea todas las tablas en el nuevo schema                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 10. ACTUALIZACIÓN DINÁMICA                                      │
│     - El dominio se agrega a la BD (schema 'public')            │
│     - En la próxima petición (máx 5 min), los middlewares:     │
│       * DynamicAllowedHostsMiddleware detecta el nuevo dominio  │
│       * DynamicCSRFMiddleware agrega https://... a CSRF         │
│     - NO se requiere reiniciar el servidor                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 11. RESPUESTA AL FRONTEND                                       │
│     {                                                            │
│       "success": true,                                          │
│       "tenant": {...},                                          │
│       "domain": "chalan-onboarding.chalanpro.net",              │
│       "redirect_url": "https://chalan-onboarding.chalanpro.net/login/"│
│     }                                                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 12. REDIRECCIÓN DEL USUARIO                                     │
│     window.location.href = "https://chalan-onboarding.chalanpro.net/login/"│
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 13. PRIMERA PETICIÓN AL DOMINIO DEL TENANT                      │
│     GET https://chalan-onboarding.chalanpro.net/login/          │
│     - Nginx recibe en wildcard *.chalanpro.net                  │
│     - Proxy a backend:8000                                      │
│     - Middleware detecta tenant por hostname                    │
│     - Cambia a schema 'chalan-onboarding'                       │
│     - Frontend se sirve (mismo build para todos los tenants)    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1.2 Puntos Clave del Flujo

1. **Onboarding en Schema Público**: El formulario de onboarding se procesa en el schema `public` (dominio `www.chalanpro.net`), no en un tenant específico.

2. **Creación Automática del Schema**: `django-tenants` crea automáticamente el schema en PostgreSQL cuando se crea un `Tenant` con `auto_create_schema=True`.

3. **Actualización Dinámica**: Los middlewares `DynamicAllowedHostsMiddleware` y `DynamicCSRFMiddleware` actualizan las configuraciones cada 5 minutos, permitiendo que nuevos tenants funcionen sin reiniciar.

4. **Mismo Frontend para Todos**: Todos los tenants comparten el mismo build del frontend Vue.js. El backend detecta el tenant por hostname y cambia al schema correspondiente.

---

## 2.2 Configuraciones para Dominio, Tenant y DNS

### 2.2.1 Configuración de DNS en Hostinger

**Panel DNS:** https://hpanel.hostinger.com/domain/chalanpro.net/dns

| Tipo      | Name | Points to / Content | TTL   | Propósito                                   |
| --------- | ---- | ------------------- | ----- | ------------------------------------------- |
| **A**     | @    | 72.60.168.62        | 14400 | Frontend principal                          |
| **A**     | api  | 72.60.168.62        | 14400 | API REST y Admin Django                     |
| **A**     | \*   | 72.60.168.62        | 14400 | Subdominios dinámicos de tenants (wildcard) |
| **CNAME** | www  | chalanpro.net       | 14400 | Frontend (www)                              |
| **CAA**   | @    | (varios)            | 14400 | Certificados SSL                            |

**Nota:** El registro wildcard `*` permite que cualquier subdominio (ej: `tenant1.chalanpro.net`) resuelva a la IP del servidor.

### 2.2.2 Configuración de Certificados SSL

**Certificado Wildcard:** `*.chalanpro.net` (obtenido con `init-certbot-wildcard.sh`)

Este certificado cubre:

- `chalanpro.net`
- `www.chalanpro.net`
- `api.chalanpro.net`
- `*.chalanpro.net` (cualquier subdominio de tenant)

**Ubicación:** `/etc/letsencrypt/live/chalanpro.net/`

### 2.2.3 Configuración de Tenant en Django

**Variables de Entorno (`envs/backend.env`):**

```bash
TENANT_BASE_DOMAIN=chalanpro.net
ALLOWED_HOSTS="chalanpro.net,*.chalanpro.net,www.chalanpro.net,api.chalanpro.net,www.api.chalanpro.net,72.60.168.62,localhost,127.0.0.1"
CSRF_TRUSTED_ORIGINS=https://chalanpro.net,https://www.chalanpro.net,https://api.chalanpro.net,https://www.api.chalanpro.net,https://*.chalanpro.net
```

**Configuración en `project/settings.py`:**

```python
TENANT_BASE_DOMAIN = os.environ.get('TENANT_BASE_DOMAIN', 'chalanpro.net')
PUBLIC_SCHEMA_URLCONF = 'project.urls_public'  # URLs para schema público
```

### 2.2.4 Estructura de Dominios en Base de Datos

**Schema `public` (tabla `tenants_domain`):**

| id  | domain                            | tenant_id  | is_primary |
| --- | --------------------------------- | ---------- | ---------- |
| 1   | `chalanpro.net`                   | 1 (public) | true       |
| 2   | `api.chalanpro.net`               | 1 (public) | false      |
| 3   | `chalan-onboarding.chalanpro.net` | 2          | true       |
| 4   | `tenant2.chalanpro.net`           | 3          | true       |

**Nota:** Cada tenant tiene al menos un dominio en `tenants_domain`. El dominio primario (`is_primary=True`) es el que se usa para identificar el tenant.

---

## 3. Comandos Rápidos - PostgreSQL en Docker

### 3.1 Conexión a PostgreSQL

```bash
# Acceder a PostgreSQL desde el contenedor
docker compose exec postgres psql -U chalanpro_user -d chalanpro

# Desde el host (si PostgreSQL está expuesto)
psql -h localhost -p 5432 -U chalanpro_user -d chalanpro
```

### 3.2 Consultas Útiles

```sql
-- Listar todos los schemas (tenants)
SELECT schema_name FROM information_schema.schemata
WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast');

-- Listar tenants activos
SELECT id, name, schema_name, is_active FROM tenants_tenant;

-- Listar dominios de tenants
SELECT d.domain, t.name, t.schema_name
FROM tenants_domain d
JOIN tenants_tenant t ON d.tenant_id = t.id;

-- Cambiar a schema de un tenant específico
SET search_path TO "chalan-onboarding";

-- Ver tablas en el schema actual
\dt

-- Volver al schema público
SET search_path TO public;
```

### 3.3 Backup y Restauración

```bash
# Backup completo de la base de datos
docker compose exec postgres pg_dump -U chalanpro_user chalanpro > backup_$(date +%Y%m%d).sql

# Backup de un schema específico (tenant)
docker compose exec postgres pg_dump -U chalanpro_user -n "chalan-onboarding" chalanpro > backup_tenant.sql

# Restaurar backup completo
docker compose exec -T postgres psql -U chalanpro_user chalanpro < backup_20241213.sql

# Backup con compresión
docker compose exec postgres pg_dump -U chalanpro_user -Fc chalanpro > backup_$(date +%Y%m%d).dump

# Restaurar backup comprimido
docker compose exec -T postgres pg_restore -U chalanpro_user -d chalanpro backup_20241213.dump
```

### 3.4 Gestión de Tenants

```bash
# Listar todos los tenants
docker compose exec backend python manage.py list_tenants

# Crear tenant manualmente
docker compose exec backend python manage.py create_tenant \
  --name "Mi Tenant" \
  --schema mi-tenant \
  --domain mi-tenant.chalanpro.net

# Crear superusuario para un tenant
docker compose exec backend python manage.py create_tenant_superuser \
  --schema mi-tenant \
  --username admin \
  --email admin@example.com \
  --password mi_password
```

---

## 4. Cómo Desplegar Cambios

### 4.1 Desplegar Cambios en el Backend

```bash
# 1. Acceder al directorio raíz del proyecto (donde está .git)
cd /opt/chalanpro

# 2. Actualizar código desde Git
git pull origin main

# 3. Reconstruir y reiniciar el contenedor backend
cd /opt/chalanpro
docker compose up -d --build backend

# 4. Ejecutar migraciones (si hay cambios en modelos)
docker compose exec backend python manage.py migrate_schemas

# 5. Recopilar archivos estáticos (si hay cambios)
docker compose exec backend python manage.py collectstatic --noinput

# 6. Verificar logs
docker compose logs -f backend

docker compose logs -f nginx backend

# 7. Log de WebSocket
docker compose logs -f backend | grep -i "websocket\|tenant"
```

**Nota:** Si solo cambias código Python (sin cambios en modelos), no necesitas ejecutar migraciones. Solo reconstruye y reinicia.

**Importante sobre WebSocket:** El servidor backend usa **Daphne (ASGI)** en lugar de Gunicorn (WSGI) para soportar conexiones WebSocket. Esto permite actualizaciones en tiempo real del calendario y notificaciones. El cambio se realizó en `docker-compose.yml` y `Dockerfile.backend`.

### 4.2 Desplegar Cambios en el Frontend

```bash
# 1. Acceder al directorio raíz del proyecto (donde está .git)
cd /opt/chalanpro

# 2. Actualizar código desde Git
git pull origin main

# 3. Reconstruir el frontend (esto compila Vue.js)
cd /opt/chalanpro
docker compose up -d --build frontend

# 4. Reiniciar Nginx para servir los nuevos archivos estáticos
docker compose restart nginx

# 5. Verificar logs
docker compose logs -f frontend
```

**Nota:** El build del frontend puede tardar 1-2 minutos. Los archivos compilados se copian a `./app/vuefrontend/dist/` que es servido por Nginx.

### 4.3 Desplegar Cambios en Ambos (Backend + Frontend)

```bash
# 1. Actualizar código
cd /opt/chalanpro
git pull origin main

# 2. Reconstruir ambos servicios
cd /opt/chalanpro
docker compose up -d --build backend frontend

# 3. Ejecutar migraciones (si es necesario)
docker compose exec backend python manage.py migrate_schemas
docker compose exec backend python manage.py collectstatic --noinput

# 4. Reiniciar Nginx
docker compose restart nginx

# 5. Verificar estado
docker compose ps
docker compose logs -f
```

---

## 4.1 Estructura de Branches de Git

**⚠️ IMPORTANTE - Cambio en la Estructura del Repositorio (Diciembre 2024):**

El repositorio Git se movió de `/opt/chalanpro/app/` a `/opt/chalanpro/` para incluir toda la configuración de infraestructura (Docker, Nginx, scripts) en el repositorio. Esto permite que cualquier desarrollador que clone el repo tenga todo lo necesario para levantar el stack completo.

**Estructura actual:**

- Repositorio Git: `/opt/chalanpro/.git/` (raíz del proyecto)
- Código de aplicación: `/opt/chalanpro/app/` (subdirectorio)
- Configuración Docker: `/opt/chalanpro/docker-compose.yml` (en el repo)
- Configuración Nginx: `/opt/chalanpro/nginx/` (en el repo)
- Scripts de utilidad: `/opt/chalanpro/*.sh` (en el repo)

**Archivos excluidos del repositorio (en `.gitignore`):**

- `envs/*.env` (archivos con secretos, solo templates `.example.env` están en el repo)
- `postgres_data/` (datos de base de datos)
- `certbot/` (certificados SSL)
- `backups/` (backups de base de datos)

### 4.1.1 Branches Actuales

```bash
# Ver branches locales
cd /opt/chalanpro
git branch

# Ver branches remotos
git branch -r

# Ver todas las branches (locales + remotas)
git branch -a
```

**Branches principales:**

- `main`: Branch de producción (estable)
- `chalan_onboarding_local_12-8-25`: Branch de desarrollo/onboarding

### 4.1.2 Actualizar Branch Main con Últimos Cambios

```bash
# 1. Asegurarse de estar en main
cd /opt/chalanpro
git checkout main

# 2. Obtener últimos cambios del remoto
git fetch origin

# 3. Ver diferencias antes de hacer merge
git log HEAD..origin/main

# 4. Hacer merge de origin/main a main local
git merge origin/main

# O usar pull (fetch + merge en un comando)
git pull origin main

# 5. Si hay conflictos, resolverlos y hacer commit
# git add .
# git commit -m "Resolve merge conflicts"

# 6. Verificar el estado
git status
git log --oneline -5
```

### 4.1.3 Verificar Estado del Repositorio

```bash
# Ver estado actual (archivos modificados, staged, etc.)
git status

# Ver último commit
git log -1

# Ver diferencias con el remoto
git fetch origin
git diff main origin/main

# Ver historial de commits
git log --oneline -10

# Ver información del remoto
git remote -v

# Verificar si hay cambios sin commitear
git status --short
```

### 4.1.4 Workflow Recomendado

1. **Antes de desplegar:**

   ```bash
   cd /opt/chalanpro
   git fetch origin
   git status
   git log HEAD..origin/main  # Ver qué cambios hay
   ```

2. **Actualizar main:**

   ```bash
   git checkout main
   git pull origin main
   ```

3. **Desplegar cambios:**

   ```bash
   cd /opt/chalanpro
   docker compose up -d --build backend frontend
   ```

4. **Verificar:**
   ```bash
   docker compose ps
   docker compose logs -f backend
   ```

---

## 5. Host y Credenciales PostgreSQL

### 5.1 Información de Conexión

| Parámetro              | Valor                                                      |
| ---------------------- | ---------------------------------------------------------- |
| **Host**               | `localhost` (desde el servidor) o `72.60.168.62` (externo) |
| **Puerto**             | `5432`                                                     |
| **Base de Datos**      | `chalanpro`                                                |
| **Usuario**            | `chalanpro_user`                                           |
| **Contraseña**         | `2hSGqPHiNhaktRS_lxY3CprmDBYtHJxsIxWZhe-iqd4`              |
| **Schema por Defecto** | `public` (para gestión de tenants)                         |

### 5.2 Conexión desde el Servidor

```bash
# Usando psql (si está instalado en el host)
psql -h localhost -p 5432 -U chalanpro_user -d chalanpro

# Usando Docker
docker compose exec postgres psql -U chalanpro_user -d chalanpro
```

### 5.3 Conexión Externa (desde otra máquina)

**Requisitos:**

- Puerto 5432 debe estar abierto en el firewall
- PostgreSQL debe aceptar conexiones externas (verificar `postgresql.conf` y `pg_hba.conf`)

```bash
# Desde otra máquina
psql -h 72.60.168.62 -p 5432 -U chalanpro_user -d chalanpro
```

**Nota:** Por seguridad, se recomienda usar un túnel SSH o VPN en lugar de exponer PostgreSQL directamente a Internet.

### 5.4 Conexión desde pgAdmin

**URL:** `http://72.60.168.62:5050`

**Credenciales pgAdmin:**

- **Email:** `admin@chalanpro.net`
- **Password:** `ChalanPro2024!`

**Configuración del servidor en pgAdmin:**

- **Name:** Chalan-Pro Production
- **Host:** `postgres` (nombre del servicio Docker) o `172.x.x.x` (IP del contenedor)
- **Port:** `5432`
- **Maintenance database:** `chalanpro`
- **Username:** `chalanpro_user`
- **Password:** `2hSGqPHiNhaktRS_lxY3CprmDBYtHJxsIxWZhe-iqd4`

---

## 6. Seguridad del Servidor

### 6.1 Estado Actual de Seguridad

| Aspecto                  | Estado                  | Nivel | Notas                                             |
| ------------------------ | ----------------------- | ----- | ------------------------------------------------- |
| **HTTPS/SSL**            | ✅ Activo               | Alto  | Certificados Let's Encrypt, renovación automática |
| **Firewall**             | ⚠️ Parcial              | Medio | Solo puertos 80, 443, 5432, 5050 abiertos         |
| **Autenticación Django** | ✅ Activo               | Alto  | Token-based authentication, CSRF protection       |
| **ALLOWED_HOSTS**        | ✅ Dinámico             | Alto  | Actualización automática vía middleware           |
| **CSRF Protection**      | ✅ Dinámico             | Alto  | Actualización automática vía middleware           |
| **DEBUG Mode**           | ✅ Deshabilitado        | Alto  | `DEBUG=False` en producción                       |
| **Secret Keys**          | ✅ Variables de entorno | Alto  | No hardcodeadas en código                         |
| **PostgreSQL Acceso**    | ⚠️ Expuesto             | Medio | Puerto 5432 abierto (considerar restringir)       |
| **pgAdmin Acceso**       | ⚠️ Expuesto             | Bajo  | Puerto 5050 abierto sin autenticación adicional   |
| **Headers de Seguridad** | ✅ Configurados         | Alto  | HSTS, X-Frame-Options, X-Content-Type-Options     |
| **Backups Automáticos**  | ❌ No configurado       | Bajo  | Requiere configuración de cron job                |

### 6.2 Mejoras Recomendadas

#### 🔴 Prioridad Alta

1. **Restringir Acceso a PostgreSQL:**

   ```bash
   # Cerrar puerto 5432 al público
   # Usar solo conexiones internas de Docker o túnel SSH
   # Editar docker-compose.yml: remover "5432:5432" de ports
   ```

2. **Proteger pgAdmin:**
   - Configurar autenticación adicional (2FA)
   - Restringir acceso por IP
   - O mejor: acceder solo vía túnel SSH

3. **Configurar Backups Automáticos:**
   ```bash
   # Agregar a crontab
   0 2 * * * docker compose -f /opt/chalanpro/docker-compose.yml exec -T postgres pg_dump -U chalanpro_user chalanpro > /opt/chalanpro/backups/backup_$(date +\%Y\%m\%d).sql
   ```

#### 🟡 Prioridad Media

4. **Configurar Fail2Ban:**
   - Proteger contra ataques de fuerza bruta
   - Bloquear IPs después de intentos fallidos

5. **Monitoreo y Alertas:**
   - Configurar logs centralizados
   - Alertas por errores críticos
   - Monitoreo de recursos (CPU, RAM, disco)

6. **Rate Limiting:**
   - Limitar requests por IP en Nginx
   - Proteger endpoints de API contra abuso

#### 🟢 Prioridad Baja

7. **WAF (Web Application Firewall):**
   - Implementar ModSecurity en Nginx
   - Protección adicional contra ataques comunes

8. **Auditoría de Seguridad:**
   - Escaneo de vulnerabilidades periódico
   - Revisión de dependencias (npm audit, pip check)

### 6.3 Configuración Actual de Headers de Seguridad

**Nginx (`nginx/default.conf`):**

```nginx
# Headers configurados
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
```

**Django (`project/settings.py`):**

- `SECURE_SSL_REDIRECT`: Configurado vía Nginx
- `SESSION_COOKIE_SECURE`: `True` (si está configurado)
- `CSRF_COOKIE_SECURE`: `True` (si está configurado)

### 6.4 Checklist de Seguridad

- [x] HTTPS habilitado y forzado
- [x] Certificados SSL válidos y renovación automática
- [x] DEBUG=False en producción
- [x] Secret keys en variables de entorno
- [x] ALLOWED_HOSTS configurado
- [x] CSRF protection activo
- [x] Headers de seguridad en Nginx
- [ ] PostgreSQL no expuesto públicamente
- [ ] pgAdmin protegido o accesible solo vía SSH
- [ ] Backups automáticos configurados
- [ ] Fail2Ban configurado
- [ ] Monitoreo y alertas activos
- [ ] Rate limiting configurado

---

## 7. URLs del Sistema

### 7.1 URLs de Producción

| Servicio               | URL                                     | Descripción                      |
| ---------------------- | --------------------------------------- | -------------------------------- |
| **Frontend Principal** | `https://chalanpro.net`                 | Frontend Vue.js (público)        |
| **Frontend (www)**     | `https://www.chalanpro.net`             | Frontend Vue.js (www)            |
| **Onboarding**         | `https://www.chalanpro.net/onboarding`  | Formulario de creación de tenant |
| **API REST**           | `https://api.chalanpro.net/api/`        | API REST de Django               |
| **Admin Django**       | `https://api.chalanpro.net/admin/`      | Panel de administración          |
| **Tenant Login**       | `https://{tenant}.chalanpro.net/login/` | Login de tenant específico       |
| **pgAdmin**            | `http://72.60.168.62:5050`              | Interfaz web de PostgreSQL       |

### 7.2 Credenciales de Acceso

**Admin Django:**

- **URL:** `https://api.chalanpro.net/admin/`
- **Username:** `superchalan`
- **Password:** `d162025OH$!`

**pgAdmin:**

- **URL:** `http://72.60.168.62:5050`
- **Email:** `admin@chalanpro.net`
- **Password:** `ChalanPro2024!`

---

## 8. Comandos Útiles Adicionales

### 8.1 Gestión de Contenedores

```bash
# Ver estado de todos los contenedores
docker compose ps

# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f backend
docker compose logs -f nginx

# Reiniciar un servicio
docker compose restart backend
docker compose restart nginx

# Detener todos los servicios
docker compose down

# Iniciar todos los servicios
docker compose up -d

# Reconstruir un servicio específico
docker compose up -d --build backend
```

### 8.2 Django Management

```bash
# Ejecutar migraciones en todos los schemas
docker compose exec backend python manage.py migrate_schemas

# Ejecutar migraciones en un schema específico
docker compose exec backend python manage.py migrate_schemas --schema public
docker compose exec backend python manage.py migrate_schemas --schema chalan-onboarding

# Crear superusuario (schema público)
docker compose exec backend python manage.py createsuperuser

# Shell de Django
docker compose exec backend python manage.py shell

# Recopilar archivos estáticos
docker compose exec backend python manage.py collectstatic --noinput
```

### 8.3 Certificados SSL

```bash
# Verificar renovación de certificados (dry-run)
sudo certbot renew --dry-run

# Renovar certificados manualmente
sudo certbot renew

# Reiniciar Nginx después de renovar
docker compose restart nginx

# Ver certificados instalados
sudo certbot certificates
```

---

## 9. Inventory Master Data Setup

### 9.1 Resumen de la Implementación

El sistema de **Inventory Master Data Setup** permite a los administradores de tenants importar datos maestros de inventario de forma opcional y controlada. Esta funcionalidad fue implementada para permitir que cada tenant decida cuándo y si desea cargar los datos maestros iniciales de productos, marcas, categorías, unidades, tipos de precio, almacenes y precios de productos.

**Características principales:**

- ✅ Importación opcional y controlada por el administrador del tenant
- ✅ Descarga de archivo Excel pre-generado con todos los datos maestros
- ✅ **Imágenes de productos**: se importan desde `appinventory/fixtures/media/products/{product_id}/{brand_id}/` y se crean registros `ProductImage` tras el loaddata
- ✅ Bloqueo de doble importación mediante flag `seed_inventory_done`
- ✅ Operación transaccional (si falla, no se guarda nada parcial)
- ✅ Reseteo automático de secuencias de base de datos después de la importación
- ✅ Acceso desde el menú "Configuration" del NavbarComponent
- ✅ Interfaz en inglés con estilos consistentes del sistema

### 9.2 Componentes del Sistema

#### Backend (Django)

**Modelo Tenant (`tenants/models.py`):**

- Campo `seed_inventory_done`: BooleanField que indica si los datos maestros han sido importados para el tenant.

**Vistas API (`appinventory/views.py`):**

- `InventoryMasterDataPreviewAPIView` (GET `/api/master-data/preview/`): Verifica el estado de `seed_inventory_done` y devuelve información sobre si los datos ya fueron importados.
- `InventoryMasterDataExcelDownloadAPIView` (GET `/api/master-data/excel/`): Sirve el archivo Excel pre-generado desde `appinventory/static/appinventory/masters_inventory.xlsx`.
- `InventoryMasterDataImportAPIView` (POST `/api/master-data/import/`): Copia el repo de imágenes a `MEDIA_ROOT/products/`, carga `masters_inventory.json` **sin** entradas ProductImage, luego inyecta `masters_productimage.json` (ProductImage con assignment_id 1,2,3…). Si no existe ese fixture, crea ProductImage desde `MEDIA_ROOT/products/{product_id}/{brand_id}/`. Resetea secuencias (incl. `appinventory_productimage`) y marca `seed_inventory_done=True`.

**Management Command (`appinventory/management/commands/generate_masters_inventory_excel.py`):**

- Genera el archivo Excel `masters_inventory.xlsx` desde el fixture JSON `masters_inventory.json`.
- Crea hojas separadas para cada modelo: Categorías de Unidades, Unidades de Medida, Almacenes, Categorías de Productos, Marcas, Tipos de Precio, Productos, y Precios de Productos.
- Guarda el archivo en `appinventory/static/appinventory/masters_inventory.xlsx` para su descarga.

**Fixture de Datos (`appinventory/fixtures/masters_inventory.json`):**

- Archivo JSON con todos los datos maestros de inventario.
- Incluye: UnitCategory, UnitOfMeasure, Warehouse, ProductCategory, ProductBrand, PriceType, Product, ProductPrice. **Product debe incluir el campo `brands`** (ej. `"brands": [1]`) para que al cargar se creen las filas en `appinventory_productbrandassignment`; si falta, el backend **inyecta en memoria** `brands` con el primer ProductBrand del fixture para evitar "No brand assigned" y la FK en ProductImage. En la importación se omiten las entradas ProductImage si las hubiera.
- **Warehouse con `truck_id`:** En la importación se anula `truck` para evitar la FK `crewsapp_truck` (no existe en el tenant destino). Los warehouses móviles quedan como almacenes normales.

**Fixture de imágenes de productos (`appinventory/fixtures/masters_productimage.json`):**

- Se carga **después** de `masters_inventory.json`. Contiene solo ProductImage con **assignment_id 1, 2, 3…** (orden igual al de las asignaciones creadas al cargar el maestro).
- Se genera con: `python manage.py generate_masters_productimage_fixture --schema test_dominio_local`.

**Repo de imágenes a importar (`appinventory/fixtures/media/products/` o `media_volume`):**

- Directorio base con las imágenes de productos. Estructura: `{product_id}/{brand_id}/*.jpg`.
- Se copia a `MEDIA_ROOT/products/` (en Docker, `media_volume` montado en `/app/media`) **antes** del loaddata; tras loaddata se crean los registros `ProductImage` desde ese directorio por `(product_id, brand_id)`.
- Se actualiza desde el tenant de desarrollo **test-dominio-local.chalanpro.net** con: `python manage.py export_fixture_product_images --schema test_dominio_local`.
- Así el repo queda como fuente única; cada tenant que hace Inventory Master Data Setup recibe productos e imágenes desde ese repo.

**Dónde se guardan las imágenes de productos (ubicación en runtime):**

- **Ruta física:** `MEDIA_ROOT/products/{product_id}/{brand_id}/{timestamp}_{nombre}.{ext}` (ej. `products/42/3/20260214_133045_imagen_producto.jpg`).
- **En Docker:** `/app/media/products/` (volumen `media_volume` montado en el contenedor backend).
- **En local:** `app/media/products/` (según `MEDIA_ROOT = BASE_DIR / 'media'` en `settings.py`).
- **URL pública:** `/media/` (configurada en `MEDIA_URL`). Ejemplo: `http://dominio/media/products/42/3/20260214_133045_imagen.jpg`.

#### Frontend (Vue.js)

**Componente (`vuefrontend/src/components/inventory/InventoryMasterDataSetup.vue`):**

- Componente regular (no modal) con estilos del sistema.
- Funcionalidades:
  - Descarga del archivo Excel pre-generado
  - Vista previa del estado de importación (`seedDone`)
  - Confirmación de importación con SweetAlert2
  - Bloqueo de importación si ya se realizó (`seedDone === true`)
  - Indicadores de carga y mensajes de estado

**Vista (`vuefrontend/src/views/InventoryMasterDataSetupView.vue`):**

- Vista dedicada que contiene el componente `InventoryMasterDataSetup`.

**Router (`vuefrontend/src/router/index.js`):**

- Ruta `/inventory-master-data-setup` que apunta a `InventoryMasterDataSetupView`.

**Navbar (`vuefrontend/src/components/layout/NavbarComponent.vue`):**

- Opción "Inventory Master Data Setup" en el menú desplegable "Configuration".

### 9.3 Flujo de Uso

1. **Acceso:**
   - El administrador del tenant accede a "Configuration" → "Inventory Master Data Setup" desde el NavbarComponent.

2. **Estado Inicial:**
   - El componente carga el estado de `seed_inventory_done` desde `/api/master-data/preview/`.
   - Si `seedDone === false`, muestra opciones para descargar e importar.
   - Si `seedDone === true`, muestra "Inventory masters imported" y deshabilita la importación.

3. **Descarga del Excel:**
   - El administrador hace clic en "Download Excel File".
   - El sistema descarga `masters_inventory.xlsx` desde `/api/master-data/excel/`.
   - El archivo contiene todas las hojas con los datos maestros.

4. **Revisión:**
   - El administrador puede revisar y ajustar precios en el Excel descargado (opcional, offline).

5. **Importación:**
   - El administrador hace clic en "Import Masters into My Tenant".
   - Se muestra una confirmación con SweetAlert2.
   - Al confirmar, se envía POST a `/api/master-data/import/`.
   - El backend:
     - Copia el repo de imágenes `appinventory/fixtures/media/products/` a `MEDIA_ROOT/products/` (en Docker: media_volume en `/app/media`)
     - Carga `masters_inventory.json` sin entradas ProductImage
     - Carga `masters_productimage.json` (ProductImage con assignment_id 1,2,3…). Si no existe, crea ProductImage desde `MEDIA_ROOT/products/{product_id}/{brand_id}/`
     - Resetea las secuencias de las tablas (incl. `appinventory_productimage`)
     - Marca `seed_inventory_done=True` en el tenant
     - Confirma la transacción
   - Si hay error, la transacción se revierte y `seed_inventory_done` permanece `False`.
   - La respuesta puede incluir `images_copied` (archivos copiados desde repo) e `images_synced` (registros ProductImage creados).

6. **Post-Importación:**
   - Después de la importación exitosa, el componente muestra "Inventory masters imported".
   - La opción de importar queda deshabilitada.

### 9.4 Comandos de Gestión

**Generar masters_inventory.json, masters_productimage.json y productbrandassignment.json desde un tenant:**

```bash
# Genera, en este orden: masters_inventory.json, masters_productimage.json y productbrandassignment.json
# (todos desde el mismo schema para mantener coherencia de IDs)
docker compose exec backend python manage.py generate_masters_inventory_fixture --schema test_dominio_local

# Con ruta de salida distinta para el inventario
docker compose exec backend python manage.py generate_masters_inventory_fixture --schema test_dominio_local --output /app/appinventory/fixtures/masters_inventory.json
```

**Generar el archivo Excel:**

```bash
# Desde el contenedor backend
docker compose exec backend python manage.py generate_masters_inventory_excel

# El archivo se guarda en: app/appinventory/static/appinventory/masters_inventory.xlsx
```

**Actualizar el repo de imágenes desde el tenant de desarrollo (test-dominio-local):**

```bash
docker compose exec backend python manage.py export_fixture_product_images --schema test_dominio_local
# Estructura: appinventory/fixtures/media/products/<product_id>/<brand_id>/*.jpg
```

**Generar masters_productimage.json (inyección tras masters_inventory.json):**

```bash
# Desde un tenant que tenga ProductImage (ej. test_dominio_local). Asigna assignment_id 1,2,3...
docker compose exec backend python manage.py generate_masters_productimage_fixture --schema test_dominio_local
# Salida: appinventory/fixtures/masters_productimage.json
```

**Verificar el estado de un tenant:**

```bash
# Desde el shell de Django
docker compose exec backend python manage.py shell
>>> from tenants.models import Tenant
>>> tenant = Tenant.objects.get(schema_name='nombre-del-tenant')
>>> print(f"Seed done: {tenant.seed_inventory_done}")
```

**Forzar re-importación (solo para desarrollo/testing):**

```bash
# Desde el shell de Django
docker compose exec backend python manage.py shell
>>> from tenants.models import Tenant
>>> tenant = Tenant.objects.get(schema_name='nombre-del-tenant')
>>> tenant.seed_inventory_done = False
>>> tenant.save()
```

**Nota:** El archivo Excel debe regenerarse si se actualiza el fixture `masters_inventory.json`. Ejecutar el comando `generate_masters_inventory_excel` después de cualquier cambio en los datos maestros.

#### 9.4.1 Configuración DocumentType: creates_serialized_items

En el formulario de tipos de documento (**DocTypeForm.vue**, ruta `/document-types`) existe el campo de configuración **"Creates Serialized Items"** (`creates_serialized_items`). Este switch indica que el tipo de documento es el que **crea o registra ítems serializados** (p. ej. **GRN – Goods Receipt Note**). Cuando está activo y Stock Movement es +1 Entry:

- Al guardar un documento de ese tipo que tenga líneas con productos SERIALIZED, se abre el modal **AssetTagAssignmentModal** para asignar números de serie.
- El botón **"Assign Serial Numbers"** en la grilla de líneas solo se muestra para documentos cuyo tipo tiene este flag activo.

El campo incluye **tooltip** (`v-tt` + `data-title`) según las guías del proyecto: _"Document type that creates/registers serialized items; opens the asset tag assignment modal when the document has serialized items (e.g. GRN)"_.

**Después de cambiar el modelo DocumentType o esta configuración:**

1. **Aplicar la migración en todos los schemas/tenants:**

   ```bash
   docker compose exec backend python manage.py migrate_schemas
   ```

2. **Regenerar el fixture maestro de inventario** (si también se actualizan datos maestros de inventario):

   ```bash
   docker compose exec backend python manage.py generate_masters_inventory_fixture --schema test_dominio_local --output /app/appinventory/fixtures/masters_inventory.json
   ```

3. **Regenerar el fixture maestro de tipos de documento** (para que los nuevos tenants reciban los tipos actualizados con `creates_serialized_items`):
   ```bash
   docker compose exec backend python manage.py tenant_command dumpdata \
     --schema test_dominio_local \
     apptransactions.DocumentType \
     --indent 2 \
     --output /app/apptransactions/fixtures/masters_document_type.json
   ```

### 9.5 Generar el Fixture JSON de Datos Maestros

**Importante:** Para generar o actualizar el archivo `masters_inventory.json` desde la base de datos de un tenant, use el comando `dumpdata` de Django. Se recomienda usar el **tenant de desarrollo** (test-dominio-local.chalanpro.net / schema `test_dominio_local`) como fuente principal.

**Paso 1 – Actualizar repo de imágenes desde el tenant de desarrollo (opcional):**

```bash
docker compose exec backend python manage.py export_fixture_product_images --schema test_dominio_local
```

**Paso 2 – Generar o actualizar el fixture JSON:**

```bash
# Generar el fixture JSON desde el tenant de desarrollo (ProductImage es opcional; en la importación se omiten)
# Nota: Warehouse con truck_id se anula en la importación (evita FK crewsapp_truck inexistente en tenant destino)
docker compose exec backend python manage.py tenant_command dumpdata \
  --schema test_dominio_local \
  appinventory.UnitCategory \
  appinventory.UnitOfMeasure \
  appinventory.Warehouse \
  appinventory.ProductCategory \
  appinventory.ProductBrand \
  appinventory.PriceType \
  appinventory.Product \
  appinventory.ProductPrice \
  --indent 2 \
  --output /app/appinventory/fixtures/masters_inventory.json
```

**Nota:** El fixture `masters_inventory.json` debe tener en cada Product el campo **`brands`** (ej. `"brands": [60]`) para que al cargar se creen las filas en `appinventory_productbrandassignment` (assignment_id 1, 2, 3…). Si no, al cargar `masters_productimage.json` fallará la FK. Para generar `masters_productimage.json` (inyección tras el maestro): `python manage.py generate_masters_productimage_fixture --schema test_dominio_local`. Después de cambiar el JSON, ejecute `generate_masters_inventory_excel` para regenerar el Excel.

-- Productos sin ninguna imagen (en schema test_dominio_local)
SELECT p.id AS product_id,
p.sku AS codigo,
p.name AS nombre
FROM test_dominio_local.appinventory_product p
LEFT JOIN test_dominio_local.appinventory_productimage pi ON pi.product_id = p.id
WHERE pi.id IS NULL
AND p.is_active = true
ORDER BY p.sku;

-- producto–marca sin imagen
SELECT p.id AS product_id,
p.sku AS codigo,
p.name AS nombre,
a.id AS assignment_id,
b.name AS marca
FROM test_dominio_local.appinventory_product p
JOIN test_dominio_local.appinventory_productbrandassignment a ON a.product_id = p.id
JOIN test_dominio_local.appinventory_productbrand b ON b.id = a.brand_id
LEFT JOIN test_dominio_local.appinventory_productimage pi ON pi.assignment_id = a.id
WHERE pi.id IS NULL
AND p.is_active = true
ORDER BY p.sku, b.name;

---

## 10. Troubleshooting

### 10.1 El Frontend No Carga

1. Verificar que el build se completó:

   ```bash
   docker compose logs frontend
   ```

2. Verificar archivos en `./app/vuefrontend/dist/`:

   ```bash
   ls -la /opt/chalanpro/app/vuefrontend/dist/
   ```

3. Reconstruir el frontend:
   ```bash
   docker compose up -d --build frontend
   ```

### 10.2 El Backend No Responde

1. Verificar logs:

   ```bash
   docker compose logs backend
   ```

2. Verificar conexión a la base de datos:

   ```bash
   docker compose exec backend python manage.py check --database default
   ```

3. Ejecutar migraciones:
   ```bash
   docker compose exec backend python manage.py migrate_schemas
   ```

### 10.3 Problemas con Multi-Tenant

1. Verificar que el dominio esté en la base de datos:

   ```bash
   docker compose exec backend python manage.py shell
   >>> from tenants.models import Domain
   >>> Domain.objects.all()
   ```

2. Verificar que el dominio esté en ALLOWED_HOSTS (se actualiza dinámicamente cada 5 min)

3. Verificar logs del middleware:
   ```bash
   docker compose logs backend | grep -i "allowed_hosts\|csrf"
   ```

### 10.4 Certificados SSL No Se Generan

1. Verificar que los DNS estén configurados:

   ```bash
   nslookup chalanpro.net
   nslookup api.chalanpro.net
   ```

2. Verificar que el puerto 80 esté abierto:

   ```bash
   sudo ufw status
   ```

3. Verificar que Nginx esté corriendo:
   ```bash
   docker compose ps nginx
   ```

### 10.5 Errores 502 Bad Gateway

**Síntomas:**

- Errores 502 en el navegador al intentar acceder a `/api/` o `/media/`
- Nginx no puede conectar con el backend

**Diagnóstico:**

1. **Revisar logs de Nginx para errores de conexión:**

   ```bash
   docker compose logs --since "2025-12-21T00:00:00" nginx 2>&1 | grep -E "error|502|Connection refused" | tail -30
   ```

2. **Verificar estado del backend:**

   ```bash
   docker compose ps backend
   docker compose logs --tail=20 backend
   ```

3. **Verificar resolución DNS desde Nginx:**

   ```bash
   docker compose exec nginx getent hosts backend
   ```

4. **Verificar conectividad:**
   ```bash
   docker compose exec nginx ping -c 2 chalanpro_backend
   ```

**Soluciones:**

1. **Si el backend está caído:**

   ```bash
   docker compose restart backend
   docker compose logs -f backend
   ```

2. **Si hay problema de resolución DNS (IP cacheada):**
   - La configuración actual de Nginx ya incluye resolución DNS dinámica
   - Reiniciar Nginx para refrescar la caché:

   ```bash
   docker compose restart nginx
   ```

3. **Verificar que la configuración de Nginx tenga resolver DNS:**
   - Debe incluir `resolver 127.0.0.11 valid=10s;` en cada bloque `server`
   - Los `proxy_pass` deben usar variables: `set $backend_upstream http://backend:8000; proxy_pass $backend_upstream;`

**Nota:** Desde Diciembre 2024, la configuración de Nginx incluye resolución DNS dinámica para evitar este problema automáticamente.

### 10.6 Problemas con WebSocket

**Importante:** El servidor usa **Daphne (ASGI)** en lugar de Gunicorn (WSGI) para soportar conexiones WebSocket.

1. **Verificar que Daphne esté corriendo:**

   ```bash
   docker compose logs backend | grep -i "daphne\|listening"
   ```

   Deberías ver: `Listening on TCP address 0.0.0.0:8000`

2. **Verificar conexiones WebSocket en los logs:**

   ```bash
   docker compose logs -f backend | grep -i "websocket\|tenant"
   ```

   Deberías ver mensajes como: `✅ Tenant configurado para WebSocket: [schema_name]`

3. **Si WebSocket no conecta:**
   - Verificar que el servidor esté usando Daphne (no Gunicorn):
     ```bash
     docker compose exec backend ps aux | grep daphne
     ```
   - Verificar configuración de Nginx para `/ws/`:
     ```bash
     cat nginx/default.conf | grep -A 10 "location /ws/"
     ```
   - Verificar que el middleware de tenant esté funcionando:
     ```bash
     docker compose logs backend | grep "Tenant configurado"
     ```

4. **Reiniciar el backend si es necesario:**

   ```bash
   docker compose restart backend
   ```

5. **Verificar en el navegador:**
   - Abrir consola del navegador (F12)
   - Buscar mensajes de conexión WebSocket
   - Deberías ver: `🔌 Conectando WebSocket a: wss://[dominio]/ws/calendar-updates/`
   - Y luego: `Conexión WebSocket establecida.`

**Nota:** Las conexiones WebSocket requieren que el servidor use ASGI (Daphne). Si el servidor está usando Gunicorn, las conexiones WebSocket fallarán con errores 404.

---

## 11. Contacto y Soporte

Para problemas o preguntas:

- Revisar logs: `docker compose logs -f`
- Consultar esta documentación
- Contactar al equipo de desarrollo

---

**Última actualización:** Diciembre 2025  
**Versión del documento:** 1.0
