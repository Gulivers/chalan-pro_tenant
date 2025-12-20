<template>
  <div>
    <canvas ref="barChart"></canvas>
  </div>
</template>

<script>
import { defineComponent, onMounted, ref } from 'vue';
import axios from 'axios';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default defineComponent({
  name: 'BarChart',
  setup() {
    const barChart = ref(null);
    const chartInstance = ref(null);

    const fetchChartData = async () => {
      try {
        const response = await axios.get('/api/monthly_summary/');
        // console.log(response.data);  // Verifica los datos en la consola para asegurarse de que se están obteniendo
        const chartData = processChartData(response.data);
        updateChart(chartData);
      } catch (error) {
        console.error('Error fetching chart data:', error);
      }
    };

    const processChartData = (data) => {
      const labels = [...new Set(data.map(item => item.month))]; // Meses únicos
      const trimData = [];
      const roughData = [];

      // Llenar los datos de trim y rough por mes
      labels.forEach(month => {
        const trimItem = data.find(item => item.job_type === 'Trim' && item.month === month); // Usar 'Trim' con mayúsculas
        const roughItem = data.find(item => item.job_type === 'Rough' && item.month === month); // Usar 'Rough' con mayúsculas
        trimData.push(trimItem ? trimItem.total_contracts : 0);
        roughData.push(roughItem ? roughItem.total_contracts : 0);
      });

      return {
        labels,
        datasets: [
          {
            label: 'Trim',
            data: trimData,
            backgroundColor: '#4e73df',
            borderColor: '#4e73df',
            borderWidth: 1
          },
          {
            label: 'Rough',
            data: roughData,
            backgroundColor: '#1cc88a',
            borderColor: '#1cc88a',
            borderWidth: 1
          }
        ]
      };
    };

    const updateChart = (chartData) => {
      if (chartInstance.value) {
        chartInstance.value.destroy();
      }
      chartInstance.value = new Chart(barChart.value, {
        type: 'bar',
        data: chartData,
        options: {
          maintainAspectRatio: false,
          scales: {
            x: { beginAtZero: true },
            y: { beginAtZero: true },
          },
        },
      });
    };

    onMounted(() => {
      fetchChartData(); // Obtener datos al montar el componente
    });

    return { barChart };
  }
});
</script>

<style scoped>
canvas {
  max-width: 100%;
  height: 400px;
}
</style>
