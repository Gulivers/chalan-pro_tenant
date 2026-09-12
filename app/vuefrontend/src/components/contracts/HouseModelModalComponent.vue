<template>
  <div
    class="modal fade"
    ref="modalElement"
    id="houseModelModal"
    tabindex="-1"
    aria-labelledby="houseModelModalLabel"
    aria-hidden="true">
    <div class="modal-dialog modal-xl modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="houseModelModalLabel">
            {{
              action === 'edit'
                ? `Edit House Model #${resolvedHouseModelId || ''}`
                : 'Add House Model'
            }}
          </h5>
          <button
            type="button"
            class="btn-close"
            @click="closeModal"
            aria-label="Close"></button>
        </div>
        <div class="modal-body text-start">
          <DynamicForm
            :key="formKey"
            ref="houseModelForm"
            schema-endpoint="/api/schema/house-model/"
            api-endpoint="/api/house_model/"
            :object-id="action === 'edit' ? resolvedHouseModelId : null"
            :form-title="
              action === 'edit' ? 'Edit House Model' : 'Create House Model'
            "
            :is-modal="true"
            @saved="handleSaved"
            @cancel="closeModal" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import DynamicForm from '@/components/parties/DynamicForm.vue';

export default {
  name: 'HouseModelModalComponent',
  components: { DynamicForm },
  props: {
    action: { type: String, default: 'add' },
    /** Edit id, or legacy array-of-job-ids used when adding from a job context. */
    houseModelId: { default: null },
    jobs: { type: Array, default: () => [] },
  },
  data() {
    return {
      modalInstance: null,
      formNonce: 0,
    };
  },
  computed: {
    resolvedHouseModelId() {
      const raw = this.houseModelId;
      if (raw == null) return null;
      if (Array.isArray(raw)) return null;
      return raw;
    },
    formKey() {
      const id =
        this.action === 'edit' ? this.resolvedHouseModelId || 'edit' : 'new';
      return `hm-modal-${id}-${this.formNonce}`;
    },
  },
  mounted() {
    if (this.$refs.modalElement) {
      this.modalInstance = Modal.getOrCreateInstance(this.$refs.modalElement);
    }
  },
  methods: {
    showModal() {
      this.formNonce += 1;
      this.modalInstance?.show();
    },
    hideModal() {
      this.modalInstance?.hide();
    },
    closeModal() {
      this.hideModal();
      this.$emit('close');
    },
    handleSaved(saved) {
      this.$emit('saved', saved);
      this.$emit('refresh', saved);
      this.closeModal();
    },
  },
};
</script>

<style scoped>
.modal-xl {
  max-width: 90%;
}

@media (min-width: 1200px) {
  .modal-xl {
    max-width: 1140px;
  }
}
</style>
