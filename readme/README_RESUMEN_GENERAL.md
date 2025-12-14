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
- [9. Troubleshooting](#9-troubleshooting)
  - [9.1 El Frontend No Carga](#91-el-frontend-no-carga)
  - [9.2 El Backend No Responde](#92-el-backend-no-responde)
  - [9.3 Problemas con Multi-Tenant](#93-problemas-con-multi-tenant)
  - [9.4 Certificados SSL No Se Generan](#94-certificados-ssl-no-se-generan)
- [10. Contacto y Soporte](#10-contacto-y-soporte)

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
   │         │        │ Gunicorn  │      │           │
   │  Build  │        │  :8000    │      │  :5432    │
   │  Static │        │           │      │           │
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

| Servicio | Contenedor | Puerto | Descripción |
|----------|-----------|--------|-------------|
| **Nginx** | `chalanpro_nginx` | 80, 443 | Reverse proxy, SSL/TLS termination, enrutamiento de requests |
| **Backend** | `chalanpro_backend` | 8000 (interno) | API Django REST + Admin, Gunicorn con 3 workers |
| **Frontend** | `chalanpro_frontend` | - | Build de Vue.js, archivos estáticos servidos por Nginx |
| **PostgreSQL** | `chalanpro_postgres` | 5432 | Base de datos multi-tenant con schemas aislados |
| **pgAdmin** | `chalanpro_pgadmin` | 5050 | Interfaz web para administración de PostgreSQL |

### 1.3 Flujo de Peticiones

1. **Frontend (chalanpro.net, www.chalanpro.net):**
   - Cliente → Nginx (443) → Archivos estáticos Vue.js
   - `/api/*` → Nginx → Backend (8000)

2. **API/Admin (api.chalanpro.net):**
   - Cliente → Nginx (443) → Backend (8000)
   - Rutas: `/api/*`, `/admin/*`

3. **Tenants (*.chalanpro.net):**
   - Cliente → Nginx (443) → Archivos estáticos Vue.js
   - `/api/*` → Nginx → Backend (8000) → Middleware detecta tenant → Schema específico

---

## 2. Estructura General del Proyecto

### 2.1 Diagrama de Estructura de Archivos

```
/opt/chalanpro/
│
├── app/                                    # Monorepo principal (clonado de Git)
│   ├── manage.py                          # Script de gestión de Django
│   ├── requirements.txt                   # Dependencias Python del backend
│   ├── Dockerfile.backend                 # Imagen Docker para backend Django
│   │
│   ├── project/                           # Configuración principal de Django
│   │   ├── settings.py                    # Configuración Django (ALLOWED_HOSTS, CSRF, etc.)
│   │   ├── urls.py                        # URLs principales (tenant-specific)
│   │   ├── urls_public.py                 # URLs para schema público (onboarding, admin global)
│   │   ├── wsgi.py                        # WSGI application para Gunicorn
│   │   │
│   │   └── middleware/                    # Middlewares personalizados
│   │       ├── tenant_hostname.py         # Normaliza hostname (remueve puerto)
│   │       ├── dynamic_allowed_hosts.py   # Actualiza ALLOWED_HOSTS dinámicamente
│   │       └── dynamic_csrf.py            # Actualiza CSRF_TRUSTED_ORIGINS dinámicamente
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
├── docker-compose.yml                     # Orquestación de contenedores Docker
│
├── setup.sh                               # Script de inicialización del sistema
├── init-certbot.sh                        # Script para certificados SSL (dominio principal)
├── init-certbot-api.sh                    # Script para certificados SSL (api.chalanpro.net)
├── init-certbot-wildcard.sh               # Script para certificado SSL wildcard (*.chalanpro.net)
└── enable-https.sh                        # Script para habilitar HTTPS en Nginx
```

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

| Tipo | Name | Points to / Content | TTL | Propósito |
|------|------|---------------------|-----|-----------|
| **A** | @ | 72.60.168.62 | 14400 | Frontend principal |
| **A** | api | 72.60.168.62 | 14400 | API REST y Admin Django |
| **A** | * | 72.60.168.62 | 14400 | Subdominios dinámicos de tenants (wildcard) |
| **CNAME** | www | chalanpro.net | 14400 | Frontend (www) |
| **CAA** | @ | (varios) | 14400 | Certificados SSL |

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

| id | domain | tenant_id | is_primary |
|----|--------|-----------|------------|
| 1 | `chalanpro.net` | 1 (public) | true |
| 2 | `api.chalanpro.net` | 1 (public) | false |
| 3 | `chalan-onboarding.chalanpro.net` | 2 | true |
| 4 | `tenant2.chalanpro.net` | 3 | true |

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
# 1. Acceder al directorio del proyecto
cd /opt/chalanpro/app

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
```

**Nota:** Si solo cambias código Python (sin cambios en modelos), no necesitas ejecutar migraciones. Solo reconstruye y reinicia.

### 4.2 Desplegar Cambios en el Frontend

```bash
# 1. Acceder al directorio del proyecto
cd /opt/chalanpro/app

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
cd /opt/chalanpro/app
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

### 4.1.1 Branches Actuales

```bash
# Ver branches locales
cd /opt/chalanpro/app
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
cd /opt/chalanpro/app
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
   cd /opt/chalanpro/app
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

| Parámetro | Valor |
|-----------|-------|
| **Host** | `localhost` (desde el servidor) o `72.60.168.62` (externo) |
| **Puerto** | `5432` |
| **Base de Datos** | `chalanpro` |
| **Usuario** | `chalanpro_user` |
| **Contraseña** | `2hSGqPHiNhaktRS_lxY3CprmDBYtHJxsIxWZhe-iqd4` |
| **Schema por Defecto** | `public` (para gestión de tenants) |

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

| Aspecto | Estado | Nivel | Notas |
|---------|--------|-------|-------|
| **HTTPS/SSL** | ✅ Activo | Alto | Certificados Let's Encrypt, renovación automática |
| **Firewall** | ⚠️ Parcial | Medio | Solo puertos 80, 443, 5432, 5050 abiertos |
| **Autenticación Django** | ✅ Activo | Alto | Token-based authentication, CSRF protection |
| **ALLOWED_HOSTS** | ✅ Dinámico | Alto | Actualización automática vía middleware |
| **CSRF Protection** | ✅ Dinámico | Alto | Actualización automática vía middleware |
| **DEBUG Mode** | ✅ Deshabilitado | Alto | `DEBUG=False` en producción |
| **Secret Keys** | ✅ Variables de entorno | Alto | No hardcodeadas en código |
| **PostgreSQL Acceso** | ⚠️ Expuesto | Medio | Puerto 5432 abierto (considerar restringir) |
| **pgAdmin Acceso** | ⚠️ Expuesto | Bajo | Puerto 5050 abierto sin autenticación adicional |
| **Headers de Seguridad** | ✅ Configurados | Alto | HSTS, X-Frame-Options, X-Content-Type-Options |
| **Backups Automáticos** | ❌ No configurado | Bajo | Requiere configuración de cron job |

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

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend Principal** | `https://chalanpro.net` | Frontend Vue.js (público) |
| **Frontend (www)** | `https://www.chalanpro.net` | Frontend Vue.js (www) |
| **Onboarding** | `https://www.chalanpro.net/onboarding` | Formulario de creación de tenant |
| **API REST** | `https://api.chalanpro.net/api/` | API REST de Django |
| **Admin Django** | `https://api.chalanpro.net/admin/` | Panel de administración |
| **Tenant Login** | `https://{tenant}.chalanpro.net/login/` | Login de tenant específico |
| **pgAdmin** | `http://72.60.168.62:5050` | Interfaz web de PostgreSQL |

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

## 9. Troubleshooting

### 9.1 El Frontend No Carga

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

### 9.2 El Backend No Responde

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

### 9.3 Problemas con Multi-Tenant

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

### 9.4 Certificados SSL No Se Generan

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

---

## 10. Contacto y Soporte

Para problemas o preguntas:
- Revisar logs: `docker compose logs -f`
- Consultar esta documentación
- Contactar al equipo de desarrollo

---

**Última actualización:** Diciembre 2025  
**Versión del documento:** 1.0

