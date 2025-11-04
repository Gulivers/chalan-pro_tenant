# 🔄 Eliminar Tablas y Recrear Migraciones en Render

## Paso 1: Eliminar Tablas en PostgreSQL (Render)

Ve al Web Shell de Render y ejecuta estos comandos SQL para eliminar las tablas de las apps mencionadas:

```sql
-- Conectar a la base de datos desde el Shell de Render
python manage.py dbshell
```

O desde pgAdmin, ejecuta estos comandos SQL:

```sql
-- Eliminar tablas de appschedule
DROP TABLE IF EXISTS appschedule_event CASCADE;
DROP TABLE IF EXISTS appschedule_eventdraft CASCADE;
DROP TABLE IF EXISTS appschedule_eventimage CASCADE;
DROP TABLE IF EXISTS appschedule_eventnote CASCADE;
DROP TABLE IF EXISTS appschedule_eventchatmessage CASCADE;
DROP TABLE IF EXISTS appschedule_eventchatreadstatus CASCADE;
DROP TABLE IF EXISTS appschedule_absencereason CASCADE;

-- Eliminar tablas de apptransactions
DROP TABLE IF EXISTS apptransactions_documentline CASCADE;
DROP TABLE IF EXISTS apptransactions_document CASCADE;
DROP TABLE IF EXISTS apptransactions_documenttype CASCADE;
DROP TABLE IF EXISTS apptransactions_partytype CASCADE;
DROP TABLE IF EXISTS apptransactions_partycategory CASCADE;
DROP TABLE IF EXISTS apptransactions_party CASCADE;
DROP TABLE IF EXISTS apptransactions_workaccount CASCADE;
DROP TABLE IF EXISTS apptransactions_transactionfavorite CASCADE;

-- Eliminar tablas de auditapp
DROP TABLE IF EXISTS auditapp_useractionlog CASCADE;

-- Eliminar tablas de crewsapp
DROP TABLE IF EXISTS crewsapp_category CASCADE;
DROP TABLE IF EXISTS crewsapp_crew CASCADE;
DROP TABLE IF EXISTS crewsapp_truck CASCADE;
DROP TABLE IF EXISTS crewsapp_truckassignment CASCADE;

-- Eliminar tablas de ctrctsapp
DROP TABLE IF EXISTS ctrctsapp_contractdetails CASCADE;
DROP TABLE IF EXISTS ctrctsapp_contract CASCADE;
DROP TABLE IF EXISTS ctrctsapp_workprice CASCADE;
DROP TABLE IF EXISTS ctrctsapp_housemodel CASCADE;
DROP TABLE IF EXISTS ctrctsapp_job CASCADE;
DROP TABLE IF EXISTS ctrctsapp_builder CASCADE;

-- Eliminar registros de migraciones de estas apps
DELETE FROM django_migrations WHERE app IN ('appschedule', 'apptransactions', 'auditapp', 'crewsapp', 'ctrctsapp');
```

## Paso 2: Crear Nuevas Migraciones

Una vez eliminadas las tablas, ejecuta en el Web Shell:

```bash
# Crear migraciones para todas las apps
python manage.py makemigrations

# O crear migraciones por app específica
python manage.py makemigrations appschedule
python manage.py makemigrations apptransactions
python manage.py makemigrations auditapp
python manage.py makemigrations crewsapp
python manage.py makemigrations ctrctsapp
```

## Paso 3: Aplicar Migraciones

```bash
python manage.py migrate
```

## Paso 4: Verificar

```bash
python manage.py showmigrations
```

Deberías ver todas las migraciones aplicadas correctamente.

---

## Alternativa: Eliminar Todo y Empezar de Cero

Si quieres eliminar TODAS las tablas y empezar completamente de cero:

```sql
-- ⚠️ CUIDADO: Esto elimina TODAS las tablas
-- Ejecutar desde el Shell de Render: python manage.py dbshell

-- Eliminar todas las tablas de Django
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

-- Eliminar todos los registros de migraciones
DELETE FROM django_migrations;
```

Luego ejecuta:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Nota sobre Datos

⚠️ **ADVERTENCIA:** Estos comandos eliminarán todos los datos de estas tablas. Asegúrate de tener un backup si necesitas los datos.

