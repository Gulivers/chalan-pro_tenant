<template>
  <div class="product-movements-report">
    <!-- Filters -->
    <div class="filters-section mb-4">
      <div class="card">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="fas fa-filter"></i>
            Search Filters
          </h6>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-3 mb-3">
              <label class="form-label">Date From</label>
              <input type="date" 
                     v-model="filters.startDate" 
                     class="form-control form-control-sm"
                     @change="onFilterChange">
            </div>
            <div class="col-md-3 mb-3">
              <label class="form-label">Date To</label>
              <input type="date" 
                     v-model="filters.endDate" 
                     class="form-control form-control-sm"
                     @change="onFilterChange">
            </div>
            <div class="col-md-3 mb-3">
              <label class="form-label">Document Type</label>
              <select v-model="filters.documentType" 
                      class="form-control form-control-sm"
                      @change="onFilterChange">
                <option value="">All</option>
                <option v-for="docType in documentTypes" 
                        :key="docType.id" 
                        :value="docType.id">
                  {{ docType.description }}
                </option>
              </select>
            </div>
            <div class="col-md-3 mb-3">
              <label class="form-label">Warehouse</label>
              <select v-model="filters.warehouseId" 
                      class="form-control form-control-sm"
                      @change="onFilterChange">
                <option value="">All</option>
                <option v-for="warehouse in warehouses" 
                        :key="warehouse.id" 
                        :value="warehouse.id">
                  {{ warehouse.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="row">
            <div class="col-md-12 text-right">
              <button class="btn btn-primary btn-sm my-2 mx-2" @click="applyFilters">
                Search
              </button>
              <button class="btn btn-secondary btn-sm" @click="resetFilters">
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Movements table -->
    <div class="movements-table">
      <div class="card">
        <div class="card-header">
          <div class="d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="fas fa-exchange-alt"></i>
              Product Movements
            </h6>
            <div class="export-buttons">
              <button class="btn btn-outline-success btn-sm" 
                      @click="exportToExcel"
                      :disabled="loading">
                  <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="me-1" />
                  Download Excel
              </button>
            </div>
          </div>
        </div>
        <div class="card-body">
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
            </div>
            <div class="mt-2">
              <small class="text-muted">Loading products...</small>
            </div>
          </div>
          
          <div v-else-if="movements.length === 0" class="text-center py-4">
            <div class="alert alert-info">
              <i class="fas fa-info-circle"></i>
              No movements found with the applied filters
            </div>
          </div>
          
          <div v-else class="table-responsive">
            <table class="table table-hover table-sm">
              <thead class="table-light">
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Type</th>
                  <th>Product</th>
                  <th>SKU</th>
                  <th>Quantity</th>
                  <th>Warehouse</th>
                  <th>Document</th>
                  <th>User</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="movement in movements" 
                    :key="movement.id"
                    :class="getMovementRowClass(movement)">
                  <td>{{ formatDate(movement.date) }}</td>
                  <td>{{ formatTime(movement.time) }}</td>
                  <td>
                    <span class="badge" :class="getMovementBadgeClass(movement)">
                      {{ movement.movement_type }}
                    </span>
                  </td>
                  <td>
                    <strong>{{ movement.product.name }}</strong>
                    <br>
                    <small class="text-muted">{{ movement.product.sku }}</small>
                  </td>
                  <td><code>{{ movement.product.sku }}</code></td>
                  <td>
                    <span :class="getQuantityClass(movement)">
                      {{ formatNumber(movement.quantity) }}
                    </span>
                  </td>
                  <td>{{ movement.warehouse.name }}</td>
                  <td>
                    <code>{{ movement.document || 'N/A' }}</code>
                  </td>
                  <td>
                    <small class="text-muted">
                      {{ movement.created_by.username }}
                    </small>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ProductMovementsReport',
  props: {
    // Removed movements and loading props - component will manage its own data
  },
  data() {
    return {
      filters: {
        startDate: this.getDefaultStartDate(),
        endDate: this.getDefaultEndDate(),
        documentType: '',
        warehouseId: ''
      },
      warehouses: [],
      documentTypes: [],
      movements: [],
      loading: false
    }
  },
  async mounted() {
    await this.loadWarehouses()
    await this.loadDocumentTypes()
    this.applyFilters()
  },
  methods: {
    getDefaultStartDate() {
      const date = new Date()
      date.setDate(date.getDate() - 30)
      return date.toISOString().split('T')[0]
    },
    
    getDefaultEndDate() {
      return new Date().toISOString().split('T')[0]
    },
    
    async loadWarehouses() {
      try {
        console.log('Loading warehouses...')
        const response = await axios.get('/api/warehouses/?is_active=true')
        console.log('Warehouses response:', response.data)
        this.warehouses = response.data.results || response.data
        console.log('Warehouses loaded:', this.warehouses)
      } catch (error) {
        console.error('Error loading warehouses:', error)
      }
    },
    
    async loadDocumentTypes() {
      try {
        console.log('Loading document types...')
        const response = await axios.get('/api/document-types/?is_active=true')
        console.log('Document types response:', response.data)
        this.documentTypes = response.data.results || response.data
        console.log('Document types loaded:', this.documentTypes)
      } catch (error) {
        console.error('Error loading document types:', error)
      }
    },
    
    async loadMovements() {
      try {
        this.loading = true
        console.log('Loading movements with filters:', this.filters)
        
        // Build query parameters
        const params = new URLSearchParams({
          start_date: this.filters.startDate,
          end_date: this.filters.endDate
        })
        
        if (this.filters.documentType) {
          params.append('document_type', this.filters.documentType)
        }
        
        if (this.filters.warehouseId) {
          params.append('warehouse_id', this.filters.warehouseId)
        }
        
        const url = `/api/dashboard/product-movements/?${params.toString()}`
        console.log('Requesting movements from:', url)
        
        const response = await axios.get(url)
        console.log('Movements response:', response.data)
        
        this.movements = Array.isArray(response.data) ? response.data : []
        console.log('Movements loaded:', this.movements.length, 'records')
        
      } catch (error) {
        console.error('Error loading movements:', error)
        this.movements = []
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      // Mostrar la fecha como string directamente sin conversión de zona horaria
      // El backend envía fechas en formato ISO YYYY-MM-DD
      if (typeof dateString === 'string') {
        // Si viene en formato ISO completo (YYYY-MM-DDTHH:MM:SS), extraer solo la fecha
        const datePart = dateString.split('T')[0] // Extraer YYYY-MM-DD
        const [year, month, day] = datePart.split('-')
        return `${month}/${day}/${year}` // Formato MM/DD/YYYY
      }
      // Fallback para otros formatos (no debería ocurrir con nuestro backend)
      console.warn('Unexpected date format:', dateString)
      return 'N/A'
    },
    
    formatTime(timeString) {
      if (!timeString) return 'N/A'
      return timeString.substring(0, 5) // HH:MM
    },
    
    formatNumber(value) {
      if (!value) return '0'
      return new Intl.NumberFormat('en-US').format(value)
    },
    
    getMovementRowClass(movement) {
      if (movement.movement_type === 'Entrada') return 'table-success'
      if (movement.movement_type === 'Salida') return 'table-danger'
      return 'table-warning'
    },
    
    getMovementBadgeClass(movement) {
      if (movement.movement_type === 'Entrada') return 'badge-success'
      if (movement.movement_type === 'Salida') return 'badge-danger'
      return 'badge-warning'
    },
    
    getQuantityClass(movement) {
      if (movement.quantity > 0) return 'text-success font-weight-bold'
      if (movement.quantity < 0) return 'text-danger font-weight-bold'
      return 'text-muted font-weight-bold'
    },
    
    onFilterChange() {
      // Auto-aplicar filtros cuando cambien
      this.applyFilters()
    },
    
    applyFilters() {
      this.loadMovements()
    },
    
    resetFilters() {
      this.filters = {
        startDate: this.getDefaultStartDate(),
        endDate: this.getDefaultEndDate(),
        documentType: '',
        warehouseId: ''
      }
      this.applyFilters()
    },
    
    async exportToExcel() {
      try {
        const params = new URLSearchParams({
          start_date: this.filters.startDate,
          end_date: this.filters.endDate
        })
        if (this.filters.documentType) params.append('document_type', this.filters.documentType)
        if (this.filters.warehouseId) params.append('warehouse_id', this.filters.warehouseId)

        // Correct endpoint and authenticated blob download
        const url = `/api/export/product-movements/?${params.toString()}`
        const response = await axios.get(url, {
          responseType: 'blob',
          headers: {
            Authorization: `Token ${localStorage.getItem('authToken')}`
          }
        })

        if (!response || !response.data) throw new Error('No data received')

        const contentType = (response.headers && response.headers['content-type']) || 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        const blob = new Blob([response.data], { type: contentType })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = `product_movements_report_${new Date().toISOString().split('T')[0]}.xlsx`
        link.click()
        window.URL.revokeObjectURL(link.href)
      } catch (error) {
        console.error('Error exporting to Excel:', error)
        alert('Error exporting to Excel. Please try again.')
      }
    }
  }
}
</script>

<style scoped>
.product-movements-report {
  min-height: 400px;
}

.filters-section .card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filters-section .card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #dee2e6;
  border-radius: 12px 12px 0 0 !important;
}

.movements-table .card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.movements-table .card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #dee2e6;
  border-radius: 12px 12px 0 0 !important;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
  background-color: #f8f9fa;
  font-size: 0.9rem;
}

