# JobRhythm UI — Libro de reglas (frontend upgrade)

**Qué es:** contrato operativo para pantallas migradas del upgrade (`jobrhythm-frontend-upgrade`).  
**Autoridad:** `PRODUCT.md` → `DESIGN.md` Target State (Pilot) → **este libro** → implementación.  
**Tokens / CSS:** `app/vuefrontend/src/assets/css/jr-design-system.css`  
**Preset:** `jr-primevue-preset.js`  
**Piloto vivo:** Product List + Product Form.

`app/docs/ai-guidelines.md` es **obsoleto** como guía visual (Bootstrap / `b-table` / `btn-success`). Sigue valiendo para permisos Django, `v-tt`, toasts, `search` y contratos API.

Arquitectura:

`feature view | App Shell → JR primitive → PrimeVue (styled) → tokens JR`

No mezclar Bootstrap y JR en la misma pantalla (ni en Navbar / Footer).

| Capítulo | Dónde |
|---|---|
| Este libro | Tokens, isolation, primitivos, **formularios**, **botones**, overlays |
| Listas (detalle) | [LIST_VIEWS.md](./LIST_VIEWS.md) — toolbar, tabla, badges, pager, mobile |
| Formularios (alias) | [FORMS.md](./FORMS.md) apunta aquí; no duplicar normas |

---

## 1. Isolation

- Envolver **solo** pantallas de feature migradas en `JRPage` (añade `.jr-pilot`).
- Tailwind utilities viven como `.jr-pilot .utility` (y `.jr-shell` cuando exista en el App Shell). Bootstrap (`p-4`, etc.) sigue ganando **solo** en pantallas aún no migradas.
- Tailwind Preflight **no** está activo mientras queden restos Bootstrap globales.
- **Navbar / Footer están en el alcance del upgrade:** migrar a tokens JR + PrimeVue (ver `DESIGN.md` Target State → App Shell). No dejar Bootstrap / `skin-modern` como contrato permanente del shell.
- Overlays portaleados (drawer, dialog, menú): `.jr-pilot` / `.jr-shell` / `.jr-overlay` en el overlay; menús flotantes usan `.jr-overlay`, no el `jr-pilot` de página.
- Capa CSS: `theme, base, primevue, components, utilities`. Tipografía de `h1`/`h2` del pilot y `text-decoration` de menús overlay van **fuera** de `@layer components` (Bootstrap `h1`/`a` no está en capa).
- Impeccable / design-reviewer deben evaluar Navbar y Footer contra el Target State (sin waiver “shell = Bootstrap”).

---

## 2. Tokens

Usar `var(--color-jr-*)`. No hex sueltos en la vista.

### Superficie

| Token | Valor | Uso |
|---|---|---|
| `--color-jr-page` | `#f3f4f6` | Fondo de página |
| `--color-jr-surface` | `#ffffff` | Paneles, inputs, tablas |
| `--color-jr-surface-muted` | `#f9fafb` | Header de tabla, wells, hover |
| `--color-jr-border` | `#e5e7eb` | Divisores, outline |
| `--color-jr-hover-border` | `#d1d5db` | Hover de control / thumb |
| `--color-jr-text` | `#111827` | Texto primario |
| `--color-jr-muted` | `#4b5563` | Hints, meta, secondary |

### Acción y semántica

| Token | Fill | Texto (badge / hint) | Fondo subtle |
|---|---|---|---|
| Primary | `#2563eb` / hover `#1d4ed8` | — | — |
| Success | `#16a34a` | `#166534` | mix 14% + surface |
| Danger | `#dc2626` | `#991b1b` | mix 14% + surface |
| Warning | `#d97706` | `#92400e` | mix 14% + surface |
| Info | `#0284c7` | `#1e40af` | mix 14% primary + surface |

**Badges (Light Background):** texto oscuro (~800) sobre pastel del mismo tono. Sin borde. Radio `--radius-jr-control` (`0`), no pastilla. No usar fill `#16a34a` / `#0284c7` como texto de chip (falla AA a 0.75rem).

