<template>
  <div class="stock-export-buttons">
    <div class="row">
      <div class="col-md-6 mb-3">
        <div class="export-card">
          <div class="export-icon">
            <i class="fas fa-warehouse"></i>
          </div>
          <div class="export-content">
            <h6>Stock by Warehouse</h6>
            <p class="text-muted">Export current stock grouped by warehouse</p>
            <button class="btn btn-outline-success" 
                    @click="exportStockByWarehouse"
                    :disabled="loading">
              <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="excel-icon">
              Download Excel
            </button>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 mb-3">
        <div class="export-card">
          <div class="export-icon">
            <i class="fas fa-boxes"></i>
          </div>
          <div class="export-content">
            <h6>Complete Stock</h6>
            <p class="text-muted">Export entire inventory with details</p>
            <button class="btn btn-outline-primary" 
                    @click="exportCompleteStock"
                    :disabled="loading">
              <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="excel-icon">
              Download Excel
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="row">
      <div class="col-md-6 mb-3">
        <div class="export-card">
          <div class="export-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="export-content">
            <h6>Low Stock Products</h6>
            <p class="text-muted">Only products below reorder level</p>
            <button class="btn btn-outline-warning" 
                    @click="exportLowStockProducts"
                    :disabled="loading">
              <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="excel-icon">
              Download Excel
            </button>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 mb-3">
        <div class="export-card">
          <div class="export-icon">
            <i class="fas fa-chart-bar"></i>
          </div>
          <div class="export-content">
            <h6>Stock Report</h6>
            <p class="text-muted">Complete report with analysis</p>
            <button class="btn btn-outline-info" 
                    @click="exportStockReport"
                    :disabled="loading">
              <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="excel-icon">
              Download Excel
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
      </div>
      <div class="mt-2">
        <small class="text-muted">Loading products...</small>
      </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'StockExportButtons',
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      exportLoading: false
    }
  },
  methods: {
    async exportStockByWarehouse() {
      await this.performExport('/api/export/stock-by-warehouse/', 'stock_por_almacen')
    },
    
    async exportCompleteStock() {
      await this.performExport('/api/export/complete-stock/', 'stock_completo')
    },
    
    async exportLowStockProducts() {
      await this.performExport('/api/export/low-stock-products/', 'productos_stock_bajo')
    },
    
    async exportStockReport() {
      await this.performExport('/api/export/stock-report/', 'reporte_stock')
    },
    
    async performExport(url, filename) {
      try {
        this.exportLoading = true
        
        const response = await axios.get(url, { 
          responseType: 'blob' 
        })
        
        // Crear blob y descargar
        const blob = new Blob([response.data], { 
          type: response.headers['content-type'] 
        })
        
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = `${filename}_${this.getCurrentDate()}.xlsx`
        link.click()
        window.URL.revokeObjectURL(link.href)
        
        this.notifyToastSuccess?.('Stock report downloaded successfully');
        
      } catch (error) {
        console.error('Error exporting data:', error)
        
        // Manejo seguro de errores
        let errorMessage = 'Error generating Excel file'
        
        if (error.response) {
          // El servidor respondió con un código de error
          if (error.response.data && error.response.data.error) {
            errorMessage = error.response.data.error
          } else if (error.response.status === 404) {
            errorMessage = 'Export endpoint not found'
          } else if (error.response.status === 500) {
            errorMessage = 'Server error while generating file'
          } else {
            errorMessage = `Server error: ${error.response.status}`
          }
        } else if (error.request) {
          // La petición fue hecha pero no hubo respuesta
          errorMessage = 'No response from server'
        } else {
          // Algo más pasó
          errorMessage = error.message || 'Unknown error occurred'
        }
        
        alert(errorMessage)
      } finally {
        this.exportLoading = false
      }
    },
    
    getCurrentDate() {
      const now = new Date()
      return now.toISOString().split('T')[0]
    }
  },
  computed: {
    isLoading() {
      return this.loading || this.exportLoading
    }
  }
}
</script>

<style scoped>
.stock-export-buttons {
  position: relative;
}

.excel-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  vertical-align: middle;
}

.export-card {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 12px;
  padding: 25px;
  height: 100%;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.export-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.export-icon {
  font-size: 2.5rem;
  color: #6c757d;
  min-width: 60px;
  text-align: center;
}

.export-content {
  flex: 1;
}

.export-content h6 {
  color: #495057;
  font-weight: 600;
  margin-bottom: 8px;
}

.export-content p {
  font-size: 0.9rem;
  margin-bottom: 15px;
  line-height: 1.4;
}

.btn {
  border-radius: 8px;
  font-weight: 500;
  padding: 10px 20px;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn-success {
  background-color: #28a745;
  border-color: #28a745;
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.btn-warning {
  background-color: #ffc107;
  border-color: #ffc107;
  color: #212529;
}

.btn-info {
  background-color: #17a2b8;
  border-color: #17a2b8;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  z-index: 1000;
}

.loading-content {
  text-align: center;
}

.loading-content p {
  color: #6c757d;
  font-weight: 500;
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .export-card {
    flex-direction: column;
    text-align: center;
    gap: 15px;
    padding: 20px;
  }
  
  .export-icon {
    font-size: 2rem;
    min-width: auto;
  }
  
  .btn {
    width: 100%;
  }
}

@media (max-width: 576px) {
  .export-card {
    padding: 15px;
  }
  
  .export-icon {
    font-size: 1.8rem;
  }
  
  .export-content h6 {
    font-size: 1rem;
  }
  
  .export-content p {
    font-size: 0.8rem;
  }
}
</style>
