<template>
  <DynamicForm
    :schema-endpoint="'/api/schema/house-model/'"
    :api-endpoint="'/api/house_model/'"
    :object-id="$route.params.id"
    :form-title="formTitle"
    :read-only="isViewMode"
    :redirect-after-save="'house-model-list'"
  />
</template>

<script>
import DynamicForm from '@/components/parties/DynamicForm.vue'

export default {
  name: 'HouseModelFormView',
  components: {
    DynamicForm
  },
  computed: {
    isViewMode() {
      return this.$route.name === 'house-model-view'
    },
    formTitle() {
      if (this.isViewMode) {
        return 'View House Model'
      } else if (this.$route.params.id) {
        return 'Edit House Model'
      } else {
        return 'Create House Model'
      }
    }
  }
}
</script>

