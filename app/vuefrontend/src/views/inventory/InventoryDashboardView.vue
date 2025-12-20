<template>
  <div class="inventory-dashboard-view">
    <InventoryDashboard />
  </div>
</template>

<script>
import InventoryDashboard from '@/components/inventory/dashboard/InventoryDashboard.vue'

export default {
  name: 'InventoryDashboardView',
  components: {
    InventoryDashboard
  },
  metaInfo: {
    title: 'Inventory Dashboard - ChalanPro'
  }
}
</script>

<style scoped>
.inventory-dashboard-view {
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>
