<template>
  <div class="card">
    <div class="card-header">
      <!-- Desktop Layout -->
      <div class="d-none d-md-flex align-items-center justify-content-between">
        <div class="d-flex gap-2">
            <button class="btn btn-outline-primary" type="button" @click="addLine">
              <i class="bi bi-plus-lg me-1"></i>
              Add Row
            </button>
            <button class="btn btn-outline-info" type="button" :disabled="!hasSelection" @click="duplicateSelected">
              <i class="bi bi-files me-1"></i>
              Duplicate selected
            </button>
            <button class="btn btn-outline-danger" type="button" :disabled="!hasSelection" @click="removeSelected">
              <i class="bi bi-trash me-1"></i>
              Delete selected
            </button>
        </div>
        <div class="small text-muted">Rows: {{ linesLocal?.length || 0 }}</div>
      </div>
      
      <!-- Mobile Layout -->
      <div class="d-md-none">
        <!-- Title Row -->
        <div class="d-flex justify-content-between align-items-center mb-2">
          <div class="small text-muted">Rows: {{ linesLocal?.length || 0 }}</div>
        </div>
        
        <!-- Button Row - Responsive -->
        <div class="d-flex gap-1 flex-wrap">
          <button class="btn btn-outline-primary btn-sm flex-fill" type="button" @click="addLine">
            <i class="bi bi-plus-lg"></i>
            <span class="d-none d-sm-inline ms-1">Add Row</span>
            <span class="d-sm-none ms-1">Add</span>
          </button>
          <button class="btn btn-outline-info btn-sm flex-fill" type="button" :disabled="!hasSelection" @click="duplicateSelected">
            <i class="bi bi-files"></i>
            <span class="d-none d-sm-inline ms-1">Duplicate</span>
            <span class="d-sm-none ms-1">Copy</span>
          </button>
          <button class="btn btn-outline-danger btn-sm flex-fill" type="button" :disabled="!hasSelection" @click="removeSelected">
            <i class="bi bi-trash"></i>
            <span class="d-none d-sm-inline ms-1">Delete</span>
            <span class="d-sm-none ms-1">Del</span>
          </button>
        </div>
      </div>
    </div>

    <div class="table-responsive" style="max-height: 70vh; min-height: 400px">
      <table class="table table-sm align-middle table-hover table-sticky">
        <thead>
          <tr>
            <th style="width: 30px" class="text-center">
              <input type="checkbox" class="form-check-input" v-model="selectAll" />
            </th>
            <th style="min-width: 300px">Product</th>
            <th style="min-width: 100px" v-tt="'Quantity'">Qty</th>
            <th style="min-width: 200px">Unit</th>
            <th style="min-width: 120px">Unit Price</th>
            <th style="min-width: 100px">Disc %</th>
            <th style="min-width: 180px">Warehouse</th>
            <th style="min-width: 150px">Price Type</th>
            <th style="min-width: 150px">Brand</th>
            <th style="min-width: 120px" class="text-end">Final</th>
            <th style="width: 80px"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, idx) in linesLocal"
            :key="row.__key"
            :class="{ 'table-warning': Object.keys(row._errors || {}).length > 0 }">
            <td class="text-center">
              <input type="checkbox" class="form-check-input" v-model="row.selected" />
            </td>

            <!-- Product (remote search) -->
            <td>
              <v-select
                :id="`product-${idx}`"
                :options="productOptions"
                label="label"
                :reduce="o => o.value"
                :filterable="true"
                :loading="loading.products[idx]"
                v-model="row.product"
                @search="q => searchProducts(idx, q)"
                @option:selected="opt => onProductSelected(idx, opt)"
                @clear="onProductCleared(idx)"
                @update:modelValue="val => onProductChanged(idx, val)"
                @keydown.enter="focusNextField(idx, 'quantity')"
                placeholder="Search product..."
                :class="{ 'is-invalid': row._errors?.product }">
                <template #selected-option="{ label, product }">
                  <div class="text-truncate" style="max-width: 280px">
                    {{ row.product_label || product?.name || label || 'No name' }}
                  </div>
                </template>
                <template #option="{ label, product }">
                  <div class="text-truncate" style="max-width: 280px">
                    {{ product?.name || label || 'No name' }}
                  </div>
                </template>
                <template #no-options>
                  <div class="text-muted small">Type at least 2 characters to search...</div>
                </template>
              </v-select>
              <div class="text-danger small" v-if="row._errors?.product">{{ row._errors.product[0] }}</div>
            </td>

            <!-- Qty -->
            <td>
              <input
                :id="`quantity-${idx}`"
                ref="quantityInputs"
                type="number"
                min="0"
                step="0.01"
                class="form-control form-control-sm"
                :class="{ 'is-invalid': row._errors?.quantity }"
                v-model.number="row.quantity"
                @input="recalcRow(idx)"
                @keydown.enter="focusNextField(idx, 'unit')"
                @focus="$event.target.select()"
                placeholder="0.00" />
              <div class="text-danger small" v-if="row._errors?.quantity">{{ row._errors.quantity[0] }}</div>
            </td>

            <!-- Unit -->
            <td>
               <v-select
                 :id="`unit-${idx}`"
                 :options="unitsOptions"
                 :reduce="o => o.value"
                 label="label"
                 v-model="row.unit"
                 @update:modelValue="recalcRow(idx)"
                 @keydown.enter="focusNextField(idx, 'unit_price')"
                 :class="{ 'is-invalid': row._errors?.unit }"
                 placeholder="Select unit...">
                 <template #selected-option="{ label }">
                   <div class="text-truncate" style="max-width: 180px">{{ label }}</div>
                 </template>
                 <template #option="{ label }">
                   <div class="text-truncate" style="max-width: 180px">{{ label }}</div>
                 </template>
               </v-select>
              <div class="text-danger small" v-if="row._errors?.unit">{{ row._errors.unit[0] }}</div>
            </td>

            <!-- Unit Price -->
            <td>
              <input
                :id="`unit_price-${idx}`"
                ref="unitPriceInputs"
                type="number"
                min="0"
                step="0.01"
                class="form-control form-control-sm"
                :class="{ 'is-invalid': row._errors?.unit_price }"
                v-model.number="row.unit_price"
                @input="recalcRow(idx)"
                @keydown.enter="focusNextField(idx, 'discount_percentage')"
                @focus="$event.target.select()"
                placeholder="0.00" />
              <div class="text-danger small" v-if="row._errors?.unit_price">{{ row._errors.unit_price[0] }}</div>
            </td>

            <!-- Discount % -->
            <td>
              <input
                :id="`discount_percentage-${idx}`"
                ref="discountInputs"
                type="number"
                min="0"
                max="100"
                step="0.01"
                class="form-control form-control-sm"
                :class="{ 'is-invalid': row._errors?.discount_percentage }"
                v-model.number="row.discount_percentage"
                @input="recalcRow(idx)"
                @keydown.enter="focusNextField(idx, 'warehouse')"
                @focus="$event.target.select()"
                placeholder="0.00" />
              <div class="text-danger small" v-if="row._errors?.discount_percentage">
                {{ row._errors.discount_percentage[0] }}
              </div>
            </td>

            <!-- Warehouse (required per line when doc type requires it) -->
            <td>
               <v-select
                 :id="`warehouse-${idx}`"
                 :options="warehousesOptions"
                 :reduce="o => o.value"
                 label="label"
                 v-model="row.warehouse"
                 @keydown.enter="focusNextField(idx, 'price_type')"
                 :class="{ 'is-invalid': row._errors?.warehouse }"
                 placeholder="Select warehouse...">
                 <template #selected-option="{ label }">
                   <div class="text-truncate" style="max-width: 160px">{{ label }}</div>
                 </template>
                 <template #option="{ label }">
                   <div class="text-truncate" style="max-width: 160px">{{ label }}</div>
                 </template>
               </v-select>
              <div class="text-danger small" v-if="row._errors?.warehouse">{{ row._errors.warehouse[0] }}</div>
            </td>

            <!-- Price Type -->
            <td>
               <v-select
                 :id="`price_type-${idx}`"
                 :options="priceTypesOptions"
                 :reduce="o => o.value"
                 label="label"
                 v-model="row.price_type"
                 @keydown.enter="focusNextField(idx, 'brand')"
                 placeholder="Price type...">
                 <template #selected-option="{ label }">
                   <div class="text-truncate" style="max-width: 130px">{{ label }}</div>
                 </template>
                 <template #option="{ label }">
                   <div class="text-truncate" style="max-width: 130px">{{ label }}</div>
                 </template>
               </v-select>
            </td>

            <!-- Brand -->
            <td>
               <v-select
                 :id="`brand-${idx}`"
                 :options="(row.brands && row.brands.length > 0) ? row.brands : brandsOptions"
                 :reduce="o => o.value"
                 label="label"
                 v-model="row.brand"
                 @keydown.enter="focusNextRow(idx)"
                 :placeholder="(row.brands && row.brands.length > 0) ? 'Brand...' : 'Load brands from product...'"
                 :disabled="!row.product">
                 <template #selected-option="{ label }">
                   <div class="text-truncate" style="max-width: 130px">{{ label }}</div>
                 </template>
                 <template #option="{ label }">
                   <div class="text-truncate" style="max-width: 130px">{{ label }}</div>
                 </template>
                 <template #no-options>
                   <div class="text-muted small">
                     {{ row.product ? 'No brands available' : 'Select a product first' }}
                   </div>
                 </template>
               </v-select>
            </td>

            <!-- Final -->
            <td class="text-end">
              {{ currency(row.final_price) }}
            </td>

            <td class="text-end">
              <div class="d-flex gap-1 justify-content-end">
                <button
                  class="btn btn-sm btn-outline-info"
                  type="button"
                  @click="duplicateRow(idx)"
                  title="Duplicate line">
                  <i class="bi bi-copy"></i>
                  <img src="@/assets/img/duplicate-alt.svg" alt="Duplicar" style="width: 18px; height: 18px; margin-left: 2px;" />
                </button>
                <button class="btn btn-sm btn-outline-danger" type="button" @click="removeRow(idx)" title="Remove line">
                  <i class="bi bi-x-lg"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
  import { ref, watch, computed, nextTick, onMounted } from 'vue';
  import axios from 'axios';
  import VSelect from 'vue-select';
  import 'vue-select/dist/vue-select.css';

  const props = defineProps({
    modelValue: { type: Array, default: () => [] }, // not used (legacy)
    lines: { type: Array, default: () => [] }, // v-model:lines
    documentTypeId: { type: [Number, null], default: null },
    workAccountId: { type: [Number, null], default: null },
    unitsOptions: { type: Array, default: () => [] },
    warehousesOptions: { type: Array, default: () => [] },
    priceTypesOptions: { type: Array, default: () => [] },
    brandsOptions: { type: Array, default: () => [] },
    mergeDuplicates: { type: Boolean, default: true },
  });
  const emit = defineEmits(['update:lines', 'recalc']);

  const linesLocal = ref([]);
  const selectAll = ref(false);
  const productOptions = ref([]);
  const loading = ref({ products: {} });
  const isUpdatingFromProps = ref(false);
  const defaultWarehouse = ref(null);

  watch(
    () => props.lines,
    async val => {
      console.log('LinesGrid: lines prop changed:', val);
      isUpdatingFromProps.value = true;

      const newLines = (val || []).map(x => ({ 
        ...x, 
        __key: x.id || cryptoRandom(),
        brands: x.brands || [], // Asegurar que brands siempre esté definido
      }));
      console.log('🔍 New lines with product_label:', newLines.map(l => ({ 
        product: l.product, 
        product_label: l.product_label 
      })));

      // Only update if there are actual changes to avoid infinite loops
      // Compare lengths and IDs to avoid deep comparison issues
      const currentLength = linesLocal.value.length;
      const newLength = newLines.length;
      const currentIds = linesLocal.value.map(l => l.id).sort();
      const newIds = newLines.map(l => l.id).sort();

      if (currentLength !== newLength || JSON.stringify(currentIds) !== JSON.stringify(newIds)) {
        linesLocal.value = newLines;

        // If no lines exist, add one empty line for user to start with
        if (linesLocal.value.length === 0) {
          addLine();
        }
      }

      nextTick(() => {
        isUpdatingFromProps.value = false;
      });
    },
    { immediate: true, deep: true }
  );

  watch(
    linesLocal,
    val => {
      console.log('LinesGrid: linesLocal changed:', val.length, 'lines');

      // Don't emit if we're updating from props to avoid infinite loops
      if (!isUpdatingFromProps.value) {
        nextTick(() => {
          emit('update:lines', val);
          emit('recalc');
        });
      }
    },
    { deep: true }
  );

  watch(selectAll, checked => {
    linesLocal.value.forEach(r => (r.selected = checked));
  });

  // Watcher para asignar warehouse por defecto cuando esté disponible
  watch(defaultWarehouse, (newWarehouse) => {
    if (newWarehouse && linesLocal.value.length > 0) {
      linesLocal.value.forEach(line => {
        if (!line.warehouse) {
          line.warehouse = newWarehouse;
        }
      });
    }
  });

  // Watch for document type changes to validate warehouse requirements
  watch(
    () => props.documentTypeId,
    async newDocTypeId => {
      console.log('🔍 LinesGrid: documentTypeId changed to:', newDocTypeId, typeof newDocTypeId)
      if (newDocTypeId) {
        try {
          console.log('🔍 LinesGrid: Making request to:', `/api/document-types/${newDocTypeId}/`)
          const { data } = await axios.get(`/api/document-types/${newDocTypeId}/`);
          const requiresWarehouse = data.warehouse_required;

          // Clear warehouse validation errors if warehouse is no longer required
          if (!requiresWarehouse) {
            linesLocal.value.forEach(line => {
              if (line._errors?.warehouse) {
                delete line._errors.warehouse;
              }
            });
          }
        } catch (error) {
          console.warn('Could not fetch document type info:', error);
        }
      }
    }
  );

  function cryptoRandom() {
    return Math.random().toString(36).slice(2) + Date.now().toString(36);
  }

  function currency(n) {
    const num = Number(n || 0);
    return num.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
  }

  function recalcRow(idx) {
    const r = linesLocal.value[idx];
    if (!r) {
      console.warn(`recalcRow: Line at index ${idx} not found`);
      return;
    }
    const qty = Number(r.quantity || 0);
    const price = Number(r.unit_price || 0);
    const disc = Number(r.discount_percentage || 0);
    r.final_price = +(qty * price * (1 - disc / 100)).toFixed(2);
  }

  // Función para cargar el warehouse predeterminado
  async function loadDefaultWarehouse() {
    try {
      const { data } = await axios.get('/api/default-warehouse/');
      if (data.id) {
        defaultWarehouse.value = data.id;
        console.log('🔍 Default warehouse loaded:', data.name);
      }
    } catch (error) {
      console.warn('Could not fetch default warehouse:', error);
    }
  }

  function addLine() {
    const newLine = {
      __key: cryptoRandom(),
      selected: false,
      id: null,
      product: null,
      product_label: '',
      quantity: 1,
      unit: null,
      unit_price: 0,
      discount_percentage: 0,
      final_price: 0,
      warehouse: defaultWarehouse.value, // Auto-fill con warehouse predeterminado
      price_type: null,
      brands: [], // Cambiar a array para múltiples marcas
      brand: null, // Mantener para compatibilidad y marca seleccionada
      _errors: {},
    };

    console.log('Adding new line with default warehouse:', newLine);
    linesLocal.value.push(newLine);
  }

  function removeRow(idx) {
    linesLocal.value.splice(idx, 1);
  }

  function duplicateRow(idx) {
    const originalLine = linesLocal.value[idx];
    const duplicatedLine = {
      ...originalLine,
      __key: cryptoRandom(),
      selected: false,
      id: null, // Reset ID for new line
      quantity: 1, // Reset quantity to 1
      final_price: 0, // Reset final price
      _errors: {},
    };
    linesLocal.value.splice(idx + 1, 0, duplicatedLine);
  }

  const hasSelection = computed(() => linesLocal.value.some(r => r.selected));
  function removeSelected() {
    linesLocal.value = linesLocal.value.filter(r => !r.selected);
    selectAll.value = false;
  }

  function duplicateSelected() {
    const selectedLines = linesLocal.value.filter(r => r.selected);
    selectedLines.forEach(line => {
      const duplicatedLine = {
        ...line,
        __key: cryptoRandom(),
        selected: false,
        id: null, // Reset ID for new line
        quantity: 1, // Reset quantity to 1
        final_price: 0, // Reset final price
        _errors: {},
      };
      linesLocal.value.push(duplicatedLine);
    });
    selectAll.value = false;
  }

  async function searchProducts(idx, query) {
    if (!query || query.length < 2) {
      productOptions.value = [];
      return;
    }

    loading.value.products[idx] = true;
    try {
      const { data } = await axios.get('/api/products/', {
        params: {
          search: query,
          page_size: 20,
          is_active: true,
        },
      });
      const list = Array.isArray(data) ? data : data?.results || [];
      console.log('🔍 Products API response:', data);
      console.log('🔍 Products list:', list);
      
      productOptions.value = list.map(p => {
        const option = {
          value: p.id,
          label: `${p.name} (${p.sku})`,
          product: p,
        };
        console.log('🔍 Mapped product option:', option);
        return option;
      });
      
      console.log('🔍 Mapped productOptions:', productOptions.value);
    } catch (error) {
      console.error('Error searching products:', error);
      productOptions.value = [];
    } finally {
      loading.value.products[idx] = false;
    }
  }

  // Función para obtener las marcas de un producto
  async function fetchProductBrands(productId) {
    try {
      const { data } = await axios.get(`/api/products/${productId}/brands/`);
      return data.brands || [];
    } catch (error) {
      console.warn('Could not fetch product brands:', error);
      return [];
    }
  }

  // Función para actualizar marcas cuando cambia el producto
  async function updateBrandsForProduct(idx, productId) {
    if (!productId) return;
    
    try {
      const brands = await fetchProductBrands(productId);
      const r = linesLocal.value[idx];
      
      if (brands.length > 0) {
        // Formatear las marcas para v-select
        r.brands = brands.map(b => ({ value: b.id, label: b.name }));
        
        // Si no hay marca seleccionada, usar la default
        if (!r.brand) {
          const defaultBrand = brands.find(b => b.is_default) || brands[0];
          r.brand = defaultBrand.id;
        }
        
        console.log('🔍 Updated brands for product:', {
          productId,
          brands: r.brands,
          selectedBrand: r.brand
        });
      }
    } catch (error) {
      console.warn('Error updating brands for product:', error);
    }
  }

  // Función para manejar cuando cambia el producto por v-model
  async function onProductChanged(idx) {
    const r = linesLocal.value[idx];
    if (r.product) {
      await updateBrandsForProduct(idx, r.product);
    } else {
      r.brands = [];
      r.brand = null;
    }
  }

  async function onProductSelected(idx, option) {
    console.log('🔍 onProductSelected called with:', option);
    const r = linesLocal.value[idx];
    r.product_label = option?.product?.name || option?.label || '';
    console.log('🔍 Set product_label to:', r.product_label);

    // Auto-fill fields from ProductPrice predeterminado
    if (option?.value) {
      try {
        // Construir params con document_type_id si está disponible
        const params = {};
        if (props.documentTypeId) {
          params.document_type_id = props.documentTypeId;
          console.log('🔍 Fetching price with document_type_id:', props.documentTypeId);
        }
        
        const { data } = await axios.get(`/api/products/${option.value}/default-price/`, { params });
        
        console.log('🔍 Received price data:', data);
        
        // Auto-fill Unit desde ProductPrice predeterminado
        if (data.unit) {
          r.unit = data.unit;
        }
        
        // Auto-fill Unit Price desde ProductPrice predeterminado
        if (data.unit_price !== undefined) {
          r.unit_price = data.unit_price;
        }
        
        // Auto-fill Price Type desde ProductPrice predeterminado
        if (data.price_type) {
          r.price_type = data.price_type;
        }
        
        // Auto-fill Brand desde Product (usa el default_brand ahora)
        if (data.default_brand?.id) {
          r.brand = data.default_brand.id;
          // Solo establecer brands si no están ya cargadas
          if (!r.brands || r.brands.length === 0) {
            await updateBrandsForProduct(idx, option.value);
          }
        }
        
        console.log('🔍 Auto-filled fields from ProductPrice:', {
          unit: data.unit,
          unit_price: data.unit_price,
          price_type: data.price_type,
          brand: data.default_brand,
          brands: r.brands,
          document_type_used: props.documentTypeId
        });
        
      } catch (error) {
        console.warn('Could not fetch product default price:', error);
        
        // Fallback: Auto-fill default unit from product if available
        if (option?.product?.unit_default) {
          r.unit = option.product.unit_default.id || option.product.unit_default;
        }
        
        // Fallback: obtener marcas disponibles del producto usando la función dedicada
        await updateBrandsForProduct(idx, option.value);
      }
    }

    // Auto-fill default price type from work account if available (fallback)
    if (props.workAccountId && props.workAccountId !== null && !r.price_type) {
      console.log('🔍 DEBUG LinesGrid: workAccountId prop:', props.workAccountId, 'Type:', typeof props.workAccountId);
      try {
        const { data } = await axios.get(`/api/work-accounts/${props.workAccountId}/`);
        if (data.default_price_type) {
          r.price_type = data.default_price_type;
        }
      } catch (error) {
        // Manejar específicamente el caso de work account no encontrado (404)
        if (error.response?.status === 404) {
          console.warn(`Work account ${props.workAccountId} not found, skipping default price type`);
        } else {
          console.warn('Could not fetch work account default price type:', error);
        }
        // No mostrar error al usuario, simplemente continuar sin el precio por defecto
      }
    }

    // Optional: prevent duplicates (product+unit+brand) → merge quantities
    let wasMerged = false;
    if (props.mergeDuplicates) {
      wasMerged = maybeMergeDuplicate(idx);
    }

    // Recalculate row after product selection (solo si no fue mergeada)
    if (!wasMerged) {
      recalcRow(idx);
    }
  }

  function onProductCleared(idx) {
    const r = linesLocal.value[idx];
    r.product_label = '';
    r.product = null;
    r.unit = null;
    r.price_type = null;
    r.brand = null;
    r.brands = []; // Limpiar marcas también
    recalcRow(idx);
  }

  function maybeMergeDuplicate(idx) {
    const r = linesLocal.value[idx];
    if (!r.product) return false;

    for (let i = 0; i < linesLocal.value.length; i++) {
      if (i === idx) continue;
      const o = linesLocal.value[i];
      if (o.product === r.product && (o.unit || null) === (r.unit || null) && (o.brand || null) === (r.brand || null)) {
        // merge into older row
        o.quantity = Number(o.quantity || 0) + Number(r.quantity || 0);
        recalcRow(i);
        linesLocal.value.splice(idx, 1);
        return true; // La línea fue eliminada/mergeada
      }
    }
    return false; // No se encontró duplicado
  }

  // Validation function for lines
  function validateLines() {
    let isValid = true;

    linesLocal.value.forEach((line, idx) => {
      line._errors = {};

      // Required fields
      if (!line.product) {
        line._errors.product = ['Product is required'];
        isValid = false;
      }

      if (!line.quantity || line.quantity <= 0) {
        line._errors.quantity = ['Quantity must be greater than 0'];
        isValid = false;
      }

      // unit es opcional según la estructura de la tabla (unit_id DEFAULT NULL)
      // if (!line.unit) {
      //   line._errors.unit = ['Unit is required'];
      //   isValid = false;
      // }

      if (line.unit_price === null || line.unit_price === undefined || line.unit_price < 0) {
        line._errors.unit_price = ['Unit price must be 0 or greater'];
        isValid = false;
      }

      // Warehouse validation based on document type
      if (props.documentTypeId) {
        // This validation should be done on the backend based on document type requirements
        // For now, we'll just ensure warehouse is provided if required
      }
    });

    return isValid;
  }

  // Función para navegar entre campos con Enter
  function focusNextField(rowIndex, fieldName) {
    nextTick(() => {
      const fieldMap = {
        'quantity': 'quantity',
        'unit_price': 'unit_price',
        'discount_percentage': 'discount_percentage',
        'unit': 'unit',
        'warehouse': 'warehouse',
        'price_type': 'price_type',
        'brand': 'brand'
      };

      const fieldId = fieldMap[fieldName];
      if (fieldId) {
        const elementId = `${fieldId}-${rowIndex}`;
        const element = document.getElementById(elementId);
        
        if (element) {
          // Para inputs normales, enfocar directamente y seleccionar contenido
          if (element.tagName === 'INPUT') {
            element.focus();
            element.select();
          } else {
            // Para vue-select, enfocar el campo de búsqueda interno
            const searchInput = element.querySelector('.vs__search');
            if (searchInput) {
              searchInput.focus();
              searchInput.select();
            }
          }
        }
      }
    });
  }

  // Función para navegar a la siguiente fila
  function focusNextRow(currentRowIndex) {
    nextTick(() => {
      const nextRowIndex = currentRowIndex + 1;
      
      // Si existe la siguiente fila, enfocar el primer campo (Product)
      if (nextRowIndex < linesLocal.value.length) {
        const productElementId = `product-${nextRowIndex}`;
        const productElement = document.getElementById(productElementId);
        if (productElement) {
          const searchInput = productElement.querySelector('.vs__search');
          if (searchInput) {
            searchInput.focus();
            searchInput.select();
          }
        }
      } else {
        // Si no hay más filas, agregar una nueva
        addLine();
        nextTick(() => {
          const newRowIndex = linesLocal.value.length - 1;
          const productElementId = `product-${newRowIndex}`;
          const productElement = document.getElementById(productElementId);
          if (productElement) {
            const searchInput = productElement.querySelector('.vs__search');
            if (searchInput) {
              searchInput.focus();
              searchInput.select();
            }
          }
        });
      }
    });
  }

  // Cargar warehouse predeterminado al montar el componente
  onMounted(async () => {
    await loadDefaultWarehouse();
    
    // Si hay líneas pero no tienen warehouse, asignar el por defecto
    if (linesLocal.value.length > 0 && defaultWarehouse.value) {
      linesLocal.value.forEach(line => {
        if (!line.warehouse) {
          line.warehouse = defaultWarehouse.value;
        }
      });
    }
  });

  // Expose validation function
  defineExpose({
    validateLines,
  });
