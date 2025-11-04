<template>
  <TxCard class="mt-0">
    <!-- Header del card -->
    <template #header>
      <div class="d-flex justify-content-between align-items-center w-100">
        <h6 class="text-primary mb-0">Products</h6>
        <div>
          <button class="btn btn-success" @click="goToCreateForm">+ New Product</button>
        </div>
      </div>
    </template>

    <div class="card-body">
      <!-- Stats Cards -->
      <div class="row mb-3 mt-0">
        <div class="col-md-3">
          <div class="card bg-primary text-white mb-2">
            <div class="card-body text-center py-1">
              <h6 class="mb-0">{{ stats.total }}</h6>
              <small>Total Products</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-success text-white mb-2">
            <div class="card-body text-center py-1">
              <h6 class="mb-0">{{ stats.active }}</h6>
              <small>Active</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card bg-secondary text-white mb-2">
            <div class="card-body text-center py-1">
              <h6 class="mb-0">{{ stats.inactive }}</h6>
              <small>Inactive</small>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card mb-2">
            <div class="card-body text-center py-1">
              <button class="btn btn-outline-success bt-sm py-2 w-100" @click="refreshTable">Refresh List</button>
            </div>
          </div>
        </div>
      </div>

      <!-- User Interface Controls -->
      <div class="row mb-3">
        <div class="col-lg-3 text-start">
          <BFormGroup
            label="entries per page:"
            label-for="per-page-select"
            label-cols-sm="6"
            label-cols-md="6"
            label-cols-lg="6"
            label-align-sm="right"
            label-size="sm"
            class="mb-0 small">
            <BFormSelect
              id="per-page-select"
              v-model="perPage"
              :options="pageOptions"
              size="sm"
              class="form-select-xs" />
          </BFormGroup>
        </div>
        <div class="col-lg-3">  </div>
        <div class="col-lg-6 text-end">
          <BFormGroup
            label="Search:"
            label-for="filter-input"
            label-cols-sm="4"
            label-cols-md="6"
            label-cols-lg="6"
            label-align-sm="text-start"
            label-size="sm"
            class="mb-0">
            <div class="position-relative">
              <div class="search-wrapper">
                <BFormInput 
                  id="filter-input" 
                  v-model="filter" 
                  type="search" 
                  placeholder="Search by name, SKU, or category..." 
                  size="sm" />
              </div>
            </div>
          </BFormGroup>
        </div>
       </div>

       <!-- Main Table with Overlay -->
       <BOverlay 
         :show="isLoading" 
         rounded="sm" 
         opacity="0.85"
         variant="light">
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
            {{ row.item.name }}
          </div>
        </template>

        <!-- Category Column -->
        <template #cell(category_name)="row">
          <div class="text-start">
            {{ row.item.category_name || '—' }}
          </div>
        </template>

        <!-- Default Brand Column -->
        <template #cell(default_brand)="row">
          <div class="text-start">
            <span v-if="row.item.default_brand?.name">
              <span class="badge bg-primary" style="font-size: 0.75rem">{{ row.item.default_brand.name }}</span>
              <small v-if="row.item.brands_count > 1" class="text-muted ms-1">
                ({{ row.item.brands_count }} brands)
              </small>
            </span>
            <span v-else class="text-muted">No brand assigned</span>
          </div>
        </template>

        <!-- Active Column -->
        <template #cell(is_active)="row">
          <span class="badge" :class="row.item.is_active ? 'bg-success' : 'bg-secondary'" style="font-size: 0.75rem">
            {{ row.item.is_active ? 'Active' : 'Inactive' }}
          </span>
        </template>

        <!-- Actions Column -->
        <template #cell(actions)="row">
          <div class="btn-group btn-group-sm">
            <button class="btn btn-outline-success me-1" @click="viewItem(row.item.id)">View</button>
            <button class="btn btn-outline-primary me-1" @click="editItem(row.item.id)">Edit</button>
            <button class="btn btn-outline-danger" @click="deleteItem(row.item.id)">Delete</button>
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
  </TxCard>
</template>

