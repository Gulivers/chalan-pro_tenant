<template>
    <div class="container">
      <h2>Resumen Semanal de Trabajos</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Desde</th>
            <th>Hasta</th>
            <th>Comunidad (Job)</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in weeklyData" :key="index">
            <td>{{ item.start_of_week }}</td>
            <td>{{ item.end_of_week }}</td>
            <td>{{ item.job__name }}</td>
            <td>{{ item.total_contracts }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  import { defineComponent, onMounted, ref } from 'vue';
  import axios from 'axios';
  
  export default defineComponent({
    name: 'WeeklySummaryList',
    setup() {
      const weeklyData = ref([]);
  
      const fetchWeeklyData = async () => {
        try {
          const response = await axios.get('/api/weekly_summary_list/');
          weeklyData.value = response.data;
        } catch (error) {
          console.error('Error fetching weekly summary data:', error);
        }
      };
  
      onMounted(() => {
        fetchWeeklyData();
      });
  
      return { weeklyData };
    }
  });
  </script>
  
  <style scoped>
  .table {
    width: 100%;
    margin-top: 20px;
  }
  </style>
