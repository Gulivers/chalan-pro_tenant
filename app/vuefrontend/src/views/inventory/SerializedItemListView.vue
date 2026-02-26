<template>
  <TxCard class="shadow-sm mt-0">
    <!-- Header del card -->
    <template #header>
      <div
        class="d-flex flex-wrap justify-content-between align-items-center w-100 gap-2">
        <h5 class="text-primary mb-0 fw-semibold listview-title">
          Serialized Items
        </h5>
        <div class="d-flex gap-2">
          <router-link
            v-if="
              features.showNewSerializedItemButton &&
              hasPermission('appinventory.add_serializeditem')
            "
            to="/serialized-items/form"
            class="btn btn-success btn-sm">
            + New Serialized Item
          </router-link>
        </div>
      </div>
    </template>

    <div class="card-body">
      <!-- Toolbar: stats + refresh -->
      <div
        class="listview-toolbar d-flex flex-wrap align-items-center gap-2 mb-3">
        <span class="badge bg-primary stats-badge">{{ totalRows }} Total</span>
        <span
          class="listview-toolbar-divider d-none d-sm-inline"
          aria-hidden="true"></span>
        <button
          type="button"
          class="btn btn-outline-success btn-sm listview-refresh-btn"
          @click="refreshTable">
          Refresh List
        </button>
      </div>

      <!-- Filters: entries per page + search -->
      <div class="listview-filters row g-2 g-md-3 mb-3 align-items-end">
        <div class="col-12 col-sm-6 col-lg-4 col-xl-3">
          <BFormGroup
            label="Entries per page:"
            label-for="per-page-select"
            label-size="sm"
            class="small mb-0 listview-filter-group">
            <BFormSelect
              id="per-page-select"
              v-model="perPage"
              :options="pageOptions"
              size="sm"
              class="form-select form-select-sm" />
          </BFormGroup>
        </div>
        <div class="col-12 col-sm-6 col-lg-5 col-xl-4 ms-lg-auto">
          <BFormGroup
            label="Search:"
            label-for="filter-input"
            label-size="sm"
            class="mb-0 listview-filter-group">
            <BFormInput
              id="filter-input"
              v-model="filter"
              type="search"
              placeholder="Search by serial number, product, warehouse, crew, notes..."
              size="sm"
              class="form-control form-control-sm" />
          </BFormGroup>
        </div>
      </div>

      <!-- Tabla con overlay -->
      <BOverlay :show="loading" rounded="sm" opacity="0.85" variant="light">
        <template #overlay>
          <div class="text-center">
            <BSpinner type="border" variant="secondary" class="mb-3" />
            <div class="h5 text-primary">Loading Serialized Items...</div>
            <div class="text-muted">Please wait while we fetch the data</div>
          </div>
        </template>

        <BTable
          ref="serializedItemTable"
          :provider="provider"
          :fields="fields"
          :filter="filter"
          :per-page="perPage"
          :current-page="currentPage"
          no-provider-sorting
          bordered
          hover
          responsive
          striped
          class="table-bordered">
          <template #cell(id)="row">
            <strong>{{ row.item.id }}</strong>
          </template>

          <template #cell(asset_tag)="row">
            {{ row.item.asset_tag || "—" }}
          </template>

          <template #cell(product_name)="row">
            {{ row.item.product_name || "—" }}
          </template>

          <template #cell(status)="row">
            <span
              v-if="row.item.status"
              class="badge"
              :class="statusBadgeClass(row.item.status)"
              style="font-size: 0.75rem">
              {{ row.item.status }}
            </span>
            <span v-else>—</span>
          </template>

          <template #cell(condition)="row">
            <span
              v-if="conditionBadgeClass(row.item.condition)"
              class="badge"
              :class="conditionBadgeClass(row.item.condition)"
              style="font-size: 0.75rem">
              {{ conditionLabel(row.item.condition) }}
            </span>
            <span v-else>—</span>
          </template>

          <template #cell(current_warehouse_name)="row">
            {{ row.item.current_warehouse_name || "—" }}
          </template>

          <template #cell(warehouse_crew_name)="row">
            {{ row.item.warehouse_crew_name || "—" }}
          </template>

          <template #cell(purchase_date)="row">
            {{ formatDate(row.item.purchase_date) }}
          </template>

          <template #cell(document_id)="row">
            {{ row.item.document_id || "—" }}
          </template>

          <template #cell(created_at)="row">
            {{ formatDateTime(row.item.created_at) }}
          </template>

          <template #cell(actions)="row">
            <div class="btn-group btn-group-sm" role="group">
              <router-link
                v-if="hasPermission('appinventory.view_serializeditem')"
                :to="`/serialized-items/view/${row.item.id}`"
                class="btn btn-outline-success me-1">
                View
              </router-link>
              <router-link
                v-if="hasPermission('appinventory.change_serializeditem')"
                :to="`/serialized-items/edit/${row.item.id}`"
                class="btn btn-outline-primary me-1">
                Edit
              </router-link>
              <button
                v-if="hasPermission('appinventory.delete_serializeditem')"
                class="btn btn-outline-danger"
                @click="deleteItem(row.item.id)">
                Delete
              </button>
            </div>
          </template>
        </BTable>
      </BOverlay>

      <!-- Paginación -->
      <div class="d-flex justify-content-end mt-3">
        <BPagination
          v-model="currentPage"
          :total-rows="totalRows"
          :per-page="perPage"
          @update:model-value="onPageChange" />
      </div>
    </div>
  </TxCard>
