<template>
  <JRPage>
    <JRPageHeader title="Party Categories">
      <template #actions>
        <JRButton
          v-if="hasPermission('apptransactions.add_partycategory')"
          type="button"
          @click="goToCreateForm">
          + New Party Category
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-master-list__search">
          <label class="jr-sr-only" for="pcat-filter-input">
            Search party categories
          </label>
          <span class="jr-master-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="pcat-filter-input"
            v-model="filter"
            type="search"
            placeholder="Search by name or description..." />
        </div>
      </template>

      <template #stats>
        <div class="jr-master-list__summary" aria-live="polite">
          <JRBadge :value="`${stats.total} Total`" severity="secondary" />
          <JRBadge
            :value="`${stats.active} Active`"
            :severity="stats.active > 0 ? 'success' : 'secondary'" />
          <JRBadge
            :value="`${stats.inactive} Inactive`"
            severity="secondary" />
        </div>
      </template>

      <template #actions>
        <label class="jr-sr-only" for="pcat-per-page">
          Entries per page
        </label>
        <JRSelect
          class="jr-master-list__entries"
          inputId="pcat-per-page"
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
        Loading party categories…
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
            <p v-if="item.description" class="jr-master-row__meta">
              {{ item.description }}
            </p>
          </div>
          <div class="jr-master-row__aside">
            <JRBadge
              :value="item.is_active ? 'Active' : 'Inactive'"
              :severity="item.is_active ? 'success' : 'secondary'" />
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
        tableStyle="min-width: 36rem"
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
        <Column field="name" header="Name" sortable>
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
        <Column field="description" header="Description" sortable>
          <template #body="{ data }">
            {{ data.description || "—" }}
          </template>
        </Column>
        <Column field="is_active" header="Status" sortable>
          <template #body="{ data }">
            <JRBadge
              :value="data.is_active ? 'Active' : 'Inactive'"
              :severity="data.is_active ? 'success' : 'secondary'" />
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

const ENDPOINT = "/api/party-categories/";
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

function compareValues(a, b, field) {
  const av = a?.[field];
  const bv = b?.[field];
  if (typeof av === "boolean" || typeof bv === "boolean") {
    return Number(!!av) - Number(!!bv);
  }
  const as = (av ?? "").toString().toLowerCase();
  const bs = (bv ?? "").toString().toLowerCase();
  if (as < bs) return -1;
  if (as > bs) return 1;
  return 0;
}

export default {
  name: "PartyCategoryListView",
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

    const categories = ref([]);
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
      let list = categories.value;
      if (q) {
        list = list.filter((item) =>
          `${item.name} ${item.description || ""}`.toLowerCase().includes(q)
        );
      }
      const field = sortField.value || "name";
      const order = sortOrder.value === -1 ? -1 : 1;
      return [...list].sort(
        (a, b) => compareValues(a, b, field) * order
      );
    });

    const stats = computed(() => {
      const list = filteredItems.value;
      const active = list.filter((i) => i.is_active).length;
      return { total: list.length, active, inactive: list.length - active };
    });

    const totalRows = computed(() => filteredItems.value.length);
    const tableFirst = computed(() => (currentPage.value - 1) * perPage.value);
    const pagedItems = computed(() => {
      const start = tableFirst.value;
      return filteredItems.value.slice(start, start + perPage.value);
    });

    const hasSearch = computed(() =>
      Boolean(filter.value && filter.value.trim())
    );
    const emptyTitle = computed(() => {
      if (loadError.value) return "Could not load party categories";
      if (hasSearch.value) return "No matching party categories";
      return "No party categories";
    });
    const emptyDescription = computed(() => {
      if (loadError.value) return "Try Refresh.";
      const query = filter.value.trim();
      if (query) return `No party categories match “${query}”.`;
      return "No party categories yet.";
    });

    const clearSearch = () => {
      filter.value = "";
      if (typeof document !== "undefined") {
        document.getElementById("pcat-filter-input")?.focus();
      }
    };

    const canView = computed(() =>
      !!proxy?.hasPermission?.("apptransactions.view_partycategory")
    );
    const hasRowActions = computed(
      () =>
        canView.value ||
        !!proxy?.hasPermission?.("apptransactions.change_partycategory") ||
        !!proxy?.hasPermission?.("apptransactions.delete_partycategory")
    );

    const loadItems = async () => {
      if (!isLoading.value) isLoading.value = true;
      try {
        const response = await axios.get(ENDPOINT);
        categories.value = Array.isArray(response.data) ? response.data : [];
        loadError.value = false;
        const maxPage = Math.max(
          1,
          Math.ceil(categories.value.length / perPage.value) || 1
        );
        if (currentPage.value > maxPage) currentPage.value = maxPage;
      } catch (error) {
        console.error("Error fetching party categories", error);
        loadError.value = true;
        categories.value = [];
        proxy?.notifyError?.("Error loading party categories.");
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

    const viewTo = (id) => ({
      path: "/party-categories/form",
      query: { id: String(id), mode: "view" },
    });
    const editTo = (id) => ({
      path: "/party-categories/form",
      query: { id: String(id), mode: "edit" },
    });
    const goToCreateForm = () => router.push("/party-categories/form");
    const viewItem = (id) => router.push(viewTo(id));
    const editItem = (id) => router.push(editTo(id));

    const getRowActions = (item) => {
      const actions = [];
      if (proxy?.hasPermission?.("apptransactions.view_partycategory")) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => viewItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("apptransactions.change_partycategory")) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => editItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("apptransactions.delete_partycategory")) {
        actions.push({
          key: "delete",
          label: "Delete",
          severity: "danger",
          icon: TrashIcon,
          command: () => deleteCategory(item.id),
        });
      }
      return actions;
    };

    const deleteCategory = (id) => {
      proxy?.confirmDelete?.(
        "Are you sure?",
        "This action cannot be undone.",
        async () => {
          try {
            await axios.delete(`${ENDPOINT}${id}/`);
            categories.value = categories.value.filter((cat) => cat.id !== id);
            proxy?.notifyToastSuccess?.(
              "The party category has been deleted."
            );
          } catch (err) {
            console.error("Error deleting party category", err);
            proxy?.notifyError?.("Error deleting the party category.");
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
      hasSearch,
      emptyTitle,
      emptyDescription,
      clearSearch,
      isMobile,
      isTablet,
      hasRowActions,
      canView,
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
  width: 4.75rem;
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
