# Inicio Rápido: PostgreSQL + pgAdmin en Docker

## ⚡ Comandos Rápidos

### 1. Detener el contenedor manual si existe
```powershell
docker stop chalan-postgres 2>$null
docker rm chalan-postgres 2>$null
```

### 2. Iniciar PostgreSQL + pgAdmin
```powershell
docker-compose -f docker-compose-local.yml up -d
```

### 3. Verificar que estén corriendo
```powershell
docker-compose -f docker-compose-local.yml ps
```

### 4. Acceder a pgAdmin
Abre tu navegador en: **http://localhost:5050**

**Credenciales:**
- Email: `admin@chalan.com`
- Contraseña: `chalan2024`

### 5. Conectar pgAdmin a PostgreSQL

Dentro de pgAdmin:
1. Clic derecho en "Servers" → Register → Server
2. **General Tab:**
   - Name: `Chalan PostgreSQL`
3. **Connection Tab:**
   - Host: `chalan-postgres`
   - Port: `5432`
   - Database: `postgres`
   - Username: `postgres`
   - Password: `chalan2024`
   - ✅ Save password
4. Click Save

## 🛠️ Gestión

### Detener servicios
```powershell
docker-compose -f docker-compose-local.yml stop
```

### Iniciar servicios
```powershell
docker-compose -f docker-compose-local.yml start
```

### Reiniciar servicios
```powershell
docker-compose -f docker-compose-local.yml restart
```

### Ver logs
```powershell
docker-compose -f docker-compose-local.yml logs -f
```

### Detener y eliminar todo
```powershell
docker-compose -f docker-compose-local.yml down
```

### Detener y eliminar TODO (incluyendo datos)
```powershell
docker-compose -f docker-compose-local.yml down -v
```

