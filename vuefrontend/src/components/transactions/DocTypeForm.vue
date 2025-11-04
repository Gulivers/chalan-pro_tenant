<template>
  <div class="container mt-4">
    <!-- Main Title -->
    <div class="text-center">
      <h3 class="text-warning">Transaction Types</h3>
    </div>

    <div class="card shadow-sm">
      <div class="card-header d-flex justify-content-center align-items-center">
        <h6 class="mb-0 w-100 text-center text-primary">
          {{ isViewMode ? 'View Document Type' : isEditMode ? 'Edit Document Type' : 'New Document Type' }}
        </h6>
      </div>

      <div class="card-body p-4">
        <form @submit.prevent="handleSubmit">
          <!-- Basic Information -->
          <div class="row mb-4">
            <div class="col-12">
              <h6 class="text-warning border-bottom pb-2 mb-3">
                <i class="fas fa-info-circle me-2"></i>
                Basic Information
              </h6>
            </div>
            <div class="col-md-6 mb-3">
              <div class="row">
                <div class="col-md-4">
                  <label for="type_code" class="form-label">
                    Type Code
                    <span class="text-danger">*</span>
                  </label>
                </div>
                <div class="col-md-8 text-uppercase">
                  <input
                    id="type_code"
                    v-model="form.type_code"
                    type="text"
                    class="form-control"
                    placeholder="Ex: INCOME, SUPRET"
                    :disabled="isViewMode || submitting"
                    v-tt="'Unique code to identify the document type'" />
                </div>
              </div>
            </div>
            <div class="col-md-6 mb-3">
              <div class="row">
                <div class="col-md-4">
                  <label for="description" class="form-label fw-bold">
                    Description
                    <span class="text-danger">*</span>
                  </label>
                </div>
                <div class="col-md-8">
                  <input
                    id="description"
                    v-model="form.description"
                    type="text"
                    class="form-control"
                    placeholder="Document type description"
                    :disabled="isViewMode || submitting"
                    v-tt="'Descriptive name for the document type'" />
                </div>
              </div>
            </div>
          </div>

          <!-- Inventory Configuration -->
          <div class="row mb-2">
            <div class="col-12">
              <h6 class="text-warning border-bottom pb-2 mb-3">
                <i class="fas fa-boxes me-2"></i>
                Inventory Configuration
              </h6>
            </div>
            <div class="col-md-6 mb-0">
              <div class="d-flex justify-content-between align-items-center">
                <label for="stock_movement" class="form-label mb-0">Stock Movement</label>
                <select
                  id="stock_movement"
                  v-model="form.stock_movement"
                  class="form-select"
                  style="width: 278px"
                  :disabled="isViewMode || submitting"
                  v-tt="'Defines how it affects inventory'">
                  <option :value="1">+1 Entry</option>
                  <option :value="-1">-1 Exit</option>
                  <option :value="0">0 Neutral</option>
                </select>
              </div>
            </div>
            <div class="col-md-3 mb-2 py-2">
              <label class="form-label border-bottom mb-3 fw-bold">Affects Inventory</label>
              <div class="d-flex flex-column gap-1">
                <div class="d-flex justify-content-between align-items-center">
                  <label class="form-check-label mx-4 me-0" for="affects_physical">Physical Inventory</label>
                  <div class="form-check form-switch">
                    <input
                      id="affects_physical"
                      v-model="form.affects_physical"
                      class="form-check-input me-5"
                      type="checkbox"
                      :disabled="isViewMode || submitting"
                      v-tt="'Affects physical inventory count'" />
                  </div>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                  <label class="form-check-label mx-4 me-0" for="affects_logical">Logical Inventory</label>
                  <div class="form-check form-switch">
                    <input
                      id="affects_logical"
                      v-model="form.affects_logical"
                      class="form-check-input me-5"
                      type="checkbox"
                      :disabled="isViewMode || submitting"
                      v-tt="'Affects logical inventory tracking'" />
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-3 mb-3 py-2">
              <label class="form-label border-bottom mb-3 fw-bold">Additional Configuration</label>
              <div class="d-flex flex-column gap-1">
                <div class="d-flex justify-content-between align-items-center">
                  <label class="form-check-label mx-4 me-0" for="affects_accounting">Affects Accounting</label>
                  <div class="form-check form-switch">
                    <input
                      id="affects_accounting"
                      v-model="form.affects_accounting"
                      class="form-check-input me-5"
                      type="checkbox"
                      :disabled="isViewMode || submitting"
                      v-tt="'Affects accounting records and financial reports'" />
                  </div>
                </div>
                <div class="d-flex justify-content-between align-items-center">
                  <label class="form-check-label mx-4 me-0" for="warehouse_required">Warehouse Required</label>
                  <div class="form-check form-switch">
                    <input
                      id="warehouse_required"
                      v-model="form.warehouse_required"
                      class="form-check-input me-5"
                      type="checkbox"
                      :disabled="isViewMode || submitting"
                      v-tt="'Requires warehouse selection for this document type'" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Business Configuration -->
          <div class="row mb-4">
            <div class="col-12">
              <h6 class="text-warning border-bottom pb-2 mb-3">
                <i class="fas fa-briefcase me-2"></i>
                Business Configuration
              </h6>
            </div>
            <div class="col-md-4 mb-1">
              <div class="form-check form-switch d-flex align-items-start mt-1">
                <label class="form-check-label mb-1 me-4" for="is_purchase">Purchase Document</label>
                <div class="form-check form-switch">
                  <input
                    id="is_purchase"
                    v-model="form.is_purchase"
                    class="form-check-input"
                    type="checkbox"
                    :disabled="isViewMode || submitting"
                    v-tt="'For transactions with suppliers'" />
                </div>
              </div>
            </div>
            <div class="col-md-4 mb-1">
              <div class="form-check form-switch d-flex align-items-start mt-1">
                <label class="form-check-label mb-1 me-5" for="is_sales">Sales Document</label>
                <div class="form-check form-switch">
                  <input
                    id="is_sales"
                    v-model="form.is_sales"
                    class="form-check-input"
                    type="checkbox"
                    :disabled="isViewMode || submitting"
                    v-tt="'For transactions with customers'" />
                </div>
              </div>
            </div>
            <div class="col-md-4 mb-1">
              <div class="form-check form-switch d-flex align-items-start mt-1">
                <label class="form-check-label mb-1 me-5" for="is_taxable">Subject to Taxes</label>
                <div class="form-check form-switch">
                  <input
                    id="is_taxable"
                    v-model="form.is_taxable"
                    class="form-check-input"
                    type="checkbox"
                    :disabled="isViewMode || submitting"
                    v-tt="'Applies taxes to the document'" />
                </div>
              </div>
            </div>
          </div>

          <!-- Operational Configuration -->
          <div class="row mb-4">
            <div class="col-12">
              <h6 class="text-warning border-bottom pb-2 mb-3">
                <i class="fas fa-cogs me-2"></i>
                Operational Configuration
              </h6>
            </div>
            <div class="col-md-4 mb-1">
              <div class="form-check form-switch d-flex align-items-start mt-1">
                <label class="form-check-label mb-1 me-4" for="is_operational">Operational Document</label>
                <div class="form-check form-switch">
                  <input
                    id="is_operational"
                    v-model="form.is_operational"
                    class="form-check-input"
                    type="checkbox"
                    :disabled="isViewMode || submitting"
                    v-tt="'Requires Work Account selection instead of Builder/Party'" />
                </div>
              </div>
            </div>
            <div class="col-md-4 mb-1">
              <div class="form-check form-switch d-flex align-items-start mt-1">
                <label class="form-check-label mb-1 me-4" for="allow_negative_sales">Allow Negative Sales</label>
                <div class="form-check form-switch">
                  <input
                    id="allow_negative_sales"
                    v-model="form.allow_negative_sales"
                    class="form-check-input"
                    type="checkbox"
                    :disabled="isViewMode || submitting"
                    v-tt="'Allow sales transactions even when stock is insufficient'" />
                </div>
              </div>
            </div>
          </div>

          <!-- Status -->
          <div class="row mb-4">
            <div class="col-12">
              <h6 class="text-warning border-bottom pb-2 mb-3">
                <i class="fas fa-toggle-on me-2"></i>
                Status
              </h6>
            </div>
            <div class="col-md-4">
              <div class="d-flex justify-content-between align-items-center">
                <label class="form-check-label mb-0 me-0" for="is_active">Active Document Type</label>
                <div class="form-check form-switch">
                  <input
                    id="is_active"
                    v-model="form.is_active"
                    class="form-check-input"
                    type="checkbox"
                    :disabled="isViewMode || submitting"
                    v-tt="'Allows using this type in transactions'" />
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="row">
            <div class="col-12">
              <div class="d-flex gap-2 justify-content-center">
                <button type="submit" class="btn btn-primary" :disabled="isViewMode || submitting">
                  <span
                    v-if="submitting"
                    class="spinner-border spinner-border-sm me-1"
                    role="status"
                    aria-hidden="true"></span>
                  <i v-else class="fas fa-save me-1"></i>
                  {{ submitting ? 'Saving...' : 'Save' }}
                </button>
                <button type="button" class="btn btn-secondary" :disabled="submitting" @click="handleCancel">
                  <i class="fas fa-arrow-left me-1"></i>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, onMounted, computed } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import axios from 'axios';
  import Swal from 'sweetalert2';
  import * as bootstrap from 'bootstrap';
  // import { Tooltip } from 'bootstrap'
  import '@assets/css/base.css';

  const route = useRoute();
  const router = useRouter();
  
  const emit = defineEmits(['saved', 'cancel']);

