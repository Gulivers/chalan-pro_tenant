# Variables de Entorno para Despliegue en Render

Este documento contiene todas las variables de entorno que necesitas configurar en Render para tu aplicación Chalan-Pro.

## 📋 Guía Rápida

1. Ve a tu servicio en [Render Dashboard](https://dashboard.render.com)
2. Navega a **Environment** en el menú lateral
3. Agrega cada variable de entorno una por una
4. Haz clic en **Save Changes**

---

## 🔐 Variables Obligatorias

### Django Core

```bash
# Clave secreta de Django (GENERA UNA NUEVA)
DJANGO_SECRET_KEY=tu-clave-secreta-generada-aqui
```

**Cómo generar una clave secreta:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

```bash
# Modo debug - DEBE SER False en producción
DEBUG=False

# Hosts permitidos - Tu dominio de Render
ALLOWED_HOSTS=chalan-pro.onrender.com
```

---

## 🗄️ Base de Datos (PostgreSQL)

**Para Chalan-Pro, agrega esta variable de entorno:**

```bash
DATABASE_URL=postgresql://postgre_chalan_demo_user:3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr@dpg-d41983e3jp1c73cnm4k0-a/postgre_chalan_demo
```

**Detalles de la base de datos:**
- **Hostname:** `dpg-d41983e3jp1c73cnm4k0-a`
- **Port:** `5432`
- **Database:** `postgre_chalan_demo`
- **Username:** `postgre_chalan_demo_user`
- **Password:** `3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr`

⚠️ **IMPORTANTE:** Esta es la **Internal Database URL** - solo funciona dentro de los servicios de Render.

**NO necesitas** configurar ninguna variable de entorno adicional para la base de datos.

### Configuración Automática
Tu aplicación detectará automáticamente si existe `DATABASE_URL`:
- ✅ Si existe → Usa PostgreSQL (Render)
- ❌ Si no existe → Usa MySQL (desarrollo local)

### Para Desarrollo Local (MySQL)
Si quieres usar MySQL localmente, agrega estas variables (solo en tu `.env` local, NO en Render):

```bash
MYSQL_DATABASE=chalan_sch_txn
MYSQL_USER=chalan_user
MYSQL_PASSWORD=tu_password_seguro
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

---

## 📧 Configuración de Email (SendGrid)

```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.tu-api-key-de-sendgrid-aqui
EMAIL_DEFAULT_FROM=oliver@division16llc.com
```

**Cómo obtener la API Key de SendGrid:**
1. Ve a [SendGrid Dashboard](https://app.sendgrid.com)
2. Settings → API Keys
3. Create API Key
4. Copia la clave generada

---

## 🌐 URLs del Frontend

```bash
# URL de tu aplicación frontend
FRONT_URL=https://tu-frontend.onrender.com
```

---

## 🔒 Configuración de Seguridad

```bash
# Orígenes confiables para CSRF
CSRF_TRUSTED_ORIGINS=https://tu-backend.onrender.com,https://tu-frontend.onrender.com

# CORS - Permite todos los orígenes (SOLO si es necesario)
CORS_ALLOW_ALL_ORIGINS=False
```

**Para producción, es recomendable usar:**
```bash
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://tu-frontend.onrender.com,https://tu-otro-dominio.com
```

---

## 🔴 Redis (Opcional - para WebSockets)

Si habilitas WebSockets, necesitarás Redis:

```bash
# Render generará automáticamente REDIS_URL si creas un servicio Redis
REDIS_URL=redis://tu-redis:6379/0
```

---

## 📦 Variables de Archivos Estáticos y Media

```bash
# Estos valores son por defecto, pero puedes configurarlos si necesitas personalización
STATIC_ROOT=/app/staticfiles
STATIC_URL=/static/
MEDIA_ROOT=/app/media
MEDIA_URL=/media/
```

---

## ✅ Resumen de Variables para Copiar y Pegar

### Versión Mínima (Solo lo necesario)

```bash
# Django Core
DJANGO_SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=chalan-pro.onrender.com

# Base de datos PostgreSQL
DATABASE_URL=postgresql://postgre_chalan_demo_user:3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr@dpg-d41983e3jp1c73cnm4k0-a/postgre_chalan_demo

# Seguridad y CORS
CSRF_TRUSTED_ORIGINS=https://chalan-pro.onrender.com
FRONT_URL=https://chalan-pro.onrender.com
```

### Versión Completa (Con todas las opciones)

```bash
# Django Core
DJANGO_SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=chalan-pro.onrender.com

# Base de datos PostgreSQL (Chalan-Pro)
DATABASE_URL=postgresql://postgre_chalan_demo_user:3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr@dpg-d41983e3jp1c73cnm4k0-a/postgre_chalan_demo

# Seguridad y CORS
CSRF_TRUSTED_ORIGINS=https://chalan-pro.onrender.com
CORS_ALLOW_ALL_ORIGINS=False
FRONT_URL=https://chalan-pro.onrender.com

# Email (SendGrid)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.tu-api-key-aqui
EMAIL_DEFAULT_FROM=oliver@division16llc.com

# Redis (WebSockets)
REDIS_URL=redis://tu-redis:6379/0
```

---

## 🚀 Pasos de Despliegue

1. **Crea una base de datos PostgreSQL** en Render
   - Dashboard → New → PostgreSQL
   - Render generará automáticamente `DATABASE_URL`
   - Guarda esta variable para usarla en el servicio web

2. **Crea el servicio Web** en Render
   - Dashboard → New → Web Service
   - Conecta tu repositorio de GitHub/GitLab

3. **Configura el servicio:**
   - **Build Command:** `pip install -r requirements.txt && npm install --legacy-peer-deps && cd vuefrontend && npm install --legacy-peer-deps && npm run build`
   - **Start Command:** `python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn project.wsgi:application`

4. **Agrega las variables de entorno** (sección arriba)
   - 🔑 IMPORTANTE: También agrega `DATABASE_URL` que copiaste del servicio de base de datos

5. **Haz clic en Deploy**

---

## ⚠️ Importante

- **NO compartas** tus claves secretas públicamente
- **NO subas** el archivo `.env` a Git
- **Cambia** todas las claves y contraseñas de los ejemplos
- **Verifica** que `DEBUG=False` en producción
- **Usa HTTPS** siempre en producción (Render lo proporciona automáticamente)

---

## 🔍 Verificación Post-Despliegue

Después de desplegar, verifica que:

1. ✅ La aplicación se inicia sin errores
2. ✅ Puedes acceder a `/admin/`
3. ✅ Los archivos estáticos se cargan correctamente
4. ✅ El frontend puede comunicarse con el backend
5. ✅ Las migraciones se ejecutaron correctamente

---

## 📝 Notas Adicionales

- Render asigna automáticamente la variable `PORT` - no necesitas configurarla
- Los logs de la aplicación estarán disponibles en Render Dashboard → Logs
- Puedes monitorear el rendimiento en Render Dashboard → Metrics

