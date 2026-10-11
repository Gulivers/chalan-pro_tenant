---
name: JobRhythm Admin
description: Operational Vue admin for residential trade contractors — Bootstrap 5 with skin-modern overlay, data-dense, Inter-forward.
colors:
  primary: "#2563eb"
  primary-hover: "#1d4ed8"
  primary-deep: "#1e3a8a"
  primary-mid: "#1e40af"
  section-accent: "#c08500"
  success: "#16a34a"
  danger: "#dc2626"
  info: "#0dcaf0"
  warning: "#ffc107"
  neutral-page-start: "#e8ebee"
  neutral-page-end: "#dfe3e8"
  neutral-surface: "#f1f3f5"
  neutral-card-border: "#e5e7eb"
  neutral-input-border: "#cbd0d6"
  text: "#212529"
  text-muted: "#4b5563"
  text-label: "#4b5563"
  footer-bg: "#2c3e50"
  jr-page: "#f3f4f6"
  jr-surface: "#ffffff"
  jr-surface-muted: "#f9fafb"
  jr-text: "#111827"
  jr-hover-border: "#d1d5db"
  jr-info: "#0284c7"
  jr-warning: "#d97706"
  jr-primary-950: "#172554"
typography:
  body:
    fontFamily: "Inter, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 600
    lineHeight: 1.4
  title:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1.2
  table:
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.4
  jr-body:
    fontFamily: "Inter, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.45
  jr-label:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1.3
  jr-hint:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.4
  jr-title:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "1.3125rem"
    fontWeight: 600
    lineHeight: 1.25
  jr-section:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 600
    lineHeight: 1.3
rounded:
  sm: "0.65rem"
  md: "0.7rem"
  lg: "0.8rem"
  xl: "1.25rem"
  jr-control: "0"
  jr-panel: "0.75rem"
spacing:
  xs: "0.5rem"
  sm: "0.65rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2rem"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: "0.6rem 1.4rem"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: "0.6rem 1.4rem"
  navbar:
    backgroundColor: "{colors.primary-deep}"
    textColor: "#ffffff"
  input-default:
    backgroundColor: "#ffffff"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: "0.65rem 0.9rem"
---

# Design System: JobRhythm Admin

## Overview

**Creative North Star: "Modern Field Console"**

The incumbent JobRhythm admin UI is a **Vue 3 + Bootstrap 5** operational console with an active **`skin-modern.css` overlay** imported from `main.js`, layered on top of **`custom-bootstrap.scss`**. What users see today is a soft gray page background, rounded cards, Inter-forward typography, a deep-blue gradient navbar (`.navbar-modern`), Tailwind-inspired blues for primary actions (`#2563eb`), and module-specific SCSS in isolated flows (onboarding, assistant panel, inventory widgets).

The codebase also contains **`chalanpro-theme.scss`** (ocean dark / light theme tokens via `data-theme`), but that file is **not currently imported** in `main.js` and should be treated as alternate/legacy, not the live incumbent system.

**Key Characteristics:**

- Data-dense tables, filters, and forms for daily contractor operations
- Bootstrap primitives + bootstrap-vue-next + third-party grids (AG Grid) and selects (vue-select)
- Active visual layer: `skin-modern.css` (rounded cards, modern navbar, Inter, blue primary)
- Base Bootstrap theme remap in `custom-bootstrap.scss` (blue–indigo mix) partially superseded by skin-modern `!important` rules
- Assistant panel and some modules carry local scoped styles that must not become accidental global rules during upgrade

## Colors

The live palette is dominated by **modern blues and neutral grays**, with amber used for section emphasis.

### Primary

- **Action Blue** (`#2563eb`): primary buttons, switch-on states, focus accents in `skin-modern.css`.
- **Deep Blueprint** (`#1e3a8a` → `#1e40af`): navbar gradient in `.navbar-modern`.
- **Focus Blue** (`#3b82f6`): input/switch focus rings.

### Secondary (operational accents)

- **Section Amber** (`#c08500`): `.section-title` emphasis in forms such as inventory/product flows.
- **Footer Slate** (`#2c3e50`): legacy footer background in `App.vue` (may diverge from navbar chrome).

### Neutral

- **Page Mist** (`#e8ebee` → `#dfe3e8`): default page background gradient.
- **Surface Gray** (`#f1f3f5`): card surfaces in skin-modern.
- **Border Gray** (`#e5e7eb`, `#cbd0d6`): tables, inputs, dividers.
- **Label Gray** (`#4b5563`): form labels (skin-modern overrides App.vue primary-colored labels).

