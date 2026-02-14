<template>
  <TxCard class="shadow-sm mt-0">
    <template #header>
      <div class="d-flex justify-content-between align-items-center w-100">
        <h6 class="text-primary mb-0">Truck Assignments</h6>
        <router-link
          v-if="hasPermission('crewsapp.add_truckassignment')"
          to="/crews/truck-assignments/form"
          class="btn btn-success"
          >+ New Truck Assignment</router-link
        >
      </div>
    </template>

    <div class="d-flex justify-content-between align-items-center mb-3">
      <div class="col-md-3">
        <div class="input-group">
          <select v-model="perPage" class="form-select">
            <option v-for="n in [5, 10, 25, 50]" :key="n" :value="n">
              {{ n }}
            </option>
          </select>
          <span class="text-primary p-2">entries per page</span>
        </div>
      </div>
      <div class="col-md-4">
        <div class="d-flex align-items-center gap-2">
          <span class="text-primary p-2">Search:</span>
          <div class="search-wrapper flex-grow-1">
            <input
              v-model="search"
              type="text"
              class="form-control"
              placeholder="Search by crew or truck"
              autocomplete="off"
            />
            <button
              v-show="search && search.length"
              @mousedown.prevent
              @click="search = ''"
              type="button"
              class="btn-clear-x"
              title="Clear"
            >
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
      striped
    >
      <template #cell(assigned_at)="data">
        <td>{{ formatDate(data.item.assigned_at) }}</td>
      </template>
      <template #cell(unassigned_at)="data">
        <td>
          {{
            data.item.unassigned_at ? formatDate(data.item.unassigned_at) : "—"
          }}
        </td>
      </template>
      <template #cell(actions)="data">
        <td class="text-center">
          <div class="btn-group btn-group-sm" role="group">
            <router-link
              v-if="hasPermission('crewsapp.view_truckassignment')"
              :to="`/crews/truck-assignments/view/${data.item.id}`"
              class="btn btn-outline-success me-1"
              >View</router-link
            >
            <router-link
              v-if="hasPermission('crewsapp.change_truckassignment')"
              :to="`/crews/truck-assignments/edit/${data.item.id}`"
              class="btn btn-outline-primary me-1"
              >Edit</router-link
            >
            <button
              v-if="hasPermission('crewsapp.delete_truckassignment')"
              @click="deleteItem(data.item.id)"
              class="btn btn-outline-danger"
            >
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
        :per-page="perPage"
      />
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
const perPage = ref(10);
const currentPage = ref(1);

const fields = [
  { key: "id", label: "ID", sortable: true, thClass: "text-center", tdClass: "text-center" },
  { key: "crew_name", label: "Assigned Crew", sortable: true, thClass: "text-start", tdClass: "text-start" },
  { key: "trucks_display", label: "Assigned Trucks", sortable: true, thClass: "text-start", tdClass: "text-start" },
  { key: "assigned_at", label: "Assigned At", sortable: true, thClass: "text-center", tdClass: "text-center" },
  { key: "unassigned_at", label: "Unassigned At", thClass: "text-center", tdClass: "text-center" },
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
          (item.crew_name || "").toLowerCase().includes(q) || trucksStr.includes(q)
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
    },
  );
};
</script>

<style scoped>
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
