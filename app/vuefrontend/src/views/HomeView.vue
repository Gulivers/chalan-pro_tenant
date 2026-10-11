<template>
  <JRPage>
    <JRPageHeader title="Dashboard" />

    <JRSection title="Weekly Contract Totals" class="jr-home-section">
      <AreaChart />
    </JRSection>

    <JRSection title="Monthly Contract Totals" class="jr-home-section">
      <BarChart />
    </JRSection>

    <JRSection
      v-if="hasPermission('apptransactions.add_workaccount')"
      title="Weekly Supervisor Stats"
      class="jr-home-section"
    >
      <WeeklySupervisorChart />
    </JRSection>

    <!-- Title lives inside CustomersSuppliersComparison (shared with Inventory). -->
    <JRSection
      v-if="hasPermission('apptransactions.add_document')"
      class="jr-home-section"
    >
      <CustomersSuppliersComparison
        :comparison-data="comparisonData"
        :loading="loadingComparison"
        @refresh="loadComparison"
      />
    </JRSection>
  </JRPage>
</template>

<script>
import { getAccessToken } from '@/auth/tokenHelpers';
import { defineComponent } from "vue";
import axios from "axios";
import { JRPage, JRPageHeader, JRSection } from "@ui";
import AreaChart from "@components/contracts/AreaChart.vue";
import BarChart from "@components/contracts/BarChart.vue";
import WeeklySupervisorChart from "@components/schedule/WeeklySupervisorChart.vue";
import CustomersSuppliersComparison from "@components/inventory/dashboard/components/CustomersSuppliersComparison.vue";

export default defineComponent({
  name: "HomeView",
  components: {
    JRPage,
    JRPageHeader,
    JRSection,
    AreaChart,
    BarChart,
    WeeklySupervisorChart,
    CustomersSuppliersComparison,
  },

  data() {
    return {
      comparisonData: [],
      loadingComparison: false,
    };
  },

  mounted() {
    // Log once after login when the user lands on Home
    this.checkUserIdentity().then((userId) => {
      if (userId) {
        this.logUserAction(
          "login",
          "User",
          userId,
          "User logged in successfully"
        );
      }
    });
    this.loadComparison();
  },

  methods: {
    async checkUserIdentity() {
      const user = await this.getAuthenticatedUser();
      return user ? user.id : null;
    },

    logUserAction(action, model_name, object_id, details) {
      const token = getAccessToken();
      if (token) {
        axios
          .post(
            "/api/log-action/",
            {
              action,
              model_name,
              object_id,
              details,
            },
            {
              headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
              },
            }
          )
          .then((response) => {
            console.log("Acción registrada:", response.data);
          })
          .catch((error) => {
            console.error("Error registrando la acción:", error);
          });
      } else {
        console.error("Token no encontrado. El usuario no está autenticado.");
      }
    },

    async loadComparison() {
      try {
        this.loadingComparison = true;
        const response = await axios.get(
          "/api/dashboard/customers-suppliers-comparison/"
        );
        this.comparisonData = Array.isArray(response.data) ? response.data : [];
      } catch (error) {
        console.error("Error loading comparison data:", error);
        this.comparisonData = [];
      } finally {
        this.loadingComparison = false;
      }
    },
  },
});
</script>

<style scoped>
.jr-home-section {
  margin-bottom: 2rem;
}

.jr-home-section:last-child {
  margin-bottom: 0;
}
</style>
