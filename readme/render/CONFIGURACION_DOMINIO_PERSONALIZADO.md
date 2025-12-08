# 🌐 Configuración de Dominio Personalizado en Hostinger

## 📋 Problema Actual

El dominio `www.chalanpro.net` está apuntando al **backend** de Render en lugar del **frontend (static site)**. Esto causa:
- ❌ El frontend no se muestra (404 en `/onboarding`)
- ✅ El backend funciona correctamente (`/api/` funciona)

## ✅ Solución: Configurar DNS en Hostinger

### Paso 1: Obtener la URL del Static Site de Render

1. Ve a tu dashboard de Render: https://dashboard.render.com
2. Busca el servicio **Static Site** llamado `chalan-frontend`
3. Copia la URL del servicio (ejemplo: `https://chalan-frontend.onrender.com`)

### Paso 2: Configurar DNS en Hostinger

1. **Inicia sesión en Hostinger**: https://www.hostinger.com
2. Ve a **Dominios** → Selecciona `chalanpro.net`
3. Ve a **DNS / Nameservers**
4. Configura los siguientes registros DNS:

#### Opción A: Usar CNAME (Recomendado)

```
Tipo: CNAME
Nombre: www
Valor: chalan-frontend.onrender.com
TTL: 3600 (o el valor por defecto)
```

#### Opción B: Usar A Record (Si CNAME no funciona)

Necesitas obtener la IP del static site de Render. Puedes hacerlo con:

```bash
nslookup chalan-frontend.onrender.com
```

Luego configura:

```
Tipo: A
Nombre: www
Valor: [IP obtenida del nslookup]
TTL: 3600
```

**Nota**: Si usas A Record, la IP puede cambiar cuando Render reinicie el servicio. CNAME es más estable.

### Paso 3: Configurar Dominio Raíz (chalanpro.net sin www)

Para que `chalanpro.net` (sin www) también funcione:

#### Opción A: Redirección en Hostinger

1. En Hostinger, busca la opción de **Redirecciones**
2. Crea una redirección:
   - **Desde**: `chalanpro.net`
   - **Hacia**: `www.chalanpro.net`
   - **Tipo**: 301 (Permanente)

#### Opción B: Configurar DNS para dominio raíz

Render no soporta CNAME en el dominio raíz directamente. Necesitas:

1. En Render, ve a tu Static Site `chalan-frontend`
2. Ve a **Settings** → **Custom Domains**
3. Agrega `chalanpro.net` (sin www)
4. Render te dará instrucciones específicas para configurar el DNS

### Paso 4: Configurar Dominio en Render

1. Ve a tu Static Site `chalan-frontend` en Render
2. Ve a **Settings** → **Custom Domains**
3. Haz clic en **Add Custom Domain**
4. Agrega:
   - `www.chalanpro.net`
   - `chalanpro.net` (opcional, si quieres soportar ambos)

5. Render te mostrará instrucciones específicas de DNS si es necesario

### Paso 5: Verificar la Configuración

Después de configurar DNS, espera 5-30 minutos para que los cambios se propaguen. Luego verifica:

```bash
# Verificar que www.chalanpro.net apunta al static site
nslookup www.chalanpro.net

# Verificar que el dominio responde
curl -I https://www.chalanpro.net
```

## 🔧 Configuración Actual del Backend

El backend debe seguir apuntando a su propia URL de Render:
- **Backend URL**: `https://chalan-backend.onrender.com` o `https://www.chalanpro.net/api/`
- **Frontend URL**: `https://www.chalanpro.net` (después de configurar DNS)

## 📝 Notas Importantes

1. **Propagación DNS**: Los cambios DNS pueden tardar hasta 48 horas, pero generalmente funcionan en 5-30 minutos.

2. **SSL/HTTPS**: Render proporciona SSL automáticamente para dominios personalizados. No necesitas configurar certificados manualmente.

3. **Backend vs Frontend**:
   - **Backend**: `chalan-backend.onrender.com` → API de Django
   - **Frontend**: `chalan-frontend.onrender.com` → Static Site de Vue.js
   - **Dominio personalizado**: `www.chalanpro.net` → Debe apuntar al **Frontend**

4. **Rutas del Frontend**: El frontend está configurado con `history mode` de Vue Router, por lo que todas las rutas (como `/onboarding`) deben ser manejadas por el frontend. Render ya tiene configurado un rewrite rule en `render.yaml` para esto.

## ✅ Verificación Final

Después de configurar todo, verifica:

1. ✅ `https://www.chalanpro.net` → Muestra el frontend de Vue
2. ✅ `https://www.chalanpro.net/onboarding` → Muestra la página de onboarding
3. ✅ `https://www.chalanpro.net/api/` → Muestra la API (esto debe seguir funcionando)
4. ✅ `https://www.chalanpro.net/admin/` → Muestra el admin de Django (sin error CSRF)

## 🐛 Troubleshooting

### El dominio sigue mostrando 404

- Verifica que el DNS esté configurado correctamente
- Espera más tiempo para la propagación DNS
- Verifica en Render que el dominio personalizado esté agregado y verificado

### Error CSRF en el admin

- Ya está corregido en `settings.py` agregando `https://www.chalanpro.net` a `CSRF_TRUSTED_ORIGINS`
- Asegúrate de hacer deploy del backend con los cambios

### El frontend no carga recursos estáticos

- Verifica que el build del frontend se haya completado correctamente
- Revisa los logs del static site en Render

