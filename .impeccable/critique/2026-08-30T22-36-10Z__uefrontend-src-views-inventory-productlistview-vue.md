---
target: app/vuefrontend/src/views/inventory/ProductListView.vue
total_score: 24
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
timestamp: 2026-08-30T22-36-10Z
slug: uefrontend-src-views-inventory-productlistview-vue
---
Method: dual-agent (A: 3d557117-49d2-464b-888e-8ec9e82a5613 · B: 4f2c5be4-8788-4b2c-b78f-3df4b277579d)

# Critique — Products List Pilot (`ProductListView.vue`)

**Target:** `app/vuefrontend/src/views/inventory/ProductListView.vue`  
**Live URL attempted:** `http://test-dominio-local.chalanpro.net:8082/products`  
**Mode:** Operate — Construction Operations / ERP, mobile-first, data-dense  
**Contract:** DESIGN.md → Target State (Pilot). Direction approved; this review does not replace it.

---

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Loading is a paragraph (“Loading products…”) plus a forced 300ms delay; no skeleton. Error copy says “Try Refresh.” with no control on the empty surface. |
| 2 | Match System / Real World | 3 | SKU / Category / Reorder / Serial vs Qty speak the trade; leading `Id` and “Bulk Excel” are office-system leftovers. |
| 3 | User Control and Freedom | 3 | Search is native `type="search"`; Bulk panel toggles off; delete confirms. Empty-search has no one-click clear. |
| 4 | Consistency and Standards | 2 | JR primitives mixed with raw PrimeVue `Tag` / `ToggleButton` / mobile `Paginator`, plus a Bootstrap bulk panel inside `.jr-pilot`. |
| 5 | Error Prevention | 3 | Delete confirm + bulk tooltip warning. The overwrite tool is a faded `ToggleButton` (`opacity: 0.85`), not a guarded disclosure. |
| 6 | Recognition Rather Than Recall | 2 | Per-page options are bare “10/25/50/100”; stats chips look like filters but are not; the product name looks like View. |
| 7 | Flexibility and Efficiency | 2 | Sort + debounce search exist. No shortcuts, no bulk row select, no click-to-filter Active; name click does not open the record. |
| 8 | Aesthetic and Minimalist Design | 3 | Pilot density, borders, and title are right. Duplicate SKU, 10 columns, 18rem search, and action-blue on every name add noise. |
| 9 | Error Recovery | 2 | Empty/error copy names the problem; neither surface exposes Refresh, New Product, or clear-search. |
| 10 | Help and Documentation | 2 | Tooltips on gallery + Bulk Excel; no `JRPageHeader` description; Tracking Serial/Qty unexplained. |
| **Total** | | **24/40** | **Acceptable** |

---

## Design Specificity Verdict

**Start here.** The list is authored for JobRhythm construction ops — not a marketing restyle and not a generic AI dashboard — but the authorship is incomplete. The work surface leaks generic PrimeVue/Bootstrap in the chrome.

**LLM assessment:** `JRPage` / `.jr-pilot` does the hard contract work: left `h1` at `1.3125rem` / 600, Inter, page `#f3f4f6`, white table, 1px `#e5e7eb` borders, control radius `0.5rem`, panel radius `0.75rem`. Desktop is a dense sortable catalog (SKU, Category, Tracking Serial/Qty, Brand, Reorder, Unit, Status). Mobile is a purpose-built scan list, not a crushed 10-column table. `JRRowActions` follows the contract: labeled View/Edit/Delete on desktop, overflow on mobile.

What keeps it category-interchangeable: a custom `jr-product-list__masthead` + `jr-product-list__toolbar` instead of `JRPageHeader` actions + `JRToolbar`; PrimeVue `Tag` / `ToggleButton` instead of `JRBadge` / `JRButton`; `ProductPricesBulkExcelPanel` as a Bootstrap 5 island (`form-control`, `btn-outline-success`, `rounded-3`) inside the pilot; and every product **name** painted action-blue as if it were the record, while it opens the **image gallery**. An HVAC wholesaler admin could reuse this toolbar/table chrome unchanged. The mobile row and the Serial/Qty + Reorder vocabulary are the parts that actually belong to a residential trade contractor.

**Deterministic scan:** `detect.mjs --json` on `ProductListView.vue` and the consumed primitives (`JRPage`, `JRPageHeader`, `JRToolbar`, `JRDataTable`, `JRRowActions`, `JREmptyState`) exited **0** with **0 findings**. Vue files go through `detectText` (regex), not computed-style HTML detection. That is “no static anti-pattern string matches,” not a pass on live layout. The detector did not catch the structural issues (name→gallery, unused `JRToolbar`/`JRBadge`, 18rem search, Bootstrap bulk island) because those are composition and behavior, not the patterns the text engine flags. No false positives to drop. No `ignore.md` applied.

