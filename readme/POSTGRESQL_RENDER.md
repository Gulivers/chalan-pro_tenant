# Guía de PostgreSQL en Render

Esta guía te ayudará a configurar PostgreSQL en Render para Chalan-Pro.

## 🗄️ Variables de Entorno para PostgreSQL

### ✅ Variable Única Requerida

Render **genera automáticamente** la variable `DATABASE_URL` cuando creas una base de datos PostgreSQL.

```bash
DATABASE_URL=postgresql://usuario:password@host:5432/database_name
```

**NO necesitas configurar ninguna otra variable de base de datos.**

---

## 📝 Pasos para Configurar PostgreSQL en Render

### 1. Crear la Base de Datos

1. Ve al [Render Dashboard](https://dashboard.render.com)
2. Haz clic en **New +**
3. Selecciona **PostgreSQL**
4. Configura:
   - **Name:** chalan-pro-db (o el nombre que prefieras)
   - **Database:** chalan_db
   - **User:** chalan_user
   - **Region:** Selecciona la región más cercana
   - **PostgreSQL Version:** La última versión estable
   - **Plan:** Starter (gratis) o según tus necesidades
5. Haz clic en **Create Database**

### 2. Copiar DATABASE_URL

Una vez creada la base de datos:

1. En la página de la base de datos, ve a la sección **Connections**
2. Busca la variable **Internal Database URL**
3. Haz clic en **Copy** junto a la URL
4. Guárdala, la necesitarás en el siguiente paso

**Para Chalan-Pro, tu Internal Database URL es:**
```
postgresql://postgre_chalan_demo_user:3akCvVQLY2kOIlFKEcd1yfFbS6ErF1Rr@dpg-d41983e3jp1c73cnm4k0-a/postgre_chalan_demo
```

⚠️ **IMPORTANTE:** Usa la **Internal Database URL** (no la External) dentro de Render.

### 3. Configurar en el Servicio Web

1. Ve a tu servicio web en Render
2. Haz clic en **Environment** en el menú lateral
3. Haz clic en **Add Environment Variable**
4. Agrega:
   - **Key:** `DATABASE_URL`
   - **Value:** Pega la URL que copiaste
5. Haz clic en **Save Changes**
6. **Reinicia el servicio** para aplicar los cambios

---

## 🔄 Migración de MySQL a PostgreSQL

Si tienes datos en MySQL que necesitas migrar:

### Opción 1: Usar pgloader (Recomendado)

```bash
# Instala pgloader
# En Ubuntu/Debian:
sudo apt-get install pgloader

# Migra los datos
pgloader mysql://usuario:password@localhost/chalan_db \
          postgresql://usuario:password@host:5432/chalan_db
```

### Opción 2: Exportar/Importar Manualmente

```bash
# 1. Exportar desde MySQL
mysqldump -u usuario -p chalan_sch_txn > backup.sql

# 2. Convertir el SQL (puede requerir ajustes manuales)
# 3. Importar a PostgreSQL
psql -h host -U usuario -d chalan_db < backup.sql
```

### Opción 3: Reiniciar desde Cero

Si es una instalación nueva:

1. Las migraciones de Django crearán automáticamente las tablas
2. Solo necesitas ejecutar:
```bash
python manage.py migrate
```

---

## 🛠️ Solución de Problemas

### Error: "could not connect to server"

**Causa:** El servicio web no puede alcanzar la base de datos.

**Solución:**
1. Verifica que `DATABASE_URL` está configurada correctamente
2. Usa la **Internal Database URL** (no la pública) dentro de Render
3. Verifica que ambos servicios están en la misma región

### Error: "relation does not exist"

**Causa:** Las tablas no han sido creadas.

**Solución:**
```bash
python manage.py migrate
```

### Error: "password authentication failed"

**Causa:** La contraseña en `DATABASE_URL` es incorrecta.

**Solución:**
1. Verifica que copiaste correctamente la URL
2. Regenera las credenciales si es necesario

---

## 📊 Monitoreo

### Ver Datos en la Base de Datos

Render proporciona una interfaz web para administrar PostgreSQL:

1. Ve a tu servicio de base de datos en Render
2. Haz clic en **Commands** o **psql**
3. Puedes ejecutar comandos SQL directamente

### Comandos Útiles

```sql
-- Ver todas las tablas
\dt

-- Ver estructura de una tabla
\d nombre_tabla

-- Contar registros
SELECT COUNT(*) FROM nombre_tabla;

-- Ver información de la base de datos
SELECT * FROM pg_stat_database WHERE datname = 'chalan_db';
```

---

## 🔐 Seguridad

### Variables de Entorno

✅ **SIEMPRE** usa la **Internal Database URL** dentro de Render (no la pública)
✅ **NUNCA** compartas tu `DATABASE_URL` públicamente
✅ Usa un plan con backups automáticos en producción

### Backups

Render ofrece backups automáticos en planes pagos:
- Plan Starter: Backups manuales
- Plan Pro: Backups automáticos diarios
- Plan Pro Plus: Backups automáticos + PITR (Point in Time Recovery)

---

## 💰 Costos

### Planes de PostgreSQL en Render

- **Free Tier:** $0/mes (90 días, luego $7/mes)
- **Starter:** $7/mes
- **Standard:** $20/mes
- **Pro:** Desde $60/mes

**Nota:** El plan gratuito es ideal para comenzar, pero expira después de 90 días.

---

## ✅ Checklist de Verificación

- [ ] Base de datos PostgreSQL creada en Render
- [ ] Variable `DATABASE_URL` agregada al servicio web
- [ ] Migraciones ejecutadas con `python manage.py migrate`
- [ ] Servicio web reiniciado
- [ ] Conexión a la base de datos verificada
- [ ] Backups configurados (si es necesario)

---

## 📚 Referencias

- [Render PostgreSQL Docs](https://render.com/docs/databases)
- [Django PostgreSQL Setup](https://docs.djangoproject.com/en/stable/ref/databases/#postgresql-notes)
- [dj-database-url](https://github.com/jacobian/dj-database-url)