</script>

<style scoped>
  .table tbody tr:hover {
    background-color: #fafafa;
  }

  /* Estilos para campos con errores */
  .is-invalid {
    border-color: #dc3545;
  }

  .is-invalid:focus {
    border-color: #dc3545;
    box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
  }

  /* Estilos para vue-select con errores */
  :deep(.is-invalid .vs__dropdown-toggle) {
    border-color: #dc3545;
  }

  :deep(.is-invalid .vs__dropdown-toggle:focus) {
    box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
  }

  /* Mejorar la apariencia de los inputs */
  .form-control-sm {
    font-size: 0.8rem;
    padding: 0.225rem 0.45rem;
  }

  /* Estilos para la tabla */
  .table-sticky thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: #f8f9fa;
    border-bottom: 2px solid #dee2e6;
  }

  /* Mejorar el z-index de los dropdowns */
  :deep(.vs__dropdown-menu) {
    z-index: 1050 !important;
  }

  :deep(.vs__dropdown-toggle) {
    z-index: 1049 !important;
  }

  /* Estilos para los botones de acción */
  .btn-sm {
    padding: 0.225rem 0.45rem;
    font-size: 0.8rem;
  }

   /* Estilos para el contenedor de la tabla */
   .table-responsive {
     border-radius: 0.375rem;
     overflow-x: auto; /* Scroll horizontal en pantallas pequeñas */
     overflow-y: visible; /* Permitir que los dropdowns se vean fuera del contenedor */
   }

   /* Asegurar que la tabla tenga suficiente espacio */
   .table {
     min-width: 1100px; /* Ancho mínimo para mostrar todas las columnas */
   }

   /* Responsive para pantallas pequeñas */
   @media (max-width: 768px) {
     .table-responsive {
       font-size: 0.75rem;
     }
     
     .table th,
     .table td {
       padding: 0.225rem;
       white-space: nowrap;
     }
     
     .btn-sm {
       padding: 0.15rem 0.3rem;
       font-size: 0.7rem;
     }
   }

   /* Responsive para tablets */
   @media (max-width: 1024px) and (min-width: 769px) {
     .table-responsive {
       font-size: 0.8rem;
     }
     
     .table th,
     .table td {
       padding: 0.275rem;
     }
   }

  /* Mejorar la apariencia de los placeholders */
  .form-control::placeholder {
    color: #6c757d;
    opacity: 1;
  }

  /* Estilos para el header de la tabla */
  .card-header {
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
  }

  /* Estilos para los mensajes de error */
  .text-danger.small {
    font-size: 0.7rem;
    margin-top: 0.225rem;
  }

  /* Estilos para filas con errores */
  .table-warning {
    background-color: #fff3cd !important;
  }

  .table-warning:hover {
    background-color: #ffeaa7 !important;
  }

  /* Estilos para los botones de acción en las filas */
  .btn-sm {
    min-width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Mejorar la apariencia de los gaps */
  .d-flex.gap-1 > * + * {
    margin-left: 0.225rem;
  }

  .d-flex.gap-2 > * + * {
    margin-left: 0.45rem;
  }

  /* Estilos adicionales para hacer los controles más compactos */
  .table th,
  .table td {
    padding: 0.35rem 0.45rem;
    font-size: 0.85rem;
  }
  
  /* Mobile responsive adjustments for header buttons */
  @media (max-width: 768px) {
    .card-header {
      padding: 0.75rem;
    }
    
    .btn-sm {
      font-size: 0.75rem;
      padding: 0.25rem 0.4rem;
      min-width: auto;
    }
    
    .btn-sm i {
      font-size: 0.8rem;
    }
    
    /* Ensure buttons don't overflow */
    .d-flex.gap-1 > * + * {
      margin-left: 0.25rem;
    }
    
    .flex-fill {
      flex: 1 1 auto;
      min-width: 0;
    }
  }

  /* Reducir el tamaño de los dropdowns de vue-select */
  :deep(.vs__dropdown-toggle) {
    min-height: 31px;
    height: 31px;
    font-size: 0.8rem;
  }

  :deep(.vs__selected-options) {
    padding: 0.225rem 0.35rem;
    line-height: 1.2;
  }

  :deep(.vs__search) {
    font-size: 0.8rem;
    padding: 0.225rem 0.35rem;
    line-height: 1.2;
  }

  :deep(.vs__dropdown-menu) {
    font-size: 0.8rem;
  }

  :deep(.vs__dropdown-option) {
    padding: 0.225rem 0.45rem;
    line-height: 1.2;
  }

  /* Reducir el tamaño del texto en el header */
  .card-header {
    font-size: 0.9rem;
    padding: 0.6rem 0.8rem;
  }

  /* Reducir el tamaño del contador de filas */
  .small {
    font-size: 0.75rem;
  }

  /* Asegurar que todos los controles vue-select tengan la misma altura que los inputs */
  :deep(.vs__control) {
    min-height: 31px;
    height: 31px;
  }

  :deep(.vs__actions) {
    padding: 0.225rem 0.35rem;
  }

  :deep(.vs__clear) {
    padding: 0.225rem 0.35rem;
  }

  :deep(.vs__open-indicator) {
    padding: 0.225rem 0.35rem;
  }
</style>
