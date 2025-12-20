<template>
  <div class="additional-reports-grid">
    <div class="row">
      <!-- Stock por Categoría -->
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="report-card" @click="requestReport('stock-by-category')">
          <div class="report-icon">
            <i class="fas fa-boxes"></i>
          </div>
          <div class="report-content">
            <h6>Stock por Categoría</h6>
            <p class="text-muted">Inventario agrupado por categorías de productos</p>
            <div class="report-actions">
              <button class="btn btn-outline-primary btn-sm" 
                      @click.stop="requestReport('stock-by-category')"
                      :disabled="loading">
                <i class="fas fa-chart-pie"></i>
                Ver Reporte
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Rotación de Inventario -->
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="report-card" @click="requestReport('inventory-turnover')">
          <div class="report-icon">
            <i class="fas fa-sync-alt"></i>
          </div>
          <div class="report-content">
            <h6>Rotación de Inventario</h6>
            <p class="text-muted">Análisis de velocidad de rotación de productos</p>
            <div class="report-actions">
              <button class="btn btn-outline-info btn-sm" 
                      @click.stop="requestReport('inventory-turnover')"
                      :disabled="loading">
                <i class="fas fa-chart-line"></i>
                Ver Reporte
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Análisis ABC -->
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="report-card" @click="requestReport('abc-analysis')">
          <div class="report-icon">
            <i class="fas fa-chart-bar"></i>
          </div>
          <div class="report-content">
            <h6>Análisis ABC</h6>
            <p class="text-muted">Clasificación de productos por valor e importancia</p>
            <div class="report-actions">
              <button class="btn btn-outline-success btn-sm" 
                      @click.stop="requestReport('abc-analysis')"
                      :disabled="loading">
                <i class="fas fa-chart-bar"></i>
                Ver Reporte
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- KPIs del Inventario -->
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="report-card" @click="requestReport('inventory-kpis')">
          <div class="report-icon">
            <i class="fas fa-tachometer-alt"></i>
          </div>
          <div class="report-content">
            <h6>KPIs del Inventario</h6>
            <p class="text-muted">Indicadores clave de rendimiento del inventario</p>
            <div class="report-actions">
              <button class="btn btn-outline-warning btn-sm" 
                      @click.stop="requestReport('inventory-kpis')"
                      :disabled="loading">
                <i class="fas fa-tachometer-alt"></i>
                Ver Reporte
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Reportes Avanzados -->
    <div class="row">
      <div class="col-md-6 col-lg-3 mb-4">
        <div class="report-card" @click="requestReport('slow-moving-items')">
          <div class="report-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="report-content">
            <h6>Productos Lentos</h6>
            <p class="text-muted">Productos con baja rotación y movimiento</p>
            <div class="report-actions">
              <button class="btn btn-outline-secondary btn-sm" 
                      @click.stop="requestReport('slow-moving-items')"
                      :disabled="loading">
                <i class="fas fa-clock"></i>
                Ver Reporte
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6 col-lg-3 mb-4">
        <div class="report-card" @click="requestReport('fast-moving-items')">
          <div class="report-icon">
            <i class="fas fa-rocket"></i>
          </div>
          <div class="report-content">
            <h6>Productos Rápidos</h6>
            <p class="text-muted">Productos con alta rotación y movimiento</p>
            <div class="report-actions">
              <button class="btn btn-outline-primary btn-sm" 
                      @click.stop="requestReport('fast-moving-items')"
                      :disabled="loading">
                <i class="fas fa-rocket"></i>
                Ver Reporte
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6 col-lg-3 mb-4">
        <div class="report-card" @click="requestReport('obsolete-items')">
          <div class="report-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="report-content">
            <h6>Productos Obsoletos</h6>
            <p class="text-muted">Productos sin movimiento en períodos largos</p>
            <div class="report-actions">
              <button class="btn btn-outline-danger btn-sm" 
                      @click.stop="requestReport('obsolete-items')"
                      :disabled="loading">
                <i class="fas fa-exclamation-triangle"></i>
                Ver Reporte
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6 col-lg-3 mb-4">
        <div class="report-card" @click="requestReport('inventory-valuation')">
          <div class="report-icon">
            <i class="fas fa-calculator"></i>
          </div>
          <div class="report-content">
            <h6>Valuación de Inventario</h6>
            <p class="text-muted">Valoración completa del inventario actual</p>
            <div class="report-actions">
              <button class="btn btn-outline-success btn-sm" 
                      @click.stop="requestReport('inventory-valuation')"
                      :disabled="loading">
                <i class="fas fa-calculator"></i>
                Ver Reporte
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Botón para descargar todos los reportes (hidden) -->
    <div class="row" v-if="false">
      <div class="col-12 text-center">
        <div class="download-all-section">
          <button class="btn btn-primary btn-lg" 
                  @click="downloadAllReports"
                  :disabled="loading">
            <i class="fas fa-download"></i>
            Descargar Todos los Reportes
          </button>
          <p class="text-muted mt-2">
            Descarga un archivo ZIP con todos los reportes disponibles
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdditionalReportsGrid',
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    requestReport(reportType) {
      this.$emit('report-requested', reportType)
    },
    
    downloadAllReports() {
      this.$emit('report-requested', 'all-reports')
    }
  }
}
</script>

<style scoped>
.additional-reports-grid {
  padding: 20px 0;
}

.report-card {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 12px;
  padding: 25px;
  height: 100%;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 15px;
}

.report-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  border-color: #007bff;
}

.report-icon {
  font-size: 3rem;
  color: #6c757d;
  margin-bottom: 10px;
}

.report-content {
  flex: 1;
}

.report-content h6 {
  color: #495057;
  font-weight: 600;
  margin-bottom: 10px;
  font-size: 1.1rem;
}

.report-content p {
  font-size: 0.9rem;
  margin-bottom: 15px;
  line-height: 1.4;
  color: #6c757d;
}

.report-actions {
  margin-top: auto;
}

.btn-sm {
  border-radius: 6px;
  font-size: 0.8rem;
  padding: 0.4rem 0.8rem;
  font-weight: 500;
}

.download-all-section {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  padding: 30px;
  border: 2px dashed #dee2e6;
  margin-top: 20px;
}

.btn-lg {
  border-radius: 8px;
  font-weight: 600;
  padding: 12px 30px;
}

/* Responsive */
@media (max-width: 768px) {
  .report-card {
    padding: 20px;
    gap: 12px;
  }
  
  .report-icon {
    font-size: 2.5rem;
  }
  
  .report-content h6 {
    font-size: 1rem;
  }
  
  .report-content p {
    font-size: 0.8rem;
  }
  
  .download-all-section {
    padding: 20px;
  }
  
  .btn-lg {
    padding: 10px 20px;
    font-size: 1rem;
  }
}

@media (max-width: 576px) {
  .report-card {
    padding: 15px;
  }
  
  .report-icon {
    font-size: 2rem;
  }
  
  .download-all-section {
    padding: 15px;
  }
  
  .btn-lg {
    padding: 8px 16px;
    font-size: 0.9rem;
  }
}
</style>
