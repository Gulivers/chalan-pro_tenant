<template>
  <div class="product-movements-report">
    <div class="jr-dash-filters">
      <h4 class="jr-dash-filters__title">Search Filters</h4>
      <div class="jr-dash-filters__grid">
        <JRField v-slot="{ describedby, invalid }" label="Date From" inputId="dash-mov-start">
          <JRInput
            inputId="dash-mov-start"
            v-model="filters.startDate"
            type="date"
            :invalid="invalid"
            :ariaDescribedby="describedby"
            @update:modelValue="onFilterChange"
          />
        </JRField>

        <JRField v-slot="{ describedby, invalid }" label="Date To" inputId="dash-mov-end">
          <JRInput
            inputId="dash-mov-end"
            v-model="filters.endDate"
            type="date"
            :invalid="invalid"
            :ariaDescribedby="describedby"
            @update:modelValue="onFilterChange"
          />
        </JRField>

        <JRField v-slot="{ describedby, invalid }" label="Document Type" inputId="dash-mov-doctype">
          <JRSelect
            inputId="dash-mov-doctype"
            v-model="filters.documentType"
            :options="documentTypeOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="All"
            showClear
            :invalid="invalid"
            :ariaDescribedby="describedby"
            @update:modelValue="onFilterChange"
          />
        </JRField>

        <JRField v-slot="{ describedby, invalid }" label="Warehouse" inputId="dash-mov-warehouse">
          <JRSelect
            inputId="dash-mov-warehouse"
            v-model="filters.warehouseId"
            :options="warehouseOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="All"
            showClear
            :invalid="invalid"
            :ariaDescribedby="describedby"
            @update:modelValue="onFilterChange"
          />
        </JRField>
      </div>

      <div class="jr-dash-filters__actions">
        <JRButton variant="primary" size="sm" @click="applyFilters">Search</JRButton>
        <JRButton variant="secondary" size="sm" @click="resetFilters">Clear</JRButton>
      </div>
    </div>

    <div class="jr-dash-results">
      <div class="jr-dash-results__header">
        <h4 class="jr-dash-results__title">Product Movements</h4>
        <JRButton variant="secondary" size="sm" :disabled="loading" @click="exportToExcel">
          <img src="@/assets/img/microsoft-excel-icon.svg" alt="" width="16" height="16" class="excel-icon" />
          Download Excel
        </JRButton>
      </div>

      <div v-if="loading" class="jr-dash-state">Loading…</div>

      <JREmptyState
        v-else-if="movements.length === 0"
        title="No movements found"
        description="No movements found with the applied filters"
      />

      <div v-else class="jr-dash-table-wrap">
        <table class="jr-dash-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Type</th>
              <th>Product</th>
              <th>SKU</th>
              <th>Quantity</th>
              <th>Warehouse</th>
              <th>Document</th>
              <th>User</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="movement in movements"
              :key="movement.id"
              :class="getMovementRowClass(movement)"
            >
              <td>{{ formatDate(movement.date) }}</td>
              <td>{{ formatTime(movement.time) }}</td>
              <td>
                <JRBadge
                  :value="movement.movement_type"
                  :severity="getMovementSeverity(movement)"
                />
              </td>
              <td>
                <strong>{{ movement.product.name }}</strong>
                <br />
                <span class="jr-dash-muted">{{ movement.product.sku }}</span>
              </td>
              <td><code>{{ movement.product.sku }}</code></td>
              <td>
                <span :class="getQuantityClass(movement)">
                  {{ formatNumber(movement.quantity) }}
                </span>
              </td>
              <td>{{ movement.warehouse.name }}</td>
              <td><code>{{ movement.document || 'N/A' }}</code></td>
              <td>
                <span class="jr-dash-muted">{{ movement.created_by.username }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { JRField, JRInput, JRSelect, JRButton, JRBadge, JREmptyState } from '@ui';

export default {
  name: 'ProductMovementsReport',
  components: {
    JRField,
    JRInput,
    JRSelect,
    JRButton,
    JRBadge,
    JREmptyState,
  },
  props: {},
  data() {
    return {
      filters: {
        startDate: this.getDefaultStartDate(),
        endDate: this.getDefaultEndDate(),
        documentType: null,
        warehouseId: null,
      },
      warehouses: [],
      documentTypes: [],
      movements: [],
      loading: false,
    };
  },
  computed: {
    documentTypeOptions() {
      return (this.documentTypes || []).map((docType) => ({
        label: docType.description,
        value: docType.id,
      }));
    },
    warehouseOptions() {
      return (this.warehouses || []).map((warehouse) => ({
        label: warehouse.name,
        value: warehouse.id,
      }));
    },
  },
  async mounted() {
    await this.loadWarehouses();
    await this.loadDocumentTypes();
    this.applyFilters();
  },
  methods: {
    getDefaultStartDate() {
      const date = new Date();
      date.setDate(date.getDate() - 30);
      return date.toISOString().split('T')[0];
    },

    getDefaultEndDate() {
      return new Date().toISOString().split('T')[0];
    },

    async loadWarehouses() {
      try {
        console.log('Loading warehouses...');
        const response = await axios.get('/api/warehouses/?is_active=true');
        console.log('Warehouses response:', response.data);
        this.warehouses = response.data.results || response.data;
        console.log('Warehouses loaded:', this.warehouses);
      } catch (error) {
        console.error('Error loading warehouses:', error);
      }
    },

    async loadDocumentTypes() {
      try {
        console.log('Loading document types...');
        const response = await axios.get('/api/document-types/?is_active=true');
        console.log('Document types response:', response.data);
        this.documentTypes = response.data.results || response.data;
        console.log('Document types loaded:', this.documentTypes);
      } catch (error) {
        console.error('Error loading document types:', error);
      }
    },

    async loadMovements() {
      try {
        this.loading = true;
        console.log('Loading movements with filters:', this.filters);

        const params = new URLSearchParams({
          start_date: this.filters.startDate,
          end_date: this.filters.endDate,
        });

        if (this.filters.documentType) {
          params.append('document_type', this.filters.documentType);
        }

        if (this.filters.warehouseId) {
          params.append('warehouse_id', this.filters.warehouseId);
        }

        const url = `/api/dashboard/product-movements/?${params.toString()}`;
        console.log('Requesting movements from:', url);

        const response = await axios.get(url);
        console.log('Movements response:', response.data);

        this.movements = Array.isArray(response.data) ? response.data : [];
        console.log('Movements loaded:', this.movements.length, 'records');
      } catch (error) {
        console.error('Error loading movements:', error);
        this.movements = [];
      } finally {
        this.loading = false;
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      if (typeof dateString === 'string') {
        const datePart = dateString.split('T')[0];
        const [year, month, day] = datePart.split('-');
        return `${month}/${day}/${year}`;
      }
      console.warn('Unexpected date format:', dateString);
      return 'N/A';
    },

    formatTime(timeString) {
      if (!timeString) return 'N/A';
      return timeString.substring(0, 5);
    },

    formatNumber(value) {
      if (!value) return '0';
      return new Intl.NumberFormat('en-US').format(value);
    },

    getMovementRowClass(movement) {
      if (movement.movement_type === 'Entrada') return 'is-success';
      if (movement.movement_type === 'Salida') return 'is-danger';
      return 'is-info';
    },

    getMovementSeverity(movement) {
      if (movement.movement_type === 'Entrada') return 'success';
      if (movement.movement_type === 'Salida') return 'danger';
      return 'info';
    },

    getQuantityClass(movement) {
      if (movement.quantity > 0) return 'is-success-text';
      if (movement.quantity < 0) return 'is-danger-text';
      return 'jr-dash-muted';
    },

    onFilterChange() {
      this.applyFilters();
    },

    applyFilters() {
      this.loadMovements();
    },

    resetFilters() {
      this.filters = {
        startDate: this.getDefaultStartDate(),
        endDate: this.getDefaultEndDate(),
        documentType: null,
        warehouseId: null,
      };
      this.applyFilters();
    },

    async exportToExcel() {
      try {
        const params = new URLSearchParams({
          start_date: this.filters.startDate,
          end_date: this.filters.endDate,
        });
        if (this.filters.documentType) params.append('document_type', this.filters.documentType);
        if (this.filters.warehouseId) params.append('warehouse_id', this.filters.warehouseId);

        const url = `/api/export/product-movements/?${params.toString()}`;
        const response = await axios.get(url, {
          responseType: 'blob',
          headers: {
            Authorization: `Token ${localStorage.getItem('authToken')}`,
          },
        });

        if (!response || !response.data) throw new Error('No data received');

        const contentType =
          (response.headers && response.headers['content-type']) ||
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
        const blob = new Blob([response.data], { type: contentType });
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = `product_movements_report_${new Date().toISOString().split('T')[0]}.xlsx`;
        link.click();
        window.URL.revokeObjectURL(link.href);
      } catch (error) {
        console.error('Error exporting to Excel:', error);
        this.notifyToastError?.('Error exporting to Excel. Please try again.');
      }
    },
  },
};
</script>

<style scoped>
.product-movements-report {
  min-height: 400px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.jr-dash-filters,
.jr-dash-results {
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface);
  padding: 1rem;
}

.jr-dash-filters__title,
.jr-dash-results__title {
  margin: 0 0 0.85rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-dash-filters__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
}

.jr-dash-filters__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 0.85rem;
}

.jr-dash-results__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 0.85rem;
}

