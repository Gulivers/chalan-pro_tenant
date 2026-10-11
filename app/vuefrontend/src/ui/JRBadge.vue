<template>
  <Badge class="jr-badge" :value="value" :severity="primeSeverity">
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
      validator: (value) =>
        ['success', 'secondary', 'info', 'danger', 'warn', 'warning'].includes(value),
    },
  },
  computed: {
    primeSeverity() {
      return this.severity === 'warning' ? 'warn' : this.severity;
    },
  },
};
</script>
