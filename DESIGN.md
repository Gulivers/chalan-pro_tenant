---
name: JobRhythm Admin
description: Operational Vue + PrimeVue admin for residential trade contractors — JR design system, data-dense, Inter-forward, rectangular controls.
colors:
  primary: "#2563eb"
  primary-hover: "#1d4ed8"
  primary-active: "#1e40af"
  primary-950: "#172554"
  shell-topbar-start: "#1e3a8a"
  shell-topbar-end: "#1e40af"
  page: "#f3f4f6"
  surface: "#ffffff"
  surface-muted: "#f9fafb"
  border: "#e5e7eb"
  hover-border: "#d1d5db"
  text: "#111827"
  muted: "#4b5563"
  success: "#16a34a"
  success-text: "#166534"
  danger: "#dc2626"
  danger-text: "#991b1b"
  warning: "#d97706"
  warning-text: "#92400e"
  info: "#0284c7"
  info-text: "#1e40af"
typography:
  body:
    fontFamily: "Inter, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.45
  title:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "1.3125rem"
    fontWeight: 600
    lineHeight: 1.25
  section:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 600
    lineHeight: 1.3
  label:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1.3
  hint:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 400
    lineHeight: 1.4
  table:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.4
rounded:
  control: "0"
  panel: "0.75rem"
  badge: "0.5rem"
spacing:
  xs: "0.35rem"
  sm: "0.5rem"
  md: "0.75rem"
  lg: "1rem"
  xl: "1.25rem"
  page: "1rem"
  page-md: "1.25rem 1.5rem"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.control}"
    padding: "0.5rem 1rem"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "#ffffff"
    rounded: "{rounded.control}"
    padding: "0.5rem 1rem"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.control}"
    padding: "0.5rem 1rem"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    rounded: "{rounded.control}"
    padding: "0.5rem 0.75rem"
  button-danger:
    backgroundColor: "{colors.danger}"
    textColor: "#ffffff"
    rounded: "{rounded.control}"
    padding: "0.5rem 1rem"
  input-default:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.control}"
    padding: "0.5rem 0.75rem"
  badge-success:
    backgroundColor: "color-mix(in srgb, #16a34a 14%, #ffffff)"
    textColor: "{colors.success-text}"
    rounded: "{rounded.control}"
  navbar:
    backgroundColor: "{colors.shell-topbar-start}"
    textColor: "#ffffff"
---

# Design System: JobRhythm Admin

## Overview

**Creative North Star: "Modern Field Console"**

JobRhythm’s live admin UI is a **Vue 3 + Vite + PrimeVue (styled)** operational console built on the **JR design system**. Migrated screens wrap in `JRPage` (`.jr-pilot`); the app shell uses JR tokens and PrimeVue Sidebar (`jr-shell-nav.css`). Bootstrap is **not** loaded and is not a visual authority.

The reference implementation is the Products pilot: **Product List** (`ProductListView.vue`) and **Product Form** (`ProductForm.vue`). Lists, forms, drawers, dialogs, and badges follow that pattern via primitives in `@/ui` and tokens in `jr-design-system.css` / `JobRhythmPreset`.

**Key Characteristics:**

- Data-dense tables, toolbars, and forms for contractor operations
- One action blue (`#2563eb`); neutrals and clear status semantics
- Rectangular controls (`--radius-jr-control: 0`); panels/tables/drawers use `--radius-jr-panel` (`0.75rem`)
- Flat surfaces; shadow only on overlays (`--shadow-jr-overlay`)
- Architecture: `feature view | App Shell → JR primitive → PrimeVue → JR tokens`
- Implementer rulebooks: `app/vuefrontend/src/ui/README.md`, `LIST_VIEWS.md`

## Colors

Cool operational blues and gray surfaces; status colors stay unambiguous for Active / Inactive / stock / errors.

### Primary

- **Action Blue** (`#2563eb`): primary buttons, links that open View, focus border on fields, caret.
- **Action Blue Hover** (`#1d4ed8`): primary hover / pressed hover.
- **Action Blue Active** (`#1e40af`): active / pressed primary.
- **Ink Deep** (`#172554`): deepest primary ramp (`primary-950`).
- **Shell Blueprint** (`#1e3a8a` → `#1e40af`): topbar gradient.

### Secondary

Omit a second marketing accent. Operational emphasis uses primary, muted text, or status chips — not amber section titles from the retired Bootstrap skin.

### Neutral

