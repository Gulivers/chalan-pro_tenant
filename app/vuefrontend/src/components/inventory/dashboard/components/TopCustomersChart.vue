<template>
  <div class="top-customers-chart">
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
      </div>
      <div class="mt-2">
        <small class="text-muted">Loading Customers...</small>
      </div>
    </div>

    
    <div v-else-if="customers.length === 0" class="text-center py-4">
      <div class="alert alert-info">
        <i class="fas fa-info-circle"></i>
        No customer data available
      </div>
    </div>
    
    <div v-else>
      <!-- Controles del gráfico -->
      <div class="chart-controls mb-3">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h6 class="mb-0">Top {{ Math.min(customers.length, 10) }} Customers</h6>
            <small class="text-muted">By purchase volume</small>
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
      <div class="chart-container">
        <canvas ref="chartCanvas"></canvas>
      </div>
      
      <!-- Tabla de datos -->
      <div class="chart-data-table mt-4">
        <div class="table-responsive">
          <table class="table table-sm table-hover">
            <thead class="table-light">
              <tr>
                <th>#</th>
                <th>Customer</th>
                <th>Tax ID</th>
                <th>Total Purchases</th>
                <th>Transactions</th>
                <th>Last Purchase</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(customer, index) in customers.slice(0, 10)" :key="customer.id" class="clickable-row">
                <td>{{ index + 1 }}</td>
                <td>
                  <div class="customer-info">
                    <strong>{{ customer.name }}</strong>
                    <br>
                    <small class="text-muted">{{ customer.party?.name || 'N/A' }}</small>
                  </div>
                </td>
                <td>
                  <span class="badge badge-secondary">{{ customer.party?.rfc || 'N/A' }}</span>
                </td>
                <td>
                  <span class="text-success font-weight-bold">${{ formatCurrency(customer.total_purchases) }}</span>
                </td>
                <td>
                  <span class="badge badge-info">{{ customer.transaction_count }}</span>
                </td>
                <td>
                  <small class="text-muted">{{ formatDate(customer.last_purchase) }}</small>
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
import { defineComponent, ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default defineComponent({
  name: 'TopCustomersChart',
  props: {
    customers: {
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
  emits: ['refresh', 'customer-clicked'],
  setup(props, { emit }) {
    const chartCanvas = ref(null);
    const chartInstance = ref(null);

    const formatCurrency = (value) => {
      if (!value) return '0.00';
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US');
    };

    const createChart = (retryCount = 0) => {
      try {
        if (chartInstance.value) {
          chartInstance.value.destroy();
          chartInstance.value = null;
        }

        if (!chartCanvas.value) {
          if (retryCount < 3) {
            setTimeout(() => {
              createChart(retryCount + 1);
            }, 200);
          }
          return;
        }

        if (!props.customers || props.customers.length === 0) {
          return;
        }

      const labels = props.customers.map(c => c.name.length > 20 ? c.name.substring(0, 20) + '...' : c.name);
      const data = props.customers.map(c => c.total_purchases);

      chartInstance.value = new Chart(chartCanvas.value, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Total Purchases ($)',
            data: data,
            backgroundColor: 'rgba(76, 175, 80, 0.8)',
            borderColor: 'rgba(76, 175, 80, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          indexAxis: 'y',
          animation: {
            duration: 0
          },
          plugins: {
            title: {
              display: true,
              text: 'Top 10 Customers by Purchase Volume',
              font: {
                size: 16,
                weight: 'bold'
              }
            },
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  const customer = props.customers[context.dataIndex];
                  return [
                    `Customer: ${customer.name}`,
                    `Party: ${customer.party?.name || 'N/A'}`,
                    `Tax ID: ${customer.party?.rfc || 'N/A'}`,
                    `Total: $${(customer.total_purchases || 0).toLocaleString()}`,
                    `Transactions: ${customer.transaction_count || 0}`
                  ];
                }
              }
            }
          },
          scales: {
            x: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Total Purchases ($)'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Customers'
              }
            }
          },
          onClick: (event, elements) => {
            if (elements.length > 0) {
              const index = elements[0].index;
              const customer = props.customers[index];
              emit('customer-clicked', customer);
            }
          }
        }
      });
      } catch (error) {
        if (chartInstance.value) {
          chartInstance.value.destroy();
          chartInstance.value = null;
        }
        // Reintentar si hay error
        if (retryCount < 3) {
          setTimeout(() => {
            createChart(retryCount + 1);
          }, 500);
        }
      }
    };

    const refreshChart = () => {
      emit('refresh');
      setTimeout(() => {
        createChart();
      }, 300);
    };

    // Watch for changes in customers
    watch(
      () => props.customers,
      async (newCustomers) => {
        if (newCustomers && newCustomers.length > 0) {
          await nextTick();
          await nextTick();
          setTimeout(() => {
            createChart();
          }, 100);
        }
      },
      { deep: true, immediate: true }
    );

    onMounted(async () => {
      await nextTick();
      await nextTick();
      setTimeout(() => {
        createChart();
      }, 100);
    });

    onUnmounted(() => {
      if (chartInstance.value) {
        chartInstance.value.destroy();
        chartInstance.value = null;
      }
    });

    return {
      chartCanvas,
      formatCurrency,
      formatDate,
      refreshChart
    };
  }
});
</script>

<style scoped>
.top-customers-chart {
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

.clickable-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.clickable-row:hover {
  background-color: rgba(0, 123, 255, 0.1);
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
}
</style>