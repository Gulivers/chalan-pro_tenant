<template>
  <JRPage>
    <JRPageHeader title="Serialized Items">
      <template
        v-if="
          features.showNewSerializedItemButton &&
          hasPermission('appinventory.add_serializeditem')
        "
        #actions>
        <JRButton type="button" :fluid="isMobile" @click="goToCreateForm">
          + New Serialized Item
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-serialized-list__search">
          <label class="jr-sr-only" for="serialized-filter-input">
            Search serialized items
          </label>
          <span class="jr-serialized-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="serialized-filter-input"
            v-model="filter"
            type="search"
            placeholder="Search by serial, product, warehouse, crew, notes…" />
        </div>
      </template>

      <template #stats>
        <div class="jr-serialized-list__summary" aria-live="polite">
          <JRBadge :value="`${totalRows} Total`" severity="secondary" />
        </div>
      </template>

      <template #actions>
        <label class="jr-sr-only" for="serialized-per-page">
          Entries per page
        </label>
        <JRSelect
          class="jr-serialized-list__entries"
          inputId="serialized-per-page"
          v-model="perPage"
          :options="pageOptions"
          optionLabel="label"
          optionValue="value" />
        <JRButton
          type="button"
          variant="ghost"
          size="sm"
          class="jr-serialized-list__refresh"
          @click="refreshTable">
          <RefreshIcon />
          Refresh
        </JRButton>
      </template>
    </JRToolbar>

    <div v-if="isMobile" class="jr-serialized-list__mobile">
      <JREmptyState
        v-if="!items.length && !isLoading"
        :title="emptyTitle"
        :description="emptyDescription" />
      <p v-if="isLoading && !items.length" class="jr-serialized-list__loading">
        Loading serialized items…
      </p>
      <p
        v-else-if="isLoading && items.length"
        class="jr-serialized-list__loading"
        aria-live="polite">
        Updating…
      </p>
      <ul
        v-if="items.length"
        class="jr-serialized-list__rows"
        :aria-busy="isLoading ? 'true' : 'false'">
        <li v-for="item in items" :key="item.id" class="jr-serialized-row">
          <div class="jr-serialized-row__main">
            <router-link
              v-if="canView"
              class="jr-serialized-row__name jr-serialized-row__name--link"
              :to="viewTo(item.id)"
              :aria-label="`View ${primaryLabel(item)}`">
              {{ primaryLabel(item) }}
            </router-link>
            <span v-else class="jr-serialized-row__name">
              {{ primaryLabel(item) }}
            </span>
            <p class="jr-serialized-row__meta">
              <span>{{ item.product_name || "—" }}</span>
              <span v-if="item.current_warehouse_name" aria-hidden="true">·</span>
              <span v-if="item.current_warehouse_name">
                {{ item.current_warehouse_name }}
              </span>
            </p>
          </div>
          <div class="jr-serialized-row__aside">
            <JRBadge
              v-if="item.status"
              :value="item.status"
              :severity="statusSeverity(item.status)" />
            <JRBadge
              v-if="conditionLabel(item.condition) !== '—'"
              :value="conditionLabel(item.condition)"
              :severity="conditionSeverity(item.condition)" />
            <JRRowActions
              v-if="hasRowActions"
              :actions="getRowActions(item)"
              :compact="true"
              :entity-label="primaryLabel(item)" />
          </div>
        </li>
      </ul>
      <Paginator
        v-if="totalRows > 0"
        class="jr-serialized-list__pager"
        :rows="perPage"
        :totalRecords="totalRows"
        :first="tableFirst"
        template="PrevPageLink CurrentPageReport NextPageLink"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
        @page="onTablePage" />
    </div>

    <div v-else class="jr-serialized-list__table">
      <JRDataTable
        :value="items"
        :loading="isLoading"
        dataKey="id"
        lazy
        paginator
        :rows="perPage"
        :totalRecords="totalRows"
        :first="tableFirst"
        :sortField="sortField"
        :sortOrder="sortOrder"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
        scrollable
        stripedRows
        :tableStyle="tableMinWidth"
        :emptyTitle="emptyTitle"
        :emptyDescription="emptyDescription"
        @page="onTablePage"
        @sort="onTableSort">
        <Column field="asset_tag" header="Serial Number" sortable>
          <template #body="{ data }">
            <router-link
              v-if="canView"
              class="jr-serialized-row__name jr-serialized-row__name--link"
              :to="viewTo(data.id)"
              :aria-label="`View ${primaryLabel(data)}`">
              {{ primaryLabel(data) }}
            </router-link>
            <span v-else>{{ primaryLabel(data) }}</span>
          </template>
        </Column>
        <Column field="product_name" header="Product" sortable>
          <template #body="{ data }">
            {{ data.product_name || "—" }}
          </template>
        </Column>
        <Column field="status" header="Status" sortable>
          <template #body="{ data }">
            <JRBadge
              v-if="data.status"
              :value="data.status"
              :severity="statusSeverity(data.status)" />
            <span v-else>—</span>
          </template>
        </Column>
        <Column field="condition" header="Condition" sortable>
          <template #body="{ data }">
            <JRBadge
              v-if="conditionLabel(data.condition) !== '—'"
              :value="conditionLabel(data.condition)"
              :severity="conditionSeverity(data.condition)" />
            <span v-else>—</span>
          </template>
        </Column>
        <Column field="current_warehouse_name" header="Warehouse" :sortable="false">
          <template #body="{ data }">
            {{ data.current_warehouse_name || "—" }}
          </template>
        </Column>
        <Column
          v-if="!isTablet"
          field="warehouse_crew_name"
          header="Crew"
          :sortable="false">
          <template #body="{ data }">
            {{ data.warehouse_crew_name || "—" }}
          </template>
        </Column>
        <Column
          v-if="!isTablet"
          field="purchase_date"
          header="Purchase Date"
          sortable>
          <template #body="{ data }">
            {{ formatDate(data.purchase_date) }}
          </template>
        </Column>
        <Column
          v-if="!isTablet"
          field="document_id"
          header="Document"
          :sortable="false">
          <template #body="{ data }">
            {{ data.document_id || "—" }}
          </template>
        </Column>
        <Column v-if="!isTablet" field="created_at" header="Created" sortable>
          <template #body="{ data }">
            {{ formatDateTime(data.created_at) }}
          </template>
        </Column>
        <Column
          v-if="hasRowActions"
          header="Actions"
          :sortable="false"
          :headerClass="
            isTablet
              ? 'jr-col-actions jr-col-actions--compact'
              : 'jr-col-actions'
          "
          :bodyClass="
            isTablet
              ? 'jr-col-actions jr-col-actions--compact'
              : 'jr-col-actions'
          ">
          <template #body="{ data }">
            <JRRowActions
              :actions="getRowActions(data)"
              :compact="isTablet"
              :entity-label="primaryLabel(data)" />
          </template>
        </Column>
      </JRDataTable>
    </div>
  </JRPage>
