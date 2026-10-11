<template>
  <DynamicForm
    :schema-endpoint="'/api/schema/builder/'"
    :api-endpoint="'/api/builder/'"
    :object-id="$route.params.id"
    :form-title="formTitle"
    :read-only="isViewMode"
    :redirect-after-save="'builder-list'"
    :sections="sections"
    edit-route-name="builder-edit"
  />
</template>

<script>
import DynamicForm from "@/components/parties/DynamicForm.vue";
import { BUILDER_FORM_SECTIONS } from "@/components/parties/builderFormSections";

export default {
  name: "BuilderFormView",
  components: {
    DynamicForm,
  },
  data() {
    return {
      sections: BUILDER_FORM_SECTIONS,
    };
  },
  computed: {
    isViewMode() {
      return this.$route.name === "builder-view";
    },
    formTitle() {
      if (this.isViewMode) {
        return "View Party";
      }
      if (this.$route.params.id) {
        return "Edit Party";
      }
      return "Create Party";
    },
  },
};
</script>
