<template>
  <JRPage>
    <JRPageHeader title="Inventory Transfers">
      <template #actions>
        <JRButton
          v-if="hasPermission('appinventory.add_inventorytransfer')"
          type="button"
          :fluid="isMobile"
          @click="goToCreateForm">
          + New Inventory Transfer
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-transfer-list__search">
          <label class="jr-sr-only" for="transfer-filter-input">
            Search inventory transfers
          </label>
          <span class="jr-transfer-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="transfer-filter-input"
            v-model="filter"
            type="search"
            placeholder="Search by description, warehouses, crew…" />
        </div>
      </template>

      <template #stats>
        <div class="jr-transfer-list__summary" aria-live="polite">
          <JRBadge :value="`${totalRows} Total`" severity="secondary" />
        </div>
      </template>

      <template #actions>
        <label class="jr-sr-only" for="transfer-per-page">
          Entries per page
        </label>
        <JRSelect
          class="jr-transfer-list__entries"
          inputId="transfer-per-page"
          v-model="perPage"
          :options="pageOptions"
          optionLabel="label"
          optionValue="value" />
        <JRButton
          type="button"
          variant="ghost"
          size="sm"
          class="jr-transfer-list__refresh"
          @click="refreshTable">
          <RefreshIcon />
          Refresh
        </JRButton>
      </template>
    </JRToolbar>

    <div v-if="isMobile" class="jr-transfer-list__mobile">
      <JREmptyState
        v-if="!items.length && !isLoading"
        :title="emptyTitle"
        :description="emptyDescription" />
      <p v-if="isLoading && !items.length" class="jr-transfer-list__loading">
        Loading inventory transfers…
      </p>
      <p
        v-else-if="isLoading && items.length"
        class="jr-transfer-list__loading"
        aria-live="polite">
        Updating…
      </p>
      <ul
        v-if="items.length"
        class="jr-transfer-list__rows"
        :aria-busy="isLoading ? 'true' : 'false'">
        <li v-for="item in items" :key="item.id" class="jr-transfer-row">
          <div class="jr-transfer-row__main">
            <router-link
              v-if="canView"
              class="jr-transfer-row__name jr-transfer-row__name--link"
              :to="viewTo(item.id)"
              :aria-label="`View ${primaryLabel(item)}`">
              {{ primaryLabel(item) }}
            </router-link>
            <span v-else class="jr-transfer-row__name">
              {{ primaryLabel(item) }}
            </span>
            <p class="jr-transfer-row__meta">
              <span>{{ routeSummary(item) }}</span>
              <span v-if="item.truck_crew_name" aria-hidden="true">·</span>
              <span v-if="item.truck_crew_name">{{ item.truck_crew_name }}</span>
            </p>
          </div>
          <div class="jr-transfer-row__aside">
            <JRBadge
              v-if="item.status"
              :value="item.status"
              :severity="statusSeverity(item.status)" />
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
        class="jr-transfer-list__pager"
        :rows="perPage"
        :totalRecords="totalRows"
        :first="tableFirst"
        template="PrevPageLink CurrentPageReport NextPageLink"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
        @page="onTablePage" />
    </div>

    <div v-else class="jr-transfer-list__table">
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
        <Column field="description" header="Description" sortable>
          <template #body="{ data }">
            <router-link
              v-if="canView"
              class="jr-transfer-row__name jr-transfer-row__name--link"
              :to="viewTo(data.id)"
              :aria-label="`View ${primaryLabel(data)}`">
              {{ primaryLabel(data) }}
            </router-link>
            <span v-else>{{ primaryLabel(data) }}</span>
          </template>
        </Column>
        <Column field="from_warehouse_name" header="From" sortable>
          <template #body="{ data }">
            {{ data.from_warehouse_name || "—" }}
          </template>
        </Column>
        <Column field="to_warehouse_name" header="To" sortable>
          <template #body="{ data }">
            {{ data.to_warehouse_name || "—" }}
          </template>
        </Column>
        <Column
          v-if="!isTablet"
          field="truck_crew_name"
          header="Truck Crew"
          :sortable="false">
          <template #body="{ data }">
            {{ data.truck_crew_name || "—" }}
          </template>
        </Column>
        <Column field="status" header="Status" :sortable="false">
          <template #body="{ data }">
            <JRBadge
              v-if="data.status"
              :value="data.status"
              :severity="statusSeverity(data.status)" />
            <span v-else class="jr-transfer-list__muted">—</span>
          </template>
        </Column>
        <Column field="created_at" header="Created" sortable>
          <template #body="{ data }">
            {{ formatDateTime(data.created_at) }}
          </template>
        </Column>
        <Column
          v-if="!isTablet"
          field="last_updated"
          header="Updated"
          :sortable="false">
          <template #body="{ data }">
            {{ formatDateTime(data.last_updated) }}
          </template>
        </Column>
        <Column
          v-if="!isTablet"
          field="created_by_username"
          header="Created By"
          :sortable="false">
          <template #body="{ data }">
            {{ data.created_by_username || "—" }}
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

