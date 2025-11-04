<template>
  <div class="customers-suppliers-export-buttons">
    <div class="row">
      <div class="col-md-6 mb-3">
        <div class="export-card">
          <div class="export-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="export-content">
            <h6>Customers List</h6>
            <p class="text-muted">Complete customers report with metrics</p>
            <button class="btn btn-outline-success" 
                    @click="exportCustomersList"
                    :disabled="isLoading">
              <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="excel-icon">
              Download Excel
            </button>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 mb-3">
        <div class="export-card">
          <div class="export-icon">
            <i class="fas fa-truck"></i>
          </div>
          <div class="export-content">
            <h6>Suppliers List</h6>
            <p class="text-muted">Complete suppliers report with metrics</p>
            <button class="btn btn-outline-warning" 
                    @click="exportSuppliersList"
                    :disabled="isLoading">
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
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="export-content">
            <h6>Comparative Analysis</h6>
            <p class="text-muted">Detailed comparison between customers and suppliers</p>
            <button class="btn btn-outline-info" 
                    @click="exportComparativeAnalysis"
                    :disabled="isLoading">
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
            <h6>Trends</h6>
            <p class="text-muted">Monthly trends analysis</p>
            <button class="btn btn-outline-primary" 
                    @click="exportTrends"
                    :disabled="isLoading">
              <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="excel-icon">
              Download Excel
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner-border text-primary" role="status">
          <span class="sr-only">Generando archivo...</span>
        </div>
        <p class="mt-2">Generando reporte...</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CustomersSuppliersExportButtons',
  props: {
    activeTab: {
      type: String,
      default: 'customers'
    },
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
    async exportCustomersList() {
      await this.performExport('/api/export/customers-list/', 'customers_list')
    },
    
    async exportSuppliersList() {
      await this.performExport('/api/export/suppliers-list/', 'suppliers_list')
    },
    
    async exportComparativeAnalysis() {
      await this.performExport('/api/export/comparative-analysis/', 'comparative_analysis')
    },
    
    async exportTrends() {
      await this.performExport('/api/export/trends/', 'trends_analysis')
    },
    
    async performExport(url, filename) {
      try {
        this.exportLoading = true
        
        const params = new URLSearchParams({
          active_tab: this.activeTab
        })
        
        const response = await axios.get(`${url}?${params.toString()}`, { 
          responseType: 'blob',
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          }
        })
        
        // Verificar que la respuesta sea válida
        if (!response || !response.data) {
          throw new Error('No se recibieron datos del servidor')
        }
        
        // Determinar el tipo de contenido de forma segura
        let contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        if (response.headers && response.headers['content-type']) {
          contentType = response.headers['content-type']
        }
        
        // Crear blob y descargar
        const blob = new Blob([response.data], { 
          type: contentType 
        })
        
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = `${filename}_${this.getCurrentDate()}.xlsx`
        link.click()
        window.URL.revokeObjectURL(link.href)
        
        this.notifyToastSuccess?.('Report downloaded successfully');
        
      } catch (error) {
        console.error('Error exporting data:', error)
        
        // Manejo de errores más específico
        let errorMessage = 'Error generating report'
        
        if (error.response) {
          if (error.response.status === 404) {
            errorMessage = 'Export endpoint not found'
          } else if (error.response.status === 500) {
            errorMessage = 'Server error generating report'
          } else if (error.response.data) {
            try {
              // Intentar leer el error del servidor
              if (typeof error.response.data === 'string') {
                errorMessage = error.response.data
              } else if (error.response.data.error) {
                errorMessage = error.response.data.error
              } else if (error.response.data.message) {
                errorMessage = error.response.data.message
              }
            } catch (e) {
              errorMessage = `Server error: ${error.response.status}`
            }
          }
        } else if (error.request) {
          errorMessage = 'Could not connect to server'
        } else if (error.message) {
          errorMessage = error.message
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
.customers-suppliers-export-buttons {
  position: relative;
}

.excel-icon {
  width: 18px;
  height: 18px;
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

.btn-warning {
  background-color: #ffc107;
  border-color: #ffc107;
  color: #212529;
}

.btn-info {
  background-color: #17a2b8;
  border-color: #17a2b8;
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
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
