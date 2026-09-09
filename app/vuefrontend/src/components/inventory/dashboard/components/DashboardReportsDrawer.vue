<template>
  <JRDrawer
    :visible="visible"
    header="Reports & exports"
    position="right"
    @update:visible="$emit('update:visible', $event)">
    <p class="jr-reports-lede">
      Download Excel reports without leaving the operational view. Pick a category, then export.
    </p>

    <div class="jr-reports-nav" role="tablist" aria-label="Report categories">
      <JRButton
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        size="sm"
        :variant="activeTab === tab.id ? 'primary' : 'ghost'"
        role="tab"
        :aria-selected="activeTab === tab.id"
        @click="activeTab = tab.id">
        {{ tab.label }}
      </JRButton>
    </div>

    <div v-show="activeTab === 'stock'" class="jr-reports-panel" role="tabpanel">
      <h3 class="jr-reports-panel__title">Stock reports</h3>
      <StockExportButtons :loading="loading" />
    </div>

    <div v-show="activeTab === 'sales'" class="jr-reports-panel" role="tabpanel">
      <h3 class="jr-reports-panel__title">Sales reports</h3>
      <div class="jr-reports-period">
        <JRField label="Period" inputId="dash-export-sales-period">
          <JRSelect
            inputId="dash-export-sales-period"
            v-model="salesPeriod"
            :options="periodOptions"
            optionLabel="label"
            optionValue="value"
          />
        </JRField>
      </div>
      <SalesExportButtons :period="salesPeriod" :loading="loading" />
    </div>

    <div v-show="activeTab === 'parties'" class="jr-reports-panel" role="tabpanel">
      <h3 class="jr-reports-panel__title">Customer & supplier reports</h3>
      <CustomersSuppliersExportButtons active-tab="customers" :loading="loading" />
    </div>

    <div v-show="activeTab === 'movements'" class="jr-reports-panel" role="tabpanel">
      <h3 class="jr-reports-panel__title">Product movements</h3>
      <ProductMovementsReport />
    </div>
  </JRDrawer>
</template>

<script>
import { JRDrawer, JRButton, JRField, JRSelect } from '@ui';
import StockExportButtons from './StockExportButtons.vue';
import SalesExportButtons from './SalesExportButtons.vue';
import CustomersSuppliersExportButtons from './CustomersSuppliersExportButtons.vue';
import ProductMovementsReport from './ProductMovementsReport.vue';

export default {
  name: 'DashboardReportsDrawer',
  components: {
    JRDrawer,
    JRButton,
    JRField,
    JRSelect,
    StockExportButtons,
    SalesExportButtons,
    CustomersSuppliersExportButtons,
    ProductMovementsReport,
  },
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    periodDays: {
      type: Number,
      default: 30,
    },
  },
  emits: ['update:visible'],
  data() {
    return {
      activeTab: 'stock',
      salesPeriod: this.periodDays || 30,
      periodOptions: [
        { label: 'Last 30 days', value: 30 },
        { label: 'Last 60 days', value: 60 },
        { label: 'Last 90 days', value: 90 },
        { label: 'Last year', value: 365 },
      ],
      tabs: [
        { id: 'stock', label: 'Stock' },
        { id: 'sales', label: 'Sales' },
        { id: 'parties', label: 'Customers' },
        { id: 'movements', label: 'Movements' },
      ],
    };
  },
  watch: {
    periodDays(value) {
      const days = Number(value);
      if (Number.isFinite(days) && days > 0) {
        this.salesPeriod = days;
      }
    },
  },
};
</script>

<style scoped>
.jr-reports-lede {
  margin: 0 0 1rem;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-jr-muted);
}

.jr-reports-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-reports-panel__title {
  margin: 0 0 0.85rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-reports-period {
  max-width: 14rem;
  margin-bottom: 0.85rem;
}
</style>
