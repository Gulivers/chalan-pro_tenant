# Deploy PWA + fix login en VPS Hostinger

Checklist para desplegar los cambios de PWA y corrección del login en el VPS.

## Cambios incluidos

1. **main.js**: Fix para que la PWA en `*.localhost:8080` use el backend en puerto 8000 (evita 404 en `/api/login`).
2. **nginx/default.conf**: Headers PWA para `service-worker.js` y `manifest.json` (no cachear, permitir actualizaciones).
3. **vue.config.js** y **package.json**: Plugin PWA, iconos, manifest.

## Pre-deploy (local)

```bash
# 1. Verificar que el build funciona
cd app/vuefrontend
npm run build

# 2. Comprobar que dist/ contiene los archivos PWA
ls -la dist/
# Debe haber: manifest.json, service-worker.js (o precache-manifest.*.js), img/icons/

# 3. Verificar rama y cambios
git status
git diff --stat
```

## Flujo Git (merge a main)

```bash
# Opción A: Si trabajas en dev_local_inv-img y quieres mergear a main
git checkout main
git pull origin main
git merge dev_local_inv-img
git push origin main

# Opción B: Si prefieres pasar por develop primero
git checkout develop
git pull origin develop
git merge dev_local_inv-img
git push origin develop
# Probar en develop, luego:
git checkout main
git merge develop
git push origin main
```

## Deploy en VPS

```bash
# Conectar al VPS (o usar deploy remoto)
ssh ubuntu@72.60.168.62  # o tu alias

# En el VPS
cd /opt/chalanpro
sudo ./scripts/deploy-vps.sh
```

El script hace:
- `git pull origin main`
- `docker compose build --no-cache backend frontend`
- Migraciones, collectstatic
- Reinicio de servicios

## Post-deploy (verificación)

1. **HTTPS tenant**: Abrir `https://TU-TENANT.chalanpro.net`
2. **PWA**: Comprobar que se puede instalar (icono "Instalar app" en el navegador).
3. **Login**: Hacer login y verificar que no hay 404 en `/api/login`.
4. **DevTools**: Application → Manifest, Service Worker registrado.

## Rollback (si algo falla)

```bash
# En el VPS
cd /opt/chalanpro
git log -1  # anotar el commit anterior
git checkout <commit-anterior>
sudo docker compose build --no-cache frontend
sudo docker compose up -d frontend nginx
```

## Variables de entorno (opcional)

Para el build del frontend en Docker, no se requieren variables adicionales. En producción el hostname es `*.chalanpro.net` y la lógica de `main.js` usa el mismo host (Nginx hace proxy de `/api` al backend).

Si en el futuro necesitas una API en otro host, usa:
- `VUE_APP_API_BASE_URL` en el build del frontend.
