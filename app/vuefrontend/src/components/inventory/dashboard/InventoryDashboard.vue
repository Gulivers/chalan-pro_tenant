<template>
  <JRPage>
    <JRPageHeader title="Inventory">
      <template #actions>
        <JRButton
          v-if="canOpenReports"
          type="button"
          variant="primary"
          @click="reportsOpen = true">
          Reports & exports
        </JRButton>
      </template>
    </JRPageHeader>

    <p class="jr-dash-intro">
      Operational triage first — what needs attention today — then metrics and analysis.
    </p>

    <template v-if="canViewStock">
      <AttentionSummary :products="lowStockProducts" :loading="loading" />

      <StockAnalysisSection
        :low-stock-products="lowStockProducts"
        :lowest-stock-products="lowestStockProducts"
        :loading="loading"
        @refresh-stock="loadStockData"
      />

      <JRSection title="Inventory snapshot">
        <InventoryMetricsCards :metrics="metrics" :loading="loading" />
      </JRSection>
    </template>
    <Message
      v-else
      class="jr-dash-banner"
      severity="warn"
      :closable="false"
    >
      You don’t have permission to view stock analysis. Contact an administrator if you need access.
    </Message>

    <details
      v-if="canViewDocuments"
      class="jr-dash-secondary"
      :open="analysisOpenByDefault">
      <summary>Sales &amp; customers</summary>
      <SalesAnalysisSection
        :sales-data="salesData"
        :loading="loading"
        @period-changed="onSalesPeriodChanged"
        @refresh-sales="loadSalesData"
      />

      <CustomersSuppliersSection
        :customers-data="customersData"
        :suppliers-data="suppliersData"
        :comparison-data="comparisonData"
        :loading="loading"
        @refresh-customers-suppliers="loadCustomersSuppliersData"
      />
    </details>

    <DashboardReportsDrawer
      v-if="canOpenReports"
      v-model:visible="reportsOpen"
      :loading="loading"
      :period-days="salesPeriodDays"
    />
  </JRPage>
</template>

<script>
import axios from 'axios';
import Message from 'primevue/message';
import { JRPage, JRPageHeader, JRSection, JRButton } from '@ui';
import AttentionSummary from './components/AttentionSummary.vue';
import InventoryMetricsCards from './components/InventoryMetricsCards.vue';
import StockAnalysisSection from './components/StockAnalysisSection.vue';
import SalesAnalysisSection from './components/SalesAnalysisSection.vue';
import CustomersSuppliersSection from './components/CustomersSuppliersSection.vue';
import DashboardReportsDrawer from './components/DashboardReportsDrawer.vue';

const PHONE_MQ = '(max-width: 767.98px)';

export default {
  name: 'InventoryDashboard',
  components: {
    Message,
    JRPage,
    JRPageHeader,
    JRSection,
    JRButton,
    AttentionSummary,
    InventoryMetricsCards,
    StockAnalysisSection,
    SalesAnalysisSection,
    CustomersSuppliersSection,
    DashboardReportsDrawer,
  },
  data() {
    return {
      loading: true,
      metrics: {},
      lowStockProducts: [],
      lowestStockProducts: [],
      salesData: {},
      salesPeriodDays: 30,
      customersData: {},
      suppliersData: {},
      comparisonData: [],
      reportsOpen: false,
      isPhone: false,
      phoneQuery: null,
    };
  },
  computed: {
    canViewStock() {
      return !!this.hasPermission?.('appinventory.view_product');
    },
    canViewDocuments() {
      return !!this.hasPermission?.('apptransactions.view_document');
    },
    canOpenReports() {
      return this.canViewStock || this.canViewDocuments;
    },
    analysisOpenByDefault() {
      if (this.isPhone) return false;
      const total = Number(this.salesData?.metrics?.total_sales);
      return Number.isFinite(total) && total > 0;
    },
  },
  async mounted() {
    if (typeof window !== 'undefined' && window.matchMedia) {
      this.phoneQuery = window.matchMedia(PHONE_MQ);
      this.onViewport = () => {
        this.isPhone = this.phoneQuery.matches;
      };
      this.onViewport();
      if (this.phoneQuery.addEventListener) {
        this.phoneQuery.addEventListener('change', this.onViewport);
      } else {
        this.phoneQuery.addListener(this.onViewport);
      }
    }
    await this.loadDashboardData();
  },
  beforeUnmount() {
    if (!this.phoneQuery || !this.onViewport) return;
    if (this.phoneQuery.removeEventListener) {
      this.phoneQuery.removeEventListener('change', this.onViewport);
    } else {
      this.phoneQuery.removeListener?.(this.onViewport);
    }
  },
  methods: {
    async loadDashboardData() {
      try {
        this.loading = true;

        await Promise.all([
          this.loadMetrics(),
          this.loadStockData(),
          this.loadSalesData(),
          this.loadCustomersSuppliersData(),
        ]);
      } catch (error) {
        console.error('Error loading dashboard data:', error);
        this.notifyToastError?.('Error loading dashboard data');
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

    onSalesPeriodChanged(periodDays) {
      const days = Number(periodDays);
      this.salesPeriodDays = Number.isFinite(days) && days > 0 ? days : 30;
      this.loadSalesData(this.salesPeriodDays);
    },

    async loadSalesData(periodDays = this.salesPeriodDays) {
      try {
        const days = Number(periodDays);
        const resolvedDays = Number.isFinite(days) && days > 0 ? days : this.salesPeriodDays || 30;
        const response = await axios.get('/api/dashboard/sales-analysis/', {
          params: { period_days: resolvedDays },
        });
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
        this.comparisonData = [];
      }
    },
  },
};
</script>

<style scoped>
.jr-dash-intro {
  margin: -0.35rem 0 1.1rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-dash-banner {
  margin-bottom: 1.25rem;
}

.jr-dash-secondary {
  margin-top: 0.25rem;
  margin-bottom: 1.25rem;
  border-top: 1px solid var(--color-jr-border);
  padding-top: 0.85rem;
}

.jr-dash-secondary > summary {
  cursor: pointer;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text);
  list-style: none;
  margin-bottom: 0.85rem;
}

.jr-dash-secondary > summary::-webkit-details-marker {
  display: none;
}

.jr-dash-secondary > summary::before {
  content: '▸ ';
  color: var(--color-jr-muted);
}

.jr-dash-secondary[open] > summary::before {
  content: '▾ ';
}
</style>
