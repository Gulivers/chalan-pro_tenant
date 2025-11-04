# Despliegue en Render (Backend Django + Frontend Vue)

## 1) Preparación
- Asegúrate de tener este archivo en la raíz: `render.yaml` (ya añadido).
- Repositorio en GitHub/GitLab/Bitbucket conectable a Render.

## 2) Crear Postgres en Render
1. En el dashboard de Render: New → Postgres
2. Nombre: `chalan-db` (o ajusta `render.yaml` si cambias el nombre)
3. Plan: Free/Starter
4. Espera a que se provisionen las credenciales (Render crea `DATABASE_URL`).

## 3) Crear Web Service (Backend)
1. New → Web Service
2. Conecta el repo de este proyecto
3. Render detectará `render.yaml` y creará el servicio `chalan-backend`
4. Start Command: ya definido: `daphne -b 0.0.0.0 -p $PORT project.asgi:application`
5. Variables de entorno incluidas (ver `render.yaml`):
   - `DATABASE_URL` (vinculada a `chalan-db`)
   - `PYTHON_VERSION`, `DJANGO_SETTINGS_MODULE`, `SECRET_KEY`, `ALLOWED_HOSTS`
6. Deploy.

Notas Django:
- Migrate/collectstatic se ejecutan en `buildCommand`.
- Si usas archivos estáticos desde Vue (static site), Django puede omitir servir estáticos.

## 4) Crear Static Site (Frontend)
1. New → Static Site
2. Conecta el mismo repo
3. Render leerá `render.yaml` y creará `chalan-frontend` con:
   - Build Command: `npm ci && npm run build`
   - Publish Directory: `vuefrontend/dist`
4. Deploy.

## 5) Verificar
- Backend URL (Render) → prueba `/admin` o endpoint de salud
- Frontend URL (Render) → sitio compilado de Vue

## 6) Variables útiles (opcionales)
En el Web Service (Render → Settings → Environment):
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: añade tu dominio Render y personalizados
- `CSRF_TRUSTED_ORIGINS`: incluye el dominio del frontend (`https://<frontend>.onrender.com`)

## 7) Logs y depuración
- Web Service → Logs para errores de `pip`, migraciones, o `daphne`
- Static Site → Logs de build de `npm`
- Base de datos → Panel de Postgres para conexiones y métricas

## 8) Despliegues automáticos
- Cada push a la rama configurada dispara un deploy de ambos servicios.

## 9) Cambios locales vs Render Postgres
- Local usas Docker (Postgres 16)
- Render usa `chalan-db` (gestionado). Migra con `python manage.py migrate` (ya corre en build) o ejecuta manualmente vía Shell en el servicio.

## 10) Endpoints/URLs
- Backend: `https://<chalan-backend>.onrender.com`
- Frontend: `https://<chalan-frontend>.onrender.com`

Si necesitas SSL personalizado y dominios, configura Custom Domains en cada servicio.
