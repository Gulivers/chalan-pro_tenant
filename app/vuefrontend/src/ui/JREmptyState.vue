<template>
  <div class="jr-empty-state" role="status">
    <p v-if="title" class="jr-empty-state__title">{{ title }}</p>
    <p v-if="description" class="jr-empty-state__desc">{{ description }}</p>
    <div v-if="$slots.default" class="jr-empty-state__actions">
      <slot />
    </div>
  </div>
</template>

<script>
export default {
  name: 'JREmptyState',
  props: {
    title: {
      type: String,
      default: '',
    },
    description: {
      type: String,
      default: '',
    },
  },
};
</script>