</template>

<script>
import TxCard from "@/components/layout/TxCard.vue";
import "@/assets/css/base.css";
import { features } from "@/config/features";

import { ref, getCurrentInstance } from "vue";
import axios from "axios";
import {
  BTable,
  BFormGroup,
  BFormInput,
  BFormSelect,
  BPagination,
  BOverlay,
  BSpinner,
} from "bootstrap-vue-next";

const ENDPOINT = "/api/serialized-items-provider/";

export default {
  name: "SerializedItemListView",
  components: {
    TxCard,
    BTable,
    BFormGroup,
    BFormInput,
    BFormSelect,
    BPagination,
    BOverlay,
    BSpinner,
  },

  setup() {
    const { proxy } = getCurrentInstance();

    const loading = ref(true);
    const filter = ref("");
    const perPage = ref(25);
    const currentPage = ref(1);
    const totalRows = ref(0);
    const serializedItemTable = ref(null);

    const pageOptions = [
      { value: 10, text: "10" },
      { value: 25, text: "25" },
      { value: 50, text: "50" },
      { value: 100, text: "100" },
    ];

    const fields = [
      {
        key: "id",
        label: "ID",
        sortable: true,
        thClass: "text-center",
        tdClass: "text-center",
      },
      {
        key: "asset_tag",
        label: "Serial Number",
        sortable: true,
        thClass: "text-start",
        tdClass: "text-start",
      },
      {
        key: "product_name",
        label: "Product",
        sortable: true,
        thClass: "text-start",
        tdClass: "text-start",
      },
      {
        key: "status",
        label: "Status",
        sortable: true,
        thClass: "text-center",
        tdClass: "text-center",
      },
      {
        key: "condition",
        label: "Condition",
        sortable: true,
        thClass: "text-center",
        tdClass: "text-center",
      },
      {
        key: "current_warehouse_name",
        label: "Current Warehouse",
        sortable: true,
        thClass: "text-start",
        tdClass: "text-start",
      },
      {
        key: "warehouse_crew_name",
        label: "Crew",
        sortable: true,
        thClass: "text-start",
        tdClass: "text-start",
      },
      {
        key: "purchase_date",
        label: "Purchase Date",
        sortable: true,
        thClass: "text-center",
        tdClass: "text-center",
      },
      {
        key: "document_id",
        label: "Document ID",
        sortable: true,
        thClass: "text-center",
        tdClass: "text-center",
      },
      {
        key: "created_at",
        label: "Created At",
        sortable: true,
        thClass: "text-center",
        tdClass: "text-center",
      },
      {
        key: "actions",
        label: "Actions",
        sortable: false,
        thClass: "text-center",
        tdClass: "text-center",
        thStyle: { width: "12%", whiteSpace: "nowrap" },
        tdStyle: { whiteSpace: "nowrap" },
      },
    ];

    const getOrderingFromSortBy = (sortBy) => {
      if (!sortBy) return "-id";
      const field = Object.keys(sortBy)[0];
      const desc = sortBy[field] === "desc";
      return desc ? `-${field}` : field;
    };

    const provider = async (context) => {
      try {
        if (!loading.value) loading.value = true;

        const page = context.currentPage || 1;
        const perPageValue = context.perPage || 25;
        const params = new URLSearchParams({
          page,
          per_page: perPageValue,
          search: context.filter || "",
          ordering: context.sortBy
            ? getOrderingFromSortBy(context.sortBy)
            : "-id",
        });

        const response = await axios.get(`${ENDPOINT}?${params}`);

        if (response.data && response.data.items) {
          totalRows.value = response.data.totalRows ?? 0;
          return response.data.items;
        }
        throw new Error("Invalid response format");
      } catch (error) {
        console.error("SerializedItem provider error:", error);
        proxy?.notifyError?.("Error loading serialized items.");
        return [];
      } finally {
        setTimeout(() => {
          loading.value = false;
        }, 300);
      }
    };

    const onPageChange = (page) => {
      currentPage.value = page;
    };

    const refreshTable = () => {
      loading.value = true;
      if (serializedItemTable.value) {
        serializedItemTable.value.refresh();
      }
    };

    const conditionBadgeClass = (value) => {
      const v = (value || "").toLowerCase();
      if (v === "ok") return "bg-success";
      if (v === "damaged") return "bg-warning text-dark";
      if (v === "needs_repair") return "bg-danger";
      return null;
    };

    const statusBadgeClass = (value) => {
      const v = (value || "").trim();
      if (v === "Active") return "bg-success";
      if (v === "Maintenance") return "bg-warning text-dark";
      if (v === "Lost") return "bg-danger";
      if (v === "Retired") return "bg-secondary";
      return "bg-secondary";
    };

    const conditionLabel = (value) => {
      const labels = {
        ok: "OK",
        damaged: "Damaged",
        needs_repair: "Needs Repair",
      };
      const v = (value || "").toLowerCase().replace(/\s/g, "_");
      return labels[v] || value || "—";
    };

    const formatDate = (dateString) => {
      if (!dateString) return "—";
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    };

    const formatDateTime = (dateString) => {
      if (!dateString) return "—";
      const date = new Date(dateString);
      return date.toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    const deleteItem = (id) => {
      proxy?.confirmDelete?.(
        "Are you sure?",
        `Delete serialized item #${id}? This action cannot be undone.`,
        async () => {
          try {
            await axios.delete(`/api/serialized-items/${id}/`);
            proxy?.notifyToastSuccess?.("The item has been deleted.");
            refreshTable();
          } catch (error) {
            console.error("Error deleting serialized item:", error);
            const status = error?.response?.status;
            const data = error?.response?.data;
            if (status === 403) {
              proxy?.notifyError?.(
                "You do not have permission for this action."
              );
            } else {
              const detail = data?.detail || "Error deleting the item.";
              proxy?.notifyError?.(detail);
            }
          }
        }
      );
    };

    return {
      features,
      loading,
      filter,
      perPage,
      currentPage,
      totalRows,
      serializedItemTable,
      pageOptions,
      fields,
      provider,
      onPageChange,
      refreshTable,
      statusBadgeClass,
      conditionBadgeClass,
      conditionLabel,
      formatDate,
      formatDateTime,
      deleteItem,
    };
  },
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
.table td {
  vertical-align: middle;
}
.badge {
  font-size: 0.75rem;
}
</style>
