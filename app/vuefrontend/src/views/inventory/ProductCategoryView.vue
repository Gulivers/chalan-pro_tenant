<template>
  <JRPage>
    <JRPageHeader title="Product Categories">
      <template #actions>
        <JRButton
          v-if="hasPermission('appinventory.add_productcategory')"
          type="button"
          :fluid="isMobile"
          @click="goToCreateForm">
          + New Category
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-master-list__search">
          <label class="jr-sr-only" for="category-filter-input">
            Search categories
          </label>
          <span class="jr-master-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="category-filter-input"
            v-model="filter"
            type="search"
            placeholder="Search categories..." />
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
        <label class="jr-sr-only" for="category-per-page">
          Entries per page
        </label>
        <JRSelect
          class="jr-master-list__entries"
          inputId="category-per-page"
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
        v-if="!items.length && !isLoading"
        :title="emptyTitle"
        :description="emptyDescription" />
      <p v-if="isLoading && !items.length" class="jr-master-list__loading">
        Loading categories…
      </p>
      <p
        v-else-if="isLoading && items.length"
        class="jr-master-list__loading"
        aria-live="polite">
        Updating…
      </p>
      <ul
        v-if="items.length"
        class="jr-master-list__rows"
        :aria-busy="isLoading ? 'true' : 'false'">
        <li v-for="item in items" :key="item.id" class="jr-master-row">
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
        tableStyle="min-width: 36rem"
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

const ENDPOINT = "/api/productcategory-provider/";
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
  name: "ProductCategoryView",
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
    const stats = ref({ total: 0, active: 0, inactive: 0 });
    const isLoading = ref(true);
    const loadError = ref(false);
    const currentPage = ref(1);
    const perPage = ref(25);
    const filter = ref("");
    const totalRows = ref(0);
    const sortField = ref("id");
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
    const emptyTitle = computed(() =>
      loadError.value ? "Could not load categories" : "No categories"
    );
    const emptyDescription = computed(() =>
      loadError.value
        ? "Try Refresh."
        : "No categories match the current search."
    );

    const canView = computed(() =>
      !!proxy?.hasPermission?.("appinventory.view_productcategory")
    );
    const hasRowActions = computed(
      () =>
        canView.value ||
        !!proxy?.hasPermission?.("appinventory.change_productcategory") ||
        !!proxy?.hasPermission?.("appinventory.delete_productcategory")
    );

    const getOrderingFromSortBy = (sortBy) => {
      if (!sortBy) return "-id";
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
      if (!field) return "-id";
      return desc ? `-${field}` : field;
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
          if (response.data.stats) stats.value = response.data.stats;
          totalRows.value = response.data.totalRows ?? 0;
          items.value = response.data.items;
          loadError.value = false;
        } else {
          throw new Error("Invalid response format");
        }
      } catch (error) {
        loadError.value = true;
        items.value = [];
        totalRows.value = 0;
        stats.value = { total: 0, active: 0, inactive: 0 };
        proxy?.notifyError?.("Error loading categories.");
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
      sortField.value = event.sortField || "id";
      sortOrder.value = event.sortOrder ?? -1;
      currentPage.value = 1;
      loadItems();
    };

    const refreshTable = () => {
      isLoading.value = true;
      loadItems();
    };

    const viewTo = (id) => ({ name: "product-category-view", params: { id } });
    const goToCreateForm = () => router.push({ name: "product-category-form" });
    const viewItem = (id) => router.push(viewTo(id));
    const editItem = (id) =>
      router.push({ name: "product-category-edit", params: { id } });

    const getRowActions = (item) => {
      const actions = [];
      if (proxy?.hasPermission?.("appinventory.view_productcategory")) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => viewItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("appinventory.change_productcategory")) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => editItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("appinventory.delete_productcategory")) {
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
        "Delete?",
        "This will delete the product category. This action cannot be undone.",
        async () => {
          try {
            await axios.delete(`/api/productcategory/${id}/`);
            proxy?.notifyToastSuccess?.(
              "The product category has been deleted."
            );
            refreshTable();
          } catch (error) {
            const status = error?.response?.status;
            const data = error?.response?.data;
            if (status === 403) {
              proxy?.notifyError?.(
                "You do not have permission for this action."
              );
            } else if (status === 409) {
              proxy?.notifyError?.(
                data?.detail || "Cannot delete: category is in use."
              );
            } else {
              proxy?.notifyError?.(
                data?.detail || "Error deleting the category."
              );
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
      items,
      stats,
      isLoading,
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
      viewItem,
      editItem,
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
