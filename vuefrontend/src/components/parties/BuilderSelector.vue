<template>
  <div>
    <label class="form-label d-flex align-items-center gap-2">
      Party
      <i
        v-tt
        class="fas fa-info-circle text-muted"
        data-title="Party for this transaction"></i>
    </label>
    <div class="d-flex align-items-center">
      <v-select
        :options="options"
        :reduce="o => o.value"
        label="label"
        v-model="selectedValue"
        :filterable="true"
        :clearable="true"
        :loading="loading"
        placeholder="Search party..."
        class="flex-grow-1"
        :class="{ 'is-invalid': hasError }"
        @search="searchBuilders"
        v-tt
        data-title="Search and select a party">
        <template #no-options>Type to search parties...</template>
      </v-select>
      <AddBuilderButton 
        :is-disabled="!hasPermission('ctrctsapp.add_builder')"
        @builder-added="handleBuilderAdded" />
      <EditBuilderButton 
        v-if="selectedValue && selectedBuilder"
        :builder="selectedBuilder"
        :is-disabled="!hasPermission('ctrctsapp.change_builder')"
        @builder-updated="handleBuilderUpdated" />
    </div>
    <div v-if="hasError" class="invalid-feedback d-block">{{ errorMessage }}</div>

    <!-- Modal -->
    <div class="modal fade" :id="modalId" tabindex="-1" :aria-labelledby="modalId + 'Label'" aria-hidden="true" ref="modal">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" :id="modalId + 'Label'">
              {{ editMode ? `Edit Party #${editId}` : 'New Party' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <DynamicForm 
              v-if="modalVisible && editMode && editId" 
              ref="builderForm" 
              :schema-endpoint="'/api/schema/builder/'"
              :api-endpoint="'/api/builder/'"
              :object-id="editId"
              :form-title="'Edit Party'"
              :is-modal="true"
              @saved="handleSaved" 
              @cancel="closeModal" />
            <DynamicForm 
              v-else-if="modalVisible && !editMode" 
              ref="builderForm" 
              :schema-endpoint="'/api/schema/builder/'"
              :api-endpoint="'/api/builder/'"
              :form-title="'Create Party'"
              :is-modal="true"
              @saved="handleSaved" 
              @cancel="closeModal" />
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
import DynamicForm from './DynamicForm.vue'
import AddBuilderButton from '@/components/buttons/AddBuilderButton.vue'
import EditBuilderButton from '@/components/buttons/EditBuilderButton.vue'
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
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedValue = ref(props.modelValue)
const options = ref([])
const loading = ref(false)
const editMode = ref(false)
const editId = ref(null)
const modalVisible = ref(false)
const builderForm = ref(null)
const modal = ref(null)
const selectedBuilder = ref(null)

// Generate unique modal ID
const modalId = computed(() => `builderModal_${Math.random().toString(36).substr(2, 9)}`)

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
watch(() => props.modelValue, async (newValue) => {
  selectedValue.value = newValue
  // If there's a new value, ensure it's in options
  if (newValue) {
    await ensureBuilderInOptions(newValue)
    await fetchBuilderDetails(newValue)
  }
})

// Watch for internal changes
watch(selectedValue, (newValue) => {
  emit('update:modelValue', newValue)
  emit('change', newValue)
  
  // Update selectedBuilder when selectedValue changes
  if (newValue) {
    const option = options.value.find(opt => opt.value === newValue)
    if (option) {
      // We need to fetch the full builder data
      fetchBuilderDetails(newValue)
    }
  } else {
    selectedBuilder.value = null
  }
})

async function searchBuilders(search, loadingCb) {
  loading.value = true
  loadingCb?.(true)
  try {
    const { data } = await axios.get('/api/builder/?is_active=true', { params: { search, page_size: 20 } })
    const list = Array.isArray(data) ? data : data?.results || []
    options.value = list.map(b => ({ value: b.id, label: b.name }))
  } catch (error) {
    console.error('Error searching builders:', error)
  } finally {
    loading.value = false
    loadingCb?.(false)
  }
}

async function fetchBuilderDetails(builderId) {
  try {
    const { data } = await axios.get(`/api/builder/${builderId}/`)
    selectedBuilder.value = data
  } catch (error) {
    console.error('Error fetching builder details:', error)
    selectedBuilder.value = null
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

function handleSaved(newBuilder) {
  // Add to options if not already present
  const existingOption = options.value.find(opt => opt.value === newBuilder.id)
  if (!existingOption) {
    options.value.push({ 
      value: newBuilder.id, 
      label: newBuilder.name 
    })
  }
  
  // Select the new/updated builder
  selectedValue.value = newBuilder.id
  
  // Close modal
  closeModal()
}

function handleBuilderAdded(event) {
  const newBuilder = event.builder
  if (!newBuilder || !newBuilder.id) {
    console.error('Invalid builder data received:', newBuilder)
    return
  }
  
  // Add to options if not already present
  const existingOption = options.value.find(opt => opt.value === newBuilder.id)
  if (!existingOption) {
    options.value.push({ 
      value: newBuilder.id, 
      label: newBuilder.name 
    })
  }
  
  // Select the new builder
  selectedValue.value = newBuilder.id
}

function handleBuilderUpdated(event) {
  const updatedBuilder = event.builder
  if (!updatedBuilder || !updatedBuilder.id) {
    console.error('Invalid updated builder data received:', updatedBuilder)
    return
  }
  
  // Update the option in the list
  const existingOption = options.value.find(opt => opt.value === updatedBuilder.id)
  if (existingOption) {
    existingOption.label = updatedBuilder.name
  }
  
  // Update selectedBuilder if it's the same one
  if (selectedBuilder.value && selectedBuilder.value.id === updatedBuilder.id) {
    selectedBuilder.value = updatedBuilder
  }
}

async function ensureBuilderInOptions(builderId) {
  // Check if the builder is already in options
  const existingOption = options.value.find(opt => opt.value === builderId)
  if (existingOption) {
    return // Already in options
  }
  
  try {
    // Fetch the builder details and add to options
    const { data } = await axios.get(`/api/builder/${builderId}/`)
    options.value.push({ 
      value: data.id, 
      label: data.name 
    })
  } catch (error) {
    // Si el builder no existe (404), limpiar el valor seleccionado silenciosamente
    if (error.response?.status === 404) {
      console.warn(`Builder ${builderId} not found, clearing selection`)
      selectedValue.value = null
      emit('update:modelValue', null)
      emit('change', null)
      return
    }
    
    // Para otros errores, solo logear sin mostrar al usuario
    console.error('Error ensuring builder in options:', error)
  }
}

onMounted(async () => {
  // Preload some builders so the dropdown isn't empty
  await searchBuilders('', () => {})
  
  // If there's an initial value, fetch its details and ensure it's in options
  if (props.modelValue) {
    await fetchBuilderDetails(props.modelValue)
    await ensureBuilderInOptions(props.modelValue)
  }
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
