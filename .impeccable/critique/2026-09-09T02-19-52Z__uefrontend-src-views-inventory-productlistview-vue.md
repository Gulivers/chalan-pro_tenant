---
target: app/vuefrontend/src/views/inventory/ProductListView.vue
total_score: 25
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 4
timestamp: 2026-09-09T02-19-52Z
slug: uefrontend-src-views-inventory-productlistview-vue
---
**Method: dual-agent (A: e1f00cfa-6b18-4a26-8397-69a75b11f443 · B: 9523f3b5-66fb-4c90-86f1-049b9511d0d8)**

# Critique — ProductListView.vue (JobRhythm Products)

Modo **Operate**. Inspeccionado en vivo en `http://test-dominio-local.chalanpro.net:8082/products` con 674 productos reales, a 1440x900 y 390x844.

## Design Health Score

| # | Heurística | Score | Hallazgo clave |
|---|-----------|-------|----------------|
| 1 | Visibilidad del estado | 3 | Máscara de carga de escritorio **transparente** (filas viejas legibles) y tabla sin `aria-busy`; la lista móvil sí lo pone. `setTimeout(300)` artificial en cada fetch. |
| 2 | Correspondencia con el mundo real | 3 | SKU / Reorder / Unit / Serial-vs-Qty hablan el oficio, pero el drawer expone `unit_code`, `price_type_name` en crudo y "Bulk Excel" nombra el formato, no el trabajo. |
| 3 | Control y libertad | 2 | El diálogo de imágenes no tiene botón de cerrar y el foco nunca entra: solo Escape. Sin undo tras aplicar precios masivos. 27 páginas sin salto directo. |
| 4 | Consistencia y estándares | 2 | El título renderiza **40px/500** contra `1.3125rem/600` comprometido en DESIGN.md. |
| 5 | Prevención de errores | 3 | Validación de tipo de archivo, confirmación explícita con Cancel, controles por permiso. Pero la confirmación no dice cuántas filas cambiarán. |
| 6 | Reconocer antes que recordar | 3 | Fila con nombre + SKU + categoría + marca + unidad + estado y foto. Pero 6 de 25 thumbnails son cajas grises sin señal de "sin foto". |
| 7 | Flexibilidad y eficiencia | 2 | Sin atajo para enfocar búsqueda, sin multi-selección, ~130 tabulaciones entre toolbar y paginador, `Brand` sin `sortable`. |
| 8 | Estético y minimalista | 3 | Densidad y paleta contenida correctas. Socavado por título de 40px y dos columnas constantes. |
| 9 | Recuperación de errores | 2 | Errores de delete diferenciados por status (403/409). Pero el estado de fallo dice "Try Refresh" y Refresh está en la toolbar; el estado vacío no repite la búsqueda ni ofrece limpiarla. |
| 10 | Ayuda y documentación | 2 | Bulk Excel se explica y trae plantilla, pero `JRPageHeader.description` sin usar; "Serial" vs "Qty" nunca se explica y Reorder no dice su unidad. |
| **Total** | | **25/40** | **Aceptable** |

## Design Specificity Verdict

**Autorado en los bordes, genérico en el centro.** Ya no es una tabla Bootstrap con piel nueva (los problemas estructurales de agosto están resueltos), pero la composición de escritorio sigue siendo una grilla CRUD de 8 columnas elegidas desde el modelo Django, no desde la pregunta del operador.

Autorado para contratista residencial: el breakpoint móvil está compuesto, no degradado (fila de 89px que suelta las columnas que un crew lead no puede accionar); el modelo de imágenes por marca (SIEMENS / SQUARE D / ABB / LEVITON con una primaria que alimenta el thumbnail); el vocabulario del oficio.

Genérico: `Tracking` muestra `Qty` en 674/674 y Status es `Active` en 670/674 — juntas ~211px de 1360px. No hay precio, existencia ni almacén, aunque el propio `Bulk Excel` de esta pantalla sobrescribe precios de venta y el dashboard reporta $192,105 en inventario.

**Escaneo determinista:** `detect.mjs` devolvió cero hallazgos, exit 0, en la vista y en los 20 primitivos de `src/ui`. Leer con cuidado: el detector se auto-reporta `DEGRADED — HTML parser modules unavailable`, modo que no evalúa custom properties, selectores ni contraste computado, y `design-system-color` está inerte ahí. Limpio no es evidencia de adherencia a tokens; el título a 40px es exactamente lo que ese modo no ve.

