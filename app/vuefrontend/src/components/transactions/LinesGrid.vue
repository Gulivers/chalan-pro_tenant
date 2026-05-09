<template>
  <div class="card">
    <div class="card-header">
      <!-- Desktop Layout -->
      <div class="d-none d-md-flex align-items-center justify-content-between">
        <div class="d-flex gap-2">
            <button
              class="btn btn-outline-primary"
              type="button"
              :disabled="disabled"
              @click="addLine"
              v-tt
              data-title="Add a new line to the document">
              <i class="bi bi-plus-lg me-1"></i>
              Agregar fila
            </button>
            <button
              class="btn btn-outline-info"
              type="button"
              :disabled="!hasSelection"
              @click="duplicateSelected"
              v-tt
              data-title="Duplicate the selected lines">
              <i class="bi bi-files me-1"></i>
              Duplicate selected
            </button>
            <button
              class="btn btn-outline-danger"
              type="button"
              :disabled="!hasSelection"
              @click="removeSelected"
              v-tt
              data-title="Remove the selected lines">
              <i class="bi bi-trash me-1"></i>
              Delete selected
            </button>
            <button
              v-if="documentId && documentTypeCreatesSerializedItems"
              class="btn btn-outline-secondary"
              type="button"
              @click="$emit('open-asset-tags')"
              v-tt
              data-title="Assign serial numbers for serialized items of this document (only for document types that create serialized items, e.g. GRN)">
              <i class="bi bi-tag me-1"></i>
              Assign Serial Numbers
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
          <button
            class="btn btn-outline-primary btn-sm flex-fill"
            type="button"
            :disabled="disabled"
            @click="addLine"
            v-tt
            data-title="Add a new line to the document">
            <i class="bi bi-plus-lg"></i>
            <span class="d-none d-sm-inline ms-1">Agregar fila</span>
            <span class="d-sm-none ms-1">Fila</span>
          </button>
          <button
            class="btn btn-outline-info btn-sm flex-fill"
            type="button"
            :disabled="!hasSelection"
            @click="duplicateSelected"
            v-tt
            data-title="Duplicate the selected lines">
            <i class="bi bi-files"></i>
            <span class="d-none d-sm-inline ms-1">Duplicate</span>
            <span class="d-sm-none ms-1">Copy</span>
          </button>
          <button
            class="btn btn-outline-danger btn-sm flex-fill"
            type="button"
            :disabled="!hasSelection"
            @click="removeSelected"
            v-tt
            data-title="Remove the selected lines">
            <i class="bi bi-trash"></i>
            <span class="d-none d-sm-inline ms-1">Delete</span>
            <span class="d-sm-none ms-1">Del</span>
          </button>
