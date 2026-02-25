<template>
  <TxCard class="shadow-sm mt-0">
    <template #header>
      <div
        class="d-flex flex-wrap justify-content-between align-items-center w-100 gap-2">
        <h5 class="text-primary mb-0 fw-semibold listview-title">
          Product Brands
        </h5>
        <div>
          <button
            v-if="hasPermission('appinventory.add_productbrand')"
            class="btn btn-success btn-sm"
            @click="goToCreateForm">
            + New Brand
          </button>
        </div>
      </div>
    </template>

    <div class="card-body">
      <div
        class="listview-toolbar d-flex flex-wrap align-items-center gap-2 mb-3">
        <span class="badge bg-primary stats-badge">
          {{ stats.total }} Total
        </span>
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
          @click="refreshList">
          Refresh List
        </button>
      </div>

      <div class="listview-filters row g-2 g-md-3 mb-3 align-items-end">
        <div class="col-12 col-sm-6 col-lg-4 col-xl-3">
          <div class="listview-filter-group">
            <label for="brand-per-page" class="form-label small mb-1">
              Entries per page:
            </label>
            <select
              id="brand-per-page"
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
            <label for="brand-search" class="form-label small mb-1">
              Search:
            </label>
            <div class="search-wrapper">
              <input
                id="brand-search"
                v-model="search"
                type="search"
                class="form-control form-control-sm"
                placeholder="Search by name..."
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

      <BOverlay :show="loading" rounded="sm" opacity="0.85" variant="light">
        <template #overlay>
          <div class="text-center">
            <BSpinner type="border" variant="secondary" class="mb-3" />
            <div class="h5 text-primary">Loading Brands...</div>
            <div class="text-muted">Please wait while we fetch the data</div>
          </div>
        </template>

        <b-table
          :items="filteredItems"
          :fields="fields"
          :per-page="perPage"
          :current-page="currentPage"
          bordered
          hover
          responsive
          striped>
          <template #cell(is_active)="data">
            <td class="text-center">
              <span v-if="data.item.is_active" class="badge bg-success">
                Active
              </span>
              <span v-else class="badge bg-secondary">Inactive</span>
            </td>
          </template>

          <template #cell(is_default)="data">
            <td class="text-center">
              <span v-if="data.item.is_default" class="badge bg-primary">
                Default
              </span>
              <span v-else class="badge bg-light text-dark">—</span>
            </td>
          </template>

          <template #cell(actions)="data">
            <td class="text-center">
              <div class="btn-group btn-group-sm" role="group">
                <button
                  v-if="hasPermission('appinventory.view_productbrand')"
                  class="btn btn-outline-success me-1"
                  @click="viewItem(data.item.id)">
                  View
                </button>
                <button
                  v-if="hasPermission('appinventory.change_productbrand')"
                  class="btn btn-outline-primary me-1"
                  @click="editItem(data.item.id)">
                  Edit
                </button>
                <button
                  v-if="hasPermission('appinventory.delete_productbrand')"
                  class="btn btn-outline-danger"
                  @click="confirmDelete(data.item.id)"
                  :disabled="deletingId === data.item.id">
                  <span
                    v-if="deletingId === data.item.id"
                    class="spinner-border spinner-border-sm me-1"
                    role="status"
                    aria-hidden="true"></span>
                  Delete
                </button>
              </div>
            </td>
          </template>
        </b-table>
      </BOverlay>

      <div
        v-if="!loading && filteredItems.length === 0"
        class="text-muted text-center py-5">
        <h5>No brands found</h5>
        <p class="mb-0">
          {{
            search
              ? "Try a different search term."
              : "Start by creating your first product brand."
          }}
        </p>
      </div>

      <div
        v-if="!loading && filteredItems.length > 0"
        class="d-flex justify-content-end mt-3">
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
import { BOverlay, BSpinner } from "bootstrap-vue-next";
import "@/assets/css/base.css";

import { ref, computed, onMounted, getCurrentInstance } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const { proxy } = getCurrentInstance();
const router = useRouter();

const brands = ref([]);
const search = ref("");
const perPage = ref(25);
const currentPage = ref(1);
const loading = ref(false);
const deletingId = ref(null);

const fields = [
  {
    key: "id",
    label: "ID",
    sortable: true,
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "name",
    label: "Name",
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
    key: "is_default",
    label: "Default",
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

const fetchItems = async () => {
  loading.value = true;
  try {
    const response = await axios.get("/api/productbrand/");
    brands.value = response.data;
  } catch (error) {
    console.error("Error loading brands:", error);
    proxy?.notifyError?.("Error loading product brands.");
  } finally {
    loading.value = false;
  }
};

const refreshList = () => {
  loading.value = true;
  fetchItems();
};

onMounted(fetchItems);

const filteredItems = computed(() => {
  if (!search.value) return brands.value;
  const q = search.value.toLowerCase();
  return brands.value.filter((item) => item.name.toLowerCase().includes(q));
});

const stats = computed(() => {
  const list = filteredItems.value;
  const active = list.filter((i) => i.is_active).length;
  return { total: list.length, active, inactive: list.length - active };
});

const goToCreateForm = () => {
  router.push({ name: "product-brand-form" });
};

const viewItem = (id) => {
  router.push({ name: "product-brand-view", params: { id } });
};

const editItem = (id) => {
  router.push({ name: "product-brand-edit", params: { id } });
};

const confirmDelete = (id) => {
  proxy?.confirmDelete?.(
    "Delete?",
    "This will delete the product brand. This action cannot be undone.",
    async () => {
      await deleteItem(id);
    }
  );
};

const deleteItem = async (id) => {
  deletingId.value = id;
  try {
    await axios.delete(`/api/productbrand/${id}/`);
    brands.value = brands.value.filter((b) => b.id !== id);
    proxy?.notifyToastSuccess?.("The product brand has been deleted.");
  } catch (error) {
    console.error("Error deleting product brand:", error);
    proxy?.notifyError?.("Error deleting the product brand.");
  } finally {
    deletingId.value = null;
  }
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