- **Page Mist** (`#f3f4f6`): page / shell background.
- **Surface** (`#ffffff`): inputs, table body, drawers, cards-as-panels.
- **Surface Muted** (`#f9fafb`): table headers, striped/hover rows, wells.
- **Border** (`#e5e7eb`) / **Hover Border** (`#d1d5db`): dividers, control outlines, scrollbar thumbs.
- **Text** (`#111827`) / **Muted** (`#4b5563`): body vs hints, meta, secondary actions.

### Semantic

- **Success** fill `#16a34a`, chip text `#166534`, subtle mix 14% + surface.
- **Danger** fill `#dc2626`, chip text `#991b1b`.
- **Warning** fill `#d97706`, chip text `#92400e`.
- **Info** fill `#0284c7`, chip text `#1e40af` (subtle often mixes primary into surface).

**The Light Badge Rule.** Status chips use dark text on pastel backgrounds — never bright fill as chip text at `0.75rem` (fails AA).

**The One Action Blue Rule.** Primary fill is for the main create/submit action and entity View links. Do not paint every control primary.

## Typography

**Display/Title Font:** Inter (with system-ui stack)  
**Body Font:** Inter (with system-ui stack)

**Character:** Practical, left-aligned, medium-weight labels and page titles — optimized for scanning operational data, not marketing display type.

### Hierarchy

- **Title** (600, `1.3125rem`, line-height 1.25): `JRPageHeader` page title, left-aligned.
- **Section** (600, `0.9375rem`): `JRSection` titles above a 1px border divider.
- **Body** (400, `0.9375rem`, line-height 1.45): default `.jr-pilot` text.
- **Table** (600 headers / row name, `0.875rem`): data tables and list row names.
- **Label** (600, `0.8125rem`): `JRField` labels; shell nav density often matches.
- **Hint / Badge / Meta** (400 hint / 600 badge, `0.75rem`): field hints, errors, chips, SKU/meta lines.

### Named Rules

**The Left Title Rule.** Page titles stay left-aligned at `1.3125rem` / 600 — never centered mega titles from older skins.

**The Teach-In-Field Rule.** Operational rules (money, identity, stock, purchasing) live in `JRField` `hint` + `aria-describedby`, not hover-only tooltips.

## Layout

Operational density with a clear vertical stack:

```
JRPage (.jr-pilot)
  JRPageHeader (title + actions)
  JRToolbar (#start search | #stats chips | #actions tools)
  content (JRDataTable desktop / mobile row list)
  overlays (JRDrawer / JRDialog / menus → .jr-overlay)
```

- Page padding: `1rem`; from `768px`: `1.25rem 1.5rem`.
- Forms: Identity / Classification / Inventory-style grids; desktop (≥1024px) often **three columns**.
- Breakpoints in practice: phone &lt;768px (list → cards/rows), tablet 768–1023px, desktop ≥1024px.
- Shell: topbar height `3.5rem`, sidebar width `17rem`, rail `3.25rem` (`jr-shell-nav.css`).
- Spacing rhythm: `0.35` / `0.5` / `0.75` / `1` / `1.25` rem gaps between field, section, and header blocks.

**The No Nested Card Chrome Rule.** Do not wrap JR screens in Bootstrap-style outer cards; the page surface and bordered table/panel are enough.

## Elevation & Depth

Flat by default. Depth is tonal (muted surface vs page) and 1px borders — not card drop shadows.

### Shadow Vocabulary

- **Overlay** (`box-shadow: 0 16px 40px rgba(15, 23, 42, 0.16)` / `--shadow-jr-overlay`): drawers, menus, and floating overlays only.

### Named Rules

**The Flat-By-Default Rule.** Surfaces stay flat at rest. Shadows appear only for portaled overlays.

## Shapes

- **Controls** (inputs, selects, datepickers, buttons, badges, dialogs): sharp rectangle — `--radius-jr-control: 0`.
- **Panels** (data tables, drawers, large wells): soft panel — `--radius-jr-panel: 0.75rem`.
- **Preset badge/paginator** may use `0.5rem` in PrimeVue tokens; JR CSS prefers control radius `0` for chips in the pilot.
- Borders: 1px solid border / hover-border. No pill (`999px`) chips.

**The Rectangular Field Rule.** Form fields and their dropdown/datepicker panels are rectangular. Do not reintroduce `0.5rem` (or any) radius on controls.

**The Dialog Shape Rule.** `JRDialog` / `p-dialog` stay rectangular (`border-radius: 0`), matching product-image style overlays — never panel radius on dialogs.

## Components