### Semantic

- **Success** (`#16a34a`), **Danger** (`#dc2626`), Bootstrap **warning/info** tokens for validation and alerts.
- SweetAlert2 and module code reuse Bootstrap semantic colors in dialogs.

**The Layered Source Rule.** When documenting or changing global styles, treat **`skin-modern.css` + `NavbarComponent.vue` classes** as the visible incumbent for shell/navigation; treat **`custom-bootstrap.scss`** as underlying Bootstrap remap; do not assume **`chalanpro-theme.scss`** is active without verifying import.

**The Status Semantics Rule.** Success, warning, danger, and info colors must remain unambiguous for operational states.

## Typography

**Display/Title Font:** Inter (preferred in skin-modern body; also referenced in theme file)  
**Body Font:** Inter with system-ui fallback (`skin-modern.css`)  
**App shell note:** `App.vue` still sets Avenir for `.app-container`; skin-modern and form label rules partially override label color but not all shell typography.

**Character:** Practical, medium-weight labels, bold page titles, readable table headers — optimized for scanning operational data, not marketing display type.

### Hierarchy

- **Title** (700, 2rem): `.main-title` in feature forms/pages.
- **Section** (600, 1.2rem, amber accent): `.section-title`.
- **Label** (600, 0.95rem, `#4b5563`): form field labels.
- **Body** (400, 1rem): default UI copy and controls.
- **Table header** (600, ~0.875rem): `.table-modern thead`.

**The Density Rule.** Prefer readable operational density; avoid marketing-scale whitespace inside modules.

## Layout

- App shell: `NavbarComponent` + flex column `main.content` + footer (`App.vue`).
- Bootstrap grid (`container-fluid`, rows/cols) with skin-modern gutter overrides (`--bs-gutter-x/y: 1rem` in places).
- Cards as primary content containers; many modules wrap filters/forms/tables in `.card` / `.card-modern`.
- Navbar collapses under Bootstrap `xl` breakpoint; skin-modern adds backdrop overlay for mobile menu.
- AG Grid and FullCalendar modules introduce their own layout constraints inside feature views.

## Elevation & Depth

Hybrid system:

- **Cards:** soft stacked shadows (`0 12px 35px rgba(0,0,0,.12)`) rather than flat borders alone.
- **Navbar:** gradient fill, minimal drop shadow, high z-index stack (20000+) for dropdowns.
- **Modals/drawers:** Bootstrap modal + Assistant drawer shadow (`-4px 0 24px rgba(0,0,0,.18)` locally scoped).
- **Not flat-by-default** in skin-modern, but also not glassmorphism-heavy except in unused `chalanpro-theme.scss`.

### Shadow Vocabulary

- **Card rest:** `0 12px 35px rgba(0,0,0,0.12), 0 4px 10px rgba(0,0,0,0.05)`
- **Input focus:** `0 0 0 3px rgba(59, 130, 246, 0.25)`
- **Switch focus:** same blue focus halo pattern

**The Single Global Layer Rule.** During upgrade, consolidate to one global style authority; avoid adding a fourth parallel global skin.

## Shapes

- Rounded operational UI: inputs ~`0.65rem`, buttons ~`0.7rem`, cards ~`1.25rem`, tables ~`0.8rem`.
- Navbar dropdown menus: white surfaces, rounded corners, gray text items.
- Switches use iOS-like pill controls in skin-modern.

## Components

### Buttons

- **Shape:** rounded (`0.7rem` helper `.btn-rounded`, primary defaults in skin-modern)
- **Primary:** `#2563eb` background, white text, darker hover `#1d4ed8`
- **Secondary:** gray palette `#6b7280` → `#4b5563` hover
- **Assistant nav button:** `btn-outline-light` on dark navbar

### Navigation

- **Navbar (`.navbar-modern`):** deep blue gradient, white links, logo image brand, collapsible menu with backdrop on small screens
- **Active/open dropdown:** `.text-orange` class name legacy; skin-modern forces white active treatment
- **Dropdown menus:** white background, gray items `#4b5563`, light gray hover wash

### Cards / Containers

- **Surface:** `#f1f3f5`
- **Radius:** `1.25rem`
- **Padding:** generous (`2rem 2.5rem` default in skin-modern)
- **Header:** transparent/light divider

