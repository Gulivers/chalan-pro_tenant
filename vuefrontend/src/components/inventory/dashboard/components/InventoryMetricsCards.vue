<template>
  <div class="metrics-cards">
    <div class="row">
      <!-- Total Products -->
      <div class="col-md-3 col-sm-6 mb-4">
        <div class="metric-card">
          <div class="metric-icon">
            <i class="fas fa-boxes"></i>
          </div>
          <div class="metric-content">
            <h3 class="metric-value">{{ metrics.total_products || 0 }}</h3>
            <p class="metric-label">Total Products</p>
          </div>
        </div>
      </div>

      <!-- Total Warehouses -->
      <div class="col-md-3 col-sm-6 mb-4">
        <div class="metric-card">
          <div class="metric-icon">
            <i class="fas fa-warehouse"></i>
          </div>
          <div class="metric-content">
            <h3 class="metric-value">{{ metrics.total_warehouses || 0 }}</h3>
            <p class="metric-label">Total Warehouses</p>
          </div>
        </div>
      </div>

      <!-- Total Stock -->
      <div class="col-md-3 col-sm-6 mb-4">
        <div class="metric-card">
          <div class="metric-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="metric-content">
            <h3 class="metric-value">{{ formatNumber(metrics.total_stock_units) }}</h3>
            <p class="metric-label">Total Stock</p>
          </div>
        </div>
      </div>

      <!-- Inventory Value -->
      <div class="col-md-3 col-sm-6 mb-4">
        <div class="metric-card">
          <div class="metric-icon">
            <i class="fas fa-dollar-sign"></i>
          </div>
          <div class="metric-content">
            <h3 class="metric-value">${{ formatCurrency(metrics.total_inventory_value) }}</h3>
            <p class="metric-label">Inventory Value</p>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'InventoryMetricsCards',
  props: {
    metrics: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    formatNumber(value) {
      if (!value) return '0'
      return new Intl.NumberFormat('en-US').format(value)
    },
    formatCurrency(value) {
      if (!value) return '0'
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value)
    }
  }
}
</script>

<style scoped>
.metrics-cards {
  margin-bottom: 40px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3498db;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  align-items: center;
  gap: 20px;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.metric-card.warning {
  border-left-color: #f39c12;
}

.metric-card.success {
  border-left-color: #27ae60;
}

.metric-card.info {
  border-left-color: #3498db;
}

.metric-card.primary {
  border-left-color: #9b59b6;
}

.metric-icon {
  font-size: 2.5rem;
  color: #3498db;
  min-width: 60px;
  text-align: center;
}

.metric-card.warning .metric-icon {
  color: #f39c12;
}

.metric-card.success .metric-icon {
  color: #27ae60;
}

.metric-card.info .metric-icon {
  color: #3498db;
}

.metric-card.primary .metric-icon {
  color: #9b59b6;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 1.6rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 5px 0;
  line-height: 1;
  word-break: break-all;
}

.metric-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Responsive */
@media (max-width: 768px) {
  .metric-card {
    padding: 20px;
    gap: 15px;
  }
  
  .metric-icon {
    font-size: 2rem;
    min-width: 50px;
  }
  
  .metric-value {
    font-size: 1.4rem;
  }
}

@media (max-width: 576px) {
  .metric-card {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  .metric-icon {
    font-size: 1.8rem;
    min-width: auto;
  }
  
  .metric-value {
    font-size: 1.6rem;
  }
}
</style>
