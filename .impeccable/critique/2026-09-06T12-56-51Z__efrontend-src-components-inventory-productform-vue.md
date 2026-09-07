---
target: app/vuefrontend/src/components/inventory/ProductForm.vue
total_score: 24
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
timestamp: 2026-09-06T12-56-51Z
slug: efrontend-src-components-inventory-productform-vue
---
# Critique — Product Form Pilot (`ProductForm.vue`)

**Target:** `app/vuefrontend/src/components/inventory/ProductForm.vue`  
**Mode:** Operate — Construction Operations / ERP, mobile-first, data-dense  
**Contract:** DESIGN.md → Target State (Pilot). Direction approved; this review does not replace it.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Save shows Saving… and an attention banner. Product/list load still has no skeleton or aria-busy. |
| 2 | Match System / Real World | 3 | SKU / crew / Quantity vs Serialized speak the trade. Catalog Price Type guide still leaks ORM names. |
| 3 | User Control and Freedom | 2 | One list exit. No dirty-state warning. Price-row Delete is immediate. Catalog from the sheet stacks drawers. |
| 4 | Consistency and Standards | 2 | Page chrome is JR. Catalog overlay is JRDrawer wrapping Bootstrap DynamicForm. Unmapped 400 still uses SweetAlert2. |
| 5 | Error Prevention | 2 | Required + uniqueness + From ≤ Until. Incomplete price rows are dropped silently. Classification selects can be gated on the wrong permission. |
| 6 | Recognition Rather Than Recall | 3 | Default brand and default-sale rules are on-screen. Incomplete rows still vanish without a preview. |
| 7 | Flexibility and Efficiency | 2 | Select filter + inline catalog add. No Save shortcut, no duplicate-row, one row at a time. |
| 8 | Aesthetic and Minimalist Design | 3 | Hint wall gone; hints sit under controls; Delete is ghost. Desktop matrix is still ten columns. |
| 9 | Error Recovery | 3 | Banner + scroll/focus + inline row errors. Unmapped 400 remains JSON/pre in Swal. |
| 10 | Help and Documentation | 2 | SKU / brand / tracking / default-sale earn their space. The price model is still under-taught. |
| **Total** | | **24/40** | **Acceptable** |

## Design Specificity Verdict

**Start here.** Authored JR chrome and trade IA; catalog overlay still interchangeable / incumbent.

**LLM assessment:** Identity → Classification → Inventory → Price is a contractor SKU mental model. Header copy (“Create a SKU the crew can buy and sell”), Quantity vs Serialized, Purchase/Sale/Default, and the three price densities are JobRhythm Construction Ops. The page shell matches DESIGN.md Target State (Pilot): left title, tokens, no outer card. The catalog drawer chrome is JR; its body is still DynamicForm (`form-control`, `btn btn-primary`, Font Awesome). That body could serve any ERP unchanged.

**Deterministic scan:** `detect.mjs --json` on ProductForm.vue, ProductPriceUnitTable.vue, DynamicForm.vue, and consumed JR primitives exited **0** with **0 findings**. Vue files go through text/regex detection. That is “no static anti-pattern string matches,” not a pass on live layout or Bootstrap-inside-drawer. No false positives. No `ignore.md`.

**Visual overlays:** No reliable user-visible overlay. Chrome DevTools MCP failed (`Missing X server`; `DISPLAY` unset). Mutation preflight never ran. live-server was not started. Fallback: **mutation unavailable**.

## Overall Impression

The form is no longer a JR wrapper around a mute spreadsheet. Attention banner, first-error focus, row errors, one exit, distilled hints, tablet short-table, and ghost Delete land the last critique’s top actions. The single biggest remaining gap is **object truth at the money moment**: desktop still asks ten decisions per row; incomplete rows disappear on Save; add Category/Brand/Unit/Price Type still drops the operator into a Bootstrap schema form.

## What's Working

1. **Pilot chrome + distilled first fold.** Left title, one-line description, Identity without a hint wall, SKU uniqueness and default-brand rules visible under the control.
2. **Three price densities.** Phone list + sheet; tablet type · unit · price · flags · More; desktop office columns. Add Row lives in `JRSection` `#actions`. Delete is ghost/text.
3. **Error recovery in JR.** “N fields need attention”, scroll/focus to the first Identity error, inline row errors on list/table/sheet. Price Swal is gone for matrix validation.

## Priority Issues

### [P1] Catalog add/edit is JRDrawer chrome over Bootstrap DynamicForm
- **Why it matters:** The power-user shortcut (create Category/Unit while building a SKU) is the most frequent overlay. Inside it, `form-control` / `btn btn-primary` / `spinner-border` / Price Type ORM guide leave `.jr-pilot`. LIST_VIEWS and DESIGN.md say do not mix Bootstrap chrome inside the pilot.
- **Fix:** Rebuild the four catalog overlays with JRField / JRInput / JRSelect / JRButton on the same endpoints. Price Type help: three operational lines, no model names. If opened from the price sheet, one drawer with a back-to-row title — do not stack two drawers.
- **Suggested command:** `/impeccable distill`