### Tipo y radio

| Rol | Tamaño | Peso |
|---|---|---|
| Título de página | `1.3125rem` | 600, izquierda |
| Título de sección | `0.9375rem` | 600 |
| Cuerpo | `0.9375rem` | 400 |
| Label | `0.8125rem` | 600 |
| Hint / error / meta | `0.75rem` | 400 hint; 600 error / badge |
| Tabla | `0.875rem` | 600 headers |

- Familia: Inter + system-ui.
- Control: `--radius-jr-control` (`0`, rectangular). Inputs, selects, datepickers, dropdowns, botones y badges. Panel / tabla / drawer: `--radius-jr-panel` (`0.75rem`).
- Sombra solo en overlays: `--shadow-jr-overlay`.
- Labels ocultos para a11y: `jr-sr-only`, no `.visually-hidden` de Bootstrap.

---

## 3. Primitivos (`@/ui`)

Presentacionales. Sin axios. Sin reglas de negocio.

| Primitivo | Uso |
|---|---|
| `JRPage`, `JRPageHeader`, `JRSection` | Cascarón de pantalla migrada |
| `JRField` | Label, **hint**, required, error, `aria-describedby` |
| `JRButton`, `JRInput`, `JRSelect`, `JRSelectAddon`, `JRCheckbox`, `JRDatePicker`, `JRTextarea` | Controles |
| `JRBadge`, `JRDataTable`, `JRToolbar`, `JREmptyState`, `JRRowActions` | Listas |
| `JRDrawer`, `JRDialog` | Overlay / confirm (no Swal, no `window.confirm`) |
| `JRTooltip` | Extra opcional; **nunca** el único canal de una regla operativa |

`JRDataTable` acepta `Column` de PrimeVue en el slot default.

```js
import { JRPage, JRField, JRInput, JRButton, JRDialog } from '@/ui';
import Column from 'primevue/column';
import Message from 'primevue/message';
```

---

## 4. Formularios (norma — Product Form)

Referencia: `ProductForm.vue`, `ProductPriceUnitTable.vue`.  
El formulario enseña **en el campo**, no en hover.

### Hint debajo (canal por defecto)

`JRField` `hint` para una regla que cambia **dinero, identidad, stock o compras**.  
Ese texto entra en `aria-describedby` junto al error.

```vue
<JRField
  v-slot="{ describedby, invalid }"
  label="SKU"
  required
  inputId="product-sku"
  hint="Must be unique. Used in warehouse and purchasing."
  :error="fieldErrors.sku">
  <JRInput
    inputId="product-sku"
    v-model="sku"
    :invalid="invalid"
    :ariaDescribedby="describedby" />
</JRField>
```

### No un hint en cada campo

Tope: **3–4 reglas que generan tickets** por pantalla. El label basta para Name, Model, Category y equivalentes.

| Product Form | Hint |
|---|---|
| SKU | Unique; warehouse and purchasing |
| Brands | First selected brand is the default for purchasing |
| Tracking Mode | Quantity vs Serialized |
| Reorder Level | In the default warehouse unit |
| Name, Model #, Category, Default Unit, Active | Sin hint |

### Tooltip: extra, nunca único

- No copies el hint en un `JRTooltip` / `(i)`.
- No enseñes una regla comercial o de stock solo con hover.
- Tooltip solo si aporta detalle que no cabe debajo (tabla densa, jerga rara).
- El `(i)` no puede hacer más alta la fila de label que la de los vecinos.

### Una idea, un sitio

El título de sección no necesita un lede que lo parafrasee.  
Si Brands ya dice “first selected = default”, el label “Default for purchasing” no repite la frase.

### Consecuencia contextual: PrimeVue `Message`

Cuando una **elección** cambia lo que pasa después (no cómo rellenar el campo):

```vue
import Message from 'primevue/message';

<Message
  v-if="product.tracking_mode === 'SERIALIZED'"
  severity="info"
  :closable="false">
  Serialized products create one tracked unit per quantity on purchase.
</Message>
```

