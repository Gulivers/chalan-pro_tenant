<template>
  <div class="jr-chart-block">
    <div v-if="loading" class="jr-dash-state">Loading…</div>

    <JREmptyState
      v-else-if="suppliers.length === 0"
      title="No supplier data available"
      description="There is no supplier data to chart right now."
    />

    <div v-else>
      <div class="jr-chart-controls">
        <div>
          <p class="jr-chart-controls__title">Top {{ rankedSuppliers.length }} suppliers</p>
          <span class="jr-chart-controls__hint">By purchase volume</span>
        </div>
        <JRButton variant="secondary" size="sm" type="button" @click="refreshChart">Refresh</JRButton>
      </div>

      <div class="jr-chart-container">
        <canvas
          ref="chartCanvas"
          role="img"
          :aria-label="`Bar chart of top ${rankedSuppliers.length} suppliers by purchase volume`"
        />
      </div>

      <div class="jr-chart-data">
        <div class="jr-dash-table-wrap">
          <table class="jr-dash-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Supplier</th>
                <th>Tax ID</th>
                <th>Total Purchases</th>
                <th>Transactions</th>
                <th>Last Purchase</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(supplier, index) in rankedSuppliers" :key="supplier.id">
                <td>{{ index + 1 }}</td>
                <td>
                  <strong>{{ supplier.name }}</strong>
                  <br />
                  <span class="jr-dash-muted">{{ supplier.party?.name || '—' }}</span>
                </td>
                <td><JRBadge :value="supplier.party?.rfc || '—'" severity="secondary" /></td>
                <td><span class="is-danger-text">${{ formatCurrency(supplier.total_purchases) }}</span></td>
                <td><JRBadge :value="supplier.transaction_count" severity="secondary" /></td>
                <td><span class="jr-dash-muted">{{ formatDate(supplier.last_purchase) }}</span></td>
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
  name: 'TopSuppliersChart',
  props: {
    suppliers: {
      type: Array,
      default: () => []
    },
    metrics: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh', 'supplier-clicked'],
  setup(props, { emit }) {
    const chartCanvas = ref(null);

    const rankedSuppliers = computed(() =>
      Array.isArray(props.suppliers) ? props.suppliers.slice(0, 10) : []
    );

    const formatCurrency = (value) => {
      if (!value) return '0.00';
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    };

    const formatDate = (dateString) => {
      if (!dateString) return '—';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US');
    };

    const { scheduleRender } = useDashboardChart({
      isLoading: () => props.loading,
      hasData: () => rankedSuppliers.value.length > 0,
      getCanvas: () => chartCanvas.value,
      buildChart: (canvas) => {
        const rows = rankedSuppliers.value;
        const labels = rows.map(s => s.name.length > 20 ? s.name.substring(0, 20) + '…' : s.name);
        const data = rows.map(s => s.total_purchases);

        return new Chart(canvas, {
          type: 'bar',
          data: {
            labels,
            datasets: [{
              label: 'Total Purchases ($)',
              data,
              backgroundColor: 'rgba(220, 53, 69, 0.8)',
              borderColor: 'rgba(220, 53, 69, 1)',
              borderWidth: 1
            }]
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
                    const supplier = rows[context.dataIndex];
                    return [
                      `Supplier: ${supplier.name}`,
                      `Party: ${supplier.party?.name || '—'}`,
                      `Tax ID: ${supplier.party?.rfc || '—'}`,
                      `Total: $${(supplier.total_purchases || 0).toLocaleString()}`,
                      `Transactions: ${supplier.transaction_count || 0}`
                    ];
                  }
                }
              }
            },
            scales: {
              x: {
                beginAtZero: true,
                title: { display: true, text: 'Total Purchases ($)' }
              },
              y: {
                title: { display: true, text: 'Suppliers' }
              }
            },
            onClick(_event, elements) {
              if (elements.length > 0) {
                emit('supplier-clicked', rows[elements[0].index]);
              }
            }
          }
        });
      }
    });

    watch(
      () => props.suppliers,
      () => scheduleRender(),
      { deep: true }
    );

    const refreshChart = () => {
      emit('refresh');
      scheduleRender();
    };

    return {
      chartCanvas,
      rankedSuppliers,
      formatCurrency,
      formatDate,
      refreshChart
    };
  }
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

.jr-chart-controls__title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-chart-controls__hint {
  display: block;
  margin-top: 0.2rem;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-chart-container {
  position: relative;
  height: 320px;
  margin-bottom: 0.85rem;
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
  margin-top: 0.5rem;
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

.is-danger-text {
  color: var(--color-jr-danger-text);
  font-weight: 600;
}

@media (max-width: 767.98px) {
  .jr-chart-container {
    height: 260px;
  }

}
</style>