### Inputs / Fields

- White fields, `#cbd0d6` borders, inset shadow, blue focus ring
- vue-select and Bootstrap selects styled in both global CSS and module SCSS
- Disabled fields: `#e5e7eb` background

### Tables

- Bootstrap tables + `.table-modern` wrapper (white surface, gray header `#f3f4f6`, hover `#f1f5f9`)
- AG Grid used in inventory/transactions with its own theme/CSS

### Assistant Panel (module-local)

- Right drawer, dark header `#212529`, light content area, structured blocks (KPI/table/chart)
- Preserve behavioral/security constraints from JobRhythm Assistant harness when reskinning

### Legacy / inactive theme file

- `chalanpro-theme.scss` defines ocean-dark and light corporate tokens with `--cp-*` variables and glass cards; **not active** unless re-imported deliberately.

## Do's and Don'ts

### Do:

- **Do** treat `skin-modern.css` as the primary visual reference for the current global shell.
- **Do** preserve Bootstrap semantic colors for validation and operational feedback.
- **Do** maintain scannable table/form density and clear filter toolbars.
- **Do** consolidate overlapping global styles during frontend upgrade instead of adding another parallel theme file.
- **Do** keep Assistant and third-party widget styling scoped or adapter-based when migrating to shared primitives.

### Don't:

- **Don't** assume `custom-bootstrap.scss` alone describes what users see; skin-modern overrides many rules.
- **Don't** activate `chalanpro-theme.scss` or dark ocean tokens without an explicit product decision and migration plan.
- **Don't** replace operational tables with decorative card layouts without a responsive strategy.
- **Don't** introduce gradient text, glow shadows, or decorative motion in core workflows.
- **Don't** hide backend validation meaning behind generic frontend-only messages.

---

# Target State (Pilot)

> **Status:** Target design contract for migrated modules **and** the App Shell (Navbar / Footer).
> Everything above this heading remains the **CURRENT STATE** (Bootstrap 5 + `skin-modern.css`) for screens not yet migrated. Until a screen or shell surface is on JR / PrimeVue, those current-state rules still describe what ships today.
>
> **App shell is in scope for the frontend upgrade.** Navbar and Footer must leave Bootstrap / `skin-modern` chrome and adopt JR tokens + PrimeVue (same authority as list/form pilots). Do not preserve Bootstrap traces in the shell as a permanent coexistence strategy.

## Scope of this increment

Frontend-upgrade increment (branch / harness `jobrhythm-frontend-upgrade`, e.g. `dev_local_primevue`):

- Vue CLI 5 (Webpack) + Tailwind CSS 4 + PrimeVue styled mode
- JobRhythm semantic tokens and JR primitives under `app/vuefrontend/src/ui/`
- Coexistence: Bootstrap + skin-modern remain **only** on unmigrated feature screens until each is wrapped in `JRPage` / `.jr-pilot`
- **In this increment (and follow-ons):** migrated feature modules **plus App Shell** — `NavbarComponent`, `FooterComponent`, and related layout chrome in `App.vue` as needed
- **Already landed (reference):** Product Form / Product List and other modules already on JR
- **Not in this increment:** Vite migration, Tailwind Preflight (would reset Bootstrap globally while remnants remain)

Architecture:

`feature view | App Shell → JR primitive → PrimeVue (styled) → Tailwind / JR tokens`

Volt is the pattern (thin adapters), not a dumped unprefixed catalog.

### App Shell (Navbar / Footer)

- Restyle onto **pilot tokens** (`--color-jr-*`, Inter ramp, restrained radius, 1px borders). Prefer deep blueprint primary for the bar if brand continuity is required, but implement with JR / PrimeVue — not `.navbar-modern`, Bootstrap `navbar`, or `#2c3e50` footer as the long-term contract.
- Replace Bootstrap collapse / dropdown / buttons with PrimeVue (or thin JR wrappers): `Menubar` / `Menu` / `Button` / `Avatar` as appropriate; no `.btn`, `.dropdown-menu`, `.navbar-toggler` as the authored surface.
- Footer: same JR surface / muted / border vocabulary as `.jr-pilot` pages; no incumbent slate card that diverges from the pilot neutrals unless product explicitly keeps a dark marketing strip (document that exception if kept).
- Shell may use a root class such as `.jr-shell` (or wrap chrome in `.jr-pilot`-compatible tokens) so Tailwind utilities and JR CSS apply without waiting for a full Preflight cutover.
- Impeccable / design-reviewer **must** critique Navbar and Footer against this Target State — do not ignore shell files as “out of pilot scope.”

