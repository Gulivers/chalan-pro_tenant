<template>
  <div class="jr-transfer-lines">
    <div class="jr-transfer-lines__toolbar">
      <div class="jr-transfer-lines__toolbar-actions">
        <JRButton
          type="button"
          variant="secondary"
          size="sm"
          :disabled="isReadOnly"
          @click="addLine">
          + Add Row
        </JRButton>
        <JRButton
          type="button"
          variant="danger"
          size="sm"
          :disabled="isReadOnly || !hasSelection"
          @click="removeSelected">
          Delete selected
        </JRButton>
      </div>
      <span class="jr-transfer-lines__count">Rows: {{ linesLocal?.length || 0 }}</span>
    </div>

    <div v-if="isCompact" class="jr-transfer-lines__compact">
      <JREmptyState
        v-if="!linesLocal.length"
        title="No transfer lines"
        description="Add a row to move products between warehouses.">
        <JRButton
          v-if="!isReadOnly"
          type="button"
          variant="secondary"
          size="sm"
          @click="addLine">
          + Add Row
        </JRButton>
      </JREmptyState>
      <ul v-else class="jr-transfer-line-list">
        <li
          v-for="(row, idx) in linesLocal"
          :key="row.__key"
          class="jr-transfer-line-item"
          :class="{
            'jr-transfer-line-item--error':
              Object.keys(row._errors || {}).length > 0,
          }">
          <div class="jr-transfer-line-item__check">
            <JRCheckbox
              v-if="!isReadOnly"
              :modelValue="!!row.selected"
              :ariaLabel="`Select line ${idx + 1}`"
              @update:modelValue="(v) => (row.selected = v)" />
          </div>
          <div class="jr-transfer-line-item__main">
              <JRField
              :label="`Product`"
              :inputId="`product-m-${idx}`"
              required
              :error="rowErrorText(row._errors?.product)">
              <Select
                class="jr-control"
                :inputId="`product-m-${idx}`"
                :modelValue="row.product"
                :options="optionsForProduct(row)"
                optionLabel="label"
                optionValue="value"
                placeholder="Search product…"
                filter
                filterPlaceholder="Type at least 2 characters…"
                emptyFilterMessage="Type at least 2 characters to search…"
                :loading="!!loading.products[idx]"
                :disabled="isReadOnly"
                :invalid="!!row._errors?.product"
                showClear
                fluid
                @filter="(e) => onProductFilter(idx, e)"
                @show="() => onProductShow(idx, row)"
                @update:modelValue="(val) => onProductModel(idx, val)" />
              <JRBadge
                v-if="row.isSerialized"
                class="jr-transfer-line-item__serial-badge"
                value="Serial tracking"
                severity="info" />
            </JRField>

            <p class="jr-transfer-line-item__route">
              {{ fromWarehouseLabel }} → {{ toWarehouseLabel }}
            </p>

            <div class="jr-transfer-line-item__grid">
              <JRField
                label="Quantity"
                :inputId="`quantity-m-${idx}`"
                :error="rowErrorText(row._errors?.quantity)">
                <JRInput
                  :inputId="`quantity-m-${idx}`"
                  type="number"
                  :modelValue="row.quantity"
                  :min="0.01"
                  :minFractionDigits="0"
                  :maxFractionDigits="2"
                  placeholder="1.00"
                  :disabled="row.isSerialized || isReadOnly"
                  :invalid="!!row._errors?.quantity"
                  @update:modelValue="(v) => (row.quantity = v)" />
              </JRField>

              <JRField
                label="Unit"
                :inputId="`unit-m-${idx}`"
                :error="rowErrorText(row._errors?.unit)">
                <JRSelect
                  :inputId="`unit-m-${idx}`"
                  v-model="row.unit"
                  :options="unitsOptions"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Select unit…"
                  filter
                  :disabled="isReadOnly"
                  :invalid="!!row._errors?.unit" />
              </JRField>
            </div>

            <JRField
              v-if="row.isSerialized"
              label="Serialized item"
              :inputId="`serialized-m-${idx}`"
              required
              :error="rowErrorText(row._errors?.serialized_item)">
              <Select
                class="jr-control"
                :inputId="`serialized-m-${idx}`"
                :modelValue="row.serialized_item"
                :options="row.serializedOptions || []"
                optionLabel="label"
                optionValue="value"
                placeholder="Select serial number…"
                filter
                filterPlaceholder="Search serial…"
                :loading="!!loading.serialized[idx]"
                :disabled="!row.product || isReadOnly"
                :invalid="!!row._errors?.serialized_item"
                showClear
                fluid
                @filter="(e) => onSerializedFilter(idx, e)"
                @show="() => searchSerialized(idx, '')"
                @update:modelValue="(val) => (row.serialized_item = val)" />
            </JRField>

            <div
              v-if="row.isSerialized && row.serialized_item"
              class="jr-transfer-line-item__badges">
              <JRBadge
                v-if="serializedStatus(row)"
                :value="serializedStatus(row)"
                :severity="statusSeverity(serializedStatus(row))" />
              <JRBadge
                v-if="serializedCondition(row)"
                :value="conditionLabel(serializedCondition(row))"
                :severity="conditionSeverity(serializedCondition(row))" />
            </div>
          </div>
          <div v-if="!isReadOnly" class="jr-transfer-line-item__actions">
            <JRButton
              type="button"
              variant="ghost"
              size="sm"
              aria-label="Remove line"
              @click="removeRow(idx)">
              Remove
            </JRButton>
          </div>
        </li>
      </ul>
    </div>

    <div v-else class="jr-transfer-lines__table-wrap">
      <div class="jr-transfer-table-scroll">
        <table class="jr-transfer-table">
          <thead>
            <tr>
              <th class="jr-transfer-table__check">
                <JRCheckbox
                  v-if="!isReadOnly"
                  :modelValue="selectAll"
                  ariaLabel="Select all lines"
                  @update:modelValue="onSelectAll" />
              </th>
              <th>Product <span class="jr-transfer-req" aria-hidden="true">*</span></th>
              <th>From</th>
              <th>To</th>
              <th>Quantity</th>
              <th>Unit</th>
              <th>Serialized item</th>
              <th class="jr-transfer-table__center">Status</th>
              <th class="jr-transfer-table__center">Condition</th>
              <th class="jr-transfer-table__actions"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, idx) in linesLocal"
              :key="row.__key"
              :class="{
                'jr-transfer-table__row--error':
                  Object.keys(row._errors || {}).length > 0,
              }">
              <td class="jr-transfer-table__check">
                <JRCheckbox
                  v-if="!isReadOnly"
                  :modelValue="!!row.selected"
                  :ariaLabel="`Select line ${idx + 1}`"
                  @update:modelValue="(v) => (row.selected = v)" />
              </td>
              <td>
                <Select
                  class="jr-control"
                  :inputId="`product-${idx}`"
                  :modelValue="row.product"
                  :options="optionsForProduct(row)"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Search product…"
                  filter
                  filterPlaceholder="Type at least 2 characters…"
                  emptyFilterMessage="Type at least 2 characters to search…"
                  :loading="!!loading.products[idx]"
                  :disabled="isReadOnly"
                  :invalid="!!row._errors?.product"
                  showClear
                  fluid
                  @filter="(e) => onProductFilter(idx, e)"
                  @show="() => onProductShow(idx, row)"
                  @update:modelValue="(val) => onProductModel(idx, val)" />
                <JRBadge
                  v-if="row.isSerialized"
                  class="jr-transfer-table__serial-badge"
                  value="Serial tracking"
                  severity="info" />
                <p
                  v-if="row._errors?.product"
                  class="jr-transfer-row-error"
                  role="alert">
                  {{ rowErrorText(row._errors.product) }}
                </p>
              </td>
              <td>
                <span class="jr-transfer-table__readonly">{{
                  fromWarehouseLabel
                }}</span>
              </td>
              <td>
                <span class="jr-transfer-table__readonly">{{
                  toWarehouseLabel
                }}</span>
              </td>
              <td>
                <JRInput
                  :inputId="`quantity-${idx}`"
                  type="number"
                  :modelValue="row.quantity"
                  :min="0.01"
                  :minFractionDigits="0"
                  :maxFractionDigits="2"
                  placeholder="1.00"
                  :disabled="row.isSerialized || isReadOnly"
                  :invalid="!!row._errors?.quantity"
                  @update:modelValue="(v) => (row.quantity = v)" />
                <p
                  v-if="row._errors?.quantity"
                  class="jr-transfer-row-error"
                  role="alert">
                  {{ rowErrorText(row._errors.quantity) }}
                </p>
              </td>
              <td>
                <JRSelect
                  :inputId="`unit-${idx}`"
                  v-model="row.unit"
                  :options="unitsOptions"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Select unit…"
                  filter
                  :disabled="isReadOnly"
                  :invalid="!!row._errors?.unit" />
                <p
                  v-if="row._errors?.unit"
                  class="jr-transfer-row-error"
                  role="alert">
                  {{ rowErrorText(row._errors.unit) }}
                </p>
              </td>
              <td>
                <Select
                  class="jr-control"
                  :inputId="`serialized-${idx}`"
                  :modelValue="row.serialized_item"
                  :options="row.serializedOptions || []"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Select serial number…"
                  filter
                  :loading="!!loading.serialized[idx]"
                  :disabled="!row.product || !row.isSerialized || isReadOnly"
                  :invalid="!!row._errors?.serialized_item"
                  showClear
                  fluid
                  @filter="(e) => onSerializedFilter(idx, e)"
                  @show="() => row.isSerialized && searchSerialized(idx, '')"
                  @update:modelValue="(val) => (row.serialized_item = val)" />
                <p
                  v-if="row._errors?.serialized_item"
                  class="jr-transfer-row-error"
                  role="alert">
                  {{ rowErrorText(row._errors.serialized_item) }}
                </p>
              </td>
              <td class="jr-transfer-table__center">
                <JRBadge
                  v-if="row.isSerialized && row.serialized_item && serializedStatus(row)"
                  :value="serializedStatus(row)"
                  :severity="statusSeverity(serializedStatus(row))" />
                <span v-else class="jr-transfer-table__muted">—</span>
              </td>
              <td class="jr-transfer-table__center">
                <JRBadge
                  v-if="
                    row.isSerialized &&
                    row.serialized_item &&
                    serializedCondition(row)
                  "
                  :value="conditionLabel(serializedCondition(row))"
                  :severity="conditionSeverity(serializedCondition(row))" />
                <span v-else class="jr-transfer-table__muted">—</span>
              </td>
              <td class="jr-transfer-table__actions">
                <JRButton
                  v-if="!isReadOnly"
                  type="button"
                  variant="ghost"
                  size="sm"
                  aria-label="Remove line"
                  @click="removeRow(idx)">
                  Remove
                </JRButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, nextTick, onMounted, onUnmounted } from "vue";
