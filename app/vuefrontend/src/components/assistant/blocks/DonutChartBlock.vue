<template>
  <div class="assistant-chart-block">
    <div v-if="block.title" class="assistant-block-title mb-2 text-sm text-jr-muted">
      {{ block.title }}
    </div>
    <div v-if="!hasData" class="text-start text-sm text-jr-muted">No chart data.</div>
    <div v-else class="assistant-chart-canvas-wrap">
      <canvas ref="chartCanvas" aria-label="Donut chart" role="img" />
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
import { parseChartNumber } from '../formatValue';

Chart.register(...registerables);

const PALETTE = [
  '#2563eb',
  '#16a34a',
  '#d97706',
  '#dc2626',
  '#0284c7',
  '#4b5563',
  '#1d4ed8',
  '#111827',
];

export default {
  name: 'DonutChartBlock',
  props: {
    block: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      chartInstance: null,
    };
  },
  computed: {
    labels() {
      return Array.isArray(this.block?.labels) ? this.block.labels.map(String) : [];
    },
    values() {
      return Array.isArray(this.block?.values)
        ? this.block.values.map(parseChartNumber)
        : [];
    },
    hasData() {
      return this.labels.length > 0 && this.labels.length === this.values.length;
    },
  },
  watch: {
    block: {
      deep: true,
      handler() {
        this.$nextTick(() => this.renderChart());
      },
    },
  },
  mounted() {
    this.renderChart();
  },
  beforeUnmount() {
    this.destroyChart();
  },
  methods: {
    destroyChart() {
      if (this.chartInstance) {
        this.chartInstance.destroy();
        this.chartInstance = null;
      }
    },
    renderChart() {
      this.destroyChart();
      if (!this.hasData || !this.$refs.chartCanvas) return;

      const colors = this.labels.map((_, i) => PALETTE[i % PALETTE.length]);

      this.chartInstance = new Chart(this.$refs.chartCanvas, {
        type: 'doughnut',
        data: {
          labels: this.labels,
          datasets: [
            {
              data: this.values,
              backgroundColor: colors,
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { boxWidth: 12 },
            },
          },
        },
      });
    },
  },
};
</script>

<style scoped>
.assistant-chart-block {
  text-align: left;
}
.assistant-block-title {
  font-weight: 600;
}
.assistant-chart-canvas-wrap {
  position: relative;
  height: 240px;
  width: 100%;
}
</style>
