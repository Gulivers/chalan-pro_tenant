# Git Workflow - Desarrollo Local y Producción VPS

## Objetivo
Mantener la rama `main` estable para producción (VPS Hostinger) mientras se desarrolla en local (ubuntu-house) sin romper el sistema en producción.

## Estrategia de Ramas

### Ramas Principales

1. **`main`** (Producción)
   - ✅ **Solo código probado y estable**
   - ✅ Usado por el VPS en Hostinger
   - ✅ **NUNCA** hacer push directo de cambios experimentales
   - ✅ Solo recibe merges desde `develop` después de pruebas completas

2. **`develop`** (Desarrollo/Staging)
   - ✅ Rama de integración para desarrollo
   - ✅ Todos los cambios de desarrollo se integran aquí primero
   - ✅ Se prueba en ubuntu-house antes de merge a `main`
   - ✅ Puede tener commits que aún no están listos para producción

3. **`ubuntu_house`** (Desarrollo Local Específico)
   - ✅ Configuraciones específicas del ambiente local
   - ✅ Cambios experimentales y pruebas
   - ✅ Puede divergir de `develop` temporalmente

4. **Feature Branches** (Ramas de Funcionalidad)
   - ✅ Se crean desde `develop` para nuevas features
   - ✅ Ejemplo: `feature/schedule-fix`, `feature/new-endpoint`
   - ✅ Se mergean a `develop` cuando están completas

## Workflow Recomendado

### Escenario 1: Desarrollo Normal (Nueva Feature)

```bash
# 1. Asegurarse de estar en develop y actualizado
git checkout develop
git pull origin develop

# 2. Crear rama de feature
git checkout -b feature/nombre-feature

# 3. Desarrollar y hacer commits
git add .
git commit -m "feat: descripción del cambio"

# 4. Push de la feature branch
git push origin feature/nombre-feature

# 5. Merge a develop (local o via PR en GitHub)
git checkout develop
git merge feature/nombre-feature
git push origin develop

# 6. Probar en ubuntu-house con develop
# ... pruebas locales ...

# 7. Solo cuando esté listo: merge a main
git checkout main
git pull origin main
git merge develop
git push origin main

# 8. En VPS Hostinger: hacer pull de main
# (esto se puede automatizar con webhook o manual)
```

### Escenario 2: Hotfix Urgente para Producción

```bash
# 1. Crear hotfix desde main
git checkout main
git pull origin main
git checkout -b hotfix/descripcion-fix

# 2. Hacer el fix
git add .
git commit -m "fix: descripción del hotfix"

# 3. Merge a main (urgente)
git checkout main
git merge hotfix/descripcion-fix
git push origin main

# 4. También merge a develop para mantener sincronizado
git checkout develop
git merge hotfix/descripcion-fix
git push origin develop
```

### Escenario 3: Configuración Local Específica (ubuntu-house)

```bash
# 1. Trabajar en ubuntu_house para cambios locales
git checkout ubuntu_house
git pull origin ubuntu_house  # si existe en remoto

# 2. Hacer cambios específicos del ambiente local
# (archivos .dev.env, docker-compose.dev.yml, etc.)

# 3. Commit local
git add .
git commit -m "config: ajuste específico ubuntu-house"

# 4. NO hacer merge a develop/main si son solo configs locales
# Mantener ubuntu_house separada para configuraciones del ambiente
```

## Setup Inicial en ubuntu-house

### Opción A: Clonar y Configurar Ramas (Recomendado)

```bash
# 1. Clonar el repo
cd ~/shared/projects
rm -rf chalanpro  # si ya existe y quieres empezar limpio
git clone https://github.com/Gulivers/chalan-pro_tenant.git chalanpro
cd chalanpro/app

# 2. Crear rama develop si no existe
git checkout -b develop
git push origin develop

# 3. Crear/actualizar rama ubuntu_house
git checkout -b ubuntu_house
# ... aplicar configuraciones locales ...
git push origin ubuntu_house

# 4. Volver a develop para trabajo normal
git checkout develop
```

### Opción B: Sincronizar Estado Actual