**Overlay:** inyección exitosa (servidor puerto 8400, detenido y verificado); overlays creados y limpiados. Reportó `low-contrast` real de 2.8:1 en `h2.footer-flow-title` (footer global, no esta vista) y `overused-font: inter` (suprimido por configuración a propósito).

## Overall Impression

Los tres problemas mayores de agosto están arreglados: el nombre abre la ficha, el drawer de Excel ya no es isla Bootstrap, el móvil se re-compone. Quedan dos clases distintas: una falla de cascada CSS que hace que el design system pierda silenciosamente contra Bootstrap en la pantalla de referencia del pilot, y un set de columnas que responde al modelo y no al operador. Mayor oportunidad: si `Tracking` dice "Qty" 674/674 y Status "Active" 670/674, hay ~210px libres para precio o existencia.

## What's Working

**El breakpoint móvil está autorado.** A 390px cada fila es de 89px: foto 40px, nombre como link a la ficha, `SKU · categoría` secundario, badge de estado, overflow 44px. La resta es deliberada: suelta Reorder/Unit/Tracking/Brand, conserva foto y SKU, y pone las tres acciones destructivas detrás de un target de 44px.

**La verdad del objeto está corregida.** El nombre azul resuelve a `/products/form?mode=view&id=959`; el thumbnail es botón aparte con "View images of {name}". Era el hallazgo #1 del critique anterior.

**El foco es visible y correcto.** Verificado con teclado real: `+ New Product`, select de página, Bulk Excel, `th` ordenables, thumbnail y link del nombre pintan `2px solid #2563eb` con 2px de offset; la búsqueda usa el borde primario único del contrato, sin doble anillo.

## Priority Issues

### [P1] El design system pierde contra Bootstrap en el cascade layer

**Qué.** Título en `font-size: 40px; font-weight: 500` a 1440px (27.85px a 390px, fluido). La regla correcta existe en `jr-design-system.css:115-122` dentro de `@layer components` (línea 57), y el `h1 { font-size: calc(1.375rem + 1.5vw) }` sin capa de Bootstrap le gana sin importar especificidad. Comprobado en vivo: inyectar el selector idéntico sin capa dio `21px/600`.

**Por qué importa.** DESIGN.md prohíbe explícitamente el título de escala marketing y la pantalla entrega algo más grande que los 2rem prohibidos. En teléfono quema 34px donde caben cuatro filas. Es una clase de fallo: el mismo mecanismo subraya los tres ítems del menú overflow (`a { text-decoration: underline }` de Bootstrap alcanza el menú portaleado, cuya raíz lleva `jr-overlay jr-row-menu` pero no `.jr-pilot`).

**Fix.** `@import "bootstrap" layer(base)`, o sacar la tipografía a nivel de elemento del pilot de `@layer components` a CSS sin capa (como ya está `.p-dialog.jr-dialog` en línea 820). Re-verificar título, `h2`–`h6` en `.jr-pilot` y `text-decoration` del menú. Hay dos declaraciones `@layer` en conflicto vivas: la posición relativa de `components` y `primevue` no está fijada.

**Comando:** `/impeccable polish`

### [P1] El diálogo de imágenes no recibe el foco y no tiene botón de cerrar

**Qué.** Al abrir, `document.activeElement` se queda en el thumbnail externo, con 12 enfocables dentro y `aria-modal="true"`. No existe `.p-dialog-close-button`. Escape cierra y devuelve foco.

**Por qué importa.** Usuario de teclado o lector de pantalla no tiene forma tabulable de llegar a Upload, Set primary ni cerrar. Escape es la única salida y nada lo anuncia. Único P1 de a11y restante; el escaneo determinista no puede verlo.

**Fix.** Enfocar el primer control al abrir (o contenedor con `tabindex="-1"`), agregar botón de cerrar en `JRDialog`, confinar el foco. `JRDialog` es primitivo compartido: arregla todos los overlays del pilot.

**Comando:** `/impeccable harden`

### [P1] En teléfono, 55% del viewport es chrome antes del primer producto

