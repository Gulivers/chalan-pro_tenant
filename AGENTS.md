# Agentes – Chalan-Pro (ubuntu-house)

Este documento da contexto a los agentes de IA (Cursor, Copilot, etc.) en el proyecto Chalan-Pro cuando se trabaja en el **entorno local ubuntu-house**.

## Stack

- **Backend:** Django (ASGI con Daphne), multi-tenant por schema.
- **Frontend:** Vue.js (SPA), puerto 8080 en desarrollo.
- **Base de datos:** PostgreSQL.
- **Contenedores:** Docker Compose; en local usar `docker-compose.dev.yml`.

## Entorno actual: ubuntu-house

- Servidor de **desarrollo local** (no producción).
- Ruta típica del proyecto: `~/shared/projects/chalanpro` o la raíz del workspace.
- Producción está en VPS Hostinger; los agentes **no** deben proponer ni ejecutar despliegue allí (lo hace el usuario).

## Reglas del proyecto

- Las reglas específicas del entorno ubuntu-house están en **`.cursor/rules/`** (por ejemplo `ubuntu-house.mdc`). Cursor las aplica automáticamente.
- **Idioma:** responder en español por defecto.
- **Git:** sincronización local descrita en `readme/DEPLOY_GIT_LOCAL.md` (o el doc equivalente en `readme/`). No incluir `envs/*.env` ni `postgres_data/` en commits.

## Documentación útil

- Local / ubuntu-house: `app/readme/README_RESUMEN_GENERAL_LOCAL.md`
- Resumen general: `app/readme/README_RESUMEN_GENERAL.md`
- Workflow Git: `GIT_WORKFLOW.md`, `WORKFLOW_RESUMEN.md`
- Sincronización Git local: `readme/DEPLOY_GIT_LOCAL.md`

## Cómo abrir este workspace

Abrir en Cursor el archivo **`chalanpro-ubuntu-house.code-workspace`** para tener el workspace "Chalan-Pro (ubuntu-house)" con los agentes y la configuración asociada.

## Cursor Cloud specific instructions

### Servicios y puertos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| PostgreSQL | 5432 | Base de datos multi-tenant (Docker) |
| Backend (Daphne) | 8000 | Django REST API + WebSockets (Docker) |
| Frontend (Vue dev) | 8080 | Vue.js SPA con hot-reload (host) |

### Iniciar servicios para desarrollo

Los contenedores Docker (postgres + backend) se inician con:
```
docker compose -f docker-compose.dev.yml up -d postgres backend
```
El frontend Vue.js se ejecuta directamente en el host (no en Docker) para hot-reload más rápido:
```
cd app/vuefrontend && npm run serve
```
El dev server del frontend hace proxy de `/api`, `/admin`, `/ws`, `/static`, `/media` al backend en `localhost:8000` (configurado en `vue.config.js`).

### Archivos de entorno (gitignored)

Los archivos `envs/*.env` no están en el repo. Se deben crear a partir de:
- `envs/backend.dev.example.env` → `envs/backend.dev.env`
- `envs/postgres.env` (con `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`)
- `envs/pgadmin.env` (opcional)

### Notas importantes (gotchas)

- **Migraciones multi-tenant:** Usar `migrate_schemas --shared` para migrar el schema público. Para tenants, usar `migrate_schemas`.
- **Tenant público requerido:** django-tenants necesita un tenant con `schema_name='public'` y un `Domain` asociado a `localhost` para funcionar. Sin esto, las peticiones al backend fallan.
- **Tests Django:** Los tests (`manage.py test`) fallan porque requieren `TenantTestCase` de django-tenants. Es un problema preexistente del proyecto.
- **ESLint:** Requiere `eslint@8` y `eslint-plugin-vue@9` (no están en `package.json` por defecto). Los errores de lint preexistentes (121 `no-undef`) son warnings de jQuery `$` y no afectan el funcionamiento.
- **Docker en Cloud Agent:** Se necesita `fuse-overlayfs` como storage driver y `iptables-legacy` para Docker en el entorno cloud (contenedor dentro de VM).
- **nginx/default.dev.conf:** El archivo es necesario para `docker-compose.dev.yml` pero no existía originalmente en el repo; fue añadido.
