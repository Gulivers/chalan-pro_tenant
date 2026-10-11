<template>
  <div class="jr-export-grid">
    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Sales by Product</h4>
      <p class="jr-export-item__desc">Detailed sales report by product</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportSalesByProduct">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Sales by Customer</h4>
      <p class="jr-export-item__desc">Sales report grouped by customer</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportSalesByCustomer">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Sales by Period</h4>
      <p class="jr-export-item__desc">Sales report by date range</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportSalesByPeriod">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Financial Summary</h4>
      <p class="jr-export-item__desc">Complete report with financial analysis</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportFinancialSummary">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div v-if="isLoading" class="jr-export-overlay">
      <p>Generating sales report…</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { JRButton } from '@ui';

export default {
  name: 'SalesExportButtons',
  components: { JRButton },
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
        this.notifyToastError?.('Error generating sales report');
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
.jr-export-grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.jr-export-item {
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface);
  padding: 1rem;
}

.jr-export-item__title {
  margin: 0 0 0.35rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-export-item__desc {
  margin: 0 0 0.85rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
  line-height: 1.4;
}

.excel-icon {
  margin-right: 0.4rem;
  vertical-align: middle;
}

.jr-export-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--color-jr-surface) 90%, transparent);
  z-index: 2;
}

.jr-export-overlay p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

@media (max-width: 767.98px) {
  .jr-export-grid {
    grid-template-columns: 1fr;
  }
}
</style>