## Product character (Pilot)

Construction Operations / ERP Admin. Operational, technical, fast, professional. Mobile-first field-and-office work.

- Not a marketing landing, not a generic AI dashboard, not a stack of decorative cards
- Restrained color: neutrals + one action blue
- Inter / system sans
- Tight operational density
- Subtle 1px borders over heavy card shadows

## Colors (Pilot)

| Token                  | Value     | Use                                                                                                    |
| ---------------------- | --------- | ------------------------------------------------------------------------------------------------------ |
| Page (`jr-page`)       | `#f3f4f6` | Cool gray work surface. Replaces the incumbent card-in-card mist gradient **inside** `.jr-pilot` only. |
| Surface (`jr-surface`) | `#ffffff` | Panels, inputs, tables                                                                                 |
| Surface muted          | `#f9fafb` | Subtle well / hover wash                                                                               |
| Border                 | `#e5e7eb` | Dividers, field borders, table outline                                                                 |
| Hover border           | `#d1d5db` | Field hover                                                                                            |
| Text (`jr-text`)       | `#111827` | Primary copy                                                                                           |
| Muted                  | `#4b5563` | Hints, secondary copy                                                                                  |
| Primary                | `#2563eb` | Actions, focus                                                                                         |
| Primary hover          | `#1d4ed8` | Action hover                                                                                           |
| Success                | `#16a34a` | Confirm / valid                                                                                        |
| Danger                 | `#dc2626` | Errors / destructive                                                                                   |
| Warning                | `#d97706` | Caution (unambiguous; not the Bootstrap amber token)                                                   |
| Info                   | `#0284c7` | Informational (unambiguous; not Bootstrap cyan)                                                        |

**The Status Semantics Rule still applies.** Do not mute success / danger / warning / info to match branding.

## Typography (Pilot)

Same family as the incumbent: Inter with system-ui fallback. Denser operational ramp:

| Role          | Size                                    | Weight            |
| ------------- | --------------------------------------- | ----------------- |
| Page title    | `1.25–1.375rem` (canonical `1.3125rem`) | 600               |
| Section title | `0.9375rem`                             | 600               |
| Body          | `0.9375rem`                             | 400               |
| Label         | `0.8125rem`                             | 600, left-aligned |
| Hint / error  | `0.75rem`                               | 400 / 600         |
| Table         | `0.875rem`                              | 600 headers       |

Page titles are **left-aligned** and must not use the incumbent centered `2rem` marketing-scale `.main-title`.

`App.vue` still sets `text-align: center` on `.app-container`. `JRPage` / `.jr-pilot` must reset `text-align: left`.

## Layout (Pilot)

- Full-width work surface. No outer Bootstrap card wrapper.
- Horizontal padding ~16px mobile / 24px desktop.
- Page header: title + optional description + actions. Stack on small screens, row on desktop. Actions stay reachable (no overflow-hidden toolbars).
- Sections: title + body with a 1px divider. No nested cards.
- Controls: ~40–44px min-height on mobile (touch), slightly denser on desktop.

## Radius (Pilot)

Restrained. Not the incumbent `1.25rem` mega-cards.

- Controls (inputs, selects, dropdown panels, buttons, badges): `0` — rectangular, no corner rounding
- Dialogs (`JRDialog` / PrimeVue `p-dialog`): `0` — rectangular, no corner rounding. Canonical: product images overlay (`ProductBrandImages` in `JRDialog`, and the same dialog on Product List). Header, content and footer stay square too (`--p-dialog-border-radius: 0`). Do not use `--radius-jr-panel` (`0.75rem`) on dialogs.
- Panels / tables / drawers: `0.75rem`

## Elevation (Pilot)

Prefer a 1px `#e5e7eb` border. Shadow only for overlays (drawer, dialog, select panel): `0 16px 40px rgba(15, 23, 42, 0.16)`.

## Coexistence rules

