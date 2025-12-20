<template>
  <DynamicForm
    :schema-endpoint="'/api/schema/job/'"
    :api-endpoint="'/api/job/'"
    :object-id="$route.params.id"
    :form-title="formTitle"
    :read-only="isViewMode"
    :redirect-after-save="'job-list'"
  />
</template>

<script>
import DynamicForm from '@/components/parties/DynamicForm.vue'

export default {
  name: 'JobFormView',
  components: {
    DynamicForm
  },
  computed: {
    isViewMode() {
      return this.$route.name === 'job-view'
    },
    formTitle() {
      if (this.isViewMode) {
        return 'View Job (Community)'
      } else if (this.$route.params.id) {
        return 'Edit Job (Community)'
      } else {
        return 'Create Job (Community)'
      }
    }
  }
}
</script>

