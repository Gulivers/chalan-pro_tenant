---
target: app/vuefrontend/src/components/inventory/ProductForm.vue
total_score: 20
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 2
timestamp: 2026-09-06T11-48-03Z
slug: efrontend-src-components-inventory-productform-vue
---
# Critique — Product Form Pilot (`ProductForm.vue`)

**Target:** `app/vuefrontend/src/components/inventory/ProductForm.vue`  
**Mode:** Operate — Construction Operations / ERP, mobile-first, data-dense  
**Contract:** DESIGN.md → Target State (Pilot). Direction approved; this review does not replace it.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Save shows Saving… + toast. Load has no skeleton/aria-busy. View vs Edit lives only in the h1. Row delete is silent until Save. |
| 2 | Match System / Real World | 2 | SKU / Unit / Reorder speak the trade. QUANTITY / SERIALIZED / SerializedItem and “price policy” tooltips are platform jargon. |
| 3 | User Control and Freedom | 2 | Header Back and footer Cancel are the same exit. No dirty-state warning. Price-row delete is immediate. |
| 4 | Consistency and Standards | 2 | Page chrome is JR. Price matrix is custom HTML, not JRDataTable. Catalog add/edit opens Bootstrap modals. Price errors use SweetAlert2. |
| 5 | Error Prevention | 2 | Required + uniqueness on rows. No confirm on row delete or discard. No From ≤ Until guard. |
| 6 | Recognition Rather Than Recall | 2 | Labels are visible. Default Brand = first ID (must remember). Default-sale-price rule lives in a hover tooltip. |
| 7 | Flexibility and Efficiency | 2 | Select filter + inline add help power users. No Save shortcut, no focus-first-error, no field “SKU + one price” path. |
| 8 | Aesthetic and Minimalist Design | 2 | Clean JR chrome. Noise: hint-before-control on almost every field, 10-column matrix, filled Delete per row. |
| 9 | Error Recovery | 2 | Identity errors inline. Price errors in Swal. Unmapped 400 as JSON/pre. No scroll/focus to first error. Work is preserved. |
| 10 | Help and Documentation | 2 | Many hints + v-tt, little task help. SERIALIZED banner is the only situational help that earns its space. |
| **Total** | | **20/40** | **Acceptable** |

## Design Specificity Verdict

**Start here.** Authored JR chrome; category-interchangeable mid-form.

