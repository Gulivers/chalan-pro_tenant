<template>
  <div class="inventory-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <h1 class="h1 mb-5 py-2">Inventory Dashboard</h1>
    </div>
    <!-- Page Heading -->

    <!-- Main Metrics -->
    <InventoryMetricsCards v-if="hasPermission('appinventory.view_product')" :metrics="metrics" :loading="loading" />

    <!-- Section: What Stock Do We Have? -->
    <div v-if="hasPermission('appinventory.view_product')">
      <StockAnalysisSection
        :low-stock-products="lowStockProducts"
        :lowest-stock-products="lowestStockProducts"
        :loading="loading"
        @refresh-stock="loadStockData" />
    </div>
    <div v-else class="alert alert-warning">
      <i class="fas fa-exclamation-triangle"></i>
      You don't have permission to view stock analysis. Required: appinventory.view_product
    </div>

    <!-- Section: What Have We Sold? -->
    <SalesAnalysisSection
      v-if="hasPermission('apptransactions.view_document')"
      :sales-data="salesData"
      :loading="loading"
      @refresh-sales="loadSalesData" />

    <!-- Section: Top Customers and Suppliers -->
    <CustomersSuppliersSection
      v-if="hasPermission('apptransactions.view_document')"
      :customers-data="customersData"
      :suppliers-data="suppliersData"
      :comparison-data="comparisonData"
      :loading="loading"
      @refresh-customers-suppliers="loadCustomersSuppliersData" />

    <!-- Section: Advanced Reports -->
    <ReportsSection
      v-if="hasPermission('appinventory.view_product') || hasPermission('apptransactions.view_document')" />
  </div>
</template>

<script>
  import axios from 'axios';
  import InventoryMetricsCards from './components/InventoryMetricsCards.vue';
  import StockAnalysisSection from './components/StockAnalysisSection.vue';
  import SalesAnalysisSection from './components/SalesAnalysisSection.vue';
  import CustomersSuppliersSection from './components/CustomersSuppliersSection.vue';
  import ReportsSection from './components/ReportsSection.vue';

  export default {
    name: 'InventoryDashboard',
    components: {
      InventoryMetricsCards,
      StockAnalysisSection,
      SalesAnalysisSection,
      CustomersSuppliersSection,
      ReportsSection,
    },
    data() {
      return {
        loading: true,
        metrics: {},
        lowStockProducts: [],
        lowestStockProducts: [],
        salesData: {},
        customersData: {},
        suppliersData: {},
        comparisonData: [],
      };
    },
    async mounted() {
      await this.loadDashboardData();
    },
    methods: {
      async loadDashboardData() {
        try {
          this.loading = true;

          // Cargar datos en paralelo
          await Promise.all([
            this.loadMetrics(),
            this.loadStockData(),
            this.loadSalesData(),
            this.loadCustomersSuppliersData(),
            // loadMovementsData() removed - ProductMovementsReport manages its own data
          ]);
        } catch (error) {
          console.error('Error loading dashboard data:', error);
          this.$toast.error('Error loading dashboard data');
        } finally {
          this.loading = false;
        }
      },

      async loadMetrics() {
        try {
          const response = await axios.get('/api/dashboard/metrics/');
          this.metrics = response.data || {};
        } catch (error) {
          console.error('Error loading metrics:', error);
          this.metrics = {};
        }
      },

      async loadStockData() {
        try {
          const [lowStockResponse, lowestStockResponse] = await Promise.all([
            axios.get('/api/dashboard/low-stock-products/'),
            axios.get('/api/dashboard/lowest-stock-products/'),
          ]);
          this.lowStockProducts = Array.isArray(lowStockResponse.data) ? lowStockResponse.data : [];
          this.lowestStockProducts = Array.isArray(lowestStockResponse.data) ? lowestStockResponse.data : [];
        } catch (error) {
          console.error('Error loading stock data:', error);
          this.lowStockProducts = [];
          this.lowestStockProducts = [];
        }
      },

      async loadSalesData() {
        try {
          const response = await axios.get('/api/dashboard/sales-analysis/');
          this.salesData = response.data || {};
        } catch (error) {
          console.error('Error loading sales data:', error);
          this.salesData = {};
        }
      },

      async loadCustomersSuppliersData() {
        try {
          const [customersResponse, suppliersResponse, comparisonResponse] = await Promise.all([
            axios.get('/api/dashboard/top-customers/'),
            axios.get('/api/dashboard/top-suppliers/'),
            axios.get('/api/dashboard/customers-suppliers-comparison/'),
          ]);
          this.customersData = customersResponse.data || {};
          this.suppliersData = suppliersResponse.data || {};
          this.comparisonData = Array.isArray(comparisonResponse.data) ? comparisonResponse.data : [];
        } catch (error) {
          console.error('Error loading customers/suppliers data:', error);
          // Ensure comparisonData is always an array
          this.comparisonData = [];
        }
      },

    },
  };
</script>

<style scoped>
  .inventory-dashboard {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
    background-color: #f8f9fa;
    min-height: 100vh;
  }

  .dashboard-header {
    margin-bottom: 30px;
    text-align: center;
  }

  .dashboard-title {
    color: #2c3e50;
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
  }

  .dashboard-title i {
    color: #3498db;
    font-size: 2.2rem;
  }

  .btn {
    padding: 10px 20px;
    border-radius: 4x;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
  }

  .btn-outline-dark {
    border: 2px solid #343a40;
    color: #343a40;
  }

  .btn-outline-dark:hover {
    background-color: #343a40;
    color: white;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .dashboard-header {
      flex-direction: column;
      gap: 15px;
      text-align: center;
    }

    .dashboard-title {
      font-size: 2rem;
    }
  }
</style>
