# Marketing Workspace — JobRhythm

Workspace de trabajo colaborativo (Oliver + agente) para el marketing de **JobRhythm**, la plataforma de operaciones de construcción para contratistas residenciales.

> VIVE **FUERA del repo** de la app (por decisión de Oliver, para no mezclar marketing con código). Ruta: `marketing-jobrhythm/`.
> No se commitea en `chalan-pro_tenant` salvo que se decida otra cosa.

## Documentos vivos

| Documento | Qué contiene |
|-----------|--------------|
| [`positioning.md`](positioning.md) | Fuente única de posicionamiento: nicho, mecánica, propuesta, pitch. |
| [`brand-kit.md`](brand-kit.md) | Reglas de marca: nombre, colores, tipografía, tono, do's/don'ts. |
| [`content-plan.md`](content-plan.md) | Pilares de contenido, segmentos por audiencia y calendario. |
| [`SEO.md`](SEO.md) | Keywords objetivo, estructura de páginas y reglas de SEO. |
| `campaigns/` | Un brief por campaña (activa o planeada). |
| `templates/` | Plantillas rellenables de copy: landing, ads, redes, blog, email. |

## Cómo trabajar aquí

1. **Definir la tarea** con un brief (`templates/copy-brief.md`) o un pedido directo.
2. El agente consulta `positioning.md` + `brand-kit.md` + `SEO.md` **antes** de escribir cualquier copy.
3. Todo copy que vaya a un canal visible debe salir **EN y ES** (obligatorio).
4. El copy de la landing **va a `landing/src/`** (EN: `index.html`/`pricing-en.html`/…, ES: `index-es.html`/`pricing.html`/…) y se publica con `npm run build` — nunca se edita `landing/dist/` a mano.
5. La app (SaaS `jobrhythm.net`) y la landing (`getjobrhythm.com`) son **dos superficies distintas**: tono/conversión para la landing; tono operativo/profesional dentro de la app.

## Comandos/entradas de referencia

- Landing: editar en `landing/src/{index(-es),pricing(-en),contact(-en)}.html`; build `LAN=.. npm run build` en `landing/`.
- Leer `landing/docs/ai-guidelines.md` para diseño/conversión/SEO de la landing.
- Fuentes de verdad de producto: `PRODUCT.md` y `DESIGN.md` (raíz del repo).
