<template>
  <TxCard class="shadow-sm mt-0">
    <!-- Header del card -->
    <template #header>
      <div
        class="d-flex flex-wrap justify-content-between align-items-center w-100 gap-2">
        <h5 class="text-primary mb-0 fw-semibold listview-title">
          Work Accounts
        </h5>
        <router-link
          v-if="hasPermission('apptransactions.add_workaccount')"
          to="/work-accounts/form"
          class="btn btn-success btn-sm">
          + New Work Account
        </router-link>
      </div>
    </template>

    <!-- Toolbar: stats + refresh -->
    <div
      class="listview-toolbar d-flex flex-wrap align-items-center gap-2 mb-3">
      <span class="badge bg-primary stats-badge">{{ stats.total }} Total</span>
      <span class="badge bg-success stats-badge">
        {{ stats.active }} Active
      </span>
      <span class="badge bg-secondary stats-badge">
        {{ stats.inactive }} Inactive
      </span>
      <span
        class="listview-toolbar-divider d-none d-sm-inline"
        aria-hidden="true"></span>
      <button
        type="button"
        class="btn btn-outline-success btn-sm listview-refresh-btn"
        @click.prevent="refreshList">
        Refresh List
      </button>
    </div>

    <!-- Filters: entries per page + search -->
    <div class="listview-filters row g-2 g-md-3 mb-3 align-items-end">
      <div class="col-12 col-sm-6 col-lg-4 col-xl-3">
        <label for="per-page-select" class="form-label small listview-filter-label mb-1">
          Entries per page:
        </label>
        <select
          id="per-page-select"
          v-model="perPage"
          class="form-select form-select-sm">
          <option v-for="n in [10, 25, 50, 100]" :key="n" :value="n">
            {{ n }}
          </option>
        </select>
      </div>
      <div class="col-12 col-sm-6 col-lg-5 col-xl-4 ms-lg-auto">
        <label for="search-input" class="form-label small listview-filter-label mb-1">
          Search:
        </label>
        <div class="search-wrapper position-relative">
          <input
            id="search-input"
            v-model="search"
            type="text"
            class="form-control form-control-sm"
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

    <!-- Main Table with Overlay -->
    <BOverlay :show="isLoading" rounded="sm" opacity="0.85" variant="light">
      <template #overlay>
        <div class="text-center">
          <BSpinner type="border" variant="secondary" class="mb-3" />
          <div class="h5 text-primary">Loading Work Accounts...</div>
          <div class="text-muted">Please wait while we fetch the data</div>
        </div>
      </template>

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
            <div v-if="data.item.builder_name">
              {{ data.item.builder_name }}
            </div>
            <div v-if="data.item.job_name">{{ data.item.job_name }}</div>
            <div v-if="data.item.house_model_name">
              {{ data.item.house_model_name }}
            </div>
            <div v-if="data.item.lot || data.item.address">
              <span v-if="data.item.lot">Lot {{ data.item.lot }}</span>
              <span v-if="data.item.lot && data.item.address">/</span>
              <span v-if="data.item.address">{{ data.item.address }}</span>
            </div>
          </div>
        </template>

        <template #cell(is_active)="data">
          <td class="text-center">
            <span v-if="data.item.is_active" class="badge bg-success">
              Active
            </span>
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
              <router-link
                v-if="hasPermission('apptransactions.view_workaccount')"
                :to="`/work-accounts/form?id=${data.item.id}&mode=view`"
                class="btn btn-outline-success me-1">
                View
              </router-link>
              <router-link
                v-if="hasPermission('apptransactions.change_workaccount')"
                :to="`/work-accounts/form?id=${data.item.id}`"
                class="btn btn-outline-primary me-1">
                Edit
              </router-link>
              <button
                v-if="hasPermission('apptransactions.delete_workaccount')"
                @click="deleteWorkAccount(data.item.id, data.item.title)"
                class="btn btn-outline-danger">
                Delete
              </button>
            </div>
          </td>
        </template>
      </b-table>

      <!-- paginación a la derecha -->
      <div class="d-flex justify-content-end mt-3">
        <b-pagination
          v-model="currentPage"
          :total-rows="filteredItems.length"
          :per-page="perPage" />
      </div>
    </BOverlay>
  </TxCard>
</template>

