<template>
  <div class="lowest-stock-chart">
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
      </div>
      <div class="mt-2">
        <small class="text-muted">Loading products...</small>
      </div>
    </div>
    
    <div v-else-if="products.length === 0" class="text-center py-4">
      <div class="alert alert-info">
        <i class="fas fa-info-circle"></i>
        No stock data available
      </div>
    </div>
    
    <div v-else>
      <!-- Controles del gráfico -->
      <div class="chart-controls mb-3">
        <div class="row align-items-center">
          <div class="col-md-6">
            <h6 class="mb-0">Top {{ Math.min(products.length, 25) }} Products with Lowest Stock</h6>
            <small class="text-muted">Current inventory levels</small>
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
                <th>Product</th>
                <th>SKU</th>
                <th>Current Stock</th>
                <th>Reorder Level</th>
                <th>Status</th>
                <th>Stock Value</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(product, index) in products.slice(0, 10)" :key="product.id" class="clickable-row">
                <td>{{ index + 1 }}</td>
                <td>
                  <div class="product-info">
                    <strong>{{ product.name }}</strong>
                    <br>
                    <small class="text-muted">{{ product.category?.name || 'N/A' }}</small>
                  </div>
                </td>
                <td>
                  <span class="badge badge-secondary">{{ product.sku }}</span>
                </td>
                <td>
                  <span class="text-primary font-weight-bold">{{ formatNumber(product.current_stock) }}</span>
                </td>
                <td>
                  <span class="text-muted">{{ formatNumber(product.reorder_level) }}</span>
                </td>
                <td>
                  <span :class="'badge ' + (product.is_low_stock ? 'badge-danger' : 'badge-success')">
                    {{ product.is_low_stock ? 'Low Stock' : 'OK' }}
                  </span>
                </td>
                <td>
                  <span class="text-info font-weight-bold">${{ formatCurrency(product.stock_value) }}</span>
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
  name: 'LowestStockChart',
  props: {
    products: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh', 'product-clicked'],
  setup(props, { emit }) {
    const chartCanvas = ref(null);
    const chartInstance = ref(null);

    const formatNumber = (value) => {
      if (!value) return '0';
      return new Intl.NumberFormat('en-US').format(value);
    };

    const formatCurrency = (value) => {
      if (!value) return '0.00';
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
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

        if (!props.products || props.products.length === 0) {
          return;
        }

      const topProducts = props.products.slice(0, 25);
      const labels = topProducts.map(p => p.name.length > 25 ? p.name.substring(0, 25) + '...' : p.name);
      const data = topProducts.map(p => p.current_stock || 0);
      const backgroundColors = topProducts.map(p => p.is_low_stock ? 'rgba(220, 53, 69, 0.8)' : 'rgba(40, 167, 69, 0.8)');
      const borderColors = topProducts.map(p => p.is_low_stock ? 'rgba(220, 53, 69, 1)' : 'rgba(40, 167, 69, 1)');

      chartInstance.value = new Chart(chartCanvas.value, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Current Stock',
            data: data,
            backgroundColor: backgroundColors,
            borderColor: borderColors,
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
              text: 'Top 25 Products with Lowest Stock',
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
                  const product = topProducts[context.dataIndex];
                  return [
                    `Product: ${product.name}`,
                    `SKU: ${product.sku}`,
                    `Current Stock: ${product.current_stock || 0}`,
                    `Reorder Level: ${product.reorder_level || 0}`,
                    `Status: ${product.is_low_stock ? 'Low Stock' : 'OK'}`,
                    `Stock Value: $${(product.stock_value || 0).toLocaleString()}`
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
                text: 'Current Stock'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Products'
              }
            }
          },
          onClick: (event, elements) => {
            if (elements.length > 0) {
              const index = elements[0].index;
              const product = topProducts[index];
              emit('product-clicked', product);
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

    // Watch for changes in products
    watch(
      () => props.products,
      async (newProducts) => {
        if (newProducts && newProducts.length > 0) {
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
      formatNumber,
      formatCurrency,
      refreshChart
    };
  }
});
</script>

<style scoped>
.lowest-stock-chart {
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