### [P1] Price matrix still lies at save and crowds desktop
- **Why it matters:** Desktop remains `min-width: 56rem` and ten columns. Default radio disables when Purchase is on, even if Sale is also on — against “Only a sale price can be the default.” Rows missing unit+type+price are stripped silently. Create still auto-inserts an empty row so the empty state rarely appears.
- **Fix:** Enable Default when `is_sale`. Show “This row will not be saved” on incomplete rows. Create: empty state + Add, no ghost row. If desktop still overflows, push dates/Active into More there too. Currency or unit suffix on Price.
- **Suggested command:** `/impeccable shape`

### [P1] Classification selects can freeze on the wrong permission
- **Why it matters:** Category, Brands, and Default Unit disable when the user lacks `add_productcategory`. An editor who can `change_product` but cannot create categories cannot pick a brand or unit. Add on Brands uses `add_productbrand` — the select can be off while + is on.
- **Fix:** Disable those selects only in view mode (or without `change_product`). Keep Add/Edit gated on their real permissions. If a control is disabled, say why.
- **Suggested command:** `/impeccable harden`

### [P2] No safe exit from dirty work or row delete
- **Why it matters:** Cancel / Back to list leaves without a dirty warning. Row Delete is instant next to the phone tap target. Sheet Close does not say edits are already live.
- **Fix:** Confirm discard when dirty. Row delete: short undo or confirm if the row had a price. Sheet footer: Done as the close, Delete as the destructive secondary.
- **Suggested command:** `/impeccable harden`

### [P2] Errors and required state are only half-wired for assistive tech
- **Why it matters:** JRField builds `errorId` but does not set `aria-describedby` / `aria-invalid` on the control. Required asterisk is `aria-hidden`. API errors on `prices` / `price_units` do not map to `priceRowErrors`. Unmapped 400 is still JSON in Swal.
- **Fix:** Wire describedby; `aria-required`; map price API errors to rows; keep Swal for non-field failures only.
- **Suggested command:** `/impeccable audit`

## Persona Red Flags

**Alex (Power User):** Filter + inline catalog add is the accelerator, then Bootstrap schema. No Save shortcut, no duplicate row. Save → View is an extra click if the next SKU is waiting.

**Sam (Accessibility-Dependent):** Banner is a live alert and can take focus. Field errors are not described to the input. Two drawers (sheet + catalog) stack `aria-modal`. Native radio for Default. Swal leaves the JR live region.

**Casey (Distracted Mobile / Field):** Sticky Save is correct. Add Row sits in the section header (above the fold on a long form). Phone Delete sits beside the row tap. Catalog at 100vw hides the SKU. No draft if the SPA is recycled.

**FieldOps (office + field at a residential trade contractor):** Header and tracking copy now sound like the shop. Reorder Level has no unit. Price has no currency. Tablet hides Default until More — a crew lead can save a buyable SKU with no default sale price and not notice.

## Cognitive Load

Failed 5 of 8 checklist items → **high cognitive load** (was 7/8).

| Item | Verdict |
|---|---|
| Single focus | Fail — SKU + catalog overlay + price matrix in one session |
| Chunking | Fail — desktop price row still ~10 controls |
| Grouping | Pass — JRSection Identity / Classification / Inventory / Price |
| Visual hierarchy | Fail — sections share weight; addon +/− compete with the select; drawer body is another visual system |
| One thing at a time | Fail — catalog interrupts the SKU; sheet + catalog can stack |
| Minimal choices | Fail — desktop 10-column row |
| Working memory | Fail — incomplete rows vanish; More hides office columns |
| Progressive disclosure | Pass — phone sheet, tablet office columns hidden, SERIALIZED banner, distilled hints |

Decision points with >4 visible options: desktop price row (10); Classification addon cluster; Price Type drawer (schema + guide).

## Emotional Journey

Arrival is operational: Create/Edit/View plus one line of intent. Classification is quieter without hint noise. The valley is still Price (spreadsheet or sheet) and the catalog drawer (incumbent form). Save failures now start with a banner instead of silence. Success toast + view mode remains a calm end. Peak-end is better than the last run, still not the save.

## Minor Observations

- Brands is required and still has `showClear`.
- Reorder Level defaults to 0 with no unit hint.
- Sheet attributes `sheetError` to Price Type even when the message is dates or a duplicate.
- Identity measure is 48rem; the price table is a different layout width.
- Product `Active` now has a Status label (improvement).
- `ProductImageGallery` is still not on this screen.
- App shell remains Bootstrap (in scope to note, out of scope to restyle).

## Questions to Consider

- If add-category-in-flow is the power gesture, why does that gesture still look like 2019 Bootstrap?
- Is a price row a spreadsheet or a “how this SKU is bought and sold” card? Desktop still answers “spreadsheet.”
- Should default sale price live on the product, not on a radio that disables when Purchase is checked?
- If an editor cannot create categories, should Add disappear while the select stays alive?
