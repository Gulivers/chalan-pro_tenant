# Agentes – Landing Chalan-Pro (Marketing SaaS)

Contexto para agentes de IA (Cursor, Copilot, etc.) que trabajan en la **web de marketing** de Chalan-Pro (chalanpro.com).

## Qué es este proyecto

- **Sitio estático de marketing** para chalanpro.com: explicar el producto, captar leads y apoyar SEO.
- **No es la app interna.** La app (Vue.js SPA, multi-tenant) está en chalanpro.net.
- **Stack:** HTML5 estático + Tailwind CSS (CLI). JavaScript vanilla solo cuando sea necesario. Sin Vue, React, Alpine ni jQuery en la landing.
- **Relación:** La landing enlaza a chalanpro.net para login y onboarding; objetivos de conversión: reservar demo, contactar ventas, ver precios.

## Posicionamiento

Chalan-Pro es una **plataforma de operaciones de construcción** para contratistas, supervisores y equipos de campo. La web debe transmitir: moderno, profesional, confiable, con CTAs claros y diseño tipo B2B SaaS (referencias de espíritu: Stripe, Linear, Notion; sector: Buildertrend, Procore, ServiceTitan).

## Estructura clave

```
landing/
├── src/           # Editar aquí (HTML, input.css, img)
├── dist/          # Build output — no editar manualmente
├── docs/          # Documentación
│   └── ai-guidelines.md   # Estándares obligatorios (diseño, conversión, SEO)
├── tailwind.config.js    # Colores primary/accent, fuentes
└── package.json   # Scripts: build, dev, start
```

## Reglas para agentes

1. **Editar solo en `src/`** — Los archivos en `dist/` se generan con `npm run build`.
2. **Seguir `docs/ai-guidelines.md`** — HTML, Tailwind, diseño B2B SaaS, estrategia de conversión, SEO, accesibilidad, rendimiento.
3. **Colores:** Usar `primary` (#0d6efd), `primary-dark` (#0a58ca), `accent` (#ffc107) según `tailwind.config.js`.
4. **Enlaces app:** Login → https://chalanpro.net, Onboarding → https://chalanpro.net/onboarding.
5. **Idioma:** Contenido en español; meta y atributos en español.
6. **Conversión:** Cada página importante debe tener value proposition, indicador de confianza (o placeholder), CTA above the fold y CTA cerca del final. Objetivos: reservar demo, contactar ventas, ver precios.
7. **Rendimiento:** JavaScript mínimo; preferir CSS sobre JS; evitar dependencias innecesarias; first paint rápido.
8. **Build:** Tras cambios en `src/`, ejecutar `npm run build` para actualizar `dist/`.

## Comandos útiles

- `npm run build` — Generar dist
- `npm run dev` — Watch Tailwind (en paralelo con `npm start` para desarrollo)
- `npm start` — Servir dist en puerto 3000

## Archivos de referencia

- **Estándares y guías:** `landing/docs/ai-guidelines.md`
- **Proyecto principal (app):** `../AGENTS.md` (raíz del repo) — contexto Chalan-Pro completo
- **Nginx landing:** `nginx/default.conf` — server block chalanpro.com

- Construida en **HTML plano + Tailwind CSS** (compilado, no en caliente).
- **No introducir frameworks** ni dependencias JS: nada de React, Vue, Alpine, jQuery, etc.
- El HTML debe ser **limpio, semántico**, solo **un H1 por página**, y aprovechar clases responsive de Tailwind.
- Mantén el diseño, navegación y footer tal como están.
- Sigue la estructura y convenciones descritas en `docs/ai-guidelines.md`.
- Prioriza el **SEO, accesibilidad y rendimiento**.
- JavaScript solo si es esencial para la UI, y siempre minimalista
  -Para generar cambios en producción, **edita siempre archivos en `src/`**, luego ejecuta `npm run build`.  
  **Nunca alteres manualmente el contenido de `dist/`**

Links clave (conversiones):

- Iniciar sesión: https://chalanpro.net
- Onboarding usuarios: https://chalanpro.net/onboarding
