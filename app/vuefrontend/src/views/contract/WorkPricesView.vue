<template>
  <JRPage>
    <JRPageHeader title="Piece Work Prices">
      <template #actions>
        <JRButton
          v-if="hasPermission('ctrctsapp.add_workprice')"
          type="button"
          @click="createPrice">
          + New Price
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-workprice-list__search">
          <label class="jr-sr-only" for="workprice-filter-input">
            Search piece work prices
          </label>
          <span class="jr-workprice-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="workprice-filter-input"
            v-model="search"
            type="search"
            placeholder="Search piece work prices..."
            autocomplete="off"
            :spellcheck="false"
            autocapitalize="none"
            autocorrect="off"
            enterkeyhint="search" />
        </div>
      </template>

      <template v-if="!isMobile" #stats>
        <div class="jr-workprice-list__summary" aria-live="polite">
          <JRBadge
            :value="`${filteredPrices.length} Total`"
            severity="secondary" />
        </div>
      </template>

      <template #actions>
        <template v-if="!isMobile">
          <JRSelect
            class="jr-workprice-list__entries"
            inputId="workprice-per-page"
            ariaLabel="Entries per page"
            v-model="perPage"
            :options="pageOptions"
            optionLabel="label"
            optionValue="value" />
          <JRButton
            type="button"
            variant="ghost"
            size="sm"
            class="jr-workprice-list__refresh"
            @click="fetchPrices">
            <RefreshIcon />
            Refresh
          </JRButton>
        </template>
        <template v-else>
          <button
            id="workprice-list-tools-trigger"
            type="button"
            class="jr-icon-btn"
            aria-label="List tools"
            aria-haspopup="menu"
            :aria-expanded="toolsMenuOpen ? 'true' : 'false'"
            aria-controls="workprice-list-tools-menu"
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
            id="workprice-list-tools-menu"
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

    <div v-if="isMobile" class="jr-workprice-list__mobile">
      <JREmptyState
        v-if="!pagedPrices.length && !loading"
        :title="emptyTitle"
        :description="emptyDescription">
        <JRButton
          v-if="loadError"
          type="button"
          variant="ghost"
          size="sm"
          @click="fetchPrices">
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
      <p v-if="loading && !prices.length" class="jr-workprice-list__loading">
        Loading piece work prices…
      </p>
      <p
        v-else-if="loading && prices.length"
        class="jr-workprice-list__loading"
        aria-live="polite">
        Updating…
      </p>
      <ul
        v-if="pagedPrices.length"
        class="jr-workprice-list__rows"
        :aria-busy="loading ? 'true' : 'false'">
        <li v-for="item in pagedPrices" :key="item.id" class="jr-workprice-row">
          <div class="jr-workprice-row__main">
            <router-link
              v-if="canView"
              class="jr-workprice-row__name jr-workprice-row__name--link"
              :to="viewTo(item.id)"
              :aria-label="`View ${item.name}`">
              {{ item.name }}
            </router-link>
            <span v-else class="jr-workprice-row__name">{{ item.name }}</span>
            <p class="jr-workprice-row__meta">
              <span>Trim {{ formatMoney(item.trim) }}</span>
              <span aria-hidden="true"> · </span>
              <span>Rough {{ formatMoney(item.rough) }}</span>
              <span aria-hidden="true"> · </span>
              <span>{{ item.unit_price || "—" }}</span>
            </p>
          </div>
          <div class="jr-workprice-row__aside">
            <JRRowActions
              v-if="hasRowActions"
              :actions="getRowActions(item)"
              :compact="true"
              :entity-label="item.name" />
          </div>
        </li>
      </ul>
      <Paginator
        v-if="filteredPrices.length > 0"
        class="jr-workprice-list__pager"
        :rows="perPage"
        :totalRecords="filteredPrices.length"
        :first="tableFirst"
        template="PrevPageLink CurrentPageReport NextPageLink"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
        @page="onTablePage" />
    </div>

    <div v-else class="jr-workprice-list__table">
      <JRDataTable
        :value="filteredPrices"
        :loading="loading"
        dataKey="id"
        :paginator="filteredPrices.length > 0"
        :rows="perPage"
        :totalRecords="filteredPrices.length"
        :first="tableFirst"
        :sortField="sortField"
        :sortOrder="sortOrder"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
        scrollable
        stripedRows
        :tableStyle="tableMinWidth"
        :emptyTitle="loading ? '' : emptyTitle"
        :emptyDescription="loading ? '' : emptyDescription"
        @page="onTablePage"
        @sort="onTableSort">
        <template #empty>
          <JREmptyState
            v-if="!loading"
            :title="emptyTitle"
            :description="emptyDescription">
            <JRButton
              v-if="loadError"
              type="button"
              variant="ghost"
              size="sm"
              @click="fetchPrices">
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
        <Column
          field="name"
          header="Description"
          sortable
          headerClass="jr-col-name"
          bodyClass="jr-col-name">
          <template #body="{ data }">
            <router-link
              v-if="canView"
              class="jr-workprice-row__name jr-workprice-row__name--link"
              :to="viewTo(data.id)"
              :aria-label="`View ${data.name}`">
              {{ data.name }}
            </router-link>
            <span v-else class="jr-workprice-row__name">{{ data.name }}</span>
          </template>
        </Column>
        <Column
          field="trim"
          header="Trim"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            {{ formatMoney(data.trim) }}
          </template>
        </Column>
        <Column
          field="rough"
          header="Rough"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            {{ formatMoney(data.rough) }}
          </template>
        </Column>
        <Column field="unit_price" header="Unit Price" sortable>
          <template #body="{ data }">
            {{ data.unit_price || "—" }}
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
import Menu from "primevue/menu";
import EyeIcon from "@primevue/icons/eye";
import PencilIcon from "@primevue/icons/pencil";
import RefreshIcon from "@primevue/icons/refresh";
import SearchIcon from "@primevue/icons/search";
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