<button
          v-if="documentId && documentTypeCreatesSerializedItems"
          class="btn btn-outline-secondary btn-sm flex-fill"
          type="button"
          @click="$emit('open-asset-tags')"
          v-tt
          data-title="Assign serial numbers for serialized items of this document (only for document types that create serialized items, e.g. GRN)">
            <i class="bi bi-tag"></i>
            <span class="d-none d-sm-inline ms-1">Serial Numbers</span>
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
            <th style="min-width: 300px" v-tt data-title="Product or service for this line">Product</th>
            <th style="min-width: 100px" v-tt data-title="Quantity">Qty</th>
            <th style="min-width: 200px" v-tt data-title="Unit of measure">Unit</th>
            <th style="min-width: 120px" v-tt data-title="Price per unit">Unit Price</th>
            <th style="min-width: 100px" v-tt data-title="Discount percentage applied to this line">Disc %</th>
            <th style="min-width: 180px" v-tt data-title="Warehouse for stock movement (required when document type requires it)">Warehouse</th>
            <th style="min-width: 190px" v-tt data-title="Price type (e.g. Contractor, Retail) and margin/markup rule used for the line">Price Type</th>
            <th
              v-if="documentTypeIsSales"
              style="min-width: 130px"
              v-tt
              data-title="Margin / Markup % used with purchase cost for sale pricing (Markup/Margin price types only).">
              Margin %
            </th>
            <th style="min-width: 150px" v-tt data-title="Product brand when applicable">Brand</th>
            <th
              style="min-width: 120px"
              class="text-end"
              v-tt
              data-title="Net amount for this line after Disc. % (qty × unit price × (1 − disc/100)). Footer Subtotal is the sum of qty × unit price before discounts.">
              Line total
            </th>
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
                append-to-body
                :id="`product-${idx}`"
                :options="productOptions"
                label="label"
                :reduce="o => o.value"
                :filterable="true"
                :loading="loading.products[idx]"
                :disabled="disabled"
                v-model="row.product"
                @search="q => searchProducts(idx, q)"
                @option:selected="opt => onProductSelected(idx, opt)"
                @clear="onProductCleared(idx)"
                @update:modelValue="val => onProductChanged(idx, val)"
                @keydown.enter="focusNextField(idx, 'quantity')"
                placeholder="Search product..."
                :class="{ 'is-invalid': row._errors?.product }">
                <template #selected-option="{ label, product }">
                  <div class="d-flex align-items-center gap-2" style="max-width: 280px">
                    <span class="text-truncate">{{ row.product_label || product?.name || label || 'No name' }}</span>
                    <span
                      v-if="product?.tracking_mode === 'SERIALIZED'"
                      class="badge bg-info flex-shrink-0"
                      style="font-size: 0.65rem"
                    >
                      SERIALIZED
                    </span>
                  </div>
                </template>
                <template #option="{ label, product }">
                  <div class="d-flex align-items-center gap-2" style="max-width: 280px">
                    <span class="text-truncate">{{ product?.name || label || 'No name' }}</span>
                    <span
                      v-if="product?.tracking_mode === 'SERIALIZED'"
                      class="badge bg-info flex-shrink-0"
                      style="font-size: 0.65rem"
                    >
                      SERIALIZED
                    </span>
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
                :disabled="disabled"
                v-model.number="row.quantity"
                @input="onQuantityInput(idx)"
                @blur="onQuantityBlurMerge(idx)"
                @keydown.enter="onQuantityEnterMerge(idx, $event)"
                @focus="$event.target.select()"
                placeholder="0.00" />
              <div class="text-danger small" v-if="row._errors?.quantity">{{ row._errors.quantity[0] }}</div>
            </td>

            <!-- Unit -->
            <td>
               <v-select
                 append-to-body
                 :id="`unit-${idx}`"
                 :options="unitsOptions"
                 :reduce="o => o.value"
                 label="label"
                 :disabled="disabled"
                 v-model="row.unit"
                 @update:modelValue="onUnitUpdated(idx)"
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
                :disabled="disabled"
                v-model.number="row.unit_price"
                @input="onUnitPriceInput(idx)"
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
                :disabled="disabled"
                v-model.number="row.discount_percentage"
                @input="onDiscountPercentageInput(idx)"
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
                 append-to-body
                 :id="`warehouse-${idx}`"
                 :options="warehousesOptions"
                 :reduce="o => o.value"
                 label="label"
                 :disabled="disabled"
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
                 append-to-body
                 :id="`price_type-${idx}`"
                 :options="priceTypesOptions"
                 :reduce="o => o.value"
                 label="label"
                 :disabled="disabled"
                 v-model="row.price_type"
                 @update:modelValue="onPriceTypeUpdated(idx)"
                 @keydown.enter="focusNextField(idx, documentTypeIsSales ? 'margin_percent' : 'brand')"
                 placeholder="Price type...">
                 <template #selected-option="{ label }">
                   <div class="text-truncate" style="max-width: 130px">{{ label }}</div>
                 </template>
                 <template #option="{ label }">
                   <div class="text-truncate" style="max-width: 130px">{{ label }}</div>
                 </template>
               </v-select>
               <div
                v-if="documentTypeIsSales && pricingHint(row)"
                class="small text-muted mt-1 text-truncate"
                style="max-width: 180px"
                v-tt
                :data-title="pricingHint(row)">
                {{ pricingHint(row) }}
              </div>
            </td>

            <!-- Margin % (solo documentos de venta: is_sales) -->
            <td v-if="documentTypeIsSales">
              <input
                :id="`margin_percent-${idx}`"
                type="number"
                min="0"
                max="100"
                step="0.01"
                class="form-control form-control-sm"
                :class="{ 'is-invalid': row._errors?.margin_percent }"
                v-model.number="row.margin_percent"
                :disabled="disabled || !canEditLineMargin"
                @input="onMarginPercentInput(idx)"
                @keydown.enter="focusNextField(idx, 'brand')"
                @focus="$event.target.select()"
                placeholder="0.00" />
              <div class="text-danger small" v-if="row._errors?.margin_percent">
                {{ row._errors.margin_percent[0] }}
              </div>
            </td>

            <!-- Brand -->
            <td>
               <v-select
                 append-to-body
                 :id="`brand-${idx}`"
                 :options="(row.brands && row.brands.length > 0) ? row.brands : brandsOptions"
                 :reduce="o => o.value"
                 label="label"
                 v-model="row.brand"
                 @keydown.enter="focusNextRow(idx)"
                 :placeholder="(row.brands && row.brands.length > 0) ? 'Brand...' : 'Load brands from product...'"
                 :disabled="disabled || !row.product">
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

            <!-- Line total (siempre neto: qty × unit_price × (1 − disc%); ver lineTotalAfterDiscount) -->
            <td class="text-end">
              {{ currency(lineTotalAfterDiscount(row)) }}
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
    documentId: { type: [Number, null], default: null },
    documentTypeCreatesSerializedItems: { type: Boolean, default: false },
    documentTypeId: { type: [Number, null], default: null },
    workAccountId: { type: [Number, null], default: null },
    unitsOptions: { type: Array, default: () => [] },
    warehousesOptions: { type: Array, default: () => [] },
    priceTypesOptions: { type: Array, default: () => [] },
    brandsOptions: { type: Array, default: () => [] },
    mergeDuplicates: { type: Boolean, default: true },
    /** Solo documentos de venta: precio automático desde costo de compra + tipo de precio */
    documentTypeIsSales: { type: Boolean, default: false },
    /** Solo bloquea «Agregar fila» y los inputs de línea (sin overlay sobre la tabla) */
    disabled: { type: Boolean, default: false },
  });
  const emit = defineEmits(['update:lines', 'recalc', 'open-asset-tags']);

  const linesLocal = ref([]);
  const selectAll = ref(false);
  const productOptions = ref([]);
  const loading = ref({ products: {} });
  const isUpdatingFromProps = ref(false);
  const defaultWarehouse = ref(null);

  function hasPermission(permission) {
    try {
      const userPermissions = JSON.parse(localStorage.getItem('userPermissions') || '{}');
      const permissions = Array.isArray(userPermissions?.permissions) ? userPermissions.permissions : [];
      return permissions.includes(permission);
    } catch {
      return false;
    }
  }

  const canEditLineMargin = computed(
    () =>
      props.documentTypeIsSales &&
      (hasPermission('appinventory.add_pricetype') ||
        hasPermission('appinventory.change_pricetype'))
  );

  function lineStructureKey(l) {
    const p = l?.product;
    const prod =
      p != null && typeof p === 'object' && !Array.isArray(p) && 'id' in p
        ? p.id
        : p;
    return `${l?.id ?? ''}|${l?.__key ?? ''}|${prod ?? ''}`;
  }

  function linesStructureSignature(rows) {
    return (rows || []).map(lineStructureKey).join('\n');
  }

  watch(
    () => props.lines,
    async val => {
      console.log('LinesGrid: lines prop changed:', val);
      isUpdatingFromProps.value = true;

      const newLines = (val || []).map(x => ({
        ...x,
        __key: x.__key || x.id || cryptoRandom(),
        brands: x.brands || [],
        price_manually_edited: x.price_manually_edited ?? x.pricing_rule === 'MANUAL',
        _purchase_unit_cost: x._purchase_unit_cost ?? null,
        _suppressPriceEvent: false,
      }));
      console.log('🔍 New lines with product_label:', newLines.map(l => ({ 
        product: l.product, 
        product_label: l.product_label 
      })));

      // Comparar también contenido cuando todos los ids son null (importar favoritos, etc.)
      const currentLength = linesLocal.value.length;
      const newLength = newLines.length;
      const currentIds = linesLocal.value.map(l => l.id).sort();
      const newIds = newLines.map(l => l.id).sort();
      const structureChanged =
        linesStructureSignature(linesLocal.value) !== linesStructureSignature(newLines);

      if (
        currentLength !== newLength ||
        JSON.stringify(currentIds) !== JSON.stringify(newIds) ||
        structureChanged
      ) {
        linesLocal.value = newLines;

        // If no lines exist, add one empty line for user to start with
        if (linesLocal.value.length === 0) {
          addLine();
        }
        nextTick(() => {
          recalcAllRows();
        });
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

  /** Recalcular totales si cambia venta/no venta (columna Margin y reglas). */
  watch(
    () => props.documentTypeIsSales,
    () => {
      nextTick(() => recalcAllRows());
    }
  );

  function cryptoRandom() {
    return Math.random().toString(36).slice(2) + Date.now().toString(36);
  }

  function currency(n) {
    const num = Number(n || 0);
    return num.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
  }

  /** Importe de línea con descuento aplicado (única fuente de verdad para mostrar y para final_price) */
  function lineTotalAfterDiscount(row) {
    if (!row) return 0;
    const qty = Number(row.quantity || 0);
    const price = Number(row.unit_price || 0);
    const disc = Math.min(100, Math.max(0, Number(row.discount_percentage || 0)));
    return +(qty * price * (1 - disc / 100)).toFixed(2);
  }

  function salePriceFromCost(cost, pricingMethod, pct) {
    const c = Number(cost);
    const p = Number(pct);
    if (!Number.isFinite(c) || c <= 0 || !Number.isFinite(p)) return null;
    const f = p / 100;
    if (pricingMethod === 'MARKUP') return +(c * (1 + f)).toFixed(2);
    if (pricingMethod === 'MARGIN') {
      if (f >= 1) return null;
      return +(c / (1 - f)).toFixed(2);
    }
    return null;
  }

  function pricingHint(row) {
    if (!props.documentTypeIsSales) return '';
    if (row.pricing_rule === 'MANUAL') {
      if (row.margin_percent != null && row.margin_percent !== '')
        return `Manual · ref. ${Number(row.margin_percent).toFixed(2)}%`;
      return 'Manual';
    }
    if (row.pricing_rule === 'MARKUP' && row.margin_percent != null && row.margin_percent !== '')
      return `Mkup ${Number(row.margin_percent).toFixed(2)}%`;
    if (row.pricing_rule === 'MARGIN' && row.margin_percent != null && row.margin_percent !== '')
      return `Margen ${Number(row.margin_percent).toFixed(2)}%`;
    return '';
  }

  /** Margen/markup por defecto del Price Type seleccionado (solo ventas). */
  function syncPriceTypeMetadataToRow(idx) {
    const r = linesLocal.value[idx];
    if (!r || !props.documentTypeIsSales || !r.price_type) return;
    const meta = props.priceTypesOptions.find(o => o.value === r.price_type);
    if (!meta) return;

    if (meta.pricing_method === 'MARKUP' || meta.pricing_method === 'MARGIN') {
      if (meta.margin_percent != null && meta.margin_percent !== '') {
        r.margin_percent = Number(meta.margin_percent);
      }
      r.pricing_rule = meta.pricing_method;
    } else {
      r.pricing_rule = null;
    }
  }

  /**
   * Precio de catálogo (ProductPrice / default-price) cuando no aplica costo+markup/margen.
   */
  async function applyDefaultCatalogPrice(idx) {
    const r = linesLocal.value[idx];
    if (!r?.product || !r.unit || r.price_manually_edited) return;
    try {
      const params = {};
      if (props.documentTypeId) params.document_type_id = props.documentTypeId;
      params.unit = r.unit;
      const { data } = await axios.get(`/api/products/${r.product}/default-price/`, { params });
      if (data.unit_price != null && data.unit_price !== undefined) {
        r._suppressPriceEvent = true;
        r.unit_price = Number(data.unit_price);
        nextTick(() => {
          r._suppressPriceEvent = false;
        });
      }
      // Mismo ProductPrice que fija el precio: reflejar su tipo de precio en el select
      if (data.price_type != null && data.price_type !== undefined) {
        r.price_type = data.price_type;
        syncPriceTypeMetadataToRow(idx);
      }
      if (data.purchase_unit_cost != null) {
        r._purchase_unit_cost = Number(data.purchase_unit_cost);
      }
    } catch (e) {
      console.warn('applyDefaultCatalogPrice:', e);
    }
  }

  async function refreshPurchaseCost(idx) {
    const r = linesLocal.value[idx];
    if (!r?.product) {
      r._purchase_unit_cost = null;
      return;
    }
    try {
      const params = {};
      if (r.unit) params.unit = r.unit;
      const { data } = await axios.get(`/api/products/${r.product}/purchase-cost/`, { params });
      r._purchase_unit_cost = data.unit_cost != null ? Number(data.unit_cost) : null;
    } catch {
      r._purchase_unit_cost = null;
    }
  }

  /** true si se recalculó unit_price desde costo de compra + tipo de precio. */
  function tryApplyAutoPricing(idx) {
    if (!props.documentTypeIsSales) return false;
    const r = linesLocal.value[idx];
    if (!r || r.price_manually_edited) return false;
    if (!r.product || !r.price_type || !r.unit) return false;
    const meta = props.priceTypesOptions.find(o => o.value === r.price_type);
    if (!meta || !meta.pricing_method || meta.pricing_method === 'NONE') return false;
    const cost = r._purchase_unit_cost;
    if (cost == null || cost <= 0) return false;
    const pct = r.margin_percent ?? meta.margin_percent;
    if (pct == null || pct === '') return false;
    const price = salePriceFromCost(cost, meta.pricing_method, Number(pct));
    if (price == null) return false;
    r._suppressPriceEvent = true;
    r.unit_price = price;
    r.pricing_rule = meta.pricing_method === 'MARKUP' ? 'MARKUP' : 'MARGIN';
    r.margin_percent = Number(pct);
    nextTick(() => {
      r._suppressPriceEvent = false;
    });
    return true;
  }

  function onMarginPercentInput(idx) {
    const r = linesLocal.value[idx];
    if (!r) return;

    if (!props.documentTypeIsSales) {
      recalcRow(idx);
      return;
    }

    if (!canEditLineMargin.value) {
      recalcRow(idx);
      return;
    }

    if (r.margin_percent === '' || r.margin_percent === null || r.margin_percent === undefined) {
      r.margin_percent = null;
      recalcRow(idx);
      return;
    }

    const parsed = Number(r.margin_percent);
    if (!Number.isFinite(parsed)) {
      r.margin_percent = null;
      recalcRow(idx);
      return;
    }

    r.margin_percent = Math.min(100, Math.max(0, parsed));

    if (r.pricing_rule !== 'MANUAL') {
      r.price_manually_edited = false;
      tryApplyAutoPricing(idx);
    }

    recalcRow(idx);
  }

  function onDiscountPercentageInput(idx) {
    recalcRow(idx);
  }

  async function onUnitUpdated(idx) {
    const r = linesLocal.value[idx];
    r.price_manually_edited = false;
    await refreshPurchaseCost(idx);
    syncPriceTypeMetadataToRow(idx);
    if (props.documentTypeIsSales) {
      const applied = tryApplyAutoPricing(idx);
      if (!applied) await applyDefaultCatalogPrice(idx);
    } else {
      await applyDefaultCatalogPrice(idx);
    }
    recalcRow(idx);
  }

  /** La cantidad no cambia el precio unitario; sí el importe de línea y totales. */
  function onQuantityInput(idx) {
    recalcRow(idx);
  }

  /**
   * Tras escribir cantidad: unificar duplicados al salir del campo (blur).
   * Comprueba __key para no fusionar con índice equivocado si Enter ya fusionó antes del blur.
   */
  function onQuantityBlurMerge(idx) {
    const row = linesLocal.value[idx];
    if (!row?.__key) return;
    const keySnapshot = row.__key;
    queueMicrotask(() => {
      if (!props.mergeDuplicates) return;
      const still = linesLocal.value[idx];
      if (!still || still.__key !== keySnapshot) return;
      maybeMergeDuplicate(idx);
    });
  }

  /**
   * Enter en cantidad: intenta unificar y enfoca unidad en la fila que queda (o la actual si no hubo merge).
   */
  function onQuantityEnterMerge(idx, e) {
    if (e?.preventDefault) e.preventDefault();
    if (props.mergeDuplicates) {
      const survivorIdx = maybeMergeDuplicate(idx);
      if (survivorIdx !== null && survivorIdx !== undefined) {
        nextTick(() => focusNextField(survivorIdx, 'unit'));
        return;
      }
    }
    focusNextField(idx, 'unit');
  }

  function onUnitPriceInput(idx) {
    const r = linesLocal.value[idx];
    if (r._suppressPriceEvent) {
      recalcRow(idx);
      return;
    }
    r.price_manually_edited = true;
    r.pricing_rule = 'MANUAL';
    recalcRow(idx);
  }

  function onPriceTypeUpdated(idx) {
    const r = linesLocal.value[idx];
    r.price_manually_edited = false;
    syncPriceTypeMetadataToRow(idx);
    nextTick(async () => {
      await refreshPurchaseCost(idx);
      if (props.documentTypeIsSales) {
        const applied = tryApplyAutoPricing(idx);
        if (!applied) await applyDefaultCatalogPrice(idx);
      } else {
        await applyDefaultCatalogPrice(idx);
      }
      recalcRow(idx);
    });
  }

  function recalcRow(idx) {
    const r = linesLocal.value[idx];
    if (!r) {
      console.warn(`recalcRow: Line at index ${idx} not found`);
      return;
    }
    r.final_price = lineTotalAfterDiscount(r);
  }

  function recalcAllRows() {
    linesLocal.value.forEach((_, idx) => recalcRow(idx));
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
      pricing_rule: null,
      margin_percent: null,
      price_manually_edited: false,
      _purchase_unit_cost: null,
      _suppressPriceEvent: false,
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
    const newIdx = idx + 1;
    linesLocal.value.splice(newIdx, 0, duplicatedLine);
    recalcRow(newIdx);
  }

  const hasSelection = computed(() => linesLocal.value.some(r => r.selected));
  function removeSelected() {
    linesLocal.value = linesLocal.value.filter(r => !r.selected);
    selectAll.value = false;
  }

  function duplicateSelected() {
    const selectedLines = linesLocal.value.filter(r => r.selected);
    const start = linesLocal.value.length;
    selectedLines.forEach(line => {
      const duplicatedLine = {
        ...line,
        __key: cryptoRandom(),
        selected: false,
        id: null, // Reset ID for new line
        quantity: 1, // Reset quantity to 1
        final_price: 0, // se recalcula abajo
        _errors: {},
      };
      linesLocal.value.push(duplicatedLine);
    });
    for (let i = start; i < linesLocal.value.length; i++) {
      recalcRow(i);
    }
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
    r.price_manually_edited = false;

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

        if (data.purchase_unit_cost != null) {
          r._purchase_unit_cost = Number(data.purchase_unit_cost);
        }
        
      } catch (error) {
        console.warn('Could not fetch product default price:', error);
        
        // Fallback: Auto-fill default unit from product if available
        if (option?.product?.unit_default) {
          r.unit = option.product.unit_default.id || option.product.unit_default;
        }
        
        // Fallback: obtener marcas disponibles del producto usando la función dedicada
        await updateBrandsForProduct(idx, option.value);
        await refreshPurchaseCost(idx);
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

    // La unificación de duplicados (product+unit+brand) ocurre al terminar de editar cantidad
    // (blur o Enter), no aquí, para permitir ajustar cantidad antes de sumar.

    syncPriceTypeMetadataToRow(idx);
    if (r.product && r.unit) {
      await refreshPurchaseCost(idx);
    }
    if (props.documentTypeIsSales) {
      const applied = tryApplyAutoPricing(idx);
      if (!applied) await applyDefaultCatalogPrice(idx);
    }
    recalcRow(idx);
  }

  function onProductCleared(idx) {
    const r = linesLocal.value[idx];
    r.product_label = '';
    r.product = null;
    r.unit = null;
    r.price_type = null;
    r.brand = null;
    r.brands = [];
    r.pricing_rule = null;
    r.margin_percent = null;
    r.price_manually_edited = false;
    r._purchase_unit_cost = null;
    recalcRow(idx);
  }

  /**
   * Fallback de tipo de precio cuando la línea (p. ej. favorito) no lo trae y hay cuenta operativa.
   */
  async function ensureWorkAccountDefaultPriceTypeIfNeeded(idx) {
    const r = linesLocal.value[idx];
    if (!r || props.workAccountId === null || props.workAccountId === undefined || r.price_type) return;
    try {
      const { data } = await axios.get(`/api/work-accounts/${props.workAccountId}/`);
      if (data.default_price_type) {
        r.price_type = data.default_price_type;
      }
    } catch (error) {
      if (error.response?.status === 404) {
        console.warn(`Work account ${props.workAccountId} not found, skipping default price type`);
      } else {
        console.warn('Could not fetch work account default price type:', error);
      }
    }
  }

  /**
   * Recalcula precio por línea con las mismas reglas que al elegir producto en el select
   * (markup/margen desde costo, catalog default-price si aplica).
   * Uso: import desde favoritos (lines_data puede traer precios obsoletos).
   */
  async function rehydratePricingForRow(idx) {
    const r = linesLocal.value[idx];
    if (!r?.product) return;

    r.price_manually_edited = false;

    await updateBrandsForProduct(idx, r.product);

    try {
      const params = {};
      if (props.documentTypeId) params.document_type_id = props.documentTypeId;
      if (r.unit) params.unit = r.unit;
      const { data } = await axios.get(`/api/products/${r.product}/default-price/`, { params });

      if (!r.unit && data.unit) r.unit = data.unit;
      if (data.price_type != null && data.price_type !== undefined) {
        r.price_type = data.price_type;
      }
      if (data.default_brand?.id != null && (r.brand == null || r.brand === '')) {
        r.brand = data.default_brand.id;
      }
      if (data.purchase_unit_cost != null) {
        r._purchase_unit_cost = Number(data.purchase_unit_cost);
      }
    } catch (e) {
      console.warn('rehydratePricingForRow default-price:', e);
    }

    await ensureWorkAccountDefaultPriceTypeIfNeeded(idx);

    syncPriceTypeMetadataToRow(idx);

    if (r.product && r.unit) {
      await refreshPurchaseCost(idx);
    }

    if (props.documentTypeIsSales) {
      const applied = tryApplyAutoPricing(idx);
      if (!applied) await applyDefaultCatalogPrice(idx);
    } else {
      await applyDefaultCatalogPrice(idx);
    }

    recalcRow(idx);
  }

  /**
   * Tras importar favoritos: repreciar solo líneas marcadas por TransactionForm
   * (__favoriteImportReprice), sin alterar líneas que ya había antes del append.
   */
  async function rehydratePricingAfterFavoriteImport() {
    await nextTick();
    for (let i = 0; i < linesLocal.value.length; i++) {
      const row = linesLocal.value[i];
      if (!row?.product || !row.__favoriteImportReprice) continue;
      await rehydratePricingForRow(i);
      delete row.__favoriteImportReprice;
    }
    emit('recalc');
  }

  /**
   * Si hay otra línea con mismo product+unit+brand, suma cantidad ahí y elimina la fila actual.
   * @returns {number|null} Índice de la fila que permanece (tras splice), o null si no hubo merge.
   */
  function maybeMergeDuplicate(idx) {
    const r = linesLocal.value[idx];
    if (!r?.product) return null;

    for (let i = 0; i < linesLocal.value.length; i++) {
      if (i === idx) continue;
      const o = linesLocal.value[i];
      if (o.product === r.product && (o.unit || null) === (r.unit || null) && (o.brand || null) === (r.brand || null)) {
        const keepIdx = i;
        o.quantity = Number(o.quantity || 0) + Number(r.quantity || 0);
        recalcRow(keepIdx);
        linesLocal.value.splice(idx, 1);
        return keepIdx < idx ? keepIdx : keepIdx - 1;
      }
    }
    return null;
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

      if (props.documentTypeIsSales) {
        if (line.margin_percent !== null && line.margin_percent !== undefined && line.margin_percent !== '') {
          const mp = Number(line.margin_percent);
          if (!Number.isFinite(mp) || mp < 0 || mp > 100) {
            line._errors.margin_percent = ['Margin % must be between 0 and 100'];
            isValid = false;
          }
        }
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
        'margin_percent': 'margin_percent',
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

  defineExpose({
    validateLines,
    rehydratePricingAfterFavoriteImport,
    rehydratePricingForRow,
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

  /*
   * Deshabilitado: mismo aspecto que .form-control:disabled (Bootstrap),
   * vue-select por defecto usa gris casi blanco (--vs-state-disabled-bg).
   */
  :deep(.vs--disabled) {
    --vs-disabled-bg: var(--bs-secondary-bg, #e9ecef);
    --vs-state-disabled-bg: var(--bs-secondary-bg, #e9ecef);
  }

  :deep(.vs--disabled .vs__dropdown-toggle) {
    background-color: var(--bs-secondary-bg, #e9ecef) !important;
    border-color: var(--bs-border-color, #ced4da);
  }

  :deep(.vs--disabled .vs__search) {
    background-color: transparent !important;
    color: var(--bs-secondary-color, #6c757d);
  }

  :deep(.vs--disabled.vs--single .vs__selected) {
    color: var(--bs-secondary-color, #6c757d);
  }

  :deep(.vs--disabled .vs__open-indicator) {
    fill: var(--bs-secondary-color, #6c757d);
    opacity: 0.65;
  }

  .card-header .btn.btn-outline-primary:disabled,
  .card-header .btn.btn-outline-primary.disabled {
    cursor: not-allowed;
    opacity: 0.65;
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
