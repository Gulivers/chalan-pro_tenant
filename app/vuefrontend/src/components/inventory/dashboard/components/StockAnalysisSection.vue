<template>
  <JRSection title="Needs attention">
    <p class="jr-dash-lede">
      Products below reorder level — critical and out-of-stock first.
    </p>
    <LowStockTable :products="sortedProducts" :loading="loading" />

    <div
      v-if="lowestStockProducts.length || loading"
      class="jr-dash-chart">
      <LowestStockChart
        :products="lowestStockProducts"
        :loading="loading"
        @refresh="onRefreshStock"
      />
    </div>
  </JRSection>
</template>

<script>
import { JRSection } from '@ui';
import LowStockTable from './LowStockTable.vue';
import LowestStockChart from './LowestStockChart.vue';
import { getStockQty, getStockStatus } from './stockStatus';

const STATUS_ORDER = { critical: 0, out: 1, low: 2, healthy: 3 };

export default {
  name: 'StockAnalysisSection',
  components: {
    JRSection,
    LowStockTable,
    LowestStockChart,
  },
  props: {
    lowStockProducts: {
      type: Array,
      default: () => [],
    },
    lowestStockProducts: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    sortedProducts() {
      return [...this.lowStockProducts].sort((a, b) => {
        const sa = STATUS_ORDER[getStockStatus(a)] ?? 9;
        const sb = STATUS_ORDER[getStockStatus(b)] ?? 9;
        if (sa !== sb) return sa - sb;
        return getStockQty(a) - getStockQty(b);
      });
    },
  },
  methods: {
    onRefreshStock() {
      this.$emit('refresh-stock');
    },
  },
};
</script>

<style scoped>
.jr-dash-lede {
  margin: 0 0 0.85rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-dash-chart {
  margin-top: 1rem;
  border-top: 1px solid var(--color-jr-border);
  padding-top: 0.85rem;
}

@media (max-width: 767.98px) {
  .jr-dash-chart {
    display: none;
  }
}
</style>