- **Do not** enable Tailwind Preflight until Bootstrap remnants are gone from the shell and remaining features (or Preflight is scoped safely). It would reset Bootstrap globally.
- Tailwind utilities are nested under `.jr-pilot` (and shell equivalents such as `.jr-shell` when introduced) so classes such as `p-4` do not override Bootstrap `p-4` on **unmigrated** screens. Tailwind v4 cannot use `@import ".../utilities.css" important(.jr-pilot)` — that is parsed as a media query and emits invalid CSS.
- Import `jr-design-system.css` after `skin-modern.css` while skin-modern still loads; as Navbar / Footer migrate, **stop depending on** `.navbar-modern` / skin-modern shell rules for those surfaces.
- PrimeVue styled mode uses the JobRhythm Aura preset; dark mode is disabled (`darkModeSelector: 'none'`).
- Cascade layer order is pinned in one place: `theme, base, primevue, components, utilities` (`jr-design-system.css` and PrimeVue `cssLayer.order`). JR component rules therefore win over PrimeVue; Tailwind utilities win last. Do not declare a second `@layer` list that omits `components` or `primevue`.
- Bootstrap `h1`–`h6` and `a` are unlayered. Pilot heading type (`.jr-page-header__title`, `.jr-section__title`) and overlay menu `text-decoration` live **outside** `@layer components` so they can beat those element selectors. Do not move them back into the layer.
- PrimeVue overlays (drawer, select, datepicker, menus) portal to `body`. Put `.jr-pilot` / `.jr-shell` / `.jr-overlay` on overlay roots when Tailwind utilities must apply inside them.
- Do not wrap **unmigrated** feature pages in `.jr-pilot`. Do migrate App Shell onto JR / PrimeVue; leaving Bootstrap navbar/footer “forever” is out of contract.

## Shared primitives (Pilot)

Consume from `@/ui` (alias `@ui` also resolves). Wrap each migrated screen in `JRPage`:

- `JRPage` — root `.jr-pilot` work surface
- `JRPageHeader` — title, description, actions
- `JRSection` — titled block with divider
- `JRField` — label, hint, required, error
- `JRButton`, `JRInput`, `JRSelect`, `JRSelectAddon`, `JRCheckbox`, `JRDatePicker`, `JRTextarea`
- `JRBadge`, `JRDataTable`, `JRDrawer`, `JRDialog`, `JRToolbar`, `JREmptyState`, `JRTooltip`
- `JRRowActions` — In **lists / embedded tables**: ghost **icon + label** on desktop; overflow menu on mobile (same icons). Never icon-only on desktop. Duplicate uses `CopyIcon` (`app/vuefrontend/src/ui/CopyIcon.vue`). In a **`p-drawer`**: solid `p-button p-component jr-button`, **label only** (no icon); Delete is filled danger. Page, form, drawer and dialog actions (`JRButton`: Save, Cancel, Done, Update, Upload, Delete) stay label-only `jr-button`. FileUpload basic choose buttons get `class: 'p-button p-component jr-button'`.

Primitives are presentational. No axios. No product business logic.

Implementer rulebook: `app/vuefrontend/src/ui/README.md` (forms in § 4). List detail: `app/vuefrontend/src/ui/LIST_VIEWS.md`. `FORMS.md` is an alias to the README forms chapter.

## Forms (Pilot)

Reference: Product Form (`ProductForm.vue`). Operational forms teach through the field, not through hover.

**Persistent hint under the control** is the default channel for a rule that changes money, identity, stock, or purchasing. Use `JRField` `hint` (0.75rem, muted). Put that hint in `aria-describedby` together with the error id.

**Tooltip is extra, never the only copy.** Do not put a `JRTooltip` that repeats the hint word-for-word. Do not rely on `(i)` hover for Casey (phone) or Sam (screen reader).

**Not every field gets a hint.** Name, Model, Category, and other labels that already state the ask stay silent. Cap hints at the 3–4 ticket-generating rules on the screen (example: SKU uniqueness, default purchasing brand, Quantity vs Serialized, reorder unit).

**Say each idea once.** A section title does not need a lede that restates it. A nested “Default for purchasing” label does not need the same sentence already shown on Brands.

**Contextual consequence** (what happens after a choice, not how to fill the field) uses PrimeVue `Message` (`import Message from 'primevue/message'`), `severity="info"`, `:closable="false"`, JR info tokens — not a raw `<p>` well and not a SweetAlert. Example: Serialized creates one tracked unit per purchased quantity. Keep it collapsed until that choice is active.

**Checkboxes:** visible label with a clear gap (`column-gap` ~0.85rem) in the form and in drawers. Table flag columns may use the header as the name.