const ENDPOINT = "/api/inventory-transfers-provider/";
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
  name: "InventoryTransferListView",
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
    const sortField = ref("created_at");
    const sortOrder = ref(-1);
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
      loadError.value
        ? "Could not load inventory transfers"
        : "No inventory transfers"
    );
    const emptyDescription = computed(() =>
      loadError.value
        ? "Try Refresh."
        : "No inventory transfers match the current search."
    );

    const canView = computed(() =>
      !!proxy?.hasPermission?.("appinventory.view_inventorytransfer")
    );
    const hasRowActions = computed(
      () =>
        canView.value ||
        !!proxy?.hasPermission?.("appinventory.change_inventorytransfer") ||
        !!proxy?.hasPermission?.("appinventory.delete_inventorytransfer")
    );

    const routeSummary = (item) => {
      const from = item?.from_warehouse_name || "—";
      const to = item?.to_warehouse_name || "—";
      return `${from} → ${to}`;
    };

    const primaryLabel = (item) => {
      const desc = (item?.description || "").trim();
      if (desc) return desc;
      return routeSummary(item);
    };

    const statusSeverity = (status) => {
      if (!status) return "secondary";
      const s = String(status).toLowerCase();
      if (s === "completed") return "success";
      if (s === "reverted") return "danger";
      return "secondary";
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
      if (!sortBy) return "-created_at";
      let field;
      let desc = false;
      if (sortBy.sortField) {
        field = sortBy.sortField;
        desc = sortBy.sortOrder === -1;
      } else if (Array.isArray(sortBy) && sortBy.length > 0) {
        const first = sortBy[0];
        field = first.key ?? first.field;
        const order = first.order ?? (first.sortDesc ? "desc" : "asc");
        desc = order === "desc";
      } else if (typeof sortBy === "object" && !Array.isArray(sortBy)) {
        field = Object.keys(sortBy)[0];
        desc = sortBy[field] === "desc";
      }
      if (!field) return "-created_at";
      // Backend allowlist: id, created_at, description,
      // from_warehouse__name, to_warehouse__name
      // (see InventoryTransferListProviderAPIView).
      const fieldMap = {
        id: "id",
        created_at: "created_at",
        description: "description",
        from_warehouse_name: "from_warehouse__name",
        to_warehouse_name: "to_warehouse__name",
      };
      const djangoField = fieldMap[field];
      if (!djangoField) return "-created_at";
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
        if (response.data?.items) {
          totalRows.value = response.data.totalRows ?? 0;
          items.value = response.data.items;
          loadError.value = false;
        } else {
          throw new Error("Invalid response format");
        }
      } catch (error) {
        console.error("InventoryTransfer provider error:", error);
        loadError.value = true;
        items.value = [];
        totalRows.value = 0;
        proxy?.notifyToastError?.("Error loading inventory transfers.");
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
      sortField.value = event.sortField || "created_at";
      sortOrder.value = event.sortOrder ?? -1;
      currentPage.value = 1;
      loadItems();
    };

    const refreshTable = () => {
      isLoading.value = true;
      loadItems();
    };

    const viewTo = (id) => ({
      name: "inventory-transfer-view",
      params: { id },
    });
    const goToCreateForm = () =>
      router.push({ name: "inventory-transfer-form" });
    const viewItem = (id) => router.push(viewTo(id));
    const editItem = (id) =>
      router.push({ name: "inventory-transfer-edit", params: { id } });

    const getRowActions = (item) => {
      const actions = [];
      if (proxy?.hasPermission?.("appinventory.view_inventorytransfer")) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => viewItem(item.id),
        });
      }
      if (
        proxy?.hasPermission?.("appinventory.change_inventorytransfer") &&
        item.status !== "reverted"
      ) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => editItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("appinventory.delete_inventorytransfer")) {
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
        "Delete this inventory transfer? This action cannot be undone.",
        async () => {
          try {
            await axios.delete(`/api/inventory-transfers/${id}/`);
            proxy?.notifyToastSuccess?.("Transfer deleted.");
            refreshTable();
          } catch (error) {
            const data = error?.response?.data;
            proxy?.notifyToastError?.(
              data?.detail || "Error deleting transfer."
            );
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
      items,
      isLoading,
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
      routeSummary,
      statusSeverity,
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
.jr-transfer-list__search {
  position: relative;
  min-width: 0;
  width: 100%;
}

.jr-transfer-list__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-transfer-list__search-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.jr-transfer-list__search :deep(.p-inputtext) {
  padding-left: 2.25rem;
}

.jr-transfer-list__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  pointer-events: none;
}

:deep(.jr-toolbar__actions .jr-transfer-list__entries.p-select),
:deep(.jr-toolbar__actions .jr-transfer-list__entries.jr-control) {
  width: 4.75rem;
  flex: 0 0 auto;
}

.jr-transfer-list__loading,
.jr-transfer-list__muted {
  color: var(--color-jr-muted);
}

.jr-transfer-list__loading {
  margin: 0;
  padding: 1rem 0;
  font-size: 0.875rem;
}

.jr-transfer-list__rows {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: 1px solid var(--color-jr-border);
}

.jr-transfer-list__rows[aria-busy="true"] {
  opacity: 0.55;
}

.jr-transfer-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-transfer-row__main {
  min-width: 0;
  flex: 1 1 auto;
  text-align: left;
}

.jr-transfer-row__name {
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-transfer-row__name--link {
  color: var(--color-jr-primary);
  text-decoration: none;
}

.jr-transfer-row__name--link:hover {
  text-decoration: underline;
}

.jr-transfer-row__name--link:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-transfer-row__meta {
  margin: 0.15rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jr-transfer-row__aside {
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.35rem;
}

.jr-transfer-list__pager {
  margin-top: 0.25rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-transfer-list__pager :deep(.p-paginator),
.jr-transfer-list__pager :deep(.p-paginator-content) {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.5rem;
}

.jr-transfer-list__pager :deep(.p-paginator-prev),
.jr-transfer-list__pager :deep(.p-paginator-next) {
  min-width: 2.75rem;
  min-height: 2.75rem;
}

.jr-transfer-list__pager :deep(.p-paginator-current) {
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

.jr-transfer-list__table :deep(th.jr-col-actions),
.jr-transfer-list__table :deep(td.jr-col-actions) {
  width: 16.5rem;
  text-align: center;
  white-space: nowrap;
}

.jr-transfer-list__table :deep(th.jr-col-actions.jr-col-actions--compact),
.jr-transfer-list__table :deep(td.jr-col-actions.jr-col-actions--compact) {
  width: 3.25rem;
}

.jr-transfer-list__table
  :deep(th.jr-col-actions .p-datatable-column-header-content) {
  display: flex;
  justify-content: center;
  width: 100%;
}

.jr-transfer-list__table :deep(td.jr-col-actions .jr-row-actions) {
  justify-content: center;
  width: 100%;
}
</style>