**Qué.** A 390x844 la primera `.jr-product-row` empieza en y=464; caben cuatro filas. 265px de chrome: título 33px, `+ New Product` 44px, búsqueda 44px, stats 22px, page-size + Bulk Excel + Refresh 44px. Además 5 de 25 nombres cortados: `1 in. 1/2 in. x 1 in. 1/4 in. Reducing Washer` necesita 292px con 210px disponibles. Los 25 thumbnails miden 40x40 (< 44) y los dos botones de toolbar 40px de alto.

**Por qué importa.** Caso de campo de PRODUCT.md: supervisor frente a estante con 674 productos. Tres de cinco filas no ayudan a encontrar producto, y `Bulk Excel` (sobrescribe precios de catálogo) está a un toque siendo el target más pequeño de la fila. Los nombres son `<medidas> + <tipo>`: un ellipsis de una línea destruye la mitad de la identidad sistemáticamente.

**Fix.** Búsqueda primero y a todo el ancho; plegar `674/670/4` en la línea del paginador; colapsar page-size + Bulk Excel + Refresh en un "More". Nombre con clamp de dos líneas (`-webkit-line-clamp: 2`): la fila tiene espacio vertical. Thumbnails y botones de toolbar a 44px. Objetivo: primera fila arriba de 300px.

**Comando:** `/impeccable adapt`

### [P1] 2.03 MB de imágenes a resolución completa para thumbnails de 40x40

**Qué.** 25 peticiones, 2,126,812 B codificados; 1,666,892 B (1.59 MB) de `/media/products/`. 22 de 23 imágenes a más de 4x su tamaño renderizado: `ROUGH-HB_full.jpg` 1610x1610 (430 KB), `S3-52-W_full.jpg` 1024x863 (481 KB), pintadas en 40x40. Logo del tenant 1299x328 (229 KB) a 166x42. El endpoint de datos en cambio: 269 ms y 1,462 B gzipped.

**Por qué importa.** La carga es 3.55 MB, ~60% miniaturas mal dimensionadas. Para campo con datos móviles, 2 MB por visita al catálogo para ver cuadritos de 40px.

**Fix.** Derivado `thumb` (80x80 o 120x120 retina) desde el backend en el campo de imagen del listado y `loading="lazy"`. El contrato del API no cambia si el serializer agrega una URL de miniatura junto a la existente.

**Comando:** `/impeccable optimize`

### [P2] El set de columnas responde al modelo, no al operador

**Qué.** `Tracking` es `Qty` en 674/674; Status `Active` en 670/674; y `jr-col-num` nunca aplica, porque la única regla que hace match es `.jr-col-num[data-v-b48d0916]` y PrimeVue renderiza los `td`/`th` dentro de `JRDataTable`, sin el atributo de scope de la vista — computa `text-align: start` sin `tabular-nums`, mostrando `100.00`, `3.00`, `250.00`. A 1024px el contenedor esconde 269px de columnas tras `overflow-x: auto` (clientWidth 942 vs scrollWidth 1211).

**Por qué importa.** ~211px de 1360px en dos columnas que nunca varían, mientras la única columna comparable queda a la izquierda con decimales muertos, imposible de escanear como magnitud. En tablet las columnas desaparecen sin indicación.

**Fix.** (a) `.jr-product-list__table :deep(th.jr-col-num), :deep(td.jr-col-num) { text-align: right; font-variant-numeric: tabular-nums }` — el patrón `:deep()` que el archivo ya usa bien para `jr-col-actions` doce líneas abajo — y Reorder como entero. (b) Sacar `Tracking` y mostrar `Serial` como badge junto al nombre solo en la excepción. (c) Status como filtro Active/Inactive/All y gastar los ~210px en precio unitario o existencia.

**Comando:** `/impeccable layout`

## Persona Red Flags

**Alex (power user, teclado).** Sin atajo para enfocar Search products. 143 elementos enfocables, ~130 tabulaciones entre toolbar y paginador, y cada fila mete el botón de foto antes del nombre (thumb → nombre → View → Edit → Delete x 25). 674 productos = 27 páginas con 5 links y sin campo de salto: la 18 son 17 clics. Sin multi-selección ni lote; el único camino masivo es la hoja de cálculo. +300ms artificiales por búsqueda/orden/página (`ProductListView.vue:539-542`).

