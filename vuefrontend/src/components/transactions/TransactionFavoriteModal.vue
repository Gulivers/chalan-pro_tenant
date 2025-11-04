<template>
   <div
     class="modal fade"
     id="transactionFavoriteModal"
     tabindex="-1"
     aria-labelledby="transactionFavoriteModalLabel"
     aria-hidden="true"
     @click="handleBackdropClick">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="transactionFavoriteModalLabel">
            <i class="fas fa-star text-warning me-2"></i>
            {{ isEditMode ? 'Edit Favorite' : 'Save as Favorite' }}
          </h5>
           <button type="button" class="btn-close" @click="handleCloseClick" aria-label="Close"></button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Información básica -->
            <div class="row g-3">
              <div class="col-12">
                <label class="form-label">
                  <i class="fas fa-tag me-1"></i>
                  Name
                  <span class="text-danger">*</span>
                </label>
                <input
                  type="text"
                  class="form-control"
                  v-model="form.name"
                  :class="{ 'is-invalid': errors.name }"
                  placeholder="Enter a descriptive name for this favorite"
                  required />
                <div class="invalid-feedback" v-if="errors.name">
                  {{ errors.name[0] }}
                </div>
              </div>

              <div class="col-12">
                <label class="form-label">
                  <i class="fas fa-align-left me-1"></i>
                  Description
                </label>
                <textarea
                  class="form-control"
                  v-model="form.description"
                  :class="{ 'is-invalid': errors.description }"
                  rows="3"
                  placeholder="Optional description of this favorite transaction"></textarea>
                <div class="invalid-feedback" v-if="errors.description">
                  {{ errors.description[0] }}
                </div>
              </div>
            </div>

            <!-- Vista previa de la transacción -->
            <div class="mt-4">
              <h6 class="text-primary">
                <i class="fas fa-eye me-1"></i>
                Transaction Preview
              </h6>
              <div class="card bg-light">
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-6">
                      <small class="text-muted">Document Type:</small>
                      <div class="fw-semibold">{{ documentTypeName }}</div>
                    </div>
                    <div class="col-md-6">
                      <small class="text-muted">Lines:</small>
                      <div class="fw-semibold">{{ linesCount }} items</div>
                    </div>
                    <div class="col-md-6" v-if="builderName">
                      <small class="text-muted">Builder:</small>
                      <div class="fw-semibold">{{ builderName }}</div>
                    </div>
                    <div class="col-md-6" v-if="workAccountName">
                      <small class="text-muted">Work Account:</small>
                      <div class="fw-semibold">{{ workAccountName }}</div>
                    </div>
                  </div>

                  <!-- Resumen de líneas -->
                  <div class="mt-3" v-if="linesPreview.length > 0">
                    <small class="text-muted">Products:</small>
                    <div class="mt-1">
                      <span v-for="(line, idx) in linesPreview" :key="idx" class="badge bg-secondary me-1 mb-1">
                        {{ line.product_name }} ({{ line.quantity }})
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Acciones adicionales para modo edición -->
            <div class="mt-4" v-if="isEditMode">
              <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Edit Mode:</strong>
                You can update the name and description, or click "Update Data" to refresh this favorite with the
                current transaction data.
              </div>
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <div class="d-flex justify-content-between w-100">
            <!-- Botones de la izquierda (solo en modo edición) -->
             <div v-if="isEditMode">
               <button 
                 type="button" 
                 class="btn btn-outline-danger" 
                 @click="handleDelete" 
                 :disabled="submitting || !hasPermission('apptransactions.delete_transactionfavorite')">
                 <i class="fas fa-trash me-1"></i>
                 Delete
               </button>
             </div>

            <!-- Botones de la derecha -->
            <div class="d-flex gap-2">
               <button type="button" class="btn btn-secondary" @click="handleCloseClick" :disabled="submitting">
                 Cancel
               </button>

               <button
                 v-if="isEditMode"
                 type="button"
                 class="btn btn-outline-primary"
                 @click="handleUpdateData"
                 :disabled="submitting || !hasPermission('apptransactions.change_transactionfavorite')">
                 <i class="fas fa-sync me-1"></i>
                 Update Data
               </button>

               <button
                 type="button"
                 class="btn btn-primary"
                 @click="handleSubmit"
                 :disabled="submitting || !form.name.trim() || !hasPermission('apptransactions.add_transactionfavorite')">
                 <i v-if="!submitting" class="fas fa-save me-1"></i>
                 <i v-else class="fas fa-spinner fa-spin me-1"></i>
                 {{ submitting ? 'Saving...' : isEditMode ? 'Save Changes' : 'Save Favorite' }}
               </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
   import { ref, reactive, computed, watch } from 'vue';
   import axios from 'axios';
   import Swal from 'sweetalert2';

   // Función para verificar permisos (asumiendo que existe globalmente)
   function hasPermission(permission) {
     // Esta función debería estar disponible globalmente en la aplicación
     // Si no existe, retornar true por defecto
     return typeof window.hasPermission === 'function' ? window.hasPermission(permission) : true;
   }

   // Función helper para cerrar el modal
   function closeModal() {
     const modalElement = document.getElementById('transactionFavoriteModal');
     if (modalElement) {
       if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
         const modal = bootstrap.Modal.getInstance(modalElement);
         if (modal) modal.hide();
       } else if (typeof $ !== 'undefined' && $.fn.modal) {
         $(modalElement).modal('hide');
       } else {
         // Fallback: cerrar modal usando clases CSS
         modalElement.classList.remove('show');
         modalElement.style.display = 'none';
         modalElement.removeAttribute('aria-modal');
         modalElement.removeAttribute('role');
         
         // Remover backdrop
         const backdrop = document.getElementById('modal-backdrop');
         if (backdrop) {
           backdrop.remove();
         }
         
         // Remover clase del body
         document.body.classList.remove('modal-open');
       }
     }
   }

   // Función helper para manejar clics en el backdrop
   function handleBackdropClick(event) {
     if (event.target === event.currentTarget) {
       closeModal();
     }
   }

   // Función helper para manejar clics en el botón de cerrar
   function handleCloseClick() {
     closeModal();
   }

   const props = defineProps({
    transactionData: {
      type: Object,
      required: true,
    },
    documentTypesOptions: {
      type: Array,
      default: () => [],
    },
    buildersOptions: {
      type: Array,
      default: () => [],
    },
    workAccountsOptions: {
      type: Array,
      default: () => [],
    },
    isEditMode: {
      type: Boolean,
      default: false,
    },
    favoriteToEdit: {
      type: Object,
      default: null,
    },
  });

  const emit = defineEmits(['saved', 'updated', 'deleted']);

  const submitting = ref(false);
  const errors = reactive({});

  const form = reactive({
    name: '',
    description: '',
  });

  // Computed para mostrar información de la transacción
  const documentTypeName = computed(() => {
    if (!props.transactionData.document_type) return 'Not selected';
    const docType = props.documentTypesOptions.find(dt => dt.value === props.transactionData.document_type);
    return docType ? docType.label : 'Unknown';
  });

  const builderName = computed(() => {
    if (!props.transactionData.builder) return null;
    const builder = props.buildersOptions.find(b => b.value === props.transactionData.builder);
    return builder ? builder.label : 'Unknown';
  });

  const workAccountName = computed(() => {
    if (!props.transactionData.work_account) return null;
    const workAccount = props.workAccountsOptions.find(wa => wa.value === props.transactionData.work_account);
    return workAccount ? workAccount.label : 'Unknown';
  });

  const linesCount = computed(() => {
    return props.transactionData.lines ? props.transactionData.lines.length : 0;
  });

  const linesPreview = computed(() => {
    if (!props.transactionData.lines) return [];
    return props.transactionData.lines
      .filter(line => line.product)
      .slice(0, 5) // Mostrar máximo 5 productos
      .map(line => ({
        product_name: line.product_label || 'Unknown Product',
        quantity: line.quantity || 0,
      }));
  });

  // Watcher para cargar datos del favorito en modo edición
  watch(
    () => props.favoriteToEdit,
    newFavorite => {
      if (newFavorite && props.isEditMode) {
        form.name = newFavorite.name || '';
        form.description = newFavorite.description || '';
      }
    },
    { immediate: true }
  );

  // Watcher para resetear formulario cuando se abre en modo crear
  watch(
    () => props.isEditMode,
    newValue => {
      if (!newValue) {
        form.name = '';
        form.description = '';
        clearErrors();
      }
    }
  );

  function clearErrors() {
    Object.keys(errors).forEach(key => delete errors[key]);
  }

  function validateForm() {
    clearErrors();

    if (!form.name.trim()) {
      errors.name = ['El nombre es requerido.'];
      return false;
    }

    return true;
  }

  async function handleSubmit() {
    if (!validateForm()) return;

    submitting.value = true;

    try {
      const payload = {
        name: form.name.trim(),
        description: form.description.trim(),
        document_data: props.transactionData,
        lines_data: props.transactionData.lines || [],
      };

      let response;
      if (props.isEditMode && props.favoriteToEdit) {
        // Actualizar favorito existente
        response = await axios.put(`/api/transaction-favorites/${props.favoriteToEdit.id}/`, payload);
        emit('updated', response.data);

        await Swal.fire({
          icon: 'success',
          title: 'Updated!',
          text: 'Favorite updated successfully.',
          timer: 1500,
          showConfirmButton: false,
        });
      } else {
        // Crear nuevo favorito
        response = await axios.post('/api/transaction-favorites/create-from-transaction/', payload);
        emit('saved', response.data.favorite);

        await Swal.fire({
          icon: 'success',
          title: 'Saved!',
          text: 'Transaction saved as favorite successfully.',
          timer: 1500,
          showConfirmButton: false,
        });
      }

       // Cerrar modal
       closeModal();
    } catch (error) {
      console.error('Error saving favorite:', error);

      if (error.response?.data?.details) {
        // Aplicar errores de validación del servidor
        Object.assign(errors, error.response.data.details);
      } else {
        await Swal.fire({
          icon: 'error',
          title: 'Error',
          text: error.response?.data?.error || 'Error saving favorite. Please try again.',
          confirmButtonText: 'OK',
        });
      }
    } finally {
      submitting.value = false;
    }
  }

  async function handleUpdateData() {
    if (!props.favoriteToEdit) return;

    const result = await Swal.fire({
      title: 'Update Favorite Data?',
      text: 'This will replace the current favorite data with the current transaction data.',
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Yes, Update',
      cancelButtonText: 'Cancel',
      confirmButtonColor: '#0d6efd',
      cancelButtonColor: '#6c757d',
    });

    if (!result.isConfirmed) return;

    submitting.value = true;

    try {
      const payload = {
        document_data: props.transactionData,
        lines_data: props.transactionData.lines || [],
      };

      const response = await axios.post(
        `/api/transaction-favorites/${props.favoriteToEdit.id}/update-from-transaction/`,
        payload
      );
      emit('updated', response.data.favorite);

      await Swal.fire({
        icon: 'success',
        title: 'Updated!',
        text: 'Favorite data updated successfully.',
        timer: 1500,
        showConfirmButton: false,
      });

       // Cerrar modal
       closeModal();
    } catch (error) {
      console.error('Error updating favorite data:', error);

      await Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.error || 'Error updating favorite data. Please try again.',
        confirmButtonText: 'OK',
      });
    } finally {
      submitting.value = false;
    }
  }

  async function handleDelete() {
    if (!props.favoriteToEdit) return;

    const result = await Swal.fire({
      title: 'Delete Favorite?',
      text: 'This action cannot be undone. The favorite will be permanently deleted.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Yes, Delete',
      cancelButtonText: 'Cancel',
      confirmButtonColor: '#dc3545',
      cancelButtonColor: '#6c757d',
    });

    if (!result.isConfirmed) return;

    submitting.value = true;

    try {
      await axios.delete(`/api/transaction-favorites/${props.favoriteToEdit.id}/`);
      emit('deleted', props.favoriteToEdit.id);

      await Swal.fire({
        icon: 'success',
        title: 'Deleted!',
        text: 'Favorite deleted successfully.',
        timer: 1500,
        showConfirmButton: false,
      });

       // Cerrar modal
       closeModal();
    } catch (error) {
      console.error('Error deleting favorite:', error);

      await Swal.fire({
        icon: 'error',
        title: 'Error',
        text: error.response?.data?.error || 'Error deleting favorite. Please try again.',
        confirmButtonText: 'OK',
      });
    } finally {
      submitting.value = false;
    }
  }
</script>

<style scoped>
  .modal-lg {
    max-width: 800px;
  }

  .badge {
    font-size: 0.75rem;
  }

  .alert {
    margin-bottom: 0;
  }

  .form-control.is-invalid {
    border-color: #dc3545;
  }

  .invalid-feedback {
    display: block;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .card.bg-light {
    border: 1px solid #dee2e6;
  }

  .fw-semibold {
    font-weight: 600;
  }
</style>
