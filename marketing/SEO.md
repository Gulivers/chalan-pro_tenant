# SEO — JobRhythm

Keywords, estructura y reglas. Estrategia: **nicho en vez de keywords genéricas dominadas por gigantes.**

## Regla de oro

Competir por nichents alcanzables, NO por "construction management software" (dominada por gigantes).

## Keywords objetivo

### Núcleo (long-tail de nicho)
- software for electrical contractors
- crew scheduling software for construction
- material management for trade contractors
- software for HVAC crews
- software for plumbing contractors
- construction operations platform

### Secundarias
- field service software for construction crews
- contractor scheduling software residential
- missing material request software
- piece-work contract software construction

### On-page
- Índice semántica de landing: `index.html`, `pricing` y `contact` (+ versiones `-en`/`-es`).
- Un solo H1 por página; secciones semánticas; CTAs cerca del in y del final.

## Estructura de páginas (landing)

| Página | URL (EN) | URL (ES) | Intención |
|--------|----------|----------|-----------|
| Home | `getjobrhythm.com/` | `/index-es.html` | value prop + CTAs |
| Pricing | `/pricing-en.html` | `/pricing.html` | ver precios |
| Contact | `/contact-en.html` | `/contact.html` | reservar demo / ventas |
| (futura) Blog | `/blog/...` | `/es/blog/...` | SEO (pilares) |

## Reglas técnicas

- Editar **solo `landing/src/`**; `npm run build` regenera `dist/` (SEO estático completo). Nunca editar `dist/` a mano.
- Meta title/description por página, bilingüe.
- `<nav>` se genera desde `src/partials/nav-{en,es}.html` vía `build-nav.mjs`; no duplicar nav a mano.
- Rendimiento: JS mínimo, preferir CSS; first paint rápido.
- Accesibilidad: contraste, labels, un H1.

## Backlinks/centros de contenido (plan)

- 1 artículo pilar por keyword núcleo, interconectados.
- Linkedin/industry forums apuntando a landing.
- (Sin inventar perfiles ni testimonios.)
