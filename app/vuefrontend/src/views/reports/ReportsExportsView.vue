<template>
  <JRPage>
    <JRPageHeader title="Measure the Operation">
      <template #actions>
        <JRButton type="button" variant="primary" @click="reportsOpen = true">
          Reports & exports
        </JRButton>
      </template>
    </JRPageHeader>

    <p class="jr-reports-intro">
      Sales and customer analysis for operational review, plus Excel exports.
    </p>

    <section class="jr-reports-sales" aria-label="Sales and customers">
      <h2 class="jr-reports-sales__title">Sales &amp; customers</h2>
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
    </section>

    <DashboardReportsDrawer
      v-model:visible="reportsOpen"
      variant="operations"
      :loading="loading"
      :period-days="salesPeriodDays"
    />
  </JRPage>
</template>

<script>
import axios from "axios";
import { JRPage, JRPageHeader, JRButton } from "@ui";
import SalesAnalysisSection from "@/components/inventory/dashboard/components/SalesAnalysisSection.vue";
import CustomersSuppliersSection from "@/components/inventory/dashboard/components/CustomersSuppliersSection.vue";
import DashboardReportsDrawer from "@/components/inventory/dashboard/components/DashboardReportsDrawer.vue";

export default {
  name: "ReportsExportsView",
  components: {
    JRPage,
    JRPageHeader,
    JRButton,
    SalesAnalysisSection,
    CustomersSuppliersSection,
    DashboardReportsDrawer,
  },
  metaInfo: {
    title: "Measure the Operation – JobRhythm",
  },
  data() {
    return {
      loading: true,
      salesData: {},
      salesPeriodDays: 30,
      customersData: {},
      suppliersData: {},
      comparisonData: [],
      reportsOpen: false,
    };
  },
  async mounted() {
    await this.loadPageData();
  },
  methods: {
    async loadPageData() {
      try {
        this.loading = true;
        await Promise.all([
          this.loadSalesData(),
          this.loadCustomersSuppliersData(),
        ]);
      } catch (error) {
        console.error("Error loading reports data:", error);
        this.notifyToastError?.("Error loading reports data");
      } finally {
        this.loading = false;
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
        const resolvedDays =
          Number.isFinite(days) && days > 0 ? days : this.salesPeriodDays || 30;
        const response = await axios.get("/api/dashboard/sales-analysis/", {
          params: { period_days: resolvedDays },
        });
        this.salesData = response.data || {};
      } catch (error) {
        console.error("Error loading sales data:", error);
        this.salesData = {};
      }
    },
    async loadCustomersSuppliersData() {
      try {
        const [customersResponse, suppliersResponse, comparisonResponse] =
          await Promise.all([
            axios.get("/api/dashboard/top-customers/"),
            axios.get("/api/dashboard/top-suppliers/"),
            axios.get("/api/dashboard/customers-suppliers-comparison/"),
          ]);
        this.customersData = customersResponse.data || {};
        this.suppliersData = suppliersResponse.data || {};
        this.comparisonData = Array.isArray(comparisonResponse.data)
          ? comparisonResponse.data
          : [];
      } catch (error) {
        console.error("Error loading customers/suppliers data:", error);
        this.customersData = {};
        this.suppliersData = {};
        this.comparisonData = [];
      }
    },
  },
};
</script>

<style scoped>
.jr-reports-intro {
  margin: -0.35rem 0 1.1rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-reports-sales__title {
  margin: 0 0 0.85rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text);
}
</style>
