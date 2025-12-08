# 🌐 Configuración DNS en Hostinger - Configuración Final

## ✅ Configuración Recomendada para tus URLs Objetivo

### URLs Objetivo:
- **Frontend**: `https://www.chalanpro.net` → Frontend Vue.js
- **Backend**: `https://api.chalanpro.net` → Backend Django

## 📊 Tabla de Configuración DNS Recomendada

| Tipo | Name | Priority | Content | TTL | Estado | Notas |
|------|------|----------|---------|-----|--------|-------|
| **CNAME** | `www` | 0 | `chalan-frontend.onrender.com` | 3600 | ✅ **MANTENER** | Frontend principal |
| **CNAME** | `api` | 0 | `chalan-backend.onrender.com` | 3600 | ✅ **MANTENER** | Backend API y Admin |
| **ALIAS** | `@` | 0 | `chalan-frontend.onrender.com` | 3600 | ✅ **MANTENER** | Dominio raíz → Frontend |
| **CAA** | `@` | 0 | `0 issue "letsencrypt.org"` | 14400 | ✅ **MANTENER** | SSL (puedes mantener todos) |
| **CAA** | `@` | 0 | `0 issue "comodoca.com"` | 14400 | ✅ **MANTENER** | SSL |
| **CAA** | `@` | 0 | `0 issue "globalsign.com"` | 14400 | ✅ **MANTENER** | SSL |
| **CNAME** | `*` | 0 | `chalan-frontend.onrender.com` | 3600 | ⚠️ **REVISAR** | Wildcard - ver notas abajo |
| **A** | `@` | 0 | `216.24.57.1` | 3600 | ❌ **ELIMINAR** | Conflicto con ALIAS |

## ⚠️ Problemas Identificados

### 1. Conflicto entre ALIAS y A Record para dominio raíz

**Problema**: Tienes tanto `ALIAS @` como `A @` configurados para el dominio raíz. Esto puede causar conflictos.

**Solución**: 
- ✅ **MANTENER**: `ALIAS @ → chalan-frontend.onrender.com`
- ❌ **ELIMINAR**: `A @ → 216.24.57.1`

**Razón**: El ALIAS es más flexible y permite que Render maneje el SSL automáticamente. El A Record con IP fija puede causar problemas si Render cambia sus IPs.

### 2. Wildcard CNAME `*`

**Problema**: El wildcard `CNAME *` captura todos los subdominios no especificados.

**Análisis**:
- ✅ **Funciona bien** si quieres que todos los subdominios (excepto `www` y `api`) vayan al frontend
- ⚠️ **Puede causar problemas** si en el futuro necesitas otros subdominios específicos para el backend

**Recomendación**:
- **Opción A**: **MANTENER** el wildcard si quieres que todos los subdominios vayan al frontend por defecto
- **Opción B**: **ELIMINAR** el wildcard si prefieres control explícito sobre cada subdominio

**Nota**: El orden de las reglas DNS importa. Como `api` está configurado específicamente, debería tener prioridad sobre el wildcard `*`.

## ✅ Configuración Final Recomendada

### Configuración Mínima Necesaria:

| Tipo | Name | Priority | Content | TTL | Acción |
|------|------|----------|---------|-----|--------|
| CNAME | `www` | 0 | `chalan-frontend.onrender.com` | 3600 | ✅ MANTENER |
| CNAME | `api` | 0 | `chalan-backend.onrender.com` | 3600 | ✅ MANTENER |
| ALIAS | `@` | 0 | `chalan-frontend.onrender.com` | 3600 | ✅ MANTENER |
| CAA | `@` | 0 | `0 issue "letsencrypt.org"` | 14400 | ✅ MANTENER (al menos uno) |
| A | `@` | 0 | `216.24.57.1` | 3600 | ❌ **ELIMINAR** |

### Configuración Opcional:

| Tipo | Name | Priority | Content | TTL | Acción |
|------|------|----------|---------|-----|--------|
| CNAME | `*` | 0 | `chalan-frontend.onrender.com` | 3600 | ⚠️ OPCIONAL (ver notas) |

## 🔧 Pasos para Corregir en Hostinger

### Paso 1: Eliminar el A Record del dominio raíz

1. Ve a Hostinger → Dominios → `chalanpro.net` → DNS
2. Busca el registro:
   ```
   A  @  216.24.57.1
   ```
3. Elimínalo (conflicta con el ALIAS)

### Paso 2: Verificar el orden de las reglas

Asegúrate de que las reglas específicas (`www`, `api`) estén **antes** del wildcard `*` en la lista. El orden puede importar en algunos sistemas DNS.

### Paso 3: Verificar en Render

1. **Backend**: Verifica que `api.chalanpro.net` esté agregado como dominio personalizado
   - Dashboard: https://dashboard.render.com/web/srv-d44nroripnbc73angjdg
   - Settings → Custom Domains

2. **Frontend**: Verifica que `www.chalanpro.net` esté agregado
   - Dashboard del static site `chalan-frontend`
   - Settings → Custom Domains

## ✅ Verificación de la Configuración

Después de hacer los cambios, espera 5-30 minutos y verifica:

```bash
# Verificar que www apunta al frontend
nslookup www.chalanpro.net
# Debe mostrar: chalan-frontend.onrender.com

# Verificar que api apunta al backend
nslookup api.chalanpro.net
# Debe mostrar: chalan-backend.onrender.com

# Verificar dominio raíz
nslookup chalanpro.net
# Debe mostrar: chalan-frontend.onrender.com (o la IP de Render)
```

## 📝 Resumen de Cambios Necesarios

### ✅ Lo que está BIEN:
- ✅ `CNAME www` → Frontend
- ✅ `CNAME api` → Backend
- ✅ `ALIAS @` → Frontend
- ✅ `CAA` records para SSL

### ❌ Lo que DEBES CAMBIAR:
- ❌ **ELIMINAR**: `A @ → 216.24.57.1` (conflicto con ALIAS)

### ⚠️ Lo que es OPCIONAL:
- ⚠️ `CNAME *` → Puedes mantenerlo si quieres que todos los subdominios vayan al frontend por defecto

## 🎯 Resultado Final Esperado

Después de los cambios:

| URL | Destino | Estado |
|-----|---------|--------|
| `https://www.chalanpro.net` | Frontend Vue.js | ✅ |
| `https://www.chalanpro.net/login` | Frontend Login | ✅ |
| `https://www.chalanpro.net/onboarding` | Frontend Onboarding | ✅ |
| `https://api.chalanpro.net` | Backend Django | ✅ |
| `https://api.chalanpro.net/admin/` | Admin Django | ✅ |
| `https://api.chalanpro.net/api/` | API Root | ✅ |
| `https://chalanpro.net` | Frontend (redirige a www) | ✅ |