function formatMoney(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
}

export default {
  name: "WorkPricesView",
  components: {
    Column,
    Paginator,
    Menu,
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

    const loading = ref(false);
    const loadError = ref(false);
    const prices = ref([]);
    const search = ref("");
    const perPage = ref(25);
    const currentPage = ref(1);
    const sortField = ref("name");
    const sortOrder = ref(1);
    const toolsMenu = ref(null);
    const toolsMenuOpen = ref(false);

    const initialViewport = readViewport();
    const isMobile = ref(initialViewport.isMobile);
    const isTablet = ref(initialViewport.isTablet);
    let phoneQuery = null;
    let tabletQuery = null;
    let onViewport = null;

    const pageOptions = [
      { value: 5, label: "5" },
      { value: 10, label: "10" },
      { value: 25, label: "25" },
      { value: 50, label: "50" },
    ];

    const tableMinWidth = computed(() =>
      isTablet.value ? "min-width: 36rem" : "min-width: 48rem"
    );

    const toolsMenuModel = computed(() => [
      {
        label: "Refresh",
        icon: "pi pi-refresh",
        command: () => fetchPrices(),
      },
    ]);

    const toggleToolsMenu = (event) => {
      toolsMenu.value?.toggle?.(event);
    };

    const filteredPrices = computed(() => {
      let list = [...prices.value];
      if (search.value.trim()) {
        const q = search.value.toLowerCase().trim();
        list = list.filter(
          (p) =>
            (p.name || "").toLowerCase().includes(q) ||
            (p.unit_price || "").toString().toLowerCase().includes(q)
        );
      }
      const field = sortField.value;
      const order = sortOrder.value;
      list.sort((a, b) => {
        const av = a?.[field];
        const bv = b?.[field];
        if (av === bv) return 0;
        if (av == null) return 1;
        if (bv == null) return -1;
        if (typeof av === "number" && typeof bv === "number") {
          return order === -1 ? bv - av : av - bv;
        }
        const as = String(av).toLowerCase();
        const bs = String(bv).toLowerCase();
        if (as < bs) return order === -1 ? 1 : -1;
        if (as > bs) return order === -1 ? -1 : 1;
        return 0;
      });
      return list;
    });

    const tableFirst = computed(() => (currentPage.value - 1) * perPage.value);
    const pagedPrices = computed(() => {
      const start = tableFirst.value;
      return filteredPrices.value.slice(start, start + perPage.value);
    });

    const hasSearch = computed(() => Boolean(search.value && search.value.trim()));
    const emptyTitle = computed(() => {
      if (loadError.value) return "Could not load piece work prices";
      if (hasSearch.value) return "No matching prices";
      return "No piece work prices";
    });
    const emptyDescription = computed(() => {
      if (loadError.value) return "Try Refresh.";
      if (hasSearch.value) return `No prices match “${search.value.trim()}”.`;
      return "No piece work prices yet.";
    });

    const canView = computed(() =>
      !!proxy?.hasPermission?.("ctrctsapp.view_workprice")
    );
    const hasRowActions = computed(
      () =>
        canView.value ||
        !!proxy?.hasPermission?.("ctrctsapp.change_workprice")
    );

    const clearSearch = () => {
      search.value = "";
      document.getElementById("workprice-filter-input")?.focus();
    };

    const fetchPrices = () => {
      loading.value = true;
      axios
        .get("/api/workprice/")
        .then((response) => {
          prices.value = Array.isArray(response.data)
            ? response.data
            : response.data?.results || [];
          currentPage.value = 1;
          loadError.value = false;
        })
        .catch((error) => {
          console.error("Error fetching work prices:", error);
          loadError.value = true;
          prices.value = [];
          proxy?.notifyError?.("Error loading piece work prices.");
        })
        .finally(() => {
          loading.value = false;
        });
    };

    const createPrice = () => router.push({ name: "work-prices-form" });
    const viewTo = (id) => ({ name: "work-prices-view", params: { id } });
    const editTo = (id) => ({ name: "work-prices-edit", params: { id } });
    const viewPrice = (id) => router.push(viewTo(id));
    const editPrice = (id) => router.push(editTo(id));

    const getRowActions = (item) => {
      const actions = [];
      if (proxy?.hasPermission?.("ctrctsapp.view_workprice")) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => viewPrice(item.id),
        });
      }
      if (proxy?.hasPermission?.("ctrctsapp.change_workprice")) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => editPrice(item.id),
        });
      }
      return actions;
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
      fetchPrices();
    });

    onUnmounted(() => {
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

    watch(search, () => {
      currentPage.value = 1;
    });

    watch(filteredPrices, (list) => {
      const maxPage = Math.max(1, Math.ceil(list.length / perPage.value) || 1);
      if (currentPage.value > maxPage) currentPage.value = maxPage;
    });

    return {
      loading,
      loadError,
      prices,
      search,
      perPage,
      filteredPrices,
      pagedPrices,
      tableFirst,
      tableMinWidth,
      sortField,
      sortOrder,
      pageOptions,
      hasSearch,
      emptyTitle,
      emptyDescription,
      clearSearch,
      isMobile,
      isTablet,
      canView,
      hasRowActions,
      getRowActions,
      fetchPrices,
      createPrice,
      viewTo,
      onTablePage,
      onTableSort,
      formatMoney,
      toolsMenu,
      toolsMenuOpen,
      toolsMenuModel,
      toggleToolsMenu,
    };
  },
};
</script>

