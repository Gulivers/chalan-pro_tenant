<template>
  <TxCard class="shadow-sm mt-0">
    <!-- Header del card -->
    <template #header>
      <div class="d-flex justify-content-between align-items-center w-100">
        <h6 class="text-primary mb-0">Parties</h6>
        <router-link to="/parties/form" class="btn btn-success">+ New Party</router-link>
      </div>
    </template>

    <!-- Filtros -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <!-- entries per page (izq) -->
      <div class="col-md-3">
        <div class="input-group">
          <select v-model="perPage" class="form-select">
            <option v-for="n in [5, 10, 25, 50]" :key="n" :value="n">{{ n }}</option>
          </select>
          <span class="text-primary p-2">entries per page</span>
        </div>
      </div>

      <!-- search (der) -->
      <div class="col-md-4">
        <div class="d-flex align-items-center gap-2">
          <span class="text-primary p-2">Search:</span>
          <div class="search-wrapper flex-grow-1">
            <input
              v-model="search"
              type="text"
              class="form-control"
              placeholder="Search by name, email, phone, city, state..."
              autocomplete="off" />
            <button
              v-show="search && search.length"
              @mousedown.prevent
              @click="search = ''"
              type="button"
              class="btn-clear-x"
              title="Clear">
              ×
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- tabla -->
    <b-table
      :items="filteredItems"
      :fields="fields"
      :per-page="perPage"
      :current-page="currentPage"
      bordered
      hover
      responsive
      striped
    >
      <template #cell(category)="data">
        {{ categoriesMap[data.item.category] || '—' }}
      </template>

      <template #cell(customer_rank)="data">
        <td class="text-center">{{ data.item.customer_rank }}</td>
      </template>

      <template #cell(supplier_rank)="data">
        <td class="text-center">{{ data.item.supplier_rank }}</td>
      </template>

      <template #cell(is_active)="data">
        <td class="text-center">
          <span v-if="data.item.is_active" class="badge bg-success">Active</span>
          <span v-else class="badge bg-secondary">Inactive</span>
        </td>
      </template>

      <template #cell(actions)="data">
        <td class="text-center">
          <div class="btn-group btn-group-sm" role="group">
            <router-link
              :to="`/parties/form?id=${data.item.id}&mode=view`"
              class="btn btn-outline-success me-1"
            >
              View
            </router-link>
            <router-link
              :to="`/parties/form?id=${data.item.id}`"
              class="btn btn-outline-primary me-1"
            >
              Edit
            </router-link>
            <button @click="deleteParty(data.item.id, data.item.name)" class="btn btn-outline-danger">
              Delete
            </button>
          </div>
        </td>
      </template>
    </b-table>

    <!-- paginación a la derecha -->
    <div class="d-flex justify-content-end mt-3">
      <b-pagination v-model="currentPage" :total-rows="filteredItems.length" :per-page="perPage" />
    </div>
  </TxCard>
</template>

<script setup>
import TxCard from '@/components/layout/TxCard.vue'
import '@/assets/css/base.css'

import { ref, computed, onMounted, getCurrentInstance } from 'vue'
import axios from 'axios'

const { proxy } = getCurrentInstance()

const parties = ref([])
const categoriesMap = ref({}) // id -> name
const search = ref('')
const perPage = ref(10)
const currentPage = ref(1)

const fields = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'name', label: 'Name', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'phone', label: 'Phone', sortable: true },
  { key: 'city', label: 'City', sortable: true },
  { key: 'state', label: 'State', sortable: true },
  { key: 'category', label: 'Category' },
  { key: 'customer_rank', label: 'Cust.', thClass: 'text-center', tdClass: 'text-center', sortable: true },
  { key: 'supplier_rank', label: 'Supp.', thClass: 'text-center', tdClass: 'text-center', sortable: true },
  { key: 'is_active', label: 'Status', thClass: 'text-center', tdClass: 'text-center', sortable: true },
  { key: 'actions', label: 'Actions', thClass: 'text-center', tdClass: 'text-center' },
]

// Helpers para DRF con o sin paginación
const normalizeList = (data) => Array.isArray(data) ? data : (data?.results ?? [])
const fetchParties = async () => {
  try {
    const res = await axios.get('/api/parties/?ordering=name')
    parties.value = normalizeList(res.data)
  } catch (err) {
    console.error('Error fetching parties', err)
    proxy?.notifyError?.('Error loading parties.')
  }
}
const fetchCategories = async () => {
  try {
    const res = await axios.get('/api/party-categories/?ordering=name')
    const arr = normalizeList(res.data)
    categoriesMap.value = Object.fromEntries(arr.map(c => [c.id, c.name]))
  } catch (err) {
    console.error('Error fetching categories', err)
    proxy?.notifyError?.('Error loading categories.')
  }
}

onMounted(async () => {
  await Promise.all([fetchParties(), fetchCategories()])
})

const filteredItems = computed(() => {
  if (!search.value) return parties.value
  const q = search.value.toLowerCase()
  return parties.value.filter(item => {
    const hay = [
      item.name, item.email, item.phone, item.city, item.state
    ].map(v => (v || '').toString().toLowerCase())
    return hay.some(t => t.includes(q))
  })
})

const deleteParty = (id, name) => {
  proxy?.confirmDelete?.(
    'Are you sure?',
    `Delete "${name}"? This action cannot be undone.`,
    async () => {
      try {
        await axios.delete(`/api/parties/${id}/`)
        parties.value = parties.value.filter(p => p.id !== id)
        proxy?.notifyToastSuccess?.('The party has been deleted.')
      } catch (err) {
        console.error('Error deleting party', err)
        // Manejo de tu custom_exception_handler (409 in use)
        const detail = err?.response?.data?.detail || 'Error deleting the party.'
        proxy?.notifyError?.(detail)
      }
    }
  )
}
</script>

<style scoped>
/* Reusa estilos de PartyCategoryList: clear de input */
.search-wrapper { position: relative; }
.btn-clear-x {
  position: absolute; right: .5rem; top: 50%;
  transform: translateY(-50%);
  border: none; background: transparent; font-size: 1.25rem; line-height: 1;
}
</style>
