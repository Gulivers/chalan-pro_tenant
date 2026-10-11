<template>
  <JRPage>
    <JRPageHeader title="Products">
      <template #actions>
        <JRButton
          v-if="hasPermission('appinventory.add_product')"
          type="button"
          @click="goToCreateForm">
          + New Product
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-product-list__search">
          <label class="jr-sr-only" for="filter-input">
            Search products
          </label>
          <span class="jr-product-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="filter-input"
            v-model="filter"
            type="search"
            placeholder="Search products..."
            autocomplete="off"
            :spellcheck="false"
            autocapitalize="none"
            autocorrect="off"
            enterkeyhint="search" />
        </div>
      </template>

      <template v-if="!isMobile" #stats>
        <div class="jr-product-list__summary" aria-live="polite">
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
            class="jr-product-list__entries"
            inputId="per-page-select"
            ariaLabel="Entries per page"
            v-model="perPage"
            :options="pageOptions"
            optionLabel="label"
            optionValue="value" />

          <JRButton
            v-if="canBulkUpdate"
            type="button"
            variant="ghost"
            size="sm"
            aria-controls="product-bulk-prices-panel"
            :aria-expanded="showBulkPricesPanel ? 'true' : 'false'"
            v-tt
            data-title="Updates product prices and units from Excel. This can overwrite existing values."
            @click="showBulkPricesPanel = true">
            Bulk Excel
          </JRButton>

          <JRButton
            type="button"
            variant="ghost"
            size="sm"
            class="jr-product-list__refresh"
            @click="refreshTable">
            <RefreshIcon />
            Refresh
          </JRButton>
        </template>
        <template v-else>
          <button
            id="product-list-tools-trigger"
            type="button"
            class="jr-icon-btn"
            aria-label="List tools"
            aria-haspopup="menu"
            :aria-expanded="toolsMenuOpen ? 'true' : 'false'"
            aria-controls="product-list-tools-menu"
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
            id="product-list-tools-menu"
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

    <JRDrawer
      v-if="canBulkUpdate"
      class="jr-product-list__bulk-drawer"
      :visible="showBulkPricesPanel"
      header="Bulk Excel"
      position="right"
      @update:visible="showBulkPricesPanel = $event">
      <ProductPricesBulkExcelPanel @updated="refreshTable" />
    </JRDrawer>

    <!-- Phone: compact scan list, not a squeezed table -->
    <div v-if="isMobile" class="jr-product-list__mobile">
      <JREmptyState
        v-if="!products.length && !isLoading"
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
            <div class="jr-product-cell">
              <span class="jr-product-cell__text">
                <router-link
                  v-if="canViewProduct"
                  class="jr-product-cell__name jr-product-cell__name--link"
                  :to="productViewTo(item.id)"
                  :aria-label="`View ${item.name}`">
                  {{ item.name }}
                </router-link>
                <span v-else class="jr-product-cell__name">{{ item.name }}</span>
              </span>
              <button
                type="button"
                class="jr-product-cell__thumb"
                :aria-label="`View images of ${item.name}`"
                v-tt
                data-title="View product images"
                @click="openImageGallery(item.id)">
                <img
                  v-if="productImageSrc(item)"
                  :src="productImageSrc(item)"
                  alt=""
                  class="jr-product-cell__img"
                  width="44"
                  height="44"
                  loading="lazy"
                  decoding="async"
                  @error="onProductImageError(item)" />
                <span v-else class="jr-product-cell__ph" aria-hidden="true" />
              </button>
            </div>
            <p class="jr-product-row__meta">
              <span>{{ item.sku }}</span>
              <span v-if="item.category_name" aria-hidden="true"> · </span>
              <span v-if="item.category_name">{{ item.category_name }}</span>
              <JRBadge
                v-if="item.tracking_mode === 'SERIALIZED'"
                value="Serial"
                severity="info" />
            </p>
          </div>
          <div class="jr-product-row__aside">
            <span
              class="jr-product-row__stock"
              :class="{ 'jr-product-row__stock--low': isLowStock(item) }"
              :title="isLowStock(item) ? 'Below reorder level' : undefined"
              :aria-label="onHandAriaLabel(item)">
              {{ formatQuantity(item.total_stock) }}
            </span>
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

    <!-- Tablet: short table. Desktop: dense catalog without Id / duplicate SKU -->
    <div
      v-else
      class="jr-product-list__table"
      :aria-busy="isLoading ? 'true' : 'false'">
      <JRDataTable
        :value="products"
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
        <Column field="name" header="Name" sortable>
          <template #body="{ data }">
            <div class="jr-product-cell">
              <span class="jr-product-cell__text">
                <router-link
                  v-if="canViewProduct"
                  class="jr-product-cell__name jr-product-cell__name--link"
                  :to="productViewTo(data.id)"
                  :aria-label="`View ${data.name}`">
                  {{ data.name }}
                </router-link>
                <span v-else class="jr-product-cell__name">{{ data.name }}</span>
                <span
                  v-if="data.sku || data.tracking_mode === 'SERIALIZED'"
                  class="jr-product-cell__meta">
                  <span v-if="data.sku">{{ data.sku }}</span>
                  <JRBadge
                    v-if="data.tracking_mode === 'SERIALIZED'"
                    value="Serial"
                    severity="info" />
                </span>
              </span>
              <button
                type="button"
                class="jr-product-cell__thumb"
                :aria-label="`View images of ${data.name}`"
                v-tt
                data-title="View product images"
                @click="openImageGallery(data.id)">
                <img
                  v-if="productImageSrc(data)"
                  :src="productImageSrc(data)"
                  alt=""
                  class="jr-product-cell__img"
                  width="44"
                  height="44"
                  loading="lazy"
                  decoding="async"
                  @error="onProductImageError(data)" />
                <span v-else class="jr-product-cell__ph" aria-hidden="true" />
              </button>
            </div>
          </template>
        </Column>
        <Column field="category_name" header="Category" sortable>
          <template #body="{ data }">
            {{ data.category_name || "—" }}
          </template>
        </Column>
        <Column v-if="!isTablet" field="default_brand" header="Brand">
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
          v-if="!isTablet"
          field="reorder_level"
          header="Reorder"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            {{ formatQuantity(data.reorder_level) }}
          </template>
        </Column>
        <Column field="unit_name" header="Unit" sortable />
        <Column
          field="total_stock"
          header="On hand"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            <span
              :class="{ 'jr-product-list__stock--low': isLowStock(data) }"
              :title="isLowStock(data) ? 'Below reorder level' : undefined"
              :aria-label="onHandAriaLabel(data)">
              {{ formatQuantity(data.total_stock) }}
            </span>
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

    <JRDialog
      :visible="galleryVisible"
      :header="galleryHeader"
      size="wide"
      :showFooter="false"
      @update:visible="onGalleryVisible">
      <ProductBrandImages
        v-if="selectedProductId"
        :product-id="selectedProductId"
        :readonly="!canMutateProduct"
        @changed="onImagesChanged" />
    </JRDialog>
  </JRPage>
