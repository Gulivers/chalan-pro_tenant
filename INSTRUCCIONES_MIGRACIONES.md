# Instrucciones para configurar migraciones automáticas en Render

## Opción 1: Actualizar Build Command en el Dashboard (RECOMENDADO)

1. Ve a: https://dashboard.render.com/web/srv-d44nroripnbc73angjdg/settings
2. En la sección "Build & Deploy", busca "Build Command"
3. Reemplaza el comando actual con:

```bash
pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput
```

4. Guarda los cambios. Render ejecutará las migraciones automáticamente en cada despliegue.

## Opción 2: Usar el Script de Inicio (ALTERNATIVA)

Si prefieres ejecutar las migraciones al iniciar el servidor (cada vez que se reinicia):

1. Ve a: https://dashboard.render.com/web/srv-d44nroripnbc73angjdg/settings
2. En "Start Command", cambia a:

```bash
bash start.sh
```

Nota: Esta opción ejecuta las migraciones cada vez que el servidor se reinicia, lo cual puede ser más lento.

## Opción 3: Usar render.yaml (SI TIENES ACCESO SSH)

Si Render detecta tu archivo render.yaml, puede usar la configuración automática. 
El archivo render.yaml ya tiene las migraciones configuradas.

## Verificar que las migraciones funcionan

Después de actualizar el build command:
1. Ve a la pestaña "Logs" del servicio
2. Busca en los logs del build la línea: "Running migrations..."
3. Deberías ver las tablas creadas exitosamente

## Vincular la Base de Datos (IMPORTANTE)

Antes de que las migraciones funcionen, asegúrate de que la base de datos esté vinculada:

1. Ve a: https://dashboard.render.com/web/srv-d44nroripnbc73angjdg
2. En la sección "Environment", busca "Link Database"
3. Selecciona "chalan-db" de la lista
4. Esto creará automáticamente la variable DATABASE_URL

Si no ves la opción "Link Database":
1. Ve a "Environment" > "Add Environment Variable"
2. Key: `DATABASE_URL`
3. Value: Ve a tu base de datos en https://dashboard.render.com/d/dpg-d44nlg0dl3ps73bfp1cg-a
4. Copia la "Internal Database URL" y pégala como valor
