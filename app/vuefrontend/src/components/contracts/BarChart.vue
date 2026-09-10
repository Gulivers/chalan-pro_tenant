<template>
  <div class="jr-chart-block">
    <div v-if="loading" class="jr-dash-state" aria-live="polite">Loading…</div>

    <JREmptyState
      v-else-if="loadError"
      title="Could not load monthly contracts"
      description="Try again in a moment. If the problem continues, contact an administrator."
    >
      <JRButton variant="secondary" size="sm" type="button" @click="reload">
        Retry
      </JRButton>
    </JREmptyState>

    <JREmptyState
      v-else-if="!hasData"
      title="No monthly contract data"
      description="There are no monthly contract totals to chart right now."
    />

    <div v-else>
      <div class="jr-chart-controls">
        <p class="jr-chart-controls__hint">Trim vs Rough · by month</p>
        <JRButton variant="secondary" size="sm" type="button" @click="reload">
          Refresh
        </JRButton>
      </div>

      <div class="jr-chart-container">
        <canvas
          ref="chartCanvas"
          role="img"
          aria-label="Bar chart of monthly contract totals for Trim and Rough"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed } from "vue";
import axios from "axios";
import { Chart, registerables } from "chart.js";
import { JRButton, JREmptyState } from "@ui";
import { useDashboardChart } from "@components/inventory/dashboard/components/useDashboardChart.js";

Chart.register(...registerables);

const TRIM_COLOR = "#2563eb";
const ROUGH_COLOR = "#16a34a";

export default defineComponent({
  name: "BarChart",
  components: { JRButton, JREmptyState },
  setup() {
    const chartCanvas = ref(null);
    const loading = ref(true);
    const loadError = ref(false);
    const rawData = ref([]);

    const hasData = computed(
      () => Array.isArray(rawData.value) && rawData.value.length > 0
    );

    const processChartData = (data) => {
      const labels = [...new Set(data.map((item) => item.month))];
      const trimData = [];
      const roughData = [];

      labels.forEach((month) => {
        const trimItem = data.find(
          (item) => item.job_type === "Trim" && item.month === month
        );
        const roughItem = data.find(
          (item) => item.job_type === "Rough" && item.month === month
        );
        trimData.push(trimItem ? trimItem.total_contracts : 0);
        roughData.push(roughItem ? roughItem.total_contracts : 0);
      });

      return {
        labels,
        datasets: [
          {
            label: "Trim",
            data: trimData,
            backgroundColor: TRIM_COLOR,
            borderColor: TRIM_COLOR,
            borderWidth: 1,
          },
          {
            label: "Rough",
            data: roughData,
            backgroundColor: ROUGH_COLOR,
            borderColor: ROUGH_COLOR,
            borderWidth: 1,
          },
        ],
      };
    };

    const { scheduleRender } = useDashboardChart({
      isLoading: () => loading.value,
      hasData: () => hasData.value && !loadError.value,
      getCanvas: () => chartCanvas.value,
      buildChart: (canvas) => {
        const chartData = processChartData(rawData.value);
        return new Chart(canvas, {
          type: "bar",
          data: chartData,
          options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            plugins: {
              legend: { position: "top" },
            },
            scales: {
              x: { beginAtZero: true },
              y: { beginAtZero: true },
            },
          },
        });
      },
    });

    const fetchChartData = async () => {
      loading.value = true;
      loadError.value = false;
      try {
        const response = await axios.get("/api/monthly_summary/");
        rawData.value = Array.isArray(response.data) ? response.data : [];
      } catch (error) {
        console.error("Error fetching chart data:", error);
        rawData.value = [];
        loadError.value = true;
      } finally {
        loading.value = false;
        scheduleRender();
      }
    };

    const reload = () => {
      fetchChartData();
    };

    fetchChartData();

    return {
      chartCanvas,
      loading,
      loadError,
      hasData,
      reload,
    };
  },
});
</script>

<style scoped>
.jr-chart-block {
  min-height: 0;
}

.jr-dash-state {
  padding: 0.75rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-chart-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.jr-chart-controls__hint {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-chart-container {
  position: relative;
  height: 360px;
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  border-radius: 0;
  padding: 0.85rem;
}

.jr-chart-container canvas {
  display: block;
  max-width: 100%;
}

@media (max-width: 767.98px) {
  .jr-chart-container {
    height: 280px;
  }
}
</style>
