---
target: builders / BuilderView
total_score: 23
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
timestamp: 2026-09-10T00-34-44Z
slug: app-vuefrontend-src-views-parties-builderview-vue
---
# Critique — Builders & Parties (`BuilderView.vue`)

**Method:** dual-agent (A: `2ac43adf-887b-4124-8029-054859347153` · B: `d9c3daf8-0cee-4b62-9847-26b03cff420f`)  
**Target:** `app/vuefrontend/src/views/parties/BuilderView.vue`  
**Mode:** Operate — master parties list  
**Live:** `http://test-dominio-local.chalanpro.net:8082/builders` (authenticated)  
**Contract:** PRODUCT.md → DESIGN.md Pilot → LIST_VIEWS.md · peer Party Types

## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Loading / Updating / aria-live solid |
| 2 | Match System / Real World | 2 | Parties vs Builders vs `/builders`; Trim/Rough unexplained |
| 3 | User Control and Freedom | 3 | Clear search, Refresh, delete confirm |
| 4 | Consistency and Standards | 2 | JR chrome OK; naming drift |
| 5 | Error Prevention | 3 | Delete confirm; non-interactive stats |
| 6 | Recognition Rather Than Recall | 3 | Labeled actions; no role filters |
| 7 | Flexibility and Efficiency | 1 | No bulk, column picker, Customer/Supplier filter |
| 8 | Aesthetic and Minimalist Design | 2 | Column wall + sparse `—` cells |
| 9 | Error Recovery | 3 | Empty + Clear/Refresh; toast says “builders” |
| 10 | Help and Documentation | 1 | No help for Party / Trim / Rough / ranks |
| **Total** | | **23/40** | **Acceptable** |

## Design Specificity Verdict

Competent JR pilot master-list, not strongly product-authored for residential trade ops. Domain signals (Trim/Rough, Customer/Supplier) feel bolted onto a generic contacts grid.

**Deterministic (B):** CLI `detect.mjs` → `[]` (exit 0). Browser inject: `cramped-padding` on datatable (real-ish); `em-dash-overuse` likely FP from empty `—` cells; Inter/easing/glow/footer contrast mostly shell FPs.

## Overall Impression

Shell and a11y baseline are solid; the table dumps too many sparse contact columns. Biggest opportunity: lean scan columns + unify Parties/Builders naming + role filters.

## What's Working

1. Pilot list contract — JR primitives, create-in-header, ghost Refresh, empty recovery.
2. Responsive shell — phone list vs desktop table.
3. A11y baseline — sr-only labels, aria-live, labeled row actions.

## Priority Issues

### [P1] Terminology split
H1/CTA **Parties**, URL `/builders`, error toast “builders”.

### [P1] Column wall without tablet disclosure
11 columns always on ≥768; violates LIST_VIEWS short-tablet intent.

### [P1] Sparse empty-state density
Most contact cells `—`; slows “pick a party”.

### [P2] Domain prices under-served
Trim/Rough lack clear currency/hierarchy.

### [P2] No role-axis filters
Customer/Supplier only passive badges.

## Persona Red Flags

**Alex:** No filters/bulk; horizontal scroll past empties.  
**Jordan:** Parties vs Builders mismatch; Trim/Rough opaque; dual name-link + View entry.

## Minor Observations

- Status column duplicates toolbar Active/Inactive.
- Mobile meta omits phone/email/roles.
- Client-side paging fine at n=5; not a server-list contract yet.

## Detector notes

CLI clean. Browser: cramped-padding on table worth noting; treat em-dash/Inter/easing/glow/footer gold as mostly FP.
