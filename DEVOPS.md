# DevOps – Entorno VPS Chalan-Pro (Hostinger / Ubuntu 24.04 LTS)

Documento de referencia para operar el servidor con **precisión, repetibilidad y buenas prácticas** (arquitectura cloud y contenedores). Usar como fuente única de verdad para despliegues, runbooks y estándares.

---

## 1. Stack y topología

| Componente | Contenedor | Puertos | Rol |
|------------|------------|---------|-----|
| **PostgreSQL 15** | `chalanpro_postgres` | 5432 | Base de datos multi-tenant (schemas) |
| **Backend Django** | `chalanpro_backend` | 8000 (interno) | API + Daphne (ASGI), migraciones, `collectstatic` |
| **Frontend Vue.js** | `chalanpro_frontend` | — | Build → `app/vuefrontend/dist` (servido por Nginx) |
| **Nginx** | `chalanpro_nginx` | 80, 443 | Reverse proxy, SSL/TLS, estáticos, WebSocket `/ws/` |
| **PgAdmin** | `chalanpro_pgadmin` | 5050 | Administración DB (opcional) |

- **Red:** `chalanpro_network` (bridge).
- **Volúmenes:** `postgres_data`, `staticfiles_volume`, `media_volume`, `pgadmin_data`.
- **Rutas clave:** App en `/opt/chalanpro`, compose en `/opt/chalanpro/docker-compose.yml`, envs en `envs/`.

---

## 2. Entorno VPS (baseline)

- **SO:** Ubuntu 24.04 LTS.
- **Path:** `/opt/chalanpro` (raíz del repo y del compose).
- **Compose:** `docker-compose.yml` (producción). No usar `docker-compose.dev.yml` en VPS.
- **Secrets:** `.env` en `envs/` (postgres.env, backend.env, pgadmin.env). **Nunca** versionar secretos; solo templates o ejemplos sin valores reales.
- **DNS:** Hostinger → `chalanpro.net`, `api.chalanpro.net`, `*.chalanpro.net` apuntando a la IP del VPS.
- **SSL:** Let's Encrypt (Certbot); certificados en `/etc/letsencrypt`, challenge en `/var/www/certbot`.

---

## 3. Despliegue (repetible e idempotente)

### 3.1 Requisitos previos

- Docker y Docker Compose instalados.
- Archivos `envs/*.env` creados y con valores correctos.
- DNS configurado para el dominio y subdominios.
- Certificados SSL obtenidos (por ejemplo con `init-certbot.sh` o `init-certbot-wildcard.sh`).

### 3.2 Comando estándar de deploy (después de `git pull`)

Usar el script que centraliza pasos y reduce errores:

```bash
sudo /opt/chalanpro/scripts/deploy-vps.sh
```

O manualmente, siempre desde la raíz del proyecto:

```bash
cd /opt/chalanpro
git fetch origin
git checkout main
git pull origin main

docker compose build --no-cache backend frontend  # si hubo cambios en Dockerfile o dependencias
docker compose up -d postgres
# Esperar healthcheck de postgres (o ~15s)
docker compose up -d backend
docker compose exec -T backend python manage.py migrate --noinput
docker compose exec -T backend python manage.py collectstatic --noinput
docker compose up -d frontend
# Esperar a que el frontend termine de construir (o ~30s)
docker compose up -d nginx
docker compose restart backend frontend nginx
```

- **Solo `main`** debe desplegarse en producción. No hacer `git pull` de `develop` o ramas de feature en el VPS.
- **Migraciones:** siempre con `migrate --noinput`. Si usas schemas por tenant, seguir `INSTRUCCIONES_MIGRACIONES.md` (p. ej. `migrate_schemas`).

### 3.3 Rollback rápido

```bash
cd /opt/chalanpro
git log -1 --oneline   # anotar commit actual
git checkout main
git reset --hard <commit-anterior>
docker compose build backend frontend
docker compose up -d backend frontend nginx
docker compose exec -T backend python manage.py migrate --noinput
docker compose exec -T backend python manage.py collectstatic --noinput
```

---

## 4. Runbooks

### 4.1 Ver estado de servicios

```bash
cd /opt/chalanpro
docker compose ps
docker compose logs -f --tail=100 backend nginx
```

### 4.2 Reiniciar servicios (sin redeploy de código)

```bash
cd /opt/chalanpro
docker compose restart backend frontend nginx
```

### 4.3 Solo backend (tras cambio de env o código ya desplegado)

```bash
docker compose restart backend
docker compose restart nginx   # por si Nginx cachea upstream
```

### 4.4 Renovación SSL (Let's Encrypt)

- Certbot en el host (no en contenedor) o script existente (`init-certbot.sh` / wildcard).
- Tras renovar:

```bash
docker compose -f /opt/chalanpro/docker-compose.yml restart nginx
```

### 4.5 502 Bad Gateway (Nginx → backend)

