# Docker Compose vs Scripts Individuales

## 🎯 ¿Por qué existen dos formas de hacer lo mismo?

Tienes **dos formas** de gestionar PostgreSQL en Docker:

### 📜 Método 1: Scripts Individuales
- `docker-postgres-setup.ps1` - Instalar PostgreSQL solo
- `docker-postgres-manage.ps1` - Gestionar PostgreSQL solo

### 🐳 Método 2: Docker Compose
- `docker-compose-local.yml` - PostgreSQL + pgAdmin juntos

---

## 🔄 ¿Cuál usar?

### Usa **Scripts Individuales** cuando:
- ✅ Solo necesitas PostgreSQL
- ✅ No quieres pgAdmin
- ✅ Prefieres control manual
- ✅ Estás aprendiendo Docker

### Usa **Docker Compose** cuando:
- ✅ Necesitas PostgreSQL **Y** pgAdmin juntos
- ✅ Quieres gestionar múltiples servicios
- ✅ Prefieres configuración declarativa
- ✅ Quieres todo en un solo comando

---

## 📊 Comparación Detallada

| Característica | Scripts Individuales | Docker Compose |
|---|---|---|
| PostgreSQL | ✅ Sí | ✅ Sí |
| pgAdmin | ❌ No (instalación separada) | ✅ Sí |
| Archivos | 2 scripts (.ps1) | 1 archivo (.yml) |
| Comando inicio | `.\docker-postgres-setup.ps1` | `docker-compose up -d` |
| Comando detener | `docker stop chalan-postgres` | `docker-compose down` |
| Volumen datos | chalan-postgres-data | chalan-postgres-data |
| Red | default | chalan-network |
| Dependencias | Manual | Automático (depends_on) |

---

## ⚠️ IMPORTANTE: No mezclar ambos métodos

**NO puedes usar ambos métodos al mismo tiempo** porque ambos intentan crear un contenedor con el mismo nombre: `chalan-postgres`

### Problema común:
```powershell
# Usaste scripts
.\docker-postgres-setup.ps1

# Luego intentas usar compose
docker-compose -f docker-compose-local.yml up -d

# ERROR: El contenedor chalan-postgres ya existe
```

### Solución:
```powershell
# 1. Detener y eliminar el contenedor viejo
docker stop chalan-postgres
docker rm chalan-postgres

# 2. Usar el nuevo método
docker-compose -f docker-compose-local.yml up -d
```

---

## 🎯 Recomendación

### Para tu caso actual (con pgAdmin):
**✅ Usa Docker Compose**

```powershell
# Iniciar todo
docker-compose -f docker-compose-local.yml up -d

# Ver estado
docker-compose -f docker-compose-local.yml ps

# Detener
docker-compose -f docker-compose-local.yml down
```

### Si quieres volver a scripts individuales:
**✅ Usa Scripts Individuales**

```powershell
# Primero elimina los contenedores de compose
docker-compose -f docker-compose-local.yml down

# Luego usa los scripts
.\docker-postgres-setup.ps1
.\docker-postgres-manage.ps1 -Action start
```

---

## 📁 Estructura de Archivos

```
chalan_inv_txn/
├── docker-postgres-setup.ps1       ← Script: Instalar PostgreSQL
├── docker-postgres-manage.ps1      ← Script: Gestionar PostgreSQL
├── docker-compose-local.yml        ← Compose: PostgreSQL + pgAdmin
├── test-postgres-connection.ps1    ← Script: Probar conexión
└── readme/
    ├── README-DOCKER.md
    ├── GUIA-PGADMIN.md
    ├── EXPLICACION-DOCKER.md
    └── COMANDOS-RAPIDOS.md
```

---

## 🔧 Comandos de Gestión

### Con Scripts Individuales