</template>

<script>
import axios from "axios";
import {
  ref,
  computed,
  watch,
  onMounted,
  onUnmounted,
  getCurrentInstance,
} from "vue";
import { useRouter } from "vue-router";
import Column from "primevue/column";
import Paginator from "primevue/paginator";
import EyeIcon from "@primevue/icons/eye";
import PencilIcon from "@primevue/icons/pencil";
import RefreshIcon from "@primevue/icons/refresh";
import SearchIcon from "@primevue/icons/search";
import TrashIcon from "@primevue/icons/trash";
import { features } from "@/config/features";
import {
  JRPage,
  JRPageHeader,
  JRToolbar,
  JRButton,
  JRSelect,
  JRInput,
  JRBadge,
  JRDataTable,
  JREmptyState,
  JRRowActions,
} from "@ui";

const ENDPOINT = "/api/serialized-items-provider/";
const PHONE_MQ = "(max-width: 767.98px)";
const TABLET_MQ = "(min-width: 768px) and (max-width: 1023.98px)";

function readViewport() {
  if (typeof window === "undefined" || !window.matchMedia) {
    return { isMobile: false, isTablet: false };
  }
  return {
    isMobile: window.matchMedia(PHONE_MQ).matches,
    isTablet: window.matchMedia(TABLET_MQ).matches,
  };
}

