# Explicación: Docker y los Scripts de PostgreSQL

## ¿Qué es Docker?

Docker es una plataforma que permite **empaquetar y ejecutar aplicaciones en contenedores**. Piensa en los contenedores como cajas que contienen todo lo necesario para que una aplicación funcione:

- El sistema operativo necesario
- La aplicación en sí
- Todas sus dependencias
- Configuración

### Ventajas de Docker vs Instalación Tradicional

#### **Instalación Tradicional (como PostgreSQL 18 en Windows):**
```
PostgreSQL → Se instala en Windows → Conflictos con otros programas
           → Problemas de configuración
           → Dependencias del sistema
           → Difícil de limpiar
```

#### **Con Docker:**
```
PostgreSQL → Se ejecuta en un contenedor aislado → No afecta tu sistema
           → Viene preconfigurado
           → Todo incluido en el contenedor
           → Fácil de eliminar y reinstalar
```

### Analogía Simple

Imagina que:
- **Instalación tradicional** = Construir un edificio (requiere cimientos, permisos, tiempo)
- **Docker** = Traer una casa prefabricada en un camión y colocarla (rápido, limpio, fácil de quitar)

## ¿Qué hace `docker-postgres-setup.ps1`?

Este script **crea e inicializa** tu contenedor de PostgreSQL por primera vez.

### Pasos que realiza:

1. **Verifica Docker** ✅
   - Comprueba que Docker Desktop esté instalado
   - Comprueba que Docker Desktop esté corriendo

2. **Limpia contenedores anteriores** 🧹
   - Si ya existe un contenedor `chalan-postgres`, lo detiene y elimina
   - Esto asegura un inicio limpio

3. **Crea el contenedor PostgreSQL** 📦
   ```powershell
   docker run --name chalan-postgres `
       -e POSTGRES_USER=postgres `
       -e POSTGRES_PASSWORD=chalan2024 `
       -e POSTGRES_DB=chalan_inv_txn `
       -p 5432:5432 `
       -v chalan-postgres-data:/var/lib/postgresql/data `
       -d postgres:16
   ```

   **Parámetros explicados:**
   - `--name chalan-postgres`: Nombre del contenedor
   - `-e POSTGRES_USER=postgres`: Usuario de la base de datos
   - `-e POSTGRES_PASSWORD=chalan2024`: Contraseña
   - `-e POSTGRES_DB=chalan_inv_txn`: Nombre de la base de datos a crear
   - `-p 5432:5432`: Mapea el puerto 5432 del contenedor al puerto 5432 de tu máquina
   - `-v chalan-postgres-data:/var/lib/postgresql/data`: Persiste los datos en un volumen
   - `-d`: Ejecuta en segundo plano (detached mode)
   - `postgres:16`: Imagen oficial de PostgreSQL versión 16

4. **Espera a que PostgreSQL inicie** ⏳
   - Verifica cada segundo si PostgreSQL está listo
   - Muestra puntos (...) mientras espera

5. **Muestra información de conexión** 📋
   - Imprime todos los datos necesarios para conectarte

### ¿Cuándo usar este script?

- **Primera vez**: Cuando instalas PostgreSQL en Docker
- **Recrear**: Si necesitas empezar de cero
- **Después de eliminar**: Si borraste el contenedor por error

## ¿Qué hace `docker-postgres-manage.ps1`?

Este script **gestiona** un contenedor que ya existe. Es tu "control remoto" para PostgreSQL.

### Acciones disponibles:

#### 1. **status** - Ver Estado
```powershell
.\docker-postgres-manage.ps1 -Action status
```
Muestra si el contenedor está corriendo o detenido.

#### 2. **start** - Iniciar
```powershell
.\docker-postgres-manage.ps1 -Action start
```
Inicia el contenedor si está detenido. Docker Desktop puede apagarse y el contenedor se detiene.

#### 3. **stop** - Detener
```powershell
.\docker-postgres-manage.ps1 -Action stop
```
Detiene el contenedor sin eliminar datos.

#### 4. **restart** - Reiniciar
```powershell
.\docker-postgres-manage.ps1 -Action restart
```
Detiene y vuelve a iniciar el contenedor. Útil si hay problemas.

#### 5. **logs** - Ver Logs
```powershell
.\docker-postgres-manage.ps1 -Action logs
```
Muestra los últimos 50 logs en tiempo real.

#### 6. **connect** - Conectar
```powershell
.\docker-postgres-manage.ps1 -Action connect
```
Abre la terminal de PostgreSQL (psql).

#### 7. **backup** - Crear Respaldo
```powershell
.\docker-postgres-manage.ps1 -Action backup
```
Genera un archivo `.sql` con todos los datos.

#### 8. **remove** - Eliminar
```powershell
.\docker-postgres-manage.ps1 -Action remove
```
Borra el contenedor (los datos se mantienen en el volumen).

### ¿Cuándo usar este script?

- **Todos los días**: Para iniciar, detener, ver logs
- **Debugging**: Para revisar errores con `logs`
- **Mantenimiento**: Para respaldos y reinicios

## Comparación Visual

### Flujo de Trabajo con Docker

```
┌─────────────────────────────────────────────────────────┐
│                    PRIMER DÍA                           │
└─────────────────────────────────────────────────────────┘
1. Ejecutar: docker-postgres-setup.ps1
   ↓
2. PostgreSQL se crea y empieza a correr
   ↓
3. Ya puedes conectarte

┌─────────────────────────────────────────────────────────┐
│                    DÍAS SIGUIENTES                      │
└─────────────────────────────────────────────────────────┘
1. Abrir Docker Desktop
   ↓
2. Verificar estado: .\docker-postgres-manage.ps1 -Action status
   ↓
3. Si está detenido: .\docker-postgres-manage.ps1 -Action start
   ↓
4. Trabajar con tu aplicación
   ↓
5. Si quieres detener: .\docker-postgres-manage.ps1 -Action stop
```

