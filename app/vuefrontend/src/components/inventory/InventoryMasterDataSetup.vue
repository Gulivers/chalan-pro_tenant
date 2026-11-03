<template>
  <JRPage>
    <JRPageHeader
      title="Inventory Master Data Setup"
      description="Import products, brands, categories, units, price types, warehouses, product prices, absence reasons, and optionally Import Favorites into your tenant." />

    <InventoryMasterDataSetupContent @cancel="goBack" @imported="onImported" />
  </JRPage>
</template>

<script>
import { defineComponent } from 'vue';
import { JRPage, JRPageHeader } from '@/ui';
import InventoryMasterDataSetupContent from './InventoryMasterDataSetupContent.vue';

export default defineComponent({
  name: 'InventoryMasterDataSetup',
  components: {
    JRPage,
    JRPageHeader,
    InventoryMasterDataSetupContent,
  },
  methods: {
    goBack() {
      if (this.$router && this.$route.name) {
        this.$router.back();
      } else {
        this.$router.push('/');
      }
    },
    onImported() {
      /* stay on page; content shows success state */
    },
  },
});
</script>
