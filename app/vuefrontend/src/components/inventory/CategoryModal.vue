<template>
  <div
    class="modal fade"
    id="categoryModal"
    tabindex="-1"
    aria-labelledby="categoryModalLabel"
    aria-hidden="true"
    ref="modal">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="categoryModalLabel">
            {{ objectId ? `Edit Category #${objectId}` : 'Add Category' }}
          </h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>

        <div class="modal-body">
          <DynamicForm
            ref="dynamicForm"
            :schemaEndpoint="'/api/schema/product-category/'"
            :apiEndpoint="'/api/productcategory/'"
            :objectId="objectId"
            :readOnly="false"
            :isModal="true"
            :formTitle="objectId ? 'Edit Category' : 'Add Category'"
            @saved="handleSaved"
            @cancel="closeModal"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as bootstrap from 'bootstrap';
import DynamicForm from '@components/inventory/DynamicForm.vue';

export default {
  name: 'CategoryModal',
  components: { DynamicForm },
  props: {
    objectId: {
      type: [String, Number],
      default: null,
    },
  },
  methods: {
    openModal() {
      const modalEl = this.$refs.modal;
      if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();

        // ⚡ Forzar carga del registro seleccionado
        this.$nextTick(() => {
          this.$refs.dynamicForm?.loadRecord?.();
        });
      }
    },
    closeModal() {
      const modalEl = this.$refs.modal;
      if (modalEl) {
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal?.hide();
      }
    },
    handleSaved() {
      this.closeModal();
      this.$emit('refreshCategories');
    },
  },
};
</script>

<style scoped>
.modal-title {
  font-weight: bold;
}
</style>