## Conceptos Importantes de Docker

### 1. **Contenedor** 🐋
Es la "caja" que contiene tu aplicación corriendo.

**Tu contenedor:** `chalan-postgres`
- Estado: Puede estar corriendo o detenido
- Datos: Se guardan en un volumen (persisten)
- Red: Tiene su propia red interna

### 2. **Imagen** 📦
Es el "molde" o "plantilla" del contenedor. La imagen no cambia, solo creas contenedores a partir de ella.

**Tu imagen:** `postgres:16`
- Descargada desde Docker Hub
- Oficial de PostgreSQL
- Lista para usar

### 3. **Volumen** 💾
Es donde Docker guarda los datos persistentes.

**Tu volumen:** `chalan-postgres-data`
- Almacena todas las bases de datos
- Persiste aunque elimines el contenedor
- Ubicación física en Windows: `C:\Users\[tu_usuario]\AppData\Local\Docker\wsl\data\ext4.vhdx`

### 4. **Puerto** 🔌
Es la "puerta" de comunicación entre tu máquina y el contenedor.

**Tu puerto:** `5432`
- Tu máquina escucha en `localhost:5432`
- El contenedor recibe en `5432`
- Docker conecta ambos

## Comandos Docker Fundamentales

Si prefieres usar Docker directamente en lugar de los scripts:

### Ver todos los contenedores
```bash
docker ps -a
```

### Ver solo el tuyo
```bash
docker ps -a | findstr chalan-postgres
```

### Iniciar contenedor
```bash
docker start chalan-postgres
```

### Detener contenedor
```bash
docker stop chalan-postgres
```

### Ver logs
```bash
docker logs chalan-postgres
docker logs -f chalan-postgres  # Seguir en tiempo real
```

### Ejecutar comando en el contenedor
```bash
docker exec chalan-postgres psql -U postgres -d chalan_inv_txn -c "SELECT version();"
```

### Conectar interactivamente
```bash
docker exec -it chalan-postgres psql -U postgres -d chalan_inv_txn
```

### Eliminar contenedor (mantener datos)
```bash
docker rm chalan-postgres
```

### Eliminar contenedor (eliminar datos)
```bash
docker rm -f chalan-postgres
docker volume rm chalan-postgres-data
```

## ¿Dónde se Guardan los Datos?

### Sí, son persistentes ✅

Los datos se guardan en un **volumen de Docker**, no en el contenedor. Esto significa:

- ✅ Si eliminas el contenedor: Los datos se mantienen
- ✅ Si reinicias Docker Desktop: Los datos se mantienen
- ✅ Si apagas Windows: Los datos se mantienen
- ✅ Si recreas el contenedor: Los datos se mantienen

### Ubicación Física

En Windows, Docker usa WSL2 (Windows Subsystem for Linux) para almacenar volúmenes:

```
Ubicación aproximada:
C:\Users\[TU_USUARIO]\AppData\Local\Docker\wsl\data\ext4.vhdx
```

**NO edites este archivo directamente**, usa los comandos de Docker o los scripts.

## Escenarios Comunes

### Escenario 1: "Docker Desktop se cerró"
**Síntoma:** No puedes conectarte a PostgreSQL

**Solución:**
```powershell
# 1. Abrir Docker Desktop
# 2. Esperar a que inicie
# 3. Verificar estado
.\docker-postgres-manage.ps1 -Action status

# 4. Si está detenido, iniciar
.\docker-postgres-manage.ps1 -Action start
```

### Escenario 2: "Quiero empezar de cero"
**Síntoma:** Problemas con la base de datos, quieres resetear

**Solución:**
```powershell
# 1. Detener y eliminar contenedor
.\docker-postgres-manage.ps1 -Action remove

# 2. Eliminar volumen (CUIDADO: borra datos)
docker volume rm chalan-postgres-data

# 3. Crear de nuevo
.\docker-postgres-setup.ps1
```

### Escenario 3: "Crear respaldo antes de cambios"
**Síntoma:** Vas a hacer una migración importante

**Solución:**
```powershell
# Crear backup con fecha
.\docker-postgres-manage.ps1 -Action backup

# Esto crea: chalan_postgres_backup_YYYYMMDD_HHMMSS.sql
```

### Escenario 4: "Ver qué está pasando"
**Síntoma:** Errores inesperados

**Solución:**
```powershell
# Ver últimas líneas de log
.\docker-postgres-manage.ps1 -Action logs

# O con Docker directo
docker logs chalan-postgres --tail 100
```

## Ventajas de Este Enfoque

### ✅ Facilidad
- Un solo comando para instalar
- Sin configuración compleja
- Sin conflictos con el sistema

### ✅ Portabilidad
- Mismo entorno en cualquier máquina
- Fácil de replicar
- Trabajo en equipo sin diferencias

### ✅ Limpieza
- Eliminar = Un comando
- No deja rastros en Windows
- Reinstalar = Otro comando

### ✅ Control
- Versión específica (PostgreSQL 16)
- Configuración conocida
- Fácil de actualizar

## Next Steps

Ahora que PostgreSQL está corriendo:

1. **Conectar desde tu aplicación Django:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'chalan_inv_txn',
           'USER': 'postgres',
           'PASSWORD': 'chalan2024',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

2. **Ejecutar migraciones:**
   ```bash
   python manage.py migrate
   ```

3. **Crear superusuario:**
   ```bash
   python manage.py createsuperuser
   ```

¡Todo listo! 🎉

