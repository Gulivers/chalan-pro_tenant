<template>
  <div class="card">
    <div class="card-header">
      <div class="d-none d-md-flex align-items-center justify-content-between">
        <div class="d-flex gap-2">
          <button class="btn btn-outline-primary" type="button" @click="addLine">
            <i class="bi bi-plus-lg me-1"></i>
            Add Row
          </button>
          <button class="btn btn-outline-danger" type="button" :disabled="!hasSelection" @click="removeSelected">
            <i class="bi bi-trash me-1"></i>
            Delete selected
          </button>
        </div>
        <div class="small text-muted">Rows: {{ linesLocal?.length || 0 }}</div>
      </div>
      <div class="d-md-none">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <div class="small text-muted">Rows: {{ linesLocal?.length || 0 }}</div>
        </div>
        <div class="d-flex gap-1 flex-wrap">
          <button class="btn btn-outline-primary btn-sm flex-fill" type="button" @click="addLine">
            <i class="bi bi-plus-lg"></i>
            <span class="ms-1">Add Row</span>
          </button>
          <button class="btn btn-outline-danger btn-sm flex-fill" type="button" :disabled="!hasSelection" @click="removeSelected">
            <i class="bi bi-trash"></i>
            <span class="ms-1">Delete</span>
          </button>
        </div>
      </div>
    </div>

    <div class="table-responsive" style="max-height: 70vh; min-height: 300px">
      <table class="table table-sm align-middle table-hover table-sticky">
        <thead>
          <tr>
            <th style="width: 30px" class="text-center">
              <input type="checkbox" class="form-check-input" v-model="selectAll" />
            </th>
            <th style="min-width: 240px">Product <span class="text-danger">*</span></th>
            <th style="min-width: 160px">From Warehouse</th>
            <th style="min-width: 160px">To Warehouse</th>
            <th style="min-width: 90px">Quantity</th>
            <th style="min-width: 140px">Unit</th>
            <th style="min-width: 200px">Serialized item</th>
            <th style="width: 70px"></th>
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
                placeholder="Search product..."
                :disabled="isReadOnly"
                :class="{ 'is-invalid': row._errors?.product }">
                <template #selected-option="{ label, product }">
                  <div class="d-flex align-items-center gap-2" style="max-width: 260px">
                    <span class="text-truncate">{{ row.product_label || product?.name || label || 'No name' }}</span>
                    <span
                      v-if="product?.tracking_mode === 'SERIALIZED'"
                      class="badge bg-info flex-shrink-0"
                      style="font-size: 0.65rem">
                      SERIALIZED
                    </span>
                  </div>
                </template>
                <template #option="{ label, product }">
                  <div class="d-flex align-items-center gap-2" style="max-width: 260px">
                    <span class="text-truncate">{{ product?.name || label || 'No name' }}</span>
                    <span
                      v-if="product?.tracking_mode === 'SERIALIZED'"
                      class="badge bg-info flex-shrink-0"
                      style="font-size: 0.65rem">
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

            <td>
              <span class="form-control-plaintext small">
                {{ fromWarehouseLabel }}
              </span>
            </td>

            <td>
              <span class="form-control-plaintext small">
                {{ toWarehouseLabel }}
              </span>
            </td>

            <td>
              <input
                :id="`quantity-${idx}`"
                type="number"
                min="0.01"
                step="0.01"
                class="form-control form-control-sm"
                :class="{ 'is-invalid': row._errors?.quantity }"
                v-model.number="row.quantity"
                :disabled="row.isSerialized || isReadOnly"
                placeholder="1.00" />
              <div class="text-danger small" v-if="row._errors?.quantity">{{ row._errors.quantity[0] }}</div>
            </td>

            <td>
              <v-select
                :id="`unit-${idx}`"
                :options="unitsOptions"
                :reduce="o => o.value"
                label="label"
                v-model="row.unit"
                :disabled="isReadOnly"
                :class="{ 'is-invalid': row._errors?.unit }"
                placeholder="Select unit...">
                <template #selected-option="{ label }">
                  <div class="text-truncate" style="max-width: 130px">{{ label }}</div>
                </template>
                <template #option="{ label }">
                  <div class="text-truncate" style="max-width: 130px">{{ label }}</div>
                </template>
              </v-select>
              <div class="text-danger small" v-if="row._errors?.unit">{{ row._errors.unit[0] }}</div>
            </td>

            <td>
              <v-select
                :id="`serialized-${idx}`"
                :options="row.serializedOptions || []"
                label="label"
                :reduce="o => o.value"
                v-model="row.serialized_item"
                :disabled="!row.product || !row.isSerialized || isReadOnly"
                :loading="loading.serialized[idx]"
                @search="q => searchSerialized(idx, q)"
                placeholder="Select asset tag..."
                clearable>
                <template #selected-option="{ label }">
                  <div class="text-truncate" style="max-width: 180px">{{ label }}</div>
                </template>
                <template #option="{ label }">
                  <div class="text-truncate" style="max-width: 180px">{{ label }}</div>
                </template>
                <template #no-options>
                  <div class="text-muted small">
                    {{ row.isSerialized ? (row.product ? 'Type to search...' : 'Select product first') : '—' }}
                  </div>
                </template>
              </v-select>
              <div class="text-danger small" v-if="row._errors?.serialized_item">{{ row._errors.serialized_item[0] }}</div>
            </td>

            <td class="text-end">
              <button
                v-if="!isReadOnly"
                class="btn btn-sm btn-outline-danger"
                type="button"
                @click="removeRow(idx)"
                title="Remove line">
                <i class="bi bi-x-lg"></i>
              </button>
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
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  lines: { type: Array, default: () => [] },
  fromWarehouseId: { type: [Number, null], default: null },
  toWarehouseId: { type: [Number, null], default: null },
  warehousesOptions: { type: Array, default: () => [] },
  unitsOptions: { type: Array, default: () => [] },
  isReadOnly: { type: Boolean, default: false },
});

