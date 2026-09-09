<template>
  <div class="jr-chart-block">
    <div v-if="!hasData" class="jr-dash-state">
      <div v-if="loading">Loading…</div>
      <JREmptyState
        v-else
        title="No comparison data available"
        description="There is no comparison data to chart right now."
      />
    </div>

    <div v-else>
      <div class="jr-chart-controls">
        <div>
          <p class="jr-chart-controls__title">Sales vs Purchases Comparison</p>
          <span class="jr-chart-controls__hint">Last 12 months</span>
        </div>
        <JRButton variant="secondary" size="sm" @click="refreshChart">Refresh</JRButton>
      </div>

      <div class="jr-chart-container">
        <canvas
          ref="chartCanvas"
          role="img"
          aria-label="Bar chart comparing customer sales and supplier purchases"
        />
        <div v-if="loading" class="jr-chart-overlay">
          <span class="jr-dash-muted">Refreshing data…</span>
        </div>
      </div>

      <div class="jr-metrics-summary">
        <div class="jr-metric-summary">
          <div class="jr-metric-summary__value is-success-text">${{ formatCurrency(totalSales) }}</div>
          <div class="jr-metric-summary__label">Total Sales</div>
        </div>
        <div class="jr-metric-summary">
          <div class="jr-metric-summary__value is-danger-text">${{ formatCurrency(totalPurchases) }}</div>
          <div class="jr-metric-summary__label">Total Purchases</div>
        </div>
        <div class="jr-metric-summary">
          <div class="jr-metric-summary__value is-info-text">{{ salesCount }}</div>
          <div class="jr-metric-summary__label">Sales Transactions</div>
        </div>
        <div class="jr-metric-summary">
          <div class="jr-metric-summary__value">{{ purchasesCount }}</div>
          <div class="jr-metric-summary__label">Purchase Transactions</div>
        </div>
      </div>

      <div class="jr-chart-data">
        <div class="jr-dash-table-wrap">
          <table class="jr-dash-table">
            <thead>
              <tr>
                <th>Month</th>
                <th>Sales</th>
                <th>Purchases</th>
                <th>Margin</th>
                <th>Margin %</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(month, index) in comparisonData" :key="index" :class="getRowClass(month)">
                <td><strong>{{ month.month }}</strong></td>
                <td><span class="is-success-text">${{ formatCurrency(month.sales) }}</span></td>
                <td><span class="is-danger-text">${{ formatCurrency(month.purchases) }}</span></td>
                <td>
                  <span :class="getMarginClass(month)">
                    ${{ formatCurrency((month.sales || 0) - (month.purchases || 0)) }}
                  </span>
                </td>
                <td>
                  <JRBadge
                    :value="`${getMarginPercentage(month)}%`"
                    :severity="getMarginSeverity(month)"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, shallowRef, onMounted, onUnmounted, watch, computed, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
import { JRButton, JRBadge, JREmptyState } from '@ui';
Chart.register(...registerables);

