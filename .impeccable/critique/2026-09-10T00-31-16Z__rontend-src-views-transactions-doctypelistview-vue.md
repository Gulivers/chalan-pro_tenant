---
target: document-types / DocTypeListView
total_score: 23
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 2
timestamp: 2026-09-10T00-31-16Z
slug: rontend-src-views-transactions-doctypelistview-vue
---
# Critique — Transaction Types (`DocTypeListView.vue`)

**Method:** dual-agent (A: `2cae14c2-1ecf-420c-88cb-f979d8f89f03` · B: `527d19ad-84c7-421b-8129-3b2a32ba9ce2`)  
**Target:** `app/vuefrontend/src/views/transactions/DocTypeListView.vue` (+ form glance `DocTypeForm.vue`)  
**Mode:** Operate — admin SaaS master data  
**Live:** `http://test-dominio-local.chalanpro.net:8082/document-types` (authenticated)  
**Contract:** PRODUCT.md → DESIGN.md Pilot → LIST_VIEWS.md · peer Party Types

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Loading / aria-live / pager solid; quiet refresh success |
| 2 | Match System / Real World | 2 | Domain OK; INVFIS/INVLOG & Transaction↔Document naming leak |
| 3 | User Control and Freedom | 3 | Search clear, Back, delete confirm |
| 4 | Consistency and Standards | 2 | JR shell OK; list↔form labels diverge |
| 5 | Error Prevention | 2 | Delete confirm; jargon invites mis-edit |
| 6 | Recognition Rather Than Recall | 2 | Hover-only flow names; abbreviated columns; Yes/No badge soup |
| 7 | Flexibility and Efficiency | 2 | Sort/search; no Sales/Purchase filter |
| 8 | Aesthetic and Minimalist Design | 2 | Flow band purposeful; table equal-weight clutter |
| 9 | Error Recovery | 3 | Load-error + Refresh; search clear; delete toast |
| 10 | Help and Documentation | 2 | Flow strip partial help; no column glossary |
| **Total** | | **23/40** | **Acceptable** |

## Design Specificity Verdict

**Moderately specific.** Sales/Purchase flow strip is JobRhythm/trade-ops character; the dense boolean matrix below is pilot-generic master-data chrome that another inventory SaaS could ship unchanged.

**LLM (A):** Flow band teaches lifecycle; desktop ~11 columns of Yes/No flags reads as schema dump vs Party Types’ lean Name/Description/Status.

**Deterministic (B):** CLI `detect.mjs` on list + form → `[]` (exit 0). Browser inject OK; runtime flags mostly shell FPs (`overused-font`, `bounce-easing`, `dark-glow`, footer `low-contrast` Operational Flow). No material list-owned detector defects.

## Overall Impression

JR list shell is correct and operable; the biggest opportunity is progressive disclosure — lean default columns + filters aligned to the Sales/Purchase mental model the page itself teaches.

## What's Working

1. Sales/Purchase flow band — product-specific teaching Party Types lacks.
2. Pilot list discipline — single primary CTA, labeled row actions, empty/error paths, stock Entry/Exit/Neutral semantics.
3. Mobile progressive disclosure — cards keep code/description/stock/status.

## Priority Issues

### [P1] Abbreviation + Yes/No badge matrix
INVFIS/INVLOG/Neg. Sales force recall on high-stakes inventory flags. Align headers with form; demote “No”; emphasize exceptions.

### [P1] Entity naming split
List/nav “Transaction Types” vs form “Document Type” / toasts. Pick one term end-to-end.

### [P2] Flow legend codes without visible descriptions
Meanings only in `title`/hover. Add short labels or expandable legend.

### [P2] No Sales/Purchase filters on desktop
Flow frames two worlds; table dumps all. Segment chips + hide secondary columns.

### [P3] Visual noise vs Party Types peer
~3× column density; lean default (Code, Description, Stock, Status, Actions).

## Persona Red Flags

**Alex (power admin):** Cannot filter Sales vs Purchase; no exceptions-only view of flags.  
**Jordan (first-timer):** INVFIS/INVLOG jargon; list↔form wording mismatch.  
**Sam (a11y):** Flow codes without accessible full names; long tab paths across row actions.

## Minor Observations

- Stats often decorative when all Active.
- Form has more checkboxes than list shows (neither full summary nor lean index).
- Delete confirm generic (could echo type code).
- `min-width: 56rem` vs Party Types `36rem`.

## Detector notes

CLI clean. Browser overlays: treat body-scoped Inter/easing/glow and footer gold heading contrast as shell FP for this target.
