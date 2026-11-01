<template>
  <JRPage>
    <MaterialRequestDetail
      :request-id="$route.params.id"
      :editable="$route.query.mode === 'edit'" />
  </JRPage>
</template>

<script>
import { JRPage } from '@/ui';
import MaterialRequestDetail from '@/components/material/MaterialRequestDetail.vue';

export default {
  name: 'MaterialRequestDetailView',
  components: { JRPage, MaterialRequestDetail },
};
</script>
