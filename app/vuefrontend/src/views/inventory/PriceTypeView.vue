<template>
  <TxCard class="mt-0">
    <template #header>
      <div
        class="d-flex flex-wrap justify-content-between align-items-center w-100 gap-2">
        <h5 class="text-primary mb-0 fw-semibold listview-title">
          Price Types
        </h5>
        <div>
          <button
            v-if="hasPermission('appinventory.add_pricetype')"
            class="btn btn-success btn-sm"
            @click="goToCreateForm">
            + New
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
          @click="refreshTable">
          Refresh List
        </button>
      </div>
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
              placeholder="Search by name, description... (multiple words)"
              size="sm"
              class="form-control form-control-sm" />
          </BFormGroup>
        </div>
      </div>

      <BOverlay :show="isLoading" rounded="sm" opacity="0.85" variant="light">
        <template #overlay>
          <div class="text-center">
            <BSpinner type="border" variant="secondary" class="mb-3" />
            <div class="h5 text-primary">Loading Price Types...</div>
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
          class="table-bordered price-type-fixed-table">
          <template #cell(id)="row">
            <strong>{{ row.item.id }}</strong>
          </template>

          <template #cell(name)="row">
            <div class="text-start">{{ row.item.name }}</div>
          </template>

          <template #cell(description)="row">
            <div class="text-start">{{ row.item.description || "—" }}</div>
          </template>

          <template #cell(pricing_method)="row">
            <div class="text-start small">
              {{ pricingMethodLabel(row.item.pricing_method) }}
            </div>
          </template>

          <template #cell(margin_percent)="row">
            <div class="text-end small">
              {{
                formatMarginPercent(
                  row.item.margin_percent,
                  row.item.pricing_method
                )
              }}
            </div>
          </template>

          <template #cell(is_active)="row">
            <span
              class="badge"
              :class="row.item.is_active ? 'bg-success' : 'bg-secondary'"
              style="font-size: 0.75rem">
              {{ row.item.is_active ? "Active" : "Inactive" }}
            </span>
          </template>

          <template #cell(actions)="row">
            <div class="btn-group btn-group-sm">
              <button
                v-if="hasPermission('appinventory.view_pricetype')"
                class="btn btn-outline-success me-1"
                @click="viewItem(row.item.id)">
                View
              </button>
              <button
                v-if="hasPermission('appinventory.change_pricetype')"
                class="btn btn-outline-primary me-1"
                @click="editItem(row.item.id)">
                Edit
              </button>
              <button
                v-if="hasPermission('appinventory.delete_pricetype')"
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

const ENDPOINT = "/api/pricetypes-provider/";

const PRICING_METHOD_LABELS = {
  NONE: "None (list price only)",
  MARKUP: "Markup % on cost",
  MARGIN: "Margin % on cost",
};