</template>

<script>
import ProductBrandImages from "@components/inventory/ProductBrandImages.vue";
import ProductPricesBulkExcelPanel from "@components/inventory/ProductPricesBulkExcelPanel.vue";
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
  JRDrawer,
  JRDataTable,
  JREmptyState,
  JRRowActions,
  JRDialog,
} from "@ui";

const ENDPOINT = "/api/products-provider/";
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

function formatQuantity(value) {
  if (value === null || value === undefined || value === "") return "—";
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  if (Math.abs(n - Math.round(n)) < 1e-9) {
    return String(Math.round(n));
  }
  return n.toLocaleString("en-US", {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  });
}

function isLowStock(product) {
  const stock = Number(product?.total_stock);
  const reorder = Number(product?.reorder_level);
  if (!Number.isFinite(stock) || !Number.isFinite(reorder)) return false;
  return stock < reorder;
}

function onHandAriaLabel(product) {
  const qty = formatQuantity(product?.total_stock);
  if (isLowStock(product)) {
    return `On hand ${qty}, below reorder level`;
  }
  return `On hand ${qty}`;
}

export default {
  name: "ProductListView",
  components: {
    ProductBrandImages,
    ProductPricesBulkExcelPanel,
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
    JRDrawer,
    JRDataTable,
    JREmptyState,
    JRRowActions,
    JRDialog,
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
    const galleryVisible = ref(false);
    const showBulkPricesPanel = ref(false);
    const toolsMenu = ref(null);
    const toolsMenuOpen = ref(false);
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
    const tableMinWidth = computed(() =>
      isTablet.value ? "min-width: 36rem" : "min-width: 48rem"
    );
    const hasSearch = computed(() => Boolean(filter.value && filter.value.trim()));
    const emptyTitle = computed(() => {
      if (loadError.value) return "Could not load products";
      if (hasSearch.value) return "No matching products";
      return "No products";
    });
    const emptyDescription = computed(() => {
      if (loadError.value) return "Try Refresh.";
      const query = filter.value.trim();
      if (query) return `No products match “${query}”.`;
      return "No products yet.";
    });

    const clearSearch = () => {
      filter.value = "";
      if (typeof document !== "undefined") {
        document.getElementById("filter-input")?.focus();
      }
    };

    const canBulkUpdate = computed(
      () =>
        !!proxy?.hasPermission?.("appinventory.change_product") &&
        !!proxy?.hasPermission?.("appinventory.add_productprice") &&
        !!proxy?.hasPermission?.("appinventory.change_productprice")
    );

    const canViewProduct = computed(() =>
      !!proxy?.hasPermission?.("appinventory.view_product")
    );

    const canMutateProduct = computed(
      () =>
        !!proxy?.hasPermission?.("appinventory.change_product") ||
        !!proxy?.hasPermission?.("appinventory.add_product")
    );

    const hasRowActions = computed(
      () =>
        canViewProduct.value ||
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
          severity: "primary",
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
          command: () => deleteItem(product),
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
        reorder_level: "reorder_level",
        unit_name: "unit_default__name",
        total_stock: "total_stock",
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
        isLoading.value = false;
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

    const toolsMenuModel = computed(() => {
      const items = [
        { label: "Refresh", command: () => refreshTable() },
      ];
      if (canBulkUpdate.value) {
        items.unshift({
          label: "Bulk Excel",
          command: () => {
            showBulkPricesPanel.value = true;
          },
        });
      }
      return items;
    });

    const toggleToolsMenu = (event) => {
      toolsMenu.value?.toggle(event);
    };

    const goToCreateForm = () => {
      router.push({ name: "product-form", query: { mode: "create" } });
    };

    const productViewTo = (id) => ({
      name: "product-form",
      query: { mode: "view", id },
    });

    const viewItem = (id) => {
      router.push(productViewTo(id));
    };

    const editItem = (id) => {
      router.push({
        name: "product-form",
        query: { mode: "edit", id: id },
      });
    };

    const deleteItem = (product) => {
      const id = product?.id;
      const name = product?.name ? `“${product.name}”` : `#${id}`;
      proxy?.confirmDelete?.(
        "Are you sure?",
        `Delete ${name}? This action cannot be undone.`,
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

    const galleryHeader = computed(() => {
      const product = products.value.find(
        (item) => String(item.id) === String(selectedProductId.value)
      );
      return product
        ? `Images · ${product.name}`
        : "Product images";
    });

    const openImageGallery = (productId) => {
      selectedProductId.value = productId;
      galleryVisible.value = true;
    };

    const onGalleryVisible = (visible) => {
      galleryVisible.value = visible;
      if (!visible) selectedProductId.value = null;
    };

    const onImagesChanged = () => {
      const id = selectedProductId.value;
      if (id && brokenImageIds.value[id]) {
        const next = { ...brokenImageIds.value };
        delete next[id];
        brokenImageIds.value = next;
      }
      loadProducts();
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
      loadProducts();
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
      canViewProduct,
      canMutateProduct,
      productViewTo,
      viewItem,
      editItem,
      deleteItem,
      openImageGallery,
      productImageSrc,
      onProductImageError,
      galleryVisible,
      galleryHeader,
      onGalleryVisible,
      onImagesChanged,
      selectedProductId,
      canBulkUpdate,
      showBulkPricesPanel,
      toolsMenu,
      toolsMenuOpen,
      toolsMenuModel,
      toggleToolsMenu,
      formatQuantity,
      isLowStock,
      onHandAriaLabel,
    };
  },
};
</script>

<style scoped>
.jr-product-list__search {
  position: relative;
  min-width: 0;
  width: 100%;
}

.jr-product-list__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-product-list__search-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.jr-product-list__search :deep(.p-inputtext) {
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

.jr-product-list__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  pointer-events: none;
}

:deep(.jr-toolbar__actions .jr-product-list__entries.p-select),
:deep(.jr-toolbar__actions .jr-product-list__entries.jr-control) {
  width: 6.25rem;
  min-width: 6.25rem;
  flex: 0 0 auto;
}

.jr-product-list__loading,
.jr-product-list__muted {
  color: var(--color-jr-muted);
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
  border-top: 1px solid var(--color-jr-border);
}

.jr-product-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-jr-border);
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
  min-width: 0;
  text-align: left;
}

.jr-product-cell__thumb {
  display: grid;
  place-items: center;
  order: -1;
  flex-shrink: 0;
  padding: 0;
  border: 0;
  background: none;
  line-height: 0;
  cursor: pointer;
  border-radius: var(--radius-jr-control);
}

@media (max-width: 767.98px) {
  .jr-product-cell__thumb {
    min-width: 2.75rem;
    min-height: 2.75rem;
  }
}

.jr-product-cell__thumb:hover .jr-product-cell__img,
.jr-product-cell__thumb:hover .jr-product-cell__ph {
  border-color: var(--color-jr-hover-border);
}

.jr-product-cell__thumb:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-product-cell__img,
.jr-product-cell__ph {
  width: 2.5rem;
  height: 2.5rem;
  flex-shrink: 0;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-control);
  background: var(--color-jr-surface-muted);
  object-fit: cover;
}

