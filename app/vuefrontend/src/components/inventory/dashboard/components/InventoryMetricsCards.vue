<template>
  <div class="jr-metrics" :aria-busy="loading ? 'true' : 'false'">
    <div class="jr-metric">
      <p class="jr-metric__value">{{ metrics.total_products || 0 }}</p>
      <p class="jr-metric__label">Total Products</p>
    </div>

    <div class="jr-metric">
      <p class="jr-metric__value">{{ metrics.total_warehouses || 0 }}</p>
      <p class="jr-metric__label">Total Warehouses</p>
    </div>

    <div class="jr-metric">
      <p class="jr-metric__value">{{ formatNumber(metrics.total_stock_units) }}</p>
      <p class="jr-metric__label">Total Stock</p>
    </div>

    <div class="jr-metric">
      <p class="jr-metric__value">${{ formatCurrency(metrics.total_inventory_value) }}</p>
      <p class="jr-metric__label">Inventory Value</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InventoryMetricsCards',
  props: {
    metrics: {
      type: Object,
      default: () => ({}),
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    formatNumber(value) {
      if (!value) return '0';
      return new Intl.NumberFormat('en-US').format(value);
    },
    formatCurrency(value) {
      if (!value) return '0';
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(value);
    },
  },
};
</script>

<style scoped>
.jr-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
}

.jr-metric {
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  padding: 1rem 1.1rem;
}

.jr-metric__value {
  margin: 0 0 0.35rem;
  font-size: 1.3125rem;
  font-weight: 700;
  line-height: 1.25;
  color: var(--color-jr-text);
  word-break: break-all;
}

.jr-metric__label {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-jr-muted);
}

@media (max-width: 1023.98px) {
  .jr-metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 575.98px) {
  .jr-metrics {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
