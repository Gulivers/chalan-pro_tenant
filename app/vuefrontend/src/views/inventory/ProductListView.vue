<template>
  <TxCard class="mt-0">
    <!-- Header del card -->
    <template #header>
      <div
        class="d-flex flex-wrap justify-content-between align-items-center w-100 gap-2">
        <h5 class="text-primary mb-0 fw-semibold listview-title">Products</h5>
        <div>
          <button
            v-if="hasPermission('appinventory.add_product')"
            class="btn btn-success btn-sm"
            @click="goToCreateForm">
            + New Product
          </button>
        </div>
      </div>
    </template>

    <div class="card-body">
      <!-- Toolbar: stats + refresh -->
      <div
        class="listview-toolbar d-flex flex-wrap align-items-center gap-2 mb-3">
        <span class="badge bg-primary stats-badge">
          {{ stats.total }} Total
        </span>
        <span class="badge bg-success stats-badge">
          {{ stats.active }} Active
        </span>
        <span class="badge bg-secondary stats-badge">
          {{ stats.inactive }} Inactive
        </span>
        <span
          class="listview-toolbar-divider d-none d-sm-inline"
          aria-hidden="true"></span>
        <button
          type="button"
          class="btn btn-outline-success btn-sm listview-refresh-btn"
          @click="refreshTable">
          Refresh List
        </button>
      </div>

      <!-- Filters: entries per page + bulk switch (optional) + search -->
      <div class="listview-filters row g-2 g-md-3 mb-2 align-items-end">
        <div class="col-12 col-sm-6 col-lg-3 col-xl-2">
          <BFormGroup
            label="Entries per page:"
            label-for="per-page-select"
            label-size="sm"
            class="mb-0 listview-filter-group">
            <BFormSelect
              id="per-page-select"
              v-model="perPage"
              :options="pageOptions"
              size="sm"
              class="form-select form-select-sm" />
          </BFormGroup>
        </div>
        <div
          v-if="hasPermission('appinventory.add_productprice')"
          class="col-12 col-sm-6 col-lg-4 col-xl-4">
          <BFormGroup
            label="Bulk update prices &amp; units from Excel:"
            label-for="product-list-bulk-prices-switch"
            label-size="sm"
            class="mb-0 listview-filter-group">
            <div
              class="form-check form-switch m-2 d-flex align-items-center bulk-prices-switch-wrap">
              <input
                id="product-list-bulk-prices-switch"
                v-model="showBulkPricesPanel"
                class="form-check-input"
                type="checkbox"
                role="switch"
                :aria-label="
                  showBulkPricesPanel
                    ? 'Disable bulk update panel'
                    : 'Enable bulk update panel'
                "
                aria-controls="product-bulk-prices-panel" />
            </div>
          </BFormGroup>
        </div>
        <div
          class="col-12 col-sm-12 col-lg ms-lg-auto listview-filter-search-col">
          <BFormGroup
            label="Search:"
            label-for="filter-input"
            label-size="sm"
            class="mb-0 listview-filter-group">
            <BFormInput
              id="filter-input"
              v-model="filter"
              type="search"
              placeholder="Search by name, SKU, model #, category, unit, brand..."
              size="sm"
              class="form-control form-control-sm" />
          </BFormGroup>
        </div>
      </div>

      <div
        v-if="
          showBulkPricesPanel && hasPermission('appinventory.add_productprice')
        "
        class="mb-3">
        <ProductPricesBulkExcelPanel
          id="product-bulk-prices-panel"
          @updated="refreshTable" />
      </div>

      <!-- Main Table with Overlay -->
      <BOverlay :show="isLoading" rounded="sm" opacity="0.85" variant="light">
        <template #overlay>
          <div class="text-center">
            <BSpinner type="border" variant="secondary" class="mb-3" />
            <div class="h5 text-primary">Loading Products...</div>
            <div class="text-muted">Please wait while we fetch the data</div>
          </div>
        </template>

        <BTable
          ref="productTable"
          :provider="provider"
          :fields="fields"
          :filter="filter"
          :per-page="perPage"
          :current-page="currentPage"
          no-provider-sorting
          bordered
          hover
          responsive
          striped
          class="table-bordered">
          <!-- ID Column -->
          <template #cell(id)="row">
            <strong>{{ row.item.id }}</strong>
          </template>

          <!-- Name Column -->
          <template #cell(name)="row">
            <div class="text-start">
              <a
                href="#"
                @click.prevent="openImageGallery(row.item.id)"
                class="text-decoration-none text-primary"
                style="cursor: pointer"
                v-tt
                data-title="View product images">
                {{ row.item.name }}
              </a>
            </div>
          </template>

          <template #cell(model_number)="row">
            <div class="text-start text-break small">
              {{
                (row.item.model_number || "").trim()
                  ? row.item.model_number
                  : "—"
              }}
            </div>
          </template>

          <!-- Category Column -->
          <template #cell(category_name)="row">
            <div class="text-start">
              {{ row.item.category_name || "—" }}
            </div>
          </template>

          <!-- Tracking Mode Column -->
          <template #cell(tracking_mode)="row">
            <span
              v-if="row.item.tracking_mode === 'SERIALIZED'"
              class="badge bg-info"
              style="font-size: 0.75rem">
              SERIALIZED
            </span>
            <span v-else class="badge bg-secondary" style="font-size: 0.75rem">
              QUANTITY
            </span>
          </template>

          <!-- Default Brand Column -->
          <template #cell(default_brand)="row">
            <div class="text-start">
              <span v-if="row.item.default_brand?.name">
                <span class="badge bg-primary" style="font-size: 0.75rem">
                  {{ row.item.default_brand.name }}
                </span>
                <small v-if="row.item.brands_count > 1" class="text-muted ms-1">
                  ({{ row.item.brands_count }} brands)
                </small>
              </span>
              <span v-else class="text-muted">No brand assigned</span>
            </div>
          </template>

          <!-- Active Column -->
          <template #cell(is_active)="row">
            <span
              class="badge"
              :class="row.item.is_active ? 'bg-success' : 'bg-secondary'"
              style="font-size: 0.75rem">
              {{ row.item.is_active ? "Active" : "Inactive" }}
            </span>
          </template>

          <!-- Actions Column -->
          <template #cell(actions)="row">
            <div class="btn-group btn-group-sm">
              <button
                v-if="hasPermission('appinventory.view_product')"
                class="btn btn-outline-success me-1"
                @click="viewItem(row.item.id)">
                View
              </button>
              <button
                v-if="hasPermission('appinventory.change_product')"
                class="btn btn-outline-primary me-1"
                @click="editItem(row.item.id)">
                Edit
              </button>
              <button
                v-if="hasPermission('appinventory.delete_product')"
                class="btn btn-outline-danger"
                @click="deleteItem(row.item.id)">
                Delete
              </button>
            </div>
          </template>
        </BTable>
      </BOverlay>

      <!-- Pagination -->
      <div class="d-flex justify-content-end mt-3">
        <BPagination
          v-model="currentPage"
          :total-rows="totalRows"
          :per-page="perPage"
          @update:model-value="onPageChange" />
      </div>
    </div>

    <!-- Product Image Gallery Modal -->
    <ProductImageGallery
      ref="productImageGallery"
      :productId="selectedProductId" />
  </TxCard>
