<template>
  <div class="assistant-chart-block">
    <div v-if="block.title" class="assistant-block-title text-muted small mb-2">
      {{ block.title }}
    </div>
    <div v-if="!hasData" class="text-muted small text-start">No chart data.</div>
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
  'rgba(13, 110, 253, 0.8)',
  'rgba(25, 135, 84, 0.8)',
  'rgba(255, 193, 7, 0.85)',
  'rgba(220, 53, 69, 0.8)',
  'rgba(111, 66, 193, 0.8)',
  'rgba(13, 202, 240, 0.8)',
  'rgba(108, 117, 125, 0.8)',
  'rgba(253, 126, 20, 0.8)',
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
              labels: { boxWidth: 12, font: { size: 10 } },
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
