<template>
  <div>
    <label class="form-label d-flex align-items-center gap-2">
      Party
      <i
        v-tt
        class="fas fa-info-circle text-muted"
        data-title="Customer or Supplier for this transaction"></i>
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
        @search="searchParties"
        v-tt
        data-title="Search and select a party (customer or supplier)">
        <template #no-options>Type to search parties...</template>
      </v-select>
      <button
        class="btn btn-outline-secondary btn-sm ms-1"
        type="button"
        @click="openModal('add')"
        :disabled="!hasPermission('apptransactions.add_party')"
        v-tt
        data-title="Add a new party to the system">
        <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15" />
      </button>
      <button
        v-if="selectedValue"
        class="btn btn-outline-secondary btn-sm ms-1"
        type="button"
        @click="openModal('edit', selectedValue)"
        :disabled="!hasPermission('apptransactions.change_party')"
        v-tt
        data-title="Edit the currently selected party">
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
              {{ editMode ? `Edit Party #${editId}` : 'New Party' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <PartyForm v-if="modalVisible && editMode && editId" ref="partyForm" :id="editId" :is-modal="true" @saved="handleSaved" @cancel="closeModal" />
            <PartyForm v-else-if="modalVisible && !editMode" ref="partyForm" :is-modal="true" @saved="handleSaved" @cancel="closeModal" />
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
import PartyForm from './PartyForm.vue'
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
const partyForm = ref(null)
const modal = ref(null)

// Generate unique modal ID
const modalId = computed(() => `partyModal_${Math.random().toString(36).substr(2, 9)}`)

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

async function searchParties(search, loadingCb) {
  loading.value = true
  loadingCb?.(true)
  try {
    const { data } = await axios.get('/api/parties/?is_active=true', { params: { search, page_size: 20 } })
    const list = Array.isArray(data) ? data : data?.results || []
    options.value = list.map(p => ({ value: p.id, label: p.name }))
  } catch (error) {
    console.error('Error searching parties:', error)
  } finally {
    loading.value = false
    loadingCb?.(false)
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

function handleSaved(newParty) {
  // Add to options if not already present
  const existingOption = options.value.find(opt => opt.value === newParty.id)
  if (!existingOption) {
    options.value.push({ 
      value: newParty.id, 
      label: newParty.name 
    })
  }
  
  // Select the new/updated party
  selectedValue.value = newParty.id
  
  // Close modal
  closeModal()
}

onMounted(async () => {
  // Preload some parties so the dropdown isn't empty
  await searchParties('', () => {})
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
