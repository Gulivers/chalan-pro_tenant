<template>
  <TxCard class="mt-0">
    <template #header>
      <div
        class="d-flex flex-wrap justify-content-between align-items-center w-100 gap-2">
        <h5 class="text-primary mb-0 fw-semibold listview-title">Contracts</h5>
        <div>
          <button
            v-if="hasPermission('ctrctsapp.add_contract')"
            class="btn btn-success btn-sm"
            @click="goToCreateForm">
            + New Contract
          </button>
        </div>
      </div>
    </template>

    <div class="card-body">
      <!-- Toolbar: stats + refresh -->
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
            class="mb-0 listview-filter-group">
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
              placeholder="Search..."
              size="sm"
              class="form-control form-control-sm" />
          </BFormGroup>
        </div>
      </div>

      <BOverlay :show="isLoading" rounded="sm" opacity="0.85" variant="light">
        <template #overlay>
          <div class="text-center">
            <BSpinner type="border" variant="secondary" class="mb-3" />
            <div class="h5 text-primary">Loading Contracts...</div>
            <div class="text-muted">Please wait while we fetch the data</div>
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
          striped
          class="table-bordered">
          <template #cell(id)="row">
            <strong>{{ row.item.id }}</strong>
          </template>

          <template #cell(builder)="row">
            <div class="text-start">{{ row.item.builder?.name || "—" }}</div>
          </template>

          <template #cell(job)="row">
            <div class="text-start">{{ row.item.job?.name || "—" }}</div>
          </template>

          <template #cell(house_model)="row">
            <div class="text-start">
              {{ row.item.house_model?.name || "—" }}
            </div>
          </template>

          <template #cell(date_created)="row">
            {{ formatDate(row.item.date_created) }}
          </template>

          <template #cell(needs_reprint)="row">
            <span
              class="badge"
              :class="row.item.needs_reprint ? 'bg-danger' : 'bg-success'"
              style="font-size: 0.75rem">
              {{ row.item.needs_reprint ? "Yes" : "No" }}
            </span>
          </template>

          <template #cell(actions)="row">
            <div class="btn-group btn-group-sm">
              <button
                v-if="hasPermission('ctrctsapp.view_contract')"
                class="btn btn-outline-success me-1"
                @click="viewItem(row.item.id)">
                View
              </button>
              <button
                v-if="hasPermission('ctrctsapp.change_contract')"
                class="btn btn-outline-primary me-1"
                @click="editItem(row.item.id)">
                Edit
              </button>
              <button
                v-if="hasPermission('ctrctsapp.view_contract')"
                class="btn btn-outline-dark me-1"
                @click="printItem(row.item.id)">
                Print
              </button>
              <button
                v-if="hasPermission('ctrctsapp.delete_contract')"
                class="btn btn-outline-danger"
                @click="deleteItem(row.item.id)">
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
import TxCard from "@components/layout/TxCard.vue";
import "@assets/css/base.css";
import axios from "axios";
import { ref, getCurrentInstance } from "vue";
import { useRouter } from "vue-router";
import {
  BTable,
  BFormGroup,
  BFormInput,
  BFormSelect,
  BPagination,
  BOverlay,
  BSpinner,
} from "bootstrap-vue-next";

const ENDPOINT = "/api/contract/contracts-provider/";

