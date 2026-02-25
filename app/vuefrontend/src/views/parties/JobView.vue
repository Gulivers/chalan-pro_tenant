<template>
  <TxCard class="shadow-sm mt-0">
    <template #header>
      <div
        class="d-flex flex-wrap justify-content-between align-items-center w-100 gap-2">
        <h5 class="text-primary mb-0 fw-semibold listview-title">
          Jobs (Communities)
        </h5>
        <router-link
          v-if="hasPermission('ctrctsapp.add_job')"
          to="/job/form"
          class="btn btn-success btn-sm">
          + New Job
        </router-link>
      </div>
    </template>

    <div class="card-body">
      <div
        class="listview-toolbar d-flex flex-wrap align-items-center gap-2 mb-3">
        <span class="badge bg-primary stats-badge">
          {{ filteredItems.length }} Total
        </span>
        <span
          class="listview-toolbar-divider d-none d-sm-inline"
          aria-hidden="true"></span>
        <button
          type="button"
          class="btn btn-outline-success btn-sm listview-refresh-btn"
          @click="fetchJobs">
          Refresh List
        </button>
      </div>

      <div class="listview-filters row g-2 g-md-3 mb-3 align-items-end">
        <div class="col-12 col-sm-6 col-lg-4 col-xl-3">
          <div class="listview-filter-group">
            <label for="job-per-page" class="form-label small mb-1">
              Entries per page:
            </label>
            <select
              id="job-per-page"
              v-model="perPage"
              class="form-select form-select-sm">
              <option v-for="n in [5, 10, 25, 50]" :key="n" :value="n">
                {{ n }}
              </option>
            </select>
          </div>
        </div>
        <div class="col-12 col-sm-6 col-lg-5 col-xl-4 ms-lg-auto">
          <div class="listview-filter-group">
            <label for="job-search" class="form-label small mb-1">
              Search:
            </label>
            <div class="search-wrapper">
              <input
                id="job-search"
                v-model="search"
                type="search"
                class="form-control form-control-sm"
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
        striped>
        <template #cell(builder)="data">
          {{ data.item.builder?.name || "—" }}
        </template>

        <template #cell(actions)="data">
          <td class="text-center">
            <div class="btn-group btn-group-sm" role="group">
              <router-link
                v-if="hasPermission('ctrctsapp.view_job')"
                :to="`/job/view/${data.item.id}`"
                class="btn btn-outline-success me-1">
                View
              </router-link>
              <router-link
                v-if="hasPermission('ctrctsapp.change_job')"
                :to="`/job/edit/${data.item.id}`"
                class="btn btn-outline-primary me-1">
                Edit
              </router-link>
              <button
                v-if="hasPermission('ctrctsapp.delete_job')"
                @click="deleteJob(data.item.id, data.item.name)"
                class="btn btn-outline-danger">
                Delete
              </button>
            </div>
          </td>
        </template>
      </b-table>

      <div class="d-flex justify-content-end mt-3">
        <b-pagination
          v-model="currentPage"
          :total-rows="filteredItems.length"
          :per-page="perPage" />
      </div>
    </div>
  </TxCard>
</template>

<script setup>
import TxCard from "@/components/layout/TxCard.vue";
import "@/assets/css/base.css";

import { ref, computed, onMounted, getCurrentInstance } from "vue";
import axios from "axios";

const { proxy } = getCurrentInstance();

const jobs = ref([]);
const search = ref("");
const perPage = ref(25);
const currentPage = ref(1);

const fields = [
  { key: "id", label: "ID", sortable: true },
  { key: "name", label: "Job Name", sortable: true },
  { key: "builder", label: "Builder", sortable: true },
  { key: "address", label: "Address", sortable: true },
  { key: "latitude", label: "Latitude", sortable: true },
  { key: "longitude", label: "Longitude", sortable: true },
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
const fetchJobs = async () => {
  try {
    const res = await axios.get("/api/job/?ordering=name");
    jobs.value = normalizeList(res.data);
  } catch (err) {
    console.error("Error fetching jobs", err);
    proxy?.notifyError?.("Error loading jobs.");
  }
};

onMounted(async () => {
  await fetchJobs();
});

const filteredItems = computed(() => {
  if (!search.value) return jobs.value;
  const q = search.value.toLowerCase();
  return jobs.value.filter((item) => {
    const hay = [item.name, item.address, item.builder?.name].map((v) =>
      (v || "").toString().toLowerCase()
    );
    return hay.some((t) => t.includes(q));
  });
});

const deleteJob = (id, name) => {
  proxy?.confirmDelete?.(
    "Are you sure?",
    `Delete "${name}"? This action cannot be undone.`,
    async () => {
      try {
        await axios.delete(`/api/job/${id}/`);
        jobs.value = jobs.value.filter((p) => p.id !== id);
        proxy?.notifyToastSuccess?.("The job has been deleted.");
      } catch (err) {
        console.error("Error deleting job", err);
        // Manejo de tu custom_exception_handler (409 in use)
        const detail = err?.response?.data?.detail || "Error deleting the job.";
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
.listview-filters .listview-filter-group label {
  font-size: 0.8rem;
  color: var(--bs-secondary-color);
}
.form-select-sm,
.form-control-sm {
  font-size: 0.8rem;
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
