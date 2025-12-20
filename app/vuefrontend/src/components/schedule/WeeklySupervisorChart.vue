<template>
  <div>
    <div class="row mb-3">
      <div class="col-md-4">
        <label for="category">Filter by Category:</label>
        <select class="form-select" v-model="selectedCategory" @change="handleCategoryChange">
          <option value="">All Categories</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.name">
            {{ cat.name }}
          </option>
        </select>
      </div>
      <div class="col-md-4 d-flex align-items-end justify-content-center">
        <div class="text-muted mb-4"></div>
        <i>Showing data from the last 16 weeks</i>
      </div>
      <div class="col-md-3 d-flex align-items-end justify-content-end me-2"
        v-if="hasPermission('appschedule.view_event')">

        <!-- Select Excel Export -->
        <div class="excel-export-container">
          <div class="excel-export-wrapper">
            <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" class="excel-icon" />
            <select 
              class="excel-export-select" 
              v-model="selectedExportPeriod"
              @change="handleExportPeriodChange">
              <option value="" disabled>Download Excel Report</option>
              <option value="16">Last 4 Months</option>
              <option value="24">Last 6 Months</option>
              <option value="32">Last 8 Months</option>
              <option value="52">Last 12 Months</option>
            </select>
            <div class="dropdown-arrow">▼</div>
          </div>
        </div>
      </div>
    </div>

    <div class="chart-container">
      <!-- Muestra el canvas solo cuando el DOM está listo -->
      <canvas ref="barChart" v-show="isChartVisible"></canvas>
    </div>
  </div>
</template>

<script>
  import { defineComponent, ref, onMounted, nextTick } from 'vue';
  import { Chart, registerables } from 'chart.js';
  import axios from 'axios';

  Chart.register(...registerables);

  const colorPalette = [
    'rgba(54, 162, 235, 0.7)',
    'rgba(255, 99, 132, 0.7)',
    'rgba(255, 206, 86, 0.7)',
    'rgba(75, 192, 192, 0.7)',
    'rgba(153, 102, 255, 0.7)',
    'rgba(255, 159, 64, 0.7)',
    'rgba(201, 203, 207, 0.7)',
    'rgba(0, 128, 0, 0.7)',
    'rgba(255, 20, 147, 0.7)',
    'rgba(0, 191, 255, 0.7)'
  ];

  const colorMap = {};

  const colorForLabel = label => {
    if (!colorMap[label]) {
      const nextColor = colorPalette[Object.keys(colorMap).length % colorPalette.length];
      colorMap[label] = nextColor;
    }
    return colorMap[label];
  };

  export default defineComponent({
    name: 'WeeklySupervisorChart',
    setup() {
      const barChart = ref(null);
      const chartInstance = ref(null);
      const selectedCategory = ref('');
      const categories = ref([]);
      const isChartVisible = ref(false);
      const selectedWeeks = ref(16);
      const selectedExportPeriod = ref('');

      const fetchCategories = async () => {
        try {
          const res = await axios.get('/api/categories/');
          categories.value = res.data;
        } catch (err) {
          console.error('Error loading categories:', err);
        }
      };

      const fetchChartData = async () => {
        isChartVisible.value = false;

        try {
          const res = await axios.get('/api/supervisor-stats/', {
            params: {
              weeks: selectedWeeks.value,
              category: selectedCategory.value || undefined,
            },
          });

          await nextTick();
          updateChart(res.data);
        } catch (err) {
          console.error('Error loading chart data:', err);
        }
      };

      const updateChart = data => {
        if (!barChart.value || !barChart.value.getContext) {
          console.warn('Canvas not ready');
          return;
        }

        if (chartInstance.value) {
          chartInstance.value.destroy();
          chartInstance.value = null;
        }

        chartInstance.value = new Chart(barChart.value.getContext('2d'), {
          type: 'bar',
          data: {
            labels: data.labels,
            datasets: data.datasets.map(ds => ({
              label: ds.label,
              data: ds.data,
              backgroundColor: colorForLabel(ds.label),
            })),
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'top' },
              tooltip: { mode: 'index', intersect: false },
            },
            scales: {
              x: {
                title: { display: true, text: 'Weeks' },
              },
              y: {
                beginAtZero: true,
                title: { display: true, text: 'Jobs' },
              },
            },
          },
        });

        isChartVisible.value = true;
      };

      const handleCategoryChange = () => {
        fetchChartData();
      };

      const handleExportPeriodChange = () => {
        if (selectedExportPeriod.value) {
          downloadSupervisorExcel(parseInt(selectedExportPeriod.value));
          // Resetear el select después de la descarga
          selectedExportPeriod.value = '';
        }
      };

      const downloadSupervisorExcel = async (weeks) => {
        const params = new URLSearchParams({
          weeks,
          category: selectedCategory.value || '',
        });

        try {
          const response = await axios.get(`/api/supervisor-stats-excel/?${params.toString()}`, { responseType: 'blob' });
          const blob = new Blob([response.data], { type: response.headers['content-type'] });
          const link = document.createElement('a');
          link.href = window.URL.createObjectURL(blob);

          const today = new Date();
          const formattedToday = today.toISOString().split('T')[0];
          link.download = `supervisor-stats_${formattedToday}_last${weeks}weeks.xlsx`;
          link.click();
          Swal.fire("Excel Ready!", "The file has been downloaded successfully.", "success");
        } catch (err) {
          console.error("Excel Download Error:", err);
        }
      };


      onMounted(() => {
        fetchCategories();
        fetchChartData();
      });

      return {
        barChart,
        selectedCategory,
        categories,
        isChartVisible,
        selectedExportPeriod,
        handleCategoryChange,
        handleExportPeriodChange,
        downloadSupervisorExcel
      };
    },
  });
