<template>
  <JRSection title="Customers & suppliers">
    <div class="jr-dash-tabs" role="tablist" aria-label="Customers and suppliers">
      <JRButton
        :variant="activeTab === 'customers' ? 'primary' : 'ghost'"
        size="sm"
        type="button"
        role="tab"
        :aria-selected="activeTab === 'customers'"
        @click="activeTab = 'customers'"
      >
        Customers
      </JRButton>
      <JRButton
        :variant="activeTab === 'suppliers' ? 'primary' : 'ghost'"
        size="sm"
        type="button"
        role="tab"
        :aria-selected="activeTab === 'suppliers'"
        @click="activeTab = 'suppliers'"
      >
        Suppliers
      </JRButton>
      <JRButton
        :variant="activeTab === 'comparison' ? 'primary' : 'ghost'"
        size="sm"
        type="button"
        role="tab"
        :aria-selected="activeTab === 'comparison'"
        @click="activeTab = 'comparison'"
      >
        Comparison
      </JRButton>
    </div>

    <div v-if="loading" class="jr-dash-state" aria-live="polite">Loading…</div>

    <div v-show="activeTab === 'customers'" role="tabpanel">
      <TopCustomersChart
        :customers="customersData.topCustomers"
        :metrics="customersData.metrics"
        :loading="loading"
        @customer-clicked="onCustomerClicked"
        @refresh="onRefreshCustomersSuppliers"
      />
    </div>

    <div v-show="activeTab === 'suppliers'" role="tabpanel">
      <TopSuppliersChart
        :suppliers="suppliersData.topSuppliers"
        :metrics="suppliersData.metrics"
        :loading="loading"
        @supplier-clicked="onSupplierClicked"
        @refresh="onRefreshCustomersSuppliers"
      />
    </div>

    <div v-show="activeTab === 'comparison'" role="tabpanel">
      <CustomersSuppliersComparison
        :comparison-data="comparisonData"
        :loading="loading"
        @refresh="onRefreshCustomersSuppliers"
      />
    </div>
  </JRSection>
</template>

<script>
import { JRSection, JRButton } from '@ui';
import TopCustomersChart from './TopCustomersChart.vue';
import TopSuppliersChart from './TopSuppliersChart.vue';
import CustomersSuppliersComparison from './CustomersSuppliersComparison.vue';

export default {
  name: 'CustomersSuppliersSection',
  components: {
    JRSection,
    JRButton,
    TopCustomersChart,
    TopSuppliersChart,
    CustomersSuppliersComparison,
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
      type: Array,
      default: () => [],
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
      this.$emit('refresh-customers-suppliers');
    },
  },
};
</script>

<style scoped>
.jr-dash-state {
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-dash-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-jr-border);
}
</style>
