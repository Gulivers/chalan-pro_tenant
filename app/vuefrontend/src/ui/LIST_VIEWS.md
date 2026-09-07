# JobRhythm — Estilo piloto para List Views

**Estado:** contrato visual y de composición para listas migradas a JR / PrimeVue.  
**Pantalla de referencia:** `app/vuefrontend/src/views/inventory/ProductListView.vue`  
**Tokens y CSS:** `app/vuefrontend/src/assets/css/jr-design-system.css`  
**Preset PrimeVue:** `app/vuefrontend/src/ui/jr-primevue-preset.js`  
**Autoridad:** `PRODUCT.md` → `DESIGN.md` Target State (Pilot) → este documento → implementación.

`app/docs/ai-guidelines.md` es **obsoleto** como guía visual del upgrade (Bootstrap / `b-table`). Libro general del upgrade (tokens, isolation, formularios): [README.md](./README.md). Este archivo es el capítulo de **listas**. No mezclar Bootstrap y JR en la misma pantalla.

---

## 1. Carácter

Construction Operations / ERP admin. Operativo, denso, mobile-first.

- Neutrales + **un** azul de acción.
- Bordes 1px, sin sombras de tarjeta, sin pastillas `999px`.
- El nombre de la entidad es **texto**, no un enlace azul.
- El create (`+ New …`) es el único botón primary de la página.
- Sin Bootstrap (`.card`, `.btn`, `.badge`, `.form-control`, `.visually-hidden`, `d-flex`, etc.) dentro de `.jr-pilot`.

---

## 2. Tokens

Usar siempre `var(--color-jr-*)`. No hex sueltos en la vista.

### Superficie

| Token | Valor | Uso |
|---|---|---|
| `--color-jr-page` | `#f3f4f6` | Fondo de la página |
| `--color-jr-surface` | `#ffffff` | Tabla, inputs, drawer |
| `--color-jr-surface-muted` | `#f9fafb` | Header de tabla, hover, wells |
| `--color-jr-border` | `#e5e7eb` | Divisores, outline de tabla |
| `--color-jr-hover-border` | `#d1d5db` | Hover de thumb / icon-btn |
| `--color-jr-text` | `#111827` | Título, nombre, headers |
| `--color-jr-muted` | `#4b5563` | Meta, hints, Inactive / Total |

### Acción y semántica

| Token | Fill | Texto en badge | Fondo badge (subtle) |
|---|---|---|---|
| Primary | `#2563eb` / hover `#1d4ed8` | — | — |
| Success | `#16a34a` | `#166534` | mix 14% fill + surface |
| Danger | `#dc2626` | `#991b1b` | mix 14% fill + surface |
| Warning | `#d97706` | `#92400e` | mix 14% fill + surface |
| Info / azul | `#0284c7` | `#1e40af` | mix 14% primary + surface |

**Receta de badge (Light Background):** texto oscuro (~800) sobre pastel del mismo tono. Sin borde. No usar fill `#16a34a` como texto de chip (falla AA a 0.75rem sobre blanco).

### Tipo y radio

| Rol | Tamaño | Peso |
|---|---|---|
| Título de página (`JRPageHeader`) | `1.3125rem` | 600, izquierda |
| Cuerpo | `0.9375rem` | 400 |
| Tabla / nombre de fila | `0.875rem` | 600 el nombre; 600 headers |
| Badge / meta / SKU | `0.75rem` | 600 badge; 400 meta |
| Label de campo | `0.8125rem` | 600 |

- Familia: Inter + system-ui.
- Control radius: `--radius-jr-control` (`0`, rectangular). Search, selects y overlays de dropdown incluidos.
- Panel / tabla / drawer: `--radius-jr-panel` (`0.75rem`).
- Overlay shadow solo en drawer / menú: `--shadow-jr-overlay`.
- Labels de formulario: `jr-sr-only` (no `.visually-hidden` de Bootstrap).

---

## 3. Composición de la página

```
JRPage                          ← .jr-pilot, text-align left
  JRPageHeader                  ← título + #actions (create)
  JRToolbar
    #start                      ← búsqueda (crece)
    #stats                      ← chips no interactivos
    #actions                    ← page-size, herramientas, Refresh
  contenido
    <768px                      ← lista de escaneo + Paginator
    ≥768px                      ← JRDataTable
  JRDrawer                      ← herramientas pesadas (Bulk, export…)
```

