<template>
  <TxCard class="shadow-sm mt-0">
    <!-- Header del card -->
    <template #header>
      <div class="d-flex justify-content-between align-items-center w-100">
        <h6 class="text-primary mb-0">Work Accounts</h6>
        <router-link to="/work-accounts/form" class="btn btn-success">+ New Work Account</router-link>
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
              placeholder="Search by title, builder, job, lot, address..."
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
      striped>
      <template #cell(context)="data">
        <div class="small text-muted">
          <div v-if="data.item.builder_name">{{ data.item.builder_name }}</div>
          <div v-if="data.item.job_name">{{ data.item.job_name }}</div>
          <div v-if="data.item.house_model_name">{{ data.item.house_model_name }}</div>
          <div v-if="data.item.lot || data.item.address">
            <span v-if="data.item.lot">Lot {{ data.item.lot }}</span>
            <span v-if="data.item.lot && data.item.address">/</span>
            <span v-if="data.item.address">{{ data.item.address }}</span>
          </div>
        </div>
      </template>

      <template #cell(is_active)="data">
        <td class="text-center">
          <span v-if="data.item.is_active" class="badge bg-success">Active</span>
          <span v-else class="badge bg-secondary">Inactive</span>
        </td>
      </template>

      <template #cell(created_at)="data">
        <td class="text-center">
          {{ formatDate(data.item.created_at) }}
        </td>
      </template>

      <template #cell(actions)="data">
        <td class="text-center">
          <div class="btn-group btn-group-sm" role="group">
            <router-link :to="`/work-accounts/form?id=${data.item.id}&mode=view`" class="btn btn-outline-success me-1">
              View
            </router-link>
            <router-link :to="`/work-accounts/form?id=${data.item.id}`" class="btn btn-outline-primary me-1">
              Edit
            </router-link>
            <button @click="deleteWorkAccount(data.item.id, data.item.title)" class="btn btn-outline-danger">
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
  import TxCard from '@/components/layout/TxCard.vue';
  import '@/assets/css/base.css';

  import { ref, computed, onMounted, getCurrentInstance } from 'vue';
  import axios from 'axios';

  const { proxy } = getCurrentInstance();

  const workAccounts = ref([]);
  const search = ref('');
  const perPage = ref(10);
  const currentPage = ref(1);

  const fields = [
    { key: 'id', label: 'ID', sortable: true, thClass: 'text-center', tdClass: 'text-center' },
    { key: 'title', label: 'Title', sortable: true },
    { key: 'lot', label: 'Lot', sortable: true },
    { key: 'address', label: 'Address', sortable: true },
    { key: 'city', label: 'City', sortable: true },
    { key: 'builder_name', label: 'Builder', sortable: true },
    { key: 'job_name', label: 'Job', sortable: true },
    { key: 'house_model_name', label: 'Model', sortable: true },
    { key: 'is_active', label: 'Status', thClass: 'text-center', tdClass: 'text-center', sortable: true },
    { key: 'created_at', label: 'Created', thClass: 'text-center', tdClass: 'text-center', sortable: true },
    { key: 'actions', label: 'Actions', thClass: 'text-center', tdClass: 'text-center' },

  ];

  // Helpers para DRF con o sin paginación
  const normalizeList = data => (Array.isArray(data) ? data : data?.results ?? []);

  const formatDate = dateString => {
    if (!dateString) return '—';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return '—';
    }
  };

  const fetchWorkAccounts = async () => {
    try {
      const res = await axios.get('/api/work-accounts/?ordering=-created_at');
      workAccounts.value = normalizeList(res.data);
    } catch (err) {
      console.error('Error fetching work accounts', err);
      proxy?.notifyError?.('Error loading work accounts.');
    }
  };

  onMounted(async () => {
    await fetchWorkAccounts();
  });

  const filteredItems = computed(() => {
    if (!search.value) return workAccounts.value;
    const q = search.value.toLowerCase();
    return workAccounts.value.filter(item => {
      const hay = [
        item.title,
        item.builder_name,
        item.job_name,
        item.house_model_name,
        item.lot,
        item.address,
        item.city,
        item.zipcode,
      ].map(v => (v || '').toString().toLowerCase());
      return hay.some(t => t.includes(q));
    });
  });

  const deleteWorkAccount = (id, title) => {
    proxy?.confirmDelete?.('Are you sure?', `Delete "${title}"? This action cannot be undone.`, async () => {
      try {
        await axios.delete(`/api/work-accounts/${id}/`);
        workAccounts.value = workAccounts.value.filter(wa => wa.id !== id);
        proxy?.notifyToastSuccess?.('The work account has been deleted.');
      } catch (err) {
        console.error('Error deleting work account', err);
        // Manejo de tu custom_exception_handler (409 in use)
        const detail = err?.response?.data?.detail || 'Error deleting the work account.';
        proxy?.notifyError?.(detail);
      }
    });
  };
</script>

<style scoped>
  /* Reusa estilos de PartyCategoryList: clear de input */
  .search-wrapper {
    position: relative;
  }
  .btn-clear-x {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    border: none;
    background: transparent;
    font-size: 1.25rem;
    line-height: 1;
  }
</style>
