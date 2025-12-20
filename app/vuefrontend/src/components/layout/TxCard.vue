<template>
  <!-- Hereda TODAS las attrs del padre (class, style, id, etc.) -->
  <div class="card" v-bind="$attrs">
    <div v-if="$slots.header" class="card-header d-flex justify-content-between align-items-center">
      <slot name="header" />
    </div>

    <div class="card-body p-4">
      <slot />
    </div>

    <div v-if="$slots.footer" class="card-footer d-flex justify-content-end gap-2">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
// Nada extra: puro layout.
// Tip: no necesitas props; el padre pasa class/style/ids via $attrs.
</script>

<style scoped>
/* Nada obligatorio. Si tu tema dejó transparente las cards,
   puedes forzar visual mínimo descomentando estas dos líneas:

.card { background: var(--bs-body-bg); border: 1px solid var(--bs-border-color); }
*/
</style>