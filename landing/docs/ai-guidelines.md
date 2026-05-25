# AI Guidelines – Landing JobRhythm (marketing SaaS)

Estándares para mantener consistencia, conversión y calidad en la web de marketing de **JobRhythm** (getjobrithm.com). En copy, meta, navegación y pies de página usar siempre **JobRhythm**; *Chalan-Pro* queda para contexto técnico del repositorio o rutas internas, no como nombre comercial en la landing.

## Índice

- [Posicionamiento del producto](#posicionamiento-del-producto) (ventaja competitiva, pitch 30 s)
- [Stack y tecnologías](#stack-y-tecnologías)
- [Estructura de archivos](#estructura-de-archivos)
- [Navegación global (build con parciales)](#navegación-global-build-con-parciales)
- [Dirección de diseño](#dirección-de-diseño)
- [Estrategia de conversión](#estrategia-de-conversión)
- [HTML y semántica](#html-y-semántica)
- [Tailwind CSS](#tailwind-css)
- [Rendimiento](#rendimiento)
- [SEO](#seo) (keywords por nicho)
- [Accesibilidad](#accesibilidad)
- [Enlaces y navegación](#enlaces-y-navegación)
- [Imágenes](#imágenes)
- [Formularios](#formularios)
- [Build y deploy](#build-y-deploy)

---

## Posicionamiento del producto

JobRhythm es una **plataforma de operaciones de construcción** para:

- **Contratistas** y empresas de obra
- **Supervisores** y jefes de obra
- **Equipos de campo** en crecimiento

La web de marketing debe comunicar: producto moderno, profesional, fiable; inventario, contratos, cronogramas de equipos y facturación en un solo lugar. **No es la app interna**: es el sitio público que explica el producto, capta leads y soporta SEO.

Referencias de espíritu (no copiar): Stripe, Linear, Notion (páginas de marketing), Buildertrend, Procore, ServiceTitan (sector construcción).

### Ventaja competitiva

La ventaja no es competir contra gigantes. La ventaja es **dominar el espacio entre field service y construction management** (residential trade contractors). El copy y la propuesta de valor deben reflejar este posicionamiento de nicho.

### Pitch de 30 segundos (referencia de copy)

Usar como referencia de tono y estructura: directo, pregunta que engancha, problema (caos), solución (una plataforma), cierre (visibilidad en tiempo real). Versión “Jordan Belfort style”:

- **Pregunta:** ¿Cómo llevas hoy el seguimiento de cada cuadrilla, los materiales que necesitan y lo que te cuesta cada obra?
- **Problema:** Llamadas, mensajes y papeles generan caos.
- **Solución:** Una sola plataforma para programación, contratos, materiales y comunicación de obra.
- **Cierre:** En vez de adivinar qué pasa en campo, lo ves en tiempo real.

El copy de hero, CTAs y secciones de problema/solución puede inspirarse en esta estructura.

---

## Stack y tecnologías

- **HTML5 estático** — Sin frameworks JS en la landing.
- **Tailwind CSS** v3.x (CLI, no PostCSS).
- **JavaScript** — Solo vanilla y mínimo; úsalo solo cuando sea necesario (ej. menú móvil, validación ligera).
- **Fuente:** Inter (Google Fonts) — o la definida en `tailwind.config.js`.
- **Dominio marketing:** getjobrithm.com, www.getjobrithm.com.
- **App principal:** jobrithm.net (Vue.js SPA) — la landing enlaza a login y onboarding.

### No usar en la landing

- Vue, React, Alpine (salvo petición explícita)
- jQuery
- Librerías de animación pesadas
- Component libraries (UI kits) salvo petición explícita

---

## Estructura de archivos

- **Fuente:** `src/` — archivos editables (HTML, CSS, img).
- **Menú global:** `src/partials/nav-en.html` y `src/partials/nav-es.html` — plantillas del `<nav>` (no se copian tal cual a `dist/`; ver [Navegación global](#navegación-global-build-con-parciales)).
- **Script de build del nav:** `build-nav.mjs` (raíz de `landing/`) — inyecta el menú en las páginas que llevan el marcador.
- **Build:** `dist/` — salida de `npm run build`; no editar manualmente.
- **CSS:** `src/input.css` — directivas Tailwind; clases en los HTML.
- **Imágenes:** `src/img/` — se copian a `dist/img/` en el build.
- **Docs:** `docs/` — este archivo y documentación asociada.
- **Documentación de proyecto:** `../README.md` y `../AGENTS.md` en la carpeta `landing/` — comandos, deploy y reglas para agentes (incluyen el flujo del nav).

---

## Navegación global (build con parciales)

La barra superior **no se mantiene copiada** en cada HTML de `src/`. Una sola fuente de verdad evita desalineaciones entre páginas EN/ES.

**Flujo:**

1. **`build-nav.mjs`** se ejecuta **al inicio** de `npm run build` (antes de Tailwind y assets).
2. Las plantillas **`src/partials/nav-en.html`** (inglés) y **`src/partials/nav-es.html`** (español) contienen el markup del `<nav>`. Sustituyen tokens del tipo `{{NAV_CTA_HREF}}`, `{{LANG_ES_HREF}}` o `{{LANG_EN_HREF}}` según la página, según el mapa **`NAV_BY_FILE`** dentro de `build-nav.mjs`.
3. En cada página que debe mostrar menú, el HTML de `src/` incluye **solo** la línea de marcador **`<!-- landing:inject-nav -->`** (entre `<body>` y `<main>`), con la indentación acorde al archivo.
4. El script **reemplaza** ese marcador por `<!-- Nav -->` más el HTML del menú ya resuelto. El resultado escrito en **`dist/`** es HTML **estático y completo**: los buscadores y la accesibilidad ven el mismo `<nav>` que si estuviera embebido a mano (no hay menú montado solo con JavaScript en cliente).
5. Páginas **sin** marcador (p. ej. redirecciones) se copian a `dist/` sin cambios.

**Qué editar al cambiar el menú:**

- Estructura, clases, textos EN/ES del nav: **partials** correspondientes.
- Enlaces que dependen de la página actual (selector de idioma, ancla al formulario de contacto, etc.): **`NAV_BY_FILE`** en `build-nav.mjs`.
- Añadir una página nueva con menú: marcador en el HTML + entrada en **`NAV_BY_FILE`**.

**Desarrollo local:** abrir un `*.html` desde `src/` en el navegador **no** muestra el menú. Previsualizar con **`npm run build`** (o `npm run build:watch`) y **`npm start`**, sirviendo **`dist/`**. Más detalle en **`landing/README.md`** (sección “Navegación”).

---

## Dirección de diseño

El diseño debe sentirse como un **B2B SaaS moderno**:

- **Limpio, moderno, profesional, confiable**
- **Espaciado generoso**, sin ruido visual
- **Jerarquía tipográfica clara**
- **CTAs evidentes**
- **Layouts basados en tarjetas** cuando tenga sentido
- **Uso elegante del espacio en blanco**
- Sin clutter; no es una web de agencia llamativa, es un producto de software serio

Visual: líneas claras, contenedores acotados (`max-w-screen-2xl`), secciones bien separadas, botones primarios/secundarios diferenciados.

### Hero principal (estilo dark)

- Hero **dark** con fondo `bg-slate-950` y **gradientes suaves** (radiales / lineales) en tonos indigo/cyan.
- **Texto claro y legible**: títulos en `text-slate-50`, cuerpo en `text-slate-300/400`.
- Uso de **glassmorphism** para tarjetas y frame de producto: fondos `bg-white/5`, bordes `border-white/10–15`, `backdrop-blur`.
- **Acentos**: indigo + cyan, con glows suaves (`shadow-cyan-500/40`, gradientes `from-indigo-500 to-cyan-400`).
- Screenshot real enmarcado en un contenedor glass premium, sin mockups inventados.
- Tarjetas flotantes con datos (ej. crews, work orders) también en estilo glass, con acentos cyan/indigo.

---

## Estrategia de conversión

Cada página debe apoyar la conversión.

### Objetivos principales

1. **Reservar una demo**
2. **Contactar ventas**
3. **Ver precios**

### Objetivos secundarios

- Leer funciones / soluciones
- Explorar blog o recursos (cuando existan)

### En páginas importantes

- **Value proposition** clara (qué es JobRhythm y para quién).
- **Indicador de confianza o prueba social** (placeholder si no hay datos aún).
- **CTA fuerte above the fold** (ej. “Reservar demo”, “Ver precios”, “Contactar ventas”).
- **CTA de nuevo cerca del final** de la página.

Mensajería concisa y orientada a SaaS. Evitar frases genéricas (“revolucionar tu negocio”) salvo que aporten significado concreto.

---

## HTML y semántica

- Etiquetas semánticas: `<nav>`, `<main>`, `<section>`, `<article>`, `<header>`, `<footer>`.
- El **`<nav>` principal** en páginas con menú no se escribe entero en cada archivo: se inyecta en el build (ver [Navegación global](#navegación-global-build-con-parciales)); en `src/` va el marcador `<!-- landing:inject-nav -->`.
- Un solo `<h1>` por página; jerarquía correcta (`h1` → `h2` → `h3`).
- `lang="es"` o `lang="en"` en `<html>` según la página.

### Plantilla base

```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="..." />
    <link rel="stylesheet" href="output.css" />
    <title>JobRhythm – ...</title>
  </head>
  <body class="font-sans antialiased text-gray-900 bg-white">
    <!-- landing:inject-nav -->
    <main>
      <!-- contenido principal -->
    </main>
  </body>
</html>
```

### Rutas de CSS

- En `src/*.html` usar `href="output.css"` (relativo; en `dist/` el CSS está junto al HTML).

---

## Tailwind CSS

### Colores del tema

- **primary:** `#0d6efd` (DEFAULT), `#0a58ca` (dark).
- **accent:** `#ffc107`.
- Usar `text-primary`, `bg-primary`, `hover:bg-primary-dark`, etc. (según `tailwind.config.js`) en secciones claras.
- Para el **hero dark** y zonas asociadas:
  - Fondos base: `bg-slate-950`, `bg-slate-900`, con gradientes `bg-gradient-to-b`, `bg-gradient-to-tr`.
  - Texto: `text-slate-50` para títulos, `text-slate-300/400` para cuerpo, evitando grises cálidos.
  - Acentos: `text-cyan-300`, `border-cyan-400/40`, `border-indigo-400/40`, `bg-gradient-to-r from-indigo-500 via-indigo-400 to-cyan-400`.
  - Glows suaves: sombras tipo `shadow-cyan-500/40`, `shadow-indigo-500/30`, sin efectos agresivos.

### Tipografía

- `font-sans` → Inter (o la configurada).
- Títulos: `font-bold`, tamaños `text-4xl`, `text-5xl`, etc. En el hero, escalar hasta `xl:text-7xl` si tiene sentido.
- Cuerpo: `text-gray-900`, `text-gray-600` en secciones claras; `text-slate-300/400` en secciones dark.

### Layout

- Contenedor: `max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8`.
- Espaciado: `py-20`, `gap-8`, etc.
- Responsive: prefijos `sm:`, `md:`, `lg:`.
- Nav + hero principal deben verse como un solo bloque coherente (mismo fondo dark o transiciones suaves).

### No usar

- Estilos inline (`style="..."`) salvo casos excepcionales.
- Clases CSS personalizadas fuera de `input.css`; preferir utilidades Tailwind.

---

## Rendimiento

- **JavaScript mínimo** — Solo lo imprescindible.
- **Preferir CSS frente a JS** (animaciones, estados, menús simples).
- **Evitar dependencias innecesarias.**
- **Patrones de layout reutilizables** entre páginas.
- **Imágenes comprimidas** si se añaden (WebP/optimizadas).
- **Prioridad:** first paint rápido y legibilidad.

---

## SEO

### Meta obligatorios

- `meta name="description"` — descripción única por página (≈155 caracteres).
- `meta name="keywords"` — palabras clave relevantes (construcción, contratistas, inventario, etc.).
- `meta name="robots" content="index, follow"` — salvo páginas que deban estar noindex.

### Open Graph

- `og:title`, `og:description`, `og:type`, `og:url`.
- `og:image` si hay imagen destacada.

### Canonical

- `link rel="canonical" href="https://getjobrithm.com/..."` en cada página.

### sitemap.xml y robots.txt

- Mantener `src/sitemap.xml` y `src/robots.txt` actualizados.
- Incluir todas las URLs públicas en el sitemap.

### Estrategia de keywords por nicho

No competir por términos genéricos muy disputados (ej. _construction management software_). Enfocarse en **keywords de nicho** para que el SEO sea más alcanzable, por ejemplo:

- software for electrical contractors
- crew scheduling software for construction
- material management for trade contractors
- software for HVAC crews
- software for residential contractors

Incluir estas variantes en meta keywords, títulos alternativos y contenido cuando sea natural. Priorizar long-tail y nichos alineados con “residential trade contractors”.

---

## Accesibilidad

- Enlaces con texto descriptivo; evitar “clic aquí”.
- Imágenes con `alt` significativo.
- Contraste suficiente (texto sobre fondo).
- Navegación por teclado funcional.
- Estructura de encabezados lógica para lectores de pantalla.

---

## Enlaces y navegación

### Internos (misma landing)

- Rutas relativas entre páginas equivalentes EN/ES: `index.html` ↔ `index-es.html`, `pricing-en.html` ↔ `pricing.html`, `contact-en.html` ↔ `contact.html`.
- CTAs hacia el formulario de contacto: usar ancla `#landing-contact-form` cuando el objetivo sea el formulario (p. ej. `contact-en.html#landing-contact-form`).
- En la raíz en inglés: logo y enlaces “home” coherentes con `index.html`.

### Externos (app JobRhythm)

- **Login:** `https://jobrithm.net`
- **Onboarding:** `https://www.jobrithm.net/onboarding`
- Abrir en nueva pestaña: `target="_blank" rel="noopener noreferrer"` cuando sea apropiado.

### Nav común (marca y contenido)

- En **copy y UI visible** usar el nombre **JobRhythm** (logo, navegación, pies de página). La barra debe ser **coherente** en todas las páginas: mismos ítems lógicos (Features/Workflow o Funciones/Flujo, Contacto, selector EN/ES, CTA tipo “Book a demo” / “Reservar demo”). La página de precios puede estar oculta en el menú hasta definir pricing.
- La implementación técnica del `<nav>` (partials + `build-nav.mjs`) está descrita en [Navegación global (build con parciales)](#navegación-global-build-con-parciales) y en **`landing/README.md`**.
- En la **home** se prioriza conversión; el acceso principal a login suele vivir en el footer u otras zonas, no como elemento dominante del nav.

---

## Imágenes

- Ubicación: `src/img/`.
- Formatos: PNG, JPG, WebP, SVG.
- Nombres descriptivos y en minúsculas: `hero-bg.jpg`, `logo.svg`.
- Siempre `alt` en `<img>`.
- Usar versiones comprimidas para producción.

---

## Formularios

- El formulario de contacto es estático; no hay backend en la landing.
- Usar `action` y `method` apropiados si se conecta a un servicio externo (Formspree, etc.).
- Campos con `label` asociado (`for`/`id`).
- Placeholder como complemento, no como sustituto del label.
- Formularios orientados a conversión: “Solicitar demo”, “Contactar ventas”, etc.

---

## Build y deploy

- **Build:** `npm run build` — en orden: **`build-nav.mjs`** (inyecta el `<nav>` en los HTML que llevan marcador), **Tailwind** (CSS minificado a `dist/output.css`), copia de **sitemap**, **robots**, **img**, **icons**. Los `*.html` de `dist/` salen del script de nav + copia; no se hace `cp src/*.html` directo.
- **Desarrollo:** `npm run dev` (watch solo CSS) + `npm run build` o `npm run build:watch` cuando cambien HTML o partials del nav + `npm start` (servir `dist/` en puerto 3000).
- **Deploy:** `dist/` se monta en Nginx para getjobrithm.com (ver `../../nginx/default.conf` desde esta carpeta `docs/`).

### Arquitectura ideal (site map) – Website SaaS JobRhythm

Esta es la estructura recomendada de secciones y rutas para escalar la landing y el sitio público de JobRhythm. Úsala como referencia para nuevos contenidos, navegación y enlaces:

```
/                # Home – Página principal (valor y CTA)
/product         # Producto – ¿Qué es? Qué resuelve. Visión general.
/features        # Funcionalidades – Listado y detalle de features clave.
/solutions       # Soluciones por tipo de cliente, industria o caso de uso.
/pricing         # Precios – Tabla comparativa, FAQs, políticas.
/demo            # Reservar demo (Formulario o Booking)
/blog            # Blog – Artículos, noticias, SEO.
/resources       # Recursos, guías, descargables, ayuda.
/customers       # Clientes – Casos de éxito, testimonios.
/about           # Sobre nosotros, empresa, equipo.
/contact         # Contacto directo, formularios adicionales.
```

Consideraciones:

- No todas las secciones tienen que estar activas desde el inicio, pero la navegación debe permitir escalar.
- Puedes agrupar recursos secundarios (blog, ayuda, casos de clientes) según necesidades de contenido y etapa de desarrollo.

Nota: Adapta esta arquitectura a las prioridades de marketing y SEO, asegurando siempre un flujo claro hacia el CTA ("Demo", "Precios", "Contacto").