import axios from "axios";
import Select from "primevue/select";
import {
  JRButton,
  JRSelect,
  JRInput,
  JRCheckbox,
  JRBadge,
  JRField,
  JREmptyState,
} from "@ui";

/*
  Lead / UI System note:
  Product + serialized async search needs Select `filter` emit + `loading`.
  JRSelect is multi-root and does not forward those attrs/events yet.
  Using PrimeVue Select + `jr-control` here until JRSelect gains:
  - prop: loading, filterPlaceholder, emptyFilterMessage
  - emit: filter
*/

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  lines: { type: Array, default: () => [] },
  fromWarehouseId: { type: [Number, null], default: null },
  toWarehouseId: { type: [Number, null], default: null },
  warehousesOptions: { type: Array, default: () => [] },
  unitsOptions: { type: Array, default: () => [] },
  isReadOnly: { type: Boolean, default: false },
});

const emit = defineEmits(["update:lines"]);

const PHONE_MQ = "(max-width: 767.98px)";

function readIsCompact() {
  if (typeof window === "undefined" || !window.matchMedia) return false;
  return window.matchMedia(PHONE_MQ).matches;
}

const isCompact = ref(readIsCompact());
let phoneQuery = null;
let onViewport = null;

const linesLocal = ref([]);
const selectAll = ref(false);
const productOptions = ref([]);
const loading = ref({ products: {}, serialized: {} });
const isUpdatingFromProps = ref(false);
const productFilterTimers = {};

