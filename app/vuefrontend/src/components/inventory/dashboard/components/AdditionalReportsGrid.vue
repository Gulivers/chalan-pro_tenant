<template>
  <div class="additional-reports-grid">
    <div
      v-for="report in reports"
      :key="report.type"
      class="jr-report-card"
      @click="requestReport(report.type)"
    >
      <h3 class="jr-report-card__title">{{ report.title }}</h3>
      <p class="jr-report-card__desc">{{ report.description }}</p>
      <JRButton
        variant="secondary"
        size="sm"
        :disabled="loading"
        @click.stop="requestReport(report.type)"
      >
        Open report
      </JRButton>
    </div>

    <div v-if="false" class="jr-report-download-all">
      <JRButton variant="primary" :disabled="loading" @click="downloadAllReports">
        Download all reports
      </JRButton>
      <p class="jr-report-card__desc">
        Download a ZIP with every available report
      </p>
    </div>
  </div>
</template>

<script>
import { JRButton } from '@ui';

export default {
  name: 'AdditionalReportsGrid',
  components: { JRButton },
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      reports: [
        {
          type: 'stock-by-category',
          title: 'Stock by category',
          description: 'Inventory grouped by product category',
        },
        {
          type: 'inventory-turnover',
          title: 'Inventory turnover',
          description: 'How quickly products move through stock',
        },
        {
          type: 'abc-analysis',
          title: 'ABC analysis',
          description: 'Classify products by value and importance',
        },
        {
          type: 'inventory-kpis',
          title: 'Inventory KPIs',
          description: 'Key performance indicators for inventory',
        },
        {
          type: 'slow-moving-items',
          title: 'Slow movers',
          description: 'Products with low movement and turnover',
        },
        {
          type: 'fast-moving-items',
          title: 'Fast movers',
          description: 'Products with high movement and turnover',
        },
        {
          type: 'obsolete-items',
          title: 'Obsolete items',
          description: 'Products with no movement for long periods',
        },
        {
          type: 'inventory-valuation',
          title: 'Inventory valuation',
          description: 'Full valuation of current inventory',
        },
      ],
    };
  },
  methods: {
    requestReport(reportType) {
      this.$emit('report-requested', reportType);
    },
    downloadAllReports() {
      this.$emit('report-requested', 'all-reports');
    },
  },
};
</script>

<style scoped>
.additional-reports-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.jr-report-card {
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface);
  padding: 1rem;
  cursor: pointer;
}

.jr-report-card__title {
  margin: 0 0 0.35rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-report-card__desc {
  margin: 0 0 0.85rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
  line-height: 1.4;
}

.jr-report-download-all {
  grid-column: 1 / -1;
  border: 1px dashed var(--color-jr-border);
  padding: 1.25rem;
  text-align: left;
}

@media (max-width: 575.98px) {
  .additional-reports-grid {
    grid-template-columns: 1fr;
  }
}
</style>
