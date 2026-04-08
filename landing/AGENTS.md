# Agentes – Landing Jobrithm (Marketing SaaS)

Contexto para agentes de IA (Cursor, Copilot, etc.) que trabajan en la **web de marketing** de Jobrithm (`getjobrithm.com`).

## Nota de marca (importante)

- A nivel comercial y en **todo copy visible** en la landing (títulos, párrafos, CTAs, meta, navegación, pies de página), el nombre del sistema es **Jobrithm**.
- **Chalan-Pro / chalanpro** se mantiene para nombres técnicos cuando aplique: dominios ya publicados, variables o rutas del repositorio. No reescribir URLs ni dominios salvo que el usuario lo pida explícitamente.

## Qué es este proyecto

- **Sitio estático de marketing** para `getjobrithm.com`: explicar el producto, captar leads y apoyar SEO.
- **No es la app interna.** La app (Vue.js SPA, multi-tenant) está en `jobrithm.net`.
- **Stack:** HTML5 estático + Tailwind CSS (CLI). JavaScript vanilla solo cuando sea necesario. Sin Vue, React, Alpine ni jQuery en la landing.
- **Relación:** La landing enlaza a `jobrithm.net` para login y onboarding; objetivos de conversión: reservar demo, contactar ventas, ver precios.

## Idiomas (obligatorio)

Los cambios de contenido y estructura relevantes deben aplicarse **en español y en inglés**:

- **Inglés (predeterminado en la raíz del sitio):** `landing/src/index.html`, `pricing-en.html`, `contact-en.html`, etc.
- **Español:** `landing/src/index-es.html`, `pricing.html`, `contact.html`, etc.
- **Compatibilidad:** `landing/src/index-en.html` redirige a `index.html` (enlaces antiguos a `/index-en.html`).

Mantener paridad de secciones, enlaces internos entre versiones ES/EN, y ejecutar `npm run build` tras editar para actualizar `dist/`.

**Navegación (build):** El `<nav>` no vive duplicado en cada HTML de `src/`. Se genera desde `landing/src/partials/nav-en.html` y `nav-es.html`, inyectado por `landing/build-nav.mjs` (marcador `<!-- landing:inject-nav -->`, configuración `NAV_BY_FILE`). El resultado en `dist/` es HTML estático completo (adecuado para SEO). Detalle en **`landing/README.md`** (sección “Navegación”). No abrir `src/*.html` en el navegador esperando ver el menú: usar `npm run build` y servir `dist/` o `npm start`.

## Posicionamiento

Jobrithm es una **plataforma de operaciones de construcción** para contratistas, supervisores y equipos de campo. La web debe transmitir: moderno, profesional, confiable, con CTAs claros y diseño tipo B2B SaaS (referencias de espíritu: Stripe, Linear, Notion; sector: Buildertrend, Procore, ServiceTitan).

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

## Estrategia de marketing

**Ventaja competitiva:** Mi ventaja no es competir contra gigantes. Mi ventaja es dominar el espacio entre field service y construction management.

En vez de competir por keywords genéricas como **construction management software** (dominadas por grandes empresas), enfocarse en nichos:

- software for electrical contractors
- crew scheduling software for construction
- material management for trade contractors
- software for HVAC crews

El SEO se vuelve mucho más alcanzable.

## Pitch de 30 segundos

**Versión “Jordan Belfort style”** (tono directo, pregunta-retorno, cierre claro):

> Let me ask you something.
>
> Right now, how do you track what each crew is doing, what materials they need, and what every job is costing you?
>
> Most contractors rely on calls, texts, and paper notes. That creates chaos.
>
> Our system replaces all of that with one platform that runs scheduling, contracts, materials, and job communication.
>
> So instead of guessing what's happening in the field, you see it in real time.

Construction has a rhythm.
Jobrithm runs it.

---

## Estructura clave

