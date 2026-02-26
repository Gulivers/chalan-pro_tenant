<template>
  <TxCard class="shadow-sm mt-0">
    <template #header>
      <div
        class="d-flex flex-wrap justify-content-between align-items-center w-100 gap-2">
        <h5 class="text-primary mb-0 fw-semibold listview-title">
          Truck Assignments
        </h5>
        <router-link
          v-if="hasPermission('crewsapp.add_truckassignment')"
          to="/crews/truck-assignments/form"
          class="btn btn-success btn-sm">
          + New Truck Assignment
        </router-link>
      </div>
    </template>

    <div class="card-body">
      <div
        class="listview-toolbar d-flex flex-wrap align-items-center gap-2 mb-3">
        <span class="badge bg-primary stats-badge">
          {{ itemsWithFormattedTrucks.length }} Total
        </span>
        <span
          class="listview-toolbar-divider d-none d-sm-inline"
          aria-hidden="true"></span>
        <button
          type="button"
          class="btn btn-outline-success btn-sm listview-refresh-btn"
          @click="fetchItems">
          Refresh List
        </button>
      </div>

      <div class="listview-filters row g-2 g-md-3 mb-3 align-items-end">
        <div class="col-12 col-sm-6 col-lg-4 col-xl-3">
          <div class="listview-filter-group">
            <label for="ta-per-page" class="form-label small mb-1">
              Entries per page:
            </label>
            <select
              id="ta-per-page"
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
            <label for="ta-search" class="form-label small mb-1">Search:</label>
            <div class="search-wrapper">
              <input
                id="ta-search"
                v-model="search"
                type="search"
                class="form-control form-control-sm"
                placeholder="Search by crew or truck"
                autocomplete="off" />
              <button
                v-show="search && search.length"
                @mousedown.prevent
                @click="search = ''"
                type="button"
                class="btn-clear-x"
                title="Clear">
                x
              </button>
            </div>
          </div>
        </div>
      </div>

      <b-table
        :items="itemsWithFormattedTrucks"
        :fields="fields"
        :per-page="perPage"
        :current-page="currentPage"
        bordered
        hover
        responsive
        striped>
        <template #cell(assigned_at)="data">
          <td>{{ formatDate(data.item.assigned_at) }}</td>
        </template>
        <template #cell(unassigned_at)="data">
          <td>
            {{
              data.item.unassigned_at
                ? formatDate(data.item.unassigned_at)
                : "—"
            }}
          </td>
        </template>
        <template #cell(actions)="data">
          <td class="text-center">
            <div class="btn-group btn-group-sm" role="group">
              <router-link
                v-if="hasPermission('crewsapp.view_truckassignment')"
                :to="`/crews/truck-assignments/view/${data.item.id}`"
                class="btn btn-outline-success me-1">
                View
              </router-link>
              <router-link
                v-if="hasPermission('crewsapp.change_truckassignment')"
                :to="`/crews/truck-assignments/edit/${data.item.id}`"
                class="btn btn-outline-primary me-1">
                Edit
              </router-link>
              <button
                v-if="hasPermission('crewsapp.delete_truckassignment')"
                @click="deleteItem(data.item.id)"
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
          :total-rows="itemsWithFormattedTrucks.length"
          :per-page="perPage" />
      </div>
    </div>
  </TxCard>
</template>

<script setup>
import TxCard from "@/components/layout/TxCard.vue";
import { ref, computed, onMounted, getCurrentInstance } from "vue";
import axios from "axios";
import "@/assets/css/base.css";

const { proxy } = getCurrentInstance();
const items = ref([]);
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
    key: "crew_name",
    label: "Assigned Crew",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "trucks_display",
    label: "Assigned Trucks",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "assigned_at",
    label: "Assigned At",
    sortable: true,
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "unassigned_at",
    label: "Unassigned At",
    thClass: "text-center",
    tdClass: "text-center",
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

function formatDate(val) {
  if (!val) return "—";
  const d = new Date(val);
  return isNaN(d.getTime()) ? val : d.toLocaleString();
}

const fetchItems = async () => {
  try {
    const res = await axios.get("/api/truck-assignments/");
    items.value = res.data.results ?? res.data;
  } catch (err) {
    console.error("Error fetching truck assignments", err);
    proxy?.notifyError?.("Error loading truck assignments.");
  }
};

onMounted(fetchItems);

const itemsWithFormattedTrucks = computed(() => {
  const list = !search.value
    ? items.value
    : items.value.filter((item) => {
        const q = search.value.toLowerCase();
        const trucksStr = Array.isArray(item.trucks_display)
          ? item.trucks_display.join(" ").toLowerCase()
          : (item.trucks_display || "").toLowerCase();
        return (
          (item.crew_name || "").toLowerCase().includes(q) ||
          trucksStr.includes(q)
        );
      });
  const formatted = list.map((item) => ({
    ...item,
    trucks_display: Array.isArray(item.trucks_display)
      ? item.trucks_display.join(", ")
      : item.trucks_display || "—",
  }));
  return [...formatted].sort((a, b) => {
    const crewA = (a.crew_name || "").toLowerCase();
    const crewB = (b.crew_name || "").toLowerCase();
    if (crewA !== crewB) return crewA.localeCompare(crewB);
    const dateA = new Date(a.assigned_at || 0).getTime();
    const dateB = new Date(b.assigned_at || 0).getTime();
    return dateB - dateA;
  });
});

const deleteItem = (id) => {
  proxy.confirmDelete(
    "Are you sure?",
    "This action cannot be undone.",
    async () => {
      try {
        await axios.delete(`/api/truck-assignments/${id}/`);
        items.value = items.value.filter((item) => item.id !== id);
        proxy?.notifyToastSuccess?.("Truck assignment has been deleted.");
      } catch (err) {
        console.error("Error deleting truck assignment", err);
        proxy?.notifyError?.("Error deleting truck assignment.");
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
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  cursor: pointer;
  color: #666;
}
</style>
