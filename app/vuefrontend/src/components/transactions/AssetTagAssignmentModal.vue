<template>
  <BModal
    :model-value="show"
    @update:model-value="emit('close')"
    title="Assign Asset Tags"
    size="xl"
    modal-class="asset-tag-modal"
    body-class="p-0 overflow-auto"
    footer-class="d-flex justify-content-end gap-2"
    hide-header-close
    no-close-on-backdrop
  >
    <template #header>
      <div class="w-100">
        <h5 class="modal-title mb-1">Assign Asset Tags</h5>
        <div v-if="contextLoaded" class="small text-muted">
          <strong>Document:</strong> {{ headerDocument }} — {{ headerDate }}<br>
          <strong>Serialized units:</strong> {{ items.length }} items — <strong>Missing tags:</strong> {{ missingCount }}
        </div>
      </div>
      <button type="button" class="btn-close" aria-label="Close" @click="onSkip"></button>
    </template>

    <div class="p-3">
      <p v-if="!loading && items.length > 0" class="text-muted small mb-3">
        This purchase includes serialized equipment. Assign asset tags now or skip to complete later.
      </p>

      <div v-if="loading" class="text-center py-5">
        <BSpinner variant="primary" />
        <p class="mt-2 mb-0">Loading items...</p>
      </div>

      <div v-else-if="items.length === 0" class="alert alert-warning mb-0">
        No serialized items found for this document.
      </div>

      <div v-else class="table-responsive" style="max-height: 60vh; overflow-y: auto;">
        <table class="table table-sm table-hover table-bordered align-middle mb-0">
          <thead class="table-light sticky-top">
            <tr>
              <th class="text-center">#</th>
              <th>Line ID</th>
              <th>Product</th>
              <th>Asset Tag</th>
              <th>Status</th>
              <th>Condition</th>
              <th>Warehouse</th>
              <th>Purchase Date</th>
              <th>Document ID</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(item, idx) in sortedItems"
              :key="item.id"
              :class="{ 'table-warning': item._error }"
            >
              <td class="text-center">{{ idx + 1 }}</td>
              <td>{{ item.document_line || '—' }}</td>
              <td>{{ item.product_name }}</td>
              <td>
                <div class="d-flex align-items-center gap-1">
                  <input
                    :ref="(el) => setInputRef(el, idx)"
                    v-model.trim="item._asset_tag"
                    type="text"
                    class="form-control form-control-sm"
                    :class="inputClass(item)"
                    placeholder="Optional"
                    maxlength="100"
                    @keydown.enter="focusNext(idx)"
                    @input="validateRow(item)"
                  />
                  <span v-if="item._validation === 'valid'" class="badge bg-success">✅</span>
                  <span v-else-if="item._validation === 'invalid'" class="badge bg-danger" :title="item._error">❌</span>
                </div>
                <small v-if="item._error" class="text-danger">{{ item._error }}</small>
              </td>
              <td><span class="badge bg-secondary">{{ item.status }}</span></td>
              <td>
                <span
                  class="badge"
                  :class="conditionBadgeClass(item.condition)"
                >
                  {{ conditionLabel(item.condition) }}
                </span>
              </td>
              <td>{{ item.current_warehouse_name || '—' }}</td>
              <td>{{ formatDate(item.purchase_date) }}</td>
              <td>{{ item.document_id || '—' }}</td>
              <td>
                <input
                  v-model.trim="item._notes"
                  type="text"
                  class="form-control form-control-sm"
                  placeholder="Notes"
                  maxlength="500"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <template #footer>
      <BButton variant="outline-secondary" @click="onClose">Close</BButton>
      <BButton variant="outline-primary" @click="onSkip">Skip for now</BButton>
      <BButton variant="primary" :disabled="saving" @click="onSave">
        <BSpinner v-if="saving" small class="me-1" />
        {{ saving ? 'Saving...' : 'Save Tags' }}
      </BButton>
    </template>
  </BModal>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import axios from 'axios'
import { BModal, BButton, BSpinner } from 'bootstrap-vue-next'

