<template>
  <DynamicForm
    :schema-endpoint="'/api/schema/builder/'"
    :api-endpoint="'/api/builder/'"
    :object-id="$route.params.id"
    :form-title="formTitle"
    :read-only="isViewMode"
    :redirect-after-save="'builder-list'"
  />
</template>

<script>
import DynamicForm from '@/components/parties/DynamicForm.vue'

export default {
  name: 'BuilderFormView',
  components: {
    DynamicForm
  },
  computed: {
    isViewMode() {
      return this.$route.name === 'builder-view'
    },
    formTitle() {
      if (this.isViewMode) {
        return 'View Party'
      } else if (this.$route.params.id) {
        return 'Edit Party'
      } else {
        return 'Create Party'
      }
    }
  }
}
</script>