export default defineComponent({
  components: { JRButton, JRBadge, JREmptyState },
  name: 'CustomersSuppliersComparison',
  props: {
    comparisonData: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh'],
  setup(props, { emit }) {
    const chartCanvas = ref(null);
    const chartInstance = shallowRef(null);
    const hasData = computed(() => Array.isArray(props.comparisonData) && props.comparisonData.length > 0);

    const formatCurrency = (value) => {
      if (!value) return '0.00';
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    };

    const formatNumber = (value) => {
      if (!value) return '0';
      return new Intl.NumberFormat('en-US').format(value);
    };

    const getMarginPercentage = (month) => {
      const sales = month.sales || 0;
      const purchases = month.purchases || 0;
      if (sales === 0) return 0;
      const margin = ((sales - purchases) / sales) * 100;
      return margin.toFixed(1);
    };

    const getRowClass = (month) => {
      const margin = getMarginPercentage(month);
      if (margin > 20) return 'is-success';
      if (margin < -20) return 'is-danger';
      return '';
    };

    const getMarginClass = (month) => {
      const margin = getMarginPercentage(month);
      if (margin > 0) return 'is-success-text';
      if (margin > -20) return 'is-info-text';
      return 'is-danger-text';
    };

    const getMarginSeverity = (month) => {
      const margin = getMarginPercentage(month);
      if (margin > 0) return 'success';
      if (margin > -20) return 'info';
      return 'danger';
    };

    const totalSales = computed(() => {
      if (!Array.isArray(props.comparisonData)) return 0;
      return props.comparisonData.reduce((sum, month) => sum + (month.sales || 0), 0);
    });

    const totalPurchases = computed(() => {
      if (!Array.isArray(props.comparisonData)) return 0;
      return props.comparisonData.reduce((sum, month) => sum + (month.purchases || 0), 0);
    });

    const salesCount = computed(() => {
      // Estimación basada en el promedio de transacciones por mes
      return Math.round(totalSales.value / 1000); // Estimación aproximada
    });

    const purchasesCount = computed(() => {
      // Estimación basada en el promedio de transacciones por mes
      return Math.round(totalPurchases.value / 1000); // Estimación aproximada
    });

    const renderChart = async () => {
      if (props.loading) {
        return;
      }

      if (!hasData.value) {
        if (chartInstance.value) {
          try {
            chartInstance.value.destroy();
          } catch (error) {
            console.warn('Error destroying chart instance:', error);
          }
          chartInstance.value = null;
        }
        return;
      }

      await nextTick();

      const canvasEl = chartCanvas.value;
      if (!canvasEl) {
        return;
      }

      const container = canvasEl.parentElement;
      if (container && (container.clientWidth < 2 || container.clientHeight < 2)) {
        setTimeout(() => {
          renderChart();
        }, 100);
        return;
      }

      const labels = props.comparisonData.map(item => item.month || 'N/A');
      const salesData = props.comparisonData.map(item => item.sales || 0);
      const purchasesData = props.comparisonData.map(item => item.purchases || 0);

      if (!chartInstance.value) {
        chartInstance.value = new Chart(canvasEl, {
          type: 'line',
          data: {
            labels,
            datasets: [
              {
                label: 'Customer Sales',
                data: salesData,
                borderColor: 'rgba(40, 167, 69, 1)',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                fill: true,
                tension: 0.4,
              },
              {
                label: 'Supplier Purchases',
                data: purchasesData,
                borderColor: 'rgba(220, 53, 69, 1)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                fill: true,
                tension: 0.4,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
              duration: 0,
            },
            plugins: {
              title: {
                display: true,
                text: 'Sales vs Purchases Comparison (Last 12 Months)',
                font: {
                  size: 16,
                  weight: 'bold',
                },
              },
              legend: {
                display: true,
                position: 'top',
              },
              tooltip: {
                mode: 'index',
                intersect: false,
                callbacks: {
                  label: function (context) {
                    const month = props.comparisonData[context.dataIndex];
                    const margin = getMarginPercentage(month);
                    return [
                      `${context.dataset.label}: $${(context.parsed.y || 0).toLocaleString()}`,
                      `Margin: ${margin}%`,
                    ];
                  },
                },
              },
            },
            scales: {
              x: {
                title: {
                  display: true,
                  text: 'Month',
                },
              },
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: 'Amount ($)',
                },
              },
            },
            interaction: {
              mode: 'nearest',
              axis: 'x',
              intersect: false,
            },
          },
        });
        requestAnimationFrame(() => {
          try {
            chartInstance.value?.resize();
          } catch (_) {
            /* ignore */
          }
        });
        return;
      }

      const chart = chartInstance.value;
      chart.data.labels = labels;
      if (chart.data.datasets.length >= 2) {
        chart.data.datasets[0].data = salesData;
        chart.data.datasets[1].data = purchasesData;
      }
      chart.update('none');
    };

    const refreshChart = () => {
      emit('refresh');
    };

    // Watch for changes in comparisonData
    watch(
      () => props.comparisonData,
      async (newData) => {
        if (newData && Array.isArray(newData)) {
          await renderChart();
        } else if (chartInstance.value) {
          chartInstance.value.destroy();
          chartInstance.value = null;
        }
      },
      { deep: true, immediate: true }
    );

    watch(
      () => props.loading,
      async (isLoading) => {
        if (!isLoading) {
          await renderChart();
        }
      },
      { immediate: true }
    );

    onMounted(async () => {
      await renderChart();
    });

    onUnmounted(() => {
      // Destruir chart de forma segura
      if (chartInstance.value) {
        try {
          chartInstance.value.destroy();
        } catch (error) {
          console.warn('Error destroying chart on unmount:', error);
        }
        chartInstance.value = null;
      }
    });

    return {
      chartCanvas,
      formatCurrency,
      formatNumber,
      getMarginPercentage,
      getRowClass,
      getMarginClass,
      getMarginSeverity,
      totalSales,
      totalPurchases,
      salesCount,
      purchasesCount,
      refreshChart,
      hasData
    };
  }
});
</script>
<style scoped>
.jr-chart-block {
  min-height: 500px;
}

.jr-dash-state {
  padding: 1.25rem 0;
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
  padding: 0.75rem 0.85rem;
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface-muted);
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
  height: 400px;
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  padding: 1rem;
}

.jr-chart-container canvas {
  display: block;
  max-width: 100%;
}

.jr-chart-data {
  margin-top: 1rem;
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  padding: 1rem;
}

.jr-dash-muted {
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-dash-table-wrap {
  overflow: auto;
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

.is-info-text {
  color: var(--color-jr-info-text);
  font-weight: 600;
}

.is-primary-text {
  color: var(--color-jr-primary);
  font-weight: 600;
}

.jr-chart-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--color-jr-surface) 88%, transparent);
  z-index: 2;
}

.jr-metrics-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
  margin: 0.75rem 0;
}

.jr-metric-summary {
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface);
  padding: 0.85rem;
}

.jr-metric-summary__value {
  font-size: 1.3125rem;
  font-weight: 700;
  line-height: 1.25;
  color: var(--color-jr-text);
}

.jr-metric-summary__label {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-jr-muted);
}

@media (max-width: 767.98px) {
  .jr-chart-container {
    height: 300px;
    padding: 0.65rem;
  }

  .jr-metrics-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 575.98px) {
  .jr-metrics-summary {
    grid-template-columns: 1fr;
  }
}

.jr-dash-table tbody tr.is-success {
  background: var(--color-jr-success-subtle);
}

.jr-dash-table tbody tr.is-danger {
  background: var(--color-jr-danger-subtle);
}
</style>
