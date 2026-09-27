<template>
  <JRPage>
    <JRPageHeader title="Resumen Semanal de Trabajos" />
    <JRDataTable :value="weeklyData" dataKey="_key">
      <Column field="start_of_week" header="Desde" />
      <Column field="end_of_week" header="Hasta" />
      <Column field="job__name" header="Comunidad (Job)" />
      <Column field="total_contracts" header="Total" />
      <template #empty>
        <JREmptyState
          title="No weekly summary"
          description="No contract totals were returned for this period." />
      </template>
    </JRDataTable>
  </JRPage>
</template>

<script>
import { defineComponent, onMounted, ref } from 'vue';
import axios from 'axios';
import Column from 'primevue/column';
import { JRPage, JRPageHeader, JRDataTable, JREmptyState } from '@/ui';

export default defineComponent({
  name: 'WeeklySummaryList',
  components: { JRPage, JRPageHeader, JRDataTable, JREmptyState, Column },
  setup() {
    const weeklyData = ref([]);

    const fetchWeeklyData = async () => {
      try {
        const response = await axios.get('/api/weekly_summary_list/');
        const rows = Array.isArray(response.data) ? response.data : [];
        weeklyData.value = rows.map((item, index) => ({
          ...item,
          _key: `${item.start_of_week || ''}-${item.job__name || ''}-${index}`,
        }));
      } catch (error) {
        console.error('Error fetching weekly summary data:', error);
      }
    };

    onMounted(() => {
      fetchWeeklyData();
    });

    return { weeklyData };
  },
});
</script>
