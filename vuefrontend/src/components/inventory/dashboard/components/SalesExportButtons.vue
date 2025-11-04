<template>
  <div class="sales-export-buttons">
    <div class="row">
      <div class="col-md-6 mb-3">
        <div class="export-card">
          <div class="export-icon">
            <i class="fas fa-chart-bar"></i>
          </div>
          <div class="export-content">
            <h6>Sales by Product</h6>
            <p class="text-muted">Detailed sales report by product</p>
            <button class="btn btn-outline-success" @click="exportSalesByProduct" :disabled="loading">
              <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="excel-icon" />
              Download Excel
            </button>
          </div>
        </div>
      </div>

      <div class="col-md-6 mb-3">
        <div class="export-card">
          <div class="export-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="export-content">
            <h6>Sales by Customer</h6>
            <p class="text-muted">Sales report grouped by customer</p>
            <button class="btn btn-outline-primary" @click="exportSalesByCustomer" :disabled="loading">
              <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="excel-icon" />
              Download Excel
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-md-6 mb-3">
        <div class="export-card">
          <div class="export-icon">
            <i class="fas fa-calendar"></i>
          </div>
          <div class="export-content">
            <h6>Sales by Period</h6>
            <p class="text-muted">Sales report by date range</p>
            <button class="btn btn-outline-info" @click="exportSalesByPeriod" :disabled="loading">
              <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="excel-icon" />
              Download Excel
            </button>
          </div>
        </div>
      </div>

      <div class="col-md-6 mb-3">
        <div class="export-card">
          <div class="export-icon">
            <i class="fas fa-chart-pie"></i>
          </div>
          <div class="export-content">
            <h6>Financial Summary</h6>
            <p class="text-muted">Complete report with financial analysis</p>
            <button class="btn btn-outline-warning" @click="exportFinancialSummary" :disabled="loading">
              <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="excel-icon" />
              Download Excel
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem"></div>
        <div class="mt-2">
          <small class="text-muted">Generating file...</small>
        </div>
        <p class="mt-2">Generating sales report...</p>
      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios';

  export default {
    name: 'SalesExportButtons',
    props: {
      period: {
        type: Number,
        default: 30,
      },
      loading: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        exportLoading: false,
      };
    },
    methods: {
      async exportSalesByProduct() {
        await this.performExport('/api/export/sales-by-product/', 'sales_by_product');
      },

      async exportSalesByCustomer() {
        await this.performExport('/api/export/sales-by-customer/', 'sales_by_customer');
      },

      async exportSalesByPeriod() {
        await this.performExport('/api/export/sales-by-period/', 'sales_by_period');
      },

      async exportFinancialSummary() {
        await this.performExport('/api/export/financial-summary/', 'financial_summary');
      },

      async performExport(url, filename) {
        try {
          this.exportLoading = true;

          const params = new URLSearchParams({
            period_days: this.period,
          });

          const response = await axios.get(`${url}?${params.toString()}`, {
            responseType: 'blob',
          });

          // Crear blob y descargar
          const blob = new Blob([response.data], {
            type: response.headers['content-type'],
          });

          const link = document.createElement('a');
          link.href = window.URL.createObjectURL(blob);
          link.download = `${filename}_${this.getCurrentDate()}.xlsx`;
          link.click();
          window.URL.revokeObjectURL(link.href);

          this.notifyToastSuccess?.('Sales report downloaded successfully');
        } catch (error) {
          console.error('Error exporting sales data:', error);
          alert('Error generating sales report');
        } finally {
          this.exportLoading = false;
        }
      },

      getCurrentDate() {
        const now = new Date();
        return now.toISOString().split('T')[0];
      },
    },
    computed: {
      isLoading() {
        return this.loading || this.exportLoading;
      },
    },
  };
</script>

<style scoped>
  .sales-export-buttons {
    position: relative;
  }

  .excel-icon {
    width: 18px;
    height: 18px;
    margin-right: 8px;
    vertical-align: middle;
  }

  .export-card {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 12px;
    padding: 25px;
    height: 100%;
    display: flex;
    align-items: center;
    gap: 20px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .export-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }

  .export-icon {
    font-size: 2.5rem;
    color: #6c757d;
    min-width: 60px;
    text-align: center;
  }

  .export-content {
    flex: 1;
  }

  .export-content h6 {
    color: #495057;
    font-weight: 600;
    margin-bottom: 8px;
  }

  .export-content p {
    font-size: 0.9rem;
    margin-bottom: 15px;
    line-height: 1.4;
  }

  .btn {
    border-radius: 8px;
    font-weight: 500;
    padding: 10px 20px;
    transition: all 0.3s ease;
  }

  .btn:hover {
    transform: translateY(-1px);
  }

  .btn-success {
    background-color: #28a745;
    border-color: #28a745;
  }

  .btn-primary {
    background-color: #007bff;
    border-color: #007bff;
  }

  .btn-info {
    background-color: #17a2b8;
    border-color: #17a2b8;
  }

  .btn-warning {
    background-color: #ffc107;
    border-color: #ffc107;
    color: #212529;
  }

  .loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    z-index: 1000;
  }

  .loading-content {
    text-align: center;
  }

  .loading-content p {
    color: #6c757d;
    font-weight: 500;
    margin: 0;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .export-card {
      flex-direction: column;
      text-align: center;
      gap: 15px;
      padding: 20px;
    }

    .export-icon {
      font-size: 2rem;
      min-width: auto;
    }

    .btn {
      width: 100%;
    }
  }

  @media (max-width: 576px) {
    .export-card {
      padding: 15px;
    }

    .export-icon {
      font-size: 1.8rem;
    }

    .export-content h6 {
      font-size: 1rem;
    }

    .export-content p {
      font-size: 0.8rem;
    }
  }
</style>