export default {
  name: "PriceTypeView",
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

    const stats = ref({ total: 0, active: 0, inactive: 0 });
    const isLoading = ref(true);
    const currentPage = ref(1);
    const perPage = ref(25);
    const filter = ref("");
    const totalRows = ref(0);
    const tableRef = ref(null);

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
        key: "description",
        label: "Description",
        sortable: true,
        thClass: "text-start price-type-field-desc",
        tdClass: "text-start price-type-field-desc",
        thStyle: { width: "35%" },
        tdStyle: { wordBreak: "break-word" },
      },
      {
        key: "pricing_method",
        label: "Pricing from purchase cost",
        sortable: true,
        thClass: "text-start price-type-field-pricing",
        tdClass: "text-start price-type-field-pricing",
        thStyle: {
          width: "19%",
          maxWidth: "8.25rem",
          whiteSpace: "normal",
          lineHeight: 1.25,
          fontSize: "0.90rem",
        },
        tdStyle: {
          maxWidth: "8.25rem",
          fontSize: "0.8rem",
          wordBreak: "break-word",
        },
      },
      {
        key: "margin_percent",
        label: "Markup / margin % (0–100)",
        sortable: true,
        thClass: "text-end price-type-field-margin",
        tdClass: "text-end price-type-field-margin",
        thStyle: {
          width: "19%",
          maxWidth: "8.25rem",
          whiteSpace: "normal",
          lineHeight: 1.25,
          fontSize: "0.90rem",
        },
        tdStyle: {
          width: "5.25rem",
          maxWidth: "5.5rem",
          fontVariantNumeric: "tabular-nums",
          fontSize: "0.8rem",
          whiteSpace: "nowrap",
        },
      },
      {
        key: "is_active",
        label: "Status",
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

    const pageOptions = [
      { value: 10, text: "10" },
      { value: 25, text: "25" },
      { value: 50, text: "50" },
      { value: 100, text: "100" },
    ];

    const getOrderingFromSortBy = (sortBy) => {
      if (!sortBy) return "-id";
      let field;
      let desc = false;
      if (Array.isArray(sortBy) && sortBy.length > 0) {
        const first = sortBy[0];
        field = first.key ?? first.field;
        const order = first.order ?? (first.sortDesc ? "desc" : "asc");
        desc = order === "desc";
      } else if (typeof sortBy === "object" && !Array.isArray(sortBy)) {
        field = Object.keys(sortBy)[0];
        desc = sortBy[field] === "desc";
      }
      if (!field) return "-id";
      return desc ? `-${field}` : field;
    };

    const provider = async (context) => {
      try {
        if (!isLoading.value) isLoading.value = true;
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
        if (response.data?.items) {
          if (response.data.stats) stats.value = response.data.stats;
          totalRows.value = response.data.totalRows ?? 0;
          return response.data.items;
        }
        throw new Error("Invalid response format");
      } catch (error) {
        console.error("Provider error:", error);
        proxy?.notifyError?.("Error loading price types.");
        return [];
      } finally {
        setTimeout(() => {
          isLoading.value = false;
        }, 300);
      }
    };

    const onPageChange = (page) => {
      currentPage.value = page;
    };
    const refreshTable = () => {
      isLoading.value = true;
      if (tableRef.value) tableRef.value.refresh();
    };

    const goToCreateForm = () => router.push({ name: "price-type-form" });
    const viewItem = (id) =>
      router.push({ name: "price-type-view", params: { id } });
    const editItem = (id) =>
      router.push({ name: "price-type-edit", params: { id } });

    const pricingMethodLabel = (value) =>
      PRICING_METHOD_LABELS[value] ?? value ?? "—";

    const formatMarginPercent = (marginPercent, pricingMethod) => {
      if (marginPercent == null || marginPercent === "") return "—";
      if (pricingMethod === "NONE" || !pricingMethod) {
        return "—";
      }
      const n = Number(marginPercent);
      if (!Number.isFinite(n)) return "—";
      return n.toLocaleString("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 4,
      });
    };

    const deleteItem = (id) => {
      proxy?.confirmDelete?.(
        "Delete?",
        "This will delete the price type. This action cannot be undone.",
        async () => {
          try {
            await axios.delete(`/api/pricetypes/${id}/`);
            proxy?.notifyToastSuccess?.("The price type has been deleted.");
            refreshTable();
          } catch (error) {
            const status = error?.response?.status;
            const data = error?.response?.data;
            if (status === 403)
              proxy?.notifyError?.(
                "You do not have permission for this action."
              );
            else if (status === 409)
              proxy?.notifyError?.(
                data?.detail || "Cannot delete: price type is in use."
              );
            else
              proxy?.notifyError?.(
                data?.detail || "Error deleting the price type."
              );
          }
        }
      );
    };

    return {
      stats,
      isLoading,
      currentPage,
      perPage,
      filter,
      totalRows,
      tableRef,
      fields,
      pageOptions,
      provider,
      onPageChange,
      refreshTable,
      goToCreateForm,
      viewItem,
      editItem,
      deleteItem,
      pricingMethodLabel,
      formatMarginPercent,
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
.card {
  border: none;
}
.form-select-sm,
.form-control-sm {
  font-size: 0.8rem;
}

/* Compact pricing columns; Description keeps a larger share (table-layout fixed) */
:deep(.price-type-fixed-table.table) {
  table-layout: fixed;
}
</style>
