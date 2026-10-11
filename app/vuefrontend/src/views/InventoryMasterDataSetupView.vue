<template>
  <InventoryMasterDataSetup />
</template>

<script>
import { defineComponent } from "vue";
import InventoryMasterDataSetup from "@components/inventory/InventoryMasterDataSetup.vue";

export default defineComponent({
  name: "InventoryMasterDataSetupView",
  components: {
    InventoryMasterDataSetup,
  },
});
</script>
