<template>
  <JRPage>
    <JRPageHeader title="Work Accounts">
      <template #actions>
        <JRButton
          v-if="hasPermission('apptransactions.add_workaccount')"
          type="button"
          @click="goToCreateForm">
          + New Work Account
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-wa-list__search">
          <label class="jr-sr-only" for="wa-filter-input">
            Search work accounts
          </label>
          <span class="jr-wa-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="wa-filter-input"
            v-model="filter"
            type="search"
            placeholder="Search by title, builder, community, lot, address…"
            autocomplete="off"
            :spellcheck="false"
            autocapitalize="none"
            autocorrect="off"
            enterkeyhint="search" />
        </div>
      </template>

      <template v-if="!isMobile" #stats>
        <div class="jr-wa-list__summary" aria-live="polite">
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
        <template v-if="!isMobile">
          <JRSelect
            class="jr-wa-list__entries"
            inputId="wa-per-page"
            ariaLabel="Entries per page"
            v-model="perPage"
            :options="pageOptions"
            optionLabel="label"
            optionValue="value" />
          <JRButton
            type="button"
            variant="ghost"
            size="sm"
            class="jr-wa-list__refresh"
            @click="refreshTable">
            <RefreshIcon />
            Refresh
          </JRButton>
        </template>
        <template v-else>
          <button
            id="wa-list-tools-trigger"
            type="button"
            class="jr-icon-btn"
            aria-label="List tools"
            aria-haspopup="menu"
            :aria-expanded="toolsMenuOpen ? 'true' : 'false'"
            aria-controls="wa-list-tools-menu"
            @click="toggleToolsMenu">
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              aria-hidden="true"
              fill="currentColor">
              <circle cx="8" cy="3" r="1.4" />
              <circle cx="8" cy="8" r="1.4" />
              <circle cx="8" cy="13" r="1.4" />
            </svg>
          </button>
          <Menu
            id="wa-list-tools-menu"
            ref="toolsMenu"
            class="jr-overlay jr-row-menu"
            :model="toolsMenuModel"
            :popup="true"
            ariaLabel="List tools"
            @show="toolsMenuOpen = true"
            @hide="toolsMenuOpen = false" />
        </template>
      </template>
    </JRToolbar>

    <!-- Phone: compact scan list -->
    <div v-if="isMobile" class="jr-wa-list__mobile">
      <JREmptyState
        v-if="!pageItems.length && !isLoading"
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
      <p v-if="isLoading && !pageItems.length" class="jr-wa-list__loading">
        Loading work accounts…
      </p>
      <p
        v-else-if="isLoading && pageItems.length"
        class="jr-wa-list__loading"
        aria-live="polite">
        Updating…
      </p>
      <ul
        v-if="pageItems.length"
        class="jr-wa-list__rows"
        :aria-busy="isLoading ? 'true' : 'false'">
        <li v-for="item in pageItems" :key="item.id" class="jr-wa-row">
          <div class="jr-wa-row__main">
            <router-link
              v-if="canView"
              class="jr-wa-row__name jr-wa-row__name--link"
              :to="waViewTo(item.id)"
              :aria-label="`View ${item.title}`">
              {{ item.title }}
            </router-link>
            <span v-else class="jr-wa-row__name">{{ item.title }}</span>
            <p class="jr-wa-row__meta">
              <span v-if="item.builder_name">{{ item.builder_name }}</span>
              <span v-if="item.builder_name && item.job_name" aria-hidden="true">
                ·
              </span>
              <span v-if="item.job_name">{{ item.job_name }}</span>
            </p>
            <p class="jr-wa-row__meta">
              <JRBadge
                :value="item.is_active ? 'Active' : 'Inactive'"
                :severity="item.is_active ? 'success' : 'secondary'" />
              <span v-if="item.lot">Lot {{ item.lot }}</span>
              <span v-else-if="item.address">{{ item.address }}</span>
              <span v-if="item.house_model_name" aria-hidden="true"> · </span>
              <span v-if="item.house_model_name">{{ item.house_model_name }}</span>
            </p>
          </div>
          <div class="jr-wa-row__aside">
            <JRRowActions
              v-if="hasRowActions"
              :actions="getRowActions(item)"
              :compact="true"
              :entity-label="item.title" />
          </div>
        </li>
      </ul>
      <Paginator
        v-if="totalRows > 0"
        class="jr-wa-list__pager"
        :rows="perPage"
        :totalRecords="totalRows"
        :first="tableFirst"
        template="PrevPageLink CurrentPageReport NextPageLink"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
        @page="onTablePage" />
    </div>

    <!-- Tablet / desktop table -->
    <div
      v-else
      class="jr-wa-list__table"
      :aria-busy="isLoading ? 'true' : 'false'">
      <JRDataTable
        :value="pageItems"
        :loading="isLoading"
        dataKey="id"
        lazy
        :paginator="totalRows > 0"
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

        <Column field="title" header="Title" sortable>
          <template #body="{ data }">
            <router-link
              v-if="canView"
              class="jr-wa-row__name jr-wa-row__name--link"
              :to="waViewTo(data.id)"
              :aria-label="`View ${data.title}`">
              {{ data.title }}
            </router-link>
            <strong v-else>{{ data.title }}</strong>
          </template>
        </Column>
        <Column field="builder_name" header="Builder" sortable>
          <template #body="{ data }">
            {{ data.builder_name || "—" }}
          </template>
        </Column>
        <Column field="job_name" header="Community" sortable>
          <template #body="{ data }">
            {{ data.job_name || "—" }}
          </template>
        </Column>
        <Column v-if="!isTablet" field="house_model_name" header="Model" sortable>
          <template #body="{ data }">
            {{ data.house_model_name || "—" }}
          </template>
        </Column>
        <Column field="lot" header="Lot" sortable>
          <template #body="{ data }">
            {{ data.lot || "—" }}
          </template>
        </Column>
        <Column
          v-if="!isTablet"
          field="address"
          header="Address"
          sortable
          headerClass="jr-col-address"
          bodyClass="jr-col-address">
          <template #body="{ data }">
            {{ data.address || "—" }}
          </template>
        </Column>
        <Column v-if="!isTablet" field="city" header="City" sortable>
          <template #body="{ data }">
            {{ data.city || "—" }}
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
              :entity-label="data.title" />
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
import Menu from "primevue/menu";
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

