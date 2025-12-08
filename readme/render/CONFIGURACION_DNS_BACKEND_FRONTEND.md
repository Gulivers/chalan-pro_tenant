# 🌐 Configuración DNS para Backend y Frontend

## 📋 Situación Actual

Según el log de Render, el backend está disponible en:
- `https://chalan-backend.onrender.com` ✅
- `https://www.api.chalanpro.net` ✅ (según el log: "Available at your primary URL https://www.api.chalanpro.net")

## ⚠️ Problema con la Configuración DNS Actual

Tu configuración actual en Hostinger:
```
CNAME  www     → chalan-frontend.onrender.com  ✅ (Correcto)
CNAME  *       → chalan-frontend.onrender.com  ⚠️ (Problema: captura todo)
ALIAS  @       → chalan-backend.onrender.com   ✅ (Correcto para dominio raíz)
```

**El problema**: El wildcard `CNAME *` captura **todos** los subdominios (incluyendo `api.chalanpro.net`) y los envía al frontend, antes de que se pueda procesar cualquier otra regla.

## ✅ Solución: Configuración DNS Correcta

### Opción 1: Usar `api.chalanpro.net` para el Backend (Recomendado)

#### En Hostinger - Configuración DNS:

1. **Mantener el frontend**:
   ```
   CNAME  www     → chalan-frontend.onrender.com
   ```

2. **Configurar backend con subdominio específico**:
   ```
   CNAME  api     → chalan-backend.onrender.com
   ```

3. **Remover o ajustar el wildcard**:
   - **Opción A**: Remover el `CNAME *` completamente
   - **Opción B**: Si necesitas el wildcard para otros subdominios, configurar `api` **ANTES** del wildcard (el orden importa en algunos sistemas DNS)

4. **Dominio raíz** (opcional):
   ```
   ALIAS  @       → chalan-frontend.onrender.com  (o redirección 301 a www)
   ```

#### En Render - Configurar Dominio Personalizado:

1. **Backend (`chalan-backend`)**:
   - Ve a: https://dashboard.render.com/web/srv-d44nroripnbc73angjdg
   - Settings → Custom Domains
   - Agrega: `api.chalanpro.net`
   - Render te dará instrucciones de verificación si es necesario

2. **Frontend (`chalan-frontend`)**:
   - Ya debe tener: `www.chalanpro.net`
   - Verifica que esté configurado correctamente

### Opción 2: Usar `www.api.chalanpro.net` (Ya configurado en Render)

Si Render ya tiene `www.api.chalanpro.net` configurado, entonces:

#### En Hostinger - Configuración DNS:

1. **Frontend**:
   ```
   CNAME  www     → chalan-frontend.onrender.com
   ```

2. **Backend**:
   ```
   CNAME  www.api → chalan-backend.onrender.com
   ```
   O mejor aún:
   ```
   CNAME  api     → chalan-backend.onrender.com
   ```

3. **Remover el wildcard `*`** o configurarlo después de las reglas específicas

## 📝 Configuración Final Recomendada en Hostinger

```
Tipo    Nombre      Valor
─────────────────────────────────────────────────
CNAME   www         chalan-frontend.onrender.com
CNAME   api         chalan-backend.onrender.com
ALIAS   @           chalan-frontend.onrender.com  (o redirección)
CAA     @           0 issuewild "comodoca.com"
```

**Nota**: El orden puede importar. Configura primero los subdominios específicos (`www`, `api`) y luego el wildcard si lo necesitas.

## 🔧 Actualizar Configuración en Django

Después de configurar DNS, necesitarás actualizar `settings.py` para incluir el nuevo dominio del backend:

### Agregar a ALLOWED_HOSTS:
```python
'api.chalanpro.net',  # o 'www.api.chalanpro.net' según lo que uses
```

### Agregar a CSRF_TRUSTED_ORIGINS:
```python
'https://api.chalanpro.net',  # o 'https://www.api.chalanpro.net'
```

## ✅ URLs Finales Esperadas

Después de configurar todo correctamente:

### Frontend (Vue.js):
- ✅ `https://www.chalanpro.net` → Frontend
- ✅ `https://www.chalanpro.net/login` → Login del frontend
- ✅ `https://www.chalanpro.net/onboarding` → Onboarding

### Backend (Django):
- ✅ `https://api.chalanpro.net` → Backend (o `https://www.api.chalanpro.net`)
- ✅ `https://api.chalanpro.net/admin/` → Admin de Django
- ✅ `https://api.chalanpro.net/api/` → API Root
- ✅ `https://chalan-backend.onrender.com` → Backend (URL original de Render)

## 🐛 Troubleshooting

### El wildcard `*` está capturando todo

**Problema**: El `CNAME *` tiene prioridad y captura todos los subdominios.

**Solución**: 
1. Remover el `CNAME *` temporalmente
2. Configurar primero los subdominios específicos (`www`, `api`)
3. Si necesitas el wildcard, configúralo al final (aunque esto puede no funcionar en todos los sistemas DNS)

### El orden de las reglas DNS importa

En algunos sistemas DNS, el orden de las reglas importa. Configura primero las reglas más específicas:
1. `www` → frontend
2. `api` → backend
3. `*` → frontend (si es necesario)

### Verificar la configuración DNS

```bash
# Verificar que www apunta al frontend
nslookup www.chalanpro.net

# Verificar que api apunta al backend
nslookup api.chalanpro.net

# Verificar que el dominio raíz funciona
nslookup chalanpro.net
```

## 📌 Notas Importantes

1. **Propagación DNS**: Después de cambiar DNS, espera 5-30 minutos para que se propaguen los cambios.

2. **SSL/HTTPS**: Render proporciona SSL automáticamente para dominios personalizados. No necesitas configurar certificados manualmente.

3. **Prioridad de Reglas DNS**: En Hostinger, las reglas más específicas deben configurarse antes que los wildcards.

4. **Verificación en Render**: Asegúrate de que los dominios personalizados estén agregados y verificados en Render Dashboard.