const fromWarehouseLabel = computed(() => {
  if (!props.fromWarehouseId) return "—";
  const w = props.warehousesOptions.find(
    (x) => x.value === props.fromWarehouseId
  );
  return w?.label || "—";
});

const toWarehouseLabel = computed(() => {
  if (!props.toWarehouseId) return "—";
  const w = props.warehousesOptions.find(
    (x) => x.value === props.toWarehouseId
  );
  return w?.label || "—";
});

const hasSelection = computed(() => linesLocal.value.some((r) => r.selected));

watch(
  () => props.lines,
  (val) => {
    isUpdatingFromProps.value = true;
    const newLines = (val || []).map((x) => ({
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
    nextTick(() => {
      isUpdatingFromProps.value = false;
    });
  },
  { immediate: true, deep: true }
);

watch(
  linesLocal,
  (val) => {
    if (!isUpdatingFromProps.value) {
      nextTick(() => emit("update:lines", val));
    }
  },
  { deep: true }
);

function cryptoRandom() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function rowErrorText(err) {
  if (!err) return "";
  return Array.isArray(err) ? err[0] : String(err);
}

function optionsForProduct(row) {
  const opts = [...(productOptions.value || [])];
  if (row?.product != null) {
    const exists = opts.some((o) => o.value === row.product);
    if (!exists) {
      opts.unshift({
        value: row.product,
        label: row.product_label || `Product #${row.product}`,
        product: {
          id: row.product,
          name: row.product_label,
          tracking_mode: row.isSerialized ? "SERIALIZED" : undefined,
        },
      });
    }
  }
  return opts;
}

function onSelectAll(checked) {
  selectAll.value = !!checked;
  linesLocal.value.forEach((r) => {
    r.selected = !!checked;
  });
}

function addLine() {
  const newLine = {
    __key: cryptoRandom(),
    selected: false,
    id: null,
    product: null,
    product_label: "",
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

function removeSelected() {
  linesLocal.value = linesLocal.value.filter((r) => !r.selected);
  selectAll.value = false;
}

async function searchProducts(idx, query) {
  if (!query || query.length < 2) {
    productOptions.value = [];
    return;
  }
  loading.value.products[idx] = true;
  try {
    const { data } = await axios.get("/api/products/", {
      params: { search: query, page_size: 20, is_active: true },
    });
    const list = Array.isArray(data) ? data : data?.results || [];
    productOptions.value = list.map((p) => ({
      value: p.id,
      label:
        p.tracking_mode === "SERIALIZED"
          ? `${p.name} (${p.sku}) · SERIALIZED`
          : `${p.name} (${p.sku})`,
      product: p,
    }));
  } catch (error) {
    productOptions.value = [];
  } finally {
    loading.value.products[idx] = false;
  }
}

function onProductFilter(idx, event) {
  const query = event?.value ?? "";
  if (productFilterTimers[idx]) clearTimeout(productFilterTimers[idx]);
  productFilterTimers[idx] = setTimeout(() => {
    searchProducts(idx, query);
  }, 250);
}

function onProductShow(idx, row) {
  if (row?.product_label && (!productOptions.value || !productOptions.value.length)) {
    productOptions.value = optionsForProduct(row);
  }
}

async function searchSerialized(idx, query) {
  const r = linesLocal.value[idx];
  if (!r?.product || !props.fromWarehouseId) return;
  loading.value.serialized[idx] = true;
  try {
    const { data } = await axios.get("/api/serialized-items-provider/", {
      params: {
        page: 1,
        per_page: 30,
        search: query || "",
        product_id: r.product,
        warehouse_id: props.fromWarehouseId,
      },
    });
    const list = data?.items || [];
    r.serializedOptions = list.map((s) => ({
      value: s.id,
      label: `${s.asset_tag || s.id} (${s.product_name || ""})`,
      status: s.status,
      condition: s.condition,
    }));
  } catch (error) {
    r.serializedOptions = [];
  } finally {
    loading.value.serialized[idx] = false;
  }
}

function onSerializedFilter(idx, event) {
  const query = event?.value ?? "";
  searchSerialized(idx, query);
}

async function onProductSelected(idx, option) {
  const r = linesLocal.value[idx];
  if (!r) return;
  r.product_label = option?.product?.name || option?.label || "";
  r.isSerialized = option?.product?.tracking_mode === "SERIALIZED";
  if (r.isSerialized) {
    r.quantity = 1;
    r.serializedOptions = [];
    r.serialized_item = null;
    await searchSerialized(idx, "");
  } else {
    r.serialized_item = null;
    r.serializedOptions = [];
  }
  try {
    const { data } = await axios.get(
      `/api/products/${option.value}/default-price/`
    );
    if (data?.unit != null) r.unit = data.unit;
  } catch (_) {
    const unitId =
      option?.product?.unit_default_id ?? option?.product?.unit_default?.id;
    if (unitId != null) r.unit = unitId;
  }
}

function onProductCleared(idx) {
  const r = linesLocal.value[idx];
  if (!r) return;
  r.product_label = "";
  r.isSerialized = false;
  r.serialized_item = null;
  r.serializedOptions = [];
}

function onProductModel(idx, val) {
  const r = linesLocal.value[idx];
  if (!r) return;
  r.product = val;
  if (!val) {
    onProductCleared(idx);
    return;
  }
  const option =
    optionsForProduct(r).find((o) => o.value === val) ||
    productOptions.value.find((o) => o.value === val);
  if (option) onProductSelected(idx, option);
}

function statusSeverity(value) {
  const v = (value || "").trim();
  if (v === "Active") return "success";
  if (v === "Maintenance") return "info";
  if (v === "Lost") return "danger";
  return "secondary";
}

function conditionSeverity(value) {
  const v = (value || "").toLowerCase();
  if (v === "ok") return "success";
  if (v === "damaged" || v === "needs_repair") return "danger";
  return "secondary";
}

function conditionLabel(value) {
  const labels = {
    ok: "OK",
    damaged: "Damaged",
    needs_repair: "Needs repair",
  };
  const v = (value || "").toLowerCase().replace(/\s/g, "_");
  return labels[v] || value || "—";
}

function serializedStatus(row) {
  const opt = row.serializedOptions?.find(
    (o) => o.value === row.serialized_item
  );
  return opt?.status ?? null;
}

function serializedCondition(row) {
  const opt = row.serializedOptions?.find(
    (o) => o.value === row.serialized_item
  );
  return opt?.condition ?? null;
}

function validateLines() {
  let isValid = true;
  linesLocal.value.forEach((row) => {
    row._errors = {};
    if (!row.product) {
      row._errors.product = ["Product is required"];
      isValid = false;
    }
    if (!row.isSerialized && (row.quantity == null || row.quantity <= 0)) {
      row._errors.quantity = ["Quantity must be greater than 0"];
      isValid = false;
    }
    if (row.isSerialized && !row.serialized_item) {
      row._errors.serialized_item = ["Serialized item is required"];
      isValid = false;
    }
  });
  return isValid;
}

onMounted(() => {
  if (linesLocal.value.length === 0) addLine();
  if (typeof window !== "undefined" && window.matchMedia) {
    phoneQuery = window.matchMedia(PHONE_MQ);
    onViewport = () => {
      isCompact.value = readIsCompact();
    };
    onViewport();
    if (phoneQuery.addEventListener) {
      phoneQuery.addEventListener("change", onViewport);
    } else {
      phoneQuery.addListener(onViewport);
    }
  }
});

onUnmounted(() => {
  Object.values(productFilterTimers).forEach((t) => clearTimeout(t));
  if (onViewport && phoneQuery) {
    if (phoneQuery.removeEventListener) {
      phoneQuery.removeEventListener("change", onViewport);
    } else {
      phoneQuery.removeListener?.(onViewport);
    }
  }
});

defineExpose({ validateLines });
</script>

<style scoped>
.jr-transfer-lines {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
}

.jr-transfer-lines__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.jr-transfer-lines__toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.jr-transfer-lines__count {
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-transfer-line-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.jr-transfer-line-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 0.5rem 0.75rem;
  padding: 0.75rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface-muted);
}

.jr-transfer-line-item--error {
  border-color: var(--color-jr-danger-text);
}

.jr-transfer-line-item__main {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  min-width: 0;
}

.jr-transfer-line-item__route {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-transfer-line-item__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
}

.jr-transfer-line-item__badges,
.jr-transfer-line-item__serial-badge {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.jr-transfer-line-item__serial-badge {
  margin-top: 0.35rem;
}

.jr-transfer-table-scroll {
  max-height: 70vh;
  min-height: 16rem;
  overflow: auto;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
}

.jr-transfer-table {
  width: 100%;
  min-width: 56rem;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.jr-transfer-table th,
.jr-transfer-table td {
  padding: 0.5rem 0.65rem;
  border-bottom: 1px solid var(--color-jr-border);
  vertical-align: top;
  text-align: left;
}

.jr-transfer-table thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: var(--color-jr-surface-muted);
  font-weight: 600;
  color: var(--color-jr-muted);
  border-bottom: 2px solid var(--color-jr-border);
}

.jr-transfer-table__check {
  width: 2.5rem;
  text-align: center;
}

.jr-transfer-table__center {
  text-align: center;
  white-space: nowrap;
}

.jr-transfer-table__actions {
  width: 5.5rem;
  text-align: end;
  white-space: nowrap;
}

.jr-transfer-table__readonly {
  display: inline-block;
  padding: 0.4rem 0;
  font-size: 0.8125rem;
  color: var(--color-jr-text);
}

.jr-transfer-table__muted {
  color: var(--color-jr-muted);
}

.jr-transfer-table__serial-badge {
  margin-top: 0.35rem;
}

.jr-transfer-table__row--error {
  background: var(--color-jr-danger-subtle);
}

.jr-transfer-row-error {
  margin: 0.25rem 0 0;
  font-size: 0.75rem;
  color: var(--color-jr-danger-text);
}

.jr-transfer-req {
  color: var(--color-jr-danger-text);
}
</style>
