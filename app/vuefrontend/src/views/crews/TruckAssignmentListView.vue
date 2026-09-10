<template>
  <JRPage>
    <JRPageHeader title="Truck Assignments">
      <template #actions>
        <JRButton
          v-if="hasPermission('crewsapp.add_truckassignment')"
          type="button"
          @click="goToCreateForm">
          + New Truck Assignment
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-master-list__search">
          <label class="jr-sr-only" for="ta-filter-input">
            Search truck assignments
          </label>
          <span class="jr-master-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="ta-filter-input"
            v-model="filter"
            type="search"
            placeholder="Search by crew or truck..." />
        </div>
      </template>

      <template #stats>
        <div class="jr-master-list__summary" aria-live="polite">
          <JRBadge :value="`${stats.total} Total`" severity="secondary" />
        </div>
      </template>

      <template #actions>
        <label class="jr-sr-only" for="ta-per-page">Entries per page</label>
        <JRSelect
          class="jr-master-list__entries"
          inputId="ta-per-page"
          v-model="perPage"
          :options="pageOptions"
          optionLabel="label"
          optionValue="value" />
        <JRButton
          type="button"
          variant="ghost"
          size="sm"
          class="jr-master-list__refresh"
          @click="refreshTable">
          <RefreshIcon />
          Refresh
        </JRButton>
      </template>
    </JRToolbar>

    <div v-if="isMobile" class="jr-master-list__mobile">
      <JREmptyState
        v-if="!pagedItems.length && !isLoading"
        :title="emptyTitle"
        :description="emptyDescription">
        <JRButton
          v-if="loadError"
          type="button"
          variant="ghost"
          size="sm"
          @click="refreshTable">
          Refresh
        </JRButton>
        <JRButton
          v-else-if="hasSearch"
          type="button"
          variant="ghost"
          size="sm"
          @click="clearSearch">
          Clear search
        </JRButton>
      </JREmptyState>
      <p v-if="isLoading && !pagedItems.length" class="jr-master-list__loading">
        Loading truck assignments…
      </p>
      <p
        v-else-if="isLoading && pagedItems.length"
        class="jr-master-list__loading"
        aria-live="polite">
        Updating…
      </p>
      <ul
        v-if="pagedItems.length"
        class="jr-master-list__rows"
        :aria-busy="isLoading ? 'true' : 'false'">
        <li v-for="item in pagedItems" :key="item.id" class="jr-master-row">
          <div class="jr-master-row__main">
            <router-link
              v-if="canView"
              class="jr-master-row__name jr-master-row__name--link"
              :to="viewTo(item.id)"
              :aria-label="`View assignment for ${item.crew_name}`">
              {{ item.crew_name || "—" }}
            </router-link>
            <span v-else class="jr-master-row__name">{{
              item.crew_name || "—"
            }}</span>
            <p class="jr-master-row__meta">
              {{ item.trucks_display }}
              · Assigned {{ formatDate(item.assigned_at) }}
            </p>
          </div>
          <div class="jr-master-row__aside">
            <JRRowActions
              v-if="hasRowActions"
              :actions="getRowActions(item)"
              :compact="true"
              :entity-label="item.crew_name || `Assignment ${item.id}`" />
          </div>
        </li>
      </ul>
      <Paginator
        v-if="totalRows > 0"
        class="jr-master-list__pager"
        :rows="perPage"
        :totalRecords="totalRows"
        :first="tableFirst"
        template="PrevPageLink CurrentPageReport NextPageLink"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
        @page="onTablePage" />
    </div>

    <div v-else class="jr-master-list__table">
      <JRDataTable
        :value="pagedItems"
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
        tableStyle="min-width: 48rem"
        :emptyTitle="isLoading ? '' : emptyTitle"
        :emptyDescription="isLoading ? '' : emptyDescription"
        @page="onTablePage"
        @sort="onTableSort">
        <template #empty>
          <JREmptyState
            v-if="!isLoading"
            :title="emptyTitle"
            :description="emptyDescription">
            <JRButton
              v-if="loadError"
              type="button"
              variant="ghost"
              size="sm"
              @click="refreshTable">
              Refresh
            </JRButton>
            <JRButton
              v-else-if="hasSearch"
              type="button"
              variant="ghost"
              size="sm"
              @click="clearSearch">
              Clear search
            </JRButton>
          </JREmptyState>
        </template>
        <Column field="id" header="ID" sortable style="width: 4.5rem" />
        <Column field="crew_name" header="Assigned Crew" sortable>
          <template #body="{ data }">
            <router-link
              v-if="canView"
              class="jr-master-row__name jr-master-row__name--link"
              :to="viewTo(data.id)"
              :aria-label="`View assignment for ${data.crew_name}`">
              {{ data.crew_name || "—" }}
            </router-link>
            <span v-else>{{ data.crew_name || "—" }}</span>
          </template>
        </Column>
        <Column field="trucks_display" header="Assigned Trucks" sortable>
          <template #body="{ data }">
            {{ data.trucks_display }}
          </template>
        </Column>
        <Column field="assigned_at" header="Assigned At" sortable>
          <template #body="{ data }">
            {{ formatDate(data.assigned_at) }}
          </template>
        </Column>
        <Column field="unassigned_at" header="Unassigned At" sortable>
          <template #body="{ data }">
            {{
              data.unassigned_at ? formatDate(data.unassigned_at) : "—"
            }}
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
              :entity-label="data.crew_name || `Assignment ${data.id}`" />
          </template>
        </Column>
      </JRDataTable>
    </div>
  </JRPage>
