<template>
  <div class="sales-metrics-cards">
    <div class="row">
      <!-- Total Sales -->
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="metric-card success">
          <div class="metric-icon">
            <i class="fas fa-dollar-sign"></i>
          </div>
          <div class="metric-content">
            <h4 class="metric-value">${{ formatCurrency(metrics.total_sales) }}</h4>
            <p class="metric-label">Total Sales</p>
            <small class="metric-period">{{ period }} days</small>
          </div>
        </div>
      </div>

      <!-- Promedio Diario -->
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="metric-card info">
          <div class="metric-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="metric-content">
            <h4 class="metric-value">${{ formatCurrency(metrics.daily_average) }}</h4>
            <p class="metric-label">Promedio Diario</p>
            <small class="metric-period">Por día</small>
          </div>
        </div>
      </div>

      <!-- Producto Más Vendido -->
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="metric-card warning">
          <div class="metric-icon">
            <i class="fas fa-trophy"></i>
          </div>
          <div class="metric-content">
            <h4 class="metric-value">{{ metrics.top_product_name || 'N/A' }}</h4>
            <p class="metric-label">Producto Top</p>
            <small class="metric-period">{{ metrics.top_product_qty || 0 }} unidades</small>
          </div>
        </div>
      </div>

      <!-- Crecimiento -->
      <div class="col-md-3 col-sm-6 mb-3">
        <div class="metric-card" :class="getGrowthClass(metrics.growth_percentage)">
          <div class="metric-icon">
            <i class="fas fa-percentage"></i>
          </div>
          <div class="metric-content">
            <h4 class="metric-value">{{ formatPercentage(metrics.growth_percentage) }}</h4>
            <p class="metric-label">Crecimiento</p>
            <small class="metric-period">vs período anterior</small>
          </div>
        </div>
      </div>
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
        growth_percentage: 0
      })
    },
    period: {
      type: Number,
      default: 30
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    formatCurrency(value) {
      if (!value) return '0.00'
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value)
    },
    
    formatPercentage(value) {
      if (!value) return '0%'
      const formatted = new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
      }).format(value)
      return `${formatted}%`
    },
    
    getGrowthClass(percentage) {
      if (percentage > 0) return 'success'
      if (percentage < 0) return 'danger'
      return 'secondary'
    }
  }
}
</script>

<style scoped>
.sales-metrics-cards {
  margin-bottom: 20px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #28a745;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  align-items: center;
  gap: 15px;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.metric-card.success {
  border-left-color: #28a745;
}

.metric-card.info {
  border-left-color: #17a2b8;
}

.metric-card.warning {
  border-left-color: #ffc107;
}

.metric-card.danger {
  border-left-color: #dc3545;
}

.metric-card.secondary {
  border-left-color: #6c757d;
}

.metric-icon {
  font-size: 2rem;
  color: #28a745;
  min-width: 50px;
  text-align: center;
}

.metric-card.success .metric-icon {
  color: #28a745;
}

.metric-card.info .metric-icon {
  color: #17a2b8;
}

.metric-card.warning .metric-icon {
  color: #ffc107;
}

.metric-card.danger .metric-icon {
  color: #dc3545;
}

.metric-card.secondary .metric-icon {
  color: #6c757d;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 5px 0;
  line-height: 1.2;
}

.metric-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin: 0 0 3px 0;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-period {
  font-size: 0.8rem;
  color: #95a5a6;
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .metric-card {
    padding: 15px;
    gap: 12px;
  }
  
  .metric-icon {
    font-size: 1.8rem;
    min-width: 40px;
  }
  
  .metric-value {
    font-size: 1.3rem;
  }
}

@media (max-width: 576px) {
  .metric-card {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  .metric-icon {
    font-size: 1.6rem;
    min-width: auto;
  }
  
  .metric-value {
    font-size: 1.2rem;
  }
}
</style>