Desktop (≥1024px): Identity / Classification / Inventory-style sections use **three columns**. Labels stay on one line with any help icon; a tooltip trigger must not push the input below its neighbors.

**Fields are rectangular.** `JRInput`, `JRSelect`, `JRDatePicker`, `JRTextarea` and their PrimeVue dropdown/datepicker panels use `--radius-jr-control` (`0`). Do not reintroduce `0.5rem` (or any) corner radius on form controls in later modules.

**Money / decimal amounts** (prices, SqFt rates, travel amounts, piece-work Trim/Rough): use PrimeVue `InputNumber` with normal `JRField` labels (not currency/`IftaLabel` unless the brief asks for it):

```vue
<JRField v-slot="{ describedby, invalid }" label="Trim" inputId="…">
  <InputNumber
    v-model="value"
    inputId="…"
    mode="decimal"
    locale="en-US"
    :minFractionDigits="2"
    :maxFractionDigits="2"
    :min="0"
    fluid
    :invalid="invalid"
    :inputProps="describedby ? { 'aria-describedby': describedby } : undefined"
  />
</JRField>
```

Empty / null coerces to **`0.00`** on edit and save (Django `DecimalField` stores `0.00`). Do not use plain `<input type="number">` or `JRInput type="text"` for money.

**Focus is a single line.** On text fields, selects, datepickers and number inputs the focus state is only the 1px primary border (`#2563eb`). No outline ring, no offset halo, no box-shadow. Icon buttons and checkboxes may keep a 2px offset outline (they have no field border to recolor).

## Do's and Don'ts (Pilot)

### Do

- **Do** wrap migrated feature screens in `JRPage` / `.jr-pilot`.
- **Do** migrate Navbar / Footer onto pilot tokens and PrimeVue (JR shell / thin adapters); treat App Shell as part of the frontend upgrade, not a permanent Bootstrap island.
- **Do** use JR primitives instead of one-off PrimeVue markup in features; for shell menus/buttons, prefer JR wrappers or a documented PrimeVue pattern over Bootstrap classes.
- **Do** keep labels left, 0.8125rem, weight 600.
- **Do** keep status colors unambiguous.
- **Do** put operational field help under the control (`JRField` hint + `aria-describedby`), not in a hover-only tooltip.
- **Do** use PrimeVue `Message` (info, not closable) for a consequence that appears after a choice.
- **Do** keep form fields and select/datepicker overlays rectangular (`--radius-jr-control: 0`).
- **Do** use `InputNumber` `mode="decimal"` `locale="en-US"` with 2 fraction digits for money/amount fields; coerce empty to `0.00`.
- **Do** keep `JRDialog` / `p-dialog` rectangular (`border-radius: 0`), like the product images dialog.
- **Do** use a single primary border for field focus — never a double ring.
- **Do** use `JRButton` (`p-button p-component jr-button`) in forms, drawers and dialogs; Delete is filled danger, label-only. `JRRowActions` in a drawer is the same solid treatment, no icons.
- **Do** let Impeccable and `jobrhythm-design-reviewer` score Navbar / Footer against this Target State (no “shell is out of scope” waiver).

### Don't

- **Don't** enable Tailwind Preflight or migrate the build to Vite while Bootstrap still owns unmigrated screens — unless Preflight is proven safe.
- **Don't** keep Navbar / Footer on Bootstrap / `skin-modern` as the target; do not leave Bootstrap collapse/dropdown/btn chrome as intentional long-term shell.
- **Don't** nest Bootstrap `.card` / `.card-modern` inside `JRPage` as an outer chrome.
- **Don't** use the incumbent centered 2rem title or 1.25rem mega-card radius on pilot screens.
- **Don't** hint every field or duplicate the same sentence in hint and tooltip.
- **Don't** teach a commercial or stock rule only with `JRTooltip` / `(i)`.
- **Don't** round JR inputs, selects, or dropdown panels.
- **Don't** round `JRDialog` / `p-dialog` (header, content, or footer). Canonical: product images overlay. Never apply `--radius-jr-panel` to dialogs.
- **Don't** stack outline + border (or a focus shadow) on the same field.
- **Don't** use ghost icon+label `JRRowActions` inside a drawer, or a text-link Delete.
- **Don't** add detector ignores that exempt Navbar / Footer from pilot color/type/radius rules “because shell is Bootstrap.”
