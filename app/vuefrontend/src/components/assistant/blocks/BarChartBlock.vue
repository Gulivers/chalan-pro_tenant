<template>
  <div class="assistant-chart-block">
    <div v-if="block.title" class="assistant-block-title text-muted small mb-2">
      {{ block.title }}
    </div>
    <div v-if="!hasData" class="text-muted small text-start">No chart data.</div>
    <div v-else class="assistant-chart-canvas-wrap">
      <canvas ref="chartCanvas" aria-label="Bar chart" role="img" />
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
import { parseChartNumber } from '../formatValue';

Chart.register(...registerables);

export default {
  name: 'BarChartBlock',
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
    seriesName() {
      return this.block?.series_name || 'Value';
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

      this.chartInstance = new Chart(this.$refs.chartCanvas, {
        type: 'bar',
        data: {
          labels: this.labels,
          datasets: [
            {
              label: this.seriesName,
              data: this.values,
              backgroundColor: 'rgba(13, 110, 253, 0.65)',
              borderColor: 'rgba(13, 110, 253, 1)',
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: !!this.block?.series_name },
          },
          scales: {
            x: {
              ticks: {
                maxRotation: 45,
                minRotation: 0,
                autoSkip: true,
                font: { size: 10 },
              },
            },
            y: { beginAtZero: true },
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
  height: 220px;
  width: 100%;
}
</style>
