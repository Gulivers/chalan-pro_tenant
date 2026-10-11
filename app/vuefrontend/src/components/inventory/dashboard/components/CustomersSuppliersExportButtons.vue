<template>
  <div class="jr-export-grid">
    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Customers List</h4>
      <p class="jr-export-item__desc">Complete customers report with metrics</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportCustomersList">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Suppliers List</h4>
      <p class="jr-export-item__desc">Complete suppliers report with metrics</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportSuppliersList">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Comparative Analysis</h4>
      <p class="jr-export-item__desc">Detailed comparison between customers and suppliers</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportComparativeAnalysis">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div class="jr-export-item">
      <h4 class="jr-export-item__title">Trends</h4>
      <p class="jr-export-item__desc">Monthly trends analysis</p>
      <JRButton variant="secondary" :disabled="isLoading" @click="exportTrends">
        <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
        Download Excel
      </JRButton>
    </div>

    <div v-if="isLoading" class="jr-export-overlay">
      <p>Generating report…</p>
    </div>
  </div>
</template>

<script>
import { getAccessToken } from '@/auth/tokenHelpers';
import axios from 'axios';
import { JRButton } from '@ui';

export default {
  name: 'CustomersSuppliersExportButtons',
  components: { JRButton },
  props: {
    activeTab: {
      type: String,
      default: 'customers',
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
    async exportCustomersList() {
      await this.performExport('/api/export/customers-list/', 'customers_list');
    },

    async exportSuppliersList() {
      await this.performExport('/api/export/suppliers-list/', 'suppliers_list');
    },

    async exportComparativeAnalysis() {
      await this.performExport('/api/export/comparative-analysis/', 'comparative_analysis');
    },

    async exportTrends() {
      await this.performExport('/api/export/trends/', 'trends_analysis');
    },

    async performExport(url, filename) {
      try {
        this.exportLoading = true;

        const params = new URLSearchParams({
          active_tab: this.activeTab,
        });

        const response = await axios.get(`${url}?${params.toString()}`, {
          responseType: 'blob',
          headers: {
            Authorization: `Bearer ${getAccessToken()}`,
          },
        });

        if (!response || !response.data) {
          throw new Error('No data received from server');
        }

        let contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
        if (response.headers && response.headers['content-type']) {
          contentType = response.headers['content-type'];
        }

        const blob = new Blob([response.data], {
          type: contentType,
        });

        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = `${filename}_${this.getCurrentDate()}.xlsx`;
        link.click();
        window.URL.revokeObjectURL(link.href);

        this.notifyToastSuccess?.('Report downloaded successfully');
      } catch (error) {
        console.error('Error exporting data:', error);

        let errorMessage = 'Error generating report';

        if (error.response) {
          if (error.response.status === 404) {
            errorMessage = 'Export endpoint not found';
          } else if (error.response.status === 500) {
            errorMessage = 'Server error generating report';
          } else if (error.response.data) {
            try {
              if (typeof error.response.data === 'string') {
                errorMessage = error.response.data;
              } else if (error.response.data.error) {
                errorMessage = error.response.data.error;
              } else if (error.response.data.message) {
                errorMessage = error.response.data.message;
              }
            } catch (e) {
              errorMessage = `Server error: ${error.response.status}`;
            }
          }
        } else if (error.request) {
          errorMessage = 'Could not connect to server';
        } else if (error.message) {
          errorMessage = error.message;
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