<style scoped>
.jr-workprice-list__search {
  position: relative;
  min-width: 0;
  width: 100%;
}

.jr-workprice-list__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-workprice-list__search-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.jr-workprice-list__search :deep(.p-inputtext) {
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
    align-items: center;
    gap: 0.5rem;
  }

  :deep(.jr-toolbar__start) {
    flex: 1 1 auto;
    min-width: 0;
  }

  :deep(.jr-toolbar__actions) {
    flex: 0 0 auto;
  }
}

.jr-workprice-list__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  pointer-events: none;
}

:deep(.jr-toolbar__actions .jr-workprice-list__entries.p-select),
:deep(.jr-toolbar__actions .jr-workprice-list__entries.jr-control) {
  width: 4.75rem;
  flex: 0 0 auto;
}

.jr-workprice-list__loading {
  margin: 0;
  padding: 1rem 0;
  color: var(--color-jr-muted);
  font-size: 0.875rem;
}

.jr-workprice-list__rows {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: 1px solid var(--color-jr-border);
}

.jr-workprice-list__rows[aria-busy="true"] {
  opacity: 0.55;
}

.jr-workprice-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-workprice-row__main {
  min-width: 0;
  flex: 1 1 auto;
  text-align: left;
}

.jr-workprice-row__aside {
  flex-shrink: 0;
}

