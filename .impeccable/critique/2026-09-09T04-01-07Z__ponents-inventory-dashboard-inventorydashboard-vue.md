---
target: app/vuefrontend/src/components/inventory/dashboard/InventoryDashboard.vue
total_score: 26
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 0
timestamp: 2026-09-09T04-01-07Z
slug: ponents-inventory-dashboard-inventorydashboard-vue
---
# Critique — InventoryDashboard.vue (+ componentes integrados)

**Target:** `app/vuefrontend/src/components/inventory/dashboard/InventoryDashboard.vue`  
**Mode:** Operate — Construction Operations / ERP, mobile-first, data-dense  
**Contract:** DESIGN.md → Target State (Pilot). Direction approved; this review does not replace it.  
**Baseline:** 19/40 (Poor) — 2026-09-09

## Design Health Score

| # | Heurística | Score | Hallazgo clave |
|---|-----------|-------|----------------|
| 1 | Visibilidad del estado | 3 | Attention `aria-live`; Growth “No comparable period”; exports vía toast. |
| 2 | Correspondencia con el mundo real | 3 | On hand / Reorder / Critical; copy EN operacional. |
| 3 | Control y libertad | 3 | Drawer, disclosures, filtros movements. |
| 4 | Consistencia y estándares | 3 | JR pilot; badges danger/warn; Top N alineado; headings mejorados. |
| 5 | Prevención de errores | 3 | Stock negativo ≠ Low Stock; Growth sin falsa urgencia; Advanced decoy retirado. |
| 6 | Reconocer antes que recordar | 3 | Badges de triage; Excel fuera del muro principal. |
| 7 | Flexibilidad y eficiencia | 2 | View/Edit con producto; sin bulk ni atajos; sin deep-link a movimientos. |
| 8 | Estético y minimalista | 3 | Triage primero; nested panels eliminados; reports en drawer. |
| 9 | Recuperación de errores | 3 | Empties JR; export errors → toast (no `alert`). |
| 10 | Ayuda y documentación | 2 | Intro + ledes; sin “qué hacer ahora” para Critical; permiso sin codename. |
| **Total** | | **26/40** | **Acceptable** |

## Design Specificity Verdict

**Operational JobRhythm spine, still some admin-kit texture.** Attention / Needs attention / Critical semantics are product-specific. Metric tiles + Excel drawer still feel category-generic under JR chrome.

## Overall Impression

Pasó de **BI + Excel wall** a **centro operacional con triage primero**. Los P1 del baseline (stock, Growth, Excel muro, acciones ES sin producto) están cerrados. Quedan eficiencia de experto, CTAs de movimiento de stock y densidad secundaria en desktop.

## What's Working

1. AttentionSummary + lista/tabla Critical-first con −95 como Critical danger.
2. Reports & exports en `JRDrawer` (Stock / Sales / Customers / Movements).
3. Mobile: sales colapsado; lista escaneable; charts bajo disclosure.

## Priority Issues (post-fixación)

### [P2] Sin siguiente paso operacional desde Critical
View/Edit producto; falta Adjust/Receive/Transfer con permisos (posible backend gap para deep-link).

### [P2] Drawer Excel todavía homogéneo
Misma CTA “Download Excel” × N por categoría — mejor ranking/prioridad.

### [P2] Densidad secundaria desktop
Con ventas $0 el bloque Sales puede quedarse cerrado (implementado: open solo si total_sales > 0).

## Persona Red Flags

**Alex:** sin bulk. **Sam:** charts con aria; tabs de reports imperfectos. **Marisol:** triage claro; aún no “qué reponer ya” como CTA primario.

## Minor

- `AdditionalReportsGrid` / Advanced siguen sin cablear (ocultos; mismo estado que `v-if="false"` previo).
- Typo de datos “Electrical Componet”.
- Detector browser: contrast/shell globals; CLI detect limpio.

## Trend

**19/40 → 26/40** (+7). Banda Acceptable.
