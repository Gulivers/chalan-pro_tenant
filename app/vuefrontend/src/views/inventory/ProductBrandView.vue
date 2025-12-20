<template>
  <TxCard class="shadow-sm mt-0">
    <!-- Header del card -->
    <template #header>
      <div class="d-flex justify-content-between align-items-center w-100">
        <h6 class="text-primary mb-0">Product Brands</h6>
        <button class="btn btn-success" @click="goToCreateForm">+ New Brand</button>
      </div>
    </template>

    <!-- Filtros -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <!-- entries per page (izquierda) -->
      <div class="col-md-3">
        <div class="input-group">
          <select v-model="perPage" class="form-select">
            <option v-for="n in [10, 25, 50, 100]" :key="n" :value="n">{{ n }}</option>
          </select>
          <span class="text-primary p-2">entries per page</span>
        </div>
      </div>

      <!-- search (derecha) -->
      <div class="col-md-4">
        <div class="d-flex align-items-center gap-2">
          <span class="text-primary p-2">Search:</span>
          <div class="search-wrapper flex-grow-1">
            <input
              v-model="search"
              type="text"
              class="form-control"
              placeholder="Search by name..."
              autocomplete="off"
            />
            <button
              v-show="search && search.length"
              @mousedown.prevent
              @click="search = ''"
              type="button"
              class="btn-clear-x"
              title="Clear"
            >×</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="text-center py-3">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <div class="mt-2">Loading Brands...</div>
    </div>

    <!-- tabla -->
    <b-table
      v-else
      :items="filteredItems"
      :fields="fields"
      :per-page="perPage"
      :current-page="currentPage"
      bordered
      hover
      responsive
      striped
    >
      <template #cell(is_active)="data">
        <td class="text-center">
          <span v-if="data.item.is_active" class="badge bg-success text-center">Active</span>
          <span v-else class="badge bg-secondary">Inactive</span>
        </td>
      </template>

      <template #cell(is_default)="data">
        <td class="text-center">
          <span v-if="data.item.is_default" class="badge bg-primary">Default</span>
          <span v-else class="badge bg-light text-dark">—</span>
        </td>
      </template>

      <template #cell(actions)="data">
        <td class="text-center">
          <div class="btn-group btn-group-sm" role="group">
            <button class="btn btn-outline-success" @click="viewItem(data.item.id)">
              View
            </button>
            <button class="btn btn-outline-primary" @click="editItem(data.item.id)">
              Edit
            </button>
            <button
              class="btn btn-outline-danger"
              @click="confirmDelete(data.item.id)"
              :disabled="deletingId === data.item.id"
            >
              <span
                v-if="deletingId === data.item.id"
                class="spinner-border spinner-border-sm me-1"
                role="status"
                aria-hidden="true"
              ></span>
              Delete
            </button>
          </div>
        </td>
      </template>
    </b-table>

    <!-- Empty state -->
    <div v-if="!loading && filteredItems.length === 0" class="text-muted text-center py-5">
      <h5>No brands found</h5>
      <p class="mb-0">{{ search ? 'Try a different search term.' : 'Start by creating your first product brand.' }}</p>
    </div>

    <!-- paginación a la derecha -->
    <div v-if="!loading && filteredItems.length > 0" class="d-flex justify-content-end mt-3">
      <b-pagination
        v-model="currentPage"
        :total-rows="filteredItems.length"
        :per-page="perPage"
      />
    </div>
  </TxCard>
</template>

<script setup>
import TxCard from '@/components/layout/TxCard.vue'
import '@/assets/css/base.css'

import { ref, computed, onMounted, getCurrentInstance } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const { proxy } = getCurrentInstance()
const router = useRouter()

const brands = ref([])
const search = ref('')
const perPage = ref(25)
const currentPage = ref(1)
const loading = ref(false)
const deletingId = ref(null)

const fields = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'name', label: 'Name', sortable: true, thClass: 'text-start', tdClass: 'text-start'},
  { key: 'is_active', label: 'Status',thClass: 'text-start' , tdClass: 'text-start' , sortable: true},
  { key: 'is_default', label: 'Default', thClass: 'text-start', tdClass: 'text-start' , sortable: true},
  { key: 'actions', label: 'Actions', thClass: 'text-center', tdClass: 'text-center' },
]

const fetchItems = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/productbrand/')
    brands.value = response.data
  } catch (error) {
    console.error('Error loading brands:', error)
    proxy?.notifyError?.('Error loading product brands.')
  } finally {
    loading.value = false
  }
}

onMounted(fetchItems)

const filteredItems = computed(() => {
  if (!search.value) return brands.value
  const q = search.value.toLowerCase()
  return brands.value.filter(item =>
    item.name.toLowerCase().includes(q)
  )
})

const goToCreateForm = () => {
  router.push({ name: 'product-brand-form' })
}

const viewItem = (id) => {
  router.push({ name: 'product-brand-view', params: { id } })
}

const editItem = (id) => {
  router.push({ name: 'product-brand-edit', params: { id } })
}

const confirmDelete = (id) => {
  proxy?.confirmDelete?.(
    'Delete?',
    'This will delete the product brand. This action cannot be undone.',
    async () => {
      await deleteItem(id)
    }
  )
}

const deleteItem = async (id) => {
  deletingId.value = id
  try {
    await axios.delete(`/api/productbrand/${id}/`)
    brands.value = brands.value.filter(b => b.id !== id)
    proxy?.notifyToastSuccess?.('The product brand has been deleted.')
  } catch (error) {
    console.error('Error deleting product brand:', error)
    proxy?.notifyError?.('Error deleting the product brand.')
  } finally {
    deletingId.value = null
  }
}
</script>

<style scoped>
</style>
