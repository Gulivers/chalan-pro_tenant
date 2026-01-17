# Copilot / AI contributor instructions for Chalan-Pro

Quick, actionable guidance to be productive immediately in this repository.

## Big picture
- Stack: **Django (backend)** + **Vue.js SPA (frontend)** + **PostgreSQL** + **Nginx** (reverse-proxy) + **Certbot** for SSL. See `readme/README.md` and `readme/SETUP_COMPLETO.md` for deployment context.
- Repo layout: backend in `app/` (Django project in `app/project`), frontend in `app/vuefrontend` (built output → `app/vuefrontend/dist`), container orchestration with `docker-compose.yml` (dev overrides in `docker-compose.dev.yml`).
- Multi-tenant: tenant-aware setup (tenant base domain in envs), migrations may use `migrate_schemas` (see `readme/SETUP_COMPLETO.md` and `INSTRUCCIONES_MIGRACIONES.md`).

## Quick start (dev & prod commands)
- Local / prod containers:
  - Bring up services (production-like):
    ```bash
    docker compose up -d --build
    ```
  - Development with hot-reload frontend:
    ```bash
    docker compose -f docker-compose.dev.yml up --profile dev frontend-dev
    # or in the frontend folder:
    cd app/vuefrontend && npm ci && npm run serve -- --host 0.0.0.0
    ```
- Django management (via Docker service `backend`):
  ```bash
  docker compose exec backend python manage.py migrate
  docker compose exec backend python manage.py migrate_schemas --schema public  # multi-tenant step
  docker compose exec backend python manage.py createsuperuser
  docker compose exec backend python manage.py collectstatic --noinput
  docker compose exec backend python manage.py test
  ```
- Database / backup:
  ```bash
  docker compose exec postgres psql -U chalanpro_user -d chalanpro
  docker compose exec postgres pg_dump -U chalanpro_user chalanpro > backup.sql
  ```
- SSL / production setup (server scripts):
  - `setup.sh`, `init-certbot.sh`, `enable-https.sh` are used on the target VPS (see `readme/SETUP_COMPLETO.md`).

## Project-specific conventions & patterns
- App-level single responsibility: each app (e.g., `ctrctsapp`, `crewsapp`, `auditapp`) groups models → serializers → views. See `app/README_BACKEND.md`.
- WebSockets: implemented with Django Channels—look for `consumers.py` and `routing.py` in apps that need realtime features.
- Validation and schemas: some apps use `views_schema.py` / `views_validation.py` (look in `appinventory/`), follow their patterns when adding endpoints.
- Static assets & frontend build: frontend build should produce `app/vuefrontend/dist` and Nginx mounts this path to serve the SPA (`nginx/default.conf`). The backend image runs `collectstatic` in its start command.
- Migrations on deploy: Render / CI expects `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate` (see `INSTRUCCIONES_MIGRACIONES.md`). For tenants, prefer `migrate_schemas` when appropriate.

## Debugging & observation
- Logs: `docker compose logs -f` or `docker compose logs -f backend` / `nginx` / `postgres`.
- Inspect Django runtime: `docker compose exec backend python manage.py shell` (use to inspect tenants, ALLOWED_HOSTS, etc.).
- Check URLs: `python manage.py show_urls` (if `django-extensions` is installed) to list routes.

## Files & locations to consult (high value)
- `readme/README.md` — production runbook and commands ✅
- `readme/SETUP_COMPLETO.md` — DNS, certs, and host-specific notes ✅
- `app/README_BACKEND.md` — backend conventions & architecture ✅
- `docker-compose.yml` / `docker-compose.dev.yml` — runtime and dev service names ✅
- `envs/` — `backend.env`, `backend.dev.env`, `postgres.env`, `pgadmin.env` (environment variables and secrets). ✅
- `nginx/default.conf` & `nginx/default.conf.https` — how routes are forwarded and SSL is configured.
- `INSTRUCCIONES_MIGRACIONES.md` — Render deploy migration recommendations.

## Quick tips for code changes
- If adding models: create migrations, run `makemigrations` locally, and ensure deploy runs `migrate` / `migrate_schemas` for tenants.
- If changing API behavior: add/adjust serializers and tests under the corresponding app's `tests.py`.
- If changing frontend routes or assets: update `app/vuefrontend`, run `npm run build`, verify `dist/` and `docker compose up -d --build frontend`.

## Examples (from repo)
- Backend container starts by running `collectstatic` then Gunicorn (see `docker-compose.yml` -> `backend.command`):
  ```bash
  sh -c "python manage.py collectstatic --noinput && gunicorn project.wsgi:application --bind 0.0.0.0:8000 --workers 3"
  ```
- Frontend dev hot-reload is provided by `frontend-dev` in `docker-compose.dev.yml` or directly with npm in `app/vuefrontend`:
  ```bash
  docker compose -f docker-compose.dev.yml up --profile dev frontend-dev
  # or
  cd app/vuefrontend && npm ci && npm run serve -- --host 0.0.0.0 --port 8080
  ```
- Multi-tenant migrations: use `migrate_schemas` (see `readme/SETUP_COMPLETO.md`):
  ```bash
  docker compose exec backend python manage.py migrate_schemas --schema public
  ```

## When unsure — where to check first
1. `docker compose logs -f backend` (runtime errors)
2. `app/project/settings.py` (settings and installed apps)
3. `nginx/default.conf` (routing issues)
4. `readme/*` docs above for operational context

---
Please review — do any areas feel incomplete or would you like brief, tool-assisted examples added (e.g., a sample PR checklist or more explicit tenant-migration commands)?