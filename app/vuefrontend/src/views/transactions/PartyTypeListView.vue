<template>
  <TxCard class="shadow-sm mt-0">
    <!-- Header del card -->
    <template #header>
      <div class="d-flex justify-content-between align-items-center w-100">
        <h6 class="text-primary mb-0">Party Types</h6>
        <router-link to="/party-types/form" class="btn btn-success">+ New Party Type</router-link>
      </div>
    </template>

    <!-- Filtros -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <!-- entries per page (izquierda) -->
      <div class="col-md-3">
        <div class="input-group">
          <select v-model="perPage" class="form-select">
            <option v-for="n in [5, 10, 25, 50]" :key="n" :value="n">{{ n }}</option>
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
              placeholder="Search by name or description..."
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
      <template #cell(is_active)="data">
        <td class="text-center">
          <span v-if="data.item.is_active" class="badge bg-success">Active</span>
          <span v-else class="badge bg-secondary">Inactive</span>
        </td>
      </template>

      <template #cell(actions)="data">
        <td class="text-center">
          <div class="btn-group btn-group-sm" role="group">
            <router-link :to="`/party-types/form?id=${data.item.id}&mode=view`" class="btn btn-outline-success">
              View
            </router-link>
            <router-link :to="`/party-types/form?id=${data.item.id}&mode=edit`" class="btn btn-outline-primary">
              Edit
            </router-link>
            <button @click="deletePartyType(data.item.id)" class="btn btn-outline-danger">Delete</button>
          </div>
        </td>
      </template>
    </b-table>

    <!-- paginación a la derecha -->
    <div class="d-flex justify-content-end mt-3">
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

const { proxy } = getCurrentInstance()

const partyTypes = ref([])
const search = ref('')
const perPage = ref(10)
const currentPage = ref(1)

const fields = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'name', label: 'Name', sortable: true, thClass: 'text-start', tdClass: 'text-start'},
  { key: 'description', label: 'Description', sortable: true, thClass: 'text-start', tdClass: 'text-start'},
  { key: 'is_active', label: 'Status', thClass: 'text-start', tdClass: 'text-start', sortable: true },
  { key: 'actions', label: 'Actions', thClass: 'text-center', tdClass: 'text-center'},
]

const fetchPartyTypes = async () => {
  try {
    const res = await axios.get('/api/party-types/')
    partyTypes.value = res.data
  } catch (err) {
    console.error('Error fetching party types', err)
    proxy?.notifyError?.('Error loading party types.')
  }
}

onMounted(fetchPartyTypes)

const filteredItems = computed(() => {
  if (!search.value) return partyTypes.value
  const q = search.value.toLowerCase()
  return partyTypes.value.filter(item =>
    `${item.name} ${item.description || ''}`.toLowerCase().includes(q)
  )
})

const deletePartyType = id => {
  proxy?.confirmDelete?.(
    'Are you sure?',
    'This action cannot be undone.',
    async () => {
      try {
        await axios.delete(`/api/party-types/${id}/`)
        partyTypes.value = partyTypes.value.filter(p => p.id !== id)
        proxy?.notifyToastSuccess?.('The party type has been deleted.')
      } catch (err) {
        console.error('Error deleting party type', err)
        proxy?.notifyError?.('Error deleting the party type.')
      }
    }
  )
}
</script>

<style scoped>
</style>
