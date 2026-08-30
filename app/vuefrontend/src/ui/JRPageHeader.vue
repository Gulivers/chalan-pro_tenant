<template>
  <header class="jr-page-header">
    <div class="jr-page-header__text">
      <h1 class="jr-page-header__title">{{ title }}</h1>
      <p v-if="description" class="jr-page-header__desc">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="jr-page-header__actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script>
export default {
  name: 'JRPageHeader',
  props: {
    title: {
      type: String,
      required: true,
    },
    description: {
      type: String,
      default: '',
    },
  },
};
</script>