export default {
  name: "SerializedItemListView",
  components: {
    Column,
    Paginator,
    RefreshIcon,
    SearchIcon,
    JRPage,
    JRPageHeader,
    JRToolbar,
    JRButton,
    JRSelect,
    JRInput,
    JRBadge,
    JRDataTable,
    JREmptyState,
    JRRowActions,
  },

  setup() {
    const router = useRouter();
    const { proxy } = getCurrentInstance();

    const items = ref([]);
    const isLoading = ref(true);
    const loadError = ref(false);
    const filter = ref("");
    const perPage = ref(25);
    const currentPage = ref(1);
    const totalRows = ref(0);
    const sortField = ref("asset_tag");
    const sortOrder = ref(1);
    let searchTimer = null;

    const initialViewport = readViewport();
    const isMobile = ref(initialViewport.isMobile);
    const isTablet = ref(initialViewport.isTablet);
    let phoneQuery = null;
    let tabletQuery = null;
    let onViewport = null;

    const pageOptions = [
      { value: 10, label: "10" },
      { value: 25, label: "25" },
      { value: 50, label: "50" },
      { value: 100, label: "100" },
    ];

    const tableFirst = computed(() => (currentPage.value - 1) * perPage.value);
    const tableMinWidth = computed(() =>
      isTablet.value ? "min-width: 40rem" : "min-width: 56rem"
    );
    const emptyTitle = computed(() =>
      loadError.value ? "Could not load serialized items" : "No serialized items"
    );
    const emptyDescription = computed(() =>
      loadError.value
        ? "Try Refresh."
        : "No serialized items match the current search."
    );

    const canView = computed(() =>
      !!proxy?.hasPermission?.("appinventory.view_serializeditem")
    );

    const hasRowActions = computed(
      () =>
        canView.value ||
        !!proxy?.hasPermission?.("appinventory.change_serializeditem") ||
        !!proxy?.hasPermission?.("appinventory.delete_serializeditem")
    );

    const primaryLabel = (item) => {
      const tag = (item?.asset_tag || "").toString().trim();
      return tag || "—";
    };

    const statusSeverity = (value) => {
      const v = (value || "").trim();
      if (v === "Active") return "success";
      if (v === "Maintenance") return "info";
      if (v === "Lost") return "danger";
      return "secondary";
    };

    const conditionSeverity = (value) => {
      const v = (value || "").toLowerCase();
      if (v === "ok") return "success";
      if (v === "damaged" || v === "needs_repair") return "danger";
      return "secondary";
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
      if (Number.isNaN(date.getTime())) return "—";
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    };

    const formatDateTime = (dateString) => {
      if (!dateString) return "—";
      const date = new Date(dateString);
      if (Number.isNaN(date.getTime())) return "—";
      return date.toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    };

    const getOrderingFromSortBy = (sortBy) => {
      if (!sortBy) return "asset_tag";

      let field;
      let desc = false;

      if (sortBy.sortField) {
        field = sortBy.sortField;
        desc = sortBy.sortOrder === -1;
      } else if (typeof sortBy === "object" && !Array.isArray(sortBy)) {
        field = Object.keys(sortBy)[0];
        desc = sortBy[field] === "desc";
      }

      if (!field) return "asset_tag";
      // Backend allowlist: id, asset_tag, product__name, status, condition,
      // purchase_date, created_at (see SerializedItemListProviderAPIView).
      const fieldMap = {
        id: "id",
        asset_tag: "asset_tag",
        product_name: "product__name",
        status: "status",
        condition: "condition",
        purchase_date: "purchase_date",
        created_at: "created_at",
      };
      const djangoField = fieldMap[field];
      if (!djangoField) return "asset_tag";
      return desc ? `-${djangoField}` : djangoField;
    };

    const loadItems = async () => {
      if (!isLoading.value) isLoading.value = true;

      try {
        const params = new URLSearchParams({
          page: currentPage.value,
          per_page: perPage.value,
          search: filter.value || "",
          ordering: getOrderingFromSortBy({
            sortField: sortField.value,
            sortOrder: sortOrder.value,
          }),
        });

        const response = await axios.get(`${ENDPOINT}?${params}`);

        if (response.data && response.data.items) {
          totalRows.value = response.data.totalRows ?? 0;
          items.value = response.data.items;
          loadError.value = false;
        } else {
          throw new Error("Invalid response format");
        }
      } catch (error) {
        console.error("SerializedItem provider error:", error);
        loadError.value = true;
        items.value = [];
        totalRows.value = 0;
        proxy?.notifyError?.("Error loading serialized items.");
      } finally {
        setTimeout(() => {
          isLoading.value = false;
        }, 300);
      }
    };

    const onTablePage = (event) => {
      currentPage.value = (event.page ?? 0) + 1;
      if (event.rows && event.rows !== perPage.value) {
        perPage.value = event.rows;
      }
      loadItems();
    };

    const onTableSort = (event) => {
      sortField.value = event.sortField || "asset_tag";
      sortOrder.value = event.sortOrder ?? 1;
      currentPage.value = 1;
      loadItems();
    };

    const refreshTable = () => {
      isLoading.value = true;
      loadItems();
    };

    const viewTo = (id) => ({
      name: "serialized-item-view",
      params: { id },
    });

    const goToCreateForm = () => {
      router.push("/serialized-items/form");
    };

    const viewItem = (id) => {
      router.push(viewTo(id));
    };

    const editItem = (id) => {
      router.push({ name: "serialized-item-edit", params: { id } });
    };

    const getRowActions = (item) => {
      const actions = [];
      if (proxy?.hasPermission?.("appinventory.view_serializeditem")) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => viewItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("appinventory.change_serializeditem")) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => editItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("appinventory.delete_serializeditem")) {
        actions.push({
          key: "delete",
          label: "Delete",
          severity: "danger",
          icon: TrashIcon,
          command: () => deleteItem(item.id),
        });
      }
      return actions;
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

    onMounted(() => {
      if (typeof window !== "undefined" && window.matchMedia) {
        phoneQuery = window.matchMedia(PHONE_MQ);
        tabletQuery = window.matchMedia(TABLET_MQ);
        onViewport = () => {
          const viewport = readViewport();
          isMobile.value = viewport.isMobile;
          isTablet.value = viewport.isTablet;
        };
        onViewport();
        if (phoneQuery.addEventListener) {
          phoneQuery.addEventListener("change", onViewport);
          tabletQuery.addEventListener("change", onViewport);
        } else {
          phoneQuery.addListener(onViewport);
          tabletQuery.addListener(onViewport);
        }
      }
      loadItems();
    });

    onUnmounted(() => {
      if (searchTimer) clearTimeout(searchTimer);
      if (onViewport) {
        if (phoneQuery?.removeEventListener) {
          phoneQuery.removeEventListener("change", onViewport);
          tabletQuery.removeEventListener("change", onViewport);
        } else {
          phoneQuery?.removeListener?.(onViewport);
          tabletQuery?.removeListener?.(onViewport);
        }
      }
    });

    watch(perPage, () => {
      currentPage.value = 1;
      loadItems();
    });

    watch(filter, () => {
      if (searchTimer) clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        currentPage.value = 1;
        loadItems();
      }, 300);
    });

    return {
      features,
      items,
      isLoading,
      loadError,
      filter,
      perPage,
      currentPage,
      totalRows,
      sortField,
      sortOrder,
      tableFirst,
      pageOptions,
      emptyTitle,
      emptyDescription,
      isMobile,
      isTablet,
      tableMinWidth,
      hasRowActions,
      canView,
      primaryLabel,
      statusSeverity,
      conditionSeverity,
      conditionLabel,
      formatDate,
      formatDateTime,
      getRowActions,
      refreshTable,
      onTablePage,
      onTableSort,
      goToCreateForm,
      viewTo,
      viewItem,
      editItem,
      deleteItem,
    };
  },
};
</script>