export default {
  name: "ContractListView",
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
    const router = useRouter();
    const { proxy } = getCurrentInstance();

    const isLoading = ref(true);
    const currentPage = ref(1);
    const perPage = ref(25);
    const filter = ref("");
    const totalRows = ref(0);
    const tableRef = ref(null);
    const stats = ref({ total: 0, active: 0, inactive: 0 });

    const fields = [
      {
        key: "id",
        label: "ID",
        sortable: true,
        thClass: "text-center",
        tdClass: "text-center",
      },
      { key: "doc_type", label: "Doc Type", sortable: true },
      { key: "type", label: "Type", sortable: true },
      { key: "date_created", label: "Date", sortable: true },
      { key: "builder", label: "Builder", sortable: false },
      { key: "job", label: "Job", sortable: false },
      { key: "house_model", label: "Model", sortable: false },
      { key: "lot", label: "Lot", sortable: true },
      { key: "address", label: "Address", sortable: true },
      { key: "sqft", label: "SqFt", sortable: true },
      { key: "job_price", label: "Job Price", sortable: true },
      { key: "total_options", label: "Options", sortable: true },
      { key: "total", label: "Total", sortable: true },
      { key: "needs_reprint", label: "Need Print", sortable: true },
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

    const pageOptions = [
      { value: 10, text: "10" },
      { value: 25, text: "25" },
      { value: 50, text: "50" },
      { value: 100, text: "100" },
    ];

    const provider = async (context) => {
      try {
        if (!isLoading.value) isLoading.value = true;
        const page = context.currentPage || 1;
        const perPageValue = context.perPage || 25;
        const params = new URLSearchParams({
          page: page,
          per_page: perPageValue,
          search: context.filter || "",
          ordering: context.sortBy
            ? getOrderingFromSortBy(context.sortBy)
            : "-id",
        });
        const { data } = await axios.get(`${ENDPOINT}?${params}`);
        totalRows.value = data.totalRows || 0;
        stats.value = data.stats || stats.value;
        return data.items || [];
      } catch (e) {
        console.error("contracts provider error:", e);
        proxy?.notifyError?.("Error loading contracts.");
        return [];
      } finally {
        setTimeout(() => {
          isLoading.value = false;
        }, 300);
      }
    };

    const formatDate = (iso) => {
      if (!iso) return "";
      const d = new Date(iso);
      const opts = { year: "numeric", month: "short", day: "2-digit" };
      return d.toLocaleDateString("en-US", opts);
    };

    const getOrderingFromSortBy = (sortBy) => {
      if (!sortBy) return "-id";
      const field = Object.keys(sortBy)[0];
      const desc = sortBy[field] === "desc";
      return desc ? `-${field}` : field;
    };

    const onPageChange = (page) => {
      currentPage.value = page;
    };

    const refreshTable = () => {
      isLoading.value = true;
      if (tableRef.value) tableRef.value.refresh();
    };

    const goToCreateForm = () => router.push({ name: "contract-form" });
    const viewItem = (id) =>
      router.push({ name: "contract-view", params: { id } });
    const editItem = (id) => {
      const url = router.resolve({ name: "contract-edit", params: { id } });
      window.open(url.href, "_blank");
    };
    const printItem = async (id) => {
      try {
        const response = await axios.get(`/api/contract-pdf/${id}/`, {
          headers: {
            Authorization: `Token ${localStorage.getItem("authToken")}`,
          },
          responseType: "json",
        });

        if (!response.data?.file) {
          throw new Error("No PDF file received");
        }

        const byteCharacters = atob(response.data.file);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i += 1) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "application/pdf" });
        const pdfUrl = window.URL.createObjectURL(blob);

        const win = window.open(pdfUrl, "_blank");
        if (!win) {
          const link = document.createElement("a");
          link.href = pdfUrl;
          link.download = response.data.filename || `contract_${id}.pdf`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }

        setTimeout(() => window.URL.revokeObjectURL(pdfUrl), 10000);
      } catch (error) {
        console.error("Error generating contract PDF:", error);
        proxy?.notifyError?.("Could not generate contract PDF.");
      }
    };

    const deleteItem = (id) => {
      // Usar el mismo patrón de ProductListView (confirmDelete + toast + refresh)
      proxy?.confirmDelete?.(
        "Are you sure?",
        `Delete contract #${id}? This action cannot be undone.`,
        async () => {
          try {
            await axios.delete(`/api/contract/${id}/`);
            proxy?.notifyToastSuccess?.("The contract has been deleted.");
            // Refrescar tabla sin recargar página
            refreshTable();
          } catch (error) {
            console.error("Error deleting contract:", error);
            const status = error?.response?.status;
            const data = error?.response?.data;
            if (status === 403) {
              proxy?.notifyError?.(
                "You do not have permission for this action."
              );
            } else if (status === 409) {
              const detail =
                data?.detail ||
                "Cannot delete this contract because it is being used elsewhere.";
              proxy?.notifyError?.(detail);
            } else {
              const detail = data?.detail || "Error deleting the contract.";
              proxy?.notifyError?.(detail);
            }
          }
        }
      );
    };

    return {
      isLoading,
      currentPage,
      perPage,
      filter,
      totalRows,
      tableRef,
      stats,
      fields,
      pageOptions,
      provider,
      onPageChange,
      refreshTable,
      goToCreateForm,
      viewItem,
      editItem,
      printItem,
      deleteItem,
      formatDate,
    };
  },
};
</script>

<style scoped>
/* Listview header: toolbar + filters */
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
.form-select-sm,
.form-control-sm {
  font-size: 0.8rem;
}
.card {
  border: none;
}
</style>