const props = defineProps({
  id: {
    type: [String, Number],
    default: null
  },
  isModal: {
    type: Boolean,
    default: false
  }
});

const submitting = ref(false);
const id = computed(() => props.id || route.query.id);
const isViewMode = computed(() => route.query.mode === 'view');
const isEditMode = computed(() => !!id.value && !isViewMode.value);

  const form = ref({
    type_code: '',
    description: '',
    affects_physical: true,
    affects_logical: true,
    affects_accounting: false,
    is_taxable: false,
    is_purchase: false,
    is_sales: false,
    warehouse_required: true,
    is_operational: false,
    allow_negative_sales: false,
    stock_movement: 0,
    is_active: true,
  });

  onMounted(async () => {
    // initialize bootstrap tooltips
    //const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    //tooltipTriggerList.map(el => new Tooltip(el))

    if (id.value) {
      try {
        const { data } = await axios.get(`/api/document-types/${id.value}/`);
        form.value = data;
      } catch (error) {
        console.error('Error loading data:', error);
        Swal.fire('Oops!', 'Error loading the document type.', 'error');
      }
    }
  });

  const handleSubmit = async () => {
    if (isViewMode.value) return;

    try {
      submitting.value = true;

      // 1) Trim + validación mínima
      const trimmedData = {
        type_code: (form.value.type_code ?? '').trim(),
        description: (form.value.description ?? '').trim(),
        affects_physical: form.value.affects_physical,
        affects_logical: form.value.affects_logical,
        affects_accounting: form.value.affects_accounting,
        is_taxable: form.value.is_taxable,
        is_purchase: form.value.is_purchase,
        is_sales: form.value.is_sales,
        warehouse_required: form.value.warehouse_required,
        is_operational: form.value.is_operational,
        allow_negative_sales: form.value.allow_negative_sales,
        stock_movement: form.value.stock_movement,
        is_active: form.value.is_active,
      };

      // Validaciones requeridas
      if (!trimmedData.type_code) {
        await Swal.fire('Validation', 'Type Code is required.', 'warning');
        return;
      }
      if (!trimmedData.description) {
        await Swal.fire('Validation', 'Description is required.', 'warning');
        return;
      }

      // Validaciones de longitud
      if (trimmedData.type_code.length > 10) {
        await Swal.fire('Validation', 'Type Code cannot exceed 10 characters.', 'warning');
        return;
      }
      if (trimmedData.description.length > 200) {
        await Swal.fire('Validation', 'Description cannot exceed 200 characters.', 'warning');
        return;
      }

      // 2) Guardar
      let savedData;
      if (isEditMode.value) {
        const response = await axios.put(`/api/document-types/${id.value}/`, trimmedData);
        savedData = response.data;
      } else {
        const response = await axios.post('/api/document-types/', trimmedData);
        savedData = response.data;
      }

      // Emit saved event for modal usage
      emit('saved', savedData);

      // Solo redirigir si NO estamos en modal
      if (!props.isModal) {
        goList();
      }
    } catch (error) {
      console.error('Error saving document type:', error);
      const { status, data } = error?.response || {};

      if (status === 400 && data) {
        const messages = Object.entries(data)
          .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
          .join('\n');
        await Swal.fire('Oops!', messages || 'There were validation errors.', 'error');
      } else if (status === 403) {
        await Swal.fire('Forbidden', 'You do not have permission for this action.', 'error');
      } else if (status === 409) {
        await Swal.fire('Protected', 'This document type is in use and cannot be modified.', 'error');
      } else {
        await Swal.fire('Oops!', 'Error saving the document type.', 'error');
      }
    } finally {
      submitting.value = false;
    }
  };

  const goList = () => {
    // Redirección por NOMBRE 'document-types' (con fallback al path)
    router.push({ name: 'document-types' }).catch(() => {
      router.push('/document-types');
    });
  };

  const handleCancel = () => {
    if (props.isModal) {
      // En modal, emitir evento para cerrar
      emit('cancel');
    } else {
      // En página normal, redirigir a lista
      goList();
    }
  };
</script>

<style scoped></style>