**Visual overlays:** No reliable user-visible overlay is available. Chrome DevTools MCP could not start a headful browser (`Missing X server`; `DISPLAY` unset). Mutation preflight never ran. Live-server was not started. Fallback signal: **mutation unavailable**. Assessment A also probed `http://test-dominio-local.chalanpro.net:8082/products` over HTTP and received Express `Cannot GET /products` (404); the SPA root on `:8082` returns 200. Deep-link/refresh of `/products` on that host is broken at the server; client-side nav from `/` would still work. Login and live interaction states were not reached.

---

## Overall Impression

The pilot bones are correct. This already looks like a Construction Ops work surface: left title, tight density, 1px borders, field-vs-office split. The single biggest opportunity is **object truth**: the strongest thing on every row (the blue name) is not the product record. Until that click and the toolbar composition match the JR contract, the screen will keep reading as “PrimeVue table with a JobRhythm skin” rather than the flagship of the new system.

---

## What's Working

1. **Pilot contract bones.** `JRPage` full-width work surface (no outer `.card` / `.card-modern`), left `JRPageHeader` title at canonical type, neutrals + `#2563eb`, 1px borders, `0.5rem` / `0.75rem` radii, table cell padding `0.3rem`, Inter. This is Construction Ops, not a SaaS marketing restyle of Bootstrap.

2. **Responsive strategy is authored, not wrapped.** `isMobile` at `767.98px` switches to a scan list (thumb, name, SKU · category, Status, compact `JRRowActions`) and a simpler `Paginator`. Desktop keeps `JRDataTable` + text actions. That is the field-and-office split the brief asked for.

3. **Row-action contract + delete gravity.** Desktop `JRRowActions` are labeled text buttons with entity `aria-label`s (`View {name}`); mobile is a 44px overflow with “More actions for {name}”. Delete is confirmed, not a naked trash icon.

---

## Priority Issues

### [P1] Product name is styled as the record and opens the gallery
- **Why it matters:** `jr-product-cell__name` is `#2563eb` / 600, underline on hover — the strongest object on the row. Click calls `openImageGallery`. `JRRowActions` “View” is the actual record. Field and office staff will mis-click all day. The `aria-label` (“View images of {name}”) is honest and still unexpected.
- **Fix:** Keep gallery access. Make the name (or the whole row primary target) go to View. Put images on a thumbnail-only hit target or a “Photos” action. Stop painting every name with the action blue.
- **Suggested command:** `/impeccable clarify`

### [P1] Toolbar/status chrome bypasses JR primitives; Bulk Excel is a Bootstrap island
- **Why it matters:** DESIGN.md says consume `JRToolbar`, `JRBadge`, `JRButton`; no one-off PrimeVue in features. The list builds `jr-product-list__toolbar` + PrimeVue `Tag` (stats, Tracking, Status) + `ToggleButton` “Bulk Excel”. `ProductPricesBulkExcelPanel` is incumbent Bootstrap chrome inside `.jr-pilot`.
- **Fix:** `JRPageHeader` `#actions` for New Product; `JRToolbar` for search/stats/actions; `JRBadge` for Total/Active/Inactive/Status/Tracking; `JRButton` ghost for bulk disclosure. Restyle the bulk panel with JR controls or isolate it as a `JRDrawer`. Preserve bulk Excel behavior and permissions.
- **Suggested command:** `/impeccable layout`

### [P1] Search is demoted; the table steals the viewport
- **Why it matters:** Desktop `.jr-product-list__search` is `flex: 0 1 18rem; max-width: 18rem`. The table is `min-width: 56rem` with a 16.5rem Actions column. From 768px up, operators get a horizontally scrolling 10-column grid. Search is the primary find tool for a long catalog and reads as a side widget. SKU is repeated under the name and as its own column.
- **Fix:** Let search grow (`flex: 1 1 20rem`, ~28–36rem). Drop or tuck `Id` and the duplicate SKU column. Keep Actions sticky or overflow earlier. Do not give tablets the 10-column desktop table without a mid breakpoint.
- **Suggested command:** `/impeccable adapt`

### [P2] Empty / error / loading do not finish the task
- **Why it matters:** `JREmptyState` is copy-only. Error says “Try Refresh.”; Refresh lives back in the toolbar. Loading is text + `setTimeout(300)`. Operate needs skeletons and a recovery control on the empty surface.
- **Fix:** Error empty: primary Refresh. Search-empty: clear search. Zero catalog: New Product if permitted. Skeleton rows; drop the fake 300ms delay.
- **Suggested command:** `/impeccable harden`

### [P2] Stats and page-size look like decisions they are not
- **Why it matters:** `Tag` chips “N Total / Active / Inactive” sit under the title with filter affordance and do nothing. `JRSelect` options are `"10"`…`"100"` with a visually-hidden “Entries per page”. Mobile `.jr-product-list__cluster` is `flex-wrap: nowrap` (4.75rem select + Bulk Excel + Refresh) — overflow risk at 390px. Bulk Excel on a phone is a high-stakes office tool in the primary cluster.
- **Fix:** Make chips toggle `is_active` (and show selected/clear) **or** restyle them as non-interactive summary. Label the select “25 / page”. Allow the cluster to wrap; move Bulk Excel out of the primary mobile row.
- **Suggested command:** `/impeccable distill`

