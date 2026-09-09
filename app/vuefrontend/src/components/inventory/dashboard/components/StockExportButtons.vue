<template>
  <div class="jr-export-grid">
    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Stock by Warehouse</h4>
      <p class="jr-export-item__desc">Export current stock grouped by warehouse</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportStockByWarehouse">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Complete Stock</h4>
      <p class="jr-export-item__desc">Export entire inventory with details</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportCompleteStock">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Low Stock Products</h4>
      <p class="jr-export-item__desc">Only products below reorder level</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportLowStockProducts">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Stock Report</h4>
      <p class="jr-export-item__desc">Complete report with analysis</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportStockReport">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div v-if="isLoading" class="jr-export-overlay">
      <p>Loading…</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { JRButton } from '@ui';

export default {
  name: 'StockExportButtons',
  components: { JRButton },
  props: {
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
    async exportStockByWarehouse() {
      await this.performExport('/api/export/stock-by-warehouse/', 'stock_por_almacen');
    },

    async exportCompleteStock() {
      await this.performExport('/api/export/complete-stock/', 'stock_completo');
    },

    async exportLowStockProducts() {
      await this.performExport('/api/export/low-stock-products/', 'productos_stock_bajo');
    },

    async exportStockReport() {
      await this.performExport('/api/export/stock-report/', 'reporte_stock');
    },

    async performExport(url, filename) {
      try {
        this.exportLoading = true;

        const response = await axios.get(url, {
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

        this.notifyToastSuccess?.('Stock report downloaded successfully');
      } catch (error) {
        console.error('Error exporting data:', error);

        let errorMessage = 'Error generating Excel file';

        if (error.response) {
          if (error.response.data && error.response.data.error) {
            errorMessage = error.response.data.error;
          } else if (error.response.status === 404) {
            errorMessage = 'Export endpoint not found';
          } else if (error.response.status === 500) {
            errorMessage = 'Server error while generating file';
          } else {
            errorMessage = `Server error: ${error.response.status}`;
          }
        } else if (error.request) {
          errorMessage = 'No response from server';
        } else {
          errorMessage = error.message || 'Unknown error occurred';
        }

        this.notifyToastError?.(errorMessage);
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