.jr-workprice-row__name {
  overflow: hidden;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-jr-text);
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 767.98px) {
  .jr-workprice-row {
    align-items: flex-start;
  }

  .jr-workprice-row__name {
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
}

a.jr-workprice-row__name--link {
  color: var(--color-jr-primary);
  text-decoration: none;
}

a.jr-workprice-row__name--link:hover {
  color: var(--color-jr-primary-hover);
  text-decoration: underline;
}

a.jr-workprice-row__name--link:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-workprice-row__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0.2rem 0 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
  font-variant-numeric: tabular-nums;
}

.jr-workprice-list__pager {
  margin-top: 0.25rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-workprice-list__pager :deep(.p-paginator),
.jr-workprice-list__pager :deep(.p-paginator-content) {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.5rem;
  padding: 0.35rem 0;
}

.jr-workprice-list__pager :deep(.p-paginator-current) {
  flex: 1 1 auto;
  min-width: 0;
  text-align: center;
  font-size: 0.8125rem;
  font-variant-numeric: tabular-nums;
  color: var(--color-jr-muted);
}

.jr-workprice-list__table :deep(.p-datatable) {
  --p-datatable-row-striped-background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
}

.jr-workprice-list__table :deep(.p-datatable-table-container) {
  overflow-x: auto;
}

.jr-workprice-list__table :deep(.p-datatable-thead > tr > th) {
  background: var(--color-jr-surface-muted);
  color: var(--color-jr-text);
  font-size: 0.875rem;
  font-weight: 600;
}

.jr-workprice-list__table :deep(.p-datatable-mask),
.jr-workprice-list__table :deep(.p-datatable-loading-overlay) {
  background: color-mix(in srgb, var(--color-jr-surface) 72%, transparent);
}

.jr-workprice-list__table :deep(.p-datatable-tbody > tr > td) {
  font-size: 0.875rem;
  vertical-align: middle;
  padding-top: 0.3rem;
  padding-bottom: 0.3rem;
}

.jr-workprice-list__table :deep(th.jr-col-name),
.jr-workprice-list__table :deep(td.jr-col-name) {
  min-width: 12rem;
  white-space: normal;
  overflow-wrap: anywhere;
}

.jr-workprice-list__table :deep(th.jr-col-num),
.jr-workprice-list__table :deep(td.jr-col-num) {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.jr-workprice-list__table :deep(th.jr-col-actions),
.jr-workprice-list__table :deep(td.jr-col-actions) {
  width: 12rem;
  text-align: center;
  white-space: nowrap;
}

.jr-workprice-list__table :deep(th.jr-col-actions.jr-col-actions--compact),
.jr-workprice-list__table :deep(td.jr-col-actions.jr-col-actions--compact) {
  width: 3.25rem;
}

.jr-workprice-list__table
  :deep(th.jr-col-actions .p-datatable-column-header-content) {
  display: flex;
  justify-content: center;
  width: 100%;
}

.jr-workprice-list__table :deep(td.jr-col-actions .jr-row-actions) {
  justify-content: center;
  width: 100%;
}
</style>