---

## Persona Red Flags

**Alex (Power User):** No keyboard accelerators for search-focus, View, or next page. Cannot click Active to filter. Cannot multi-select / batch-delete. Name click is the wrong accelerator. 300ms load tax on every refresh/search. Horizontal scroll on a 56rem table. Bulk Excel is the only batch path and it is hidden behind a toggle that looks disabled.

**Sam (Accessibility-Dependent):** Search and per-page have visually-hidden labels (good). Name control announces “View images of {name}” — honest, unexpected. Status is text+color (good). Image placeholder is `aria-hidden` empty. `aria-live` on stats and “Updating…” helps. Focus rings were not verified live. Raw `ToggleButton` / `Tag` / portaled `Menu` are the SR risk. Desktop `JRRowActions` at `min-height: 2.25rem` (36px) is tight for motor impairment.

**Casey (Distracted Mobile / Field):** `+ New Product` is full-width at the **top** (not thumb zone). Search is full-width on small screens (good). Cluster `nowrap` can shove Bulk Excel / Refresh off-screen. Overflow menu is correct. Name tap opens photos, not the product — expensive mis-tap. Mobile list hides Unit, Reorder, Tracking, Brand. Bulk Excel on a phone is a high-stakes control in the primary cluster.

**FieldOps (office + field staff at a residential trade contractor):** They need find-by SKU/name, Active, category, unit, maybe a photo to confirm the part. The desktop grid leads with **Id** and repeats SKU. Reorder — useful in the office — vanishes on mobile. “Bulk Excel” is an office-admin weapon on a field screen. Gallery-on-name *would* help a crew lead confirm a fixture **if** it were a thumbnail, not the title. The page has no `JRPageHeader` description.

---

## Cognitive Load

Failed 4 of 8 checklist items → **high cognitive load**.

| Item | Verdict |
|---|---|
| Single focus | Fail — stats chips, Bulk Excel, gallery-on-name, and 10 columns compete with find → open |
| Chunking | Fail — desktop table is 10 columns |
| Grouping | Pass — masthead / toolbar / table (or mobile rows) are separated |
| Visual hierarchy | Fail — `+ New Product` is correctly primary; search is demoted to 18rem; every name is `#2563eb` |
| One thing at a time | Pass — search → scan → act; bulk is a disclosure |
| Minimal choices | Fail — toolbar is 5 chrome controls; 8 sortable headers |
| Working memory | Pass — search/query stay on-screen |
| Progressive disclosure | Pass — mobile overflow; bulk panel; mobile list vs desktop table |

Decision points with >4 visible options: desktop toolbar (Search + per-page + Bulk Excel + Refresh + New Product = 5); sortable headers (8).

---

## Emotional Journey

Arrival is operational, not decorative — title + `+ New Product` is a competent start. The peak is typing in “Search products…” and scanning a dense table, or a mobile row of name / SKU · category / Active. The valley is clicking the blue name expecting the record and getting `ProductImageGallery`. Zero results and load failure are another valley: copy without a control. Delete confirm is the right high-stakes reassurance. Bulk Excel can overwrite prices/units; that warning lives in a tooltip on a faded toggle, then a Bootstrap essay. The session end (`{first}–{last} of {totalRecords}`) is a clean close.

---

## Minor Observations

- SKU appears under the name **and** in a SKU column.
- `JRPageHeader` `#actions` unused; create lives in a one-off masthead. Header `margin-bottom` is overridden to `0.25rem`.
- Search magnifier is a hand-drawn SVG; Refresh uses `@primevue/icons/refresh`. Two icon dialects.
- `+ New Product` uses a typed plus, not the icon system.
- No page description.
- Desktop pager includes First/Last; mobile is Prev / report / Next — correct.
- Tracking Serial/info vs Qty/secondary is good operational encoding — should be `JRBadge`.
- Numeric Reorder uses `jr-col-num` + tabular-nums — keep.
- Loading opacity `0.55` on the mobile list (`aria-busy`) is unused on desktop (table `loading` prop only).
- App shell still `text-align: center` + Avenir on `.app-container` (JRPage counters this; Navbar/Footer correctly stay incumbent).
- PWA `themeColor` in `vue.config.js` is still Bootstrap `#0d6efd`, not `#2563eb` (out of this screen’s scope).

---

## Questions to Consider

- If the product **name** is the thing operators hunt, why is it a photo viewer?
- Why do “12 Active” / “3 Inactive” exist if they cannot filter the list?
- Is Bulk Excel a peer of Search, or a dangerous office tool that belongs in a drawer?
- Does a crew lead on a 390px phone need Id, Brand +N, and Tracking — or name, SKU, status, unit?
- If `JRToolbar` and `JRBadge` were designed for this pilot, why does the flagship list reinvent both?
