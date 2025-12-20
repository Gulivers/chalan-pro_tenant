# 📊 Enhanced Inventory Dashboard - ChalanPro

## 🎯 Description

Comprehensive inventory dashboard that combines stock, sales, and purchase information to facilitate decision-making for product acquisition. Includes interactive charts with Chart.js, Excel export functionality, and complete permission system.

## 🏗️ Estructura del Proyecto

### Backend (Django)
```
appinventory/
├── views.py                    # Nuevas vistas API para dashboard
├── urls.py                     # URLs actualizadas
└── models.py                   # Modelos existentes (sin cambios)
```

### Frontend (Vue.js)
```
vuefrontend/src/
├── components/inventory/dashboard/
│   ├── InventoryDashboard.vue           # Componente principal
│   └── components/
│       ├── InventoryMetricsCards.vue    # Métricas principales
│       ├── StockAnalysisSection.vue     # Análisis de stock
│       ├── LowStockTable.vue            # Tabla de stock bajo
│       ├── LowestStockChart.vue         # Gráfico de menor stock
│       ├── StockExportButtons.vue       # Botones de exportación
│       ├── SalesAnalysisSection.vue     # Análisis de ventas
│       ├── TopSellingChart.vue          # Gráfico de ventas
│       ├── SalesMetricsCards.vue        # Métricas de ventas
│       ├── SalesExportButtons.vue       # Exportación de ventas
│       ├── CustomersSuppliersSection.vue # Clientes y proveedores
│       ├── TopCustomersChart.vue        # Gráfico de clientes
│       ├── TopSuppliersChart.vue        # Gráfico de proveedores
│       ├── CustomersSuppliersComparison.vue # Comparación
│       ├── CustomersSuppliersExportButtons.vue # Exportación
│       ├── ReportsSection.vue           # Sección de reportes
│       ├── ProductMovementsReport.vue   # Reporte de movimientos
│       └── AdditionalReportsGrid.vue    # Reportes adicionales
└── views/inventory/
    └── InventoryDashboardView.vue      # Vista principal
```

## 🚀 Funcionalidades Implementadas

### 1. **Métricas Principales**
- Total de productos activos
- Total de almacenes
- Stock total en unidades
- Valor total del inventario
- Productos con stock bajo
- Productos vendidos (30 días)
- Proveedores activos
- Clientes activos

### 2. **Análisis de Stock**
- ⚠️ Productos bajo reorder level
- 📉 Top 25 productos con menor stock (gráfico Chart.js)
- 📥 Exportación a Excel por almacén
- 📥 Exportación completa del stock

### 3. **Análisis de Ventas**
- 📈 Top 25 productos más vendidos (gráfico Chart.js)
- 📊 Métricas de ventas por período
- 📥 Exportación de reportes de ventas
- 🔄 Filtros por período (30/60/90/365 días)

### 4. **Clientes y Proveedores**
- 👥 Top 10 clientes por volumen (gráfico Chart.js)
- 🏭 Top 10 proveedores por volumen (gráfico Chart.js)
- 📊 Comparación mensual clientes vs proveedores
- 📥 Exportación de reportes de clientes/proveedores

### 5. **Reportes Avanzados**
- 📋 Reporte de movimientos de productos con filtros
- 📊 Reportes adicionales (ABC, rotación, KPIs)
- 📥 Exportación a Excel y PDF
- 🔍 Filtros por fecha, tipo de documento y almacén

## 🔐 Sistema de Permisos

Cada componente incluye verificaciones de permisos usando `hasPermission()`:

```vue
<!-- Ejemplo de uso de permisos -->
<InventoryMetricsCards 
  v-if="hasPermission('inventory.view_product')"
  :metrics="metrics"
  :loading="loading"
/>
```

### Permisos Requeridos:
- `inventory.view_product` - Ver productos y métricas de inventario
- `apptransactions.view_document` - Ver transacciones y análisis de ventas
- `ctrctsapp.view_builder` - Ver información de clientes/proveedores
- `inventory.change_product` - Editar productos

