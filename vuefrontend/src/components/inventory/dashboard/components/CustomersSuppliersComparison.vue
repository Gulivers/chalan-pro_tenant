<template>
  <div class="customers-suppliers-comparison">
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
      </div>
      <div class="mt-2">
        <small class="text-muted">Loading ...</small>
      </div>
    </div>
    
    <div v-else-if="!Array.isArray(comparisonData) || comparisonData.length === 0" class="text-center py-4">
      <div class="alert alert-info">
        <i class="fas fa-info-circle"></i>
        No comparison data available
      </div>
    </div>
    
    <div v-else>
      <!-- Controles del gráfico -->
      <div class="chart-controls mb-1">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h6 class="mb-0">Sales vs Purchases Comparison</h6>
            <small class="text-muted">Last 12 months</small>
          </div>
          <div class="col-md-6 text-right">
            <button class="btn btn-sm btn-outline-success" @click="refreshChart">
              <i class="fas fa-sync-alt"></i>
              Refresh
            </button>
          </div>
        </div>
      </div>
      
      <!-- Canvas del gráfico -->
      <div class="chart-container mb-3">
        <canvas ref="chartCanvas"></canvas>
      </div>

        <!-- Resumen de métricas -->
        <div class="metrics-summary mb-2">
        <div class="row">
          <div class="col-md-3">
            <div class="metric-summary-card">
              <div class="metric-value text-success">${{ formatCurrency(totalSales) }}</div>
              <div class="metric-label">Total Sales</div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-summary-card">
              <div class="metric-value text-danger">${{ formatCurrency(totalPurchases) }}</div>
              <div class="metric-label">Total Purchases</div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-summary-card">
              <div class="metric-value text-info">{{ salesCount }}</div>
              <div class="metric-label">Sales Transactions</div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-summary-card">
              <div class="metric-value text-warning">{{ purchasesCount }}</div>
              <div class="metric-label">Purchase Transactions</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Tabla de datos -->
      <div class="chart-data-table mt-4">
        <div class="table-responsive">
          <table class="table table-sm table-hover">
            <thead class="table-light">
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
                <td>
                  <span class="text-success font-weight-bold">${{ formatCurrency(month.sales) }}</span>
                </td>
                <td>
                  <span class="text-danger font-weight-bold">${{ formatCurrency(month.purchases) }}</span>
                </td>
                <td>
                  <span :class="getMarginClass(month)">
                    ${{ formatCurrency((month.sales || 0) - (month.purchases || 0)) }}
                  </span>
                </td>
                <td>
                  <span :class="'badge ' + getMarginBadgeClass(month)">
                    {{ getMarginPercentage(month) }}%
                  </span>
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
import { defineComponent, ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default defineComponent({
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
    const chartInstance = ref(null);
    const isCreatingChart = ref(false);

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
      if (margin > 20) return 'table-success';
      if (margin < -20) return 'table-danger';
      return '';
    };

    const getMarginClass = (month) => {
      const margin = getMarginPercentage(month);
      if (margin > 0) return 'text-success';
      if (margin > -20) return 'text-warning';
      return 'text-danger';
    };

    const getMarginBadgeClass = (month) => {
      const margin = getMarginPercentage(month);
      if (margin > 0) return 'badge-success';
      if (margin > -20) return 'badge-warning';
      return 'badge-danger';
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

    const createChart = (retryCount = 0) => {
      // Evitar múltiples llamadas simultáneas
      if (isCreatingChart.value && retryCount === 0) {
        return;
      }
      
      isCreatingChart.value = true;
      
      try {
        // Verificar si el componente sigue montado
        if (!chartCanvas.value || !chartCanvas.value.getContext) {
          if (retryCount < 3) {
            setTimeout(() => {
              createChart(retryCount + 1);
            }, 200);
          }
          return;
        }

        // Destruir instancia anterior de forma segura
        if (chartInstance.value) {
          try {
            chartInstance.value.destroy();
          } catch (error) {
            console.warn('Error destroying chart instance:', error);
          }
          chartInstance.value = null;
        }

        if (!Array.isArray(props.comparisonData) || props.comparisonData.length === 0) {
          return;
        }

        // Verificar que el canvas sigue siendo válido
        if (!chartCanvas.value || !chartCanvas.value.getContext) {
          return;
        }

      const labels = props.comparisonData.map(item => item.month || 'N/A');
      const salesData = props.comparisonData.map(item => item.sales || 0);
      const purchasesData = props.comparisonData.map(item => item.purchases || 0);

      chartInstance.value = new Chart(chartCanvas.value, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Customer Sales',
              data: salesData,
              borderColor: 'rgba(40, 167, 69, 1)',
              backgroundColor: 'rgba(40, 167, 69, 0.1)',
              fill: true,
              tension: 0.4
            },
            {
              label: 'Supplier Purchases',
              data: purchasesData,
              borderColor: 'rgba(220, 53, 69, 1)',
              backgroundColor: 'rgba(220, 53, 69, 0.1)',
              fill: true,
              tension: 0.4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            duration: 0
          },
          plugins: {
            title: {
              display: true,
              text: 'Sales vs Purchases Comparison (Last 12 Months)',
              font: {
                size: 16,
                weight: 'bold'
              }
            },
            legend: {
              display: true,
              position: 'top'
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                label: function(context) {
                  const month = props.comparisonData[context.dataIndex];
                  const margin = getMarginPercentage(month);
                  return [
                    `${context.dataset.label}: $${(context.parsed.y || 0).toLocaleString()}`,
                    `Margin: ${margin}%`
                  ];
                }
              }
            }
          },
          scales: {
            x: {
              title: {
                display: true,
                text: 'Month'
              }
            },
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Amount ($)'
              }
            }
          },
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
          }
        }
      });
      
      // Chart creado exitosamente
      isCreatingChart.value = false;
      
      } catch (error) {
        console.warn('Chart creation error:', error);
        
        // Limpiar instancia de forma segura
        if (chartInstance.value) {
          try {
            chartInstance.value.destroy();
          } catch (destroyError) {
            console.warn('Error destroying chart after creation error:', destroyError);
          }
          chartInstance.value = null;
        }
        
        // Reintentar si hay error y el componente sigue montado
        if (retryCount < 3 && chartCanvas.value) {
          setTimeout(() => {
            createChart(retryCount + 1);
          }, 500);
        } else {
          // Si no se puede reintentar, liberar el flag
          isCreatingChart.value = false;
        }
      }
    };

    const refreshChart = () => {
      emit('refresh');
      // Solo crear chart si no está en proceso de creación
      if (!isCreatingChart.value) {
        setTimeout(() => {
          createChart();
        }, 300);
      }
    };

    // Watch for changes in comparisonData
    watch(
      () => props.comparisonData,
      async (newData) => {
        if (newData && Array.isArray(newData) && newData.length > 0 && !isCreatingChart.value) {
          await nextTick();
          await nextTick();
          setTimeout(() => {
            if (!isCreatingChart.value) {
              createChart();
            }
          }, 100);
        }
      },
      { deep: true, immediate: true }
    );

    onMounted(async () => {
      await nextTick();
      await nextTick();
      setTimeout(() => {
        if (!isCreatingChart.value) {
          createChart();
        }
      }, 100);
    });

    onUnmounted(() => {
      // Marcar que el componente se está desmontando
      isCreatingChart.value = true;
      
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
      getMarginBadgeClass,
      totalSales,
      totalPurchases,
      salesCount,
      purchasesCount,
      refreshChart
    };
  }
});
</script>

<style scoped>
.customers-suppliers-comparison {
  min-height: 500px;
}

.chart-controls {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.chart-container {
  position: relative;
  height: 400px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-container canvas {
  max-width: 100%;
  height: 100%;
}

.metrics-summary {
  margin-bottom: 20px;
}

.metric-summary-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #dee2e6;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 0.9rem;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chart-data-table {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
  background-color: #f8f9fa;
}

.table td {
  vertical-align: middle;
}

.badge {
  font-size: 0.75rem;
  padding: 0.3rem 0.6rem;
}

/* Responsive */
@media (max-width: 768px) {
  .chart-container {
    height: 300px;
    padding: 10px;
  }
  
  .chart-controls {
    padding: 10px;
  }
  
  .chart-data-table {
    padding: 15px;
  }
  
  .table-responsive {
    font-size: 0.9rem;
  }
  
  .metric-summary-card {
    padding: 15px;
    margin-bottom: 10px;
  }
  
  .metric-value {
    font-size: 1.2rem;
  }
}
</style>