<style scoped>
.jr-serialized-list__search {
  position: relative;
  min-width: 0;
  width: 100%;
}

.jr-serialized-list__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-serialized-list__search-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.jr-serialized-list__search :deep(.p-inputtext) {
  padding-left: 2.25rem;
}

.jr-serialized-list__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  pointer-events: none;
}

:deep(.jr-toolbar__actions .jr-serialized-list__entries.p-select),
:deep(.jr-toolbar__actions .jr-serialized-list__entries.jr-control) {
  width: 6.25rem;
  min-width: 6.25rem;
  flex: 0 0 auto;
}

.jr-serialized-list__loading {
  margin: 0;
  padding: 1rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-serialized-list__rows {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: 1px solid var(--color-jr-border);
}

.jr-serialized-list__rows[aria-busy="true"] {
  opacity: 0.55;
}

.jr-serialized-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-serialized-row__main {
  min-width: 0;
  flex: 1 1 auto;
  text-align: left;
}

.jr-serialized-row__name {
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-serialized-row__name--link {
  color: var(--color-jr-primary);
  text-decoration: none;
}

.jr-serialized-row__name--link:hover {
  text-decoration: underline;
}

.jr-serialized-row__name--link:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-serialized-row__meta {
  margin: 0.15rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jr-serialized-row__aside {
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.35rem;
}

.jr-serialized-list__pager {
  margin-top: 0.25rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-serialized-list__pager :deep(.p-paginator),
.jr-serialized-list__pager :deep(.p-paginator-content) {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.5rem;
}

.jr-serialized-list__pager :deep(.p-paginator-prev),
.jr-serialized-list__pager :deep(.p-paginator-next) {
  min-width: 2.75rem;
  min-height: 2.75rem;
}

.jr-serialized-list__pager :deep(.p-paginator-current) {
  flex: 1 1 auto;
  min-width: 0;
  text-align: center;
  font-size: 0.8125rem;
  font-variant-numeric: tabular-nums;
  color: var(--color-jr-muted);
}

.jr-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.jr-serialized-list__table :deep(th.jr-col-actions),
.jr-serialized-list__table :deep(td.jr-col-actions) {
  width: 16.5rem;
  text-align: center;
  white-space: nowrap;
}

.jr-serialized-list__table :deep(th.jr-col-actions.jr-col-actions--compact),
.jr-serialized-list__table :deep(td.jr-col-actions.jr-col-actions--compact) {
  width: 3.25rem;
}

.jr-serialized-list__table
  :deep(th.jr-col-actions .p-datatable-column-header-content) {
  display: flex;
  justify-content: center;
  width: 100%;
}

.jr-serialized-list__table :deep(td.jr-col-actions .jr-row-actions) {
  justify-content: center;
  width: 100%;
}
</style>
