<template>
  <div
    class="modal fade"
    :id="modalId"
    tabindex="-1"
    aria-labelledby="assetTagModalLabel"
    aria-hidden="true"
    data-bs-backdrop="static"
  >
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="assetTagModalLabel">
            Assign Asset Tags
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close" @click="onSkip"></button>
        </div>
        <div class="modal-body">
          <p class="text-muted small mb-3">
            This purchase includes serialized equipment. Assign asset tags now or skip to complete later.
          </p>
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2 mb-0">Loading items...</p>
          </div>
          <div v-else-if="items.length === 0" class="alert alert-warning mb-0">
            No serialized items found for this document.
          </div>
          <div v-else class="table-responsive">
            <table class="table table-sm table-hover align-middle">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Product</th>
                  <th>Asset Tag</th>
                  <th>Status</th>
                  <th>Condition</th>
                  <th>Warehouse</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in items" :key="item.id" :class="{ 'table-warning': item._error }">
                  <td>{{ idx + 1 }}</td>
                  <td>{{ item.product_name }}</td>
                  <td>
                    <input
                      v-model.trim="item._asset_tag"
                      type="text"
                      class="form-control form-control-sm"
                      :class="{ 'is-invalid': item._error }"
                      placeholder="Optional"
                      maxlength="100"
                    />
                    <div v-if="item._error" class="invalid-feedback d-block">{{ item._error }}</div>
                  </td>
                  <td><span class="badge bg-secondary">{{ item.status }}</span></td>
                  <td><span class="badge bg-secondary">{{ item.condition }}</span></td>
                  <td>{{ item.current_warehouse_name || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" @click="onSkip">
            Skip
          </button>
          <button type="button" class="btn btn-primary" :disabled="saving" @click="onSave">
            <span v-if="saving" class="spinner-border spinner-border-sm me-1" role="status"></span>
            {{ saving ? 'Saving...' : 'Assign Tags' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'

const props = defineProps({
  show: { type: Boolean, default: false },
  documentId: { type: Number, default: null },
  mode: { type: String, default: 'purchase' },
})

const emit = defineEmits(['close', 'saved'])

const modalId = 'assetTagAssignmentModal'
const items = ref([])
const loading = ref(false)
const saving = ref(false)

watch(
  () => [props.show, props.documentId],
  async ([show, docId]) => {
    if (show && docId) {
      await loadItems()
      await nextTick()
      const el = document.getElementById(modalId)
      if (el && typeof bootstrap !== 'undefined') {
        let modal = bootstrap.Modal.getInstance(el)
        if (!modal) {
          modal = new bootstrap.Modal(el)
        }
        modal.show()
      }
    }
  },
  { immediate: true }
)

async function loadItems() {
  if (!props.documentId) return
  loading.value = true
  items.value = []
  try {
    const { data } = await axios.get('/api/serialized-items/', {
      params: { document: props.documentId },
    })
    const list = Array.isArray(data) ? data : data?.results || []
    items.value = list.map((i) => ({
      ...i,
      _asset_tag: i.asset_tag || '',
      _error: null,
    }))
  } catch (err) {
    console.error('Error loading serialized items:', err)
    items.value = []
  } finally {
    loading.value = false
  }
}

function onSkip() {
  const el = document.getElementById(modalId)
  if (el && typeof bootstrap !== 'undefined') {
    const modal = bootstrap.Modal.getInstance(el)
    if (modal) modal.hide()
  }
  emit('close')
}

async function onSave() {
  const payload = items.value.map((i) => ({ id: i.id, asset_tag: i._asset_tag || '' }))
  saving.value = true
  items.value.forEach((i) => (i._error = null))
  try {
    await axios.patch('/api/serialized-items/bulk-update-tags/', { items: payload })
    if (typeof Swal !== 'undefined') {
      Swal.fire({ toast: true, position: 'bottom-end', icon: 'success', title: 'Asset tags saved.', showConfirmButton: false, timer: 2500 })
    }
    const el = document.getElementById(modalId)
    if (el && typeof bootstrap !== 'undefined') {
      const modal = bootstrap.Modal.getInstance(el)
      if (modal) modal.hide()
    }
    emit('saved')
    emit('close')
  } catch (err) {
    const errData = err?.response?.data
    const errors = errData?.errors || []
    errors.forEach((e) => {
      const item = items.value.find((i) => i.id === e.id)
      if (item) item._error = e.detail
    })
    if (errors.length === 0 && errData?.detail) {
      Swal.fire('Error', errData.detail, 'error')
    }
  } finally {
    saving.value = false
  }
}
</script>
