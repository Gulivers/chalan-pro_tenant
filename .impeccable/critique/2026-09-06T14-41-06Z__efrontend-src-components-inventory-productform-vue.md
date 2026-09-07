---
target: app/vuefrontend/src/components/inventory/ProductForm.vue
total_score: 29
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 1
timestamp: 2026-09-06T14-41-06Z
slug: efrontend-src-components-inventory-productform-vue
---
# Critique — Product Form Pilot (`ProductForm.vue`)

**Target:** `app/vuefrontend/src/components/inventory/ProductForm.vue`  
**Mode:** Operate — Construction Operations / ERP, mobile-first, data-dense  
**Contract:** DESIGN.md → Target State (Pilot). Direction approved; this review does not replace it.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Banner, Saving…, empty prices. Product/list load still has no skeleton. |
| 2 | Match System / Real World | 3 | Crew/SKU/Quantity vs Serialized. Catalog Price Type copy is operational. Section titles stay ERP-generic. |
| 3 | User Control and Freedom | 3 | One list exit, dirty confirm, protected row delete, no stacked drawers. No undo after save. |
| 4 | Consistency and Standards | 3 | Catalog overlay is JR. Default is a native radio; Cancel uses window.confirm. |
| 5 | Error Prevention | 3 | Incomplete rows explained and block save. Default enabled on is_sale. Selects no longer gated on add_category. |
| 6 | Recognition Rather Than Recall | 3 | Tooltips on the five needed fields. Brand default is still first-selected. Dates live in More. |
| 7 | Flexibility and Efficiency | 2 | Filter + inline catalog add. No Save shortcut, no duplicate-row. |
| 8 | Aesthetic and Minimalist Design | 3 | Hint wall gone. Desktop/tablet share a 7-column short table + More. |
| 9 | Error Recovery | 4 | Banner + describedby + live clear-on-correct. Unmapped 400 is a human banner, not Swal JSON. |
| 10 | Help and Documentation | 2 | Targeted JRTooltip. Help text is not in aria-describedby; hover-first on desktop. |
| **Total** | | **29/40** | **Good** |

## Design Specificity Verdict

**Start here.** Authored JR chrome and trade IA; catalog overlay is now the same visual system as the page.

**LLM assessment:** Identity → Classification → Inventory → Price still matches a contractor SKU mental model. Header copy, Quantity vs Serialized, Purchase/Sale/Default, and three price densities remain JobRhythm Construction Ops. Catalog add/edit is JRField/JRInput/JRSelect/JRCheckbox — no Bootstrap `form-control` / `btn-primary` in this flow. Assessment A notes the section titles are still generic ERP; that is residual voice, not a chrome leak.

**Deterministic scan:** `detect.mjs --json` on ProductForm.vue, ProductPriceUnitTable.vue, and ProductCatalogForm.vue exited **0** with **0 findings**. Vue files go through text/regex detection. That is “no static anti-pattern string matches,” not a pass on live layout. No false positives. No `ignore.md`.

**Visual overlays:** No reliable user-visible overlay. Chrome DevTools MCP failed (`Missing X server`; `DISPLAY` unset). Mutation preflight never ran. live-server was not started. Fallback: **mutation unavailable**.

## Overall Impression

The 24/40 P1s are gone: catalog is JR, the money row no longer lies at save, and classification selects are usable without create-catalog permission. The remaining valley is help (tooltip-only) and the still-dense price object — now seven visible decisions plus More, not ten columns that silently drop rows.

## What's Working

1. **Catalog overlay matches the pilot.** Same endpoints as DynamicForm, JR primitives only, Price Type help in three operational lines, no ORM names, no Bootstrap alert.
2. **Price truth at save.** Incomplete rows name what they still need and block the product save. Default radio follows `is_sale`. Empty create state is real (no ghost row).
3. **Error recovery in JR.** Field errors clear as the user types; 400 maps to JRField / row / banner; no JSON `<pre>` in Swal.

## Priority Issues

### [P1] Help is still hover-first and not in the field accessibility tree
- **Why it matters:** SKU uniqueness, brand-default, tracking, and default-sale rules live in JRTooltip. `JRField` `describedby` is error-only. Sam and touch users can miss the rule.
- **Fix:** Keep the icon. Also expose those five strings as `aria-describedby` (or a collapsible hint) so help is in the tree without bringing back a hint wall.
- **Suggested command:** `/impeccable harden`

### [P2] Product/catalog load has no busy/skeleton state
- **Why it matters:** Edit can show empty fields until GET returns. Catalog says “Loading…” without aria-busy.
- **Fix:** `aria-busy` on the form; disable controls or skeleton until hydrate.
- **Suggested command:** `/impeccable harden`

### [P2] Dirty confirm is Cancel-only
- **Why it matters:** `window.confirm` on Cancel / Back to list. Browser back and navbar leave without it.
- **Fix:** `beforeRouteLeave` reusing `isDirty()`. Optional JR dialog later.
- **Suggested command:** `/impeccable harden`

### [P2] Price sheet still packs every office field
- **Why it matters:** More → drawer is correct for phone and for hiding dates. The sheet itself still shows 9+ controls. Tablet inherits the short table (`min-width: 36rem`).
- **Fix:** Keep as-is unless a later increment splits “quote” vs “office dates.” Do not return to a 10-column desktop grid.
- **Suggested command:** `/impeccable distill`

## Persona Red Flags

**Alex (Power User):** Filter + JR catalog add is the accelerator. No Save shortcut. Save → View is an extra click.

**Sam (Accessibility-Dependent):** Banner is a live alert. Identity errors are described. Help tooltips are not. Native radio for Default. `window.confirm` leaves the JR live region.

**Casey (Distracted Mobile / Field):** Sticky Save is correct. Phone Delete is inside More. Catalog at 100vw hides the SKU. No draft if the SPA is recycled.

**FieldOps:** Header and tracking copy sound like the shop. Reorder Level still has no unit. Price has a unit suffix, not currency.

## Cognitive Load

Failed 4 of 8 checklist items → **medium-high** (was 5/8 at 24/40).

| Item | Verdict |
|---|---|
| Single focus | Fail — SKU + catalog overlay + price matrix |
| Chunking | Fail — price row still ~7 visible controls |
| Grouping | Pass — Identity / Classification / Inventory / Price |
| Visual hierarchy | Pass — Name+SKU priority; Model secondary; no Bootstrap drawer body |
| One thing at a time | Fail — catalog interrupts the SKU |
| Minimal choices | Fail — desktop 7-column row |
| Working memory | Partial — incomplete rows explain themselves; More still hides dates |
| Progressive disclosure | Pass — phone sheet, tablet/desktop office columns hidden, SERIALIZED banner, tooltips |

## Emotional Journey

Arrival is operational. Classification is quieter and selectable. The valley is still Price, but it no longer lies at save and no longer opens a 2019 Bootstrap form. Peak-end is banner + toast + view — calmer than 24/40.

## Minor Observations

- Brands required; `showClear` removed.
- Reorder Level still defaults to 0 with no unit.
- Identity measure is 48rem; the price table is full-bleed.
- `ProductImageGallery` is still not on this screen.
- App shell remains Bootstrap (out of scope).
- Assessment A asked for inline phone price edit; this increment required More → drawer. Treat inline edit as a later choice, not a regression.

## Questions to Consider

- If help must stay off the canvas, how does it enter the accessibility tree without becoming a hint wall?
- Should a SKU refuse to save with zero price rows, or is an identity-only draft legitimate?
- Is first-selected brand still the purchasing default the shop expects?
