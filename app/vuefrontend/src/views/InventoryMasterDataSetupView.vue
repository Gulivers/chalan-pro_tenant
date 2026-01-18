<template>
  <div class="container-fluid">
    <InventoryMasterDataSetup />
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import InventoryMasterDataSetup from '@components/inventory/InventoryMasterDataSetup.vue';

export default defineComponent({
  name: 'InventoryMasterDataSetupView',
  components: {
    InventoryMasterDataSetup,
  },
  methods: {},
});
</script>

<style scoped>
</style>
