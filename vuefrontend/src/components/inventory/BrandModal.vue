<template>
  <div
    class="modal fade"
    id="brandModal"
    tabindex="-1"
    aria-labelledby="brandModalLabel"
    aria-hidden="true"
    ref="modal">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="brandModalLabel">
            {{ objectId ? `Edit Brand #${objectId}` : 'Add Brand' }}
          </h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>

        <div class="modal-body">
          <DynamicForm
            ref="dynamicForm"
            :schemaEndpoint="'/api/schema/productbrand/'"
            :apiEndpoint="'/api/productbrand/'"
            :objectId="objectId"
            :readOnly="false"
            :isModal="true"
            :formTitle="objectId ? 'Edit Brand' : 'Add Brand'"
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
  name: 'BrandModal',
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

        // Forzar recarga del registro si está en modo edición
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
      this.$emit('refreshBrands'); // El padre (ProductForm) recarga el v-select de marcas
    },
  },
};
</script>

<style scoped>
.modal-title {
  font-weight: bold;
}
</style>
