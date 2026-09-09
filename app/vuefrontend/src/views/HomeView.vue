<template>
  <JRPage>
    <JRPageHeader title="Dashboard" />

    <p class="jr-dash-intro">
      Morning console — contract pace, crew load, and sales vs purchases at a glance.
    </p>

    <JRSection title="Weekly Contract Totals">
      <AreaChart />
    </JRSection>

    <JRSection title="Monthly Contract Totals">
      <BarChart />
    </JRSection>

    <JRSection
      v-if="hasPermission('apptransactions.add_workaccount')"
      title="Weekly Supervisor Stats"
    >
      <WeeklySupervisorChart />
    </JRSection>

    <!-- Title lives inside CustomersSuppliersComparison (shared with Inventory). -->
    <JRSection v-if="hasPermission('apptransactions.add_document')">
      <CustomersSuppliersComparison
        :comparison-data="comparisonData"
        :loading="loadingComparison"
        @refresh="loadComparison"
      />
    </JRSection>
  </JRPage>
</template>

<script>
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
      const token = localStorage.getItem("authToken");
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
                Authorization: `Token ${token}`,
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
.jr-dash-intro {
  margin: -0.35rem 0 1.1rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}
</style>
