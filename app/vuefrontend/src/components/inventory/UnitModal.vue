<template>
  <div class="modal fade" id="unitModal" tabindex="-1" aria-labelledby="unitModalLabel" aria-hidden="true" ref="modal">
    <div class="modal-dialog modal-lg modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="unitModalLabel">
            {{ objectId ? 'Edit Unit of Measure' : 'Add Unit of Measure' }}
          </h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>

        <div class="modal-body">
          <DynamicForm
            :schemaEndpoint="'/api/schema/unitofmeasure/'"
            :apiEndpoint="'/api/unitsofmeasure/'"
            :objectId="objectId"
            :readOnly="false"
            :isModal="true"
            @saved="handleSaved"
            @cancel="closeModal" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import * as bootstrap from 'bootstrap';
  import DynamicForm from '@components/inventory/DynamicForm.vue';

  export default {
    name: 'UnitModal',
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
        this.$emit('refreshUnits'); // Emitimos evento para que el ProductForm recargue el select de unidades
      },
    },
  };
</script>

<style scoped>
  .modal-title {
    font-weight: bold;
  }
</style>
