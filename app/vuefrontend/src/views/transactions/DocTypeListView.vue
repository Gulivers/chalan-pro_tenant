<template>
  <TxCard class="shadow-sm mt-0">
    <!-- Header del card -->
    <template #header>
      <div
        class="d-flex flex-wrap justify-content-between align-items-center gap-2 w-100">
        <h6 class="text-primary mb-0">Transaction Types</h6>
        <router-link
          v-if="hasPermission('apptransactions.add_documenttype')"
          to="/document-types/form"
          class="btn btn-success btn-sm">
          + New Transaction Type
        </router-link>
      </div>
    </template>

    <!-- Flujos administrativos: Sales y Purchase -->
    <div class="mb-4">
      <h6 class="text-primary mb-3">Administrative Process Flows</h6>
      <div class="row g-3">
        <div class="col-12 col-md-6">
          <div class="card border-primary h-100">
            <div class="card-header bg-primary text-white py-2 small">
              <strong>Sales Flow</strong>
            </div>
            <div
              class="card-body py-3 d-flex flex-column align-items-center justify-content-center">
              <div
                class="d-flex flex-wrap align-items-center justify-content-center gap-1 flow-sequence">
                <span
                  v-for="(node, i) in salesFlow"
                  :key="node.code"
                  class="d-inline-flex align-items-center">
                  <span class="badge bg-success flow-node" :title="node.desc">
                    {{ node.code }}
                  </span>
                  <span
                    v-if="i < salesFlow.length - 1"
                    class="flow-arrow text-muted">
                    →
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-12 col-md-6">
          <div class="card border-info h-100">
            <div class="card-header bg-info text-white py-2 small">
              <strong>Purchase Flow</strong>
            </div>
            <div
              class="card-body py-3 d-flex flex-column align-items-center justify-content-center">
              <div
                class="d-flex flex-wrap align-items-center justify-content-center gap-1 flow-sequence">
                <span
                  v-for="(node, i) in purchaseFlow"
                  :key="node.code"
                  class="d-inline-flex align-items-center">
                  <span class="badge bg-info flow-node" :title="node.desc">
                    {{ node.code }}
                  </span>
                  <span
                    v-if="i < purchaseFlow.length - 1"
                    class="flow-arrow text-muted">
                    →
                  </span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filtros arriba de la tabla -->
    <div class="row g-4 mb-3">
      <!-- Entries per page -->
      <div class="col-12 col-sm-6">
        <div class="d-flex align-items-center gap-2">
          <label for="doctype-per-page" class="form-label small mb-0 text-nowrap">Entries per page:</label>
          <select id="doctype-per-page" v-model="perPage" class="form-select form-select-sm">
            <option v-for="n in [5, 10, 25, 50]" :key="n" :value="n">
              {{ n }}
            </option>
          </select>
        </div>
      </div>

      <!-- Search -->
      <div class="col-12 col-sm-6">
        <div class="d-flex align-items-center gap-2">
          <label for="doctype-search" class="form-label small mb-0 text-nowrap">Search:</label>
          <div class="search-wrapper flex-grow-1">
            <input
              id="doctype-search"
              v-model="search"
              type="text"
              class="form-control form-control-sm"
              placeholder="Search by Title or Description"
              autocomplete="off" />
            <!-- Botón X flotante -->
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
      :items="filteredItems"
      :fields="fields"
      :per-page="perPage"
      :current-page="currentPage"
      bordered
      hover
      responsive
      striped>
      <!-- Affects Physical -->
      <template #cell(affects_physical)="data">
        <td class="sorting_1 text-center">
          <span
            :class="
              data.item.affects_physical
                ? 'badge bg-success'
                : 'badge bg-secondary'
            ">
            {{ data.item.affects_physical ? "Yes" : "No" }}
          </span>
        </td>
      </template>

      <!-- Affects Logical -->
      <template #cell(affects_logical)="data">
        <td class="sorting_1 text-center">
          <span
            :class="
              data.item.affects_logical
                ? 'badge bg-success'
                : 'badge bg-secondary'
            ">
            {{ data.item.affects_logical ? "Yes" : "No" }}
          </span>
        </td>
      </template>

      <!-- Is Purchase -->
      <template #cell(is_purchase)="data">
        <td class="sorting_1 text-center">
          <span
            :class="
              data.item.is_purchase ? 'badge bg-success' : 'badge bg-secondary'
            ">
            {{ data.item.is_purchase ? "Yes" : "No" }}
          </span>
        </td>
      </template>

      <!-- Is Sales -->
      <template #cell(is_sales)="data">
        <td class="sorting_1 text-center">
          <span
            :class="
              data.item.is_sales ? 'badge bg-success' : 'badge bg-secondary'
            ">
            {{ data.item.is_sales ? "Yes" : "No" }}
          </span>
        </td>
      </template>

      <!-- Is Operational -->
      <template #cell(is_operational)="data">
        <td class="sorting_1 text-center">
          <span
            :class="
              data.item.is_operational ? 'badge bg-info' : 'badge bg-secondary'
            ">
            {{ data.item.is_operational ? "Yes" : "No" }}
          </span>
        </td>
      </template>

      <!-- Allow Negative Sales -->
      <template #cell(allow_negative_sales)="data">
        <td class="sorting_1 text-center">
          <span
            :class="
              data.item.allow_negative_sales
                ? 'badge bg-warning'
                : 'badge bg-secondary'
            ">
            {{ data.item.allow_negative_sales ? "Yes" : "No" }}
          </span>
        </td>
      </template>

      <!-- Status -->
      <template #cell(is_active)="data">
        <td class="text-center">
          <span v-if="data.item.is_active" class="badge bg-success">
            Active
          </span>
          <span v-else class="badge bg-secondary">Inactive</span>
        </td>
      </template>

      <!-- Actions -->
      <template #cell(actions)="data">
        <td class="text-center">
          <div class="btn-group btn-group-sm" role="group">
            <router-link
              v-if="hasPermission('apptransactions.view_documenttype')"
              :to="`/document-types/form?id=${data.item.id}&mode=view`"
              class="btn btn-outline-success me-1">
              View
            </router-link>
            <router-link
              v-if="hasPermission('apptransactions.change_documenttype')"
              :to="`/document-types/form?id=${data.item.id}&mode=edit`"
              class="btn btn-outline-primary me-1">
              Edit
            </router-link>
            <button
              v-if="hasPermission('apptransactions.delete_documenttype')"
              @click="deleteDocType(data.item.id)"
              class="btn btn-outline-danger">
              Delete
            </button>
          </div>
        </td>
      </template>
    </b-table>

    <div
      class="d-flex flex-wrap justify-content-center justify-content-md-end mt-3">
      <b-pagination
        v-model="currentPage"
        :total-rows="filteredItems.length"
        :per-page="perPage"
        size="sm"
        class="mb-0" />
    </div>
  </TxCard>
