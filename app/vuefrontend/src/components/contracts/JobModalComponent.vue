<template>
  <div
    class="modal fade"
    ref="modalElement"
    :id="id"
    tabindex="-1"
    role="dialog"
    aria-labelledby="jobModalLabel"
    aria-hidden="true">
    <div class="modal-dialog modal-xl modal-dialog-centered" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="jobModalLabel">
            {{
              action === 'edit'
                ? `Edit Community #${job?.id || ''}`
                : 'Add Community'
            }}
          </h5>
          <button
            type="button"
            class="btn-close"
            @click="closeModal"
            aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <DynamicForm
            :key="formKey"
            ref="jobForm"
            schema-endpoint="/api/schema/job/"
            api-endpoint="/api/job/"
            :object-id="action === 'edit' ? job?.id : null"
            :form-title="
              action === 'edit' ? 'Edit Community' : 'Create Community'
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
  name: 'JobModalComponent',
  components: { DynamicForm },
  props: {
    id: { type: String, default: 'jobModal' },
    action: { type: String, default: 'add' },
    job: { type: Object, default: null },
    /** Kept for call-site compat; DynamicForm loads builders from schema. */
    builders: { type: Array, default: () => [] },
  },
  data() {
    return {
      modalInstance: null,
      formNonce: 0,
    };
  },
  computed: {
    formKey() {
      const id = this.action === 'edit' ? this.job?.id || 'edit' : 'new';
      return `job-modal-${id}-${this.formNonce}`;
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
    handleSaved(savedJob) {
      this.$emit('saved', savedJob);
      this.$emit('refresh', savedJob);
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
