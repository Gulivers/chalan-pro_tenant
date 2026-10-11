<template>
  <InventoryDashboard />
</template>

<script>
import InventoryDashboard from '@/components/inventory/dashboard/InventoryDashboard.vue'

export default {
  name: 'InventoryDashboardView',
  components: {
    InventoryDashboard
  },
  metaInfo: {
    title: 'Inventory Dashboard – JobRhythm'
  }
}
</script>
