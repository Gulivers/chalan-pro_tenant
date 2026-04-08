# Jobrithm – Web de marketing (Landing)

**Inspiración (nicho y segmento):**

> **Construction operations platform for residential trade contractors.**

En SaaS aplica la regla: _The riches are in the niches._ Cuanto más específico sea el problema que resuelves, más fácil es vender.

**Dónde entra el sistema (nicho de negocio):**

El producto está exactamente aquí:

```
              Enterprise Construction
                    |
                    |
    Builder PM ---- | ---- Field Service
                    |
                    |
           ⭐ JOBRITHM ZONE ⭐
   Residential trade contractors operations
                    |
                    |
                Small contractors
```

Ese espacio tiene:

- millones de empresas
- baja digitalización
- mucho dolor operativo

---

Sitio estático, orientado a SEO y conversión, para **getjobrithm.com**. Presenta Jobrithm como plataforma de operaciones de construcción para contratistas residenciales, supervisores y equipos de campo.

**No es la app interna.** Es la web pública que explica el producto, capta leads (demo, contacto, precios) y soporta el crecimiento orgánico.

Arrancar servidor: npm start  
Construir cambios: npm run build

## Stack

- **HTML** estático
- **Tailwind CSS** compilado con npm (CLI)
- **JavaScript** vanilla mínimo (solo cuando haga falta)
- Sin Vue, React, Alpine ni jQuery en la landing

## Estructura de archivos

```
landing/
├── dist/                      # Build de producción (generado, no editar)
│   ├── output.css             # CSS compilado y minificado
│   ├── *.html                 # HTML con nav ya inyectado (ver sección “Navegación”)
│   ├── sitemap.xml
│   ├── robots.txt
│   └── img/                   # Imágenes copiadas desde src/img
│
├── src/                       # Fuentes (editar aquí)
│   ├── partials/              # Plantillas del menú (solo fuente; ver “Navegación”)
│   │   ├── nav-en.html
│   │   └── nav-es.html
│   ├── input.css              # Entrada Tailwind
│   ├── index.html             # Página principal (marcador de nav, no el <nav> completo)
│   ├── pricing.html           # Precios
│   ├── contact.html           # Contacto
│   ├── sitemap.xml
│   ├── robots.txt
│   └── img/                   # Imágenes (opcional)
│
├── docs/
│   └── ai-guidelines.md       # Estándares para IA y desarrolladores
│
├── build-nav.mjs              # Inyecta el nav desde partials al generar dist/
├── package.json
├── tailwind.config.js         # Config Tailwind (colores, fuentes)
├── README.md                  # Este archivo
└── AGENTS.md                  # Contexto para agentes de IA
```

## Navegación (parciales en build)

La barra de navegación **no se duplica** en cada HTML de `src/`. Se define en plantillas y se **concatena en el build**, de modo que el HTML servido en producción sigue siendo **estático y completo** (sin impacto negativo en SEO: los crawlers reciben el mismo `<nav>` que si estuviera pegado en cada página).

**Cómo funciona:**

1. **`build-nav.mjs`** (Node, sin dependencias extra) se ejecuta **al inicio** de `npm run build`.
2. Las plantillas están en **`src/partials/nav-en.html`** y **`src/partials/nav-es.html`**. Usan sustitución de tokens (`{{NAV_CTA_HREF}}`, `{{LANG_ES_HREF}}` o `{{LANG_EN_HREF}}`) según la página.
3. Las páginas que llevan menú incluyen solo el marcador **`<!-- landing:inject-nav -->`** entre `<body>` y `<main>`. El script lo reemplaza por `<!-- Nav -->` más el HTML del menú ya resuelto.
4. Los enlaces variables por página (idioma, contacto en la misma URL, etc.) están centralizados en el objeto **`NAV_BY_FILE`** dentro de `build-nav.mjs`.
5. Los HTML que **no** llevan ese marcador (p. ej. redirecciones) se copian tal cual a `dist/`.

**Importante para desarrollo local:** abrir un `*.html` directamente desde `src/` **no** muestra el menú. Para ver la landing completa hay que ejecutar **`npm run build`** y servir **`dist/`** (p. ej. `npm start`) o confiar en `npm run build:watch` para regenerar al guardar.

**Si cambias el menú:** edita los partials y/o `NAV_BY_FILE`, luego `npm run build`. Si añades una página nueva con nav, añade el marcador en el HTML y una entrada en `NAV_BY_FILE`.

## Comandos

| Comando               | Descripción                                        |
| --------------------- | -------------------------------------------------- |
| `npm install`         | Instalar dependencias (Tailwind, chokidar-cli)     |
| `npm run build`       | `build-nav.mjs` + Tailwind + assets → `dist/`      |
| `npm run dev`         | Watch Tailwind (regenera solo CSS al guardar)      |
| `npm run build:watch` | Watch `src/`: ejecuta build completo al guardar    |
| `npm start`           | Servir `dist/` en http://localhost:3000            |

## Desarrollo local

**Terminal 1** — Watch CSS:

```bash
npm run dev
```

**Terminal 2** — Servir archivos:

```bash
npm start
```

Abrir http://localhost:3000 en el navegador. Tras editar estilos o HTML, recargar la página (F5).

## Diseño y conversión

- **Diseño:** B2B SaaS moderno (referencias: Stripe, Linear, Notion; sector: Buildertrend, Procore, ServiceTitan). Limpio, profesional, con jerarquía clara y CTAs visibles.
- **Conversión:** Cada página debe incluir value proposition, indicador de confianza (o placeholder) y CTA above the fold + CTA cerca del final. Objetivos principales: reservar demo, contactar ventas, ver precios.

Detalle en **`docs/ai-guidelines.md`**.

## Deploy (getjobrithm.com)

1. **Build:** `npm run build`
2. **Nginx:** Configurado en `../nginx/default.conf` para `getjobrithm.com` y `www.getjobrithm.com`
3. **Docker:** El volumen `./landing/dist` se monta en el contenedor nginx
4. **SSL:** Obtener certificado Let's Encrypt cuando corresponda
5. **Reiniciar nginx:** `docker compose restart nginx` (en el entorno de producción)

## Documentación

- **Estándares y guías:** `docs/ai-guidelines.md`
- **Agentes IA:** `AGENTS.md`
- **Proyecto principal (app):** `../AGENTS.md` (raíz del repo)
