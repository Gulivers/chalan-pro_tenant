<template>
  <TxCard class="shadow-sm mt-0">
    <template #header>
      <div class="d-flex justify-content-between align-items-center w-100">
        <h6 class="text-primary mb-0">Crew Categories</h6>
        <router-link
          v-if="hasPermission('crewsapp.add_category')"
          to="/crews/categories/form"
          class="btn btn-success"
          >+ New Category</router-link
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
              placeholder="Search by name"
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
      <template #cell(actions)="data">
        <td class="text-center">
          <div class="btn-group btn-group-sm" role="group">
            <router-link
              v-if="hasPermission('crewsapp.view_category')"
              :to="`/crews/categories/view/${data.item.id}`"
              class="btn btn-outline-success me-1"
              >View</router-link
            >
            <router-link
              v-if="hasPermission('crewsapp.change_category')"
              :to="`/crews/categories/edit/${data.item.id}`"
              class="btn btn-outline-primary me-1"
              >Edit</router-link
            >
            <button
              v-if="hasPermission('crewsapp.delete_category')"
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
  {
    key: "id",
    label: "ID",
    sortable: true,
    thStyle: { width: "4rem" },
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "name",
    label: "Name",
    sortable: true,
    thStyle: { minWidth: "200px", width: "60%" },
    thClass: "text-start",
    tdClass: "text-start",
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
    const res = await axios.get("/api/categories/");
    items.value = res.data.results ?? res.data;
  } catch (err) {
    console.error("Error fetching categories", err);
    proxy?.notifyError?.("Error loading categories.");
  }
};

onMounted(fetchItems);

const filteredItems = computed(() => {
  if (!search.value) return items.value;
  return items.value.filter((item) =>
    (item.name || "").toLowerCase().includes(search.value.toLowerCase()),
  );
});

const deleteItem = (id) => {
  proxy.confirmDelete(
    "Are you sure?",
    "This action cannot be undone.",
    async () => {
      try {
        await axios.delete(`/api/categories/${id}/`);
        items.value = items.value.filter((item) => item.id !== id);
        proxy?.notifyToastSuccess?.("Category has been deleted.");
      } catch (err) {
        console.error("Error deleting category", err);
        proxy?.notifyError?.("Error deleting category.");
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
