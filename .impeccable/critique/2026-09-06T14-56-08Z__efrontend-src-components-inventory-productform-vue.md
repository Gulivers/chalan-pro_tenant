---
target: app/vuefrontend/src/components/inventory/ProductForm.vue
total_score: 25
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
timestamp: 2026-09-06T14-56-08Z
slug: efrontend-src-components-inventory-productform-vue
---
# Critique — Product Form Pilot (`ProductForm.vue`)

**Target:** `app/vuefrontend/src/components/inventory/ProductForm.vue`  
**Mode:** Operate — Construction Operations / ERP, mobile-first, data-dense  
**Contract:** DESIGN.md → Target State (Pilot). Direction approved; this review does not replace it.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Save and attention banner work. Product/list load has no skeleton; dirty state only appears on Cancel. |
| 2 | Match System / Real World | 3 | Crew/SKU/Quantity vs Serialized. Default-brand-by-chip-order and combo-duplicate copy still speak admin. |
| 3 | User Control and Freedom | 3 | One list exit, Cancel confirm, protected row delete, no stacked drawers. Browser Back / navbar skip the dirty guard. |
| 4 | Consistency and Standards | 2 | Catalog overlay is JR. Default is a native radio; discard/delete use window.confirm; catalog textarea is raw. |
| 5 | Error Prevention | 3 | Incomplete rows explain and block save. Default follows is_sale. Selects no longer gated on add_category. No route leave guard. |
| 6 | Recognition Rather Than Recall | 2 | Default brand and Valid dates live in tooltip / More. Default Unit vs row units is unexplained. |
| 7 | Flexibility and Efficiency | 2 | Filter + inline catalog add. No Save shortcut, no duplicate-row. Save forces View. |
| 8 | Aesthetic and Minimalist Design | 3 | Hint wall gone. Desktop/tablet still share a 7-column table (`isTablet` unused). |
| 9 | Error Recovery | 3 | Banner + describedby + live clear-on-correct. Unmapped 400 is human, not JSON. Min-length copy is terse. |
| 10 | Help and Documentation | 2 | Targeted JRTooltip. Help is hover-first; Reorder and unit systems have none. |
| **Total** | | **25/40** | **Acceptable** |

## Design Specificity Verdict

**Start here.** Authored IA and trade copy; price composition is still a generic ERP grid.

**LLM assessment:** Identity → Classification → Inventory → Price, crew header copy, Quantity vs Serialized, Purchase/Sale/Default, and unit suffix on price are JobRhythm Construction Ops. The page shell matches DESIGN.md Target State (Pilot): left title, tokens, JR catalog overlay, no Bootstrap `form-control` in this flow. The money surface is still a short spreadsheet (7 columns + More/Delete). Status + Active could sit on any inventory form unchanged. Assessment A called the chrome category-interchangeable and the IA authored — that split is right.

**Deterministic scan:** `detect.mjs --json` on ProductForm.vue, ProductPriceUnitTable.vue, ProductCatalogForm.vue, JRTooltip.vue, and consumed JR primitives exited **0** with **0 findings**. Vue files go through text/regex detection. That is “no static anti-pattern string matches,” not a pass on live layout or hover-only help. No false positives. No `ignore.md`.

**Visual overlays:** No reliable user-visible overlay. Chrome DevTools MCP failed (`Missing X server`; `DISPLAY` unset). Mutation preflight never ran. live-server was not started. Fallback: **mutation unavailable**.

## Overall Impression

The 24/40 P1s (Bootstrap catalog, silent row drop, permission-gated selects) stay closed. This independent pass is stricter than the 29/40 run: recovery and catalog chrome are Good; the remaining valley is **how the SKU is bought and sold on a 768px+ grid**, plus rules that still live in tooltip or chip order. Tablet is declared in JS and unused — 768–1023 gets the same short table as desktop.

## What's Working

1. **Pilot chrome is one system.** JRPage / sections / catalog drawer / ProductCatalogForm. Same endpoints as DynamicForm. Price Type help is three operational lines, no ORM names.
2. **Price truth at save.** Incomplete rows name what they still need and block the product save. Default radio follows `is_sale`. Phone: More → sheet → Delete inside, confirmed.
3. **Error recovery in JR.** Attention banner, first-error focus, live clear-on-correct, field-mapped 400s, human non-field failures.

## Priority Issues

### [P1] Price row is still a 7-control grid; tablet density is dead code
- **Why it matters:** Money is the high-stakes moment. `isTablet` is set from 768–1023 and never read. Tablet and desktop share `jr-price-table--short` (Price Type, Unit, Purchase, Sale, Price, Default, More, Delete). Each type/unit cell still carries +/pencil. Phone “More” is the only editor but reads as overflow.
- **Fix:** Desktop: type · unit · price · buy/sell as the sentence; dates/Active/Default in More if they still crowd. Tablet: short list or four columns, not the 36rem table. Phone label: Edit, not More. Empty state should carry + Add Row.
- **Suggested command:** `/impeccable distill`

