<template>
  <TxCard class="shadow-sm mt-0">
    <!-- Header del card -->
    <template #header>
      <div class="d-flex justify-content-between align-items-center w-100">
        <h6 class="text-primary mb-0">Jobs (Communities)</h6>
        <router-link to="/job/form" class="btn btn-success">+ New Job</router-link>
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
              placeholder="Search by name, address, builder..."
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
      <template #cell(builder)="data">
        {{ data.item.builder?.name || '—' }}
      </template>

      <template #cell(actions)="data">
        <td class="text-center">
          <div class="btn-group btn-group-sm" role="group">
            <router-link
              :to="`/job/view/${data.item.id}`"
              class="btn btn-outline-success me-1"
            >
              View
            </router-link>
            <router-link
              :to="`/job/edit/${data.item.id}`"
              class="btn btn-outline-primary me-1"
            >
              Edit
            </router-link>
            <button @click="deleteJob(data.item.id, data.item.name)" class="btn btn-outline-danger">
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

const jobs = ref([])
const search = ref('')
const perPage = ref(10)
const currentPage = ref(1)

const fields = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'name', label: 'Job Name', sortable: true },
  { key: 'builder', label: 'Builder', sortable: true },
  { key: 'address', label: 'Address', sortable: true },
  { key: 'latitude', label: 'Latitude', sortable: true },
  { key: 'longitude', label: 'Longitude', sortable: true },
  { key: 'actions', label: 'Actions', thClass: 'text-center', tdClass: 'text-center' },
]

// Helpers para DRF con o sin paginación
const normalizeList = (data) => Array.isArray(data) ? data : (data?.results ?? [])
const fetchJobs = async () => {
  try {
    const res = await axios.get('/api/job/?ordering=name')
    jobs.value = normalizeList(res.data)
  } catch (err) {
    console.error('Error fetching jobs', err)
    proxy?.notifyError?.('Error loading jobs.')
  }
}

onMounted(async () => {
  await fetchJobs()
})

const filteredItems = computed(() => {
  if (!search.value) return jobs.value
  const q = search.value.toLowerCase()
  return jobs.value.filter(item => {
    const hay = [
      item.name, item.address, item.builder?.name
    ].map(v => (v || '').toString().toLowerCase())
    return hay.some(t => t.includes(q))
  })
})

const deleteJob = (id, name) => {
  proxy?.confirmDelete?.(
    'Are you sure?',
    `Delete "${name}"? This action cannot be undone.`,
    async () => {
      try {
        await axios.delete(`/api/job/${id}/`)
        jobs.value = jobs.value.filter(p => p.id !== id)
        proxy?.notifyToastSuccess?.('The job has been deleted.')
      } catch (err) {
        console.error('Error deleting job', err)
        // Manejo de tu custom_exception_handler (409 in use)
        const detail = err?.response?.data?.detail || 'Error deleting the job.'
        proxy?.notifyError?.(detail)
      }
    }
  )
}
</script>

<style scoped>
/* Reusa estilos de PartyListView: clear de input */
.search-wrapper { position: relative; }
.btn-clear-x {
  position: absolute; right: .5rem; top: 50%;
  transform: translateY(-50%);
  border: none; background: transparent; font-size: 1.25rem; line-height: 1;
}
</style>

