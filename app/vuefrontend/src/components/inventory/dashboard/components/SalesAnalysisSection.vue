<template>
  <JRSection title="Sales">
    <template #actions>
      <div class="jr-dash-period">
        <JRField label="Period" inputId="dash-sales-period">
          <JRSelect
            inputId="dash-sales-period"
            v-model="selectedPeriod"
            :options="periodOptions"
            optionLabel="label"
            optionValue="value"
            @update:modelValue="onPeriodChange"
          />
        </JRField>
      </div>
    </template>

    <SalesMetricsCards
      :metrics="resolvedMetrics"
      :period="selectedPeriod"
      :loading="loading"
    />

    <div class="jr-dash-chart">
      <TopSellingChart
        :products="salesData.topSellingProducts"
        :period="selectedPeriod"
        :loading="loading"
        @refresh="onRefreshSales"
      />
    </div>
  </JRSection>
</template>

<script>
import { JRSection, JRSelect, JRField } from '@ui';
import TopSellingChart from './TopSellingChart.vue';
import SalesMetricsCards from './SalesMetricsCards.vue';

export default {
  name: 'SalesAnalysisSection',
  components: {
    JRSection,
    JRSelect,
    JRField,
    TopSellingChart,
    SalesMetricsCards,
  },
  props: {
    salesData: {
      type: Object,
      default: () => ({
        topSellingProducts: [],
        metrics: {},
      }),
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    resolvedMetrics() {
      const metrics = this.salesData?.metrics || {};
      const top = Array.isArray(this.salesData?.topSellingProducts)
        ? this.salesData.topSellingProducts[0]
        : null;
      return {
        ...metrics,
        top_product_name: metrics.top_product_name || top?.name || '',
        top_product_qty: metrics.top_product_qty ?? top?.quantity_sold ?? 0,
      };
    },
  },
  data() {
    return {
      selectedPeriod: 30,
      periodOptions: [
        { label: 'Last 30 days', value: 30 },
        { label: 'Last 60 days', value: 60 },
        { label: 'Last 90 days', value: 90 },
        { label: 'Last year', value: 365 },
      ],
    };
  },
  methods: {
    onPeriodChange(value) {
      const days = Number(value ?? this.selectedPeriod);
      this.$emit('period-changed', Number.isFinite(days) && days > 0 ? days : 30);
    },
    onRefreshSales() {
      this.$emit('refresh-sales');
    },
  },
};
</script>

<style scoped>
.jr-dash-period {
  min-width: 10rem;
  max-width: 14rem;
}

.jr-dash-chart {
  margin-top: 1rem;
  border-top: 1px solid var(--color-jr-border);
  padding-top: 0.85rem;
}

@media (max-width: 575.98px) {
  .jr-dash-period {
    width: 100%;
    max-width: none;
  }
}
</style>
