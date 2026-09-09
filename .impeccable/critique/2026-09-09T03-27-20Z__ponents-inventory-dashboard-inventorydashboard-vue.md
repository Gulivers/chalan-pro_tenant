---
target: InventoryDashboard.vue + integrated components
total_score: 19
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 4
timestamp: 2026-09-09T03-27-20Z
slug: ponents-inventory-dashboard-inventorydashboard-vue
---
Method: dual-agent (A: 713c1f63-d462-4e07-ac07-c2d1d8ef46ef · B: dbe63dd8-d8bd-47ed-b26b-fea500d9a9b2)

# Critique — InventoryDashboard.vue (+ componentes integrados)

Modo **Operate**. Inspeccionado en vivo en `http://test-dominio-local.chalanpro.net:8082/inventory-dashboard` a ~1440×900 y ~390×844. Árbol: `InventoryDashboard.vue` + `components/` (métricas, stock, sales, customers/suppliers, reports, charts, exports).

## Design Health Score

| # | Heurística | Score | Hallazgo clave |
|---|-----------|-------|----------------|
| 1 | Visibilidad del estado | 2 | Loading/empties sí; métricas arrancan en 0; Growth −100% con ventas vacías; exports vía `alert()` |
| 2 | Correspondencia con el mundo real | 2 | UI EN + botones ES (“Transacciones / Editar”); poco framing de trade/warehouse JobRhythm |
| 3 | Control y libertad | 3 | Period, Clear filters, tabs, Refresh; sin undo de export |
| 4 | Consistencia y estándares | 2 | EN/ES; Low Stock = badge info azul; saltos h2→h6; “Top 2” vs chart “Top 10” |
| 5 | Prevención de errores | 2 | Stock negativo como Low Stock; Transacciones sin producto en la ruta |
| 6 | Reconocer antes que recordar | 3 | Labels visibles; 13 Excel idénticos obligan a leer secciones |
| 7 | Flexibilidad y eficiencia | 1 | Sin atajos, sin bulk, deep-link débil desde low-stock |
| 8 | Estético y minimalista | 1 | ~6.3 pantallas desktop / ~10 móvil; nested panels; muro de exports |
| 9 | Recuperación de errores | 2 | Empties OK; export errors vía `alert`; “Show Empty Table” ruido |
| 10 | Ayuda y documentación | 1 | Banner de permiso con codename `appinventory.view_product` |
| **Total** | | **19/40** | **Poor** |

## Design Specificity Verdict

**Shell JR a medias, cuerpo BI genérico.**

**LLM:** `JRPage` / `JRPageHeader` / `JRSection`, Inter, tokens `--color-jr-*` y métricas rectangulares sí son Pilot. El cuerpo es KPI → tablas → Chart.js → pared de “Download Excel” → filtros de movimientos: intercambiable con cualquier ERP de almacén. Nested `.jr-dash-panel` dentro de `JRSection` contradice Target State (“No nested cards”).

**Deterministic scan (CLI):** `detect.mjs --json` sobre `app/vuefrontend/src/components/inventory/dashboard` → exit 0, `[]` findings, no DEGRADED. Limpio no prueba adherencia a tokens.

**Overlays (inyección OK, puerto 8400, detenido):** cramped-padding en `.jr-dash-table-wrap`; skipped-heading h2→h6 “Top 2 Customers”; flat-type-hierarchy / overused-font a nivel BODY. False positives claros: low-contrast del footer shell (`footer-flow-title`), dark-glow “on dark page” en página clara, bounce-easing/layout-transition globales.

## Overall Impression

El shell migró; la tarea del operador no. El mayor problema no es el Chart.js: es que la pantalla vende **exports y densidad** antes que **triage de stock / acción del día**. Stock −95 con badge azul “Low Stock” y Growth −100% sin ventas son mentiras de estado que destruyen confianza.

## What's Working

1. Shell Pilot real: título ~21px, métricas con tokens JR y radio 0.
2. Permission banner y empties (`JREmptyState`) en stock/sales/movements.
3. Tablas con sticky header y scroll horizontal en móvil — usables, no solo decorativas.

## Priority Issues

### [P1] Stock crítico mal representado
**Qué.** Filas con stock negativo (−95) y badge “Low Stock” `info` azul; `getStatusText` trata solo `=== 0` como Out of Stock (`LowStockTable.vue`).
**Por qué.** El riesgo real no destaca; semántica de status rota.
**Fix.** Severities danger/warning; copy Negative / Below zero; highlight arriba.
**Comando:** `/impeccable clarify` (+ harden estados)

### [P1] Muro de 13× “Download Excel”
**Qué.** Stock / Sales / Customers repiten 4 exports cada uno + movements; ~6–10 pantallas de scroll.
**Por qué.** Decision fatigue; diluye “qué reordenar hoy”.
**Fix.** Zona Exports colapsada o menú; una CTA primaria por sección; progressive disclosure.
**Comando:** `/impeccable distill`

### [P1] Growth −100% con ventas vacías
**Qué.** Empty “No sales data” + Growth danger −100% (`SalesMetricsCards`).
**Por qué.** Falsa urgencia; números no fiables.
**Fix.** Sin ventas del periodo: ocultar o neutralizar Growth.
**Comando:** `/impeccable harden`

### [P1] Acción primaria de low-stock débil
**Qué.** “Transacciones” → `/transactions/form` sin producto (`LowStockTable.vue`); labels ES en UI EN.
**Por qué.** No completa el salto producto → movimientos.
**Fix.** Prefill/filtro por producto; copy EN consistente.
**Comando:** `/impeccable clarify`

### [P2] Nested cards + densidad móvil
**Qué.** `.jr-dash-panel` dentro de `JRSection`; ~10 pantallas a 390px; tablas clippean.
**Por qué.** Rompe Pilot; campo/oficina en teléfono es fricción.
**Fix.** Quitar nesting; stack/card-list low-stock en móvil; acortar above-the-fold.
**Comando:** `/impeccable layout` / `/impeccable adapt`

## Persona Red Flags

**Alex:** 13 Excel, Refresh repetido, sin atajos/bulk; Transacciones no aterriza en el SKU.
**Sam:** canvas sin nombre accesible; focus outline transparente en sitios; skipped headings; Low Stock azul como alerta; label-for ×3 en consola.
**Marisol (almacén/campo):** necesita “qué falta / qué almacén”; recibe BI EN + botones ES, stock negativo disfrazado y movements vacíos al final.

## Minor Observations

- “Show Empty Table” en empty de low-stock.
- Chart “Top 10” vs header “Top 2”.
- Advanced Reports con grid adicional `v-if="false"`.
- Overlay loading EN vs ES en exports.
- Permission Message solo en Stock, no en Sales.
- WS `/ws` Invalid frame header (shell).

## Questions to Consider

1. Si el job es “¿qué reponer antes del crew?”, ¿por qué el CTA repetido es Excel?
2. ¿Dashboard vs Reports deberían separarse?
3. ¿Growth sin ventas: ocultar o “No comparable period”?
4. ¿Charts aportan algo que la tabla no, con pocos customers y sales vacías?
5. ¿Lista densa (Products) o morning brief de una pantalla?