</template>

<script setup>
import TxCard from "@/components/layout/TxCard.vue";
import { ref, computed, onMounted, getCurrentInstance } from "vue";
import axios from "axios";
import "@/assets/css/base.css";

const { proxy } = getCurrentInstance();

const salesFlow = [
  { code: "SQ", desc: "Sales Quote" },
  { code: "SO", desc: "Sales Order" },
  { code: "PK", desc: "Picking Ticket" },
  { code: "DN", desc: "Delivery Note / Shipment" },
  { code: "INV", desc: "Sales Invoice" },
  { code: "CRN", desc: "Sales Credit Note / Return" },
];

const purchaseFlow = [
  { code: "PR", desc: "Purchase Requisition" },
  { code: "PO", desc: "Purchase Order" },
  { code: "GRN", desc: "Goods Receipt Note" },
  { code: "PINV", desc: "Purchase Invoice" },
  { code: "PRN", desc: "Purchase Return" },
];

const docTypes = ref([]);
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
    key: "type_code",
    label: "Code",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "description",
    label: "Description",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "affects_physical",
    label: "INVFIS",
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "affects_logical",
    label: "INVLOG",
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "is_purchase",
    label: "Purchase",
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "is_sales",
    label: "Sales",
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "is_operational",
    label: "Operational",
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "allow_negative_sales",
    label: "Negative Sales",
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "is_active",
    label: "Status",
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

const fetchDocTypes = async () => {
  try {
    const res = await axios.get("/api/document-types/");
    docTypes.value = res.data;
  } catch (err) {
    console.error("Error fetching document types", err);
    proxy?.notifyError?.("Error loading document types.");
  }
};

onMounted(fetchDocTypes);

const filteredItems = computed(() => {
  if (!search.value) return docTypes.value;
  return docTypes.value.filter((item) =>
    `${item.type_code} ${item.description || ""} ${
      item.is_operational ? "operational" : "non-operational"
    } ${item.allow_negative_sales ? "negative sales" : "no negative sales"}`
      .toLowerCase()
      .includes(search.value.toLowerCase())
  );
});

const deleteDocType = (id) => {
  proxy.confirmDelete(
    "Are you sure?",
    "This action cannot be undone.",
    async () => {
      try {
        await axios.delete(`/api/document-types/${id}/`);
        docTypes.value = docTypes.value.filter((doc) => doc.id !== id);
        proxy?.notifyToastSuccess?.("The document type has been deleted.");
      } catch (err) {
        console.error("Error deleting document type", err);
        proxy?.notifyError?.("Error deleting the document type.");
      }
    }
  );
};
</script>

<style scoped>
.flow-node {
  cursor: help;
  font-size: 0.75rem;
}
.flow-arrow {
  font-size: 0.9rem;
  margin: 0 0.1rem;
}
@media (min-width: 576px) {
  .flow-node {
    font-size: 0.8rem;
  }
  .flow-arrow {
    font-size: 1rem;
  }
}
</style>