Tokens: `--color-jr-info-subtle`, `--color-jr-info-text`. Visible solo cuando aplica.  
El hint explica la opción; el Message explica la consecuencia.  
No uses un `<p>` suelto ni SweetAlert para esto.

### Errores y confirmaciones

- Atención: banner JR + error de `JRField` + focus al primer fallo.
- Leave dirty / delete: `JRDialog`, no `window.confirm`.
- Checkbox + label: `column-gap` ~0.85rem en form y drawers. En tabla de banderas, el header puede ser el nombre.

### Composición

```
JRPage → JRPageHeader → form
  banner (si hay errores)
  JRSection × N
    grid 1 col → 2 col (≥768) → 3 col (≥1024)
    JRField + control
  acciones sticky (Save / Cancel)
```

- Campos rectangulares: `JRInput` / `JRSelect` / `JRDatePicker` / `JRTextarea` y el overlay del dropdown usan `--radius-jr-control` (`0`). No reintroducir radio en formularios nuevos.
- **Campos de moneda / importe:** PrimeVue `InputNumber` con `mode="decimal"`, `locale="en-US"`, `:minFractionDigits="2"`, `:maxFractionDigits="2"`, label normal vía `JRField` (no `IftaLabel` / `mode="currency"` salvo brief explícito). Vacío → `0.00` al guardar. Referencia: Trim/Rough en Piece Work Price; Trim/Rough/Travel en `/builder/form` vía `DynamicForm` (`type: "decimal"`).
- Focus de campo: **una** línea — el borde pasa a primary (`#2563eb`). Sin outline, sin anillo offset, sin box-shadow. Checkboxes / icon-btns / botones sí pueden llevar outline 2px.
- Desktop ≥1024: secciones de campos en **tres columnas**.
- Catálogo add/edit: un `JRDrawer` JR. Sin apilar drawers.
- Create: sembrar la primera fila vacía si el dominio lo espera (p. ej. precios); las filas vírgenes no bloquean Save.
- Tablas embebidas (precios, líneas): **Add** en el header de sección. **Duplicate** y **Delete** por fila (`JRRowActions`), no multi-select ni “Duplicate Selected”. Duplicate clona type/unit/precio/flags; `id` vacío y `is_default` false. Delete usa `JRDialog` (las vírgenes se van sin confirm). En compacto: Edit visible + overflow para Duplicate/Delete. Un primary de sección; ghost en la fila; danger solo en Delete.
- Imágenes por marca: `ProductBrandImages` (Tabs + `FileUpload` basic + `Image` preview). Ver es libre si hay ficha. Subir / primary: `add_product` o `change_product` **y** el permiso de `productimage`. **Borrar** exige `change_product` (editar producto) **y** `delete_productimage`. En View del form (`readonly`) no hay CRUD. En create, el empty state pide guardar primero. Delete confirma con `JRDialog`. En la lista, el thumb abre el mismo componente en `JRDialog` `size="wide"` sin footer — no modal Bootstrap.

### Botones

Un botón de form, drawer o diálogo es `JRButton` → PrimeVue `Button` con clases **`p-button p-component jr-button`**. Radio `--radius-jr-control` (`0`). No inventar `<button class="btn">` ni un `Button` de PrimeVue suelto en feature.

| Superficie | Tipo | Icono |
|---|---|---|
| Form, footer de `JRDrawer`, footer de `JRDialog` | `JRButton` sólido (`primary` / `secondary` outlined) | **No.** Save, Cancel, Done, Update, Upload |
| Delete en esas superficies | `JRButton` `variant="danger"` (rojo relleno) | **No.** |
| `FileUpload` basic | `chooseButtonProps.class`: `p-button p-component jr-button` | El `+` nativo del FileUpload |
| `JRRowActions` en **lista / tabla** | Ghost (`text`) | **Sí.** Icono + label |
| `JRRowActions` en **`p-drawer`** | Sólido (`jr-button`; auto o `solid`) | **No.** Solo label |

