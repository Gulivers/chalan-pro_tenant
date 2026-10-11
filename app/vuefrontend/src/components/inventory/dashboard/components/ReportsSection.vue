<template>
  <JRSection title="Advanced Reports">
    <div class="jr-dash-panel">
      <h3 class="jr-dash-panel__title">Product Movements Report</h3>
      <ProductMovementsReport @export-requested="onExportRequested" />
    </div>

    <div v-if="false" class="jr-dash-panel">
      <h3 class="jr-dash-panel__title">Additional Reports</h3>
      <AdditionalReportsGrid @report-requested="onReportRequested" />
    </div>
  </JRSection>
</template>

<script>
import { JRSection } from '@ui';
import ProductMovementsReport from './ProductMovementsReport.vue';
import AdditionalReportsGrid from './AdditionalReportsGrid.vue';

export default {
  name: 'ReportsSection',
  components: {
    JRSection,
    ProductMovementsReport,
    AdditionalReportsGrid,
  },
  props: {},
  methods: {
    onFilterChanged(filters) {
      this.$emit('filter-changed', filters);
    },
    onExportRequested(exportType) {
      this.$emit('export-requested', exportType);
    },
    onReportRequested(reportType) {
      this.$emit('report-requested', reportType);
    },
  },
};
</script>

<style scoped>
.jr-dash-panel {
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  padding: 1rem 1.1rem;
  margin-bottom: 0.75rem;
}

.jr-dash-panel:last-child {
  margin-bottom: 0;
}

.jr-dash-panel__title {
  margin: 0 0 0.85rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-text);
}
</style>
