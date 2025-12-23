# 🚀 Tarea: Mover Repositorio Git a Nivel Superior (VPS Hostinger)

## 📋 Contexto

El repositorio Git actualmente está en `chalanpro/app/`, pero necesitamos moverlo a `chalanpro/` para incluir toda la configuración de infraestructura (Docker, Nginx, scripts) en el repositorio. Esto permitirá que cualquier desarrollador que clone el repo tenga todo lo necesario para levantar el stack completo.

## 🎯 Objetivo

Mover el directorio `.git` de `chalanpro/app/` a `chalanpro/` y actualizar el repositorio para incluir:
- `docker-compose.yml` (producción)
- `docker-compose.dev.yml` (desarrollo)
- `nginx/` (configuración de Nginx)
- `scripts/` (scripts de utilidad)
- `envs/*.example.env` (templates de variables de entorno, NO los .env con secretos)

## ⚠️ IMPORTANTE - Reglas Estrictas

1. **NUNCA** agregar archivos `.env` con secretos al repositorio
2. **NUNCA** agregar `postgres_data/` o cualquier directorio de datos de base de datos
3. **NUNCA** agregar certificados SSL (`/etc/letsencrypt/`)
4. **Siempre** verificar que los archivos sensibles estén en `.gitignore`
5. **NO** modificar archivos de configuración existentes, solo mover y agregar al repo
6. **NO** detener servicios Docker durante el proceso (si es posible)

## 📍 Ubicación Actual del Proyecto en VPS

```
/opt/chalanpro/
├── app/                    ← Repositorio Git actual (.git está aquí)
│   ├── .git/
│   ├── project/
│   ├── vuefrontend/
│   └── ...
├── docker-compose.yml      ← Fuera del repo actualmente
├── docker-compose.dev.yml  ← Fuera del repo actualmente
├── nginx/                  ← Fuera del repo actualmente
├── envs/                   ← Fuera del repo actualmente
│   ├── backend.env         ← NO agregar (tiene secretos)
│   ├── backend.example.env ← SÍ agregar (template)
│   └── ...
└── scripts/                ← Fuera del repo actualmente
```

## 🔧 Pasos a Ejecutar

### Paso 1: Verificar Estado Actual

```bash
cd /opt/chalanpro/app
git status
git branch
git log --oneline -5
```

### Paso 2: Asegurar que Estás en la Rama Correcta

```bash
cd /opt/chalanpro/app
git checkout main
git pull origin main  # Sincronizar con remoto
```

### Paso 3: Guardar Cualquier Cambio Pendiente

```bash
cd /opt/chalanpro/app
# Si hay cambios sin commitear, guardarlos
git stash push -m "Cambios locales antes de mover repo"
```

### Paso 4: Mover .git al Nivel Superior

```bash
cd /opt/chalanpro
mv app/.git .
```

### Paso 5: Crear/Actualizar .gitignore en la Raíz

Crear `.gitignore` en `/opt/chalanpro/` con el siguiente contenido:

```gitignore
# Ignore virtual environment
venv/

# Ignore node_modules
app/vuefrontend/node_modules/
app/vuefrontend/dist/
node_modules/

# Ignore build artifacts and logs
*.log
*.log.*

# Ignore Python cache files
__pycache__/
.DS_Store
*.pyc
*.pyo

# Ignore system files
.DS_Store

# Ignore .env files (con secretos) - CRÍTICO
.env
.env_mysql
envs/*.env
!envs/*.example.env
!envs/*.dev.example.env

# Ignore IDE
.idea/
*.swp

# Ignore VisualStudioCode (excepto configuraciones útiles)
.vscode/
!.vscode/settings.json
!.vscode/launch.json
!.vscode/extensions.json

# Ignore database data - CRÍTICO
postgres_data/
pgadmin_data/

# Ignore SSL certificates (solo en producción)
# /etc/letsencrypt/ (comentado, no está en el repo)

# Ignore migrations (si no quieres commitearlas)
# app/ctrctsapp/migrations/*
# !app/ctrctsapp/migrations/__init__.py
# (repetir para cada app según necesidad)

# Ignore Vue env files
app/vuefrontend/.env.local
app/vuefrontend/.env

# Ignore workspace files
*.code-workspace
!root.code-workspace

# Ignore readme directory except specific files
readme/*
!readme/README_RESUMEN_GENERAL.md
```

### Paso 6: Verificar y Agregar Archivos de Infraestructura

```bash
cd /opt/chalanpro

# Verificar qué archivos Git ve ahora
git status

# Agregar archivos de infraestructura necesarios
git add docker-compose.yml
git add docker-compose.dev.yml
git add nginx/
git add scripts/

# Agregar solo archivos .example de envs (NO los .env con secretos)
git add envs/*.example.env envs/*.dev.example.env 2>/dev/null || true

# Verificar que NO se agreguen archivos sensibles
git status | grep -E "\.env$|postgres_data" && echo "⚠️ ERROR: Archivos sensibles detectados!" || echo "✓ No hay archivos sensibles"
```

