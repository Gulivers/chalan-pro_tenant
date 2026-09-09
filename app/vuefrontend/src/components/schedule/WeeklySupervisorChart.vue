<template>
  <div class="jr-chart-block">
    <div class="jr-chart-toolbar">
      <JRField label="Filter by category" input-id="supervisor-category">
        <template #default="{ describedby, invalid }">
          <JRSelect
            v-model="selectedCategory"
            :options="categoryOptions"
            option-label="label"
            option-value="value"
            placeholder="All categories"
            show-clear
            input-id="supervisor-category"
            :aria-describedby="describedby"
            :invalid="invalid"
            @update:modelValue="handleCategoryChange"
          />
        </template>
      </JRField>

      <p class="jr-chart-toolbar__hint">Showing data from the last 16 weeks</p>

      <JRField
        v-if="canExportExcel"
        label="Excel report"
        input-id="supervisor-export"
        class="jr-chart-toolbar__export"
      >
        <template #default="{ describedby, invalid }">
          <JRSelect
            v-model="selectedExportPeriod"
            :options="exportOptions"
            option-label="label"
            option-value="value"
            placeholder="Download Excel report"
            input-id="supervisor-export"
            :aria-describedby="describedby"
            :invalid="invalid"
            @update:modelValue="handleExportPeriodChange"
          />
        </template>
      </JRField>
    </div>

    <div v-if="loading" class="jr-dash-state" aria-live="polite">Loading…</div>

    <JREmptyState
      v-else-if="loadError"
      title="Could not load supervisor stats"
      description="Try again in a moment. If the problem continues, contact an administrator."
    >
      <JRButton variant="secondary" size="sm" type="button" @click="reload">
        Retry
      </JRButton>
    </JREmptyState>

    <JREmptyState
      v-else-if="!hasChartData"
      title="No supervisor stats"
      description="There is no weekly supervisor data for the selected filters."
    />

    <div v-else class="jr-chart-container">
      <canvas
        ref="chartCanvas"
        role="img"
        aria-label="Bar chart of weekly supervisor job stats for the last 16 weeks"
      />
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, getCurrentInstance } from "vue";
import { Chart, registerables } from "chart.js";
import axios from "axios";
import Swal from "sweetalert2";
import { JRField, JRSelect, JRButton, JREmptyState } from "@ui";
import { useDashboardChart } from "@components/inventory/dashboard/components/useDashboardChart.js";

Chart.register(...registerables);

const colorPalette = [
  "rgba(37, 99, 235, 0.75)",
  "rgba(220, 38, 38, 0.75)",
  "rgba(217, 119, 6, 0.75)",
  "rgba(22, 163, 74, 0.75)",
  "rgba(2, 132, 199, 0.75)",
  "rgba(124, 58, 237, 0.75)",
  "rgba(100, 116, 139, 0.75)",
  "rgba(190, 24, 93, 0.75)",
  "rgba(8, 145, 178, 0.75)",
  "rgba(101, 163, 13, 0.75)",
];