.table td {
  vertical-align: middle;
  font-size: 0.9rem;
}

.badge {
  font-size: 0.75rem;
  padding: 0.3rem 0.6rem;
}

.table-success {
  background-color: rgba(40, 167, 69, 0.1);
}

.table-danger {
  background-color: rgba(220, 53, 69, 0.1);
}

.table-warning {
  background-color: rgba(255, 193, 7, 0.1);
}

.form-label {
  font-weight: 500;
  color: #495057;
  font-size: 0.9rem;
}

.form-control-sm {
  border-radius: 6px;
  border: 1px solid #ced4da;
}

.btn-sm {
  border-radius: 6px;
  font-size: 0.8rem;
  padding: 0.4rem 0.8rem;
}

/* Responsive */
@media (max-width: 768px) {
  .filters-section .card-body {
    padding: 15px;
  }
  
  .movements-table .card-body {
    padding: 15px;
  }
  
  .table-responsive {
    font-size: 0.8rem;
  }
  
  .export-buttons {
    margin-top: 10px;
  }
  
  .export-buttons .btn {
    width: 100%;
    margin-bottom: 5px;
  }
}

@media (max-width: 576px) {
  .filters-section .row .col-md-3 {
    margin-bottom: 15px;
  }
  
  .table th,
  .table td {
    padding: 0.5rem 0.3rem;
    font-size: 0.8rem;
  }
}
</style>
