# JobRhythm UI (Products Pilot)

Shared primitives for screens migrated off Bootstrap / `skin-modern`.

**List Views:** see [LIST_VIEWS.md](./LIST_VIEWS.md) — tokens, badges, toolbar, table, and mobile rules for the Products pilot. Use that contract when migrating another list.

Architecture: `feature → JR primitive → PrimeVue (styled) → Tailwind tokens`.

`app/docs/ai-guidelines.md` is **obsolete** as a visual guide for the frontend upgrade (Bootstrap / `b-table` / `btn-success`). New list work follows this README + [LIST_VIEWS.md](./LIST_VIEWS.md).

## Colors (Products List)

Source: `ProductListView.vue` + tokens in `jr-design-system.css`. Use `var(--color-jr-*)` — no raw hex in the view.

### Page

| Token | Value | In the list |
|---|---|---|
| `--color-jr-page` | `#f3f4f6` | Page background |
| `--color-jr-surface` | `#ffffff` | Table, inputs, drawer |
| `--color-jr-surface-muted` | `#f9fafb` | Table header, striped row, thumb placeholder |
| `--color-jr-border` | `#e5e7eb` | Table outline, row dividers |
| `--color-jr-hover-border` | `#d1d5db` | Thumbnail hover |
| `--color-jr-text` | `#111827` | Title, product name, column headers |
| `--color-jr-muted` | `#4b5563` | SKU, category, loading, Total / Inactive chips |

### Actions

| Token | Value | In the list |
|---|---|---|
| `--color-jr-primary` | `#2563eb` | **+ New Product**, **Edit** |
| `--color-jr-primary-hover` | `#1d4ed8` | Primary hover / focus ring |
| `--color-jr-success` | `#16a34a` | **View** (text button) |
| `--color-jr-danger` | `#dc2626` | **Delete** |
| Ghost toolbar (Refresh, Bulk Excel) | muted text | Not action blue |

### Badges (light background)

Pastel fill (~14% mix of the fill on white) + dark same-hue text. No border. Radius `--radius-jr-control` (`0.5rem`), not a pill.

| Severity | Chip text | Chip background | Used for |
|---|---|---|---|
| `success` | `#166534` (`--color-jr-success-text`) | `--color-jr-success-subtle` | Active, “N Active” |
| `info` | `#1e40af` (`--color-jr-info-text`) | `--color-jr-info-subtle` | Serial |
| `secondary` | `#4b5563` | `--color-jr-surface-muted` / gray 100 | Inactive, Total, Qty |
| `danger` | `#991b1b` (`--color-jr-danger-text`) | `--color-jr-danger-subtle` | Error / cancel states |
| `warn` | `#92400e` (`--color-jr-warning-text`) | `--color-jr-warning-subtle` | Pending / caution |

Do not use fill `#16a34a` / `#0284c7` as badge label color (contrast fails at 0.75rem on white). View uses the brighter fill; Active uses the forest-green text.

## Isolation

- Wrap **only** migrated screens in `JRPage`. That root adds `.jr-pilot`.
- Tailwind utilities are generated as `.jr-pilot .utility` (utilities nested under `.jr-pilot`). Bootstrap `p-4` etc. keep winning outside `.jr-pilot`.
- Tailwind Preflight is **not** enabled.
- Navbar / Footer stay on the incumbent Bootstrap shell.

```vue
<template>
  <JRPage>
    <JRPageHeader title="Products" description="Catalog and pricing">
      <template #actions>
        <JRButton>Add product</JRButton>
      </template>
    </JRPageHeader>
    <JRToolbar>
      <template #start>
        <JRInput type="search" placeholder="Search…" />
      </template>
      <template #stats>24 products</template>
      <template #actions>
        <JRButton variant="secondary" size="sm">Export</JRButton>
      </template>
    </JRToolbar>
    <JRSection title="Details">
      <JRField label="Name" required error="">
        <JRInput v-model="name" />
      </JRField>
    </JRSection>
  </JRPage>
</template>

<script>
import { JRPage, JRPageHeader, JRToolbar, JRSection, JRField, JRInput, JRButton } from '@/ui';
// @ui also resolves to this folder

export default {
  components: { JRPage, JRPageHeader, JRToolbar, JRSection, JRField, JRInput, JRButton },
};
</script>
```

## Imports

```js
import { JRPage, JRSelectAddon, JRDataTable } from '@/ui';
import Column from 'primevue/column';
```

`JRDataTable` accepts PrimeVue `Column` (and other column nodes) in the default slot.

## Overlay note

PrimeVue drawers, selects, and datepickers portal to `document.body`. `JRDrawer` adds `.jr-pilot` on the overlay so Tailwind utilities still apply. Select / datepicker panels are styled by the JobRhythm Aura preset, not by Tailwind utilities.
