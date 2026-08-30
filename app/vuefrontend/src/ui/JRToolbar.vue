<template>
  <div class="jr-toolbar">
    <div v-if="$slots.stats" class="jr-toolbar__stats">
      <slot name="stats" />
    </div>
    <div v-if="$slots.actions || $slots.default" class="jr-toolbar__actions">
      <slot name="actions" />
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  name: 'JRToolbar',
};
</script>
