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
    - [2.2.2.1 Renovación wildcard automática (API DNS Hostinger)](#2221-renovación-wildcard-automática-api-dns-hostinger)
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
  - [4.4 Desplegar Solo Landing (sin backend)](#44-desplegar-solo-landing-sin-backend)
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
  - [6.5 Remediación de seguridad — Onboarding público](#65-remediación-de-seguridad--onboarding-público)
  - [6.6 Política de secretos en documentación](#66-política-de-secretos-en-documentación)
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
  - [9.6 Workflow: Serialized Items e Inventory Transfers](#96-workflow-serialized-items-e-inventory-transfers)
  - [9.7 Cálculo dinámico de precios en líneas de documento](#97-precios-lineas-documento)
- [10. Billing (Stripe SaaS — appbilling)](#10-billing-stripe-saas--appbilling)
  - [10.1 Arquitectura y schema](#101-arquitectura-y-schema)
  - [10.2 Modelos y planes](#102-modelos-y-planes)
  - [10.3 Endpoints API](#103-endpoints-api)
  - [10.4 Trial, acceso y límites de cuadrillas](#104-trial-acceso-y-límites-de-cuadrillas)
  - [10.5 Variables de entorno Stripe](#105-variables-de-entorno-stripe)
  - [10.6 Comandos de gestión](#106-comandos-de-gestión)
  - [10.7 Frontend y despliegue](#107-frontend-y-despliegue)
  - [10.8 Django admin: solo schema public](#108-django-admin-solo-schema-public)
- [11. Semantic Search (appsearch — JobRhythm)](#11-semantic-search-appsearch--jobrhythm)
  - [11.1 Resumen y modelos](#111-resumen-y-modelos)
  - [11.2 Variables de entorno y PostgreSQL](#112-variables-de-entorno-y-postgresql)
  - [11.3 Comandos de gestión](#113-comandos-de-gestión)
  - [11.3.1 Scripts shell en el host](#1131-scripts-shell-en-el-host)
  - [11.4 API y UI (Fase 2)](#114-api-y-ui-fase-2)
  - [11.5 Fase 3 — Advanced Retrieval y afinación](#115-fase-3--advanced-retrieval-y-afinación)
- [12. Troubleshooting](#12-troubleshooting)
- [13. Contacto y Soporte](#13-contacto-y-soporte)

---

## 📋 Resumen Ejecutivo

Sistema multi-tenant Django con frontend Vue.js desplegado en VPS Hostinger con Ubuntu 24.04 LTS. La plataforma permite la creación dinámica de tenants mediante un proceso de onboarding, donde cada tenant obtiene su propio subdominio y schema de base de datos aislado.

**VPS (Hostinger):** IP y acceso SSH → panel **hPanel → VPS** (no documentar en este repositorio).  
**Dominio Base (actual):** `jobrhythm.net`  
**Landing:** `getjobrhythm.com`  
**Legacy (solo 301, sin app):** `jobrithm.net`, `getjobrithm.com`, `chalanpro.net`, `chalanpro.com`  
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
│   ├── appbilling/                        # Billing Stripe (SHARED_APPS / schema public)
│   │   ├── models.py                      # Plan, Subscription, PaymentEvent
│   │   ├── views.py                       # API billing + webhook Stripe
│   │   ├── middleware.py                  # Enforcement 402 post-trial
│   │   ├── services/                      # Stripe, access, sync, crews limits
│   │   └── management/commands/           # seed_plans, backfill_trial_dates, send_trial_reminders
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
│   ├── appsearch/                         # Búsqueda semántica (SearchIndex, pgvector)
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
│    URL: https://www.jobrithm.net/onboarding                     │
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
│ 3. PETICIÓN HTTP POST (paso 1 — solicitud)                      │
│    POST /api/onboarding/                                        │
│    Body: FormData + turnstile_token + datos del wizard          │
│    Host: api.jobrhythm.net (schema public)                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3b. PROTECCIONES DE SEGURIDAD (ver sección 6.5)                 │
│    - Nginx limit_req (1 req/min por IP en /api/onboarding/)     │
│    - DRF throttling (IP + email)                                 │
│    - Cloudflare Turnstile (CAPTCHA server-side)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. NGINX → BACKEND (schema public)                               │
│    - Throttling / CAPTCHA / validación de formulario            │
│    - Guarda OnboardingPendingRegistration (sin crear schema)    │
│    - Envía email: {FRONT_URL}/onboarding/verify?token=...       │
│    - Respuesta 202: verification_required: true                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. USUARIO CONFIRMA EMAIL                                       │
│    GET /onboarding/verify?token=...  →  POST /api/onboarding/verify/ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. VISTA: verify_onboarding_email() → provision_tenant_workspace│
│    (tenants/services/onboarding_provision.py)                   │
│    - Valida token, expiración y email no registrado             │
│    - Genera schema_name y dominio únicos                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. CREACIÓN DEL TENANT (solo tras verificación)               │
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

1. **Onboarding en Schema Público**: El formulario se procesa en el schema `public` (dominio `api.jobrhythm.net`). La creación del schema del tenant ocurre **solo** tras verificar el email ([6.5](#65-remediación-de-seguridad--onboarding-público)).
2. **Protección anti-abuso**: Throttling DRF, `limit_req` en Nginx, Turnstile y verificación de email en `POST /api/onboarding/` antes de provisionar.

3. **Creación Automática del Schema**: `django-tenants` crea automáticamente el schema en PostgreSQL cuando se crea un `Tenant` con `auto_create_schema=True` (tras la verificación de email).

4. **Actualización Dinámica**: Los middlewares `DynamicAllowedHostsMiddleware` y `DynamicCSRFMiddleware` actualizan las configuraciones cada 5 minutos, permitiendo que nuevos tenants funcionen sin reiniciar.

5. **Mismo Frontend para Todos**: Todos los tenants comparten el mismo build del frontend Vue.js. El backend detecta el tenant por hostname y cambia al schema correspondiente.

---

## 2.2 Configuraciones para Dominio, Tenant y DNS

### 2.2.1 Configuración de DNS en Hostinger

**IP del VPS:** obtener en **hPanel → VPS** (usar `<IP-VPS>` en los registros A; no fijar la IP en Git si el servidor cambia).

**Panel DNS:** https://hpanel.hostinger.com/domain/jobrithm.net/dns

| Tipo      | Name | Points to / Content | TTL   | Propósito                                   |
| --------- | ---- | ------------------- | ----- | ------------------------------------------- |
| **A**     | @    | <IP-VPS>            | 14400 | Frontend principal                          |
| **A**     | api  | <IP-VPS>            | 14400 | API REST y Admin Django                     |
| **A**     | \*   | <IP-VPS>            | 14400 | Subdominios dinámicos de tenants (wildcard) |
| **CNAME** | www  | jobrithm.net        | 300   | Frontend (www)                              |
| **CAA**   | @    | (varios)            | 14400 | Certificados SSL                            |

**Nota:** El registro wildcard `*` permite que cualquier subdominio (ej: `tenant1.`jobrhythm.net`(legacy`jobrithm.net`)) resuelva a la IP del servidor.

### 2.2.2 Configuración de Certificados SSL

**Certificado Wildcard actual:** `*.`jobrhythm.net`(legacy`jobrithm.net`)

Este certificado cubre:

- ``jobrhythm.net` (legacy `jobrithm.net`)
- `www.`jobrhythm.net`(legacy`jobrithm.net`)
- `api.`jobrhythm.net`(legacy`jobrithm.net`)
- `*.`jobrhythm.net`(legacy`jobrithm.net`) (cualquier subdominio de tenant)

**Ubicación:** `/etc/letsencrypt/live/jobrithm.net/`

**Compatibilidad temporal:** se mantiene certificado/dominios de `chalanpro.net` durante transición y rollback controlado.

#### 2.2.2.1 Renovación wildcard automática (API DNS Hostinger)

Hostinger expone una **API** para gestionar DNS (documentación: [developers.hostinger.com](https://developers.hostinger.com)). Con un token de API se puede automatizar el desafío DNS y renovar el wildcard sin tocar el panel.

**Requisitos**

1. Token de API en Hostinger: hPanel → Perfil → [API](https://hpanel.hostinger.com/profile/api).
2. En el VPS (donde corre certbot), instalar el SDK y dejar el token disponible:

   ```bash
   sudo apt-get install -y python3.12-venv
   python3 -m venv /opt/chalanpro/.venv-hostinger
   /opt/chalanpro/.venv-hostinger/bin/pip install hostinger_api
   ```

   **Dependencia operativa requerida (obligatoria):**
   - El virtualenv `/opt/chalanpro/.venv-hostinger` debe existir y contener `hostinger_api`.
   - Los hooks `scripts/certbot_hostinger_auth.py` y `scripts/certbot_hostinger_cleanup.py` dependen de ese entorno para la validación DNS-01.
   - Sin este virtualenv, la renovación del wildcard de ``jobrhythm.net` (legacy `jobrithm.net`) fallará.

3. Scripts en el repo (en el VPS, típicamente en `scripts/`):
   - `certbot_hostinger_auth.py` — manual-auth-hook: añade el TXT `_acme-challenge` vía API.
   - `certbot_hostinger_cleanup.py` — manual-cleanup-hook: borra ese TXT tras la validación.
   - `renew_wildcard_certbot_auto.sh` — script histórico para `chalanpro.net`.
   - `renew_wildcard_certbot_auto_domain.sh` — script parametrizable por dominio/email (recomendado).

**Uso (renovación manual con API)**

```bash
HOSTINGER_API_TOKEN=$(cat /root/.hostinger-api-token) /opt/chalanpro/scripts/renew_wildcard_certbot_auto_domain.sh --domain jobrithm.net --email admin@jobrhythm.net
```

**Cron (renovación automática del wildcard)**

Si el token está en un archivo (p. ej. `/root/.hostinger-api-token`, `chmod 600`):

```bash
# Renovar wildcard de jobrithm.net el día 1 de cada mes a las 03:00 (cert válido ~90 días)
0 3 1 * * HOSTINGER_API_TOKEN=$(cat /root/.hostinger-api-token) /opt/chalanpro/scripts/renew_wildcard_certbot_auto_domain.sh --domain jobrithm.net --email admin@jobrhythm.net
```

O definir `HOSTINGER_API_TOKEN` en `/etc/environment` o en el cron y usar `sudo -E` en el script (el script ya usa `sudo -E certbot` para pasar el token a certbot y a los hooks).

### 2.2.3 Configuración de Tenant en Django

**Variables de Entorno (`envs/backend.env`):**

```bash
TENANT_BASE_DOMAIN=jobrhythm.net
ALLOWED_HOSTS="chalanpro.net,*.chalanpro.net,...,jobrithm.net,*.jobrithm.net,...,jobrhythm.net,*.jobrhythm.net,www.jobrhythm.net,api.jobrhythm.net,...,<IP-VPS>,localhost,127.0.0.1"
CSRF_TRUSTED_ORIGINS=...,https://jobrithm.net,...,https://jobrhythm.net,...,https://*.jobrhythm.net
EMAIL_DEFAULT_FROM=noreply@jobrhythm.net
LANDING_CONTACT_TO_EMAIL=team@jobrhythm.net
```

**Configuración en `project/settings.py`:**

```python
TENANT_BASE_DOMAIN = os.environ.get('TENANT_BASE_DOMAIN', 'jobrhythm.net')
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
  --password '<contraseña-segura>'
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

**Migraciones multi-tenant (`migrate_schemas`):** Conviene ejecutar **`migrate_schemas`** en el servidor tras desplegar **cualquier cambio en modelos**, incluyendo migraciones sobre la app compartida **`tenants`** en el schema **public** (por ejemplo nuevas columnas en el modelo **Tenant**, como **`landing_selected_plan`**). Para migrar sólo **public** o un schema de empresa concreto: ver **§8.2 Gestión Django** (`migrate_schemas --schema public`, etc.), según la práctica habitual del equipo.

**URL de onboarding en producción (landing / CTAs):** `https://www.jobrithm.net/onboarding`. Parámetro opcional desde pricing: `?plan=starter`, `professional` o `enterprise` (debe coincidir con el onboarding / `planFromQuery.js`).

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

**Favicon (icono del sitio/ERP):** Si no se ve el favicon en el navegador, es porque no existe el archivo `favicon.ico` en la carpeta `app/vuefrontend/public/`. Para que aparezca: (1) colocar tu `favicon.ico` en `app/vuefrontend/public/`, (2) reconstruir el frontend (`docker compose up -d --build frontend`) y (3) reiniciar Nginx. El `index.html` ya referencia `<link rel="icon" href=".../favicon.ico">`; solo falta el archivo en `public/` para que el build lo copie a la raíz del sitio.

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

### 4.4 Desplegar Solo Landing (sin backend)

Para cambios exclusivamente de la landing (HTML/CSS/imagenes en `landing/`), usar el script dedicado:

```bash
sudo /opt/chalanpro/scripts/deploy-landing-vps.sh
```

**Flujo del script (`scripts/deploy-landing-vps.sh`):**

1. Actualiza código desde `origin/main` (fetch + checkout + pull `--ff-only`).
2. Reinicia solo `nginx` (no reconstruye `backend`/`frontend`, no migraciones).
3. Ejecuta smoke test HTTP(S) a la landing (`https://getjobrhythm.com` por defecto).

**Opciones útiles:**

```bash
# No hacer pull (usar código ya presente localmente)
sudo /opt/chalanpro/scripts/deploy-landing-vps.sh --no-pull

# Verificar otra URL de landing
sudo /opt/chalanpro/scripts/deploy-landing-vps.sh --url=https://www.getjobrhythm.com
```

**Cuándo usarlo:** cuando el commit trae solo cambios en `landing/src` y/o `landing/dist`.  
**Cuándo NO usarlo:** si hay cambios en backend, frontend SPA, modelos o migraciones.

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

## 5. Host y Credenciales PostgreSQL

> **Secretos:** contraseña y URL completas en `envs/postgres.env` (`POSTGRES_PASSWORD`, `POSTGRES_USER`) y `envs/backend.env` (`DATABASE_URL`). Ver [§6.6](#66-política-de-secretos-en-documentación).

### 5.1 Información de Conexión

| Parámetro              | Valor                                                   |
| ---------------------- | ------------------------------------------------------- |
| **Host**               | `localhost` / servicio Docker `postgres` (desde el VPS) |
| **Puerto**             | `5432`                                                  |
| **Base de Datos**      | `chalanpro`                                             |
| **Usuario**            | `chalanpro_user` (ver `envs/postgres.env`)              |
| **Contraseña**         | Ver `envs/postgres.env` → `POSTGRES_PASSWORD`           |
| **Schema por Defecto** | `public` (para gestión de tenants)                      |

### 5.2 Conexión desde el Servidor

```bash
# Usando psql (si está instalado en el host)
psql -h localhost -p 5432 -U chalanpro_user -d chalanpro

# Usando Docker
docker compose exec postgres psql -U chalanpro_user -d chalanpro
```

### 5.3 Conexión Externa (desde otra máquina)

**Requisitos:**

- Preferir **túnel SSH** (ver `DEVOPS.md`); evitar exponer PostgreSQL a Internet.
- Si aplica acceso externo: IP del VPS en hPanel → VPS (no documentar aquí).

```bash
# Túnel SSH (recomendado) — host según tu ~/.ssh/config
ssh -L 5432:127.0.0.1:5432 <alias-vps>
psql -h localhost -p 5432 -U chalanpro_user -d chalanpro
```

### 5.4 Conexión desde pgAdmin

**URL:** puerto `5050` del VPS (mapear solo si es imprescindible; preferir túnel SSH).

**Credenciales pgAdmin:** ver `envs/pgadmin.env` (`PGADMIN_DEFAULT_EMAIL`, `PGADMIN_DEFAULT_PASSWORD`).

**Configuración del servidor en pgAdmin:**

- **Name:** Chalan-Pro Production
- **Host:** `postgres` (nombre del servicio Docker) o `172.x.x.x` (IP del contenedor)
- **Port:** `5432`
- **Maintenance database:** `chalanpro`
- **Username:** `chalanpro_user` (ver `envs/postgres.env`)
- **Password:** ver `envs/postgres.env` → `POSTGRES_PASSWORD`

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
   - ~~Limitar requests por IP en Nginx~~ ✅ Implementado en onboarding (ver [6.5](#65-remediación-de-seguridad--onboarding-público))
   - ~~Proteger endpoints de API contra abuso~~ ✅ Throttling DRF + CAPTCHA + verificación de email

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
- [x] Rate limiting en onboarding (DRF + Nginx + CAPTCHA + verificación email — ver [6.5](#65-remediación-de-seguridad--onboarding-público))

### 6.5 Remediación de seguridad — Onboarding público

**Hallazgo auditado:** onboarding público (`POST /api/onboarding/`) permitía creación ilimitada de tenants sin rate limit (severidad **High**).  
**Fecha de remediación:** 2025-06-02.  
**Archivos principales:** `app/tenants/throttles.py`, `app/tenants/views.py`, `app/tenants/services/`, `nginx/default.conf`, `nginx/default.dev.conf`, frontend onboarding (`TurnstileWidget.vue`, `OnboardingVerifyView.vue`).

#### Remediation Applied

##### 1. DRF throttling (capa aplicación)

Throttling de Django REST Framework en el endpoint público de onboarding:

| Scope                                 | Límite por defecto | Variable de entorno             |
| ------------------------------------- | ------------------ | ------------------------------- |
| IP (`onboarding_create_ip`)           | 5 POST/hora        | `ONBOARDING_THROTTLE_IP`        |
| Email (`onboarding_create_email`)     | 3 POST/día         | `ONBOARDING_THROTTLE_EMAIL`     |
| Verificación (`onboarding_verify_ip`) | 20 POST/hora       | `ONBOARDING_VERIFY_THROTTLE_IP` |

- Clases: `OnboardingCreateIPThrottle`, `OnboardingCreateEmailThrottle`, `OnboardingVerifyIPThrottle` (`app/tenants/throttles.py`).
- Respuesta ante exceso: **HTTP 429** antes de ejecutar lógica pesada (sin crear schema).
- La IP se toma de `X-Forwarded-For` (Nginx como reverse proxy).
- Auditoría: log `onboarding_rate_limited scope=... ip=...`.

Configuración en `app/project/settings.py` → `REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']`.

##### 2. Nginx `limit_req` (capa borde)

Protección adicional en Nginx para rutas de creación de tenant (filtro grueso anti-ráfaga):

```nginx
# nginx/default.conf y nginx/default.dev.conf (contexto http)
limit_req_zone $binary_remote_addr zone=onboarding_create:10m rate=1r/m;
limit_req_status 429;

# Location específica (antes del location /api/ genérico)
location ~ ^/api/onboarding(/create-tenant/)?$ {
    limit_req zone=onboarding_create burst=0 nodelay;
    proxy_pass http://backend:8000;
    ...
}
```

- **Nota:** Nginx solo admite `r/s` y `r/m` (no `r/h`); `1r/m` complementa el throttling fino de DRF (`5/hour`).
- Aplica en bloques que proxyan `/api/onboarding/` hacia el backend (`api.jobrhythm.net`, `jobrhythm.net`, subdominios `*.jobrhythm.net`).
- Tras cambiar Nginx en VPS: `docker compose restart nginx`.

##### 3. CAPTCHA — Cloudflare Turnstile

Verificación server-side antes de aceptar una solicitud de onboarding:

| Componente                | Ubicación                                                       |
| ------------------------- | --------------------------------------------------------------- |
| Verificación backend      | `app/tenants/services/captcha.py`                               |
| Widget frontend           | `app/vuefrontend/src/components/onboarding/TurnstileWidget.vue` |
| Config pública (site key) | `GET /api/onboarding/config/`                                   |

**Cómo obtener las claves Turnstile**

1. Entrar en [Cloudflare Dashboard](https://dash.cloudflare.com/) → **Turnstile**.
2. **Add site** → nombre (ej. `JobRhythm Onboarding`), dominios (`jobrhythm.net`, `getjobrhythm.com`, `localhost` en dev).
3. Elegir widget (recomendado: **Managed**).
4. Copiar **Site Key** (pública, va al frontend vía API) y **Secret Key** (solo backend).

**Configuración en el VPS** (`envs/backend.env` o variables del contenedor backend):

```bash
TURNSTILE_SITE_KEY=<site-key-de-cloudflare>
TURNSTILE_SECRET_KEY=<secret-key-de-cloudflare>
```

**Desarrollo local** (`envs/backend.dev.env`) — claves de prueba de Cloudflare (siempre pasan):

```bash
TURNSTILE_SITE_KEY=1x00000000000000000000AA
TURNSTILE_SECRET_KEY=1x0000000000000000000000000000000AA
```

- El frontend obtiene la site key con `GET /api/onboarding/config/` al cargar el wizard.
- El token se envía en `POST /api/onboarding/` como `turnstile_token` / `cf_turnstile_response`.
- Si `TURNSTILE_SECRET_KEY` no está configurada y `DEBUG=True`, el backend omite la verificación (solo desarrollo).

##### 4. Verificación de email antes de crear el schema

Flujo en **dos pasos** — el schema PostgreSQL y las migraciones **no** se ejecutan hasta confirmar el email:

| Paso | Endpoint                       | Acción                                                                                   |
| ---- | ------------------------------ | ---------------------------------------------------------------------------------------- |
| 1    | `POST /api/onboarding/`        | Valida datos + CAPTCHA → guarda `OnboardingPendingRegistration` → envía email con enlace |
| 2    | `POST /api/onboarding/verify/` | Valida token UUID → provisiona tenant (schema, dominio, migraciones, admin)              |

- Modelo: `OnboardingPendingRegistration` (schema `public`, migración `tenants.0006`).
- Enlace del email: `{FRONT_URL}/onboarding/verify?token=<uuid>` (vista `OnboardingVerifyView.vue`).
- Expiración del token: `ONBOARDING_VERIFY_EXPIRY_HOURS` (default **24** horas).
- Requiere SMTP configurado (`EMAIL_HOST_PASSWORD`) en producción.
- En `DEBUG` sin SMTP, la API devuelve `debug_verify_url` para pruebas locales.

**Variables relacionadas:**

```bash
ONBOARDING_VERIFY_EXPIRY_HOURS=24
FRONT_URL=https://jobrhythm.net   # base del enlace de verificación
```

**Despliegue tras este cambio:**

```bash
# VPS — schema public (modelo pending)
docker compose exec backend python manage.py migrate_schemas --shared

docker compose restart backend nginx
# Rebuild frontend si cambió el wizard / verify view
```

#### Security Impact

| Riesgo mitigado                         | Antes                   | Después                                         |
| --------------------------------------- | ----------------------- | ----------------------------------------------- |
| Creación masiva automatizada de tenants | Ilimitada por IP/email  | Limitada (DRF + Nginx)                          |
| Abuso de CPU/DB/disco por migraciones   | Cada POST creaba schema | Schema solo tras verificar email                |
| Squatting de subdominios                | Posible en volumen      | Coste por intento (CAPTCHA + email + throttles) |
| Bots en formulario público              | Sin fricción            | Turnstile + verificación de buzón               |

**Reducción de severidad:** finding **High** → **mitigado** en la capa de abuso automatizado del onboarding.

#### Potential Side Effects

1. **NAT / oficina compartida:** varios registros legítimos desde la misma IP pública pueden recibir **429** (ajustar `ONBOARDING_THROTTLE_IP` si hace falta).
2. **Nginx `1r/m`:** un segundo `POST /api/onboarding/` en menos de 1 minuto desde la misma IP puede ser rechazado en el borde (antes de llegar a Django).
3. **Cache DRF por worker:** con varios workers Daphne, el límite efectivo por IP puede ser mayor por proceso; Nginx compensa en producción.
4. **Verificación de email obligatoria:** el usuario debe abrir el enlace del correo; sin SMTP en producción el onboarding no completa el flujo.
5. **`FRONT_URL` incorrecto:** el enlace del email apuntará al host equivocado — verificar en `envs/backend.env` del VPS.
6. **Turnstile en producción:** sin claves reales de Cloudflare, el CAPTCHA fallará (`TURNSTILE_SITE_KEY` / `TURNSTILE_SECRET_KEY` obligatorias con `DEBUG=False`).

### 6.6 Política de secretos en documentación

**Regla:** este repositorio **no** debe contener contraseñas, claves API, tokens ni valores que permitan acceso a producción. La documentación solo nombra **variables** y **rutas** bajo `envs/` (archivos reales en `.gitignore`; plantillas en `*.example.env`).

| Tipo de secreto             | Dónde configurarlo                                         | No documentar en markdown                             |
| --------------------------- | ---------------------------------------------------------- | ----------------------------------------------------- |
| PostgreSQL                  | `envs/postgres.env` → `POSTGRES_PASSWORD`, `POSTGRES_USER` | Contraseñas, URLs con password embebida               |
| Django / DB URL             | `envs/backend.env` → `DATABASE_URL`, `DJANGO_SECRET_KEY`   | Secret key, connection strings completos              |
| Admin Django                | `createsuperuser` en VPS o gestión interna                 | Usuario/contraseña de superuser                       |
| pgAdmin                     | `envs/pgadmin.env`                                         | Email/contraseña de pgAdmin                           |
| SMTP / onboarding           | `envs/backend.env` → `EMAIL_*`                             | Contraseñas de buzón                                  |
| Stripe                      | `envs/backend.env` → `STRIPE_*`                            | Cualquier `sk_…`, `pk_…`, `whsec_…` real o de ejemplo |
| Turnstile                   | `envs/backend.env` → `TURNSTILE_*`                         | Secret key (site key pública solo vía API config)     |
| Hostinger API (certbot DNS) | `/root/.hostinger-api-token` en el VPS (`chmod 600`)       | Token en Git o markdown                               |
| IP / SSH del VPS            | hPanel → VPS → detalles; alias en `~/.ssh/config`          | IP fija repetida como credencial; contraseñas SSH     |

En tablas DNS de este documento, `<IP-VPS>` significa la IP pública actual del VPS en Hostinger (consultar panel, no commitear si cambia de servidor).

---

## 7. URLs del Sistema

### 7.1 URLs de Producción

| Servicio               | URL                                                | Descripción                      |
| ---------------------- | -------------------------------------------------- | -------------------------------- |
| **Frontend Principal** | `https://jobrhythm.net`                            | Frontend Vue.js (público)        |
| **Frontend (www)**     | `https://www.jobrhythm.net`                        | Frontend Vue.js (www)            |
| **Onboarding**         | `https://www.jobrhythm.net/onboarding`             | Formulario de creación de tenant |
| **API REST**           | `https://api.jobrhythm.net/api/`                   | API REST de Django               |
| **Admin Django**       | `https://api.jobrhythm.net/admin/`                 | Panel de administración          |
| **Tenant Login**       | `https://{tenant}.jobrhythm.net/login/`            | Login de tenant específico       |
| **Landing**            | `https://getjobrhythm.com`                         | Web de marketing                 |
| **pgAdmin**            | Túnel SSH → puerto `5050` (ver `envs/pgadmin.env`) | Interfaz web de PostgreSQL       |

**Ejemplo tenant Phoenix (schema `phoenix_electric_and_air_llc`):**

| URL                                    | Uso                                                |
| -------------------------------------- | -------------------------------------------------- |
| `https://phoenix.jobrhythm.net/`       | Dominio primario SaaS (producción)                 |
| `https://phoenix.jobrhythm.net/login/` | Login del tenant                                   |
| `https://phoenix.jobrithm.net/`        | Legacy → 301 a `phoenix.jobrhythm.net` (Nginx VPS) |

### 7.2 Dominios legacy y redirecciones 301

Los dominios antiguos **no sirven la aplicación**; Nginx en el VPS (`nginx/legacy-redirects.conf`) responde solo con **301** hacia JobRhythm:

| Origen (inhabilitado)                            | Destino                        |
| ------------------------------------------------ | ------------------------------ |
| `getjobrithm.com`, `www`                         | `getjobrhythm.com`             |
| `jobrithm.net`, `www`, `api`, `*.jobrithm.net`   | equivalente en `jobrhythm.net` |
| `chalanpro.net`, `www`, `api`, `*.chalanpro.net` | equivalente en `jobrhythm.net` |
| `chalanpro.com`, `www`                           | `getjobrhythm.com`             |

Verificación rápida:

```bash
curl -sI https://getjobrithm.com/ | grep -i location
# location: https://getjobrhythm.com/

curl -sI https://phoenix.jobrithm.net/login/ | grep -i location
# location: https://phoenix.jobrhythm.net/login/
```

### 7.3 Dominios personalizados de clientes (fuera de `*.jobrhythm.net`)

Algunos clientes conservan un **dominio propio** (registro/DNS en otro proveedor) que debe terminar en su subdominio JobRhythm.

**Caso verificado: Phoenix Electric and Air — `phoenixelectricandair.net`**

| Comprobación                    | Resultado (2026-05-25)                                                                                                                           |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| DNS `phoenixelectricandair.net` | `160.153.175.22` (no apunta al VPS JobRhythm `<IP-VPS>`)                                                                                         |
| Cadena HTTPS completa           | **Sí llega a** `https://phoenix.jobrhythm.net/` con **200**                                                                                      |
| Paso 1                          | `https://phoenixelectricandair.net/` → **301** → `https://phoenix.jobrithm.net/` (redirección configurada en el hosting del dominio del cliente) |
| Paso 2                          | `https://phoenix.jobrithm.net/` → **301** → `https://phoenix.jobrhythm.net/` (Nginx legacy en VPS)                                               |
| Destino final                   | `https://phoenix.jobrhythm.net/` — tenant `phoenix_electric_and_air_llc`, dominio primario en BD: `phoenix.jobrhythm.net`                        |

```bash
curl -sI -L -o /dev/null -w "%{url_effective}\n" https://phoenixelectricandair.net/
# https://phoenix.jobrhythm.net/
```

**Recomendación (un solo salto 301):** en el panel DNS del dominio del cliente, apuntar `phoenixelectricandair.net` (y `www`) con registro **A** a `<IP-VPS>` y añadir en el VPS un bloque Nginx que haga `return 301 https://phoenix.jobrhythm.net$request_uri;` (requiere certificado SSL para ese host, p. ej. certbot). Mientras el DNS siga en otra IP, el primer 301 seguirá gestionándose fuera del VPS.

### 7.4 Credenciales de Acceso

> **Política:** no documentar contraseñas en markdown. Usar solo `envs/` en el VPS (ver [§6.6](#66-política-de-secretos-en-documentación)).

**Admin Django:**

- **URL:** `https://api.jobrhythm.net/admin/`
- **Usuario / contraseña:** gestionar en el VPS (`createsuperuser` o variables en `envs/backend.env` si aplica)

**pgAdmin:**

- **Acceso:** puerto `5050` (restringir por firewall o túnel SSH)
- **Credenciales:** `envs/pgadmin.env`

### 7.5 Post-migración JobRhythm

Checklist:

- [x] Redirecciones 301 Nginx: dominios legacy → `jobrhythm.net` / `getjobrhythm.com` (`nginx/legacy-redirects.conf`).
- [x] Wildcard SSL `*.jobrhythm.net` (`/etc/letsencrypt/live/jobrhythm.net-0001/`).
- [x] `TENANT_BASE_DOMAIN=jobrhythm.net` en `envs/backend.env` (recrear backend tras cambiar env: `docker compose up -d --force-recreate backend`).
- [ ] Confirmar operación estable en producción (login tenants, onboarding, API, correo).
- [ ] Opcional: DNS de dominios de cliente (ej. `phoenixelectricandair.net`) → VPS para un único 301 directo a `*.jobrhythm.net`.
- [ ] Renovar wildcard: `renew_wildcard_certbot_auto_domain.sh --domain jobrhythm.net` (cron + `/root/.hostinger-api-token`).

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

### 9.6 Workflow: Serialized Items e Inventory Transfers

Reseña de las funcionalidades de **ítems serializados** y **transferencias entre almacenes** y cómo se usan en el flujo operativo.

#### Serialized Items (ítems con número de serie)

- **Objetivo:** Registrar equipos o productos que se rastrean por unidad (número de serie / asset tag), no solo por cantidad.
- **Configuración previa:**
  - En **Inventario → Productos**, el producto debe tener **Tracking mode = Serialized**.
  - En **Transacciones → Tipos de documento** (`/document-types`), el tipo que recibe la mercancía (p. ej. **GRN – Goods Receipt Note**) debe tener activo **"Creates Serialized Items"** y **Stock Movement = +1 Entry**.
- **Flujo típico (compra/entrada):**
  1. Se crea un documento del tipo configurado (ej. GRN) con líneas que incluyen productos SERIALIZED y cantidad.
  2. Al guardar, el sistema crea registros **SerializedItem** por cada unidad y abre el modal **Assign Serial Numbers** para asignar número de serie (y opcionalmente condición, notas).
  3. El usuario puede completar los seriales en ese momento o cerrar el modal y usar después el botón **"Assign Serial Numbers"** en la grilla de líneas del mismo documento (solo visible si el tipo tiene `creates_serialized_items`).
- **Dónde se usa:** Lista de ítems serializados, asignación de tags desde el documento de compra/entrada y seguimiento por almacén y documento de origen.

#### Inventory Transfers (transferencias entre almacenes)

- **Objetivo:** Mover stock (y, cuando aplique, ítems serializados) entre dos almacenes, generando movimientos de salida en origen y entrada en destino.
- **Flujo:**
  1. Desde el menú de inventario se accede a **Inventory Transfers** (o equivalente según la navegación del tenant).
  2. Se crea una transferencia indicando **almacén origen**, **almacén destino**, descripción opcional y las líneas (producto, cantidad y, si el producto es SERIALIZED, qué unidades/seriales se mueven).
  3. Al confirmar, el sistema registra movimientos de inventario (y actualiza `SerializedItem.current_warehouse` cuando corresponde) y el estado de la transferencia queda **Completed** (o **Reverted** si se revierte).
- **API:** CRUD en `/api/inventory-transfers/`; existe además un endpoint de listado para proveedores de datos (`/api/inventory-transfers-provider/`).

En conjunto, **Serialized Items** cubre el registro y trazabilidad por unidad en entradas (p. ej. GRN), y **Inventory Transfers** permite reubicar stock y ítems serializados entre almacenes de forma controlada.

<a id="97-precios-lineas-documento"></a>

### 9.7 Cálculo dinámico de precios en líneas de documento

Esta sección resume **cómo se obtiene y recalcula el precio unitario** en el formulario de transacciones, las **condiciones** de cada camino y **qué endpoints** intervienen. La lógica interactiva vive sobre todo en **`vuefrontend/src/components/transactions/LinesGrid.vue`**, dentro de **`TransactionForm.vue`**; el tipo de documento aporta `is_sales` (venta) y el id del tipo (`document_type_id`).

#### 9.7.1 Modelo de datos relevante (`PriceType` y líneas)

- **`PriceType`** (`appinventory.models`): campo **`pricing_method`** — valores típicos `NONE` (sin precio automático desde costo), **`MARKUP`** o **`MARGIN`**; y **`margin_percent`** (porcentaje 0–100 cuando el método es markup o margen). En validación del modelo, markup/margin requieren porcentaje; margen no puede ser ≥ 100 %.
- En la línea del documento, el frontend lleva **`unit_price`**, **`price_type`**, **`margin_percent`**, **`pricing_rule`** (p. ej. reflejo del método o manualidad), **`price_manually_edited`** y **`_purchase_unit_cost`** (costo por unidad de compra resuelto vía API, no necesariamente persistido igual en backend al guardar).

#### 9.7.2 API: costo de compra (`purchase-cost`)

- **Vista:** `ProductPurchaseCostAPIView` en `appinventory/views.py`.
- **`GET /api/products/<product_id>/purchase-cost/?unit=<unit_id>`** (el parámetro `unit` es opcional).
- Usa **`_purchase_unit_cost_for_product`**: toma registros **`ProductPrice`** con **`is_purchase=True`** y **`is_active=True`**; si se indica **`unit_id`**, prioriza la fila con esa unidad; si no hay coincidencia, devuelve el **primer** precio de compra por `id`.
- **Respuesta:** `unit_cost` (float o `null`) y `unit_id` (unidad con la que se resolvió el costo).

Sirve para alimentar **`_purchase_unit_cost`** en la grilla al cambiar **unidad**, **producto** o **tipo de precio**, antes de aplicar markup/margen sobre el costo.

#### 9.7.3 API: precio predeterminado de catálogo (`default-price`)

- **Vista:** `ProductDefaultPriceAPIView` en `appinventory/views.py`.
- **`GET /api/products/<product_id>/default-price/`** con query params opcionales como **`brand_id`**, **`document_type_id`**.
- Con **`document_type_id`**:
  - Si el tipo es **compra** (`is_purchase`): primer **`ProductPrice`** de compra activo.
  - Si el tipo es **venta** (`is_sales`): precio de venta con **`is_default=True`**; si no existe, primer precio de venta activo.
- **Fallback:** precio con `is_default=True`, luego cualquier precio activo.
- La respuesta incluye **`unit`**, **`unit_price`**, **`price_type`**, datos de marca y **`purchase_unit_cost`** (derivado del costo de compra para la unidad del precio elegido vía `_purchase_unit_cost_for_product`).
- **`unit` como query parameter:** La vista **`ProductDefaultPriceAPIView`** (en la versión descrita aquí) **no utiliza `unit`** en la cadena de consulta para elegir el registro `ProductPrice`. El SPA (`LinesGrid.vue`) puede añadir `unit` igualmente en la URL; ese valor es **transparente para el servidor** hasta que exista soporte explícito. La unidad del JSON de respuesta es la del **`ProductPrice` seleccionado** por tipo de documento y fallbacks del apartado anterior.

#### 9.7.4 Documentos de venta (`is_sales`) vs otros

| Aspecto                                                       | Documento de venta (`is_sales`)                                 | No venta                                                                             |
| ------------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Columna **Margin %** en grilla                                | Visible y editable según permisos                               | Oculta; no participa en la UX de margen/markup automático desde costo como en ventas |
| Auto-precio desde **costo + PriceType** (`MARKUP` / `MARGIN`) | Activo cuando se cumplen las condiciones del apartado siguiente | No aplica ese flujo desde costo en el mismo modo “venta”                             |
| Sugerencias / hints de pricing                                | Pueden mostrarse (margen/markup/manual)                         | No orientadas al margen de venta desde costo                                         |

#### 9.7.5 Cuándo el precio unitario sale del **costo de compra** (ventas)

En el frontend, una función de **auto-pricing desde costo** solo recalcula **`unit_price`** si **todas** estas condiciones se cumplen (resumen conceptual):

1. El documento es de **venta** (`documentTypeIsSales`).
2. Hay **producto**, **unidad** y **tipo de precio** en la línea.
3. El **`PriceType`** elegido tiene **`pricing_method`** **`MARKUP`** o **`MARGIN`** (no `NONE`).
4. Existe **`_purchase_unit_cost`** **> 0** (tras `purchase-cost`, o información traída por `default-price` cuando aplique).
5. Hay porcentaje usable: **`margin_percent`** en la línea o el **`margin_percent`** del tipo de precio.
6. El usuario **no** dejó la línea en modo **precio editado manualmente** (`price_manually_edited`); la regla de negocio en UI evita sobrescribir un precio que el usuario fijó a mano.

**Fórmulas (mismo criterio que en la UI):** sobre costo **`c`** y porcentaje **`p`**: **markup:** precio ≈ **`c × (1 + p/100)`**; **margen:** precio ≈ **`c / (1 − p/100)`** (con `p < 100`).

Al **cambiar tipo de precio**, el cliente puede **sincronizar** `margin_percent` y `pricing_rule` desde la opción del desplegable (`priceTypesOptions`: `pricing_method`, `margin_percent`).

#### 9.7.6 Cuándo se usa **precio de catálogo** (`default-price`)

Si **no** se cumple la cadena del apartado 9.7.5 (por ejemplo método `NONE`, costo ausente o cero, o sin MARKUP/MARGIN), el SPA hace **`GET default-price`** típicamente con **`document_type_id`** (y parámetros que el backend sí interpreta, p. ej. **`brand_id`**) para rellenar **`unit_price`** y, si viene en la respuesta, **`purchase_unit_cost`**. Tras cambiar la **unidad** en pantalla puede seguir llamando a este endpoint incluyendo `unit` en la query por coherencia con otras llamadas, pero **el precio devuelto no se filtra aún por esa unidad en el servidor** (ver 9.7.3). Esto cubre: selección inicial de producto, cambio de **unidad** o **tipo de precio** cuando el precio **no** sale del bloque «costo + margen/markup».

#### 9.7.7 Coherencia de **cantidad**, **descuento** y totales de línea

- **Cantidad (`Qty`):** no debe cambiar el **precio unitario** por sí sola; solo el **importe de línea** y los totales del documento (**subtotal**, **descuento**, **total**), que el formulario agrega en base a **`final_price`** (o equivalente) por línea.
- **Porcentaje de descuento (`Disc %`):** recalcula el importe de línea manteniendo el precio unitario (salvo decisiones posteriores del usuario sobre el campo precio).
- **Importe de línea después de descuento (referencia frontend):** en esencia **`cantidad × unit_price × (1 − Disc%/100)`** (con el descuento acotado a 0–100 % donde la UI lo aplica).

#### 9.7.8 **Margin %** y modo manual

- Si **`pricing_rule`** (o la lógica asociada) indica precio **manual**, al editar solo **Margen %** no se debe sobreescribir el **precio unitario** automáticamente; igualmente se actualizan **totales de línea** donde corresponda.
- Si **no** es manual y el método del tipo de precio es markup/margen, al cambiar **Margen %** se puede volver a derivar **`unit_price`** desde **`_purchase_unit_cost`** y luego recalcular la línea.

#### 9.7.9 Aclaración: `ProductPrice` (`is_purchase` / `is_sale`) y método del tipo de precio

- **Si el `PriceType` usa `MARKUP` o `MARGIN`:** en documentos de venta, el **costo unitario de compra** que alimenta la fórmula proviene de filas **`appinventory_productprice`** con **`is_purchase=True`** (activas; el API `purchase-cost` prioriza la unidad de la línea cuando aplica). Sobre ese costo se aplica markup o margen para obtener el **precio de venta** de la línea.
- **Si el método es `NONE` (“list price only”):** no significa que el sistema “no use” precios de venta en `ProductPrice`. Significa que **no** se calcula el precio de venta con la fórmula desde el costo de compra. El precio de lista / catálogo sigue apoyándose en filas de **venta**, típicamente **`is_sale=True`** (p. ej. elección en `default-price`: predeterminado de venta y fallbacks), distinto del camino “costo `is_purchase` + fórmula”.

La guía en pantalla para administradores del tipo de precio está en **`vuefrontend/src/components/inventory/PriceTypePricingGuide.vue`**.

---

## 10. Billing (Stripe SaaS — `appbilling`)

Monetización SaaS con **Stripe Checkout**, **Customer Portal** y webhooks. La app Django vive en **`app/appbilling/`** (schema **public**, `SHARED_APPS`), al mismo nivel que `appinventory`, `apptransactions`, etc.

**Dominio producción:** `jobrhythm.net` · **API:** `https://api.jobrhythm.net` · **Webhook Stripe:** `https://api.jobrhythm.net/stripe/webhook/`

### 10.1 Arquitectura y schema

| Capa                                           | Ubicación                                                                        |
| ---------------------------------------------- | -------------------------------------------------------------------------------- |
| Modelos `Plan`, `Subscription`, `PaymentEvent` | Schema **public** (`appbilling`)                                                 |
| Campos trial en `tenants.Tenant`               | `trial_start`, `trial_end`, `on_trial`, `paid_until`                             |
| Datos operativos (crews, contratos, etc.)      | Schema por tenant                                                                |
| Stripe Customer                                | Se crea en la **primera visita a Billing** (checkout o portal), no en onboarding |

Las tablas en PostgreSQL conservan el prefijo histórico **`billing_*`** (`billing_plan`, `billing_subscription`, `billing_paymentevent`) mediante `db_table` en los modelos.

### 10.2 Modelos y planes

Planes sembrados con `seed_plans` (precios alineados con [getjobrhythm.com/pricing.html](https://getjobrhythm.com/pricing.html)):

| Slug           | Mensual | Anual (−15 %) | `max_crews` | `max_users`      |
| -------------- | ------- | ------------- | ----------- | ---------------- |
| `starter`      | $436    | $4,447        | 3           | 1                |
| `professional` | $877    | $8,945        | 10          | 10 (recomendado) |
| `enterprise`   | $1,758  | $17,931       | ilimitado   | ilimitado        |

El plan sugerido al upgrade viene de `landing_selected_plan` / `recommended_plan` del onboarding.

### 10.3 Endpoints API

| Método | Ruta                                           | Auth         | Descripción                                                   |
| ------ | ---------------------------------------------- | ------------ | ------------------------------------------------------------- |
| GET    | `/api/billing/status/`                         | Token        | Estado trial/suscripción, plan sugerido                       |
| GET    | `/api/billing/public-plans/`                   | Público      | Catálogo activo (landing, sin auth)                           |
| GET    | `/api/billing/plans/`                          | Token        | Mismo catálogo (app `/billing`)                               |
| POST   | `/api/billing/create-checkout-session/`        | Token        | Body: `plan_slug`, `billing_interval` (`monthly` \| `yearly`) |
| POST   | `/api/billing/create-customer-portal-session/` | Token        | URL portal Stripe                                             |
| POST   | `/stripe/webhook/`                             | Firma Stripe | Sincroniza suscripciones e invoices                           |

Los **price IDs** de Stripe solo se resuelven en backend (modelo `Plan`), nunca desde el frontend.

### 10.4 Trial, acceso workspace y límites de cuadrillas

**Fuente de verdad:** `tenants.services.access.get_tenant_access(tenant)` — orden: `is_active` → billing (`get_billing_access`).

| Condición                | `access_allowed` | `access_reason`                         | HTTP API | Pantalla SPA          |
| ------------------------ | ---------------- | --------------------------------------- | -------- | --------------------- |
| `is_active=false`        | false            | `tenant_inactive`                       | **403**  | `/account-suspended`  |
| Trial OK o Stripe OK     | true             | `trial` / `active` / …                  | —        | App normal            |
| Trial vencido / sin pago | false            | `trial_expired` / `no_subscription` / … | **402**  | `/billing?reason=...` |

- **Trial:** 30 días desde onboarding (`start_trial_for_tenant`). Requiere `on_trial=true` y `now < trial_end`.
- **Enforcement:** `tenants.middleware.TenantAccessEnforcementMiddleware` (schema tenant, no public):
  - `/api/*` → 403 o 402 (exentas: billing, login, logout, validate-token, user_detail, …)
  - **`/admin/*`** → HTML 403 (bloquea login y todo el admin del tenant si trial venció o workspace inactivo)
- **Login:** `assert_login_allowed` — solo bloquea `tenant_inactive`; billing vencido permite token → guard manda a `/billing`.
- **Grace `past_due`:** 7 días (`BILLING_PAST_DUE_GRACE_DAYS`).
- **Cuadrillas:** `crewsapp` → `appbilling.services.crews.validate_crew_create`.
- **Frontend:** guard Vue (`tenant_active` primero), interceptor axios 403/402, rutas `/billing`, `/account-suspended`.

Admin **public** (`api.jobrhythm.net/admin`) no se ve afectado.

### 10.5 Variables de entorno Stripe

Definir **solo** en `envs/backend.env` del VPS (plantilla: `envs/backend.dev.example.env`). **No** pegar claves reales en markdown ni en Git.

| Variable                                   | Descripción                                                  |
| ------------------------------------------ | ------------------------------------------------------------ |
| `STRIPE_SECRET_KEY`                        | Clave secreta Stripe (Dashboard → Developers → API keys)     |
| `STRIPE_PUBLISHABLE_KEY`                   | Clave publicable (frontend / Checkout)                       |
| `STRIPE_WEBHOOK_SECRET`                    | Secreto del endpoint webhook (`whsec_…` en Stripe Dashboard) |
| `STRIPE_SUCCESS_URL`                       | URL post-checkout (opcional)                                 |
| `STRIPE_CANCEL_URL`                        | URL cancelación checkout                                     |
| `STRIPE_CUSTOMER_PORTAL_RETURN_URL`        | Return URL del portal de cliente                             |
| `BILLING_PAST_DUE_GRACE_DAYS`              | Días de gracia en `past_due` (default `7`)                   |
| `BILLING_ENFORCEMENT_ENABLED`              | Activar enforcement de billing                               |
| `STRIPE_*_PRODUCT_ID` / `STRIPE_*_PRICE_*` | IDs de productos/precios por plan (`seed_plans`)             |

```bash
# Ejemplo de nombres en envs/backend.env — valores reales solo en el servidor
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
```

Correos transaccionales de trial: `DEFAULT_FROM_EMAIL=noreply@jobrhythm.net`.

### 10.6 Comandos de gestión

```bash
# Migraciones (schema public)
docker compose exec backend python manage.py migrate_schemas --shared

# Planes + Stripe IDs desde env
docker compose exec backend python manage.py seed_plans

# Trial dates en tenants existentes
docker compose exec backend python manage.py backfill_trial_dates

# Recordatorios trial (cron diario en VPS)
docker compose exec backend python manage.py send_trial_reminders
docker compose exec backend python manage.py send_trial_reminders --dry-run
```

**Admin Django (schema public):** ver [§10.8](#108-django-admin-solo-schema-public). Para el cliente legacy, ajustar manualmente `trial_end` y/o `Subscription`.

**Migración app `billing` → `appbilling` (solo si el VPS tenía la app antigua):**

```sql
UPDATE django_migrations SET app = 'appbilling' WHERE app = 'billing';
```

Luego `migrate_schemas --shared` para aplicar `appbilling.0002_rename_app_label_tables`.

### 10.7 Frontend y despliegue

| Archivo                                        | Rol                         |
| ---------------------------------------------- | --------------------------- |
| `vuefrontend/src/views/BillingPage.vue`        | UI planes, checkout, portal |
| `vuefrontend/src/views/BillingSuccessView.vue` | Retorno post-Stripe         |
| `vuefrontend/src/api/billing.js`               | Cliente API                 |
| `vuefrontend/src/router/index.js`              | Rutas + guard suscripción   |

Tras desplegar backend con cambios en `appbilling` o `tenants`: **`migrate_schemas --shared`**, **`seed_plans`**, configurar webhook en Stripe Dashboard apuntando a `https://api.jobrhythm.net/stripe/webhook/`.

**Precios en landing y app:** una sola fuente en el modelo `Plan` (admin o `seed_plans`). La landing (`pricing.html` / `pricing-en.html`) consume `GET /api/billing/public-plans/` vía `landing/src/js/pricing-plans.js` (mismo payload que `appbilling.catalog.list_active_plans`). En **getjobrhythm.com** la petición es **same-origin** (`/api/billing/public-plans/`) gracias al proxy en `nginx/default.conf` (bloque landing). En **local** (`npm start`, IP `192.168.x.x`) el script llama a `http://api.chalanpro.net:8000/api/billing/public-plans/` (requiere entrada en `hosts` y backend levantado). Tras cambiar precios en admin: `cd landing && npm run build` y desplegar `dist/`. En VPS también hace falta **pull** del backend (el endpoint devuelve 404 si el código no está desplegado).

### 10.8 Django admin: solo schema public

Las apps en **`SHARED_APPS`** (`tenants`, `appbilling`) registran modelos en el admin de Django. Sin restricción adicional, esos módulos también aparecen cuando un superusuario entra a `/admin/` desde el **subdominio de un cliente** (p. ej. `phoenix.jobrhythm.net`), lo cual no debe ocurrir.

**Solución compartida:** `PublicSchemaOnlyAdminMixin` en `app/project/admin_mixins.py`. Comprueba que `connection.schema_name` (o `request.tenant.schema_name`) sea el schema **public** antes de conceder permisos de módulo, vista, alta, edición o borrado.

| `ModelAdmin`        | App          | Modelos        |
| ------------------- | ------------ | -------------- |
| `TenantAdmin`       | `tenants`    | `Tenant`       |
| `DomainAdmin`       | `tenants`    | `Domain`       |
| `PlanAdmin`         | `appbilling` | `Plan`         |
| `SubscriptionAdmin` | `appbilling` | `Subscription` |
| `PaymentEventAdmin` | `appbilling` | `PaymentEvent` |

**Orden de herencia recomendado:** el mixin va **primero** (p. ej. `class TenantAdmin(PublicSchemaOnlyAdminMixin, TenantAdminMixin, admin.ModelAdmin)`).

**Dónde sí se ve todo (operador / dueño del SaaS):**

| Entorno              | URL típica                             |
| -------------------- | -------------------------------------- |
| Producción           | `https://api.jobrhythm.net/admin/`     |
| Local (ubuntu-house) | `http://api.chalanpro.net:8000/admin/` |

**Dónde no deben aparecer TENANTS ni BILLING (clientes):**

| Entorno        | URL típica                                                                       |
| -------------- | -------------------------------------------------------------------------------- |
| App del tenant | `https://{tenant}.jobrhythm.net` → `/admin/` (o `:8080/admin/` en dev con proxy) |

**Añadir un nuevo modelo solo-admin-public:** importar `PublicSchemaOnlyAdminMixin` desde `project.admin_mixins` y aplicarlo al `ModelAdmin` del modelo en `SHARED_APPS`.

---

## 11. Semantic Search (`appsearch` — JobRhythm)

Documentación detallada en **`app/appsearch/README.md`**. Resumen operativo para VPS y referencia de comandos.

### 11.1 Resumen y modelos

Capa desacoplada por schema de tenant para búsqueda semántica de transacciones:

| Modelo            | Función                                                                                                                                        |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **`SearchIndex`** | Índice persistido: `chunk_text`, embedding (1536 dims), FTS (`search_vector`) y `metadata` JSON por `DocumentLine`                             |
| **`IndexOutbox`** | Cola de trabajos: al guardar/borrar líneas o cambiar cabecera de documento, se encola upsert/delete; **no** interviene cuando el usuario busca |

Flujo de indexación: señal → `IndexOutbox` → cron `process_index_outbox_all` → OpenAI → `SearchIndex`.

### 11.2 Variables de entorno y PostgreSQL

En `envs/backend.env` (plantilla: `envs/backend.dev.example.env`):

- `OPENAI_API_KEY` — API OpenAI (`text-embedding-3-small`; independiente de suscripción ChatGPT Pro)
- `SEARCH_EMBEDDING_MODEL`, `SEARCH_EMBEDDING_DIMENSIONS=1536`
- `SEARCH_INDEXING_ENABLED=True`
- `SEARCH_MIN_RELEVANCE_SCORE=0.12` — umbral de relevancia híbrida (subir = menos ruido; ver `app/appsearch/eval/README.md`)

Infraestructura:

- Imagen Postgres **`pgvector/pgvector:pg15`** (ver `docker-compose.yml`)
- Tras cambiar env del backend: `docker compose up -d --force-recreate backend`

### 11.3 Comandos de gestión

En **ubuntu-house** añadir `-f docker-compose.dev.yml` a `docker compose`. En **VPS** usar los comandos tal cual.

#### `migrate_schemas`

Aplica migraciones en **todos** los schemas (public + tenants), creando tablas `appsearch_*` y extensión `vector` donde corresponda.

```bash
docker compose exec backend python manage.py migrate_schemas
```

Ejecutar tras desplegar cambios en modelos de `appsearch`.

#### `reindex_document_lines`

Reconstruye el **SearchIndex completo** del tenant: texto denormalizado, embeddings OpenAI y FTS. Uso típico: backfill inicial o cambio de modelo de embedding.

```bash
docker compose exec backend python manage.py reindex_document_lines --schema NOMBRE_SCHEMA

# Sin OpenAI (solo chunk + FTS)
docker compose exec backend python manage.py reindex_document_lines --schema NOMBRE_SCHEMA --no-embed

# Solo un documento
docker compose exec backend python manage.py reindex_document_lines --schema NOMBRE_SCHEMA --document-id 123
```

#### `process_index_outbox`

Procesa la cola **pendiente** de `IndexOutbox` (cambios incrementales tras guardar transacciones en la app).

```bash
docker compose exec backend python manage.py process_index_outbox --schema NOMBRE_SCHEMA

# Solo las líneas de un documento concreto (reindex directo, sin outbox)
docker compose -f docker-compose.dev.yml exec backend python manage.py reindex_document_lines --schema TU_SCHEMA --document-id 123

docker compose exec backend python manage.py process_index_outbox --schema NOMBRE_SCHEMA --limit 200
```

Tras importaciones masivas o depuración en un tenant concreto.

#### `process_index_outbox_all` (Fase A — cron)

Procesa la cola en **todos los tenants activos**. Ejecutar desde cron en el **host** (no dentro del contenedor backend):

```bash
# Manual en VPS
docker compose exec backend python manage.py process_index_outbox_all --limit 200

# Script unificado (ubuntu-house: --dev)
./scripts/process_search_outbox_cron.sh --dev
/opt/chalanpro/scripts/process_search_outbox_cron.sh
```

**Crontab VPS (cada 3 minutos):**

```cron
*/3 * * * * root /opt/chalanpro/scripts/process_search_outbox_cron.sh
```

Log VPS: `/var/log/chalanpro/search-outbox.log` (`sudo mkdir -p /var/log/chalanpro`). En **ubuntu-house**, log en `logs/search-outbox.log` con `--dev`.

Salida distinta de cero si hubo entradas fallidas o errores por tenant (útil para alertas). Por defecto continúa con el siguiente tenant; `--fail-fast` detiene al primer error.

#### 11.3.1 Scripts shell en el host

Scripts en **`scripts/`** pensados para ejecutarse en el **host** (ubuntu-house o VPS), no dentro del contenedor. En ubuntu-house usar **`--dev`** para apuntar a `docker-compose.dev.yml` y logs en `logs/`.

| Script | Para qué sirve |
|--------|----------------|
| **`process_search_outbox_cron.sh`** | Indexación **incremental**: procesa `IndexOutbox` en todos los tenants vía `process_index_outbox_all`. Diseñado para **cron** (p. ej. cada 3 min) tras crear/editar transacciones en la app. Usa `flock` para evitar solapamientos. Log: `logs/search-outbox.log` (dev) o `/var/log/chalanpro/search-outbox.log` (VPS). |
| **`run_search_eval.sh`** | **Regresión de Smart search**: ejecuta `search_eval` contra el JSON golden del tenant (`app/appsearch/eval/golden_queries.<schema>.json`). Comprueba recall@k, `min_count`, IDs prohibidos y avisos esperados. Falla con exit code ≠ 0 si algo se rompe. Opciones: `--fail-under 0.95`, `--update-baseline` (refrescar expected IDs tras cambio aprobado). |
| **`reindex_search_after_chunk_change.sh`** | **Reindex completo** tras cambios en `app/appsearch/services/chunk.py` o metadata indexada: primero drena outbox pendiente, luego `reindex_document_lines` (embeddings OpenAI). Un tenant: `--schema NOMBRE_SCHEMA`; todos: `--all-tenants`. |

Ejemplos **ubuntu-house**:

```bash
# Cron / manual — cola de indexación
./scripts/process_search_outbox_cron.sh --dev

# Verificar que las ~26 golden queries siguen pasando
./scripts/run_search_eval.sh --dev test_dominio_local
./scripts/run_search_eval.sh --dev test_dominio_local --fail-under 0.95

# Tras modificar chunk/metadata del índice
./scripts/reindex_search_after_chunk_change.sh --dev --schema test_dominio_local
```

Ejemplos **VPS** (sin `--dev`; ruta típica `/opt/chalanpro`):

```bash
/opt/chalanpro/scripts/process_search_outbox_cron.sh
/opt/chalanpro/scripts/run_search_eval.sh NOMBRE_SCHEMA --fail-under 0.95
/opt/chalanpro/scripts/reindex_search_after_chunk_change.sh --schema NOMBRE_SCHEMA
```

Documentación ampliada: **`app/appsearch/eval/README.md`**.

Comando Django relacionado (no es `.sh`): `seed_builder_aliases --schema NOMBRE_SCHEMA` — carga alias de party desde `app/appsearch/eval/builder_aliases.recommended.json`.

### 11.4 API y UI (Fase 2)

**API:** `POST /api/search/transactions/`

```json
{ "query": "Harbor Freight purchases over $500 this month", "limit": 50 }
```

**Respuesta:** `document_ids`, `results[]` (snippet, score, metadata), `applied_filters`, `resolved_entities`.

Resolución de **Party / Work Account / DocumentType** con matching difuso. Búsqueda acotada al **schema del tenant** del subdominio (django-tenants).

**Filtros de monto (Fase 2.5):**

- **`document_total_gte`** — «over $6,000» cuando no queda texto de producto (totales de factura vía `Document.total_amount`).
- **`line_final_price_gte`** — mismo patrón de monto pero con concepto/producto en la consulta (p. ej. cable + mínimo por línea).

**UI:** checkbox *Smart search (AI)* y botón **Similar** por fila en `/transactions`. Requiere `apptransactions.view_document`.

### 11.5 Fase 3 — Advanced Retrieval y afinación

Ver **`app/appsearch/README.md`** y **`app/appsearch/eval/README.md`**. Resumen:

| Capacidad | Detalle |
|-----------|---------|
| **Similares** | `POST /api/search/transactions/similar/` con `document_id` o `document_line_id` |
| **Rank fusion** | `SEARCH_FUSION_MODE` (`weighted` / `rrf`), pesos vector/FTS tunables |
| **Builder aliases** | Modelo `BuilderAlias` en admin del tenant; plantilla JSON + `seed_builder_aliases` |
| **Outbox** | `SEARCH_OUTBOX_MAX_ATTEMPTS`, dead letter (`dead_letter_at`), `outbox_status`, `requeue_dead_letter_outbox` |
| **Métricas** | `SearchTelemetry`, comandos `search_metrics` y `search_eval` |
| **Golden queries** | `app/appsearch/eval/golden_queries.<schema>.json` + `./scripts/run_search_eval.sh` |
| **Relevancia** | `SEARCH_MIN_RELEVANCE_SCORE`, filtro por tokens en snippet, tipos compuestos (`sales order`, …) |

Tras desplegar: **`migrate_schemas`**.

**Admin (por tenant):** Search index · Index outbox · Builder search aliases · Search telemetry.

---

## 12. Troubleshooting

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

## 13. Contacto y Soporte

Para problemas o preguntas:

- Revisar logs: `docker compose logs -f`
- Consultar esta documentación
- Contactar al equipo de desarrollo

---

**Última actualización:** Diciembre 2025  
**Versión del documento:** 1.0
