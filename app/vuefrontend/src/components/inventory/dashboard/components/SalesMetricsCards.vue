<template>
  <div class="jr-metrics" :aria-busy="loading ? 'true' : 'false'">
    <div class="jr-metric">
      <p class="jr-metric__value">${{ formatCurrency(metrics.total_sales) }}</p>
      <p class="jr-metric__label">Total Sales</p>
      <p class="jr-metric__hint">{{ period }} days</p>
    </div>

    <div class="jr-metric">
      <p class="jr-metric__value">${{ formatCurrency(metrics.daily_average) }}</p>
      <p class="jr-metric__label">Daily Average</p>
      <p class="jr-metric__hint">Per day</p>
    </div>

    <div class="jr-metric">
      <p class="jr-metric__value">{{ metrics.top_product_name || '—' }}</p>
      <p class="jr-metric__label">Top Product</p>
      <p class="jr-metric__hint">{{ formatUnits(metrics.top_product_qty) }}</p>
    </div>

    <div class="jr-metric" :class="growthToneClass">
      <p class="jr-metric__value">{{ growthDisplay }}</p>
      <p class="jr-metric__label">Growth</p>
      <p class="jr-metric__hint">{{ growthHint }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SalesMetricsCards',
  props: {
    metrics: {
      type: Object,
      default: () => ({
        total_sales: 0,
        daily_average: 0,
        top_product_name: '',
        top_product_qty: 0,
        growth_percentage: 0,
      }),
    },
    period: {
      type: Number,
      default: 30,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    totalSales() {
      const n = Number(this.metrics?.total_sales);
      return Number.isFinite(n) ? n : 0;
    },
    growthValue() {
      const n = Number(this.metrics?.growth_percentage);
      return Number.isFinite(n) ? n : 0;
    },
    /**
     * Backend sets growth to 0 when previous period sales are 0, and −100% when
     * current is 0 but previous had sales. Without previous totals in the payload,
     * zero current sales (or a −100% with no activity) is not a trustworthy signal.
     */
    isGrowthComparable() {
      if (this.totalSales <= 0) return false;
      if (this.growthValue === -100) return false;
      return true;
    },
    growthDisplay() {
      if (!this.isGrowthComparable) return 'No comparable period';
      return this.formatPercentage(this.growthValue);
    },
    growthHint() {
      if (!this.isGrowthComparable) {
        return 'Not enough sales history to compare';
      }
      return 'vs previous period';
    },
    growthToneClass() {
      if (!this.isGrowthComparable) return 'tone-secondary';
      if (this.growthValue > 0) return 'tone-success';
      if (this.growthValue < 0) return 'tone-danger';
      return 'tone-secondary';
    },
  },
  methods: {
    formatCurrency(value) {
      const n = Number(value);
      if (!Number.isFinite(n) || n === 0) return '0.00';
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(n);
    },

    formatPercentage(value) {
      const n = Number(value);
      if (!Number.isFinite(n)) return '0%';
      const formatted = new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
      }).format(n);
      return `${formatted}%`;
    },

    formatUnits(value) {
      const n = Number(value);
      if (!Number.isFinite(n) || n === 0) return '0 units';
      return `${new Intl.NumberFormat('en-US').format(n)} units`;
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

.jr-metric.tone-success {
  background: var(--color-jr-success-subtle);
}

.jr-metric.tone-danger {
  background: var(--color-jr-danger-subtle);
}

.jr-metric.tone-secondary {
  background: var(--color-jr-surface-muted);
}

.jr-metric__value {
  margin: 0 0 0.35rem;
  font-size: 1.3125rem;
  font-weight: 700;
  line-height: 1.25;
  color: var(--color-jr-text);
  word-break: break-word;
}

.jr-metric__label {
  margin: 0 0 0.2rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-jr-muted);
}

.jr-metric__hint {
  margin: 0;
  font-size: 0.75rem;
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
