<template>
  <div class="sales-analysis-section">
    <i class="fas fa-chart-line"></i>

    <!-- Top 25 Best Selling Products -->
    <div class="top-selling-products mb-4">
      <div class="card">
        <div class="card-header">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="fas fa-chart-bar text-success"></i>
              Top 25 Best Selling Products
            </h5>
            <div class="period-selector">
              <select v-model="selectedPeriod" @change="onPeriodChange" class="form-control form-control-sm">
                <option value="30">Last 30 days</option>
                <option value="60">Last 60 days</option>
                <option value="90">Last 90 days</option>
                <option value="365">Last year</option>
              </select>
            </div>
          </div>
        </div>
        <div class="card-body">
          <TopSellingChart
            :products="salesData.topSellingProducts"
            :period="selectedPeriod"
            :loading="loading"
            @refresh="onRefreshSales" />
        </div>
      </div>
    </div>

    <!-- Sales Metrics -->
    <div class="sales-metrics mb-4">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-chart-pie text-info"></i>
            Sales Metrics
          </h5>
        </div>
        <div class="card-body">
          <SalesMetricsCards :metrics="salesData.metrics" :loading="loading" />
        </div>
      </div>
    </div>

    <!-- Export Sales Reports -->
    <div class="sales-export-section">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-file-excel text-success"></i>
            Export Sales Reports
          </h5>
        </div>
        <div class="card-body">
          <SalesExportButtons :period="selectedPeriod" :loading="loading" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import TopSellingChart from './TopSellingChart.vue';
  import SalesMetricsCards from './SalesMetricsCards.vue';
  import SalesExportButtons from './SalesExportButtons.vue';

  export default {
    name: 'SalesAnalysisSection',
    components: {
      TopSellingChart,
      SalesMetricsCards,
      SalesExportButtons,
    },
    props: {
      salesData: {
        type: Object,
        default: () => ({
          topSellingProducts: [],
          metrics: {},
        }),
      },
      loading: {
        type: Boolean,
        default: false,
      },
    },
    watch: {
      salesData: {
        handler(newData) {
          // console.log('SalesAnalysisSection salesData changed:', newData);
        },
        deep: true,
      },
    },
    data() {
      return {
        selectedPeriod: 30,
      };
    },
    methods: {
      onPeriodChange() {
        this.$emit('period-changed', this.selectedPeriod);
      },

      onRefreshSales() {
        this.$emit('refresh-sales');
      },
    },
  };
</script>

<style scoped>
  .sales-analysis-section {
    margin-bottom: 50px;
  }

  .section-title {
    color: #2c3e50;
    font-size: 1.8rem;
    font-weight: 600;
    margin: 0;
  }

  .section-title i {
    color: #28a745;
    margin-right: 10px;
  }

  .card {
    border: none;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
  }

  .card-header {
    background: linear-gradient(135deg, #e9ecef#e9ecef 100%);
    border-bottom: 1px solid #ced4da;
    border-radius: 12px 12px 0 0 !important;
    padding: 20px 25px;
  }

  .card-header h5 {
    color: #495057;
    font-weight: 40;
    margin: 0;
  }

  .period-selector {
    min-width: 150px;
  }

  .form-control-sm {
    border-radius: 6px;
    border: 1px solid #ced4da;
    font-size: 0.9rem;
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

    .card-header .d-flex {
      flex-direction: column;
      gap: 15px;
      align-items: flex-start !important;
    }

    .period-selector {
      width: 100%;
    }

    .card-body {
      padding: 20px;
    }

  }
</style>
