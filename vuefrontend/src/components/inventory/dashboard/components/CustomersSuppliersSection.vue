<template>
  <div class="customers-suppliers-section">
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem"></div>
      <div class="mt-2">
        <small class="text-muted">Loading products...</small>
      </div>
    </div>
    <div class="section-header">
      <h2 class="section-title">Top Customers and Suppliers</h2>
    </div>

    <!-- Tabs para alternar entre vistas -->
    <div class="chart-tabs mb-4">
      <div class="card">
        <div class="card-header">
          <ul class="nav nav-tabs card-header-tabs" role="tablist">
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'customers' }"
                @click="activeTab = 'customers'"
                type="button">
                <i class="fas fa-users"></i>
                Top Customers
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'suppliers' }"
                @click="activeTab = 'suppliers'"
                type="button">
                <i class="fas fa-truck"></i>
                Top Suppliers
              </button>
            </li>
            <li class="nav-item">
              <button
                class="nav-link"
                :class="{ active: activeTab === 'comparison' }"
                @click="activeTab = 'comparison'"
                type="button">
                <i class="fas fa-chart-line"></i>
                Comparison
              </button>
            </li>
          </ul>
        </div>
        <div class="card-body">
          <!-- Customers Tab -->
          <div v-show="activeTab === 'customers'" class="tab-content">
            <TopCustomersChart
              :customers="customersData.topCustomers"
              :metrics="customersData.metrics"
              :loading="loading"
              @customer-clicked="onCustomerClicked"
              @refresh="onRefreshCustomersSuppliers" />
          </div>

          <!-- Suppliers Tab -->
          <div v-show="activeTab === 'suppliers'" class="tab-content">
            <TopSuppliersChart
              :suppliers="suppliersData.topSuppliers"
              :metrics="suppliersData.metrics"
              :loading="loading"
              @supplier-clicked="onSupplierClicked"
              @refresh="onRefreshCustomersSuppliers" />
          </div>

          <!-- Comparison Tab -->
          <div v-show="activeTab === 'comparison'" class="tab-content">
            <CustomersSuppliersComparison
              :comparison-data="comparisonData"
              :loading="loading"
              @refresh="onRefreshCustomersSuppliers" />
          </div>
        </div>
      </div>
    </div>

    <!-- Export Reports -->
    <div class="export-section">
      <div class="card">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="fas fa-file-excel text-success"></i>
            Export Customer and Supplier Reports
          </h5>
        </div>
        <div class="card-body">
          <CustomersSuppliersExportButtons :active-tab="activeTab" :loading="loading" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import TopCustomersChart from './TopCustomersChart.vue';
  import TopSuppliersChart from './TopSuppliersChart.vue';
  import CustomersSuppliersComparison from './CustomersSuppliersComparison.vue';
  import CustomersSuppliersExportButtons from './CustomersSuppliersExportButtons.vue';

  export default {
    name: 'CustomersSuppliersSection',
    components: {
      TopCustomersChart,
      TopSuppliersChart,
      CustomersSuppliersComparison,
      CustomersSuppliersExportButtons,
    },
    props: {
      customersData: {
        type: Object,
        default: () => ({
          topCustomers: [],
          metrics: {},
        }),
      },
      suppliersData: {
        type: Object,
        default: () => ({
          topSuppliers: [],
          metrics: {},
        }),
      },
      comparisonData: {
        type: Object,
        default: () => ({}),
      },
      loading: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        activeTab: 'customers',
      };
    },
    methods: {
      onCustomerClicked(customer) {
        this.$emit('customer-clicked', customer);
      },

      onSupplierClicked(supplier) {
        this.$emit('supplier-clicked', supplier);
      },
      onRefreshCustomersSuppliers() {
        // Propagar al padre para que recargue clientes, proveedores y comparación
        this.$emit('refresh-customers-suppliers');
      },
    },
  };
</script>

<style scoped>
  .customers-suppliers-section {
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
    color: #9b59b6;
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
    padding: 0;
  }

  .nav-tabs {
    border-bottom: none;
    margin: 0;
  }

  .nav-tabs .nav-link {
    border: none;
    border-radius: 0;
    padding: 15px 25px;
    color: #6c757d;
    font-weight: 500;
    transition: all 0.3s ease;
    background: transparent;
  }

  .nav-tabs .nav-link:hover {
    border-color: transparent;
    color: #495057;
    background-color: rgba(0, 0, 0, 0.05);
  }

  .nav-tabs .nav-link.active {
    color: #495057;
    background-color: white;
    border-bottom: 2px solid #007bff;
    font-weight: 600;
  }

  .nav-tabs .nav-link i {
    margin-right: 8px;
  }

  .card-body {
    padding: 25px;
  }

  .tab-content {
    min-height: 400px;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .section-title {
      font-size: 1.5rem;
    }

    .nav-tabs {
      flex-direction: column;
    }

    .nav-tabs .nav-link {
      border-radius: 8px 8px 0 0;
      margin-bottom: 2px;
    }

    .nav-tabs .nav-link.active {
      border-bottom: none;
      border-right: 2px solid #007bff;
    }

    .card-body {
      padding: 20px;
    }
  }

  @media (max-width: 576px) {
    .nav-tabs .nav-link {
      padding: 12px 20px;
      font-size: 0.9rem;
    }

    .nav-tabs .nav-link i {
      margin-right: 5px;
    }
  }
</style>
