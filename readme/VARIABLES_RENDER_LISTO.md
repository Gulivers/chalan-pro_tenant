# ✅ Variables de Entorno para Render - Chalan-Pro

## 🚀 Configuración Rápida

Copia y pega estas variables directamente en el Dashboard de Render.

---

## 📋 Variables Mínimas Requeridas

Agrega estas variables en **Environment** de tu servicio web en Render:

```bash
DJANGO_SECRET_KEY=django-insecure-CAMBIA-ESTA-CLAVE-POR-UNA-SECURA
DEBUG=False
ALLOWED_HOSTS=chalan-pro.onrender.com
DATABASE_URL=postgresql://postgre_chalan_demo_user:3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr@dpg-d41983e3jp1c73cnm4k0-a/postgre_chalan_demo
CSRF_TRUSTED_ORIGINS=https://chalan-pro.onrender.com
FRONT_URL=https://chalan-pro.onrender.com
```

---

## 🔑 Explicación de Cada Variable

### 1. DJANGO_SECRET_KEY
**GENERA UNA NUEVA CLAVE SEGURA**

Ejecuta este comando en tu terminal:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**❌ NO uses:** `django-insecure-CAMBIA-ESTA-CLAVE-POR-UNA-SECURA` en producción

### 2. DEBUG
```bash
DEBUG=False
```
Siempre `False` en producción por seguridad.

### 3. ALLOWED_HOSTS
```bash
ALLOWED_HOSTS=chalan-pro.onrender.com
```
✅ **Tu dominio en Render**

### 4. DATABASE_URL
```bash
DATABASE_URL=postgresql://postgre_chalan_demo_user:3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr@dpg-d41983e3jp1c73cnm4k0-a/postgre_chalan_demo
```
✅ **Esta es la URL correcta de tu base de datos PostgreSQL**

### 5. CSRF_TRUSTED_ORIGINS
```bash
CSRF_TRUSTED_ORIGINS=https://chalan-pro.onrender.com
```
✅ **Lista de dominios permitidos para CSRF**

### 6. FRONT_URL
```bash
FRONT_URL=https://chalan-pro.onrender.com
```
✅ **URL de tu aplicación**

---

## 📦 Variables Opcionales (Configuración Avanzada)

### Email (SendGrid)

Si necesitas enviar correos electrónicos:

```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.tu-api-key-sendgrid
EMAIL_DEFAULT_FROM=oliver@division16llc.com
```

### Redis (Para WebSockets)

Si habilitas notificaciones en tiempo real:

```bash
REDIS_URL=redis://tu-redis:6379/0
```

### CORS Configuración

Para mayor seguridad, en lugar de permitir todos los orígenes:

```bash
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://chalan-pro.onrender.com
```

---

## 🎯 Instrucciones Paso a Paso para Render

### Paso 1: Crear el Servicio Web

1. Ve a [Render Dashboard](https://chalan-pro.onrender.com)
2. Haz clic en **New +**
3. Selecciona **Web Service**
4. Conecta tu repositorio de GitHub/GitLab
5. Configura:
   - **Name:** chalan-pro-backend (o el nombre que prefieras)
   - **Region:** Oregon (recommendado para coincidir con la BD)
   - **Branch:** main
   - **Root Directory:** (déjalo vacío)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt && npm install --legacy-peer-deps && cd vuefrontend && npm install --legacy-peer-deps && npm run build`
   - **Start Command:** `python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn project.wsgi:application`

### Paso 2: Agregar Variables de Entorno

1. Desplázate a la sección **Environment**
2. Haz clic en **Add Environment Variable**
3. Agrega cada variable una por una:

| Key | Value |
|-----|-------|
| `DJANGO_SECRET_KEY` | `TU_CLAVE_SECRETA_GENERADA` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `chalan-pro.onrender.com` |
| `DATABASE_URL` | `postgresql://postgre_chalan_demo_user:3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr@dpg-d41983e3jp1c73cnm4k0-a/postgre_chalan_demo` |
| `CSRF_TRUSTED_ORIGINS` | `https://chalan-pro.onrender.com` |
| `FRONT_URL` | `https://chalan-pro.onrender.com` |

4. Haz clic en **Save Changes**

### Paso 3: Desplegar

1. Haz clic en **Save Changes** en la parte superior
2. Render comenzará a construir y desplegar automáticamente
3. Espera a que termine el despliegue (puede tomar 5-10 minutos)
4. Verifica los logs para asegurarte de que no hay errores

---

## ✅ Checklist de Verificación

- [ ] Servicio web creado en Render
- [ ] Base de datos PostgreSQL ya existe (`postgre_chalan_demo`)
- [ ] Todas las variables de entorno agregadas
- [ ] DJANGO_SECRET_KEY es una clave segura (no la del ejemplo)
- [ ] ALLOWED_HOSTS tiene tu dominio correcto
- [ ] Build Command configurado correctamente
- [ ] Start Command configurado correctamente
- [ ] Despliegue completado sin errores

---

## 🐛 Solución de Problemas

### Error: "Module not found: psycopg2"

**Solución:** Verifica que `psycopg2-binary==2.9.9` está en `requirements.txt`

### Error: "Database connection failed"

**Solución:** Verifica que `DATABASE_URL` está configurada correctamente con la Internal URL

### Error: "DisallowedHost"

**Solución:** Agrega tu dominio a `ALLOWED_HOSTS`

### Error: "CSRF verification failed"

**Solución:** Agrega tu URL a `CSRF_TRUSTED_ORIGINS`

---

## 📝 Información de la Base de Datos

**Hostname:** `dpg-d41983e3jp1c73cnm4k0-a`  
**Port:** `5432`  
**Database:** `postgre_chalan_demo`  
**Username:** `postgre_chalan_demo_user`  
**Password:** `3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr`  

**Internal Database URL:**
```
postgresql://postgre_chalan_demo_user:3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr@dpg-d41983e3jp1c73cnm4k0-a/postgre_chalan_demo
```

---

## 🔐 Seguridad Importante

⚠️ **ADVERTENCIAS DE SEGURIDAD:**

1. **NO compartas** este archivo públicamente
2. **Genera una nueva** `DJANGO_SECRET_KEY` para producción
3. **NUNCA** uses `DEBUG=True` en producción
4. La base de datos PostgreSQL en Render es **solo accesible internamente**
5. Considera usar un servicio para gestionar secretos (como AWS Secrets Manager)

---

## 📚 Documentación Adicional

- `RENDER_VARIABLES.md` - Documentación completa de variables
- `POSTGRESQL_RENDER.md` - Guía de PostgreSQL
- `env.example` - Archivo de ejemplo con todas las variables

