# 🔐 Guía: Conectar a chalan-db y Acceder al Admin de Django

## 📊 Conectar a chalan-db desde pgAdmin

### Paso 1: Obtener las credenciales de Render

1. Ve al [Render Dashboard](https://dashboard.render.com)
2. Navega a tu base de datos `chalan-db`
3. En la sección **Connections**, busca **External Database URL**
4. Copia la URL completa (tiene este formato):
   ```
   postgresql://usuario:password@host:5432/database_name
   ```

### Paso 2: Extraer las credenciales de la URL

De la URL de ejemplo en tu proyecto:
```
postgresql://postgre_chalan_demo_user:3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr@dpg-d41983e3jp1c73cnm4k0-a/postgre_chalan_demo
```

**Credenciales extraídas:**
- **Host:** `dpg-d41983e3jp1c73cnm4k0-a`
- **Port:** `5432` (por defecto)
- **Database:** `postgre_chalan_demo`
- **Username:** `postgre_chalan_demo_user`
- **Password:** `3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr`

⚠️ **NOTA:** Estas credenciales son de ejemplo. Usa las que aparecen en tu dashboard de Render.

### Paso 3: Configurar pgAdmin

1. Abre pgAdmin
2. **Clic derecho en "Servers"** → **Register** → **Server**
3. En la pestaña **General**:
   - **Name:** `chalan-db (Render)`
4. En la pestaña **Connection**:
   - **Host name/address:** `dpg-d41983e3jp1c73cnm4k0-a` (o el host de tu External URL)
   - **Port:** `5432`
   - **Maintenance database:** `postgre_chalan_demo` (o el nombre de tu base de datos)
   - **Username:** `postgre_chalan_demo_user` (o tu usuario)
   - **Password:** `3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr` (o tu contraseña)
   - ✅ **Marcar:** "Save password"
5. En la pestaña **SSL**:
   - **SSL mode:** `Require` (Render requiere SSL para conexiones externas)
6. Clic en **Save**

### Paso 4: Verificar conexión

Si todo está correcto, deberías ver la base de datos `chalan-db` en pgAdmin y poder navegar por las tablas.

---

## 🗄️ Ejecutar Migraciones desde el Web Shell

### Paso 1: Acceder al Web Shell

1. Ve al [Render Dashboard](https://dashboard.render.com)
2. Navega a tu servicio `chalan-backend`
3. Haz clic en **Shell** en el menú lateral
4. Espera a que se abra la terminal

### Paso 2: Ejecutar Migraciones

Una vez en el Shell, ejecuta:

```bash
python manage.py migrate
```

O si quieres ver más detalles:

```bash
python manage.py migrate --verbosity 2
```

### Paso 3: Verificar las Migraciones

Para ver qué migraciones están pendientes:

```bash
python manage.py showmigrations
```

Este comando mostrará:
- ✅ Migraciones ya aplicadas
- ❌ Migraciones pendientes

### Comandos Útiles Adicionales

```bash
# Crear nuevas migraciones (si has cambiado modelos)
python manage.py makemigrations

# Aplicar migraciones de una app específica
python manage.py migrate appschedule

# Ver el estado de todas las migraciones
python manage.py showmigrations

# Verificar conexión a la base de datos
python manage.py check --database default
```

### Nota Importante

⚠️ **Las migraciones ya se ejecutan automáticamente** en el `startCommand` del `render.yaml`:
```yaml
startCommand: |
  python manage.py migrate --noinput || echo "Migration failed, continuing..."
```

Pero si necesitas ejecutarlas manualmente o verificar su estado, puedes usar el Web Shell como se explica arriba.

---

## 👤 Acceder al Admin de Django

### Opción 1: Crear un superusuario en Render (Recomendado)

Si aún no tienes un superusuario creado en Render:

1. Ve al dashboard de Render → Tu servicio `chalan-backend`
2. Haz clic en **Shell** (en el menú lateral)
3. Ejecuta este comando:
   ```bash
   python manage.py createsuperuser
   ```
4. Sigue las instrucciones:
   - **Username:** (elige un nombre de usuario, ej: `admin`)
   - **Email address:** (tu email)
   - **Password:** (elige una contraseña segura)
   - **Password (again):** (confirma la contraseña)

### Opción 2: Usar el Shell de Render

Si el Shell no está disponible, puedes usar la consola de Render:

1. Ve a **chalan-backend** → **Events** → Busca el último deploy
2. En los logs, busca si hay algún usuario creado
3. O usa el método de línea de comandos desde tu máquina local conectado a Render

### Opción 3: Crear superusuario desde tu máquina local

Si tienes acceso SSH o puedes conectarte directamente:

```bash
# Conectar a Render (si tienes acceso SSH configurado)
render ssh <service-name>

# O ejecutar el comando directamente
python manage.py createsuperuser
```

### Acceder al Admin

Una vez creado el superusuario:

1. Ve a tu backend en Render: `https://chalan-backend.onrender.com/admin/`
2. Ingresa con las credenciales que creaste:
   - **Username:** (el que elegiste)
   - **Password:** (la contraseña que configuraste)

---

## 🔍 Verificar usuarios existentes en la base de datos

Si quieres ver qué usuarios existen en la base de datos:

### Desde pgAdmin:

1. Conecta a `chalan-db` como se explicó arriba
2. Expande: `chalan-db` → `Schemas` → `public` → `Tables`
3. Busca la tabla `auth_user`
4. Clic derecho → **View/Edit Data** → **All Rows**
5. Verás todos los usuarios, incluyendo los superusuarios (`is_superuser = true`)

### Desde SQL:

```sql
SELECT id, username, email, is_superuser, is_staff, is_active 
FROM auth_user;
```

---

## 🛠️ Reseteo de contraseña del Admin

Si olvidaste la contraseña del admin:

### Opción 1: Cambiar desde el Shell de Render

```bash
python manage.py changepassword <username>
```

### Opción 2: Cambiar desde SQL (pgAdmin)

```sql
-- Cambiar contraseña del usuario 'admin' a 'nuevapassword123'
UPDATE auth_user 
SET password = 'pbkdf2_sha256$720000$...' 
WHERE username = 'admin';
```

**⚠️ Nota:** Para generar el hash de contraseña correcto, es mejor usar el comando de Django.

### Opción 3: Crear un nuevo superusuario

```bash
python manage.py createsuperuser
```

---

## 📝 Credenciales de Ejemplo (De tu base de datos de desarrollo)

Según los datos de tu base de datos local, estos usuarios existen:

- **Username:** `phoenixroot` (Superusuario)
- **Email:** `oliveralverto@gmail.com`
- **Username:** `Jose` (Superusuario)
- **Email:** `jnainv@gmail.com`
- **Username:** `Oliver` (Superusuario)
- **Email:** `oliverhernandez.p@gmail.com`

⚠️ **IMPORTANTE:** Estos usuarios son de tu base de datos local. En Render necesitas crear nuevos usuarios o migrar estos datos.

---

## 🔐 Seguridad

- ✅ **NUNCA** compartas las credenciales públicamente
- ✅ Usa contraseñas seguras para el admin
- ✅ Considera usar autenticación de dos factores si está disponible
- ✅ Limita el acceso al admin solo a usuarios confiables
- ✅ Usa SSL siempre (Render lo proporciona automáticamente)

---

## 🆘 Solución de Problemas

### Error: "could not connect to server"

**Causa:** pgAdmin no puede alcanzar la base de datos de Render.

**Soluciones:**
1. Verifica que estás usando la **External Database URL** (no la Internal)
2. Verifica que el modo SSL está configurado como `Require`
3. Verifica que tu IP está permitida en Render (algunos planes pueden tener restricciones)

### Error: "password authentication failed"

**Causa:** Las credenciales son incorrectas.

**Solución:**
1. Copia nuevamente la External Database URL desde Render
2. Verifica que copiaste correctamente el usuario y contraseña
3. Regenera las credenciales si es necesario desde Render Dashboard

### Error: "No se puede acceder al admin"

**Causa:** No hay superusuario creado o las credenciales son incorrectas.

**Solución:**
1. Crea un superusuario usando `python manage.py createsuperuser`
2. Verifica que el usuario tiene `is_superuser = True` y `is_staff = True`
3. Verifica que el usuario está activo (`is_active = True`)

---

## 📚 Referencias

- [Render PostgreSQL Docs](https://render.com/docs/databases)
- [Django Admin Documentation](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)
- [pgAdmin Documentation](https://www.pgadmin.org/docs/)