### [P1] Default brand is chip order; Default Unit vs row units is unspoken
- **Why it matters:** Buying on the wrong brand is a money error. The rule is only in a tooltip and a late “Default brand: …” line. Warehouse default unit and price-row units are two systems with no on-screen bridge.
- **Fix:** An explicit “Default for purchasing” control (not `brands[0]`). One persistent line: default unit is the warehouse count; price rows may use other units. Do not change the backend rule unless product asks — make the existing rule visible and operable.
- **Suggested command:** `/impeccable clarify`

### [P1] Dirty work dies on Back / navbar
- **Why it matters:** `isDirty()` + Cancel confirm exist. `beforeRouteLeave` does not. Field staff lose a half-built SKU when they hit the browser back control or a menu link.
- **Fix:** Route guard (and a cheap “Unsaved” mark on the sticky Save if it stays honest).
- **Suggested command:** `/impeccable harden`

### [P2] Help is hover-first; Reorder and dates stay hidden
- **Why it matters:** Casey in the truck does not hover. Valid From/Until and row Active live only in the sheet. Reorder Level has no unit or meaning. Catalog Price Type already uses a persistent note — the parent form does not.
- **Fix:** Persistent JRField hint on the 3–4 money rules. Tooltips for the rest. Rename More to “Dates & default” where that is what it opens.
- **Suggested command:** `/impeccable clarify`

### [P2] Native radio, native confirm, Status/Active split
- **Why it matters:** The pilot promised JR primitives. Sale default is `<input type="radio">`. Discard and row delete are `window.confirm`. Status is a label around an Active checkbox. Catalog description is a raw textarea.
- **Fix:** JR default control; JR confirm/dialog; one Active switch; JR textarea if the catalog needs one.
- **Suggested command:** `/impeccable polish`

## Persona Red Flags

**Alex (Power User):** Filter + inline catalog add is the accelerator. No Cmd+S, no paste/duplicate price rows. Save → View is an extra click. Opening Add Price Type from the sheet closes the sheet first.

**Sam (Accessibility-Dependent):** Banner can take focus. Field errors describedby on identity. Tooltip text is not in the input’s describedby. Native radio and window.confirm leave JR/Prime. Status label is not tied to `#isActive`. Desktop tab order walks every addon cluster.

**Casey (Distracted Mobile / Field):** Sticky Save is correct. Phone list + full-width sheet is the right split. “More” is the only editor and sounds like overflow. Tooltips fail under a thumb. Catalog interrupt (close sheet → drawer → reopen) is costly one-handed.

**FieldOps (office + field at a residential trade contractor):** Header and tracking sound like the shop. The money row still looks like flags and combos, not “bought by the box at $X.” Reorder has no unit. Wrong default brand is easy if they treat chips as a bag, not a ranked list.

## Cognitive Load

Failed 6 of 8 checklist items → **high cognitive load**.

| Item | Verdict |
|---|---|
| Single focus | Fail — SKU identity and price matrix are two jobs |
| Chunking | Fail — 7–8 controls per desktop price row |
| Grouping | Pass — JRSection Identity / Classification / Inventory / Price |
| Visual hierarchy | Fail — four sections share weight; money is not visually first |
| One thing at a time | Fail — sheet closes so catalog can open |
| Minimal choices | Fail — desktop row + addon +/pencil |
| Working memory | Fail — brand order; unit_default vs row unit; dates in More |
| Progressive disclosure | Fail — phone sheet yes; tablet unused; help is hover |

Decision points with >4 visible options: desktop price row (8+); price sheet (10+); Category/Unit addon cluster; Brands chips + hidden default.

## Emotional Journey

Arrival is operational. Identity is in control. Classification feels like admin chrome (+/pencil). The valley is Price: a short spreadsheet, fear of incomplete rows, and a sheet that closes when catalog opens. Invalid save is better than silence (banner + focus). Success toast + View is a calm end with an extra Edit click if they meant to keep loading prices.

## Minor Observations

- Brands has Add, not Edit; Category and Unit have both.
- Empty price state does not host the Add Row action (it lives on the section header).
- Button “Update” vs title “Edit Product” vs toast “Product updated.”
- Post-save `mode=view` avoids double-submit; it hurts “save and keep pricing.”
- Required asterisk and 2px primary focus match the pilot.
- App shell remains Bootstrap (in scope to note, out of scope to restyle).

## Questions to Consider

- If a price row were a sentence (“Sold by the box at $12.50”), would seven columns still be the desktop answer?
- Does default brand deserve its own control, or is chip order really the purchasing mental model?
- Should creating a SKU be two beats — identity first, prices after the SKU exists?
- What does a crew-lead 60-second thumb completion look like if no tooltip is required?
