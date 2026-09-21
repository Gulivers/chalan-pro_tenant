<template>
  <JRPage>
    <JRPageHeader title="Communities">
      <template #actions>
        <JRButton
          v-if="hasPermission('ctrctsapp.add_job')"
          type="button"
          @click="goToCreateForm">
          + New Community
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-master-list__search">
          <label class="jr-sr-only" for="job-filter-input">
            Search communities
          </label>
          <span class="jr-master-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="job-filter-input"
            v-model="filter"
            type="search"
            placeholder="Search by name, address, builder..." />
        </div>
      </template>

      <template #stats>
        <div class="jr-master-list__summary" aria-live="polite">
          <JRBadge :value="`${stats.total} Total`" severity="secondary" />
        </div>
      </template>

      <template #actions>
        <label class="jr-sr-only" for="job-per-page">
          Entries per page
        </label>
        <JRSelect
          class="jr-master-list__entries"
          inputId="job-per-page"
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
        Loading communities…
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
              :aria-label="`View ${item.name}`">
              {{ item.name }}
            </router-link>
            <span v-else class="jr-master-row__name">{{ item.name }}</span>
            <p class="jr-master-row__meta">
              {{ mobileMeta(item) }}
            </p>
          </div>
          <div class="jr-master-row__aside">
            <JRRowActions
              v-if="hasRowActions"
              :actions="getRowActions(item)"
              :compact="true"
              :entity-label="item.name" />
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
        <Column field="id" header="ID" sortable>
          <template #body="{ data }">
            {{ data.id }}
          </template>
        </Column>
        <Column field="name" header="Community" sortable>
          <template #body="{ data }">
            <router-link
              v-if="canView"
              class="jr-master-row__name jr-master-row__name--link"
              :to="viewTo(data.id)"
              :aria-label="`View ${data.name}`">
              {{ data.name }}
            </router-link>
            <span v-else>{{ data.name }}</span>
          </template>
        </Column>
        <Column field="builder" header="Builder" sortable>
          <template #body="{ data }">
            {{ builderLabel(data) }}
          </template>
        </Column>
        <Column field="address" header="Address" sortable>
          <template #body="{ data }">
            {{ data.address || "—" }}
          </template>
        </Column>
        <Column
          field="latitude"
          header="Latitude"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            {{ formatCoord(data.latitude) }}
          </template>
        </Column>
        <Column
          field="longitude"
          header="Longitude"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            {{ formatCoord(data.longitude) }}
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
              :entity-label="data.name" />
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

const ENDPOINT = "/api/job/";
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

function normalizeList(data) {
  return Array.isArray(data) ? data : data?.results ?? [];
}

function builderLabel(item) {
  return item?.builder?.name || "—";
}

function builderSortValue(item) {
  return item?.builder?.name || "";
}

function compareValues(a, b, field) {
  let av = a?.[field];
  let bv = b?.[field];
  if (field === "builder") {
    av = builderSortValue(a);
    bv = builderSortValue(b);
  }
  if (typeof av === "number" || typeof bv === "number") {
    return Number(av || 0) - Number(bv || 0);
  }
  const as = (av ?? "").toString().toLowerCase();
  const bs = (bv ?? "").toString().toLowerCase();
  if (as < bs) return -1;
  if (as > bs) return 1;
  return 0;
}

