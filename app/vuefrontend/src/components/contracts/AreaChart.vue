<template>
  <canvas ref="areaChart"></canvas>
</template>

<script>
import { defineComponent, onMounted, ref } from 'vue';
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default defineComponent({
  name: 'AreaChart',
  setup() {
    const areaChart = ref(null);
    const chartInstance = ref(null);

    const fetchChartData = async () => {
      try {
        const response = await axios.get('/api/weekly_summary/');
        const chartData = processChartData(response.data);
        updateChart(chartData);
      } catch (error) {
        console.error('Error fetching chart data:', error);
      }
    };

    const processChartData = (data) => {
      const labels = [...new Set(data.map(item => item.week))]; // Etiquetas de semanas
      const types = ['Trim', 'Rough'];

      const datasets = types.map(type => {
        const typeData = data.filter(item => item.type === type);
        const totals = labels.map(week => {
          const item = typeData.find(d => d.week === week);
          return item ? item.total_contracts : 0;  // Usar 'total_contracts' para contar contratos
        });

        return {
          label: type,
          data: totals,
          backgroundColor: type === 'Trim' ? 'rgba(78, 115, 223, 0.5)' : 'rgba(28, 200, 138, 0.5)',
          borderColor: type === 'Trim' ? 'rgba(78, 115, 223, 1)' : 'rgba(28, 200, 138, 1)',
          fill: true,
        };
      });

      return { labels, datasets };
    };

    const updateChart = (chartData) => {
      if (chartInstance.value) {
        chartInstance.value.destroy();
      }
      chartInstance.value = new Chart(areaChart.value, {
        type: 'line',
        data: chartData,
        options: {
          maintainAspectRatio: false,
          scales: {
            x: { beginAtZero: true },
            y: { beginAtZero: true }
          }
        }
      });
    };

    onMounted(() => {
      fetchChartData();
    });

    return { areaChart };
  }
});
</script>

<style scoped>
canvas {
  max-width: 100%;
  height: 400px;
}
</style>
