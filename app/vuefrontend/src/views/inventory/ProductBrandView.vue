<template>
  <JRPage>
    <JRPageHeader title="Product Brands">
      <template #actions>
        <JRButton
          v-if="hasPermission('appinventory.add_productbrand')"
          type="button"
          :fluid="isMobile"
          @click="goToCreateForm">
          + New Brand
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-master-list__search">
          <label class="jr-sr-only" for="brand-filter-input">
            Search brands
          </label>
          <span class="jr-master-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="brand-filter-input"
            v-model="filter"
            type="search"
            placeholder="Search brands..." />
        </div>
      </template>

      <template #stats>
        <div class="jr-master-list__summary" aria-live="polite">
          <JRBadge :value="`${stats.total} Total`" severity="secondary" />
          <JRBadge :value="`${stats.active} Active`" severity="success" />
          <JRBadge
            :value="`${stats.inactive} Inactive`"
            severity="secondary" />
        </div>
      </template>

      <template #actions>
        <label class="jr-sr-only" for="brand-per-page">Entries per page</label>
        <JRSelect
          class="jr-master-list__entries"
          inputId="brand-per-page"
          v-model="perPage"
          :options="pageOptions"
          optionLabel="label"
          optionValue="value" />
        <JRButton
          type="button"
          variant="ghost"
          size="sm"
          class="jr-master-list__refresh"
          @click="refreshList">
          <RefreshIcon />
          Refresh
        </JRButton>
      </template>
    </JRToolbar>

    <div v-if="isMobile" class="jr-master-list__mobile">
      <JREmptyState
        v-if="!pagedItems.length && !isLoading"
        :title="emptyTitle"
        :description="emptyDescription" />
      <p v-if="isLoading && !brands.length" class="jr-master-list__loading">
        Loading brands…
      </p>
      <p
        v-else-if="isLoading && brands.length"
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
            <p v-if="item.is_default" class="jr-master-row__meta">Default</p>
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
        :tableStyle="tableMinWidth"
        :emptyTitle="emptyTitle"
        :emptyDescription="emptyDescription"
        @page="onTablePage"
        @sort="onTableSort">
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
        <Column field="is_active" header="Status" sortable>
          <template #body="{ data }">
            <JRBadge
              :value="data.is_active ? 'Active' : 'Inactive'"
              :severity="data.is_active ? 'success' : 'secondary'" />
          </template>
        </Column>
        <Column field="is_default" header="Default" sortable>
          <template #body="{ data }">
            <JRBadge
              v-if="data.is_default"
              value="Default"
              severity="info" />
            <span v-else class="jr-master-list__muted">—</span>
          </template>
        </Column>
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
  name: "ProductBrandView",
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

    const brands = ref([]);
    const filter = ref("");
    const perPage = ref(25);
    const currentPage = ref(1);
    const isLoading = ref(false);
    const loadError = ref(false);
    const deletingId = ref(null);
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
      let list = brands.value.slice();
      if (filter.value) {
        const q = filter.value.toLowerCase();
        list = list.filter((item) =>
          String(item.name || "")
            .toLowerCase()
            .includes(q)
        );
      }

      const field = sortField.value || "name";
      const dir = sortOrder.value === -1 ? -1 : 1;
      list.sort((a, b) => {
        let av = a[field];
        let bv = b[field];
        if (typeof av === "boolean") av = av ? 1 : 0;
        if (typeof bv === "boolean") bv = bv ? 1 : 0;
        if (av == null) av = "";
        if (bv == null) bv = "";
        if (typeof av === "string" && typeof bv === "string") {
          return av.localeCompare(bv) * dir;
        }
        if (av < bv) return -1 * dir;
        if (av > bv) return 1 * dir;
        return 0;
      });
      return list;
    });

    const totalRows = computed(() => filteredItems.value.length);
    const tableFirst = computed(() => (currentPage.value - 1) * perPage.value);
    const tableMinWidth = computed(() =>
      isTablet.value ? "min-width: 36rem" : "min-width: 48rem"
    );
    const pagedItems = computed(() => {
      const start = tableFirst.value;
      return filteredItems.value.slice(start, start + perPage.value);
    });

    const clampCurrentPage = () => {
      const maxPage = Math.max(1, Math.ceil(totalRows.value / perPage.value) || 1);
      if (currentPage.value > maxPage) currentPage.value = maxPage;
    };

    const stats = computed(() => {
      const list = filteredItems.value;
      const active = list.filter((i) => i.is_active).length;
      return { total: list.length, active, inactive: list.length - active };
    });

    const emptyTitle = computed(() =>
      loadError.value ? "Could not load brands" : "No brands"
    );
    const emptyDescription = computed(() => {
      if (loadError.value) return "Try Refresh.";
      if (filter.value) return "Try a different search term.";
      return "Start by creating your first product brand.";
    });

    const canView = computed(() =>
      !!proxy?.hasPermission?.("appinventory.view_productbrand")
    );
    const hasRowActions = computed(
      () =>
        canView.value ||
        !!proxy?.hasPermission?.("appinventory.change_productbrand") ||
        !!proxy?.hasPermission?.("appinventory.delete_productbrand")
    );

    const fetchItems = async () => {
      isLoading.value = true;
      try {
        const response = await axios.get("/api/productbrand/");
        brands.value = Array.isArray(response.data) ? response.data : [];
        loadError.value = false;
      } catch (error) {
        console.error("Error loading brands:", error);
        brands.value = [];
        loadError.value = true;
        proxy?.notifyError?.("Error loading product brands.");
      } finally {
        isLoading.value = false;
      }
    };

    const refreshList = () => {
      fetchItems();
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

    const viewTo = (id) => ({ name: "product-brand-view", params: { id } });
    const goToCreateForm = () => router.push({ name: "product-brand-form" });
    const viewItem = (id) => router.push(viewTo(id));
    const editItem = (id) =>
      router.push({ name: "product-brand-edit", params: { id } });

    const getRowActions = (item) => {
      const actions = [];
      if (proxy?.hasPermission?.("appinventory.view_productbrand")) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => viewItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("appinventory.change_productbrand")) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => editItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("appinventory.delete_productbrand")) {
        actions.push({
          key: "delete",
          label: "Delete",
          severity: "danger",
          icon: TrashIcon,
          disabled: deletingId.value === item.id,
          command: () => confirmDelete(item.id),
        });
      }
      return actions;
    };

    const confirmDelete = (id) => {
      proxy?.confirmDelete?.(
        "Delete?",
        "This will delete the product brand. This action cannot be undone.",
        async () => {
          await deleteItem(id);
        }
      );
    };

    const deleteItem = async (id) => {
      deletingId.value = id;
      try {
        await axios.delete(`/api/productbrand/${id}/`);
        brands.value = brands.value.filter((b) => b.id !== id);
        clampCurrentPage();
        proxy?.notifyToastSuccess?.("The product brand has been deleted.");
      } catch (error) {
        console.error("Error deleting product brand:", error);
        const status = error?.response?.status;
        const data = error?.response?.data;
        if (status === 403) {
          proxy?.notifyError?.(
            "You do not have permission for this action."
          );
        } else if (status === 409) {
          proxy?.notifyError?.(
            data?.detail || "Cannot delete: brand is in use."
          );
        } else {
          proxy?.notifyError?.(
            data?.detail || "Error deleting the product brand."
          );
        }
      } finally {
        deletingId.value = null;
      }
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
      fetchItems();
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

    return {
      brands,
      filter,
      perPage,
      currentPage,
      isLoading,
      sortField,
      sortOrder,
      pageOptions,
      pagedItems,
      totalRows,
      tableFirst,
      tableMinWidth,
      stats,
      emptyTitle,
      emptyDescription,
      isMobile,
      isTablet,
      hasRowActions,
      canView,
      getRowActions,
      refreshList,
      onTablePage,
      onTableSort,
      goToCreateForm,
      viewTo,
      viewItem,
      editItem,
      confirmDelete,
      deleteItem,
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

.jr-master-row__meta {
  margin: 0.15rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
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