**LLM assessment:** The page shell is JobRhythm Construction Ops: `JRPage` / `.jr-pilot`, left title at `1.3125rem` / 600, labels `0.8125rem` / 600, page `#f3f4f6`, 1px `#e5e7eb`, control `0.5rem` / panel `0.75rem`, one action blue, no outer `.card`. Domain vocabulary (SKU, Model #, Default Unit, Reorder, Purchase/Sale, Quantity vs Serialized) is trade-specific. The Identity + Classification block and the 10-column price grid could still serve a generic ERP SKU unchanged. Enum copy (`QUANTITY (Inventory item)`, `SERIALIZED (Equipment/Tool)`, `SerializedItem`) is system voice, not crew voice.

**Deterministic scan:** `detect.mjs --json` on ProductForm.vue, ProductPriceUnitTable.vue, Category/Brand/Unit/PriceType modals, and consumed JR primitives (JRPage, JRPageHeader, JRSection, JRField, JRButton, JRInput, JRSelect, JRSelectAddon, JRCheckbox) exited **0** with **0 findings**. Vue files go through text/regex detection. That is “no static anti-pattern string matches,” not a pass on live layout, Bootstrap islands, or error UX. No false positives. No `ignore.md`.

**Visual overlays:** No reliable user-visible overlay. Chrome DevTools MCP failed (`Missing X server`; `DISPLAY` unset). Mutation preflight never ran. live-server was not started. Fallback: **mutation unavailable**. SPA root on `:8082` returns 200; `/products/form` on that host returned Express 404 (client-route / refresh). `:8080` refused connections. Login and live interaction states were not reached.

## Overall Impression

The pilot bones of the form are correct: left title, JR sections, sticky Save on the phone, and a purpose-built mobile price sheet instead of a crushed 10-column grid. The single biggest opportunity is **object truth on save**: Identity occupies the first fold; the work that makes a SKU buyable/sellable is a 56rem spreadsheet (or a SweetAlert if it fails). Until the price matrix, error recovery, and catalog overlays live in the same JR system as the chrome, this reads as “JR form wrapper around an admin price grid.”

## What's Working

1. **Pilot chrome.** `JRPage` + `JRPageHeader` + `JRSection` + `JRField` + JR controls. No outer Bootstrap card, no 2rem centered title. Tokens and type match `jr-design-system.css`.
2. **Authored mobile strategy for prices.** Below 768px: compact rows + `JRDrawer` + `JREmptyState`. Sticky footer puts Save/Cancel in the thumb zone. That is the field/office split the brief asked for.
3. **Mode + identity validation.** Title tracks create/edit/view. View exposes Edit when permitted. Name/SKU/Model/Category/Brands/Unit get `fieldErrors` + invalid. SERIALIZED banner only when that mode is on.

## Priority Issues

### [P1] Price matrix is ten simultaneous decisions from 768px up
- **Why it matters:** Desktop/tablet table is `min-width: 56rem` with 10 columns (type, unit, purchase, sale, price, default, from, until, active, actions). The list pilot already authored a tablet short-table; the form jumps from phone sheet to full spreadsheet. Identity sits in a 48rem measure; prices overflow. Field and office staff lose Price / Default / Active off-screen.
- **Fix:** Three densities without changing APIs: keep the phone sheet; tablet = type · unit · price · flags · overflow; desktop = office columns. Row delete as text/ghost, not filled danger. `+ Add Row` can live in `JRSection` `#actions`.
- **Suggested command:** `/impeccable adapt`

### [P1] Error recovery is split and mute
- **Why it matters:** Identity fails under the field with no scroll/focus. Price rows fail in SweetAlert HTML. Unmapped 400 becomes `<pre>` JSON or Django DEBUG copy. Operators hit Save and see nothing, or leave the JR world.
- **Fix:** Banner/toast “N fields need attention” + focus first `JRField` error; inline row errors on the table/sheet; keep work. Reserve Swal for non-field failures only if JR Message/dialog is not ready.
- **Suggested command:** `/impeccable harden`

### [P2] Hint wall + two help channels + duplicate exits
- **Why it matters:** `JRField` paints `hint` above the control. SKU, Model, Category, Brands, Unit, Reorder, Tracking all speak at once; `v-tt` duplicates on hover (useless on a phone). Header Back and footer Cancel are the same `cancelForm`. Header has no mode description.
- **Fix:** Keep hints only where they prevent tickets (tracking, default brand, default sale price, SKU uniqueness). Hint below the control. One exit. One-line `JRPageHeader` description.
- **Suggested command:** `/impeccable distill`

### [P2] Bootstrap / SweetAlert islands inside the pilot
- **Why it matters:** `JRSelectAddon` +/pencil open Category/Brand/Unit/PriceType Bootstrap modals. Invalid prices and some 400s open SweetAlert2. Default price is a raw radio. DESIGN.md and LIST_VIEWS say do not mix Bootstrap chrome inside `.jr-pilot`.
- **Fix:** Reuse the existing `JRDrawer` pattern (already used for the mobile price sheet) for catalog add/edit in this flow; JR-surface errors; JR default-price control. Same endpoints and permissions.
- **Suggested command:** `/impeccable layout`

### [P2] Price-row actions and badges fight the list contract
- **Why it matters:** Filled danger Delete next to the mobile row tap-target. Purchase/Sale badges default to muted secondary. Radio is 16px. Desktop does not use `JRRowActions`. Status semantics are weaker than Active/Serial on the list.
- **Fix:** Purchase/Sale as distinct JRBadge severities; Default stays info; Delete ghost/text; radio ≥ 44px or a JR control.
- **Suggested command:** `/impeccable colorize`

## Persona Red Flags

**Alex (Power User):** No Save accelerator. Tab order walks hints + three addons + ten cells. Filled row-delete is a costly misclick with no undo. Inline Category/Brand/Unit add is the only accelerator and it opens a Bootstrap modal. Save → view forces another Edit if a price was missed.

**Sam (Accessibility-Dependent):** Required asterisk is `aria-hidden`. `JRInput` does not wire `aria-describedby` to hint/error. `v-tt` is hover-only. Swal and `.modal.fade` leave `.jr-pilot`. Radio is 1rem. Focus-visible 2px primary exists in the design system.

**Casey (Distracted Mobile / Field):** Sticky Save is correct. Edit/Back sit at the top. At 768px the 56rem table returns. Phone Delete competes with the row sheet. Hints eat the first viewport. No draft if the SPA is recycled.

**FieldOps (office + field at a residential trade contractor):** They need a breaker/cable/tool SKU buyable before a purchase. Model # is the most trade-native hint. No photo on this form (gallery lives elsewhere). Quantity vs Serialized is the real field decision and is labeled as an enum. Contractor/Wholesale/Counter pricing is the office job and is buried in the spreadsheet. A crew lead can add a price row and then hit a Bootstrap Category modal or “Row 1: Unit is required” Swal.

## Cognitive Load

Failed 7 of 8 checklist items → **high cognitive load**.

| Item | Verdict |
|---|---|
| Single focus | Fail — identity + classification + inventory + 10-col matrix + header/footer exits |
| Chunking | Fail — price row = 10 controls |
| Grouping | Pass — JRSection Identity / Classification / Inventory / Price |
| Visual hierarchy | Fail — every field has 600 label + hint + tooltip; only sticky Save is clearly primary |
| One thing at a time | Fail — desktop asks type, unit, flags, amount, default, dates, active together |
| Minimal choices | Fail — 10-column row; each JRSelectAddon is select + filter + Add + Edit |
| Working memory | Fail — implicit default brand; default-price rule in tooltip; mode only in title |
| Progressive disclosure | Fail — phone sheet yes; desktop and hints no. SERIALIZED banner yes |

Decision points with >4 visible options: desktop price row (10); each JRSelectAddon cluster; mobile row (edit + delete + badges).

## Emotional Journey

Arrival is operational: Create/Edit/View Product, left title, dense. The valley is Classification (three addons + “Required…” hints) then the price matrix (56rem scroll or phone Delete). High-stakes Save either stays silent on identity errors or opens a pre-pilot Swal. Success toast + view mode is a calm end, but the header never restates SKU/name as “ready to buy/sell.” Peak-end is the valley, not the save.

## Minor Observations

- `JRPageHeader` `description` unused.
- Product `Active` checkbox sits in a `JRField` with no label.
- Brand/Category/Unit disable can share `add_productcategory` visually.
- Create auto-inserts an empty price row — desktop empty state rarely appears.
- Product-level Active vs row-level Active/Purchase/Sale overlap conceptually.
- Sheet drawer `Done` looks like submit; it only closes the sheet.
- `ProductImageGallery` is not mounted on this screen.
- App shell remains Bootstrap (in scope to note, out of scope to restyle).
- `novalidate` on the form is correct if JR owns errors.

## Questions to Consider

- If the job is “make this SKU buyable/sellable,” why does Identity own the first fold and pricing sit in a 10-column appendix?
- What if the header were one operational line (`SKU · Name · Active`) and there were not two identical exits?
- Does every field need a hint, or only the ones that generate tickets?
- Why can a supervisor create a Category here but not see the product photo on this same view?
- What does “create in the truck cab” look like: name, SKU, unit, one purchase price — and the rest under More pricing?
