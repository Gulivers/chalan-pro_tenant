# Filtrado de v-select por is_active

## 🎯 **Objetivo**
Filtrar todos los v-select en formularios para mostrar solo registros activos (`is_active=true`) de los maestros de datos.

## ✅ **Cambios Implementados**

### **Frontend - Consultas API**

#### **1. DocumentTypeSelector.vue**
```javascript
// ANTES
const { data } = await axios.get('/api/document-types/')

// DESPUÉS
const { data } = await axios.get('/api/document-types/?is_active=true')
```

#### **2. TransactionForm.vue**
```javascript
// ANTES
axios.get('/api/document-types/')
axios.get('/api/builder/')
axios.get('/api/unitsofmeasure/')
axios.get('/api/warehouses/')
axios.get('/api/pricetypes/')
axios.get('/api/productbrand/')

// DESPUÉS
axios.get('/api/document-types/?is_active=true')
axios.get('/api/builder/?is_active=true')
axios.get('/api/unitsofmeasure/?is_active=true')
axios.get('/api/warehouses/?is_active=true')
axios.get('/api/pricetypes/?is_active=true')
axios.get('/api/productbrand/?is_active=true')
```

#### **3. PartyForm.vue**
```javascript
// ANTES
axios.get('/api/party-types/?ordering=name')
axios.get('/api/party-categories/?ordering=name')
axios.get('/api/pricetypes/?ordering=name')

// DESPUÉS
axios.get('/api/party-types/?is_active=true&ordering=name')
axios.get('/api/party-categories/?is_active=true&ordering=name')
axios.get('/api/pricetypes/?is_active=true&ordering=name')
```

### **Backend - ViewSets con Filtros**

#### **apptransactions/views.py**
```python
# DocumentTypeViewSet
filter_backends = [DjangoFilterBackend]
filterset_fields = ['is_active']

# PartyTypeViewSet
filter_backends = [DjangoFilterBackend]
filterset_fields = ['is_active']

# PartyCategoryViewSet
filter_backends = [DjangoFilterBackend]
filterset_fields = ['is_active']
```

#### **appinventory/views.py**
```python
# WarehouseViewSet
filter_backends = [DjangoFilterBackend]
filterset_fields = ['is_active']

# ProductCategoryViewSet
filter_backends = [DjangoFilterBackend]
filterset_fields = ['is_active']

# UnitCategoryViewSet
filter_backends = [DjangoFilterBackend]
filterset_fields = ['is_active']

# ProductBrandViewSet
filter_backends = [DjangoFilterBackend]
filterset_fields = ['is_active']

# PriceTypeViewSet
filter_backends = [DjangoFilterBackend]
filterset_fields = ['is_active']

# UnitOfMeasureViewSet
filter_backends = [DjangoFilterBackend]
filterset_fields = ['is_active']
```

#### **ctrctsapp/views.py**
```python
# BuilderViewSet
filter_backends = [DjangoFilterBackend]
filterset_fields = ['is_active']
```

## 📋 **Maestros Filtrados**

### **✅ Completamente Implementados:**
- **Document Types** - Solo tipos de documento activos
- **Party Types** - Solo tipos de parte activos
- **Party Categories** - Solo categorías de parte activas
- **Builders** - Solo builders activos
- **Warehouses** - Solo almacenes activos
- **Product Categories** - Solo categorías de producto activas
- **Product Brands** - Solo marcas activas
- **Price Types** - Solo tipos de precio activos
- **Units of Measure** - Solo unidades de medida activas

### **🔧 Ya Configurados:**
- **Work Accounts** - Ya tenía filtro `active_only=true`
- **Products** - Ya tenía filtro `is_active=true`

## 🎯 **Beneficios**

### **1. Experiencia de Usuario Mejorada:**
- ✅ Solo opciones válidas en los selectores
- ✅ Menos confusión con registros inactivos
- ✅ Formularios más limpios y organizados

### **2. Consistencia de Datos:**
- ✅ Previene selección de registros inactivos
- ✅ Mantiene integridad referencial
- ✅ Reduce errores de validación

### **3. Rendimiento:**
- ✅ Consultas más rápidas (menos datos)
- ✅ Menos carga en el frontend
- ✅ Mejor experiencia de navegación

## 🔍 **Verificación**

### **URLs de Prueba:**
```bash
# Document Types activos
GET /api/document-types/?is_active=true

# Builders activos
GET /api/builder/?is_active=true

# Warehouses activos
GET /api/warehouses/?is_active=true

# Price Types activos
GET /api/pricetypes/?is_active=true
```

### **Frontend:**
- ✅ TransactionForm carga solo opciones activas
- ✅ DocumentTypeSelector muestra solo tipos activos
- ✅ PartyForm filtra tipos y categorías activas
- ✅ Todos los v-select funcionan correctamente

## 📝 **Notas Importantes**

### **1. Compatibilidad:**
- Los filtros son opcionales (no rompen funcionalidad existente)
- Se puede usar `?is_active=false` para ver inactivos si es necesario

### **2. Mantenimiento:**
- Al desactivar un registro, automáticamente desaparece de los selectores
- Al reactivar un registro, automáticamente aparece en los selectores

### **3. Casos Especiales:**
- Los formularios de edición pueden necesitar mostrar registros inactivos si ya están seleccionados
- Los administradores pueden necesitar acceso a todos los registros

## 🚀 **Estado del Proyecto**
- [x] Frontend actualizado
- [x] Backend configurado
- [x] Filtros implementados
- [x] Documentación creada
- [x] Verificación completada

**¡Todos los v-select ahora filtran por registros activos!**
