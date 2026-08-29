<template>
  <div class="assistant-kpi-group">
    <div v-if="block.title" class="assistant-block-title text-muted small mb-2">
      {{ block.title }}
    </div>
    <div class="assistant-kpi-group-grid">
      <KpiBlock
        v-for="(kpi, index) in kpis"
        :key="kpi.id || `kpi-${index}`"
        :block="normalizeKpi(kpi, index)" />
    </div>
  </div>
</template>

<script>
import KpiBlock from './KpiBlock.vue';

export default {
  name: 'KpiGroupBlock',
  components: { KpiBlock },
  props: {
    block: {
      type: Object,
      required: true,
    },
  },
  computed: {
    kpis() {
      const items = this.block?.items || this.block?.kpis || this.block?.children;
      return Array.isArray(items) ? items.filter((item) => item && typeof item === 'object') : [];
    },
  },
  methods: {
    normalizeKpi(kpi, index) {
      return {
        type: 'kpi',
        id: kpi.id || `${this.block.id || 'kpi-group'}-${index}`,
        title: kpi.title,
        value: kpi.value,
        format: kpi.format || 'number',
        currency: kpi.currency,
        subtitle: kpi.subtitle,
      };
    },
  },
};
</script>

<style scoped>
.assistant-kpi-group {
  text-align: left;
}
.assistant-block-title {
  font-weight: 600;
}
.assistant-kpi-group-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.5rem;
}
</style>
