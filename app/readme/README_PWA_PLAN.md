# Plan de Implementación PWA - ChalanPro

Plan para habilitar Progressive Web App (PWA) en ChalanPro. Implementación en fases: primero en el servidor local **ubuntu_house**, luego en el VPS de producción en Hostinger.

> **Estado:** Fase 1 implementada (plugin PWA, vue.config.js, iconos en `public/img/icons/`). Fase 2 (VPS Hostinger) a cargo del usuario.

---

## 📋 Tabla de Contenidos

1. [Contexto y Alcance](#contexto-y-alcance)
2. [Requisitos PWA (Contexto Seguro)](#requisitos-pwa-contexto-seguro)
3. [Fase 1: Servidor Local ubuntu_house](#fase-1-servidor-local-ubuntu_house)
4. [Fase 2: VPS Hostinger (Producción)](#fase-2-vps-hostinger-producción)
5. [Configuración Técnica](#configuración-técnica)
6. [Verificación y Pruebas](#verificación-y-pruebas)

---

## Contexto y Alcance

### Entorno de Desarrollo

- **Servidor:** ubuntu_house (192.168.0.105)
- **Acceso:** Solo vía SSH al servidor
- **Pruebas:** Desde `localhost` o `127.0.0.1` en el propio servidor Ubuntu (contexto seguro para PWA)
- **Frontend:** Vue CLI 5, puerto 8080
- **Backend:** Daphne + Django, puerto 8000

### Flujo de Trabajo

1. Conectar por SSH a ubuntu-house
2. Desarrollar y probar PWA accediendo a `http://localhost:8080` o `http://127.0.0.1:8080` desde el navegador del servidor (o tunnel SSH)
3. Las PWAs requieren **contexto seguro**: HTTPS o localhost/127.0.0.1
4. Una vez validado en local, desplegar en VPS Hostinger

---

## Requisitos PWA (Contexto Seguro)

Las PWAs solo funcionan en:

- `https://` (cualquier dominio)
- `http://localhost`
- `http://127.0.0.1`

En ubuntu_house usaremos **localhost** o **127.0.0.1** para pruebas sin certificado SSL.

---

## Fase 1: Servidor Local ubuntu_house

### 1.1 Instalación del Plugin PWA

```bash
cd /home/oliver/shared/projects/chalanpro/app/vuefrontend
npm install -D @vue/cli-plugin-pwa
vue add pwa
```

O manualmente en `package.json`:

```json
"devDependencies": {
  "@vue/cli-plugin-pwa": "^5.0.0"
}
```

### 1.2 Configuración en vue.config.js

Añadir la sección `pwa` en `vue.config.js`:

```javascript
module.exports = defineConfig({
  // ... configuración existente ...
  pwa: {
    name: 'ChalanPro',
    themeColor: '#0d6efd',
    msTileColor: '#000000',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'default',
    manifestPath: 'manifest.json',
    workboxPluginMode: 'GenerateSW',
    workboxOptions: {
      skipWaiting: true,
      clientsClaim: true,
    },
    manifestOptions: {
      name: 'ChalanPro',
      short_name: 'ChalanPro',
      theme_color: '#0d6efd',
      background_color: '#ffffff',
      display: 'standalone',
      start_url: '/',
      icons: [
        {
          src: './img/icons/icon-192x192.png',
          sizes: '192x192',
          type: 'image/png',
        },
        {
          src: './img/icons/icon-512x512.png',
          sizes: '512x512',
          type: 'image/png',
        },
      ],
    },
  },
});
```

### 1.3 Iconos PWA

Crear iconos en `app/vuefrontend/public/img/icons/`:

- `icon-192x192.png`
- `icon-512x512.png`

Puedes usar [PWA Asset Generator](https://www.pwabuilder.com/imageGenerator) o generar desde un logo base.

### 1.4 Probar en ubuntu_house

**Opción A: Desarrollo (sin Service Worker real)**

```bash
cd /home/oliver/shared/projects/chalanpro/app/vuefrontend
npm run serve
```

Acceder desde el servidor: `http://localhost:8080` o `http://127.0.0.1:8080`

**Opción B: Build de producción (con Service Worker)**

```bash
npm run build
npx serve -s dist -l 8080
```

Acceder: `http://localhost:8080` — el Service Worker se registrará correctamente.

**Opción C: Tunnel SSH (desde tu PC)**

```bash
ssh -L 8080:localhost:8080 oliver@ubuntu-house
```

Luego en tu navegador local: `http://localhost:8080` (contexto seguro).

### 1.5 Verificación en ubuntu_house

1. Abrir DevTools → Application → Manifest: debe mostrar el manifest correcto
2. Application → Service Workers: debe aparecer el SW registrado (solo en build)
3. Lighthouse → Progressive Web App: revisar puntuación

---

## Fase 2: VPS Hostinger (Producción)

Una vez validado en ubuntu_house:

1. **HTTPS obligatorio** en producción (Let's Encrypt o certificado del hosting)
2. **Build del frontend:** `npm run build`
3. **Desplegar** la carpeta `dist` en el servidor (Nginx/Apache)
4. **Headers de seguridad** para Service Worker y manifest
5. **Actualizar** `start_url` y rutas en el manifest si el dominio cambia

### Headers Nginx recomendados (producción)

```nginx
# Service Worker y manifest deben servirse con headers correctos
location ~* (service-worker\.js|manifest\.json)$ {
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

---

## Configuración Técnica

### Estructura de Archivos Esperada

```
app/vuefrontend/
├── public/
│   ├── img/
│   │   └── icons/
│   │       ├── icon-192x192.png
│   │       └── icon-512x512.png
│   └── index.html
├── vue.config.js      # + sección pwa
├── package.json       # + @vue/cli-plugin-pwa
└── src/
    └── registerServiceWorker.js  # (opcional, generado por el plugin)
```

### Variables de Entorno

Para producción en VPS, asegurar:

- `VUE_APP_BASE_URL` o similar si el frontend se sirve en un subpath
- `start_url` en manifest coherente con la URL pública

---

## Verificación y Pruebas

### Checklist ubuntu_house

- [ ] Plugin PWA instalado
- [ ] vue.config.js con sección pwa
- [ ] Iconos 192x192 y 512x512 en public/img/icons/
- [ ] `npm run build` genera `dist/` con `manifest.json` y `service-worker.js`
- [ ] Acceso por `http://localhost:8080` o `http://127.0.0.1:8080`
- [ ] Manifest visible en DevTools → Application
- [ ] Service Worker registrado (en build)
- [ ] Instalable como PWA (Add to Home Screen / Install app)

### Checklist VPS Hostinger

- [ ] HTTPS activo
- [ ] Build desplegado
- [ ] Manifest y SW accesibles
- [ ] PWA instalable desde el dominio de producción

---

## Troubleshooting

**Error `EACCES: permission denied` en `dist/`:** Si `dist` fue creado por root (ej. Docker), corregir permisos:
```bash
sudo chown -R $USER:$USER app/vuefrontend/dist
```

---

## Notas

- El Service Worker solo se genera en **build** (`npm run build`), no en `npm run serve`
- Para probar el SW en desarrollo, usar `npm run build` + servidor estático local
- En ubuntu_house, **solo** programar desde la conexión SSH; las pruebas se hacen en localhost/127.0.0.1 del servidor
- La imagen de referencia (constructor con casco y brackets de código) representa el proceso de construcción del PWA