### Paso 7: Verificar que NO se Agreguen Archivos Sensibles

**CRÍTICO**: Antes de hacer commit, verificar:

```bash
cd /opt/chalanpro

# Listar archivos en staging
git diff --cached --name-only

# Verificar que NO hay .env con secretos
git diff --cached --name-only | grep -E "envs/.*\.env$" | grep -v example && echo "⚠️ ERROR: Archivos .env con secretos detectados!" || echo "✓ No hay .env con secretos"

# Verificar que NO hay postgres_data
git diff --cached --name-only | grep postgres_data && echo "⚠️ ERROR: postgres_data detectado!" || echo "✓ No hay postgres_data"
```

### Paso 8: Commit de los Cambios

```bash
cd /opt/chalanpro

git commit -m "chore: mover repositorio a nivel superior e incluir configuración Docker

- Mover .git de app/ a raíz del proyecto
- Incluir docker-compose.yml y docker-compose.dev.yml
- Incluir configuración nginx/
- Incluir scripts de utilidad
- Actualizar .gitignore para nivel superior
- Mantener estructura app/ para código de aplicación
- Excluir archivos sensibles (.env, postgres_data)"
```

### Paso 9: Verificar Estructura Final

```bash
cd /opt/chalanpro

# Verificar estructura
git log --oneline -5
git status

# Verificar que .gitignore funciona
git check-ignore envs/backend.env && echo "✓ .env ignorado correctamente" || echo "⚠️ .env NO está siendo ignorado"
git check-ignore postgres_data/ && echo "✓ postgres_data ignorado correctamente" || echo "⚠️ postgres_data NO está siendo ignorado"
```

### Paso 10: Push al Remoto

```bash
cd /opt/chalanpro

# Verificar rama actual
git branch

# Push a origin/main
git push origin main

# Si hay rama develop, también hacer push
git checkout develop 2>/dev/null && git push origin develop || echo "No hay rama develop"
```

### Paso 11: Verificar que los Servicios Siguen Funcionando

```bash
# Verificar que Docker sigue funcionando
cd /opt/chalanpro
docker compose ps

# Si algo falla, los servicios deberían seguir corriendo
# El cambio de ubicación de .git no afecta los contenedores
```

## ✅ Checklist de Verificación

Antes de considerar la tarea completada, verificar:

- [ ] `.git` movido de `app/` a raíz (`/opt/chalanpro/`)
- [ ] `.gitignore` creado/actualizado en la raíz
- [ ] `docker-compose.yml` agregado al repo
- [ ] `docker-compose.dev.yml` agregado al repo
- [ ] `nginx/` agregado al repo
- [ ] `scripts/` agregado al repo
- [ ] Solo archivos `.example.env` agregados (NO los `.env` con secretos)
- [ ] `postgres_data/` en `.gitignore` y NO agregado
- [ ] Commit realizado con mensaje descriptivo
- [ ] Push a `origin/main` exitoso
- [ ] Servicios Docker siguen funcionando
- [ ] Estructura verificada: `git status` muestra solo cambios esperados

## 🚨 Si Algo Sale Mal

### Rollback del Movimiento de .git

```bash
cd /opt/chalanpro
mv .git app/
git status  # Verificar que todo vuelve a la normalidad
```

### Si se Agregaron Archivos Sensibles por Error

```bash
cd /opt/chalanpro
# Remover del staging
git reset HEAD envs/backend.env  # ejemplo
# Asegurarse de que estén en .gitignore
echo "envs/*.env" >> .gitignore
git add .gitignore
git commit -m "fix: asegurar que .env estén en .gitignore"
```

## 📝 Notas Adicionales

1. **No es necesario reiniciar servicios**: El movimiento de `.git` no afecta los contenedores Docker que ya están corriendo.

2. **Estructura final esperada**:
   ```
   /opt/chalanpro/
   ├── .git/              ← Aquí ahora
   ├── .gitignore         ← Actualizado
   ├── docker-compose.yml
   ├── docker-compose.dev.yml
   ├── nginx/
   ├── envs/
   │   ├── *.env          ← NO en repo (secretos)
   │   └── *.example.env   ← SÍ en repo (templates)
   ├── scripts/
   └── app/               ← Código de la aplicación
   ```

3. **Después del cambio**: Cualquier desarrollador que clone el repo tendrá toda la infraestructura necesaria para levantar el stack completo.

4. **En el VPS**: Los archivos `.env` con secretos seguirán existiendo localmente, pero NO estarán en el repositorio Git.

---

## 🎯 Resumen para el Agente

**Tarea principal**: Mover `.git` de `chalanpro/app/` a `chalanpro/` y agregar archivos de infraestructura al repositorio, asegurándote de NO agregar archivos sensibles (`.env` con secretos, `postgres_data/`).

**Prioridad**: Alta - Esto permitirá que los desarrolladores tengan todo lo necesario al clonar el repo.

**Riesgo**: Bajo - El movimiento de `.git` no afecta los servicios Docker en ejecución.

