<template>
  <JRPage>
    <JRPageHeader title="Material Requests" />

    <JRToolbar>
      <template #start>
        <div class="jr-master-list__search">
          <label class="jr-sr-only" for="mr-filter-input">Search material requests</label>
          <span class="jr-master-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="mr-filter-input"
            v-model="filter"
            type="search"
            placeholder="Search by number, work account, or requester..." />
        </div>
      </template>

      <template #stats>
        <div class="jr-master-list__summary" aria-live="polite">
          <JRBadge :value="`${stats.total} Total`" severity="secondary" />
          <JRBadge
            :value="`${stats.open} Open`"
            :severity="stats.open > 0 ? 'info' : 'secondary'" />
          <JRBadge
            :value="`${stats.closed} Closed`"
            :severity="stats.closed > 0 ? 'success' : 'secondary'" />
        </div>
      </template>

      <template #actions>
        <label class="jr-sr-only" for="mr-status-filter">Status</label>
        <JRSelect
          inputId="mr-status-filter"
          ariaLabel="Status"
          v-model="status"
          :options="statusOptions"
          optionLabel="label"
          optionValue="value" />
        <label class="jr-sr-only" for="mr-per-page">Entries per page</label>
        <JRSelect
          class="jr-master-list__entries"
          inputId="mr-per-page"
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
        v-if="!rows.length && !isLoading"
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
      <p v-if="isLoading && !rows.length" class="jr-master-list__loading">
        Loading material requests…
      </p>
      <ul
        v-if="rows.length"
        class="jr-master-list__rows"
        :aria-busy="isLoading ? 'true' : 'false'">
        <li v-for="item in rows" :key="item.id" class="jr-master-row">
          <div class="jr-master-row__main">
            <router-link
              v-if="canView"
              class="jr-master-row__name jr-master-row__name--link"
              :to="viewTo(item.id)"
              :aria-label="`View ${item.document_number}`">
              {{ item.document_number }}
            </router-link>
            <span v-else class="jr-master-row__name">{{ item.document_number }}</span>
            <p class="jr-master-row__meta">
              {{ item.work_account_title || '—' }}
              <span v-if="item.phase"> · {{ item.phase }}</span>
            </p>
            <p class="jr-master-row__meta">
              <JRBadge :value="item.status_name || '—'" :severity="statusSeverity(item.status)" />
            </p>
          </div>
          <div class="jr-master-row__aside">
            <JRRowActions
              v-if="hasRowActions"
              :actions="getRowActions(item)"
              :compact="true"
              :entity-label="item.document_number" />
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
        :value="rows"
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
        <Column field="document_number" header="Number" sortable>
          <template #body="{ data }">
            <router-link
              v-if="canView"
              class="jr-master-row__name jr-master-row__name--link"
              :to="viewTo(data.id)"
              :aria-label="`View ${data.document_number}`">
              {{ data.document_number }}
            </router-link>
            <span v-else>{{ data.document_number }}</span>
          </template>
        </Column>
        <Column field="work_account_title" header="Work account" sortable />
        <Column v-if="!isTablet" field="phase" header="Phase" sortable />
        <Column v-if="!isTablet" field="requested_by" header="Requested by" sortable />
        <Column field="status_name" header="Status" sortable>
          <template #body="{ data }">
            <JRBadge :value="data.status_name || '—'" :severity="statusSeverity(data.status)" />
          </template>
        </Column>
        <Column field="date" header="Date" sortable />
        <Column
          v-if="hasRowActions"
          header="Actions"
          :sortable="false"
          :headerClass="isTablet ? 'jr-col-actions jr-col-actions--compact' : 'jr-col-actions'"
          :bodyClass="isTablet ? 'jr-col-actions jr-col-actions--compact' : 'jr-col-actions'">
          <template #body="{ data }">
            <JRRowActions
              :actions="getRowActions(data)"
              :compact="isTablet"
              :entity-label="data.document_number" />
          </template>
        </Column>
      </JRDataTable>
    </div>
  </JRPage>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, getCurrentInstance } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
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

const ENDPOINT = "/api/material-requests/";
const PHONE_MQ = "(max-width: 767.98px)";
const TABLET_MQ = "(min-width: 768px) and (max-width: 1023.98px)";

const router = useRouter();
const { proxy } = getCurrentInstance();

const rows = ref([]);
const totalRows = ref(0);
const stats = ref({ total: 0, open: 0, closed: 0 });
const isLoading = ref(false);
const loadError = ref(false);
const filter = ref("");
const status = ref("");
const perPage = ref(10);
const currentPage = ref(1);
const sortField = ref("document_number");
const sortOrder = ref(-1);
const isMobile = ref(false);
const isTablet = ref(false);

const statusOptions = [
  { label: "All statuses", value: "" },
  { label: "Requested", value: "requested" },
  { label: "Approved", value: "approved" },
  { label: "Preparing", value: "preparing" },
  { label: "Delivered", value: "delivered" },
  { label: "Closed", value: "closed" },
];
const pageOptions = [
  { label: "10", value: 10 },
  { label: "25", value: 25 },
  { label: "50", value: 50 },
];

let phoneQuery;
let tabletQuery;
let onViewport = () => {};
let searchTimer = null;

function readViewport() {
  if (typeof window === "undefined" || !window.matchMedia) {
    return { isMobile: false, isTablet: false };
  }
  return {
    isMobile: window.matchMedia(PHONE_MQ).matches,
    isTablet: window.matchMedia(TABLET_MQ).matches,
  };
}

