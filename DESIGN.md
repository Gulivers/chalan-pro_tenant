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
  jr-control: "0.5rem"
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

> **Status:** Target design contract for the Products Pilot and later migrated modules.
> **Does not describe the live global UI.** Everything above this heading remains the **CURRENT STATE** (Bootstrap 5 + `skin-modern.css`). Until a screen is wrapped in `JRPage` / `.jr-pilot` and consumes JR primitives, the current-state rules still apply.
>
> App shell (Navbar / Footer) stays on the incumbent Bootstrap / skin-modern system for this increment.

## Scope of this increment

Pilot increment:

- Vue CLI 5 (Webpack) + Tailwind CSS 4 + PrimeVue styled mode
- JobRhythm semantic tokens and JR primitives under `app/vuefrontend/src/ui/`
- Coexistence: Bootstrap + skin-modern remain the default everywhere outside `.jr-pilot`
- **In this increment:** Product Form + Product List wrapped in `JRPage` / `.jr-pilot`
- **Not in this increment:** App Shell redesign, Vite, Tailwind Preflight, remaining inventory modules

Architecture:

`feature view → JR primitive → PrimeVue (styled) → Tailwind tokens`

Volt is the pattern (thin adapters), not a dumped unprefixed catalog.

## Product character (Pilot)

Construction Operations / ERP Admin. Operational, technical, fast, professional. Mobile-first field-and-office work.

- Not a marketing landing, not a generic AI dashboard, not a stack of decorative cards
- Restrained color: neutrals + one action blue
- Inter / system sans
- Tight operational density
- Subtle 1px borders over heavy card shadows

## Colors (Pilot)

| Token | Value | Use |
|---|---|---|
| Page (`jr-page`) | `#f3f4f6` | Cool gray work surface. Replaces the incumbent card-in-card mist gradient **inside** `.jr-pilot` only. |
| Surface (`jr-surface`) | `#ffffff` | Panels, inputs, tables |
| Surface muted | `#f9fafb` | Subtle well / hover wash |
| Border | `#e5e7eb` | Dividers, field borders, table outline |
| Hover border | `#d1d5db` | Field hover |
| Text (`jr-text`) | `#111827` | Primary copy |
| Muted | `#4b5563` | Hints, secondary copy |
| Primary | `#2563eb` | Actions, focus |
| Primary hover | `#1d4ed8` | Action hover |
| Success | `#16a34a` | Confirm / valid |
| Danger | `#dc2626` | Errors / destructive |
| Warning | `#d97706` | Caution (unambiguous; not the Bootstrap amber token) |
| Info | `#0284c7` | Informational (unambiguous; not Bootstrap cyan) |

**The Status Semantics Rule still applies.** Do not mute success / danger / warning / info to match branding.

## Typography (Pilot)

Same family as the incumbent: Inter with system-ui fallback. Denser operational ramp:

| Role | Size | Weight |
|---|---|---|
| Page title | `1.25–1.375rem` (canonical `1.3125rem`) | 600 |
| Section title | `0.9375rem` | 600 |
| Body | `0.9375rem` | 400 |
| Label | `0.8125rem` | 600, left-aligned |
| Hint / error | `0.75rem` | 400 / 600 |
| Table | `0.875rem` | 600 headers |

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

- Controls: `0.5rem`
- Panels / tables / drawers: `0.75rem`

## Elevation (Pilot)

Prefer a 1px `#e5e7eb` border. Shadow only for overlays (drawer, dialog, select panel): `0 16px 40px rgba(15, 23, 42, 0.16)`.

## Coexistence rules

- **Do not** enable Tailwind Preflight. It would reset Bootstrap globally.
- Tailwind utilities are nested under `.jr-pilot` (equivalent of selector `important`) so classes such as `p-4` do not override Bootstrap `p-4` outside migrated screens. Tailwind v4 cannot use `@import ".../utilities.css" important(.jr-pilot)` — that is parsed as a media query and emits invalid CSS.
- Import `jr-design-system.css` after `skin-modern.css`.
- PrimeVue styled mode uses the JobRhythm Aura preset; dark mode is disabled (`darkModeSelector: 'none'`).
- PrimeVue overlays (drawer, select, datepicker) portal to `body`. Put `.jr-pilot` on overlay roots when Tailwind utilities must apply inside them.
- Do not wrap non-pilot pages in `.jr-pilot`.

## Shared primitives (Pilot)

Consume from `@/ui` (alias `@ui` also resolves). Wrap each migrated screen in `JRPage`:

- `JRPage` — root `.jr-pilot` work surface
- `JRPageHeader` — title, description, actions
- `JRSection` — titled block with divider
- `JRField` — label, hint, required, error
- `JRButton`, `JRInput`, `JRSelect`, `JRSelectAddon`, `JRCheckbox`, `JRDatePicker`
- `JRBadge`, `JRDataTable`, `JRDrawer`, `JRToolbar`, `JREmptyState`
- `JRRowActions` — View/Edit/Delete (or equivalent) as text buttons on desktop; overflow menu on mobile

Primitives are presentational. No axios. No product business logic.

## Do's and Don'ts (Pilot)

### Do

- **Do** wrap only migrated screens in `JRPage` / `.jr-pilot`.
- **Do** use JR primitives instead of one-off PrimeVue markup in features.
- **Do** keep labels left, 0.8125rem, weight 600.
- **Do** keep status colors unambiguous.

### Don't

- **Don't** enable Tailwind Preflight or migrate the build to Vite in this increment.
- **Don't** restyle Navbar / Footer onto the pilot tokens yet.
- **Don't** nest Bootstrap `.card` / `.card-modern` inside `JRPage` as an outer chrome.
- **Don't** use the incumbent centered 2rem title or 1.25rem mega-card radius on pilot screens.
