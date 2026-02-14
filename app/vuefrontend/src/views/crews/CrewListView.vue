<template>
  <TxCard class="shadow-sm mt-0">
    <template #header>
      <div class="d-flex justify-content-between align-items-center w-100">
        <h6 class="text-primary mb-0">Crews</h6>
        <router-link
          v-if="hasPermission('crewsapp.add_crew')"
          to="/crews/form"
          class="btn btn-success"
          >+ New Crew</router-link
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
              placeholder="Search by name or category"
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
      :items="filteredItems"
      :fields="fields"
      :per-page="perPage"
      :current-page="currentPage"
      bordered
      hover
      responsive
      striped
    >
      <template #cell(status)="data">
        <td class="text-center">
          <span v-if="data.item.status" class="badge bg-success">Active</span>
          <span v-else class="badge bg-secondary">Inactive</span>
        </td>
      </template>
      <template #cell(permission_create_event)="data">
        <td class="text-center">
          <span
            :class="
              data.item.permission_create_event
                ? 'badge bg-success'
                : 'badge bg-secondary'
            "
          >
            {{ data.item.permission_create_event ? "Yes" : "No" }}
          </span>
        </td>
      </template>
      <template #cell(actions)="data">
        <td class="text-center">
          <div class="btn-group btn-group-sm" role="group">
            <router-link
              v-if="hasPermission('crewsapp.view_crew')"
              :to="`/crews/view/${data.item.id}`"
              class="btn btn-outline-success me-1"
              >View</router-link
            >
            <router-link
              v-if="hasPermission('crewsapp.change_crew')"
              :to="`/crews/edit/${data.item.id}`"
              class="btn btn-outline-primary me-1"
              >Edit</router-link
            >
            <button
              v-if="hasPermission('crewsapp.delete_crew')"
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
        :total-rows="filteredItems.length"
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
  { key: "name", label: "Crew Name", sortable: true, thClass: "text-start", tdClass: "text-start" },
  { key: "category_name", label: "Category", sortable: true, thClass: "text-start", tdClass: "text-start" },
  {
    key: "status",
    label: "Status",
    thClass: "text-center",
    tdClass: "text-center",
    thStyle: { width: "5%", whiteSpace: "nowrap" },
    tdStyle: { whiteSpace: "nowrap" },
  },
  {
    key: "permission_create_event",
    label: "Can Create/Update Schedule?",
    thClass: "text-center",
    tdClass: "text-center",
    thStyle: { width: "12%", whiteSpace: "nowrap" },
    tdStyle: { whiteSpace: "nowrap" },
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

const fetchItems = async () => {
  try {
    const res = await axios.get("/api/crews/");
    items.value = res.data.results ?? res.data;
  } catch (err) {
    console.error("Error fetching crews", err);
    proxy?.notifyError?.("Error loading crews.");
  }
};

onMounted(fetchItems);

const filteredItems = computed(() => {
  if (!search.value) return items.value;
  const q = search.value.toLowerCase();
  return items.value.filter(
    (item) =>
      (item.name || "").toLowerCase().includes(q) ||
      (item.category_name || "").toLowerCase().includes(q),
  );
});

const deleteItem = (id) => {
  proxy.confirmDelete(
    "Are you sure?",
    "This action cannot be undone.",
    async () => {
      try {
        await axios.delete(`/api/crews/${id}/`);
        items.value = items.value.filter((item) => item.id !== id);
        proxy?.notifyToastSuccess?.("Crew has been deleted.");
      } catch (err) {
        console.error("Error deleting crew", err);
        proxy?.notifyError?.("Error deleting crew.");
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