export default {
  name: "JobView",
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

    const jobs = ref([]);
    const isLoading = ref(true);
    const loadError = ref(false);
    const currentPage = ref(1);
    const perPage = ref(25);
    const filter = ref("");
    const sortField = ref("name");
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
      let list = jobs.value;
      if (q) {
        list = list.filter((item) => {
          const hay = [item.name, item.address, item.builder?.name].map((v) =>
            (v || "").toString().toLowerCase()
          );
          return hay.some((t) => t.includes(q));
        });
      }
      const field = sortField.value || "name";
      const order = sortOrder.value === -1 ? -1 : 1;
      return [...list].sort((a, b) => compareValues(a, b, field) * order);
    });

    const stats = computed(() => ({ total: filteredItems.value.length }));

    const totalRows = computed(() => filteredItems.value.length);
    const tableFirst = computed(() => (currentPage.value - 1) * perPage.value);
    const pagedItems = computed(() => {
      const start = tableFirst.value;
      return filteredItems.value.slice(start, start + perPage.value);
    });

    const tableMinWidth = computed(() =>
      isTablet.value ? "min-width: 36rem" : "min-width: 48rem"
    );
    const hasSearch = computed(() =>
      Boolean(filter.value && filter.value.trim())
    );
    const emptyTitle = computed(() => {
      if (loadError.value) return "Could not load communities";
      if (hasSearch.value) return "No matching communities";
      return "No communities";
    });
    const emptyDescription = computed(() => {
      if (loadError.value) return "Try Refresh.";
      const query = filter.value.trim();
      if (query) return `No communities match “${query}”.`;
      return "No communities yet.";
    });

    const clearSearch = () => {
      filter.value = "";
      if (typeof document !== "undefined") {
        document.getElementById("job-filter-input")?.focus();
      }
    };

    const canView = computed(() =>
      !!proxy?.hasPermission?.("ctrctsapp.view_job")
    );
    const hasRowActions = computed(
      () =>
        canView.value ||
        !!proxy?.hasPermission?.("ctrctsapp.change_job") ||
        !!proxy?.hasPermission?.("ctrctsapp.delete_job")
    );

    const formatCoord = (value) => {
      if (value === null || value === undefined || value === "") return "—";
      return value;
    };

    const mobileMeta = (item) => {
      const parts = [builderLabel(item), item.address].filter(
        (p) => p && p !== "—"
      );
      return parts.length ? parts.join(" · ") : "—";
    };

    const loadItems = async () => {
      if (!isLoading.value) isLoading.value = true;
      try {
        const response = await axios.get(`${ENDPOINT}?ordering=name`);
        jobs.value = normalizeList(response.data);
        loadError.value = false;
        const maxPage = Math.max(
          1,
          Math.ceil(jobs.value.length / perPage.value) || 1
        );
        if (currentPage.value > maxPage) currentPage.value = maxPage;
      } catch (error) {
        console.error("Error fetching jobs", error);
        loadError.value = true;
        jobs.value = [];
        proxy?.notifyError?.("Error loading communities.");
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
      sortField.value = event.sortField || "name";
      sortOrder.value = event.sortOrder ?? 1;
      currentPage.value = 1;
    };

    const refreshTable = () => {
      isLoading.value = true;
      loadItems();
    };

    const viewTo = (id) => `/job/view/${id}`;
    const editTo = (id) => `/job/edit/${id}`;
    const goToCreateForm = () => router.push("/job/form");
    const viewItem = (id) => router.push(viewTo(id));
    const editItem = (id) => router.push(editTo(id));

    const getRowActions = (item) => {
      const actions = [];
      if (proxy?.hasPermission?.("ctrctsapp.view_job")) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => viewItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("ctrctsapp.change_job")) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => editItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("ctrctsapp.delete_job")) {
        actions.push({
          key: "delete",
          label: "Delete",
          severity: "danger",
          icon: TrashIcon,
          command: () => deleteJob(item.id, item.name),
        });
      }
      return actions;
    };

    const deleteJob = (id, name) => {
      proxy?.confirmDelete?.(
        "Are you sure?",
        `Delete "${name}"? This action cannot be undone.`,
        async () => {
          try {
            await axios.delete(`${ENDPOINT}${id}/`);
            jobs.value = jobs.value.filter((p) => p.id !== id);
            proxy?.notifyToastSuccess?.("The community has been deleted.");
          } catch (err) {
            console.error("Error deleting community", err);
            const detail =
              err?.response?.data?.detail || "Error deleting the community.";
            proxy?.notifyError?.(detail);
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

    return {
      stats,
      isLoading,
      loadError,
      perPage,
      filter,
      totalRows,
      sortField,
      sortOrder,
      tableFirst,
      pagedItems,
      pageOptions,
      tableMinWidth,
      hasSearch,
      emptyTitle,
      emptyDescription,
      clearSearch,
      isMobile,
      isTablet,
      hasRowActions,
      canView,
      builderLabel,
      formatCoord,
      mobileMeta,
      getRowActions,
      refreshTable,
      onTablePage,
      onTableSort,
      goToCreateForm,
      viewTo,
    };
  },
};
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

.jr-master-list__loading,
.jr-master-list__muted {
  color: var(--color-jr-muted);
}

.jr-master-list__loading {
  margin: 0;
  padding: 1rem 0;
  font-size: 0.875rem;
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

.jr-master-list__table :deep(th.jr-col-num),
.jr-master-list__table :deep(td.jr-col-num) {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
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