- Sin `.card` / `.card-modern` envolviendo la página.
- Create en `#actions` del header, no en el toolbar. En teléfono: `:fluid="isMobile"`.
- Toolbar en **columna hasta 1023px**; en desktop (`≥1024`) fila: search `max-width: 36rem`, stats, actions `margin-left: auto`.
- Stats **no son filtros**. `pointer-events: none`. Total / Inactive = `secondary`. Active / conteo positivo de estado = `success`.

---

## 4. Botones

| Rol | Variante | Color |
|---|---|---|
| Crear (`+ New …`) | `JRButton` primary | `#2563eb` |
| Refresh, Bulk, secundarios de toolbar | `ghost` `size="sm"` | muted / secondary text |
| View | `JRRowActions` `severity: "success"` | fill `#16a34a` (texto de acción, no el 800 del badge) |
| Edit | `severity: "primary"` | mismo azul que New |
| Delete | `severity: "danger"` | `#dc2626` |

PrimeVue no tiene `severity="primary"`: `JRRowActions` lo mapea a severity `undefined` (botón default) y clase de menú `--primary`.

Iconos: familia `@primevue/icons` (Search, Refresh, Eye, Pencil, Trash). Duplicate (tablas embebidas) usa `CopyIcon` en `ui/CopyIcon.vue` — mismo BaseIcon 14×14; `@primevue/icons` 5 no incluye Copy. No mezclar SVG a mano con PrimeIcons en el mismo chrome. Acciones de fila: **icono + label**. Nunca icon-only en desktop.

---

## 5. Badges (`JRBadge`)

```vue
<JRBadge :value="item.is_active ? 'Active' : 'Inactive'"
         :severity="item.is_active ? 'success' : 'secondary'" />
<JRBadge v-if="serialized" value="Serial" severity="info" />
<JRBadge v-else value="Qty" severity="secondary" />
```

| Severity | Cuándo |
|---|---|
| `success` | Active, estados OK |
| `info` | Distinción operativa (Serial, tipo) — azul profundo, no cian Bootstrap |
| `secondary` | Inactive, Total, Qty, vacío |
| `danger` / `warn` | Error / pendiente — misma receta pastel + texto 800 |

No usar PrimeVue `Tag` ni Bootstrap `badge`.

---

## 6. Acciones de fila (`JRRowActions`)

- Desktop (`≥1024`): **icono + label** View / Edit / Delete (o equivalente: Duplicate). El icono no sustituye al texto.
- Tablet y teléfono: menú overflow (44px) con los **mismos** iconos.
- `entity-label` para `aria-label` (`View {name}`, `More actions for {name}`).
- Columna Actions: header y celdas **centradas** sobre el grupo de botones. El `scoped` de la vista no pinta el `<th>` de PrimeVue: usar `:deep(th.jr-col-actions)` desde el wrapper de la tabla.
- Si la fila no cabe: overflow para Duplicate/Delete. No quitar labels para ganar ancho.

```css
.jr-list__table :deep(th.jr-col-actions),
.jr-list__table :deep(td.jr-col-actions) {
  text-align: center;
}
.jr-list__table :deep(th.jr-col-actions .p-datatable-column-header-content),
.jr-list__table :deep(td.jr-col-actions .jr-row-actions) {
  justify-content: center;
  width: 100%;
}
```

Delete siempre confirma (flujo existente del proyecto). No borrar en un clic.

---

## 7. Responsive

| Viewport | Layout | Columnas típicas |
|---|---|---|
| Teléfono `<768` | Lista: thumb + nombre + meta · status + overflow | No tabla |
| Tablet `768–1023` | Tabla corta | Name (+ SKU debajo), campos clave, Status, Actions compact |
| Desktop `≥1024` | Catálogo denso | + columnas de oficina; Actions icono + label |

Breakpoints canónicos:

```js
const PHONE_MQ = "(max-width: 767.98px)";
const TABLET_MQ = "(min-width: 768px) and (max-width: 1023.98px)";
```

