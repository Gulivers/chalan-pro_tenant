<template>
  <JRPage>
    <div class="jr-product-list__masthead">
      <div class="jr-product-list__masthead-text">
        <JRPageHeader title="Products" />
        <div class="jr-product-list__summary" aria-live="polite">
          <Tag :value="`${stats.total} Total`" severity="info" />
          <Tag :value="`${stats.active} Active`" severity="success" />
          <Tag :value="`${stats.inactive} Inactive`" severity="secondary" />
        </div>
      </div>
      <JRButton
        v-if="hasPermission('appinventory.add_product')"
        type="button"
        class="jr-product-list__create"
        @click="goToCreateForm">
        + New Product
      </JRButton>
    </div>

    <div class="jr-product-list__toolbar">
      <div class="jr-product-list__search">
        <label class="visually-hidden" for="filter-input">
          Search products
        </label>
        <span class="jr-product-list__search-icon" aria-hidden="true">
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            stroke-width="1.6">
            <circle cx="6.75" cy="6.75" r="4.25" />
            <path d="m10.2 10.2 3.3 3.3" />
          </svg>
        </span>
        <JRInput
          inputId="filter-input"
          v-model="filter"
          type="search"
          placeholder="Search products..." />
      </div>

      <div class="jr-product-list__cluster">
        <label class="visually-hidden" for="per-page-select">
          Entries per page
        </label>
        <JRSelect
          class="jr-product-list__entries"
          inputId="per-page-select"
          v-model="perPage"
          :options="pageOptions"
          optionLabel="label"
          optionValue="value" />

        <ToggleButton
          v-if="canBulkUpdate"
          v-model="showBulkPricesPanel"
          class="jr-product-list__bulk-toggle"
          onLabel="Bulk Excel"
          offLabel="Bulk Excel"
          aria-controls="product-bulk-prices-panel"
          v-tt
          data-title="Updates product prices and units from Excel. This can overwrite existing values." />

        <JRButton
          type="button"
          variant="ghost"
          size="sm"
          class="jr-product-list__refresh"
          @click="refreshTable">
          <RefreshIcon />
          Refresh
        </JRButton>
      </div>
    </div>

    <div
      v-if="showBulkPricesPanel && canBulkUpdate"
      class="jr-product-list__bulk">
      <ProductPricesBulkExcelPanel
        id="product-bulk-prices-panel"
        @updated="refreshTable" />
    </div>

    <!-- Mobile: compact scan list, not a squeezed desktop table -->
    <div v-if="isMobile" class="jr-product-list__mobile">
      <JREmptyState
        v-if="!products.length && !isLoading"
        :title="emptyTitle"
        :description="emptyDescription" />
      <p v-if="isLoading && !products.length" class="jr-product-list__loading">
        Loading products…
      </p>
      <p
        v-else-if="isLoading && products.length"
        class="jr-product-list__loading"
        aria-live="polite">
        Updating…
      </p>
      <ul
        v-if="products.length"
        class="jr-product-list__rows"
        :aria-busy="isLoading ? 'true' : 'false'">
        <li v-for="item in products" :key="item.id" class="jr-product-row">
          <div class="jr-product-row__main">
            <button
              type="button"
              class="jr-product-cell"
              :aria-label="`View images of ${item.name}`"
              v-tt
              data-title="View product images"
              @click="openImageGallery(item.id)">
              <img
                v-if="productImageSrc(item)"
                :src="productImageSrc(item)"
                :alt="item.name"
                class="jr-product-cell__img"
                @error="onProductImageError(item)" />
              <span v-else class="jr-product-cell__ph" aria-hidden="true" />
              <span class="jr-product-cell__text">
                <span class="jr-product-cell__name">{{ item.name }}</span>
              </span>
            </button>
            <p class="jr-product-row__meta">
              <span>{{ item.sku }}</span>
              <span v-if="item.category_name" aria-hidden="true">·</span>
              <span v-if="item.category_name">{{ item.category_name }}</span>
            </p>
          </div>
          <div class="jr-product-row__aside">
            <Tag
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
        class="jr-product-list__pager"
        :rows="perPage"
        :totalRecords="totalRows"
        :first="tableFirst"
        template="PrevPageLink CurrentPageReport NextPageLink"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
        @page="onTablePage" />
    </div>

    <!-- Desktop / tablet: dense operational table -->
    <div v-else class="jr-product-list__table">
      <JRDataTable
        :value="products"
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
        tableStyle="min-width: 56rem"
        :emptyTitle="emptyTitle"
        :emptyDescription="emptyDescription"
        @page="onTablePage"
        @sort="onTableSort">
        <Column
          field="id"
          header="Id"
          sortable
          headerClass="jr-col-id"
          bodyClass="jr-col-id" />
        <Column field="name" header="Name" sortable>
          <template #body="{ data }">
            <button
              type="button"
              class="jr-product-cell"
              :aria-label="`View images of ${data.name}`"
              v-tt
              data-title="View product images"
              @click="openImageGallery(data.id)">
              <img
                v-if="productImageSrc(data)"
                :src="productImageSrc(data)"
                :alt="data.name"
                class="jr-product-cell__img"
                @error="onProductImageError(data)" />
              <span v-else class="jr-product-cell__ph" aria-hidden="true" />
              <span class="jr-product-cell__text">
                <span class="jr-product-cell__name">{{ data.name }}</span>
                <span v-if="data.sku" class="jr-product-cell__meta">{{ data.sku }}</span>
              </span>
            </button>
          </template>
        </Column>
        <Column field="sku" header="SKU" sortable />
        <Column field="category_name" header="Category" sortable>
          <template #body="{ data }">
            {{ data.category_name || "—" }}
          </template>
        </Column>
        <Column field="tracking_mode" header="Tracking" sortable>
          <template #body="{ data }">
            <Tag
              v-if="data.tracking_mode === 'SERIALIZED'"
              value="Serial"
              severity="info" />
            <Tag v-else value="Qty" severity="secondary" />
          </template>
        </Column>
        <Column field="default_brand" header="Brand">
          <template #body="{ data }">
            <span v-if="data.default_brand?.name">
              {{ data.default_brand.name }}
              <span v-if="data.brands_count > 1" class="jr-product-list__muted">
                +{{ data.brands_count - 1 }}
              </span>
            </span>
            <span v-else class="jr-product-list__muted">—</span>
          </template>
        </Column>
        <Column
          field="reorder_level"
          header="Reorder"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num" />
        <Column field="unit_name" header="Unit" sortable />
        <Column field="is_active" header="Status" sortable>
          <template #body="{ data }">
            <Tag
              :value="data.is_active ? 'Active' : 'Inactive'"
              :severity="data.is_active ? 'success' : 'secondary'" />
          </template>
        </Column>
        <Column
          v-if="hasRowActions"
          header="Actions"
          :sortable="false"
          headerClass="jr-col-actions"
          bodyClass="jr-col-actions">
          <template #body="{ data }">
            <JRRowActions
              :actions="getRowActions(data)"
              :compact="false"
              :entity-label="data.name" />
          </template>
        </Column>
      </JRDataTable>
    </div>

    <ProductImageGallery
      ref="productImageGallery"
      :productId="selectedProductId" />
  </JRPage>