<script>
  import TxCard from '@components/layout/TxCard.vue';
  import '@assets/css/base.css';
  import axios from 'axios';
  import { computed, ref, watch, onMounted, getCurrentInstance } from 'vue';
  import { useRouter } from 'vue-router';

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
  } from 'bootstrap-vue-next';

  // Provider endpoint for server-side rendering
  const ENDPOINT = '/api/products-provider/';

  export default {
    name: 'ProductListView',
    components: {
      TxCard,
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
      const filter = ref('');
      const totalRows = ref(0);

      // Table configuration
      const fields = [
        { key: 'id', label: 'ID', sortable: true, thClass: 'text-center', tdClass: 'text-center' },
        { key: 'name', label: 'Name', sortable: true, thClass: 'text-start' },
        { key: 'sku', label: 'SKU', sortable: true },
        { key: 'category_name', label: 'Category', sortable: true },
        { key: 'default_brand', label: 'Default Brand', sortable: false },
        {
          key: 'reorder_level',
          label: 'Reorder Level',
          sortable: true,
          thClass: 'text-center',
          tdClass: 'text-center',
        },
        { key: 'unit_name', label: 'Default Unit', sortable: true },
        { key: 'is_active', label: 'Active', sortable: true, thClass: 'text-center', tdClass: 'text-center' },
        { key: 'actions', label: 'Actions', sortable: false, thClass: 'text-center', tdClass: 'text-center' },
      ];

      const pageOptions = [
        { value: 10, text: '10' },
        { value: 25, text: '25' },
        { value: 50, text: '50' },
        { value: 100, text: '100' },
      ];

      // Provider function for server-side rendering
      const provider = async context => {
        try {
          console.log('📡 Provider called with context:', context);
          
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
            search: context.filter || '',
            ordering: context.sortBy ? getOrderingFromSortBy(context.sortBy) : '-id',
          });

          const response = await axios.get(`${ENDPOINT}?${params}`);

          if (response.data && response.data.items) {
            // Update stats from server response
            if (response.data.stats) {
              stats.value = response.data.stats;
            }
            totalRows.value = response.data.totalRows || 0;
            lastUpdate.value = new Date().toLocaleString();

            console.log('✅ Provider response:', response.data.items.length, 'items');
            return response.data.items;
          } else {
            throw new Error('Invalid response format');
          }
        } catch (error) {
          console.error('❌ Provider error:', error);
          proxy?.notifyError?.('Error loading products.');
          return [];
        } finally {
          // Add a small delay to show the loading state (minimum 300ms for UX)
          setTimeout(() => {
            isLoading.value = false;
          }, 300);
        }
      };

      // Helper function to convert sortBy to Django ordering
      const getOrderingFromSortBy = sortBy => {
        if (!sortBy) return '-id';

        // Convert Bootstrap Vue Next sortBy format to Django ordering
        const field = Object.keys(sortBy)[0];
        const desc = sortBy[field] === 'desc';
        return desc ? `-${field}` : field;
      };

      // Table reference
      const productTable = ref(null);

      // Page change handler
      const onPageChange = page => {
        console.log('📄 Page changed to:', page);
        currentPage.value = page;
        // The provider will be called automatically by BTable
      };

      // Refresh function for manual refresh
      const refreshTable = () => {
        console.log('🔄 Refreshing table...');
        isLoading.value = true;
        // The provider will be called automatically by BTable
        // We just need to trigger a refresh
        if (productTable.value) {
          productTable.value.refresh();
        }
      };

      // Load products on mount - not needed with provider pattern
      onMounted(async () => {
        console.log('🚀 ProductListView mounted with provider pattern');
      });

      const goToCreateForm = () => {
        // Unificar en una sola ruta con querys
        router.push({ name: 'product-form', query: { mode: 'create' } });
      };

      const viewItem = id => {
        // Navigate to view mode using query parameter
        router.push({ name: 'product-form', query: { mode: 'view', id: id } });
      };

      const editItem = id => {
        // Open in new tab
        const url = router.resolve({ name: 'product-form', query: { mode: 'edit', id: id } });
        window.open(url.href, '_blank');
      };

      const deleteItem = id => {
        // Use the same pattern as BuilderView
        proxy?.confirmDelete?.('Are you sure?', `Delete product #${id}? This action cannot be undone.`, async () => {
          try {
            await axios.delete(`/api/products/${id}/`);
            // Show success toast and refresh table
            proxy?.notifyToastSuccess?.('The product has been deleted.');
            // Refresh the table to show updated data
            refreshTable();
          } catch (error) {
            console.error('Error deleting product:', error);
            const status = error?.response?.status;
            const data = error?.response?.data;

            if (status === 403) {
              proxy?.notifyError?.('You do not have permission for this action.');
            } else if (status === 409) {
              const detail = data?.detail || 'Cannot delete this product because it is being used elsewhere.';
              proxy?.notifyError?.(detail);
            } else {
              const detail = data?.detail || 'Error deleting the product.';
              proxy?.notifyError?.(detail);
            }
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
      };
    },
  };
</script>

<style scoped>
  .table td {
    vertical-align: middle;
  }
  .badge {
    font-size: 0.75rem;
  }
  .card {
    border: none;
  }
  .form-select-sm {
    font-size: 0.75rem;
    padding: 0.2rem 0.4rem;
    height: auto;
  }

  .form-select-xs {
    font-size: 0.7rem;
    padding: 0.15rem 0.3rem;
    height: 1.6rem;
    min-width: 60px;
  }

  .text-muted.small {
    font-size: 0.8rem;
  }

  /* Search clear button styles - copied from BuilderView */
  .search-wrapper { 
    position: relative; 
  }

</style>
