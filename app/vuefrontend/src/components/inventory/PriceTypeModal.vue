<template>
  <div class="modal fade" tabindex="-1" ref="modal" aria-labelledby="priceTypeModalTitle">
    <div
      class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-xl price-type-modal-dialog w-100 mx-auto"
      role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="priceTypeModalTitle">
            {{ objectId ? `Edit Price Type #${objectId}` : 'Add Price Type' }}
          </h5>
          <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
        </div>

        <div class="modal-body px-3 px-sm-4 py-3">
          <DynamicForm
            ref="dynamicForm"
            :schemaEndpoint="'/api/schema/pricetype/'"
            :apiEndpoint="'/api/pricetypes/'"
            :objectId="objectId"
            :readOnly="false"
            :isModal="true"
            :formTitle="objectId ? 'Edit Price Type' : 'Add Price Type'"
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
    name: 'PriceTypeModal',
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

          // 👇 Forzar recarga del registro al abrir
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
        this.$emit('refresh'); // Emitimos evento para que el padre recargue la lista
      },
    },
  };
</script>

<style scoped>
/* Ancho generoso en tablet/desktop; en móvil Bootstrap usa casi 100% del viewport */
.price-type-modal-dialog {
  max-width: min(960px, calc(100vw - 1.25rem));
}

@media (max-width: 575.98px) {
  .price-type-modal-dialog {
    max-width: 100%;
    margin: 0.5rem;
  }
}
</style>