.jr-dash-results__header .jr-dash-results__title {
  margin: 0;
}

.excel-icon {
  margin-right: 0.4rem;
  vertical-align: middle;
}

.jr-dash-state {
  padding: 1rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-dash-muted {
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-dash-table-wrap {
  overflow: auto;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel, 0.75rem);
}

.jr-dash-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  margin: 0;
}

.jr-dash-table th,
.jr-dash-table td {
  padding: 0.55rem 0.65rem;
  border-bottom: 1px solid var(--color-jr-border);
  text-align: left;
  vertical-align: middle;
}

.jr-dash-table thead th {
  background: var(--color-jr-surface-muted);
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-dash-table tbody tr.is-success {
  background: var(--color-jr-success-subtle);
}

.jr-dash-table tbody tr.is-danger {
  background: var(--color-jr-danger-subtle);
}

.jr-dash-table tbody tr.is-info {
  background: var(--color-jr-info-subtle);
}

.is-success-text {
  color: var(--color-jr-success-text);
  font-weight: 600;
}

.is-danger-text {
  color: var(--color-jr-danger-text);
  font-weight: 600;
}

@media (max-width: 1023.98px) {
  .jr-dash-filters__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 575.98px) {
  .jr-dash-filters__grid {
    grid-template-columns: 1fr;
  }
}
</style>
