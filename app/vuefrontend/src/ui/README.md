# JobRhythm UI (Products Pilot)

Shared primitives for screens migrated off Bootstrap / `skin-modern`.

Architecture: `feature → JR primitive → PrimeVue (styled) → Tailwind tokens`.

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
