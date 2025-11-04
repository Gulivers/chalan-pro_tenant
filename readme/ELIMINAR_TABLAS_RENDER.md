# 🔗 Conectar a chalan-db desde Render (Sin pgAdmin)

## Problema con pgAdmin

Render bloquea conexiones externas por defecto. Las bases de datos en Render solo aceptan conexiones **internas** (desde otros servicios de Render) o necesitas habilitar acceso externo manualmente.

## Solución: Usar el Web Shell de Render

Es la forma más fácil y directa de ejecutar SQL en Render.

### Paso 1: Acceder al Web Shell

1. Ve al [Render Dashboard](https://dashboard.render.com)
2. Navega a tu servicio `chalan-backend`
3. Haz clic en **Shell** en el menú lateral izquierdo
4. Espera a que se abra la terminal

### Paso 2: Conectar a la Base de Datos

En el Shell, ejecuta:

```bash
python manage.py dbshell
```

Esto abrirá una conexión directa a PostgreSQL.

### Paso 3: Ejecutar los Comandos SQL

Una vez conectado, copia y pega **todo este bloque** de SQL:

```sql
DROP TABLE IF EXISTS appschedule_event CASCADE;
DROP TABLE IF EXISTS appschedule_eventdraft CASCADE;
DROP TABLE IF EXISTS appschedule_eventimage CASCADE;
DROP TABLE IF EXISTS appschedule_eventnote CASCADE;
DROP TABLE IF EXISTS appschedule_eventchatmessage CASCADE;
DROP TABLE IF EXISTS appschedule_eventchatreadstatus CASCADE;
DROP TABLE IF EXISTS appschedule_absencereason CASCADE;
DROP TABLE IF EXISTS apptransactions_documentline CASCADE;
DROP TABLE IF EXISTS apptransactions_document CASCADE;
DROP TABLE IF EXISTS apptransactions_documenttype CASCADE;
DROP TABLE IF EXISTS apptransactions_partytype CASCADE;
DROP TABLE IF EXISTS apptransactions_partycategory CASCADE;
DROP TABLE IF EXISTS apptransactions_party CASCADE;
DROP TABLE IF EXISTS apptransactions_workaccount CASCADE;
DROP TABLE IF EXISTS apptransactions_transactionfavorite CASCADE;
DROP TABLE IF EXISTS auditapp_useractionlog CASCADE;
DROP TABLE IF EXISTS crewsapp_category CASCADE;
DROP TABLE IF EXISTS crewsapp_crew CASCADE;
DROP TABLE IF EXISTS crewsapp_truck CASCADE;
DROP TABLE IF EXISTS crewsapp_truckassignment CASCADE;
DROP TABLE IF EXISTS ctrctsapp_contractdetails CASCADE;
DROP TABLE IF EXISTS ctrctsapp_contract CASCADE;
DROP TABLE IF EXISTS ctrctsapp_workprice CASCADE;
DROP TABLE IF EXISTS ctrctsapp_housemodel CASCADE;
DROP TABLE IF EXISTS ctrctsapp_job CASCADE;
DROP TABLE IF EXISTS ctrctsapp_builder CASCADE;
DELETE FROM django_migrations WHERE app IN ('appschedule', 'apptransactions', 'auditapp', 'crewsapp', 'ctrctsapp');
```

4. Presiona Enter para ejecutar

### Paso 4: Salir del dbshell

Escribe `\q` y presiona Enter para salir.

---

## Alternativa: Ejecutar SQL desde Python

Si `dbshell` no funciona, puedes ejecutar SQL directamente desde Python:

```bash
python manage.py shell
```

Luego ejecuta:

```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("DROP TABLE IF EXISTS appschedule_event CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS appschedule_eventdraft CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS appschedule_eventimage CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS appschedule_eventnote CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS appschedule_eventchatmessage CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS appschedule_eventchatreadstatus CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS appschedule_absencereason CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS apptransactions_documentline CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS apptransactions_document CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS apptransactions_documenttype CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS apptransactions_partytype CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS apptransactions_partycategory CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS apptransactions_party CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS apptransactions_workaccount CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS apptransactions_transactionfavorite CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS auditapp_useractionlog CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS crewsapp_category CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS crewsapp_crew CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS crewsapp_truck CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS crewsapp_truckassignment CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS ctrctsapp_contractdetails CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS ctrctsapp_contract CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS ctrctsapp_workprice CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS ctrctsapp_housemodel CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS ctrctsapp_job CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS ctrctsapp_builder CASCADE;")
    cursor.execute("DELETE FROM django_migrations WHERE app IN ('appschedule', 'apptransactions', 'auditapp', 'crewsapp', 'ctrctsapp');")
    
print("Tablas eliminadas correctamente")
```

---

## Habilitar Conexión Externa en Render (Opcional)

Si realmente necesitas conectar desde pgAdmin:

1. Ve al Dashboard de Render → Tu base de datos `chalan-db`
2. Ve a **Connections**
3. Busca la opción **Allow External Connections** (puede estar en Settings)
4. Habilítala si está disponible
5. Usa la **External Database URL** que aparece ahí

⚠️ **Nota:** Algunos planes de Render no permiten conexiones externas por seguridad.

---

## Verificar que las Tablas fueron Eliminadas

Desde el Web Shell:

```bash
python manage.py dbshell
```

Luego ejecuta:

```sql
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND (
    tablename LIKE 'appschedule%' OR 
    tablename LIKE 'apptransactions%' OR 
    tablename LIKE 'auditapp%' OR 
    tablename LIKE 'crewsapp%' OR 
    tablename LIKE 'ctrctsapp%'
);
```

Si no devuelve resultados, las tablas fueron eliminadas correctamente.