const ENDPOINT = "/api/work-accounts/";
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

export default {
  name: "WorkAccountListView",
  components: {
    Column,
    Menu,
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

    const workAccounts = ref([]);
    const totalRows = ref(0);
    const stats = ref({ total: 0, active: 0, inactive: 0 });
    const isLoading = ref(true);
    const loadError = ref(false);
    const currentPage = ref(1);
    const perPage = ref(25);
    const filter = ref("");
    const sortField = ref("created_at");
    const sortOrder = ref(-1);
    const toolsMenu = ref(null);
    const toolsMenuOpen = ref(false);
    let searchTimer = null;
    let fetchSeq = 0;

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

    const pageItems = computed(() => workAccounts.value);
    const tableFirst = computed(() => (currentPage.value - 1) * perPage.value);

    const tableMinWidth = computed(() =>
      isTablet.value ? "min-width: 36rem" : "min-width: 48rem"
    );
    const hasSearch = computed(() =>
      Boolean(filter.value && filter.value.trim())
    );
    const emptyTitle = computed(() => {
      if (loadError.value) return "Could not load work accounts";
      if (hasSearch.value) return "No matching work accounts";
      return "No work accounts";
    });
    const emptyDescription = computed(() => {
      if (loadError.value) return "Try Refresh.";
      const query = filter.value.trim();
      if (query) return `No work accounts match “${query}”.`;
      return "No work accounts yet.";
    });

    const canView = computed(() =>
      !!proxy?.hasPermission?.("apptransactions.view_workaccount")
    );
    const hasRowActions = computed(
      () =>
        canView.value ||
        !!proxy?.hasPermission?.("apptransactions.change_workaccount") ||
        !!proxy?.hasPermission?.("apptransactions.delete_workaccount")
    );

    const toolsMenuModel = computed(() => [
      { label: "Refresh", command: () => refreshTable() },
    ]);

    const clearSearch = () => {
      filter.value = "";
      if (typeof document !== "undefined") {
        document.getElementById("wa-filter-input")?.focus();
      }
    };

    const getOrderingFromSort = () => {
      const fieldMap = {
        title: "title",
        builder_name: "builder__name",
        job_name: "job__name",
        house_model_name: "house_model__name",
        lot: "lot",
        address: "address",
        city: "city",
        is_active: "is_active",
        created_at: "created_at",
        id: "id",
      };
      const djangoField = fieldMap[sortField.value] || "created_at";
      return sortOrder.value === 1 ? djangoField : `-${djangoField}`;
    };

    const fetchWorkAccounts = async () => {
      const seq = ++fetchSeq;
      if (!isLoading.value) isLoading.value = true;
      try {
        const params = {
          page: currentPage.value,
          page_size: perPage.value,
          ordering: getOrderingFromSort(),
        };
        const q = (filter.value || "").trim();
        if (q) params.search = q;

        const { data } = await axios.get(ENDPOINT, { params });
        if (seq !== fetchSeq) return;

        workAccounts.value = normalizeList(data);
        totalRows.value = Number(data?.count ?? workAccounts.value.length) || 0;
        stats.value = {
          total: Number(data?.stats?.total ?? totalRows.value) || 0,
          active: Number(data?.stats?.active ?? 0) || 0,
          inactive: Number(data?.stats?.inactive ?? 0) || 0,
        };
        loadError.value = false;
      } catch (err) {
        if (seq !== fetchSeq) return;
        console.error("Error fetching work accounts", err);
        loadError.value = true;
        workAccounts.value = [];
        totalRows.value = 0;
        stats.value = { total: 0, active: 0, inactive: 0 };
        proxy?.notifyError?.("Error loading work accounts.");
      } finally {
        if (seq === fetchSeq) isLoading.value = false;
      }
    };

    const refreshTable = () => {
      isLoading.value = true;
      fetchWorkAccounts();
    };

    const onTablePage = (event) => {
      const nextRows =
        event.rows != null && event.rows !== ""
          ? Number(event.rows)
          : perPage.value;
      if (Number.isFinite(nextRows) && nextRows > 0 && nextRows !== perPage.value) {
        perPage.value = nextRows;
      }
      currentPage.value = (event.page ?? 0) + 1;
    };

    const onTableSort = (event) => {
      sortField.value = event.sortField || "created_at";
      sortOrder.value = event.sortOrder ?? -1;
      currentPage.value = 1;
    };

    const toggleToolsMenu = (event) => {
      toolsMenu.value?.toggle(event);
    };

    const goToCreateForm = () => {
      router.push({ name: "work-accounts-form" });
    };

    const waViewTo = (id) => ({
      name: "work-order-viewer",
      params: { id },
    });

    const viewItem = (id) => {
      router.push(waViewTo(id));
    };

    const editItem = (id) => {
      router.push({
        name: "work-accounts-form",
        query: { id },
      });
    };

    const getRowActions = (item) => {
      const actions = [];
      if (proxy?.hasPermission?.("apptransactions.view_workaccount")) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => viewItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("apptransactions.change_workaccount")) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => editItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("apptransactions.delete_workaccount")) {
        actions.push({
          key: "delete",
          label: "Delete",
          severity: "danger",
          icon: TrashIcon,
          command: () => deleteWorkAccount(item),
        });
      }
      return actions;
    };

    const deleteWorkAccount = (item) => {
      const id = item?.id;
      const title = item?.title ? `“${item.title}”` : `#${id}`;
      proxy?.confirmDelete?.(
        "Are you sure?",
        `Delete ${title}? This action cannot be undone.`,
        async () => {
          try {
            await axios.delete(`${ENDPOINT}${id}/`);
            proxy?.notifyToastSuccess?.(
              "The work account has been deleted."
            );
            await fetchWorkAccounts();
          } catch (err) {
            console.error("Error deleting work account", err);
            const status = err?.response?.status;
            const data = err?.response?.data;
            if (status === 403) {
              proxy?.notifyError?.(
                "You do not have permission for this action."
              );
            } else {
              const detail =
                data?.detail || "Error deleting the work account.";
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
      fetchWorkAccounts();
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

    watch([currentPage, perPage, sortField, sortOrder], (next, prev) => {
      // Changing page size while not on page 1: reset to page 1, then that change loads.
      if (prev && next[1] !== prev[1] && next[0] !== 1) {
        currentPage.value = 1;
        return;
      }
      fetchWorkAccounts();
    });

    watch(filter, () => {
      if (searchTimer) clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        if (currentPage.value !== 1) {
          currentPage.value = 1;
        } else {
          fetchWorkAccounts();
        }
      }, 300);
    });

    return {
      workAccounts,
      pageItems,
      stats,
      isLoading,
      loadError,
      currentPage,
      perPage,
      filter,
      totalRows,
      sortField,
      sortOrder,
      tableFirst,
      pageOptions,
      emptyTitle,
      emptyDescription,
      hasSearch,
      clearSearch,
      isMobile,
      isTablet,
      tableMinWidth,
      hasRowActions,
      getRowActions,
      refreshTable,
      onTablePage,
      onTableSort,
      goToCreateForm,
      canView,
      waViewTo,
      toolsMenu,
      toolsMenuOpen,
      toolsMenuModel,
      toggleToolsMenu,
    };
  },
};
</script>

<style scoped>
.jr-wa-list__search {
  position: relative;
  min-width: 0;
  width: 100%;
}

.jr-wa-list__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-wa-list__search-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.jr-wa-list__search :deep(.p-inputtext) {
  padding-left: 2.25rem;
}

@media (max-width: 767.98px) {
  :deep(.jr-page-header) {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  :deep(.jr-page-header__actions) {
    flex-shrink: 0;
  }

  :deep(.jr-toolbar) {
    flex-direction: row;
    flex-wrap: nowrap;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0 0.5rem;
    margin-bottom: 0.5rem;
  }

  :deep(.jr-toolbar__start) {
    flex: 1 1 auto;
    min-width: 0;
  }

  :deep(.jr-toolbar__actions) {
    flex: 0 0 auto;
  }
}

.jr-wa-list__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  pointer-events: none;
}

:deep(.jr-toolbar__actions .jr-wa-list__entries.p-select),
:deep(.jr-toolbar__actions .jr-wa-list__entries.jr-control) {
  width: 6.25rem;
  min-width: 6.25rem;
  flex: 0 0 auto;
}

:deep(.jr-toolbar__actions .jr-wa-list__entries .p-select-label) {
  overflow: visible;
  text-overflow: clip;
}

:deep(.jr-toolbar__actions .jr-wa-list__entries .p-select-label) {
  overflow: visible;
  text-overflow: clip;
}

.jr-wa-list__loading {
  margin: 0;
  padding: 1rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-wa-list__rows {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: 1px solid var(--color-jr-border);
}

.jr-wa-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-wa-row__main {
  min-width: 0;
  flex: 1 1 auto;
  text-align: left;
}

.jr-wa-row__name {
  display: block;
  overflow: hidden;
  color: var(--color-jr-text);
  font-weight: 600;
  font-size: 0.875rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 767.98px) {
  .jr-wa-row__name {
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
}

a.jr-wa-row__name--link {
  color: var(--color-jr-primary);
  text-decoration: none;
}

a.jr-wa-row__name--link:hover {
  color: var(--color-jr-primary-hover);
  text-decoration: underline;
}

a.jr-wa-row__name--link:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-wa-row__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0.2rem 0 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-wa-row__aside {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.35rem;
  flex-shrink: 0;
}

.jr-wa-list__rows[aria-busy="true"] {
  opacity: 0.55;
}

.jr-wa-list__pager {
  margin-top: 0.25rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-wa-list__pager :deep(.p-paginator),
.jr-wa-list__pager :deep(.p-paginator-content) {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.5rem;
  padding: 0.35rem 0;
}

.jr-wa-list__pager :deep(.p-paginator-prev),
.jr-wa-list__pager :deep(.p-paginator-next) {
  min-width: 2.75rem;
  min-height: 2.75rem;
}

.jr-wa-list__pager :deep(.p-paginator-current) {
  flex: 1 1 auto;
  min-width: 0;
  text-align: center;
  font-size: 0.8125rem;
  font-variant-numeric: tabular-nums;
  color: var(--color-jr-muted);
}

.jr-wa-list__table :deep(.p-datatable) {
  --p-datatable-row-striped-background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
}

.jr-wa-list__table :deep(.p-datatable-table-container) {
  overflow-x: auto;
}

.jr-wa-list__table :deep(.p-datatable-thead > tr > th) {
  background: var(--color-jr-surface-muted);
  color: var(--color-jr-text);
  font-size: 0.875rem;
  font-weight: 600;
}

.jr-wa-list__table :deep(.p-datatable-mask),
.jr-wa-list__table :deep(.p-datatable-loading-overlay) {
  background: color-mix(in srgb, var(--color-jr-surface) 72%, transparent);
}

.jr-wa-list__table :deep(.p-datatable-tbody > tr > td) {
  font-size: 0.875rem;
  vertical-align: middle;
  padding-top: 0.3rem;
  padding-bottom: 0.3rem;
}

.jr-wa-list__table :deep(th.jr-col-address),
.jr-wa-list__table :deep(td.jr-col-address) {
  max-width: 14rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jr-wa-list__table :deep(th.jr-col-actions),
.jr-wa-list__table :deep(td.jr-col-actions) {
  width: 16.5rem;
  text-align: center;
  white-space: nowrap;
}

.jr-wa-list__table :deep(th.jr-col-actions.jr-col-actions--compact),
.jr-wa-list__table :deep(td.jr-col-actions.jr-col-actions--compact) {
  width: 3.25rem;
}

.jr-wa-list__table
  :deep(th.jr-col-actions .p-datatable-column-header-content) {
  display: flex;
  justify-content: center;
  width: 100%;
}

.jr-wa-list__table :deep(td.jr-col-actions .jr-row-actions) {
  justify-content: center;
  width: 100%;
}
</style>