```powershell
# Iniciar
.\docker-postgres-manage.ps1 -Action start

# Detener
.\docker-postgres-manage.ps1 -Action stop

# Estado
.\docker-postgres-manage.ps1 -Action status

# Logs
.\docker-postgres-manage.ps1 -Action logs

# Conectar
.\docker-postgres-manage.ps1 -Action connect

# Backup
.\docker-postgres-manage.ps1 -Action backup
```

### Con Docker Compose

```powershell
# Iniciar todo
docker-compose -f docker-compose-local.yml up -d

# Ver estado
docker-compose -f docker-compose-local.yml ps

# Ver logs
docker-compose -f docker-compose-local.yml logs

# Logs en tiempo real
docker-compose -f docker-compose-local.yml logs -f

# Logs solo de PostgreSQL
docker-compose -f docker-compose-local.yml logs postgres

# Logs solo de pgAdmin
docker-compose -f docker-compose-local.yml logs pgadmin

# Detener servicios
docker-compose -f docker-compose-local.yml stop

# Iniciar servicios
docker-compose -f docker-compose-local.yml start

# Reiniciar servicios
docker-compose -f docker-compose-local.yml restart

# Eliminar contenedores (mantiene datos)
docker-compose -f docker-compose-local.yml down

# Eliminar TODO (datos incluidos)
docker-compose -f docker-compose-local.yml down -v

# Ejecutar comando en PostgreSQL
docker-compose -f docker-compose-local.yml exec postgres psql -U postgres -d chalan_inv_txn

# Conectar a pgAdmin
# Abre: http://localhost:5050
```

---

## 💡 Ventajas de Cada Método

### Scripts Individuales
- ✅ Más simples de entender
- ✅ Paso a paso manual
- ✅ Bueno para aprender
- ✅ Menos configuración
- ❌ No incluye pgAdmin
- ❌ Más comandos para gestionar

### Docker Compose
- ✅ Todo configurado en un archivo
- ✅ PostgreSQL + pgAdmin juntos
- ✅ Gestión unificada
- ✅ Dependencias automáticas
- ✅ Red personalizada
- ✅ Fácil de compartir
- ❌ Más complejo de entender
- ❌ Requiere conocer YAML

---

## 🎓 Cuándo Cambiar de Método

### Cambiar de Scripts → Compose

**Cuándo:** Cuando necesitas pgAdmin

```powershell
# 1. Detener scripts
docker stop chalan-postgres
docker rm chalan-postgres

# 2. Usar compose
docker-compose -f docker-compose-local.yml up -d
```

### Cambiar de Compose → Scripts

**Cuándo:** Cuando no necesitas pgAdmin

```powershell
# 1. Detener compose
docker-compose -f docker-compose-local.yml down

# 2. Usar scripts
.\docker-postgres-setup.ps1
```

---

## 🔄 Migración de Datos

**Buenas noticias:** Ambos métodos usan el mismo volumen de datos (`chalan-postgres-data`), por lo que puedes cambiar entre métodos sin perder datos.

### Ejemplo:

```powershell
# Usas scripts y tienes datos
.\docker-postgres-setup.ps1
# ... creas tablas, insertas datos ...

# Cambias a compose
docker stop chalan-postgres
docker rm chalan-postgres
docker-compose -f docker-compose-local.yml up -d

# ¡Tus datos siguen ahí! ✅
```

---

## 📝 Resumen

- **Ahora usas:** Docker Compose (PostgreSQL + pgAdmin)
- **Puedes cambiar a:** Scripts individuales (solo PostgreSQL)
- **Los datos se mantienen** en ambos casos
- **No mezcles** ambos métodos a la vez

---

## 🆘 Si hay Conflicto

Si intentas ejecutar uno y te dice que el contenedor ya existe:

```powershell
# Ver qué está corriendo
docker ps -a | findstr chalan

# Detener y eliminar TODO
docker stop chalan-postgres chalan-pgadmin
docker rm chalan-postgres chalan-pgadmin

# O si usas compose
docker-compose -f docker-compose-local.yml down

# Luego inicia el que quieras usar
```