Severities de fila: View `success` (texto `#166534`, no el fill `#16a34a`), Edit `primary`, Duplicate `secondary`, Delete `danger`.  
Familia de iconos (solo ghost de lista): `@primevue/icons` + `CopyIcon` para Duplicate. Nunca icon-only en desktop. Si la columna no cabe: overflow, no quitar el texto.

---

## 5. Listas

Composición, badges, `JRRowActions`, pager y breakpoints: **[LIST_VIEWS.md](./LIST_VIEWS.md)**.  
Referencia: `ProductListView.vue`.

Resumen: create en el header; search + stats + Refresh en toolbar; stats no filtran; el nombre es enlace a View; View / Edit / Delete = icono + label (verde / azul / danger); teléfono = lista de escaneo, no tabla aplastada.

---

## 6. Overlays

Drawers, selects y datepickers portalean a `document.body`. `JRDrawer` / `JRDialog` llevan `.jr-pilot`. Los paneles de Select / DatePicker los pinta el preset Aura, no utilities Tailwind. Botones del overlay: **§ 4 Botones**.

**`JRDialog` / `p-dialog` son rectangulares:** `border-radius: 0` (`--radius-jr-control`). Header, content y footer también cuadrados (`--p-dialog-border-radius: 0`). Referencia canónica: overlay de imágenes de producto (`ProductBrandImages` en `JRDialog` wide). No uses `--radius-jr-panel` (`0.75rem`) en dialogs; ese radio es para paneles, tablas y drawers.

---

## 7. Do / Don't

### Do

- `JRPage` / `.jr-pilot` solo en pantallas migradas.
- Tokens `var(--color-jr-*)`.
- Hint persistente + `aria-describedby` en las 3–4 reglas de ticket.
- `Message` info (no closable) para la consecuencia de una elección.
- `JRDialog` para leave / delete.
- Acciones de fila en **lista**: icono + label. En **drawer**: `jr-button` sólido, sin icono; Delete danger.
- Campos y overlays de select/datepicker rectangulares (`--radius-jr-control: 0`).
- `InputNumber` decimal (en-US, 2 decimales) para importes; vacío = `0.00`.
- `JRDialog` / `p-dialog` rectangulares (`border-radius: 0`), como el de imágenes de producto.
- Focus de campo a una sola línea (borde primary).
- Mismos endpoints, permisos y payloads que antes de migrar.

### Don't

- Tailwind Preflight o Vite mientras Bootstrap aún domine pantallas no migradas (salvo prueba segura).
- Dejar Navbar / Footer en Bootstrap / `skin-modern` como objetivo; no chrome `.navbar-*` / `.btn` / `.dropdown-*` a largo plazo en el shell.
- `.card` / `.form-control` / `.btn` / `b-table` dentro de `.jr-pilot`.
- `JRRowActions` ghost (icono + texto) en un `p-drawer`, o Delete como enlace azul.
- Redondear inputs, selects o paneles de dropdown JR.
- Redondear `JRDialog` / `p-dialog` (ni header/content/footer). No aplicar `--radius-jr-panel` a dialogs.
- Focus doble (borde + outline / halo) en el mismo campo.
- Muro de hints, o la misma oración en hint y tooltip.
- Regla operativa solo en `(i)`.
- Recuadro extra con `<p>` o Swal.
- Cambiar Django / DRF para “quedar bonito”.
- Ignores de detector que eximan Navbar / Footer “porque el shell es Bootstrap”.

---

## 8. Esqueleto mínimo

```vue
<template>
  <JRPage>
    <JRPageHeader title="…" description="…">
      <template #actions>
        <JRButton variant="primary">Save</JRButton>
      </template>
    </JRPageHeader>
    <JRSection title="Identity">
      <JRField v-slot="{ describedby }" label="SKU" hint="Must be unique." inputId="sku">
        <JRInput inputId="sku" v-model="sku" :ariaDescribedby="describedby" />
      </JRField>
    </JRSection>
  </JRPage>
</template>
```