</template>

<script>
import ProductImageGallery from "@components/inventory/ProductImageGallery.vue";
import ProductPricesBulkExcelPanel from "@components/inventory/ProductPricesBulkExcelPanel.vue";
import axios from "axios";
import {
  ref,
  computed,
  watch,
  onMounted,
  onUnmounted,
  getCurrentInstance,
  nextTick,
} from "vue";
import { useRouter } from "vue-router";
import Column from "primevue/column";
import Paginator from "primevue/paginator";
import EyeIcon from "@primevue/icons/eye";
import PencilIcon from "@primevue/icons/pencil";
import RefreshIcon from "@primevue/icons/refresh";
import TrashIcon from "@primevue/icons/trash";
import Tag from "primevue/tag";
import ToggleButton from "primevue/togglebutton";
import {
  JRPage,
  JRPageHeader,
  JRButton,
  JRSelect,
  JRInput,
  JRDataTable,
  JREmptyState,
  JRRowActions,
} from "@ui";

const ENDPOINT = "/api/products-provider/";
const MOBILE_MQ = "(max-width: 767.98px)";

export default {
  name: "ProductListView",
  components: {
    ProductImageGallery,
    ProductPricesBulkExcelPanel,
    Column,
    Paginator,
    RefreshIcon,
    Tag,
    ToggleButton,
    JRPage,
    JRPageHeader,
    JRButton,
    JRSelect,
    JRInput,
    JRDataTable,
    JREmptyState,
    JRRowActions,
  },

  setup() {
    const router = useRouter();
    const { proxy } = getCurrentInstance();

    const products = ref([]);
    const stats = ref({
      total: 0,
      active: 0,
      inactive: 0,
    });
    const isLoading = ref(true);
    const loadError = ref(false);

    const currentPage = ref(1);
    const perPage = ref(25);
    const filter = ref("");
    const totalRows = ref(0);
    const selectedProductId = ref(null);
    const productImageGallery = ref(null);
    const showBulkPricesPanel = ref(false);
    const sortField = ref("id");
    const sortOrder = ref(-1);
    let searchTimer = null;

    const isMobile = ref(
      typeof window !== "undefined" && window.matchMedia
        ? window.matchMedia(MOBILE_MQ).matches
        : false
    );
    let mediaQuery = null;
    let onMedia = null;

    const pageOptions = [
      { value: 10, label: "10" },
      { value: 25, label: "25" },
      { value: 50, label: "50" },
      { value: 100, label: "100" },
    ];

    const tableFirst = computed(() => (currentPage.value - 1) * perPage.value);
    const emptyTitle = computed(() =>
      loadError.value ? "Could not load products" : "No products"
    );
    const emptyDescription = computed(() =>
      loadError.value ? "Try Refresh." : "No products match the current search."
    );

    const canBulkUpdate = computed(
      () =>
        !!proxy?.hasPermission?.("appinventory.change_product") &&
        !!proxy?.hasPermission?.("appinventory.add_productprice") &&
        !!proxy?.hasPermission?.("appinventory.change_productprice")
    );

    const hasRowActions = computed(
      () =>
        !!proxy?.hasPermission?.("appinventory.view_product") ||
        !!proxy?.hasPermission?.("appinventory.change_product") ||
        !!proxy?.hasPermission?.("appinventory.delete_product")
    );

    const getRowActions = (product) => {
      const actions = [];
      if (proxy?.hasPermission?.("appinventory.view_product")) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => viewItem(product.id),
        });
      }
      if (proxy?.hasPermission?.("appinventory.change_product")) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "info",
          icon: PencilIcon,
          command: () => editItem(product.id),
        });
      }
      if (proxy?.hasPermission?.("appinventory.delete_product")) {
        actions.push({
          key: "delete",
          label: "Delete",
          severity: "danger",
          icon: TrashIcon,
          command: () => deleteItem(product.id),
        });
      }
      return actions;
    };

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
      const fieldMap = {
        id: "id",
        name: "name",
        sku: "sku",
        model_number: "model_number",
        category_name: "category__name",
        tracking_mode: "tracking_mode",
        reorder_level: "reorder_level",
        unit_name: "unit_default__name",
        is_active: "is_active",
      };
      const djangoField = fieldMap[field];
      if (!djangoField) return "-id";
      return desc ? `-${djangoField}` : djangoField;
    };

    const loadProducts = async () => {
      if (!isLoading.value) {
        isLoading.value = true;
      }

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
          if (response.data.stats) {
            stats.value = response.data.stats;
          }
          totalRows.value = response.data.totalRows || 0;
          products.value = response.data.items;
          loadError.value = false;
        } else {
          throw new Error("Invalid response format");
        }
      } catch (error) {
        loadError.value = true;
        products.value = [];
        totalRows.value = 0;
        stats.value = { total: 0, active: 0, inactive: 0 };
        proxy?.notifyError?.("Error loading products.");
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
      loadProducts();
    };

    const onTableSort = (event) => {
      sortField.value = event.sortField || "id";
      sortOrder.value = event.sortOrder ?? -1;
      currentPage.value = 1;
      loadProducts();
    };

    const refreshTable = () => {
      isLoading.value = true;
      loadProducts();
    };

    const goToCreateForm = () => {
      router.push({ name: "product-form", query: { mode: "create" } });
    };

    const viewItem = (id) => {
      router.push({ name: "product-form", query: { mode: "view", id: id } });
    };

    const editItem = (id) => {
      router.push({
        name: "product-form",
        query: { mode: "edit", id: id },
      });
    };

    const deleteItem = (id) => {
      proxy?.confirmDelete?.(
        "Are you sure?",
        `Delete product #${id}? This action cannot be undone.`,
        async () => {
          try {
            await axios.delete(`/api/products/${id}/`);
            proxy?.notifyToastSuccess?.("The product has been deleted.");
            refreshTable();
          } catch (error) {
            const status = error?.response?.status;
            const data = error?.response?.data;

            if (status === 403) {
              proxy?.notifyError?.(
                "You do not have permission for this action."
              );
            } else if (status === 409) {
              const detail =
                data?.detail ||
                "Cannot delete this product because it is being used elsewhere.";
              proxy?.notifyError?.(detail);
            } else {
              const detail = data?.detail || "Error deleting the product.";
              proxy?.notifyError?.(detail);
            }
          }
        }
      );
    };

    const brokenImageIds = ref({});

    const productImageSrc = (product) => {
      if (!product?.id || brokenImageIds.value[product.id]) return "";
      return product.image || "";
    };

    const onProductImageError = (product) => {
      if (!product?.id) return;
      brokenImageIds.value = { ...brokenImageIds.value, [product.id]: true };
    };

    const openImageGallery = (productId) => {
      selectedProductId.value = productId;
      nextTick(() => {
        if (productImageGallery.value) {
          productImageGallery.value.openModal();
        }
      });
    };

    onMounted(() => {
      if (typeof window !== "undefined" && window.matchMedia) {
        mediaQuery = window.matchMedia(MOBILE_MQ);
        isMobile.value = mediaQuery.matches;
        onMedia = (event) => {
          isMobile.value = event.matches;
        };
        if (mediaQuery.addEventListener) {
          mediaQuery.addEventListener("change", onMedia);
        } else {
          mediaQuery.addListener(onMedia);
        }
      }
      loadProducts();
    });

    onUnmounted(() => {
      if (searchTimer) clearTimeout(searchTimer);
      if (mediaQuery && onMedia) {
        if (mediaQuery.removeEventListener) {
          mediaQuery.removeEventListener("change", onMedia);
        } else {
          mediaQuery.removeListener(onMedia);
        }
      }
    });

    watch(perPage, () => {
      currentPage.value = 1;
      loadProducts();
    });

    watch(filter, () => {
      if (searchTimer) clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        currentPage.value = 1;
        loadProducts();
      }, 300);
    });

    return {
      products,
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
      isMobile,
      hasRowActions,
      getRowActions,
      refreshTable,
      onTablePage,
      onTableSort,
      goToCreateForm,
      viewItem,
      editItem,
      deleteItem,
      openImageGallery,
      productImageSrc,
      onProductImageError,
      productImageGallery,
      selectedProductId,
      canBulkUpdate,
      showBulkPricesPanel,
    };
  },
};
</script>

