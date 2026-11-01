<template>
  <div class="assistant-kpi-block">
    <div class="assistant-kpi-title text-sm text-jr-muted">{{ block.title || 'Metric' }}</div>
    <div class="assistant-kpi-value">{{ formattedValue }}</div>
    <div v-if="block.subtitle" class="assistant-kpi-subtitle text-sm text-jr-muted">
      {{ block.subtitle }}
    </div>
  </div>
</template>

<script>
import { formatAssistantValue } from '../formatValue';

export default {
  name: 'KpiBlock',
  props: {
    block: {
      type: Object,
      required: true,
    },
  },
  computed: {
    formattedValue() {
      return formatAssistantValue(
        this.block?.value,
        this.block?.format || 'text',
        this.block?.currency || 'USD'
      );
    },
  },
};
</script>

<style scoped>
.assistant-kpi-block {
  text-align: left;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface-muted);
}
.assistant-kpi-title {
  font-weight: 600;
  margin-bottom: 0.15rem;
}
.assistant-kpi-value {
  font-size: 1.3125rem;
  font-weight: 600;
  color: var(--color-jr-text);
  line-height: 1.2;
}
.assistant-kpi-subtitle {
  margin-top: 0.2rem;
}
</style>