const emit = defineEmits(['update:lines']);

const linesLocal = ref([]);
const selectAll = ref(false);
const productOptions = ref([]);
const loading = ref({ products: {}, serialized: {} });
const isUpdatingFromProps = ref(false);

const fromWarehouseLabel = computed(() => {
  if (!props.fromWarehouseId) return '—';
  const w = props.warehousesOptions.find(x => x.value === props.fromWarehouseId);
  return w?.label || '—';
});

const toWarehouseLabel = computed(() => {
  if (!props.toWarehouseId) return '—';
  const w = props.warehousesOptions.find(x => x.value === props.toWarehouseId);
  return w?.label || '—';
});

watch(
  () => props.lines,
  val => {
    isUpdatingFromProps.value = true;
    const newLines = (val || []).map(x => ({
      ...x,
      __key: x.__key || x.id || cryptoRandom(),
      serializedOptions: x.serializedOptions || [],
      isSerialized: x.isSerialized ?? false,
    }));
    if (newLines.length > 0) {
      linesLocal.value = newLines;
    } else if (linesLocal.value.length === 0) {
      addLine();
    }
    nextTick(() => { isUpdatingFromProps.value = false; });
  },
  { immediate: true, deep: true }
);

watch(
  linesLocal,
  val => {
    if (!isUpdatingFromProps.value) {
      nextTick(() => emit('update:lines', val));
    }
  },
  { deep: true }
);

watch(selectAll, checked => { linesLocal.value.forEach(r => (r.selected = checked)); });

function cryptoRandom() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
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
    serialized_item: null,
    serializedOptions: [],
    isSerialized: false,
    _errors: {},
  };
  linesLocal.value.push(newLine);
}

function removeRow(idx) {
  linesLocal.value.splice(idx, 1);
}

const hasSelection = computed(() => linesLocal.value.some(r => r.selected));

function removeSelected() {
  linesLocal.value = linesLocal.value.filter(r => !r.selected);
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
      params: { search: query, page_size: 20, is_active: true },
    });
    const list = Array.isArray(data) ? data : data?.results || [];
    productOptions.value = list.map(p => ({
      value: p.id,
      label: `${p.name} (${p.sku})`,
      product: p,
    }));
  } catch (error) {
    productOptions.value = [];
  } finally {
    loading.value.products[idx] = false;
  }
}

async function searchSerialized(idx, query) {
  const r = linesLocal.value[idx];
  if (!r?.product || !props.fromWarehouseId) return;
  loading.value.serialized[idx] = true;
  try {
    const { data } = await axios.get('/api/serialized-items-provider/', {
      params: {
        page: 1,
        per_page: 30,
        search: query || '',
        product_id: r.product,
        warehouse_id: props.fromWarehouseId,
      },
    });
    const list = data?.items || [];
    r.serializedOptions = list.map(s => ({
      value: s.id,
      label: `${s.asset_tag || s.id} (${s.product_name || ''})`,
    }));
  } catch (error) {
    r.serializedOptions = [];
  } finally {
    loading.value.serialized[idx] = false;
  }
}

async function onProductSelected(idx, option) {
  const r = linesLocal.value[idx];
  r.product_label = option?.product?.name || option?.label || '';
  r.isSerialized = option?.product?.tracking_mode === 'SERIALIZED';
  if (r.isSerialized) {
    r.quantity = 1;
    r.serializedOptions = [];
    r.serialized_item = null;
    await searchSerialized(idx, '');
  } else {
    r.serialized_item = null;
    r.serializedOptions = [];
    try {
      const { data } = await axios.get(`/api/products/${option.value}/default-price/`);
      if (data?.unit) r.unit = data.unit;
    } catch (_) {
      if (option?.product?.unit_default) r.unit = option.product.unit_default?.id;
    }
  }
}

function onProductChanged(idx, val) {
  if (!val) {
    const r = linesLocal.value[idx];
    r.product_label = '';
    r.isSerialized = false;
    r.serialized_item = null;
    r.serializedOptions = [];
  }
}

function onProductCleared(idx) {
  const r = linesLocal.value[idx];
  r.product_label = '';
  r.isSerialized = false;
  r.serialized_item = null;
  r.serializedOptions = [];
}

function validateLines() {
  let isValid = true;
  linesLocal.value.forEach(row => {
    row._errors = {};
    if (!row.product) {
      row._errors.product = ['Product is required'];
      isValid = false;
    }
    if (!row.isSerialized && (row.quantity == null || row.quantity <= 0)) {
      row._errors.quantity = ['Quantity must be greater than 0'];
      isValid = false;
    }
    if (row.isSerialized && !row.serialized_item) {
      row._errors.serialized_item = ['Serialized item is required'];
      isValid = false;
    }
  });
  return isValid;
}

onMounted(() => {
  if (linesLocal.value.length === 0) addLine();
});

defineExpose({ validateLines });
</script>

<style scoped>
.table tbody tr:hover { background-color: #fafafa; }
.is-invalid { border-color: #dc3545; }
:deep(.is-invalid .vs__dropdown-toggle) { border-color: #dc3545; }
.table-sticky thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}
:deep(.vs__dropdown-menu) { z-index: 1050 !important; }
:deep(.vs__dropdown-toggle) { z-index: 1049 !important; }
.table-responsive { border-radius: 0.375rem; overflow-x: auto; }
.form-control-plaintext { padding: 0.225rem 0.45rem; }
</style>