```bash
# 1. Resolver divergencia actual en main
cd ~/shared/projects/chalanpro/app
git status  # ver estado actual

# 2. Guardar cambios locales en ubuntu_house
git stash  # si hay cambios sin commit
git checkout ubuntu_house
git stash pop  # si aplica

# 3. Crear develop desde main limpio
git checkout main
git pull origin main  # traer cambios remotos
git checkout -b develop
git push origin develop

# 4. Merge cambios de ubuntu_house a develop (solo los que sean aplicables)
git checkout develop
git merge ubuntu_house --no-ff  # revisar conflictos
```

## Reglas de Oro

### ✅ HACER
- ✅ Trabajar en `develop` o feature branches para desarrollo
- ✅ Probar cambios en ubuntu-house antes de merge a `main`
- ✅ Hacer commits descriptivos y frecuentes
- ✅ Mantener `main` siempre estable y funcional
- ✅ Sincronizar `develop` con `main` regularmente
- ✅ Usar `ubuntu_house` solo para configuraciones locales

### ❌ NO HACER
- ❌ **NUNCA** hacer push directo a `main` desde desarrollo
- ❌ **NUNCA** hacer merge a `main` sin probar primero
- ❌ **NUNCA** hacer force push a `main`
- ❌ No mezclar configuraciones locales con código de producción
- ❌ No hacer commits de archivos `.env` con secretos

## Comandos Útiles

### Ver estado de ramas
```bash
git branch -a                    # Ver todas las ramas
git log --oneline --graph --all  # Ver historial visual
git status                       # Ver estado actual
```

### Sincronizar con remoto
```bash
git fetch origin                 # Traer cambios sin merge
git pull origin <rama>          # Traer y mergear
git push origin <rama>          # Subir cambios
```

### Comparar ramas
```bash
git diff main..develop           # Ver diferencias
git log main..develop           # Ver commits únicos en develop
```

## Deployment en VPS Hostinger

### Proceso Manual (Actual)
```bash
# En el VPS (72.60.168.62)
cd /opt/chalanpro/app
git fetch origin
git checkout main
git pull origin main
docker compose restart backend frontend nginx
```

### Proceso Automatizado (Futuro - Opcional)
- Configurar webhook de GitHub para auto-deploy
- O usar GitHub Actions para CI/CD
- Verificar que solo `main` active el deploy

## Checklist Antes de Merge a Main

- [ ] Código probado en ubuntu-house (develop)
- [ ] Tests pasando (si existen)
- [ ] Migraciones probadas y funcionando
- [ ] Frontend build sin errores
- [ ] WebSockets funcionando correctamente
- [ ] No hay cambios en archivos `.env` con secretos
- [ ] Documentación actualizada si aplica
- [ ] Revisión de código (si trabajas en equipo)

## Resolución de Conflictos

Si hay conflictos al hacer merge:

```bash
# 1. Ver archivos en conflicto
git status

# 2. Abrir archivos y resolver manualmente
# (buscar marcadores <<<<<<< ======= >>>>>>>)

# 3. Marcar como resuelto
git add <archivo-resuelto>

# 4. Completar merge
git commit
```

## Estructura de Commits Recomendada

Usar prefijos descriptivos:
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Documentación
- `config:` Configuración
- `refactor:` Refactorización
- `test:` Tests
- `chore:` Tareas de mantenimiento

Ejemplo:
```bash
git commit -m "feat(schedule): agregar filtro por fecha en FullCalendar"
git commit -m "fix(websocket): corregir reconexión automática en Daphne"
git commit -m "config(nginx): ajustar proxy para desarrollo local"
```

---

## Preguntas Frecuentes

**P: ¿Qué pasa si hago un cambio urgente directamente en main?**
R: Si es absolutamente necesario, hazlo, pero inmediatamente después haz merge a `develop` para mantener sincronización.

**P: ¿Cómo sé qué cambios están en main pero no en develop?**
R: `git log develop..main` mostrará los commits únicos de main.

**P: ¿Puedo trabajar directamente en develop?**
R: Sí, pero es mejor usar feature branches para cambios grandes y mergear a develop.

**P: ¿Qué hacer con los cambios locales en ubuntu_house?**
R: Si son solo configuraciones locales (`.dev.env`, etc.), mantenerlos en `ubuntu_house`. Si son cambios de código aplicables a producción, mergear a `develop` primero.