<script setup>
import TxCard from "@/components/layout/TxCard.vue";
import "@/assets/css/base.css";

import { ref, computed, onMounted, getCurrentInstance } from "vue";
import axios from "axios";
import { BOverlay, BSpinner } from "bootstrap-vue-next";

const { proxy } = getCurrentInstance();

const workAccounts = ref([]);
const isLoading = ref(false);
const search = ref("");
const perPage = ref(25);
const currentPage = ref(1);

const fields = [
  {
    key: "id",
    label: "ID",
    sortable: true,
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "title",
    label: "Title",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "lot",
    label: "Lot",
    sortable: true,
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "address",
    label: "Address",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "city",
    label: "City",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "builder_name",
    label: "Builder",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "job_name",
    label: "Job",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "house_model_name",
    label: "Model",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "is_active",
    label: "Status",
    thClass: "text-center",
    tdClass: "text-center",
    sortable: true,
  },
  {
    key: "created_at",
    label: "Created",
    thClass: "text-center",
    tdClass: "text-center",
    sortable: true,
  },
  {
    key: "actions",
    label: "Actions",
    thClass: "text-center",
    tdClass: "text-center",
    thStyle: { width: "12%", whiteSpace: "nowrap" },
    tdStyle: { whiteSpace: "nowrap" },
  },
];

// Helpers para DRF con o sin paginación
const normalizeList = (data) =>
  Array.isArray(data) ? data : data?.results ?? [];

const formatDate = (dateString) => {
  if (!dateString) return "—";
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "—";
  }
};

const fetchWorkAccounts = async () => {
  try {
    const res = await axios.get("/api/work-accounts/?ordering=-created_at");
    workAccounts.value = normalizeList(res.data);
  } catch (err) {
    console.error("Error fetching work accounts", err);
    proxy?.notifyError?.("Error loading work accounts.");
  }
};

onMounted(async () => {
  await fetchWorkAccounts();
});

const filteredItems = computed(() => {
  if (!search.value) return workAccounts.value;
  const q = search.value.toLowerCase();
  return workAccounts.value.filter((item) => {
    const hay = [
      item.title,
      item.builder_name,
      item.job_name,
      item.house_model_name,
      item.lot,
      item.address,
      item.city,
      item.zipcode,
    ].map((v) => (v || "").toString().toLowerCase());
    return hay.some((t) => t.includes(q));
  });
});

const stats = computed(() => {
  const items = filteredItems.value;
  return {
    total: items.length,
    active: items.filter((i) => i.is_active).length,
    inactive: items.filter((i) => !i.is_active).length,
  };
});

const refreshList = async () => {
  isLoading.value = true;
  try {
    await fetchWorkAccounts();
  } finally {
    setTimeout(() => {
      isLoading.value = false;
    }, 300);
  }
};

const deleteWorkAccount = (id, title) => {
  proxy?.confirmDelete?.(
    "Are you sure?",
    `Delete "${title}"? This action cannot be undone.`,
    async () => {
      try {
        await axios.delete(`/api/work-accounts/${id}/`);
        workAccounts.value = workAccounts.value.filter((wa) => wa.id !== id);
        proxy?.notifyToastSuccess?.("The work account has been deleted.");
      } catch (err) {
        console.error("Error deleting work account", err);
        // Manejo de tu custom_exception_handler (409 in use)
        const detail =
          err?.response?.data?.detail || "Error deleting the work account.";
        proxy?.notifyError?.(detail);
      }
    }
  );
};
</script>

<style scoped>
.listview-title {
  font-size: 1.1rem;
  letter-spacing: -0.01em;
}
.listview-toolbar {
  padding: 0.5rem 0.75rem;
  background-color: rgba(13, 110, 253, 0.06);
  border: 1px solid rgba(13, 110, 253, 0.12);
  border-radius: 0.375rem;
}
.listview-toolbar .stats-badge {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  line-height: 1.2;
}
.listview-toolbar-divider {
  width: 1px;
  height: 1.25rem;
  background-color: rgba(0, 0, 0, 0.12);
  margin: 0 0.15rem;
}
.listview-refresh-btn {
  padding: 0.2rem 0.6rem;
  font-size: 0.8rem;
}
.listview-filter-label {
  font-size: 0.8rem;
  color: var(--bs-secondary-color);
}
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
