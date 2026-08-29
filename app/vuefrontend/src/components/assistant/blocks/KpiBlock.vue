<template>
  <div class="assistant-kpi-block">
    <div class="assistant-kpi-title text-muted small">{{ block.title || 'Metric' }}</div>
    <div class="assistant-kpi-value">{{ formattedValue }}</div>
    <div v-if="block.subtitle" class="assistant-kpi-subtitle text-muted small">
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
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 0.375rem;
  background: #f8f9fa;
}
.assistant-kpi-title {
  font-weight: 600;
  margin-bottom: 0.15rem;
}
.assistant-kpi-value {
  font-size: 1.35rem;
  font-weight: 700;
  color: #212529;
  line-height: 1.2;
}
.assistant-kpi-subtitle {
  margin-top: 0.2rem;
}
</style>
