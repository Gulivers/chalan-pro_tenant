# Brand Kit — JobRhythm

Reglas de marca para todo material de marketing. Destilado de `DESIGN.md`, `landing/AGENTS.md`, `PRODUCT.md`.

## Nombre

- **Comercial / visible:** **JobRhythm** (app, landing, PDFs, mensajes, presentaciones).
- **Técnico / interno:** `chalanpro`, `Chalan-Pro`, `chalan-pro_tenant`, `jobrithm.net` (alias técnico) — solo en rutas, variables, infraestructura.
- No usar "Chalan-Pro" como nombre comercial en ningún copy visible.
- Durante la transición siguen activos los legacy `jobrithm.net` y `getjobrithm.com` (no reescribir dominios salvo pedido explícito).

## Dominios

- SaaS / app: **`jobrhythm.net`** (subdominios tenant).
- Landing: **`getjobrhythm.com`**.
- Legacy (transición): `jobrithm.net`, `getjobrithm.com`.

## Colores

### Landing (Tailwind) — `landing/tailwind.config.js`
- `primary` **#0d6efd**, `primary-dark` **#0a58ca**, `accent` **#ffc107**.
- Fondo claro, diseño B2B SaaS (espíritu Stripe / Linear / Notion).

### App (tokens Pilot, `--color-jr-*`)
- Page `#f3f4f6`, surface `#ffffff`, surface-muted `#f9fafb`, border `#e5e7eb`.
- Text `#111827`, muted `#4b5563`.
- Primary `#2563eb`, hover `#1d4ed8`.
- Semánticos: success `#16a34a`, danger `#dc2626`, warning `#d97706`, info `#0284c7`.

> **Regla de semántica:** success/warning/danger/info se mantienen inconfundibles — no atenuarlas para "hacer match" con la marca.

## Tipografía

- **Inter** (con fallback system-ui) en app y landing.
- Carácter: operativo, medio-peso para labels, títulos en negrita, cabeceras de tabla legibles. Densidad legible, no display marketing.
- Sistema operativo/operacional por defecto para el copy del app; landing puede usar Inter como familia única, jerarquía clara.

## Tono de voz

- **Profesional, técnico, confiable** — no gloss de marketing de consumo dentro de la app.
- Landing: B2B SaaS claro y directo, con CTAs accionables.
- Español = neutro latino de negocio; Inglés = Americano (en-US).
- **Bilingüe obligatorio** para cualquier copy de canal visible (EN + ES).

## Do's

- Usar **JobRhythm** siempre en visible.
- Mantener colores semánticos claros para estados operativos.
- Copy scannable, CTAs claros ("Reservar demo", "Contactar ventas", "Ver precios").
- Densidad y claridad sobre decoración.

## Don'ts

- No "Chalan-Pro" ni `chalanpro` en visible.
- No gradientes de texto, glow ni micro-animaciones decorativas en flujos de trabajo.
- No usar emoji como sistema de iconos en copy de producto.
- No inventar customer logos / testimonios / benchmarks / pricing.
- No reescribir dominios legacy sin aprobación.