- Comprobar que el backend está up: `docker compose ps backend`.
- Logs: `docker compose logs --tail=50 backend nginx`.
- Resolución DNS interna: `docker compose exec nginx getent hosts backend`.
- La configuración actual de Nginx usa `resolver 127.0.0.11` y variables para evitar caché de IP del backend; si persiste, `docker compose restart nginx`.

### 4.6 Espacio en disco

```bash
df -h
docker system df
docker compose logs --tail=0 backend 2>&1 | wc -l   # volumen de logs si aplica
```

### 4.7 Backups (sistema + base de datos con tenants)

**Script recomendado:** `scripts/backup_completo_VPS.sh`

```bash
# Backup completo (sistema + DB con todos los schemas/tenants)
sudo /opt/chalanpro/scripts/backup_completo_VPS.sh

# Con retención: mantener solo los últimos 7 backups
sudo /opt/chalanpro/scripts/backup_completo_VPS.sh --retention 7
```

- **Destino:** `/opt/backups/`
- **Archivos:** `chalanpro_vps_YYYYMMDD_HHMMSS.tar.gz` (sistema), `chalanpro_vps_db_YYYYMMDD_HHMMSS.sql` (DB)
- **Restaurar (rollback):**

```bash
sudo /opt/chalanpro/scripts/restore_backup.sh YYYYMMDD_HHMMSS
# Solo sistema: --sistema-only
# Solo DB: --db-only
```

- Programar con cron (ej. diario a las 3:00): `0 3 * * * root /opt/chalanpro/scripts/backup_completo_VPS.sh --retention 7`
- Probar restauración de forma periódica.

---

## 5. Buenas prácticas

- **No editar código ni config sensible directamente en el VPS.** Todo cambio vía repo (rama `main`) y deploy con el proceso definido.
- **Secrets:** solo en `envs/*.env` (fuera de Git). No hardcodear en Dockerfile ni en código.
- **Un solo compose en producción:** `docker-compose.yml`. No exponer PgAdmin a internet si no es necesario; restringir por firewall o no mapear puerto en producción.
- **Logs:** usar `docker compose logs`; si se centraliza en ficheros, rotar con logrotate.
- **Actualizaciones de seguridad:** mantener Ubuntu y las imágenes base (postgres, nginx, python) actualizadas; revisar CVE y renovar imágenes cuando proceda.
- **Healthchecks:** el compose ya define healthcheck para `postgres`; `depends_on` con `condition: service_healthy` para el backend. Mantener este patrón.

---

## 6. Referencia rápida de archivos

| Archivo | Uso |
|---------|-----|
| `docker-compose.yml` | Stack producción VPS |
| `docker-compose.dev.yml` | Solo desarrollo local |
| `nginx/default.conf` | Nginx producción (HTTP/HTTPS, API, WebSocket, estáticos) |
| `setup.sh` | Primera configuración del proyecto en el servidor |
| `scripts/deploy-vps.sh` | Deploy idempotente en VPS |
| `scripts/backup_completo_VPS.sh` | Backup sistema + DB (todos los tenants) → `/opt/backups/` |
| `scripts/restore_backup.sh` | Restaurar backup para rollback |
| `init-certbot.sh` / `init-certbot-wildcard.sh` | Obtención/renovación SSL |
| `enable-https.sh` | Cambio de config Nginx a HTTPS |
| `GIT_WORKFLOW.md` | Ramas, merge a `main`, deploy en VPS |
| `app/INSTRUCCIONES_MIGRACIONES.md` | Migraciones Django y tenants |

---

## 7. Cursor por SSH y workspace (agentes y chat en el VPS)

Para que los agentes de Cursor y el historial de chat estén disponibles al conectarte por SSH al VPS:

1. **Conectar por Remote-SSH** en Cursor al host del VPS (Hostinger).
2. **Abrir el workspace:** una vez conectado, abrir el archivo de workspace:
   - `File → Open Workspace from File…` (o equivalente).
   - Seleccionar en el VPS: `/opt/chalanpro/chalanpro-vps.code-workspace`.
3. Cursor usará `/opt/chalanpro` como raíz del proyecto; las reglas en `.cursor/rules/` (p. ej. `devops-vps.mdc`) se cargan y el historial de chat y agentes quedan asociados a este workspace.

Así, al entrar por SSH y abrir `chalanpro-vps.code-workspace`, tendrás el mismo contexto (reglas DevOps, migraciones con `migrate_schemas`) y podrás seguir las conversaciones y agentes en el VPS.

---

## 8. Checklist pre-deploy (antes de merge a `main`)

- [ ] Código probado en entorno de desarrollo (p. ej. `develop` en ubuntu-house).
- [ ] Migraciones probadas (incl. tenants si aplica); en producción usar `migrate_schemas`.
- [ ] Build del frontend sin errores.
- [ ] WebSockets y API probados.
- [ ] Sin secretos ni `.env` reales en el commit.
- [ ] Documentación/runbooks actualizados si cambia el flujo.