```
landing/
├── src/           # Editar aquí (HTML, input.css, img, partials del nav)
├── src/partials/  # nav-en.html / nav-es.html — plantillas del menú (inyectadas en build)
├── build-nav.mjs  # Inyecta el nav en dist/; ver README sección “Navegación”
├── dist/          # Build output — no editar manualmente
├── docs/          # Documentación
│   └── ai-guidelines.md   # Estándares obligatorios (diseño, conversión, SEO)
├── tailwind.config.js    # Colores primary/accent, fuentes
└── package.json   # Scripts: build, dev, start
```

## Reglas para agentes

1. **Editar solo en `src/`** — Los archivos en `dist/` se generan con `npm run build`. El menú global: editar **`src/partials/nav-*.html`** y, si hace falta enlaces por página, **`build-nav.mjs`** (`NAV_BY_FILE`); no pegar un `<nav>` entero en cada página salvo excepción acordada.
2. **Seguir `docs/ai-guidelines.md`** — HTML, Tailwind, diseño B2B SaaS, estrategia de conversión, SEO, accesibilidad, rendimiento.
3. **Colores:** Usar `primary` (#0d6efd), `primary-dark` (#0a58ca), `accent` (#ffc107) según `tailwind.config.js`.
4. **Enlaces app:** Login → https://jobrithm.net, Onboarding → https://jobrithm.net/onboarding.
5. **Marca en UI y copy:** Usar **Jobrithm** en textos visibles; no usar “Chalan-Pro” como nombre comercial en la landing salvo contexto técnico explícito.
6. **Bilingüe:** Cualquier cambio sustancial (copy, secciones nuevas, CTAs, meta, navegación) debe replicarse en **EN** e **ES** (`index.html` ↔ `index-es.html`, y pares `pricing` / `contact`, etc.).
7. **Conversión:** Cada página importante debe tener value proposition, indicador de confianza (o placeholder), CTA above the fold y CTA cerca del final. Objetivos: reservar demo, contactar ventas, ver precios.
8. **Rendimiento:** JavaScript mínimo; preferir CSS sobre JS; evitar dependencias innecesarias; first paint rápido.
9. **Build:** Tras cambios en `src/`, ejecutar `npm run build` para actualizar `dist/`.

## Comandos útiles

- `npm run build` — Generar dist
- `npm run dev` — Watch Tailwind (en paralelo con `npm start` para desarrollo)
- `npm start` — Servir dist en puerto 3000

## Archivos de referencia (contexto)

- **README landing:** `landing/README.md` — inspiración, nicho, diagrama de posicionamiento, comandos, estructura del proyecto y **navegación (parciales + `build-nav.mjs`)**.
- **Estándares y guías:** `landing/docs/ai-guidelines.md` — diseño, conversión, SEO, accesibilidad; obligatorio para copy y maquetado.
- **Proyecto principal (app):** `../AGENTS.md` (raíz del repo) — contexto global (Jobrithm / Chalan-Pro técnico).
- **Nginx landing:** `nginx/default.conf` — server block `getjobrithm.com` (y hosts legacy si aplica).

## Convenciones técnicas (resumen)

- Construida en **HTML plano + Tailwind CSS** (compilado, no en caliente).
- **No introducir frameworks** ni dependencias JS: nada de React, Vue, Alpine, jQuery, etc.
- El HTML debe ser **limpio, semántico**, solo **un H1 por página**, y aprovechar clases responsive de Tailwind.
- Mantén coherencia de diseño, navegación y footer entre páginas ES/EN.
- Sigue la estructura y convenciones descritas en `docs/ai-guidelines.md`.
- Prioriza **SEO, accesibilidad y rendimiento**.
- JavaScript solo si es esencial para la UI, y siempre minimalista.
- Para generar cambios en producción, **edita siempre archivos en `src/`**, luego ejecuta `npm run build`. **No alteres manualmente el contenido de `dist/`.**

## Links clave (conversiones)

- Iniciar sesión: https://jobrithm.net
- Onboarding usuarios: https://jobrithm.net/onboarding
