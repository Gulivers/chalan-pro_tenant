<template>
  <Badge :value="value" :severity="severity">
    <slot />
  </Badge>
</template>

<script>
import Badge from 'primevue/badge';

export default {
  name: 'JRBadge',
  components: { Badge },
  props: {
    value: {
      type: [String, Number],
      default: null,
    },
    severity: {
      type: String,
      default: 'secondary',
      validator: (value) => ['success', 'secondary', 'info', 'danger'].includes(value),
    },
  },
};
</script>