Stack: JR primitives (`@/ui`) wrap PrimeVue styled mode with `JobRhythmPreset`. Features should not invent one-off PrimeVue chrome.

### Buttons (`JRButton`)

- **Shape:** rectangular (`0`)
- **Primary:** Action Blue fill, white label — page create / form submit
- **Secondary:** outlined / muted surface
- **Ghost:** text/ghost for Refresh and secondary tools
- **Danger:** filled danger, **label only** (Delete in forms/drawers)
- **Focus:** visible; icon buttons may use 2px offset outline

### Badges / Chips (`JRBadge`)

- **Style:** light background + dark semantic text; no bright fill-as-text
- **Shape:** rectangular (control radius)
- **Use:** Active/Inactive, stock, stats in toolbar (non-interactive)

### Cards / Containers

- Prefer `JRSection`, bordered `JRDataTable`, and drawer panels — not decorative card stacks
- **Panel radius:** `0.75rem` on tables/drawers
- **Border:** 1px `border`
- **Shadow:** none at rest

### Inputs / Fields (`JRField` + `JRInput` / `JRSelect` / `InputNumber`)

- **Style:** white surface, 1px border, rectangular
- **Focus:** single 1px primary border only — no outline ring, no halo, no box-shadow on fields
- **Invalid:** danger border; error text under control
- **Hint:** persistent under control for ticket-generating rules only
- **Money:** PrimeVue `InputNumber` decimal `en-US`, 2 fraction digits; empty → `0.00`
- **Tooltip:** optional extra; never the only channel for a commercial/stock rule

### Navigation (App Shell)

- **Topbar:** blueprint gradient, white/light nav links, account menu (PrimeVue `Menu` + `.jr-overlay`)
- **Sidebar:** PrimeVue Sidebar, surface background, muted labels, active item with primary emphasis
- **Footer:** JR footer with operational flow steps; icons are `markRaw` components (non-reactive)

### Lists (`JRToolbar` + `JRDataTable` + `JRRowActions`)

- Reference: Product List
- Entity name → View link when permitted
- Desktop row actions: ghost **icon + label**; mobile: overflow menu
- Drawer row/actions: solid label-only buttons; Delete filled danger
- Empty states: `JREmptyState` with Refresh / Clear search

### Overlays (`JRDrawer`, `JRDialog`)

- Portaled to body; root gets `.jr-pilot` / `.jr-shell` / `.jr-overlay` so tokens apply
- Prefer JR dialogs over SweetAlert / `window.confirm` on migrated screens

## Do's and Don'ts

### Do

- **Do** wrap migrated feature screens in `JRPage` / `.jr-pilot`.
- **Do** use JR primitives from `@/ui` instead of one-off PrimeVue markup.
- **Do** use `var(--color-jr-*)` — no raw hex in feature views.
- **Do** keep page titles left, `1.3125rem`, weight 600.
- **Do** put operational help under the control (`JRField` hint + `aria-describedby`).
- **Do** use PrimeVue `Message` (info, not closable) for consequences after a choice (e.g. Serialized).
- **Do** keep fields, select/datepicker overlays, and dialogs rectangular (`--radius-jr-control: 0`).
- **Do** use `InputNumber` decimal for money/amounts; coerce empty to `0.00`.
- **Do** use a single primary border for field focus — never a double ring.
- **Do** use light-background badges with dark text for status chips.
- **Do** treat App Shell (Navbar / Footer) as JR/PrimeVue — part of the same system.

### Don't

- **Don't** use Bootstrap (`.card`, `.btn`, `.badge`, `.form-control`, `.visually-hidden`, utility grid classes) inside JR screens or as shell chrome.
- **Don't** treat `skin-modern` / Bootstrap SCSS as the design source of truth — they are retired.
- **Don't** nest decorative cards around `JRPage` content.
- **Don't** use centered mega titles or large card radii from the old skin.
- **Don't** hint every field or duplicate the same sentence in hint and tooltip.
- **Don't** teach a commercial or stock rule only with `JRTooltip` / `(i)`.
- **Don't** round JR inputs, selects, dropdown panels, or dialogs.
- **Don't** apply `--radius-jr-panel` to dialogs.
- **Don't** stack outline + border (or a focus shadow) on the same field.
- **Don't** use ghost icon+label `JRRowActions` inside a drawer, or a text-link Delete there.
- **Don't** enable Tailwind Preflight without a deliberate global reset plan.
- **Don't** invent a second cascade `@layer` order; keep `theme, base, primevue, components, utilities`.