**Sam (a11y).** El foco pasa, pero: el botón `View` de fila falla AA (`#16a34a` sobre blanco a 0.875rem = 3.3:1 contra 4.5; 3.2:1 en filas rayadas), mientras Edit 5.2:1 y Delete 4.8:1 pasan — y hay conflicto de contrato, porque `LIST_VIEWS §4` manda ese `#16a34a` explícitamente, así que contrato y línea base de contraste de PRODUCT.md se contradicen (necesita decisión, no fix silencioso). El `<label for="per-page-select">` apunta a un `<span class="p-select-label">`, no etiquetable: el control de paginación no tiene etiqueta programática. En el menú overflow el foco cae en el `ul role="menu"` con outline alrededor de toda la lista, no del ítem activo, con ítems de 37px contra 44 del contrato.

**Marisol — supervisora de almacén/campo en teléfono** (derivada de PRODUCT.md). 464 de 844px son chrome; ve cuatro productos. Busca "reducing washer" y la fila muestra `…1/4 in. R…`: las palabras que escribió son las cortadas. 6 de 25 filas muestran cuadro gris vacío que igual es botón; tocarlo cuesta un diálogo "No photos for this brand". La línea bajo el nombre lee `WP5100C4234·Test Interfaz produc`, sin espacio en el separador. Reorder y Unit son solo de escritorio. La búsqueda no tiene `autocapitalize="none"` ni `spellcheck="false"`: el teclado capitaliza y autocorrige números de parte.

## Minor Observations

- El diálogo muestra dos marcas con badge "Default": en 215GFI Breaker renderiza SIEMENS [Default] / SQUARE D [Default] / ABB / LEVITON. "Marca por defecto de compra" es singular y decide a dónde va una orden; la duda se transfiere al `+2` de la columna Brand. Badgear máximo una y `Message` info cuando el payload traiga más (`ProductBrandImages.vue:42-46`).
- El WebSocket a `/ws` falla en bucle: 6 errores al cargar, 51 al final de la sesión (`Invalid frame header`).
- `/api/user_detail/` se pide 6 veces en una sola carga (45–134 ms cada una).
- El drawer de Excel presenta el paso 2 antes del paso 1: `Choose .xlsx` primario azul arriba de `Download Excel template` en outline apagado. La confirmación no dice cuántas filas cambiarán; falta pre-conteo.
- El diálogo de resultado del bulk está en el sistema viejo (`text-start small mb-1` de Bootstrap dentro de SweetAlert), en el momento de mayor riesgo.
- `:fluid="isMobile"` en `+ New Product` es no-op: la clase se aplica pero ninguna regla define `width: 100%`; renderiza 125px donde LIST_VIEWS §3 espera ancho completo.
- Headers de tabla 15px vs celdas 14px: la vista fija el `font-size` del `td` pero no del `th`.
- Sombra del drawer fuera de token (`shadow-xl` de Tailwind en vez de `--shadow-jr-overlay`, que existe y el diálogo usa bien); su botón de cerrar mide 36x36 en drawer de pantalla completa.
- `0 Active` sigue verde cuando la búsqueda no devuelve nada. El estado vacío no repite la búsqueda y el slot de acciones de `JREmptyState` está sin usar: ni error ni sin-resultados ofrecen Refresh o Clear.
- `JREmptyState` renderiza su título como `<p>`: "No products" no es alcanzable por navegación de encabezados (el contenedor es `role="status"`, así que se anuncia).
- Ya corregido: cero clases Bootstrap dentro de `.jr-pilot`; badges rectangulares con receta pastel+800 (`#166534` sobre `#DEF2E6` = 6.1:1); `border-radius: 0` en diálogo, header y content; sin scroll horizontal a 1440px; acciones de fila a 40px.

## Questions to Consider

1. Si `Tracking` dice "Qty" 674 de 674 veces, ¿para qué es? ¿Columna, o badge solo en los serializados — y si el catálogo tiene cero, la funcionalidad está en la pantalla equivocada?
2. ¿Por qué esta pantalla puede sobrescribir todos los precios del catálogo pero nunca muestra uno? ¿Qué está mal: la ubicación de la herramienta o el set de columnas?
3. Si el CSS del design system pierde contra Bootstrap en cada selector de elemento, ¿cómo se enteraría alguien? El título lleva 40px en la pantalla insignia del pilot y nada lo detectó. ¿Qué más está en `@layer components` escrito, documentado y sin renderizar?
4. ¿Qué hace una supervisora con cuatro filas visibles? Si la respuesta es "busca", ¿por qué la búsqueda es la tercera cosa que alcanza?