</template>

<script setup>
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

const ENDPOINT = "/api/truck-assignments/";
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

function formatDate(val) {
  if (!val) return "—";
  const d = new Date(val);
  return isNaN(d.getTime()) ? val : d.toLocaleString();
}

function trucksDisplayText(item) {
  if (Array.isArray(item.trucks_display)) {
    return item.trucks_display.join(", ") || "—";
  }
  return item.trucks_display || "—";
}

function compareValues(a, b, field) {
  if (field === "assigned_at" || field === "unassigned_at") {
    const at = new Date(a?.[field] || 0).getTime();
    const bt = new Date(b?.[field] || 0).getTime();
    return at - bt;
  }
  if (field === "trucks_display") {
    const as = trucksDisplayText(a).toLowerCase();
    const bs = trucksDisplayText(b).toLowerCase();
    if (as < bs) return -1;
    if (as > bs) return 1;
    return 0;
  }
  const av = a?.[field];
  const bv = b?.[field];
  if (typeof av === "number" || typeof bv === "number") {
    return Number(av ?? 0) - Number(bv ?? 0);
  }
  const as = (av ?? "").toString().toLowerCase();
  const bs = (bv ?? "").toString().toLowerCase();
  if (as < bs) return -1;
  if (as > bs) return 1;
  return 0;
}

const router = useRouter();
const { proxy } = getCurrentInstance();

const items = ref([]);
const isLoading = ref(true);
const loadError = ref(false);
const currentPage = ref(1);
const perPage = ref(25);
const filter = ref("");
const sortField = ref("crew_name");
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

const filteredItems = computed(() => {
  const q = (filter.value || "").toLowerCase().trim();
  let list = items.value;
  if (q) {
    list = list.filter((item) => {
      const trucksStr = Array.isArray(item.trucks_display)
        ? item.trucks_display.join(" ").toLowerCase()
        : (item.trucks_display || "").toLowerCase();
      return (
        (item.crew_name || "").toLowerCase().includes(q) ||
        trucksStr.includes(q)
      );
    });
  }

  const formatted = list.map((item) => ({
    ...item,
    trucks_display: trucksDisplayText(item),
  }));

  const field = sortField.value || "crew_name";
  const order = sortOrder.value === -1 ? -1 : 1;

  // Default: crew A→Z, then assigned_at newest first (legacy behavior)
  if (!sortField.value || sortField.value === "crew_name") {
    return [...formatted].sort((a, b) => {
      const crewCmp = compareValues(a, b, "crew_name") * order;
      if (crewCmp !== 0) return crewCmp;
      return (
        new Date(b.assigned_at || 0).getTime() -
        new Date(a.assigned_at || 0).getTime()
      );
    });
  }

  return [...formatted].sort((a, b) => compareValues(a, b, field) * order);
});

const stats = computed(() => ({ total: filteredItems.value.length }));
const totalRows = computed(() => filteredItems.value.length);
const tableFirst = computed(() => (currentPage.value - 1) * perPage.value);
const pagedItems = computed(() => {
  const start = tableFirst.value;
  return filteredItems.value.slice(start, start + perPage.value);
});

const hasSearch = computed(() => Boolean(filter.value && filter.value.trim()));
const emptyTitle = computed(() => {
  if (loadError.value) return "Could not load truck assignments";
  if (hasSearch.value) return "No matching truck assignments";
  return "No truck assignments";
});
const emptyDescription = computed(() => {
  if (loadError.value) return "Try Refresh.";
  const query = filter.value.trim();
  if (query) return `No truck assignments match “${query}”.`;
  return "No truck assignments yet.";
});

const clearSearch = () => {
  filter.value = "";
  if (typeof document !== "undefined") {
    document.getElementById("ta-filter-input")?.focus();
  }
};

const canView = computed(() =>
  !!proxy?.hasPermission?.("crewsapp.view_truckassignment")
);
const hasRowActions = computed(
  () =>
    canView.value ||
    !!proxy?.hasPermission?.("crewsapp.change_truckassignment") ||
    !!proxy?.hasPermission?.("crewsapp.delete_truckassignment")
);

