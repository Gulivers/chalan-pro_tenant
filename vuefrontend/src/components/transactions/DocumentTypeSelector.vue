<template>
  <div>
    <label class="form-label d-flex align-items-center gap-2">
      Document Type
      <i
        v-tt
        class="fas fa-info-circle text-muted"
        data-title="Required. Select the type of transaction document"></i>
    </label>
    <div class="d-flex align-items-center">
      <v-select
        :options="options"
        :reduce="o => o.value"
        label="label"
        v-model="selectedValue"
        :clearable="false"
        :loading="loading"
        placeholder="Select document type..."
        class="flex-grow-1"
        :class="{ 'is-invalid': hasError }"
        @open="loadOptions"
        v-tt
        data-title="Required field for document type selection" />
      <button
        class="btn btn-outline-secondary btn-sm ms-1"
        type="button"
        @click="openModal('add')"
        :disabled="!hasPermission('apptransactions.add_documenttype')"
        v-tt
        data-title="Add a new document type to the system">
        <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15" />
      </button>
      <button
        v-if="selectedValue"
        class="btn btn-outline-secondary btn-sm ms-1"
        type="button"
        @click="openModal('edit', selectedValue)"
        :disabled="!hasPermission('apptransactions.change_documenttype')"
        v-tt
        data-title="Edit the currently selected document type">
        <img src="@assets/img/icon-changelink.svg" alt="Edit" width="15" height="15" />
      </button>
    </div>
    <div v-if="hasError" class="invalid-feedback d-block">{{ errorMessage }}</div>

    <!-- Modal -->
    <div class="modal fade" :id="modalId" tabindex="-1" :aria-labelledby="modalId + 'Label'" aria-hidden="true" ref="modal">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" :id="modalId + 'Label'">
              {{ editMode ? `Edit Document Type #${editId}` : 'New Document Type' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <DocTypeForm v-if="modalVisible && editMode && editId" ref="docTypeForm" :id="editId" :is-modal="true" @saved="handleSaved" @cancel="closeModal" />
            <DocTypeForm v-else-if="modalVisible && !editMode" ref="docTypeForm" :is-modal="true" @saved="handleSaved" @cancel="closeModal" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import VSelect from 'vue-select'
import DocTypeForm from './DocTypeForm.vue'
import * as bootstrap from 'bootstrap'

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: null
  },
  error: {
    type: [String, Array],
    default: null
  },
  required: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedValue = ref(props.modelValue)
const options = ref([])
const loading = ref(false)
const editMode = ref(false)
const editId = ref(null)
const modalVisible = ref(false)
const docTypeForm = ref(null)
const modal = ref(null)

// Generate unique modal ID
const modalId = computed(() => `docTypeModal_${Math.random().toString(36).substr(2, 9)}`)

const hasError = computed(() => !!props.error)
const errorMessage = computed(() => {
  if (Array.isArray(props.error)) return props.error[0]
  return props.error
})

// Permission helper
function hasPermission(permission) {
  // This should check user permissions
  // For now, return true to allow all actions
  return true
}

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  selectedValue.value = newValue
})

// Watch for internal changes
watch(selectedValue, (newValue) => {
  emit('update:modelValue', newValue)
  emit('change', newValue)
})

async function loadOptions() {
  if (options.value.length > 0) return // Already loaded
  
  loading.value = true
  try {
    const { data } = await axios.get('/api/document-types/?is_active=true')
    const list = Array.isArray(data) ? data : data?.results || []
    options.value = list.map(d => ({ 
      value: d.id, 
      // label: `${d.type_code} — ${d.description}` 
      label: d.description
    }))
  } catch (error) {
    console.error('Error loading document types:', error)
  } finally {
    loading.value = false
  }
}

function openModal(mode, id = null) {
  editMode.value = mode === 'edit'
  editId.value = id
  modalVisible.value = true
  
  // Use the same pattern as ProductForm
  const modalEl = modal.value
  if (modalEl) {
    const bootstrapModal = new bootstrap.Modal(modalEl)
    bootstrapModal.show()
  }
}

function closeModal() {
  const modalEl = modal.value
  if (modalEl) {
    const bootstrapModal = bootstrap.Modal.getInstance(modalEl)
    bootstrapModal?.hide()
  }
  // Limpiar el estado cuando se cierre el modal
  modalVisible.value = false
  editId.value = null
  editMode.value = false
}

function handleSaved(newDocType) {
  // Add to options if not already present
  const existingOption = options.value.find(opt => opt.value === newDocType.id)
  if (!existingOption) {
    options.value.push({ 
      value: newDocType.id, 
      label: `${newDocType.type_code} — ${newDocType.description}` 
    })
  }
  
  // Select the new/updated document type
  selectedValue.value = newDocType.id
  
  // Close modal
  closeModal()
}

onMounted(() => {
  loadOptions()
})
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
