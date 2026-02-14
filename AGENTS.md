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
