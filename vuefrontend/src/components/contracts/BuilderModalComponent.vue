<template>
  <div class="modal fade" ref="modalElement" :id="id" tabindex="-1" role="dialog" aria-labelledby="builderModalLabel"
    aria-hidden="true">
    <div class="modal-dialog modal-xl modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            {{ action === 'edit' ? `Edit Party #${builder?.id || ''}` : 'Add Party' }}
          </h5>
          <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <DynamicForm 
            ref="builderForm" 
            :schema-endpoint="'/api/schema/builder/'"
            :api-endpoint="'/api/builder/'"
            :object-id="action === 'edit' ? builder?.id : null"
            :form-title="action === 'edit' ? 'Edit Party' : 'Create Party'"
            :is-modal="true"
            @saved="handleSaved" 
            @cancel="closeModal" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from "bootstrap";
import DynamicForm from '@/components/parties/DynamicForm.vue';

export default {
  components: {
    DynamicForm
  },
  props: ["id", "action", "builder"],
  data() {
    return {
      modalInstance: null, // Store the Bootstrap modal instance
    };
  },
  mounted() {
    if (this.$refs.modalElement) {
      this.modalInstance = Modal.getOrCreateInstance(this.$refs.modalElement);
    }
  },
  methods: {
    showModal() {
      if (this.modalInstance) {
        this.modalInstance.show();
      }
    },
    hideModal() {
      if (this.modalInstance) {
        this.modalInstance.hide();
      }
    },
    closeModal() {
      this.hideModal();
      this.$emit("close");
    },
    handleSaved(savedBuilder) {
      this.$emit("saved", savedBuilder);
      this.closeModal();
    }
  },
};
</script>

<style scoped>
/* Modal específico para Builder con DynamicForm */
.modal-xl {
  max-width: 90%;
}

@media (min-width: 1200px) {
  .modal-xl {
    max-width: 1140px;
  }
}
</style>