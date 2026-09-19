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

    <DashboardReportsDrawer
      v-if="canOpenReports"
      v-model:visible="reportsOpen"
      variant="inventory"
      :loading="loading"
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
import DashboardReportsDrawer from './components/DashboardReportsDrawer.vue';

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
    DashboardReportsDrawer,
  },
  data() {
    return {
      loading: true,
      metrics: {},
      lowStockProducts: [],
      lowestStockProducts: [],
      reportsOpen: false,
    };
  },
  computed: {
    canViewStock() {
      return !!this.hasPermission?.('appinventory.view_product');
    },
    canOpenReports() {
      return (
        !!this.hasPermission?.('appinventory.add_product') ||
        !!this.hasPermission?.('appinventory.change_product')
      );
    },
  },
  async mounted() {
    await this.loadDashboardData();
  },
  methods: {
    async loadDashboardData() {
      try {
        this.loading = true;
        await Promise.all([this.loadMetrics(), this.loadStockData()]);
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
        this.lowStockProducts = Array.isArray(lowStockResponse.data)
          ? lowStockResponse.data
          : [];
        this.lowestStockProducts = Array.isArray(lowestStockResponse.data)
          ? lowestStockResponse.data
          : [];
      } catch (error) {
        console.error('Error loading stock data:', error);
        this.lowStockProducts = [];
        this.lowestStockProducts = [];
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
</style>
