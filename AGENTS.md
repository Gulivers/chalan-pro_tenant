# Agentes – Chalan-Pro (ubuntu-house)

Este documento da contexto a los agentes de IA (Cursor, Copilot, etc.) en el proyecto Chalan-Pro cuando se trabaja en el **entorno local ubuntu-house**.

## Nota de marca (importante)

- A nivel comercial y de interfaz de usuario, el nombre del sistema es **JobRhythm**.
- **Chalan-Pro / chalanpro** se mantiene para nombres técnicos internos (rutas, repositorio, variables, infraestructura) cuando aplique.
- En adelante, para textos visibles al usuario (web app, admin, landing, PDFs y mensajes), usar **JobRhythm**.
- Dominios actuales: SaaS `jobrhythm.net` (y subdominios tenant); landing `getjobrhythm.com`. Durante la transición (7–14 días) siguen activos `jobrithm.net` y `getjobrithm.com`.

## Stack

- **Backend:** Django (ASGI con Daphne), multi-tenant por schema.
- **Frontend:** Vue.js (SPA), puerto 8080 en desarrollo.
- **Base de datos:** PostgreSQL.
- **Contenedores:** Docker Compose; el archivo a usar depende del servidor (ver abajo).

## Docker Compose por servidor

- **`docker-compose.yml`**: para el **servidor VPS en Hostinger** (producción). Es el entorno donde se despliega la app (host típico: `srv1186738`). Es el que se usa cuando se trabaja o se ejecutan comandos en ese VPS.
- **`docker-compose.dev.yml`**: para el **servidor en casa** (ubuntu-house / desarrollo local). Usar en la máquina de desarrollo, no en el VPS.

## Entorno actual: ubuntu-house

- Servidor de **desarrollo local** (no producción).
- Ruta típica del proyecto: `~/shared/projects/chalanpro` o la raíz del workspace.
- Producción está en VPS Hostinger; los agentes **no** deben proponer ni ejecutar despliegue allí (lo hace el usuario).

## Reglas del proyecto

- Las reglas específicas del entorno ubuntu-house están en **`.cursor/rules/`** (por ejemplo `ubuntu-house.mdc`). Cursor las aplica automáticamente.
- **Idioma:** responder en español por defecto.
- **Git:** sincronización local en `readme/DEPLOY_GIT_LOCAL.md`. No incluir `envs/*.env` ni `postgres_data/` en commits.

## Ramas Git (junio 2026)

| Rama | Uso |
|------|-----|
| **`dev_local_status`** | Desarrollo activo en ubuntu-house |
| **`main_deploy`** | Producción VPS (`deploy-vps.sh`, `deploy-landing-vps.sh`) |
| **`main`**, **`develop`**, **`dev_local_inv-img`** | Históricas (con búsqueda semántica archivada; no desplegar) |

Flujo: commit en `dev_local_status` → merge a `main_deploy` → push → en VPS `sudo ./scripts/deploy-vps.sh`.

## Documentación útil

- Local / ubuntu-house: `app/readme/README_RESUMEN_GENERAL_LOCAL.md`
- Resumen general produccion en VPS en Hostinger: `app/readme/README_RESUMEN_GENERAL.md`
- Estándares del frontend del Proyecto: `app/docs/ai-guidelines.md`
- Workflow Git: `GIT_WORKFLOW.md`, `WORKFLOW_RESUMEN.md`
- Sincronización Git local: `readme/DEPLOY_GIT_LOCAL.md`
- Deploy en VPS (cuando aplique): `DEVOPS.md` (sección 3.2; script `scripts/deploy-vps.sh` con opciones `--no-pull`, `--no-build`, `--no-migrate`; usar `--no-migrate` cuando no hay cambios en modelos).

## Cómo abrir este workspace

Abrir en Cursor el archivo **`chalanpro-ubuntu-house.code-workspace`** para tener el workspace "Chalan-Pro (ubuntu-house)" con los agentes y la configuración asociada.