</template>

<script>
import TxCard from "@components/layout/TxCard.vue";
import ProductImageGallery from "@components/inventory/ProductImageGallery.vue";
import ProductPricesBulkExcelPanel from "@components/inventory/ProductPricesBulkExcelPanel.vue";
import "@assets/css/base.css";
import axios from "axios";
import {
  computed,
  ref,
  watch,
  onMounted,
  getCurrentInstance,
  nextTick,
} from "vue";
import { useRouter } from "vue-router";

// Bootstrap Vue Next components
import {
  BTable,
  BFormGroup,
  BFormInput,
  BInputGroup,
  BInputGroupText,
  BButton,
  BFormSelect,
  BPagination,
  BOverlay,
  BSpinner,
} from "bootstrap-vue-next";

// Provider endpoint for server-side rendering
const ENDPOINT = "/api/products-provider/";

export default {
  name: "ProductListView",
  components: {
    TxCard,
    ProductImageGallery,
    ProductPricesBulkExcelPanel,
    BTable,
    BFormGroup,
    BFormInput,
    BInputGroup,
    BInputGroupText,
    BButton,
    BFormSelect,
    BPagination,
    BOverlay,
    BSpinner,
  },

  setup() {
    const router = useRouter();
    const { proxy } = getCurrentInstance();

    // Reactive data
    const products = ref([]);
    const stats = ref({
      total: 0,
      active: 0,
      inactive: 0,
    });
    const lastUpdate = ref(null);
    const isLoading = ref(true); // Start with loading state

    // Table controls
    const currentPage = ref(1);
    const perPage = ref(25);
    const filter = ref("");
    const totalRows = ref(0);
    const selectedProductId = ref(null);
    const productImageGallery = ref(null);
    const showBulkPricesPanel = ref(false);

    // Table configuration
    const fields = [
      {
        key: "id",
        label: "ID",
        sortable: true,
        thClass: "text-center",
        tdClass: "text-center",
      },
      { key: "name", label: "Name", sortable: true, thClass: "text-start" },
      { key: "sku", label: "SKU", sortable: true },
      {
        key: "model_number",
        label: "Model #",
        sortable: true,
        thClass: "text-start",
        tdClass: "text-start",
      },
      { key: "category_name", label: "Category", sortable: true },
      {
        key: "tracking_mode",
        label: "Tracking",
        sortable: true,
        thClass: "text-center",
        tdClass: "text-center",
      },
      { key: "default_brand", label: "Default Brand", sortable: false },
      {
        key: "reorder_level",
        label: "Reorder Level",
        sortable: true,
        thClass: "text-center",
        tdClass: "text-center",
      },
      { key: "unit_name", label: "Default Unit", sortable: true },
      {
        key: "is_active",
        label: "Status",
        sortable: true,
        thClass: "text-center",
        tdClass: "text-center",
      },
      {
        key: "actions",
        label: "Actions",
        sortable: false,
        thClass: "text-center",
        tdClass: "text-center",
        thStyle: { width: "12%", whiteSpace: "nowrap" },
        tdStyle: { whiteSpace: "nowrap" },
      },
    ];

    const pageOptions = [
      { value: 10, text: "10" },
      { value: 25, text: "25" },
      { value: 50, text: "50" },
      { value: 100, text: "100" },
    ];

    // Provider function for server-side rendering
    const provider = async (context) => {
      try {
        console.log("📡 Provider called with context:", context);

        // Only show loading if not already loading (avoid flickering)
        if (!isLoading.value) {
          isLoading.value = true;
        }

        // Use context values for pagination (from BTable provider context)
        const page = context.currentPage || 1;
        const perPageValue = context.perPage || 25;

        const params = new URLSearchParams({
          page: page,
          per_page: perPageValue,
          search: context.filter || "",
          ordering: context.sortBy
            ? getOrderingFromSortBy(context.sortBy)
            : "-id",
        });

        const response = await axios.get(`${ENDPOINT}?${params}`);

        if (response.data && response.data.items) {
          // Update stats from server response
          if (response.data.stats) {
            stats.value = response.data.stats;
          }
          totalRows.value = response.data.totalRows || 0;
          lastUpdate.value = new Date().toLocaleString();

          console.log(
            "✅ Provider response:",
            response.data.items.length,
            "items"
          );
          return response.data.items;
        } else {
          throw new Error("Invalid response format");
        }
      } catch (error) {
        console.error("❌ Provider error:", error);
        proxy?.notifyError?.("Error loading products.");
        return [];
      } finally {
        // Add a small delay to show the loading state (minimum 300ms for UX)
        setTimeout(() => {
          isLoading.value = false;
        }, 300);
      }
    };

    // Helper function to convert sortBy to Django ordering
    // Bootstrap Vue Next passes sortBy as array: [{key: 'id', order: 'desc'}]
    const getOrderingFromSortBy = (sortBy) => {
      if (!sortBy) return "-id";

      let field;
      let desc = false;

      if (Array.isArray(sortBy) && sortBy.length > 0) {
        const first = sortBy[0];
        field = first.key ?? first.field;
        const order = first.order ?? (first.sortDesc ? "desc" : "asc");
        desc = order === "desc";
      } else if (typeof sortBy === "object" && !Array.isArray(sortBy)) {
        field = Object.keys(sortBy)[0];
        desc = sortBy[field] === "desc";
      }

      if (!field) return "-id";
      // Map API field names to Django model ordering (category_name -> category__name)
      const fieldMap = { category_name: "category__name" };
      const djangoField = fieldMap[field] ?? field;
      return desc ? `-${djangoField}` : djangoField;
    };

    // Table reference
    const productTable = ref(null);

    // Page change handler
    const onPageChange = (page) => {
      console.log("📄 Page changed to:", page);
      currentPage.value = page;
      // The provider will be called automatically by BTable
    };

    // Refresh function for manual refresh
    const refreshTable = () => {
      console.log("🔄 Refreshing table...");
      isLoading.value = true;
      // The provider will be called automatically by BTable
      // We just need to trigger a refresh
      if (productTable.value) {
        productTable.value.refresh();
      }
    };

    // Load products on mount - not needed with provider pattern
    onMounted(async () => {
      console.log("🚀 ProductListView mounted with provider pattern");
    });

    const goToCreateForm = () => {
      // Unificar en una sola ruta con querys
      router.push({ name: "product-form", query: { mode: "create" } });
    };

    const viewItem = (id) => {
      // Navigate to view mode using query parameter
      router.push({ name: "product-form", query: { mode: "view", id: id } });
    };

    const editItem = (id) => {
      router.push({
        name: "product-form",
        query: { mode: "edit", id: id },
      });
    };

    const deleteItem = (id) => {
      // Use the same pattern as BuilderView
      proxy?.confirmDelete?.(
        "Are you sure?",
        `Delete product #${id}? This action cannot be undone.`,
        async () => {
          try {
            await axios.delete(`/api/products/${id}/`);
            // Show success toast and refresh table
            proxy?.notifyToastSuccess?.("The product has been deleted.");
            // Refresh the table to show updated data
            refreshTable();
          } catch (error) {
            console.error("Error deleting product:", error);
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

    const openImageGallery = (productId) => {
      console.log("🖼️ openImageGallery llamado con productId:", productId);
      console.log(
        "📦 Producto completo:",
        products.value.find((p) => p.id === productId) ||
          "No encontrado en products array"
      );

      selectedProductId.value = productId;
      console.log(
        "✅ selectedProductId actualizado a:",
        selectedProductId.value
      );
      console.log(
        "🔗 URL de la galería sería: /api/products/" + productId + "/images/"
      );

      // Esperar al siguiente tick para asegurar que el componente esté montado
      nextTick(() => {
        console.log("⏱️ nextTick ejecutado");
        console.log(
          "🔍 productImageGallery.value existe?",
          !!productImageGallery.value
        );

        if (productImageGallery.value) {
          console.log("🚀 Llamando a openModal()");
          productImageGallery.value.openModal();
        } else {
          console.error("❌ productImageGallery.value es null o undefined");
        }
      });
    };

    return {
      // Data
      products,
      stats,
      lastUpdate,
      isLoading,

      // Table controls
      currentPage,
      perPage,
      filter,
      totalRows,

      // Table reference
      productTable,

      // Configuration
      fields,
      pageOptions,

      // Provider
      provider,

      // Methods
      refreshTable,
      onPageChange,
      goToCreateForm,
      viewItem,
      editItem,
      deleteItem,
      openImageGallery,
      productImageGallery,
      selectedProductId,
      showBulkPricesPanel,
    };
  },
};
</script>

<style scoped>
/* Listview header: toolbar + filters */
.listview-title {
  font-size: 1.1rem;
  letter-spacing: -0.01em;
}
.listview-toolbar {
  padding: 0.5rem 0.75rem;
  background-color: rgba(13, 110, 253, 0.06);
  border: 1px solid rgba(13, 110, 253, 0.12);
  border-radius: 0.375rem;
}
.listview-toolbar .stats-badge {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  line-height: 1.2;
}
.listview-toolbar-divider {
  width: 1px;
  height: 1.25rem;
  background-color: rgba(0, 0, 0, 0.12);
  margin: 0 0.15rem;
}
.listview-refresh-btn {
  padding: 0.2rem 0.6rem;
  font-size: 0.8rem;
}
.listview-filters .listview-filter-group label {
  font-size: 0.8rem;
  color: var(--bs-secondary-color);
}
.table td {
  vertical-align: middle;
}
.badge {
  font-size: 0.75rem;
}
.card {
  border: none;
}
.form-select-sm,
.form-control-sm {
  font-size: 0.8rem;
}
/* Search ocupa el resto de la fila de filtros; ancho mínimo legible */
.listview-filter-search-col {
  min-width: min(100%, 240px);
}
/* Alinea la altura del switch con form-select-sm / form-control-sm (~31px) */
.bulk-prices-switch-wrap {
  min-height: 31px;
  justify-content: center;
}
.text-muted.small {
  font-size: 0.8rem;
}
</style>
