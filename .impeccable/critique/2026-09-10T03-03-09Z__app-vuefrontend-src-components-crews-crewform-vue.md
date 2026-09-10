---
target: CrewForm /crews/form
total_score: 20
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 4
p2_count: 1
timestamp: 2026-09-10T03-03-09Z
slug: app-vuefrontend-src-components-crews-crewform-vue
---
Method: dual-agent (A: 3751b05d-cedf-4cab-b450-f8a662048309 · B: ee78ea15-6495-4227-a87b-2b1677d6c9a3)

#### Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | Loading/Saving exist; chosen count / filter-active not surfaced |
| 2 | Match System / Real World | 2 | Ctrl tip vs PickList buttons; Builder vs customers vs Is Customer |
| 3 | User Control and Freedom | 3 | Cancel/clear exist; Move All / silent empty Available lack explanation |
| 4 | Consistency and Standards | 2 | Nested JRField + raw PickList + Django help vs Product Form patterns |
| 5 | Error Prevention | 2 | Move All mass-assign; filter hides jobs without clear scope |
| 6 | Recognition Rather Than Recall | 2 | filterBy=name only; builder stacked not suffix; filter scope recall |
| 7 | Flexibility and Efficiency | 2 | Detached Builder slows frequent path |
| 8 | Aesthetic and Minimalist Design | 1 | Tip + Builder hint + dual essay headers drown primary task |
| 9 | Error Recovery | 2 | Swal interrupts; jobs errors not field-adjacent |
| 10 | Help and Documentation | 2 | High volume, low task focus |
| **Total** | | **20/40** | **Acceptable** |

#### Design Specificity Verdict

**LLM assessment**: JR pilot shell is real; Assigned Jobs reads as Django Admin dual-list transplant. Builder treated as peer field, not PickList lens. Row content almost right but stacked.

**Deterministic scan**: CLI detect.mjs on CrewForm.vue: 0 findings (exit 0). Browser inject: 9 anti-patterns; form-relevant: cramped-padding ×2 on PickList lists; rest footer/shell false positives.

**Visual overlays**: Injection succeeded on Add Crew; overlays in browser [Human] tab during Assessment B (live-server stopped after).

#### Overall Impression

Solid JR form skeleton; the jobs dual-list is the valley—detached Builder, stacked labels, and instructional walls.

#### What's Working

1. JRPage / JRSection / sticky Save-Cancel skeleton
2. Community + muted builder content already present on rows
3. Schedule permission uses in-field hint correctly

#### Priority Issues

**[P1] Builder filter detached from PickList**
- Why: Reads as separate form question
- Fix: Integrate into PickList chrome/toolbar
- Suggested: /impeccable layout

**[P1] Row labels stack Builder, not inline suffix**
- Why: Slows scan; fights "Community — Builder" reading
- Fix: Single-line primary + muted suffix; filterBy includes builder
- Suggested: /impeccable typeset

**[P1] Django-admin help walls**
- Why: Wrong metaphor; high extraneous load
- Fix: Short Available/Chosen labels; drop Ctrl tip
- Suggested: /impeccable distill

**[P1] Copy: Builder vs customers vs Is Customer**
- Why: Schema jargon
- Fix: Plain "Filter available by customer"
- Suggested: /impeccable clarify

**[P2] Sticky Save vs PickList on mobile**
- Why: Thumb/viewport competition
- Fix: Safe-area padding / adapt
- Suggested: /impeccable adapt

#### Persona Red Flags

**Jordan**: Ctrl tip, Is Customer jargon, essay headers
**Sam**: Nested field describedby; option SR announcement
**Casey**: Stacked dual-list + tip + sticky bar
**Alex**: Cannot search by builder name; detached filter hop

#### Minor Observations

Single Details section packs too much; view mode still shows full chrome; no N chosen summary.

#### Questions to Consider

- If Builder is only a lens, why a full JRField equal to Crew Name?
- Would a filtered checklist beat dual-list for this task?