const loadItems = async () => {
  if (!isLoading.value) isLoading.value = true;
  try {
    const response = await axios.get(ENDPOINT);
    items.value = response.data.results ?? response.data;
    if (!Array.isArray(items.value)) items.value = [];
    loadError.value = false;
    const maxPage = Math.max(
      1,
      Math.ceil(items.value.length / perPage.value) || 1
    );
    if (currentPage.value > maxPage) currentPage.value = maxPage;
  } catch (error) {
    console.error("Error fetching truck assignments", error);
    loadError.value = true;
    items.value = [];
    proxy?.notifyError?.("Error loading truck assignments.");
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
};

const onTableSort = (event) => {
  sortField.value = event.sortField || "crew_name";
  sortOrder.value = event.sortOrder ?? 1;
  currentPage.value = 1;
};

const refreshTable = () => {
  isLoading.value = true;
  loadItems();
};

const viewTo = (id) => `/crews/truck-assignments/view/${id}`;
const editTo = (id) => `/crews/truck-assignments/edit/${id}`;
const goToCreateForm = () => router.push("/crews/truck-assignments/form");
const viewItem = (id) => router.push(viewTo(id));
const editItem = (id) => router.push(editTo(id));

const getRowActions = (item) => {
  const actions = [];
  if (proxy?.hasPermission?.("crewsapp.view_truckassignment")) {
    actions.push({
      key: "view",
      label: "View",
      severity: "success",
      icon: EyeIcon,
      command: () => viewItem(item.id),
    });
  }
  if (proxy?.hasPermission?.("crewsapp.change_truckassignment")) {
    actions.push({
      key: "edit",
      label: "Edit",
      severity: "primary",
      icon: PencilIcon,
      command: () => editItem(item.id),
    });
  }
  if (proxy?.hasPermission?.("crewsapp.delete_truckassignment")) {
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
    "This action cannot be undone.",
    async () => {
      try {
        await axios.delete(`${ENDPOINT}${id}/`);
        items.value = items.value.filter((item) => item.id !== id);
        proxy?.notifyToastSuccess?.("Truck assignment has been deleted.");
      } catch (err) {
        console.error("Error deleting truck assignment", err);
        proxy?.notifyError?.("Error deleting truck assignment.");
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
});

watch(filter, () => {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    currentPage.value = 1;
  }, 300);
});

watch(filteredItems, (list) => {
  const maxPage = Math.max(1, Math.ceil(list.length / perPage.value) || 1);
  if (currentPage.value > maxPage) currentPage.value = maxPage;
});
</script>

<style scoped>
.jr-master-list__search {
  position: relative;
  min-width: 0;
  width: 100%;
}

.jr-master-list__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-master-list__search-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.jr-master-list__search :deep(.p-inputtext) {
  padding-left: 2.25rem;
}

.jr-master-list__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  pointer-events: none;
}

:deep(.jr-toolbar__actions .jr-master-list__entries.p-select),
:deep(.jr-toolbar__actions .jr-master-list__entries.jr-control) {
  width: 4.75rem;
  flex: 0 0 auto;
}

.jr-master-list__loading {
  margin: 0;
  padding: 1rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-master-list__rows {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: 1px solid var(--color-jr-border);
}

.jr-master-list__rows[aria-busy="true"] {
  opacity: 0.55;
}

.jr-master-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-master-row__main {
  min-width: 0;
  flex: 1 1 auto;
  text-align: left;
}

.jr-master-row__name {
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-master-row__name--link {
  color: var(--color-jr-primary);
  text-decoration: none;
}

.jr-master-row__name--link:hover {
  text-decoration: underline;
}

.jr-master-row__name--link:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-master-row__meta {
  margin: 0.15rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jr-master-row__aside {
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.35rem;
}

.jr-master-list__pager {
  margin-top: 0.25rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-master-list__pager :deep(.p-paginator),
.jr-master-list__pager :deep(.p-paginator-content) {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.5rem;
}

.jr-master-list__pager :deep(.p-paginator-prev),
.jr-master-list__pager :deep(.p-paginator-next) {
  min-width: 2.75rem;
  min-height: 2.75rem;
}

.jr-master-list__pager :deep(.p-paginator-current) {
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

.jr-master-list__table :deep(th.jr-col-actions),
.jr-master-list__table :deep(td.jr-col-actions) {
  width: 16.5rem;
  text-align: center;
  white-space: nowrap;
}

.jr-master-list__table :deep(th.jr-col-actions.jr-col-actions--compact),
.jr-master-list__table :deep(td.jr-col-actions.jr-col-actions--compact) {
  width: 3.25rem;
}

.jr-master-list__table
  :deep(th.jr-col-actions .p-datatable-column-header-content) {
  display: flex;
  justify-content: center;
  width: 100%;
}

.jr-master-list__table :deep(td.jr-col-actions .jr-row-actions) {
  justify-content: center;
  width: 100%;
}
</style>
