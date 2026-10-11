<template>
  <section class="jr-section">
    <div v-if="title || $slots.title || $slots.actions" class="jr-section__header">
      <h2 class="jr-section__title">
        <slot name="title">{{ title }}</slot>
      </h2>
      <div v-if="$slots.actions">
        <slot name="actions" />
      </div>
    </div>
    <div class="jr-section__body">
      <slot />
    </div>
  </section>
</template>

<script>
export default {
  name: 'JRSection',
  props: {
    title: {
      type: String,
      default: '',
    },
  },
};
</script>