<style scoped>
.jr-product-list__masthead {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.jr-product-list__masthead :deep(.jr-page-header) {
  margin-bottom: 0.25rem;
}

.jr-product-list__create {
  width: 100%;
}

.jr-product-list__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
}

.jr-product-list__summary :deep(.p-tag) {
  font-size: 0.75rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.jr-product-list__toolbar {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.5rem;
  margin: 0 0 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-product-list__search {
  position: relative;
  min-width: 0;
  flex: 1 1 auto;
}

.jr-product-list__bulk-toggle {
  opacity: 0.85;
}

.jr-product-list__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted, #4b5563);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-product-list__search :deep(.p-inputtext) {
  padding-left: 2.25rem;
}

.jr-product-list__cluster {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  align-self: flex-start;
  gap: 0.5rem;
  flex: 0 0 auto;
}

.jr-product-list__entries {
  width: 4.75rem;
  flex: 0 0 auto;
}

.jr-product-list__cluster :deep(.jr-product-list__entries.p-select),
.jr-product-list__cluster :deep(.p-select) {
  width: 4.75rem;
}

.jr-product-list__cluster :deep(.p-togglebutton) {
  flex: 0 0 auto;
  min-height: 2.5rem;
  white-space: nowrap;
}

.jr-product-list__bulk {
  margin-bottom: 1rem;
}

.jr-product-list__loading,
.jr-product-list__muted {
  color: var(--color-jr-muted, #4b5563);
}

.jr-product-list__loading {
  margin: 0;
  padding: 1rem 0;
  font-size: 0.875rem;
}

.jr-product-list__rows {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-product-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-product-row__main {
  min-width: 0;
  flex: 1 1 auto;
  text-align: left;
}

.jr-product-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  max-width: 100%;
  padding: 0;
  border: 0;
  background: none;
  color: inherit;
  font-family: inherit;
  text-align: left;
  cursor: pointer;
}

.jr-product-cell__img,
.jr-product-cell__ph {
  width: 2.5rem;
  height: 2.5rem;
  flex-shrink: 0;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-control, 0.5rem);
  background: var(--color-jr-surface-muted, #f9fafb);
  object-fit: cover;
}

.jr-product-cell__ph {
  display: block;
}

.jr-product-cell__text {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.1rem;
}

.jr-product-cell__name {
  overflow: hidden;
  color: var(--color-jr-primary, #2563eb);
  font-weight: 600;
  font-size: 0.875rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jr-product-cell__meta {
  overflow: hidden;
  color: var(--color-jr-muted, #4b5563);
  font-size: 0.75rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jr-product-cell:hover .jr-product-cell__name {
  color: var(--color-jr-primary-hover, #1d4ed8);
  text-decoration: underline;
}

.jr-product-cell:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 2px;
}

.jr-product-row__meta {
  margin: 0.2rem 0 0 calc(2.5rem + 0.75rem);
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jr-product-row__aside {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.35rem;
  flex-shrink: 0;
}

.jr-product-list__rows[aria-busy="true"] {
  opacity: 0.55;
}

.jr-product-list__pager {
  margin-top: 0.5rem;
}

.jr-product-list__pager :deep(.p-paginator) {
  display: flex;
  flex-wrap: nowrap;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

.jr-product-list__table :deep(.p-datatable) {
  --p-datatable-row-striped-background: var(--color-jr-surface-muted, #f9fafb);
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  background: var(--color-jr-surface, #ffffff);
}

.jr-product-list__table :deep(.p-datatable-table-container) {
  overflow-x: auto;
}

.jr-product-list__table :deep(.p-datatable-thead > tr > th) {
  background: var(--color-jr-surface-muted, #f9fafb);
  color: var(--color-jr-text, #111827);
  font-weight: 600;
}

.jr-product-list__table :deep(.p-datatable-tbody > tr > td) {
  font-size: 0.875rem;
  vertical-align: middle;
  padding-top: 0.3rem;
  padding-bottom: 0.3rem;
}

.jr-product-list__table :deep(.p-tag),
.jr-product-row__aside :deep(.p-tag) {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  padding: 0.1rem 0.4rem;
}

.jr-col-id {
  width: 3.5rem;
  color: var(--color-jr-muted, #4b5563);
  font-variant-numeric: tabular-nums;
}

.jr-col-num {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.jr-col-actions {
  width: 16.5rem;
  text-align: right;
  white-space: nowrap;
}

@media (min-width: 768px) {
  .jr-product-list__masthead {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .jr-product-list__create {
    width: auto;
  }

  .jr-product-list__toolbar {
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
  }

  .jr-product-list__search {
    flex: 0 1 18rem;
    max-width: 18rem;
  }

  .jr-product-list__cluster {
    align-self: center;
  }
}
</style>