## 📡 APIs del Backend

### Nuevas Endpoints:
```
GET /api/inventory/dashboard/metrics/                    # Métricas generales
GET /api/inventory/dashboard/top-selling-products/       # Top productos vendidos
GET /api/inventory/dashboard/top-customers/              # Top clientes
GET /api/inventory/dashboard/top-suppliers/              # Top proveedores
GET /api/inventory/dashboard/customers-suppliers-comparison/ # Comparación
GET /api/inventory/dashboard/product-movements/         # Movimientos de productos
```

### Parámetros de Query:
- `period_days` - Período en días para análisis
- `start_date` - Fecha de inicio para filtros
- `end_date` - Fecha de fin para filtros
- `document_type` - Tipo de documento
- `warehouse_id` - ID del almacén

## 🎨 Características de Diseño

### Responsive Design
- Adaptable a móviles, tablets y desktop
- Grid system de Bootstrap
- Componentes flexibles

### Interactividad
- Gráficos Chart.js con tooltips
- Click en gráficos para ver detalles
- Filtros dinámicos en tiempo real
- Botones de exportación prominentes

### Colores y Estilos
- Esquema de colores consistente
- Alertas visuales para stock bajo
- Iconos FontAwesome para mejor UX
- Animaciones suaves en hover

## 📊 Gráficos Chart.js

### Tipos de Gráficos Implementados:
1. **Barras Horizontales** - Top productos/clientes/proveedores
2. **Líneas** - Comparación temporal
3. **Interactivos** - Click para ver detalles

### Características:
- Responsive automático
- Tooltips informativos
- Colores diferenciados por estado
- Exportación como imagen

## 📥 Exportación a Excel

### Funcionalidades:
- Exportación de stock por almacén
- Reportes de ventas por período
- Listas de clientes y proveedores
- Análisis comparativos
- Reportes de movimientos

### Librerías Utilizadas:
- Backend: `openpyxl` para generar archivos Excel
- Frontend: `xlsx` para manejo de archivos

## 🔧 Instalación y Configuración

### Dependencias Frontend:
```bash
npm install chart.js
npm install xlsx
```

### Dependencias Backend:
```python
# requirements.txt
openpyxl>=3.0.0
```

### Configuración de URLs:
```python
# project/urls.py
path('inventory/', include('appinventory.urls')),
```

## 🚀 Uso

### Acceso al Dashboard:
```
http://localhost:8000/inventory/dashboard/
```

### Navegación:
- Scroll vertical para ver todas las secciones
- Filtros dinámicos en cada sección
- Botones de exportación en cada reporte
- Permisos automáticos según rol de usuario

## 📈 Métricas de Rendimiento

### Optimizaciones Implementadas:
- Consultas SQL optimizadas con `select_related`
- Paginación en reportes grandes
- Caché de datos frecuentes
- Lazy loading de componentes

### Tiempos Objetivo:
- Dashboard completo: < 3 segundos
- Gráficos Chart.js: < 1 segundo
- Exportación Excel: < 5 segundos

## 🔄 Próximas Mejoras

### Fase 2 (Futuro):
- [ ] Notificaciones push para stock bajo
- [ ] Dashboard en tiempo real con WebSockets
- [ ] Análisis predictivo de demanda
- [ ] Integración con sistemas externos
- [ ] Mobile app nativa

## 📝 Notas de Desarrollo

### Componentes Reutilizables:
Todos los componentes están diseñados para ser reutilizables en otras partes del sistema.

### Mantenibilidad:
- Código modular y bien documentado
- Separación clara de responsabilidades
- Uso de props y eventos para comunicación
- Sistema de permisos centralizado

### Escalabilidad:
- Fácil agregar nuevas métricas
- Sistema de filtros extensible
- APIs RESTful bien estructuradas
- Componentes independientes

---

**Desarrollado para ChalanPro - Sistema de Gestión de Inventario**