const canView = computed(() => !!proxy?.hasPermission?.("apptransactions.view_document"));
const hasRowActions = computed(
  () =>
    canView.value ||
    !!proxy?.hasPermission?.("apptransactions.change_document") ||
    !!proxy?.hasPermission?.("apptransactions.delete_document")
);
const hasSearch = computed(() => !!filter.value.trim());

function statusSeverity(code) {
  if (code === "delivered") return "success";
  if (code === "preparing") return "warning";
  if (code === "closed") return "secondary";
  return "info";
}

const tableFirst = computed(() => (currentPage.value - 1) * perPage.value);
const tableMinWidth = computed(() => (isTablet.value ? "min-width: 40rem" : "min-width: 56rem"));

const emptyTitle = computed(() => {
  if (loadError.value) return "Could not load material requests";
  if (hasSearch.value || status.value) return "No matching material requests";
  return "No material requests";
});
const emptyDescription = computed(() => {
  if (loadError.value) return "Try Refresh.";
  if (hasSearch.value) return `No material requests match “${filter.value.trim()}”.`;
  if (status.value) return "No material requests with this status.";
  return "Requests submitted from a work order show up here.";
});

watch(status, () => {
  currentPage.value = 1;
  load();
});
watch(perPage, () => {
  currentPage.value = 1;
  load();
});
watch(filter, () => {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    currentPage.value = 1;
    load();
  }, 300);
});

function viewTo(id) {
  return { name: "material-request-detail", params: { id: String(id) } };
}
function editTo(id) {
  return {
    name: "material-request-detail",
    params: { id: String(id) },
    query: { mode: "edit" },
  };
}

function getRowActions(item) {
  const actions = [];
  if (proxy?.hasPermission?.("apptransactions.view_document")) {
    actions.push({
      key: "view",
      label: "View",
      severity: "success",
      icon: EyeIcon,
      command: () => router.push(viewTo(item.id)),
    });
  }
  if (proxy?.hasPermission?.("apptransactions.change_document")) {
    actions.push({
      key: "edit",
      label: "Edit",
      severity: "primary",
      icon: PencilIcon,
      command: () => router.push(editTo(item.id)),
    });
  }
  if (
    proxy?.hasPermission?.("apptransactions.delete_document") &&
    item.status !== "closed"
  ) {
    actions.push({
      key: "delete",
      label: "Delete",
      severity: "danger",
      icon: TrashIcon,
      command: () => deleteRequest(item),
    });
  }
  return actions;
}

function deleteRequest(item) {
  proxy?.confirmDelete?.(
    "Delete this material request?",
    "This action cannot be undone.",
    async () => {
      try {
        await axios.delete(`${ENDPOINT}${item.id}/`);
        proxy?.notifyToastSuccess?.("Material request deleted.");
        load();
      } catch (err) {
        const data = err?.response?.data;
        const detail = data?.status || data?.detail || data?.non_field_errors;
        const message = Array.isArray(detail) ? detail.join(" ") : detail;
        proxy?.notifyError?.(message || "Could not delete the material request.");
      }
    }
  );
}

function orderingParam() {
  const field = sortField.value || "id";
  return sortOrder.value === -1 ? `-${field}` : field;
}

async function load() {
  isLoading.value = true;
  try {
    const { data } = await axios.get(ENDPOINT, {
      params: {
        page: currentPage.value,
        per_page: perPage.value,
        search: filter.value.trim(),
        ordering: orderingParam(),
        status: status.value || undefined,
      },
    });
    rows.value = Array.isArray(data?.items) ? data.items : [];
    totalRows.value = data?.totalRows || 0;
    stats.value = data?.stats || { total: 0, open: 0, closed: 0 };
    loadError.value = false;
  } catch {
    rows.value = [];
    totalRows.value = 0;
    stats.value = { total: 0, open: 0, closed: 0 };
    loadError.value = true;
    proxy?.notifyError?.("Error loading material requests.");
  } finally {
    isLoading.value = false;
  }
}

function refreshTable() {
  load();
}
function clearSearch() {
  filter.value = "";
}
function onTablePage(event) {
  currentPage.value = (event.page ?? 0) + 1;
  if (event.rows && event.rows !== perPage.value) perPage.value = event.rows;
  load();
}
function onTableSort(event) {
  sortField.value = event.sortField || "id";
  sortOrder.value = event.sortOrder ?? -1;
  currentPage.value = 1;
  load();
}

onMounted(() => {
  const viewport = readViewport();
  isMobile.value = viewport.isMobile;
  isTablet.value = viewport.isTablet;
  if (typeof window !== "undefined" && window.matchMedia) {
    phoneQuery = window.matchMedia(PHONE_MQ);
    tabletQuery = window.matchMedia(TABLET_MQ);
    onViewport = () => {
      const next = readViewport();
      isMobile.value = next.isMobile;
      isTablet.value = next.isTablet;
    };
    if (phoneQuery.addEventListener) {
      phoneQuery.addEventListener("change", onViewport);
      tabletQuery.addEventListener("change", onViewport);
    }
  }
  load();
});

onUnmounted(() => {
  if (phoneQuery?.removeEventListener) {
    phoneQuery.removeEventListener("change", onViewport);
    tabletQuery.removeEventListener("change", onViewport);
  }
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
  width: 6.25rem;
  min-width: 6.25rem;
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
}
.jr-master-row__aside {
  display: flex;
  flex-shrink: 0;
  align-items: flex-end;
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
.jr-master-list__table :deep(th.jr-col-actions .p-datatable-column-header-content) {
  display: flex;
  justify-content: center;
  width: 100%;
}
.jr-master-list__table :deep(td.jr-col-actions .jr-row-actions) {
  justify-content: center;
  width: 100%;
}
</style>
