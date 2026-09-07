---
target: app/vuefrontend/src/components/inventory/ProductForm.vue
total_score: 26
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
timestamp: 2026-09-06T23-21-17Z
slug: efrontend-src-components-inventory-productform-vue
---
# Critique — Product Form Pilot (`ProductForm.vue`)

**Target:** `app/vuefrontend/src/components/inventory/ProductForm.vue`  
**Mode:** Operate — Construction Operations / ERP, mobile-first, data-dense  
**Contract:** DESIGN.md → Target State (Pilot). Direction approved; this review does not replace it.

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Unsaved + Saving… + banner. Product load has no skeleton; create-empty can look like the real state. |
| 2 | Match System / Real World | 3 | Crew/SKU/Quantity vs Serialized. Prices have no currency; dates stay ISO. |
| 3 | User Control and Freedom | 3 | Cancel + leave dialog + protected row delete. Catalog still closes the price sheet. |
| 4 | Consistency and Standards | 3 | Catalog, confirms, and textarea are JR. Tablet is a compact list, not LIST_VIEWS short-table. |
| 5 | Error Prevention | 3 | Incomplete rows block save. Dirty route guard. Empty + Add Row can become a save trap. |
| 6 | Recognition Rather Than Recall | 2 | Default brand is an explicit select. Default sale / dates / row Active still live in the sheet. |
| 7 | Flexibility and Efficiency | 2 | Filter + inline catalog add. No Save shortcut. Save forces View. |
| 8 | Aesthetic and Minimalist Design | 3 | Hint wall gone. Desktop is a sentence row; phone/tablet share compact cards. Type/Unit addons still crowd the row. |
| 9 | Error Recovery | 3 | Banner + describedby + live clear-on-correct. Row errors stay one concatenated blob. |
| 10 | Help and Documentation | 2 | Persistent Price note. SKU / brand / tracking are hover-only; help is not in describedby. |
| **Total** | | **26/40** | **Acceptable** |

## Design Specificity Verdict

**Start here.** Authored IA and trade copy; chrome is earned Operate familiarity, not a unique visual signature.

**LLM assessment:** Identity → Classification → Inventory → Price, crew header, Quantity vs Serialized, Default for purchasing, and “how this product is bought and sold” are JobRhythm Construction Ops. The page shell matches DESIGN.md Target State (Pilot): left title, tokens, JR catalog/dialog/textarea, no Bootstrap form chrome. The money surface is a shorter sentence table plus compact cards — still an ERP price matrix, but no longer a 10-column spreadsheet.

**Deterministic scan:** `detect.mjs --json` on ProductForm, ProductPriceUnitTable, ProductCatalogForm, JRDialog, JRTextarea, JRTooltip, and consumed JR primitives exited **0** with **0 findings**. Vue files go through text/regex detection. No false positives. No `ignore.md`.

**Visual overlays:** No reliable user-visible overlay. Chrome DevTools MCP failed (`Missing X server`). Mutation preflight never ran. live-server was not started. Fallback: **mutation unavailable**.

## Overall Impression

The last action set landed: tablet is real, More became Edit, leave/delete use JRDialog, default brand is operable, Price has a persistent rule line. The remaining valley is still the **money object**: desktop edits type/unit/price/flags without seeing default/dates; empty Add Row can block Save; commercial help is still hover-gated.

## What's Working

1. **One JR system.** Page, catalog drawer, leave/delete dialogs, and catalog textarea share primitives. No Bootstrap form chrome in this flow.
2. **Three densities that exist.** Phone and tablet: compact cards + Edit → sheet. Desktop: Price Type · Unit · Price · Purchase · Sale · Edit. Empty state hosts + Add Row.
3. **Operational risk controls.** Unsaved chip, `beforeRouteLeave`, JRDialog leave/delete, attention banner, first-error focus, incomplete rows named and blocking.

## Priority Issues