</script>

<style scoped>
  .chart-container {
    position: relative;
    width: 100%;
    height: 380px;
    overflow: hidden;
  }

  canvas {
    width: 100% !important;
    height: 100% !important;
  }

  /* Estilos para el select de exportación - Estilo btn-outline-success */
  .excel-export-container {
    min-width: 250px;
  }

  .excel-export-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    border: 1px solid #28a745;
    border-radius: 0.375rem;
    background-color: transparent;
    transition: all 0.15s ease-in-out;
    overflow: hidden;
  }

  .excel-export-wrapper:hover {
    background-color: #198754;
    border-color: #198754;
  }

  .excel-export-wrapper:hover .excel-export-select {
    color: white;
  }

  .excel-export-wrapper:hover .dropdown-arrow {
    color: white;
  }

  .excel-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    z-index: 2;
    pointer-events: none;
  }

  .excel-export-select {
    background: transparent;
    color: #28a745;
    border: none;
    padding: 0.375rem 2.5rem 0.375rem 2.5rem;
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1.5;
    cursor: pointer;
    width: 100%;
    outline: none;
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    transition: color 0.15s ease-in-out;
  }

  .excel-export-select:focus {
    box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25);
  }

  .excel-export-select option {
    background-color: #f8fff9;
    color: #155724;
    padding: 8px 12px;
    border: none;
  }

  .excel-export-select option:hover {
    background-color: #d4edda;
    color: #155724;
  }

  .excel-export-select option:checked {
    background-color: #d4edda;
    color: #155724;
  }

  .dropdown-arrow {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #28a745;
    font-size: 0.75rem;
    pointer-events: none;
    z-index: 2;
    transition: color 0.15s ease-in-out;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .excel-export-container {
      min-width: 200px;
    }
    
    .excel-export-select {
      font-size: 0.8rem;
      padding: 0.3rem 2rem 0.3rem 2rem;
    }
    
    .excel-icon {
      left: 10px;
      width: 18px;
      height: 18px;
    }
    
    .dropdown-arrow {
      right: 10px;
      font-size: 0.7rem;
    }
  }
</style>