.jr-product-cell__ph {
  display: block;
  border-style: dashed;
}

.jr-product-cell__text {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.1rem;
}

.jr-product-cell__name {
  overflow: hidden;
  color: var(--color-jr-text);
  font-weight: 600;
  font-size: 0.875rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 767.98px) {
  .jr-product-row {
    align-items: flex-start;
  }

  .jr-product-cell {
    align-items: flex-start;
  }

  .jr-product-cell__name {
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .jr-product-cell__img,
  .jr-product-cell__ph {
    width: 2.75rem;
    height: 2.75rem;
  }
}

a.jr-product-cell__name--link {
  color: var(--color-jr-primary);
  text-decoration: none;
}

a.jr-product-cell__name--link:hover {
  color: var(--color-jr-primary-hover);
  text-decoration: underline;
}

a.jr-product-cell__name--link:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-product-cell__meta {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  overflow: hidden;
  color: var(--color-jr-muted);
  font-size: 0.75rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jr-product-row__meta {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0.2rem 0 0 calc(2.5rem + 0.75rem);
  font-size: 0.75rem;
  color: var(--color-jr-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 767.98px) {
  .jr-product-row__meta {
    margin-left: calc(2.75rem + 0.75rem);
  }
}

.jr-product-row__aside {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.35rem;
  flex-shrink: 0;
}

.jr-product-row__stock {
  font-size: 0.875rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--color-jr-text);
}

.jr-product-row__stock--low,
.jr-product-list__stock--low {
  color: var(--color-jr-warning-text);
}

.jr-product-list__rows[aria-busy="true"] {
  opacity: 0.55;
}

.jr-product-list__pager {
  margin-top: 0.25rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-product-list__pager :deep(.p-paginator),
.jr-product-list__pager :deep(.p-paginator-content) {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.5rem;
  padding: 0.35rem 0;
}

.jr-product-list__pager :deep(.p-paginator-prev),
.jr-product-list__pager :deep(.p-paginator-next) {
  min-width: 2.75rem;
  min-height: 2.75rem;
}

.jr-product-list__pager :deep(.p-paginator-current) {
  flex: 1 1 auto;
  min-width: 0;
  text-align: center;
  font-size: 0.8125rem;
  font-variant-numeric: tabular-nums;
  color: var(--color-jr-muted);
}

.jr-product-list__table :deep(.p-datatable) {
  --p-datatable-row-striped-background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
}

.jr-product-list__table :deep(.p-datatable-table-container) {
  overflow-x: auto;
}

.jr-product-list__table :deep(.p-datatable-thead > tr > th) {
  background: var(--color-jr-surface-muted);
  color: var(--color-jr-text);
  font-size: 0.875rem;
  font-weight: 600;
}

.jr-product-list__table :deep(.p-datatable-mask),
.jr-product-list__table :deep(.p-datatable-loading-overlay) {
  background: color-mix(in srgb, var(--color-jr-surface) 72%, transparent);
}

.jr-product-list__table :deep(.p-datatable-tbody > tr > td) {
  font-size: 0.875rem;
  vertical-align: middle;
  padding-top: 0.3rem;
  padding-bottom: 0.3rem;
}

.jr-product-list__table :deep(th.jr-col-num),
.jr-product-list__table :deep(td.jr-col-num) {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.jr-product-list__table :deep(th.jr-col-actions),
.jr-product-list__table :deep(td.jr-col-actions) {
  width: 16.5rem;
  text-align: center;
  white-space: nowrap;
}

.jr-product-list__table :deep(th.jr-col-actions.jr-col-actions--compact),
.jr-product-list__table :deep(td.jr-col-actions.jr-col-actions--compact) {
  width: 3.25rem;
}

.jr-product-list__table :deep(th.jr-col-actions .p-datatable-column-header-content) {
  display: flex;
  justify-content: center;
  width: 100%;
}

.jr-product-list__table :deep(td.jr-col-actions .jr-row-actions) {
  justify-content: center;
  width: 100%;
}

</style>

<style>
.p-drawer.jr-product-list__bulk-drawer {
  width: min(28rem, 100vw);
}

@media (max-width: 767.98px) {
  .p-drawer.jr-product-list__bulk-drawer {
    width: 100vw;
    max-width: 100vw;
  }
}
</style>
