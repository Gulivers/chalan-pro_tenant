<template>
  <div class="low-stock-table">
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
      </div>
      <div class="mt-2">
        <small class="text-muted">Loading products...</small>
      </div>
    </div>
    
    <div v-else-if="products.length === 0" class="text-center py-4">
      <div class="alert alert-success">
        <i class="fas fa-check-circle"></i>
        ✅ All products are above reorder level
      </div>
      <button class="btn btn-outline-primary btn-sm mt-2" @click="showEmptyTable = !showEmptyTable">
        <i class="fas fa-table"></i>
        {{ showEmptyTable ? 'Hide' : 'Show' }} Empty Table
      </button>
    </div>
    
    <div v-else-if="showEmptyTable || products.length > 0" class="table-responsive scrollable-table">
      <table class="table table-hover">
        <thead>
          <tr>
            <th>Name</th>
            <th>SKU</th>
            <th>Current Stock</th>
            <th>Reorder Level</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id" 
              :class="getRowClass(product)">
            <td>
              <strong>{{ product.name }}</strong>
              <br>
              <small class="text-muted">{{ product.category?.name || 'No category' }}</small>
            </td>
            <td>
              <code>{{ product.sku }}</code>
            </td>
            <td>
              <span class="stock-value" :class="getStockClass(product)">
                {{ formatNumber(product.current_stock || product.total_stock || 0) }}
              </span>
            </td>
            <td>
              <span class="reorder-level">
                {{ formatNumber(product.reorder_level || 0) }}
              </span>
            </td>
            <td>
              <span class="badge" :class="getStatusBadgeClass(product)">
                {{ getStatusText(product) }}
              </span>
            </td>
            <td>
              <button class="btn btn-sm btn-outline-primary" 
                      @click="viewProduct(product)"
                      v-if="hasPermission('appinventory.view_product')"
                      title="Ver Transacciones">
                <i class="fas fa-receipt"></i>
                Transacciones
              </button>
              <button class="btn btn-sm btn-outline-warning" 
                      @click="editProduct(product)"
                      v-if="hasPermission('appinventory.change_product')"
                      title="Editar Producto">
                <i class="fas fa-edit"></i>
                Editar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LowStockTable',
  props: {
    products: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      showEmptyTable: false
    }
  },
  methods: {
    formatNumber(value) {
      if (!value) return '0'
      return new Intl.NumberFormat('en-US').format(value)
    },
    
    getRowClass(product) {
      const stock = product.current_stock || product.total_stock || 0
      const reorderLevel = product.reorder_level || 0
      
      if (stock === 0) return 'table-danger'
      if (stock < reorderLevel) return 'table-warning'
      return ''
    },
    
    getStockClass(product) {
      const stock = product.current_stock || product.total_stock || 0
      const reorderLevel = product.reorder_level || 0
      
      if (stock === 0) return 'text-danger font-weight-bold'
      if (stock < reorderLevel) return 'text-warning font-weight-bold'
      return 'text-success'
    },
    
    getStatusBadgeClass(product) {
      const stock = product.current_stock || product.total_stock || 0
      const reorderLevel = product.reorder_level || 0
      
      if (stock === 0) return 'badge-danger'
      if (stock < reorderLevel) return 'badge-warning'
      return 'badge-success'
    },
    
    getStatusText(product) {
      const stock = product.current_stock || product.total_stock || 0
      const reorderLevel = product.reorder_level || 0
      
      if (stock === 0) return 'Out of Stock'
      if (stock < reorderLevel) return 'Low Stock'
      return 'Normal'
    },
    
    viewProduct(product) {
      this.$router.push(`/transactions/form`)
    },
    
    editProduct(product) {
      this.$router.push(`/products/edit/${product.id}`)
    }
  }
}
</script>

<style scoped>
.low-stock-table {
  min-height: 200px;
}

.table {
  margin-bottom: 0;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
  background-color: #f8f9fa;
}

.table td {
  vertical-align: middle;
}

.stock-value {
  font-size: 1.1rem;
  font-weight: 600;
}

.reorder-level {
  font-weight: 500;
  color: #6c757d;
}

.badge {
  font-size: 0.8rem;
  padding: 0.4rem 0.8rem;
}

.table-danger {
  background-color: rgba(220, 53, 69, 0.1);
}

.table-warning {
  background-color: rgba(255, 193, 7, 0.1);
}

.btn {
  margin-right: 5px;
}

.btn:last-child {
  margin-right: 0;
}

/* Spinner fixes */
.spinner-border {
  animation: spinner-border 0.75s linear infinite;
}

@keyframes spinner-border {
  to {
    transform: rotate(360deg);
  }
}

/* Scroll optimizado para muchas filas */
.scrollable-table {
  max-height: 500px;
  overflow-y: auto;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
}

.scrollable-table thead th {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

/* Scroll suave */
.scrollable-table {
  scroll-behavior: smooth;
}

/* Scrollbar personalizado */
.scrollable-table::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.scrollable-table::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;

}

.scrollable-table::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.scrollable-table::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Responsive */
@media (max-width: 768px) {
  .scrollable-table {
    font-size: 0.9rem;
    max-height: 400px;
  }
  
  .btn {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
  }
}
</style>
