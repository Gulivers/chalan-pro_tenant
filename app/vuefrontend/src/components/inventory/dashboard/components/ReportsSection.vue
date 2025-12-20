<template>
  <div class="reports-section">
    <div class="section-header">
      <h2 class="section-title">
        <i class="fas fa-chart-bar"></i>
        Advanced Reports
      </h2>
    </div>

    <!-- Product Movements Report -->
    <div class="product-movements-report mb-4">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-exchange-alt text-primary"></i>
            Product Movements Report
          </h5>
        </div>
        <div class="card-body">
          <ProductMovementsReport 
            @export-requested="onExportRequested"
          />
        </div>
      </div>
    </div>

    <!-- Additional Reports (hidden) -->
    <div class="additional-reports" v-if="false">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-file-alt text-info"></i>
            Additional Reports
          </h5>
        </div>
        <div class="card-body">
          <AdditionalReportsGrid 
            :loading="loading"
            @report-requested="onReportRequested"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ProductMovementsReport from './ProductMovementsReport.vue'
import AdditionalReportsGrid from './AdditionalReportsGrid.vue'

export default {
  name: 'ReportsSection',
  components: {
    ProductMovementsReport,
    AdditionalReportsGrid
  },
  props: {
    // Removed props - ProductMovementsReport manages its own data now
  },
  methods: {
    onFilterChanged(filters) {
      this.$emit('filter-changed', filters)
    },
    
    onExportRequested(exportType) {
      this.$emit('export-requested', exportType)
    },
    
    onReportRequested(reportType) {
      this.$emit('report-requested', reportType)
    }
  }
}
</script>

<style scoped>
.reports-section {
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
  color: #17a2b8;
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
