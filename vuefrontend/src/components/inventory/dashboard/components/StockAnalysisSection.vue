<template>
  <div class="stock-analysis-section">
    <div class="section-header">
      <h4 class="text-primary">
        <i class="fas fa-boxes"></i>
        Stock
      </h4>
    </div>

    <!-- Products Below Reorder Level -->
    <div class="low-stock-alerts mb-4">
      <TxCard>
        <template #header>
          <h5 class="mb-0">
            <i class="fas fa-exclamation-triangle text-warning"></i>
            Products Below Reorder Level
          </h5>
        </template>
        <LowStockTable 
          :products="lowStockProducts"
          :loading="loading"
        />
      </TxCard>
    </div>

    <!-- Top 25 Products with Lowest Stock -->
    <div class="lowest-stock-chart mb-4">
      <TxCard>
        <template #header>
          <h5 class="mb-0">
            <i class="fas fa-chart-bar text-danger"></i>
            Top 25 Products with Lowest Stock
          </h5>
        </template>
        <LowestStockChart 
          :products="lowestStockProducts"
          :loading="loading"
          @refresh="onRefreshStock"
        />
      </TxCard>
    </div>

    <!-- Export Stock to Excel -->
    <div class="export-section">
      <TxCard>
        <template #header>
          <h5 class="mb-0">
            <i class="fas fa-file-excel text-success"></i>
            Export Stock to Excel
          </h5>
        </template>
        <StockExportButtons 
          :loading="loading"
        />
      </TxCard>
    </div>
  </div>
</template>

<script>
import LowStockTable from './LowStockTable.vue'
import LowestStockChart from './LowestStockChart.vue'
import StockExportButtons from './StockExportButtons.vue'
import TxCard from '@/components/layout/TxCard.vue'

export default {
  name: 'StockAnalysisSection',
  components: {
    LowStockTable,
    LowestStockChart,
    StockExportButtons,
    TxCard
  },
  props: {
    lowStockProducts: {
      type: Array,
      default: () => []
    },
    lowestStockProducts: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    onRefreshStock() {
      // Propagar al padre para que recargue los datos de stock
      this.$emit('refresh-stock')
    }
  }
}
</script>

<style scoped>
.stock-analysis-section {
  margin-bottom: 50px;
}

.section-header {
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e9ecef;
}

.section-title {
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
}

.section-title i {
  color: #3498db;
  margin-right: 10px;
}

.card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #dee2e6;
  border-radius: 12px 12px 0 0 !important;
  padding: 20px 25px;
}

.card-header h5 {
  color: #495057;
  font-weight: 600;
  margin: 0;
}

.card-body {
  padding: 25px;
}

/* Responsive */
@media (max-width: 768px) {
  .section-title {
    font-size: 1.5rem;
  }
  
  .card-header {
    padding: 15px 20px;
  }
  
  .card-body {
    padding: 20px;
  }
}
</style>
