# Resumen Rápido: Docker y PostgreSQL

## 🐋 ¿Qué es Docker?

**Docker** = Caja que contiene todo lo necesario para que PostgreSQL funcione, sin instalar nada en tu Windows.

### Ventaja Principal:
```
Sin Docker:  PostgreSQL → Se instala en Windows → Puede causar problemas
Con Docker:  PostgreSQL → Corre en una caja aislada → Cero conflictos
```

---

## 📜 Los Dos Scripts

### 1. `docker-postgres-setup.ps1` 
**¿Qué hace?** Crea e instala PostgreSQL por primera vez

**¿Cuándo?** Una sola vez (o cuando necesitas empezar de cero)

**¿Qué hace dentro?**
1. Verifica que Docker esté corriendo
2. Elimina contenedores anteriores si existen
3. Descarga PostgreSQL 16
4. Lo instala y configura
5. Lo pone a correr
6. Te da la información de conexión

**Comando:**
```powershell
.\docker-postgres-setup.ps1
```

---

### 2. `docker-postgres-manage.ps1`
**¿Qué hace?** Controla tu PostgreSQL que ya está instalado

**¿Cuándo?** Todos los días (iniciar, detener, ver logs, hacer backups)

**Comandos útiles:**
```powershell
# Ver si está corriendo
.\docker-postgres-manage.ps1 -Action status

# Iniciar PostgreSQL
.\docker-postgres-manage.ps1 -Action start

# Detener PostgreSQL
.\docker-postgres-manage.ps1 -Action stop

# Conectar a la base de datos
.\docker-postgres-manage.ps1 -Action connect

# Ver qué está pasando (logs)
.\docker-postgres-manage.ps1 -Action logs

# Crear backup de datos
.\docker-postgres-manage.ps1 -Action backup
```

---

## 🔄 Flujo de Trabajo Diario

### Primera Vez:
```
1. .\docker-postgres-setup.ps1          ← Crear PostgreSQL
2. Abrir tu aplicación Django
3. Trabajar normalmente
```

### Todos los Días:
```
1. Abrir Docker Desktop (si no está abierto)
2. .\docker-postgres-manage.ps1 -Action start    ← Si está detenido
3. Abrir tu aplicación Django
4. Trabajar normalmente
5. .\docker-postgres-manage.ps1 -Action stop     ← Opcional: si quieres detenerlo
```

---

## 🎯 Conceptos Clave

### **Contenedor**
- Es la "caja" donde corre PostgreSQL
- Puede estar "corriendo" o "detenido"
- Se llama: `chalan-postgres`

### **Datos Persisten**
- Aunque cierres Docker, tus datos NO se pierden
- Están en un "volumen" que persiste
- Solo se pierden si los eliminas explícitamente

### **Puerto 5432**
- Es la "puerta" de conexión
- Tu aplicación se conecta a `localhost:5432`
- Docker reenvía al contenedor

---

## ⚙️ Configuración

```
Host: localhost
Puerto: 5432
Usuario: postgres
Contraseña: chalan2024
Base de datos: chalan_inv_txn
```

---

## 🆘 Solución Rápida de Problemas

### "No puedo conectarme"
```powershell
.\docker-postgres-manage.ps1 -Action status  # Ver si está corriendo
.\docker-postgres-manage.ps1 -Action start   # Iniciar si está detenido
.\docker-postgres-manage.ps1 -Action logs    # Ver errores
```

### "Quiero empezar de cero"
```powershell
.\docker-postgres-manage.ps1 -Action remove  # Eliminar contenedor
docker volume rm chalan-postgres-data        # Eliminar datos (CUIDADO!)
.\docker-postgres-setup.ps1                  # Recrear
```

### "Crear backup antes de cambiar algo"
```powershell
.\docker-postgres-manage.ps1 -Action backup
```

---

## 📚 Archivos de Documentación

1. **EXPLICACION-DOCKER.md** - Explicación detallada completa
2. **README-DOCKER.md** - Guía paso a paso de instalación
3. **COMANDOS-RAPIDOS.md** - Lista de todos los comandos
4. **RESUMEN-RAPIDO.md** - Este archivo (lo esencial)

---

## ✨ Ventajas de Usar Docker

✅ **Fácil:** Un comando instala todo
✅ **Limpio:** No afecta tu Windows
✅ **Confiable:** Misma configuración siempre
✅ **Portable:** Funciona igual en cualquier máquina
✅ **Controlable:** Fácil de detener, iniciar, reinstalar

---

¡Eso es todo! 🎉

