<template>
  <TxCard class="shadow-sm mt-0">
    <template #header>
      <div class="d-flex justify-content-between align-items-center w-100">
        <h6 class="text-primary mb-0">Inventory Transfers</h6>
        <div class="d-flex gap-2">
          <router-link
            v-if="hasPermission('appinventory.add_inventorytransfer')"
            to="/inventory-transfers/form"
            class="btn btn-success">
            + New
          </router-link>
          <button
            v-if="!loading"
            class="btn btn-outline-primary btn-sm"
            @click="refreshTable">
            Refresh List
          </button>
        </div>
      </div>
    </template>

    <div class="card-body">
      <div class="row mb-3">
        <div class="col-lg-3 text-start">
          <BFormGroup
            label="entries per page:"
            label-for="per-page-select"
            label-cols-sm="6"
            label-size="sm"
            class="mb-0 small">
            <BFormSelect
              id="per-page-select"
              v-model="perPage"
              :options="pageOptions"
              size="sm"
              class="form-select-xs" />
          </BFormGroup>
        </div>
        <div class="col-lg-3"></div>
        <div class="col-lg-6 text-end">
          <BFormGroup
            label="Search:"
            label-for="filter-input"
            label-cols-sm="4"
            label-size="sm"
            class="mb-0">
            <BFormInput
              id="filter-input"
              v-model="filter"
              type="search"
              placeholder="Search by description, warehouses..."
              size="sm" />
          </BFormGroup>
        </div>
      </div>

      <BOverlay :show="loading" rounded="sm" opacity="0.85" variant="light">
        <template #overlay>
          <div class="text-center">
            <BSpinner type="border" variant="secondary" class="mb-3" />
            <div class="h5 text-primary">Loading Inventory Transfers...</div>
          </div>
        </template>

        <BTable
          ref="tableRef"
          :provider="provider"
          :fields="fields"
          :filter="filter"
          :per-page="perPage"
          :current-page="currentPage"
          no-provider-sorting
          bordered
          hover
          responsive
          striped>
          <template #cell(id)="row">
            <strong>{{ row.item.id }}</strong>
          </template>
          <template #cell(from_warehouse_name)="row">
            {{ row.item.from_warehouse_name || "—" }}
          </template>
          <template #cell(to_warehouse_name)="row">
            {{ row.item.to_warehouse_name || "—" }}
          </template>
          <template #cell(description)="row">
            {{ row.item.description || "—" }}
          </template>
          <template #cell(status)="row">
            <span
              :class="statusBadgeClass(row.item.status)"
              class="badge"
              style="font-size: 0.75rem">
              {{ row.item.status || "—" }}
            </span>
          </template>
          <template #cell(created_at)="row">
            {{ formatDateTime(row.item.created_at) }}
          </template>
          <template #cell(last_updated)="row">
            {{ formatDateTime(row.item.last_updated) }}
          </template>
          <template #cell(created_by_username)="row">
            {{ row.item.created_by_username || "—" }}
          </template>
          <template #cell(actions)="row">
            <div class="btn-group btn-group-sm" role="group">
              <router-link
                v-if="hasPermission('appinventory.view_inventorytransfer')"
                :to="`/inventory-transfers/view/${row.item.id}`"
                class="btn btn-outline-success me-1">
                View
              </router-link>
              <router-link
                v-if="hasPermission('appinventory.change_inventorytransfer')"
                :to="`/inventory-transfers/edit/${row.item.id}`"
                class="btn btn-outline-primary me-1">
                Edit
              </router-link>
              <button
                v-if="hasPermission('appinventory.delete_inventorytransfer')"
                @click="deleteItem(row.item.id)"
                class="btn btn-outline-danger">
                Delete
              </button>
            </div>
          </template>
        </BTable>
      </BOverlay>

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

const ENDPOINT = "/api/inventory-transfers-provider/";

export default {
  name: "InventoryTransferListView",
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
    const tableRef = ref(null);

    const pageOptions = [
      { value: 10, text: "10" },
      { value: 25, text: "25" },
      { value: 50, text: "50" },
      { value: 100, text: "100" },
    ];

    const fields = [
      { key: "id", label: "ID", thClass: "text-center", tdClass: "text-center" },
      { key: "from_warehouse_name", label: "From Warehouse", thClass: "text-start", tdClass: "text-start" },
      { key: "to_warehouse_name", label: "To Warehouse", thClass: "text-start", tdClass: "text-start" },
      { key: "description", label: "Description", thClass: "text-start", tdClass: "text-start" },
      { key: "status", label: "Status", thClass: "text-center", tdClass: "text-center" },
      { key: "created_at", label: "Created At", thClass: "text-center", tdClass: "text-center" },
      { key: "last_updated", label: "Last Updated", thClass: "text-center", tdClass: "text-center" },
      { key: "created_by_username", label: "Created By", thClass: "text-start", tdClass: "text-start" },
      {
        key: "actions",
        label: "Actions",
        thClass: "text-center",
        tdClass: "text-center",
        thStyle: { width: "12%", whiteSpace: "nowrap" },
        tdStyle: { whiteSpace: "nowrap" },
      },
    ];

    const getOrderingFromSortBy = (sortBy) => {
      if (!sortBy) return "-created_at";
      if (Array.isArray(sortBy) && sortBy.length > 0) {
        const first = sortBy[0];
        const field = first.key ?? first.field;
        const desc = (first.order ?? "asc") === "desc";
        return field ? (desc ? `-${field}` : field) : "-created_at";
      }
      const field = Object.keys(sortBy)[0];
      const desc = sortBy[field] === "desc";
      return field ? (desc ? `-${field}` : field) : "-created_at";
    };

    const provider = async (context) => {
      try {
        loading.value = true;
        const page = context.currentPage || 1;
        const perPageValue = context.perPage || 25;
        const params = new URLSearchParams({
          page,
          per_page: perPageValue,
          search: context.filter || "",
          ordering: context.sortBy ? getOrderingFromSortBy(context.sortBy) : "-created_at",
        });
        const response = await axios.get(`${ENDPOINT}?${params}`);
        if (response.data?.items) {
          totalRows.value = response.data.totalRows ?? 0;
          return response.data.items;
        }
        return [];
      } catch (error) {
        console.error("InventoryTransfer provider error:", error);
        proxy?.notifyToastError?.("Error loading inventory transfers.");
        return [];
      } finally {
        setTimeout(() => { loading.value = false; }, 300);
      }
    };

    const onPageChange = (page) => { currentPage.value = page; };

    const refreshTable = () => {
      loading.value = true;
      if (tableRef.value) tableRef.value.refresh();
    };

    const statusBadgeClass = (status) => {
      if (!status) return "bg-secondary";
      const s = status.toLowerCase();
      if (s === "completed") return "bg-success";
      if (s === "reverted") return "bg-danger";
      return "bg-secondary";
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
        "Delete this inventory transfer? This action cannot be undone.",
        async () => {
          try {
            await axios.delete(`/api/inventory-transfers/${id}/`);
            proxy?.notifyToastSuccess?.("Transfer deleted.");
            refreshTable();
          } catch (error) {
            const data = error?.response?.data;
            proxy?.notifyToastError?.(data?.detail || "Error deleting transfer.");
          }
        }
      );
    };

    return {
      loading,
      filter,
      perPage,
      currentPage,
      totalRows,
      tableRef,
      pageOptions,
      fields,
      provider,
      onPageChange,
      refreshTable,
      statusBadgeClass,
      formatDateTime,
      deleteItem,
    };
  },
};
</script>
