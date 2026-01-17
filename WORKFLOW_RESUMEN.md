# 📋 Resumen: Homologación Desarrollo Local ↔ Producción VPS

## 🎯 Objetivo
Mantener `main` estable para producción (VPS Hostinger) mientras desarrollas en local (ubuntu-house) sin romper el sistema en producción.

## 🔀 Estrategia de Ramas

```
main (Producción VPS)
  ↑
  │ (solo después de pruebas completas)
  │
develop (Desarrollo/Staging)
  ↑
  │ (merge de features probadas)
  │
feature/* (Nuevas funcionalidades)
  │
ubuntu_house (Configuraciones locales)
```

## 📝 Workflow Paso a Paso

### 1️⃣ Setup Inicial (Primera vez)
```bash
cd ~/shared/projects/chalanpro
./scripts/git-workflow.sh setup
```

### 2️⃣ Desarrollo Normal
```bash
# Crear feature branch
./scripts/git-workflow.sh create-feature
# Nombre: schedule-fix

# Desarrollar y commitear
git add .
git commit -m "feat: mejorar schedule con FullCalendar"

# Merge a develop
./scripts/git-workflow.sh merge-to-develop

# Probar en ubuntu-house
# ... pruebas ...

# Cuando esté listo: merge a main
./scripts/git-workflow.sh merge-to-main
```

### 3️⃣ En VPS Hostinger (Después de push a main)
```bash
# En el VPS
cd /opt/chalanpro/app
git pull origin main
docker compose restart backend frontend nginx
```

## 🛡️ Protecciones

- ✅ `main` solo recibe merges desde `develop` (después de pruebas)
- ✅ Scripts con confirmaciones antes de merge a `main`
- ✅ `ubuntu_house` separada para configuraciones locales
- ✅ Feature branches para trabajo aislado

## 📚 Documentación Completa

- **Workflow detallado:** `GIT_WORKFLOW.md`
- **Comandos del script:** `./scripts/git-workflow.sh help`
- **README local:** `app/readme/README_RESUMEN_GENERAL_MY-LOCAL.md`

