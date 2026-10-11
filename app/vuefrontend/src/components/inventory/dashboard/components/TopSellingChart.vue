<template>
  <div class="jr-chart-block">
    <div v-if="loading" class="jr-dash-state">Loading…</div>

    <JREmptyState
      v-else-if="products.length === 0"
      title="No sales data"
      description="No sales data for the selected period"
    />

    <div v-else>
      <div class="jr-chart-controls">
        <div>
          <p class="jr-chart-controls__hint">
            Showing top {{ displayCount }} · Period: {{ period }} days
          </p>
        </div>
        <JRButton variant="secondary" size="sm" type="button" @click="refreshChart">Refresh</JRButton>
      </div>

      <div class="jr-chart-container">
        <canvas
          ref="chartCanvas"
          role="img"
          :aria-label="`Bar chart of top ${displayCount} selling products for the last ${period} days`"
        />
      </div>

      <div class="jr-chart-data">
        <div class="jr-dash-table-wrap">
          <table class="jr-dash-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Product</th>
                <th>SKU</th>
                <th>Quantity Sold</th>
                <th>Total Value</th>
                <th>Transactions</th>
                <th>Last Sale</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(product, index) in rankedProducts" :key="product.id">
                <td>{{ index + 1 }}</td>
                <td>
                  <strong>{{ product.name }}</strong>
                  <br />
                  <span class="jr-dash-muted">{{ product.category?.name || '—' }}</span>
                </td>
                <td><JRBadge :value="product.sku" severity="secondary" /></td>
                <td><span class="is-primary-text">{{ formatNumber(product.quantity_sold) }}</span></td>
                <td><span class="is-success-text">${{ formatCurrency(product.total_value) }}</span></td>
                <td><JRBadge :value="product.transaction_count" severity="secondary" /></td>
                <td><span class="jr-dash-muted">{{ formatDate(product.last_sale_date) }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, watch, computed } from 'vue';
import { Chart, registerables } from 'chart.js';
import { JRButton, JRBadge, JREmptyState } from '@ui';
import { useDashboardChart } from './useDashboardChart';
Chart.register(...registerables);

export default defineComponent({
  components: { JRButton, JRBadge, JREmptyState },
  name: 'TopSellingChart',
  props: {
    products: {
      type: Array,
      default: () => [],
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
  emits: ['refresh', 'product-clicked'],
  setup(props, { emit }) {
    const chartCanvas = ref(null);

    const rankedProducts = computed(() =>
      Array.isArray(props.products) ? props.products.slice(0, 25) : []
    );
    const displayCount = computed(() => rankedProducts.value.length);

    const formatNumber = value => {
      if (!value) return '0';
      return new Intl.NumberFormat('en-US').format(value);
    };

    const formatCurrency = value => {
      if (!value) return '0.00';
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(value);
    };

    const formatDate = dateString => {
      if (!dateString) return '—';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US');
    };

    const { scheduleRender } = useDashboardChart({
      isLoading: () => props.loading,
      hasData: () => rankedProducts.value.length > 0,
      getCanvas: () => chartCanvas.value,
      buildChart: (canvas) => {
        const topProducts = rankedProducts.value;
        const labels = topProducts.map(p => (p.name.length > 25 ? p.name.substring(0, 25) + '...' : p.name));
        const data = topProducts.map(p => p.total_value || 0);

        return new Chart(canvas, {
          type: 'bar',
          data: {
            labels,
            datasets: [
              {
                label: 'Total Sales Value ($)',
                data,
                backgroundColor: 'rgba(40, 167, 69, 0.8)',
                borderColor: 'rgba(40, 167, 69, 1)',
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            animation: { duration: 0 },
            plugins: {
              title: { display: false },
              legend: { display: false },
              tooltip: {
                callbacks: {
                  label(context) {
                    const product = topProducts[context.dataIndex];
                    return [
                      `Product: ${product.name}`,
                      `SKU: ${product.sku}`,
                      `Quantity: ${product.quantity_sold || 0}`,
                      `Value: $${(product.total_value || 0).toLocaleString()}`,
                      `Transactions: ${product.transaction_count || 0}`,
                    ];
                  },
                },
              },
            },
            scales: {
              x: {
                beginAtZero: true,
                title: { display: true, text: 'Total Sales Value ($)' },
              },
              y: {
                title: { display: true, text: 'Products' },
              },
            },
            onClick(_event, elements) {
              if (elements.length > 0) {
                emit('product-clicked', topProducts[elements[0].index]);
              }
            },
          },
        });
      },
    });

    watch(
      () => props.products,
      () => scheduleRender(),
      { deep: true }
    );

    watch(
      () => props.period,
      () => scheduleRender()
    );

    const refreshChart = () => {
      emit('refresh');
      scheduleRender();
    };

    return {
      chartCanvas,
      rankedProducts,
      displayCount,
      formatNumber,
      formatCurrency,
      formatDate,
      refreshChart,
    };
  },
});
</script>

<style scoped>
.jr-chart-block {
  min-height: 0;
}

.jr-dash-state {
  padding: 0.75rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-chart-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.jr-chart-controls__hint {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-chart-container {
  position: relative;
  height: 360px;
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  padding: 0.85rem;
}

.jr-chart-container canvas {
  display: block;
  max-width: 100%;
}

.jr-chart-data {
  margin-top: 0.85rem;
}

.jr-dash-muted {
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-dash-table-wrap {
  overflow: auto;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  max-height: 22rem;
}

.jr-dash-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  margin: 0;
}

.jr-dash-table th,
.jr-dash-table td {
  padding: 0.55rem 0.65rem;
  border-bottom: 1px solid var(--color-jr-border);
  text-align: left;
  vertical-align: middle;
}

.jr-dash-table thead th {
  position: sticky;
  top: 0;
  background: var(--color-jr-surface-muted);
  font-weight: 600;
  color: var(--color-jr-text);
}

.is-success-text {
  color: var(--color-jr-success-text);
  font-weight: 600;
}

.is-primary-text {
  color: var(--color-jr-primary);
  font-weight: 600;
}

@media (max-width: 767.98px) {
  .jr-chart-container {
    height: 280px;
  }
}
</style>