export default defineComponent({
  name: "WeeklySupervisorChart",
  components: { JRField, JRSelect, JRButton, JREmptyState },
  setup() {
    const colorMap = {};
    const colorForLabel = (label) => {
      if (!colorMap[label]) {
        const nextColor =
          colorPalette[Object.keys(colorMap).length % colorPalette.length];
        colorMap[label] = nextColor;
      }
      return colorMap[label];
    };

    const instance = getCurrentInstance();
    const chartCanvas = ref(null);
    const selectedCategory = ref(null);
    const categories = ref([]);
    const selectedWeeks = ref(16);
    const selectedExportPeriod = ref(null);
    const loading = ref(true);
    const loadError = ref(false);
    const chartPayload = ref(null);

    const canExportExcel = computed(() =>
      !!instance?.proxy?.hasPermission?.("appschedule.view_event")
    );

    const categoryOptions = computed(() =>
      (categories.value || []).map((cat) => ({
        label: cat.name,
        value: cat.name,
      }))
    );

    const exportOptions = [
      { label: "Last 4 months", value: 16 },
      { label: "Last 6 months", value: 24 },
      { label: "Last 8 months", value: 32 },
      { label: "Last 12 months", value: 52 },
    ];

    const hasChartData = computed(() => {
      const data = chartPayload.value;
      if (!data || !Array.isArray(data.labels) || !Array.isArray(data.datasets)) {
        return false;
      }
      return data.labels.length > 0 && data.datasets.length > 0;
    });

    const { scheduleRender } = useDashboardChart({
      isLoading: () => loading.value,
      hasData: () => hasChartData.value && !loadError.value,
      getCanvas: () => chartCanvas.value,
      buildChart: (canvas) => {
        const data = chartPayload.value;
        return new Chart(canvas, {
          type: "bar",
          data: {
            labels: data.labels,
            datasets: data.datasets.map((ds) => ({
              label: ds.label,
              data: ds.data,
              backgroundColor: colorForLabel(ds.label),
            })),
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            plugins: {
              legend: { position: "top" },
              tooltip: { mode: "index", intersect: false },
            },
            scales: {
              x: {
                title: { display: true, text: "Weeks" },
              },
              y: {
                beginAtZero: true,
                title: { display: true, text: "Jobs" },
              },
            },
          },
        });
      },
    });

    const fetchCategories = async () => {
      try {
        const res = await axios.get("/api/categories/");
        categories.value = Array.isArray(res.data) ? res.data : [];
      } catch (err) {
        console.error("Error loading categories:", err);
      }
    };

    const fetchChartData = async () => {
      loading.value = true;
      loadError.value = false;
      try {
        const res = await axios.get("/api/supervisor-stats/", {
          params: {
            weeks: selectedWeeks.value,
            category: selectedCategory.value || undefined,
          },
        });
        chartPayload.value = res.data || null;
      } catch (err) {
        console.error("Error loading chart data:", err);
        chartPayload.value = null;
        loadError.value = true;
      } finally {
        loading.value = false;
        scheduleRender();
      }
    };

    const handleCategoryChange = () => {
      fetchChartData();
    };

    const handleExportPeriodChange = () => {
      if (selectedExportPeriod.value != null && selectedExportPeriod.value !== "") {
        downloadSupervisorExcel(Number(selectedExportPeriod.value));
        selectedExportPeriod.value = null;
      }
    };

    const downloadSupervisorExcel = async (weeks) => {
      const params = new URLSearchParams({
        weeks,
        category: selectedCategory.value || "",
      });

      try {
        const response = await axios.get(
          `/api/supervisor-stats-excel/?${params.toString()}`,
          { responseType: "blob" }
        );
        const blob = new Blob([response.data], {
          type: response.headers["content-type"],
        });
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);

        const today = new Date();
        const formattedToday = today.toISOString().split("T")[0];
        link.download = `supervisor-stats_${formattedToday}_last${weeks}weeks.xlsx`;
        link.click();
        await Swal.fire(
          "Excel Ready!",
          "The file has been downloaded successfully.",
          "success"
        );
      } catch (err) {
        console.error("Excel Download Error:", err);
      }
    };

    const reload = () => {
      fetchChartData();
    };

    fetchCategories();
    fetchChartData();

    return {
      chartCanvas,
      selectedCategory,
      categoryOptions,
      loading,
      loadError,
      hasChartData,
      selectedExportPeriod,
      exportOptions,
      canExportExcel,
      handleCategoryChange,
      handleExportPeriodChange,
      reload,
    };
  },
});
</script>

<style scoped>
.jr-chart-block {
  min-height: 0;
}

.jr-chart-toolbar {
  display: grid;
  grid-template-columns: minmax(12rem, 18rem) 1fr auto;
  gap: 0.85rem 1rem;
  align-items: end;
  margin-bottom: 0.85rem;
}

.jr-chart-toolbar__hint {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
  padding-bottom: 0.55rem;
}

.jr-chart-toolbar__export {
  min-width: 14rem;
  justify-self: end;
}

.jr-dash-state {
  padding: 0.75rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-chart-container {
  position: relative;
  height: 360px;
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  padding: 0.85rem;
}

.jr-chart-container canvas {
  display: block;
  max-width: 100%;
}

@media (max-width: 767.98px) {
  .jr-chart-toolbar {
    grid-template-columns: 1fr;
  }

  .jr-chart-toolbar__export {
    justify-self: stretch;
    min-width: 0;
  }

  .jr-chart-toolbar__hint {
    padding-bottom: 0;
  }

  .jr-chart-container {
    height: 280px;
  }
}
</style>