const props = defineProps({
  show: { type: Boolean, default: false },
  documentId: { type: Number, default: null },
  documentContext: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['close', 'saved'])

const items = ref([])
const loading = ref(false)
const saving = ref(false)
const inputRefs = ref([])
const contextLoaded = ref(false)

const headerDocument = computed(() => {
  const ctx = props.documentContext
  const code = ctx.document_type_code || 'DOC'
  const id = ctx.id ?? props.documentId
  const party = ctx.builder_name || ctx.party_name || '—'
  return `${code} #${id} (${party})`
})

const headerDate = computed(() => {
  const d = props.documentContext?.date
  if (!d) return ''
  return formatDate(d)
})

const missingCount = computed(() => {
  return items.value.filter((i) => !i._asset_tag?.trim()).length
})

const sortedItems = computed(() => {
  const list = [...items.value]
  list.sort((a, b) => {
    const pa = (a.product_name || '').toLowerCase()
    const pb = (b.product_name || '').toLowerCase()
    return pa.localeCompare(pb) || (a.id - b.id)
  })
  return list
})

watch(
  () => [props.show, props.documentId],
  async ([show, docId]) => {
    contextLoaded.value = !!props.documentContext?.document_type_code
    if (show && docId) {
      await loadItems()
    } else if (!show) {
      items.value = []
    }
  },
  { immediate: true }
)

function setInputRef(el, idx) {
  if (el) inputRefs.value[idx] = el
}

function inputClass(item) {
  if (item._validation === 'valid') return 'border-success'
  if (item._validation === 'invalid') return 'is-invalid'
  return ''
}

function conditionBadgeClass(value) {
  const v = (value || '').toLowerCase()
  if (v === 'ok') return 'bg-success'
  if (v === 'damaged') return 'bg-warning text-dark'
  if (v === 'needs_repair') return 'bg-danger'
  return 'bg-secondary'
}

function conditionLabel(value) {
  const labels = { ok: 'OK', damaged: 'Damaged', needs_repair: 'Needs Repair' }
  const v = (value || '').toLowerCase().replace(/\s/g, '_')
  return labels[v] || value || '—'
}

function formatDate(dateString) {
  if (!dateString) return '—'
  const d = new Date(dateString)
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function validateRow(item) {
  const tag = (item._asset_tag || '').trim()
  if (!tag) {
    item._validation = 'invalid'
    item._error = 'Required'
    return
  }
  const seen = new Map()
  items.value.forEach((i) => {
    const t = (i._asset_tag || '').trim()
    if (t) seen.set(t.toLowerCase(), (seen.get(t.toLowerCase()) || 0) + 1)
  })
  const count = seen.get(tag.toLowerCase()) || 0
  if (count > 1) {
    item._validation = 'invalid'
    item._error = 'Duplicate tag'
    return
  }
  item._validation = 'valid'
  item._error = null
}

function hasDuplicates() {
  const seen = new Map()
  items.value.forEach((i) => {
    const t = (i._asset_tag || '').trim()
    if (t) seen.set(t.toLowerCase(), (seen.get(t.toLowerCase()) || 0) + 1)
  })
  return [...seen.values()].some((c) => c > 1)
}

function validateAll() {
  items.value.forEach((i) => validateRow(i))
}

function focusNext(currentIdx) {
  nextTick(() => {
    const sorted = sortedItems.value
    const nextIdx = currentIdx + 1
    if (nextIdx < sorted.length && inputRefs.value[nextIdx]) {
      inputRefs.value[nextIdx].focus()
    }
  })
}

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
      _notes: i.notes || '',
      _validation: null,
      _error: null,
    }))
  } catch (err) {
    console.error('Error loading serialized items:', err)
    items.value = []
  } finally {
    loading.value = false
    nextTick(() => validateAll())
  }
}

function onClose() {
  emit('close')
}

function onSkip() {
  emit('close')
}

async function onSave() {
  validateAll()
  if (hasDuplicates()) {
    return
  }
  const emptyCount = items.value.filter((i) => !(i._asset_tag || '').trim()).length
  if (emptyCount > 0 && !confirm(`${emptyCount} item(s) have no asset tag. Save anyway?`)) {
    return
  }

  const payload = items.value.map((i) => ({
    id: i.id,
    asset_tag: i._asset_tag?.trim() || '',
    notes: i._notes?.trim() || '',
  }))

  saving.value = true
  try {
    await axios.patch('/api/serialized-items/bulk-update-tags/', { items: payload })
    emit('saved')
    emit('close')
  } catch (err) {
    const errData = err?.response?.data
    const errors = errData?.errors || []
    items.value.forEach((i) => (i._error = null))
    errors.forEach((e) => {
      const item = items.value.find((i) => i.id === e.id)
      if (item) {
        item._error = e.detail || 'Error'
        item._validation = 'invalid'
      }
    })
    if (errors.length === 0 && errData?.detail) {
      alert(errData.detail)
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.asset-tag-modal :deep(.modal-dialog) {
  max-width: 95vw;
}

.asset-tag-modal :deep(.modal-body) {
  max-height: 70vh;
  overflow-y: auto;
}

.sticky-top {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #f8f9fa;
}
</style>
