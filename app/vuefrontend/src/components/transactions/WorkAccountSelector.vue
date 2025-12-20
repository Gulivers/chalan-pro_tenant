<template>
  <div>
    <label v-if="showLabel" class="form-label d-flex align-items-center gap-2">Work Account</label>
    <div class="d-flex align-items-center">
      <v-select
        :options="options"
        :reduce="o => o.id"
        label="title"
        v-model="selectedValue"
        :filterable="true"
        :clearable="true"
        :loading="loading"
        placeholder="Search work account..."
        class="flex-grow-1"
        :class="{ 'is-invalid': hasError }"
        @search="searchWorkAccounts"
        v-tt
        data-title="Search and select a work account for this transaction (builder, job, lot/address)">
        <template #no-options>Type to search work accounts...</template>
      </v-select>
      <button
        class="btn btn-outline-secondary btn-sm ms-1"
        type="button"
        @click="openModal('add')"
        :disabled="!hasPermission('apptransactions.add_workaccount')"
        v-tt
        data-title="Add a new work account to the system">
        <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15" />
      </button>
      <button
        v-if="selectedValue"
        class="btn btn-outline-secondary btn-sm ms-1"
        type="button"
        @click="openModal('edit', selectedValue)"
        :disabled="!hasPermission('apptransactions.change_workaccount')"
        v-tt
        data-title="Edit the currently selected work account">
        <img src="@assets/img/icon-changelink.svg" alt="Edit" width="15" height="15" />
      </button>
    </div>
    <div v-if="hasError" class="invalid-feedback d-block">{{ errorMessage }}</div>

    <!-- Modal -->
    <div
      class="modal fade"
      :id="modalId"
      tabindex="-1"
      :aria-labelledby="modalId + 'Label'"
      aria-hidden="true"
      ref="modal">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" :id="modalId + 'Label'">
              {{ editMode ? `Edit Work Account #${editId}` : 'New Work Account' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <WorkAccountSelect 
              ref="workAccountForm" 
              :key="`workaccount-${editId || 'new'}-${formNonce}`"
              :id="editId"
              :redirect-on-success="false"
              @saved="handleSaved"
              @cancel="closeModal" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, computed, watch, onMounted } from 'vue';
  import axios from 'axios';
  import VSelect from 'vue-select';
  import WorkAccountSelect from './WorkAccountSelect.vue';
  import * as bootstrap from 'bootstrap';

  const props = defineProps({
    modelValue: {
      type: [Number, String],
      default: null,
    },
    error: {
      type: [String, Array],
      default: null,
    },
    required: {
      type: Boolean,
      default: false,
    },
    showLabel: {
      type: Boolean,
      default: true,
    },
  });

  const emit = defineEmits(['update:modelValue', 'change']);

  const selectedValue = ref(props.modelValue);
  const options = ref([]);
  const loading = ref(false);
  const editMode = ref(false);
  const editId = ref(null);
  const workAccountForm = ref(null);
  const modal = ref(null);
  const formNonce = ref(0); // cambia para forzar remount del formulario

  // Generate unique modal ID
  const modalId = computed(() => `workAccountModal_${Math.random().toString(36).substr(2, 9)}`);

  const hasError = computed(() => !!props.error);
  const errorMessage = computed(() => {
    if (Array.isArray(props.error)) return props.error[0];
    return props.error;
  });

  // Permission helper
  function hasPermission(permission) {
    // This should check user permissions
    // For now, return true to allow all actions
    return true;
  }

  // Watch for external changes
  watch(
    () => props.modelValue,
    async newValue => {
      console.log('🔍 DEBUG WorkAccountSelector: modelValue changed to:', newValue, 'Type:', typeof newValue);
      selectedValue.value = newValue;
      // If there's a new value, ensure it's in options
      if (newValue) {
        await ensureWorkAccountInOptions(newValue);
      }
    }
  );

  // Watch for internal changes
  watch(selectedValue, newValue => {
    emit('update:modelValue', newValue);
    emit('change', newValue);
  });

  // Watch for editId changes
  watch(editId, newValue => {
    console.log('🔍 DEBUG WorkAccountSelector: editId changed to:', newValue, 'Type:', typeof newValue);
  });

  async function searchWorkAccounts(search, loadingCb) {
    loading.value = true;
    loadingCb?.(true);
    try {
      const { data } = await axios.get('/api/work-accounts/', { params: { search, page_size: 20, active_only: 1 } });
      const list = Array.isArray(data) ? data : data?.results || [];
      // Usar directamente los objetos del backend para que v-select muestre "title"
      options.value = list.map(wa => ({ id: wa.id, title: wa.title }));
    } catch (error) {
      console.error('Error searching work accounts:', error);
      // Si hay error, mostrar mensaje pero no romper la funcionalidad
      options.value = [];
    } finally {
      loading.value = false;
      loadingCb?.(false);
    }
  }

  function openModal(mode, id = null) {
    console.log('🔍 DEBUG WorkAccountSelector: openModal called with mode:', mode, 'id:', id, 'Type:', typeof id);
    editMode.value = mode === 'edit';
    editId.value = id;
    // Forzar que el formulario inicie limpio al abrir (nueva key)
    formNonce.value++;

    // Use the same pattern as ProductForm
    const modalEl = modal.value;
    if (modalEl) {
      const bootstrapModal = new bootstrap.Modal(modalEl);
      bootstrapModal.show();
    }
  }

  function closeModal() {
    const modalEl = modal.value;
    if (modalEl) {
      const bootstrapModal = bootstrap.Modal.getInstance(modalEl);
      bootstrapModal?.hide();
    }
    // Limpiar estado para siguiente apertura
    if (!editMode.value) {
      editId.value = null;
    }
  }

  function handleSaved(newWorkAccount) {
    // Add to options if not already present
    const existingOption = options.value.find(opt => opt.id === newWorkAccount.id);
    if (!existingOption) {
      options.value.push({
        id: newWorkAccount.id,
        title: newWorkAccount.title,
      });
    }

    // Select the new/updated work account
    selectedValue.value = newWorkAccount.id;

    // Close modal
    closeModal();
  }

  async function ensureWorkAccountInOptions(workAccountId) {
    // Check if the work account is already in options
    const existingOption = options.value.find(opt => opt.id === workAccountId);
    if (existingOption) {
      return; // Already in options
    }
    
    try {
      // Fetch the work account details and add to options
      const { data } = await axios.get(`/api/work-accounts/${workAccountId}/`);
      options.value.push({ id: data.id, title: data.title });
    } catch (error) {
      // Si el work account no existe (404), limpiar el valor seleccionado silenciosamente
      if (error.response?.status === 404) {
        console.warn(`WorkAccount ${workAccountId} not found, clearing selection`);
        selectedValue.value = null;
        emit('update:modelValue', null);
        emit('change', null);
        return;
      }
      
      // Para otros errores, solo logear sin mostrar al usuario
      console.error('Error ensuring work account in options:', error);
    }
  }

  onMounted(async () => {
    // Preload some work accounts so the dropdown isn't empty
    try {
      await searchWorkAccounts('', () => {});
    } catch (error) {
      console.warn('Could not preload work accounts:', error);
      // No mostrar error al usuario, simplemente dejar el dropdown vacío
    }
    
    // If there's an initial value, ensure it's in options
    if (props.modelValue) {
      await ensureWorkAccountInOptions(props.modelValue);
    }
  });
</script>

<style scoped>
  /* Flex layout for select + buttons */
  .d-flex.align-items-center .v-select {
    flex: 1;
    min-width: 0;
  }

  .d-flex.align-items-center .btn {
    flex-shrink: 0;
  }

  /* Fix for vue-select validation */
  :deep(.is-invalid .vs__dropdown-toggle) {
    border-color: #dc3545;
  }

  :deep(.is-invalid .vs__dropdown-toggle:focus) {
    box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
  }

  :deep(.vs__spinner) {
    border-color: #007bff transparent #007bff transparent;
  }
</style>