- No mostrar Id ni SKU como columna si el SKU ya va bajo el nombre.
- `tableMinWidth`: ~`36rem` tablet / ~`48rem` desktop. Scroll horizontal controlado, no 10 columnas aplastadas en tablet.
- Thumb: control que abre galería / detalle visual. **No** es el View del registro.

---

## 8. Tabla (`JRDataTable`)

- Superficie blanca, borde 1px, radio panel, filas striped, hover muted.
- Celdas: `0.875rem`, padding vertical `0.3rem`.
- Números / reorder: `text-align: right` + `tabular-nums`.
- Lazy + sort del servidor: `page`, `per_page`, `search`, `ordering`. No reinventar el contrato del provider.
- Empty: `JREmptyState` (copy). No meter acciones de recover en el empty salvo que el producto lo pida.

Estilos de tabla que viven en PrimeVue (thead, td) van con `:deep` desde un wrapper de la vista (p. ej. `.jr-product-list__table`).

---

## 9. Paginador

- Desktop (en la tabla): First / Prev / PageLinks / Next / Last + `{first}–{last} of {totalRecords}`.
- Teléfono (Paginator suelto): **Prev | reporte centrado | Next**.
- Destinos táctiles en móvil: `2.75rem`. Radio de control, no círculo Aura.
- El flex de PrimeVue 4/5 está en `.p-paginator-content`, no solo en `.p-paginator`. Sin eso, Prev/Next se pegan a la izquierda.

```css
.jr-list__pager :deep(.p-paginator-content) {
  width: 100%;
  justify-content: space-between;
}
```

---

## 10. Herramientas pesadas

Bulk Excel, exports, imports: `JRButton` ghost → `JRDrawer` a la derecha.

- UI del panel: primitivos JR + PrimeVue (`FileUpload` basic, `JRField`, `JRButton`).
- No islas Bootstrap dentro del drawer.
- Permisos y endpoints iguales que antes de migrar.
- Drawer full-viewport en teléfono.

---

## 11. Accesibilidad mínima

- Labels visibles o `jr-sr-only` en search y page-size.
- Focus visible: outline 2px `--color-jr-primary`.
- Stats con `aria-live="polite"` si cambian con el fetch.
- Thumb: `aria-label` honesto (`View images of {name}`), no fingir que abre el form.
- `prefers-reduced-motion` ya está en el design system.

---

## 12. Qué no hacer

- Pintar el nombre de la fila de azul / underline (parece View y no lo es).
- `Tag`, `ToggleButton` o `b-table` en una lista JR.
- Stats que parecen filtros y no filtran.
- Ghost / Refresh en azul primary (compiten con New).
- Edit en cian `info`; Edit es primary.
- `border-radius: 999px` en badges o pager.
- Tailwind Preflight, `.jr-pilot` en Navbar/Footer, o migrar el shell en este incremento.
- Cambiar Django / contratos API para “quedar bonito”.

---

## 13. Checklist al migrar otra List View

1. Envolver en `JRPage` / `JRPageHeader` / `JRToolbar` / `JRDataTable` / `JRRowActions` / `JRBadge` / `JREmptyState`.
2. Create en el header; search + stats + Refresh en el toolbar.
3. Tres breakpoints (lista / tabla corta / tabla densa).
4. Badges Light Background con tokens JR.
5. View verde acción, Edit azul New, Delete danger; cada una **icono + label**.
6. Actions header centrado vía `:deep`.
7. Pager móvil a todo el ancho, 44px.
8. Cero clases Bootstrap en la vista y en paneles que abra.
9. Mismos endpoints, permisos, `search`, `ordering`, confirm de delete.
10. Referencia visual: Products.

```vue
<JRPage>
  <JRPageHeader :title="title">
    <template #actions>
      <JRButton v-if="canCreate" :fluid="isMobile" @click="goToCreate">
        + New …
      </JRButton>
    </template>
  </JRPageHeader>
  <JRToolbar>
    <template #start><!-- JRInput search --></template>
    <template #stats><!-- JRBadge Total / Active / Inactive --></template>
    <template #actions><!-- page-size, ghost tools, Refresh --></template>
  </JRToolbar>
  <!-- phone list or JRDataTable -->
</JRPage>
```