### [P1] Default sale, dates, and row Active stay off the desktop sentence
- **Why it matters:** The commercial core of the SKU. Desktop edits the sentence without opening Edit; the 0.75rem Price note is not a control. Compact cards omit Valid From/Until.
- **Fix:** Surface Default (and a date hint) on the row/card. Keep the sheet for dates/Active. One primary CTA per row.
- **Suggested command:** `/impeccable distill`

### [P1] + Add Row can become a save trap
- **Why it matters:** Empty state invites Add. A virgin row fails validatePriceMatrix and blocks the product save. Compact at least opens the sheet; desktop leaves an incomplete row in the table.
- **Fix:** Tentative rows that skip validate until touched, or sheet-first on desktop too. Discard of a virgin row already skips confirm — Save should treat untouched rows the same or auto-open Edit.
- **Suggested command:** `/impeccable harden`

### [P1] Commercial help is still hover-gated
- **Why it matters:** SKU, default brand, and tracking are JRTooltip only. `aria-describedby` wires errors, not help. Casey does not hover; Sam does not hear the rule. Reorder and Price Type have no in-context help.
- **Fix:** Visible JRField hint on the 3–4 ticket-generating rules. Tooltip as extra. Put help in describedby.
- **Suggested command:** `/impeccable clarify`

### [P2] JRSelectAddon forest on the price sentence
- **Why it matters:** Each Type/Unit cell is select + add + edit. A row becomes 8–10 affordances. Catalog admin is not the SKU happy path.
- **Fix:** Selects only on the table. +/Edit in the sheet or a section “Manage lists.”
- **Suggested command:** `/impeccable quieter`

### [P2] Load gap and post-save View peaje
- **Why it matters:** No busy/skeleton on loadProduct. Save → mode=view forces Edit product for the next tweak. Sticky Save is not fluid on the phone.
- **Fix:** Loading product… After create, stay in edit or land on the list with the name visible. Fluid primary under 768.
- **Suggested command:** `/impeccable harden`

## Persona Red Flags

**Alex:** No Cmd+S. Tab walks every +/✎. Save → View is a round trip. Desktop delete only inside the sheet.

**Sam:** Tooltip text is not in describedby. Purchase/Sale table checkboxes have ariaLabel but no visible label in the control. Sheet Type/Unit JRFields do not pass inputId. Row error is one alert string.

**Casey:** Compact + 100vw sheet is right. Hover help is wrong. Sticky Save is not full-width thumb. Dates stay in the sheet. Dirty is memory-only.

**FieldOps:** Price has no currency. Price Type is back-office jargon. Hidden validity windows risk buying/selling on a lapsed list. Reorder has no unit. Serialized copy is the fragment the rest of the form should match.

## Cognitive Load

Failed 6 of 8 → **high**. Grouping and visual hierarchy pass. Single focus, chunking, one-thing, minimal choices, working memory, and progressive disclosure fail (disclosure hides the commercial rules while the row is filled).

Decision points with >4 options: desktop price row (8–10); price sheet (11); Classification addon cluster.

## Emotional Journey

Arrival is operational. Identity is easy. Classification +/✎ introduces admin doubt. The valley is Price: rules + sentence/cards. Empty Add Row then Save is the deepest dip. Banner/focus reassures. Leave dialog is a safety net. Peak-end is View Product (locked form), not “the crew can buy this SKU.”

## Minor Observations

- Leave dialog header and message repeat the same question.
- Readonly row button still says Edit; drawer header becomes “Price row.”
- Lede + three-sentence note can collapse to one line.
- `getDefaultBrandName()` may miss on id type mismatch.
- Compact cards omit Valid From/Until even as meta.
- App shell remains Bootstrap (out of scope).

## Questions to Consider

- Should Create Product save identity first and treat prices as a second beat?
- Is default sale a SKU property or a row property? Today it is a row, buried in Edit.
- Does every SKU select need inline catalog add, or is that office-admin setup?
- What would a crew lead see as “SKU ready” on a phone?
