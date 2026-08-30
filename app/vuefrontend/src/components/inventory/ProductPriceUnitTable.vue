<template>
  <div class="jr-price-unit">
    <div class="jr-price-unit__toolbar">
      <JRButton
        variant="secondary"
        size="sm"
        :disabled="readonly"
        v-tt
        data-title="Add a new price row"
        @click="addRowFromToolbar">
        + Add Row
      </JRButton>
    </div>

    <!-- Mobile: compact row list + sheet (not a 10-col input grid) -->
    <div v-if="isMobile" class="jr-price-unit__mobile">
      <JREmptyState
        v-if="!priceUnitRows.length"
        title="No price rows"
        description="Add a row to define purchase or sale prices." />
      <ul v-else class="jr-price-row-list">
        <li
          v-for="(row, index) in priceUnitRows"
          :key="'m-' + index"
          class="jr-price-row-item">
          <button
            type="button"
            class="jr-price-row-item__main"
            @click="openSheet(index)">
            <span class="jr-price-row-item__title">
              {{ priceTypeLabel(row) || "Price type" }}
              <span class="jr-price-row-item__sep" aria-hidden="true">·</span>
              {{ unitLabel(row) || "Unit" }}
            </span>
            <span class="jr-price-row-item__meta">
              <span class="jr-price-row-item__price">{{
                formatPrice(row.price)
              }}</span>
              <JRBadge v-if="row.is_purchase" value="Purchase" />
              <JRBadge v-if="row.is_sale" value="Sale" />
              <JRBadge
                v-if="row.is_default"
                value="Default"
                severity="info" />
              <JRBadge
                :value="row.is_active !== false ? 'Active' : 'Inactive'"
                :severity="row.is_active !== false ? 'success' : 'secondary'" />
            </span>
          </button>
          <JRButton
            variant="danger"
            size="sm"
            :disabled="readonly"
            aria-label="Remove this row"
            v-tt
            data-title="Remove this row (changes apply after Save)."
            @click="removeRow(index)">
            Delete
          </JRButton>
        </li>
      </ul>
    </div>

    <!-- Desktop: dense editable table -->
    <div v-else class="jr-price-unit__desktop">
      <div class="jr-price-table-scroll">
        <table class="jr-price-table">
          <thead>
            <tr>
              <th>Price Type</th>
              <th>Unit</th>
              <th class="jr-price-table__flag">Purchase</th>
              <th class="jr-price-table__flag">Sale</th>
              <th>Price</th>
              <th class="jr-price-table__flag">Default</th>
              <th>Valid From</th>
              <th>Valid Until</th>
              <th class="jr-price-table__flag">Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in priceUnitRows" :key="'d-' + index">
              <td>
                <JRSelectAddon
                  v-model="row.price_type"
                  :options="priceTypes"
                  optionLabel="name"
                  optionValue="id"
                  placeholder="Select Price Type"
                  :disabled="readonly"
                  :showAdd="true"
                  :showEdit="!!row.price_type"
                  addLabel="Add a new price type"
                  editLabel="Edit selected price type"
                  filter
                  v-tt
                  data-title="Required. Choose the price policy (e.g., Contractors, Wholesale, Counter)."
                  @show="$emit('refresh-priceTypes')"
                  @add="openModal('priceType')"
                  @edit="editModal('priceType', row.price_type)" />
              </td>
              <td>
                <JRSelectAddon
                  v-model="row.unit"
                  :options="units"
                  optionLabel="name"
                  optionValue="id"
                  placeholder="Select Unit"
                  :disabled="readonly"
                  :showAdd="true"
                  :showEdit="!!row.unit"
                  addLabel="Add a new unit"
                  editLabel="Edit selected unit"
                  filter
                  v-tt
                  data-title="Required. Unit of measure for this price (e.g., EA, Box, Pair)."
                  @show="$emit('refresh-units')"
                  @add="openModal('unit')"
                  @edit="editModal('unit', row.unit)" />
              </td>
              <td class="jr-price-table__flag">
                <JRCheckbox
                  v-model="row.is_purchase"
                  :disabled="readonly"
                  ariaLabel="Purchase"
                  v-tt
                  data-title="Check if this price applies to purchasing costs." />
              </td>
              <td class="jr-price-table__flag">
                <JRCheckbox
                  v-model="row.is_sale"
                  :disabled="readonly"
                  ariaLabel="Sale"
                  v-tt
                  data-title="Check if this price is used for sales." />
              </td>
              <td class="jr-price-table__price">
                <JRInput
                  type="number"
                  :modelValue="emptyToNull(row.price)"
                  :disabled="readonly"
                  :min="0"
                  :minFractionDigits="0"
                  :maxFractionDigits="2"
                  placeholder="Enter price"
                  v-tt
                  data-title="Numeric amount (non‑negative)."
                  @update:modelValue="setRowPrice(row, $event)" />
              </td>
              <td class="jr-price-table__flag">
                <input
                  type="radio"
                  class="jr-price-default"
                  name="jr-price-default-desktop"
                  aria-label="Default price row"
                  :checked="row.is_default"
                  :disabled="readonly || row.is_purchase"
                  v-tt
                  :data-title="
                    row.is_purchase
                      ? 'Default price is not available for purchase prices. Only sale prices can be marked as default.'
                      : 'Marks the primary price row. One default is recommended.'
                  "
                  @change="setDefault(index)" />
              </td>
              <td>
                <JRDatePicker
                  :modelValue="isoToDate(row.valid_from)"
                  :disabled="readonly"
                  placeholder="Start date"
                  v-tt
                  data-title="Start date of price validity (optional)."
                  @update:modelValue="setRowDate(row, 'valid_from', $event)" />
              </td>
              <td>
                <JRDatePicker
                  :modelValue="isoToDate(row.valid_until)"
                  :disabled="readonly"
                  placeholder="End date"
                  v-tt
                  data-title="End date of price validity (optional)."
                  @update:modelValue="setRowDate(row, 'valid_until', $event)" />
              </td>
              <td class="jr-price-table__flag">
                <JRCheckbox
                  v-model="row.is_active"
                  :disabled="readonly"
                  ariaLabel="Active"
                  v-tt
                  data-title="Enable/disable this price row." />
              </td>
              <td class="jr-price-table__flag">
                <JRButton
                  variant="danger"
                  size="sm"
                  :disabled="readonly"
                  aria-label="Remove this row"
                  v-tt
                  data-title="Remove this row (changes apply after Save)."
                  @click="removeRow(index)">
                  Delete
                </JRButton>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <JRDrawer
      class="jr-price-row-drawer"
      :visible="sheetOpen"
      :header="readonly ? 'Price row' : 'Edit price row'"
      position="right"
      @update:visible="onSheetVisible">
      <div v-if="sheetRow" class="jr-price-sheet">
        <JRField label="Price Type" required>
          <JRSelectAddon
            v-model="sheetRow.price_type"
            :options="priceTypes"
            optionLabel="name"
            optionValue="id"
            placeholder="Select Price Type"
            :disabled="readonly"
            :showAdd="true"
            :showEdit="!!sheetRow.price_type"
            addLabel="Add a new price type"
            editLabel="Edit selected price type"
            filter
            v-tt
            data-title="Required. Choose the price policy (e.g., Contractors, Wholesale, Counter)."
            @show="$emit('refresh-priceTypes')"
            @add="openModal('priceType')"
            @edit="editModal('priceType', sheetRow.price_type)" />
        </JRField>
        <JRField label="Unit" required>
          <JRSelectAddon
            v-model="sheetRow.unit"
            :options="units"
            optionLabel="name"
            optionValue="id"
            placeholder="Select Unit"
            :disabled="readonly"
            :showAdd="true"
            :showEdit="!!sheetRow.unit"
            addLabel="Add a new unit"
            editLabel="Edit selected unit"
            filter
            v-tt
            data-title="Required. Unit of measure for this price (e.g., EA, Box, Pair)."
            @show="$emit('refresh-units')"
            @add="openModal('unit')"
            @edit="editModal('unit', sheetRow.unit)" />
        </JRField>
        <div class="jr-price-sheet__flags">
          <JRCheckbox
            v-model="sheetRow.is_purchase"
            label="Purchase"
            :disabled="readonly"
            v-tt
            data-title="Check if this price applies to purchasing costs." />
          <JRCheckbox
            v-model="sheetRow.is_sale"
            label="Sale"
            :disabled="readonly"
            v-tt
            data-title="Check if this price is used for sales." />
          <JRCheckbox
            v-model="sheetRow.is_active"
            label="Active"
            :disabled="readonly"
            v-tt
            data-title="Enable/disable this price row." />
        </div>
        <JRField label="Price">
          <JRInput
            type="number"
            :modelValue="emptyToNull(sheetRow.price)"
            :disabled="readonly"
            :min="0"
            :minFractionDigits="0"
            :maxFractionDigits="2"
            placeholder="Enter price"
            v-tt
            data-title="Numeric amount (non‑negative)."
            @update:modelValue="setRowPrice(sheetRow, $event)" />
        </JRField>
        <JRField label="Default">
          <label class="jr-price-default-label">
            <input
              type="radio"
              class="jr-price-default"
              name="jr-price-default-sheet"
              :checked="sheetRow.is_default"
              :disabled="readonly || sheetRow.is_purchase"
              v-tt
              :data-title="
                sheetRow.is_purchase
                  ? 'Default price is not available for purchase prices. Only sale prices can be marked as default.'
                  : 'Marks the primary price row. One default is recommended.'
              "
              @change="setDefault(sheetIndex)" />
            <span>Use as default sale price</span>
          </label>
        </JRField>
        <JRField label="Valid From">
          <JRDatePicker
            :modelValue="isoToDate(sheetRow.valid_from)"
            :disabled="readonly"
            placeholder="Start date"
            v-tt
            data-title="Start date of price validity (optional)."
            @update:modelValue="setRowDate(sheetRow, 'valid_from', $event)" />
        </JRField>
        <JRField label="Valid Until">
          <JRDatePicker
            :modelValue="isoToDate(sheetRow.valid_until)"
            :disabled="readonly"
            placeholder="End date"
            v-tt
            data-title="End date of price validity (optional)."
            @update:modelValue="setRowDate(sheetRow, 'valid_until', $event)" />
        </JRField>
      </div>
      <template #footer>
        <div class="jr-price-sheet__footer">
          <JRButton variant="primary" @click="closeSheet">Done</JRButton>
          <JRButton
            variant="danger"
            :disabled="readonly || sheetIndex == null"
            v-tt
            data-title="Remove this row (changes apply after Save)."
            @click="removeSheetRow">
            Delete
          </JRButton>
        </div>
      </template>
    </JRDrawer>
  </div>
</template>

<script>
import {
  JRButton,
  JRSelectAddon,
  JRCheckbox,
  JRInput,
  JRDatePicker,
  JRDrawer,
  JRField,
  JRBadge,
  JREmptyState,
} from "@ui";

const MOBILE_MQ = "(max-width: 767.98px)";

export default {
  name: "ProductPriceUnitTable",
  components: {
    JRButton,
    JRSelectAddon,
    JRCheckbox,
    JRInput,
    JRDatePicker,
    JRDrawer,
    JRField,
    JRBadge,
    JREmptyState,
  },
  props: {
    modelValue: { type: Array, required: true },
    priceTypes: { type: Array, default: () => [] },
    units: { type: Array, default: () => [] },
    readonly: { type: Boolean, default: false },
  },
  emits: [
    "update:modelValue",
    "open-modal",
    "edit-modal",
    "refresh-priceTypes",
    "refresh-units",
  ],

  data() {
    return {
      isMobile: false,
      sheetOpen: false,
      sheetIndex: null,
    };
  },

  computed: {
    priceUnitRows: {
      get() {
        return this.modelValue;
      },
      set(newVal) {
        this.$emit("update:modelValue", newVal);
      },
    },
    sheetRow() {
      if (this.sheetIndex == null) return null;
      return this.priceUnitRows[this.sheetIndex] || null;
    },
  },

  watch: {
    // ensure at least one row when parent hasn't provided any yet (create mode)
    modelValue: {
      handler(val) {
        if (!this.readonly && (!val || val.length === 0)) {
          this.addRow();
        }
      },
      immediate: true,
      deep: false,
    },
  },

  created() {
    if (typeof window !== "undefined" && window.matchMedia) {
      this.isMobile = window.matchMedia(MOBILE_MQ).matches;
    }
  },

  mounted() {
    if (typeof window !== "undefined" && window.matchMedia) {
      this._mediaQuery = window.matchMedia(MOBILE_MQ);
      this.isMobile = this._mediaQuery.matches;
      this._onMedia = (event) => {
        this.isMobile = event.matches;
        if (!event.matches) this.closeSheet();
      };
      if (this._mediaQuery.addEventListener) {
        this._mediaQuery.addEventListener("change", this._onMedia);
      } else {
        this._mediaQuery.addListener(this._onMedia);
      }
    }
  },

  beforeUnmount() {
    if (this._mediaQuery && this._onMedia) {
      if (this._mediaQuery.removeEventListener) {
        this._mediaQuery.removeEventListener("change", this._onMedia);
      } else {
        this._mediaQuery.removeListener(this._onMedia);
      }
    }
  },

  methods: {
    /**
     * Rows must use real booleans for API/DB (not null/undefined/other).
     * @returns {string[]} English messages; empty when valid.
     */
    validateStrictPurchaseSaleFlags() {
      const errors = [];
      this.priceUnitRows.forEach((row, idx) => {
        const ip = row.is_purchase;
        const is = row.is_sale;
        const purchaseOk = ip === true || ip === false;
        const saleOk = is === true || is === false;
        if (!purchaseOk || !saleOk) {
          errors.push(
            `Row ${
              idx + 1
            }: Purchase and Sale must each be explicitly on or off (true or false). Clear or reload the row if values are missing or invalid.`
          );
        }
      });
      return errors;
    },

    addRow(prefill = null) {
      const row = Object.assign(
        {
          id: null,
          price_type: "",
          unit: "",
          is_purchase: false,
          is_sale: false,
          price: "",
          is_default: false,
          valid_from: "",
          valid_until: "",
          is_active: true,
        },
        prefill || {}
      );
      // push directly is fine here because parent passes an array reference via v-model
      this.priceUnitRows.push(row);
    },
    removeRow(index) {
      this.priceUnitRows.splice(index, 1);
    },
    setDefault(index) {
      this.priceUnitRows.forEach((row, i) => {
        row.is_default = i === index;
      });
    },
    openModal(type) {
      this.$emit("open-modal", type);
    },
    editModal(type, id) {
      if (id) this.$emit("edit-modal", { type, id });
    },

    addRowFromToolbar() {
      this.addRow();
      if (this.isMobile && !this.readonly) {
        this.openSheet(this.priceUnitRows.length - 1);
      }
    },
    openSheet(index) {
      this.sheetIndex = index;
      this.sheetOpen = true;
    },
    closeSheet() {
      this.sheetOpen = false;
      this.sheetIndex = null;
    },
    onSheetVisible(visible) {
      this.sheetOpen = visible;
      if (!visible) this.sheetIndex = null;
    },
    removeSheetRow() {
      if (this.sheetIndex == null) return;
      this.removeRow(this.sheetIndex);
      this.closeSheet();
    },
    labelById(list, id) {
      const nid = typeof id === "object" ? id?.id : id;
      if (nid === null || nid === undefined || nid === "") return "";
      const found = (list || []).find((item) => item.id === nid);
      return found ? found.name : "";
    },
    priceTypeLabel(row) {
      return this.labelById(this.priceTypes, row.price_type);
    },
    unitLabel(row) {
      return this.labelById(this.units, row.unit);
    },
    formatPrice(price) {
      if (price === null || price === undefined || price === "") return "—";
      const num = Number(price);
      if (Number.isNaN(num)) return "—";
      return num.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    },
    emptyToNull(value) {
      return value === "" || value === undefined ? null : value;
    },
    setRowPrice(row, value) {
      row.price = value === null || value === undefined ? "" : value;
    },
    isoToDate(value) {
      if (!value) return null;
      if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value;
      const text = String(value).slice(0, 10);
      const parts = text.split("-").map(Number);
      if (parts.length !== 3 || parts.some((n) => Number.isNaN(n))) return null;
      const [year, month, day] = parts;
      const date = new Date(year, month - 1, day);
      return Number.isNaN(date.getTime()) ? null : date;
    },
    dateToIso(value) {
      if (!value) return "";
      if (typeof value === "string") return value.slice(0, 10);
      if (!(value instanceof Date) || Number.isNaN(value.getTime())) return "";
      const year = value.getFullYear();
      const month = String(value.getMonth() + 1).padStart(2, "0");
      const day = String(value.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    },
    setRowDate(row, field, value) {
      row[field] = this.dateToIso(value);
    },
  },
};
</script>

<style scoped>
.jr-price-unit__toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.jr-price-row-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.jr-price-row-item {
  display: flex;
  align-items: stretch;
  gap: 0.5rem;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  background: var(--color-jr-surface, #ffffff);
}

.jr-price-row-item__main {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
  padding: 0;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
  color: inherit;
}

.jr-price-row-item__main:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 2px;
}

.jr-price-row-item__title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
}

.jr-price-row-item__sep {
  font-weight: 400;
  color: var(--color-jr-muted, #4b5563);
}

.jr-price-row-item__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.5rem;
}

.jr-price-row-item__price {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
}

.jr-price-table-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  background: var(--color-jr-surface, #ffffff);
}

.jr-price-table {
  width: 100%;
  min-width: 56rem;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.jr-price-table th,
.jr-price-table td {
  padding: 0.5rem 0.45rem;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
  vertical-align: middle;
  text-align: left;
}

.jr-price-table th {
  font-weight: 600;
  background: var(--color-jr-surface-muted, #f9fafb);
  white-space: nowrap;
}

.jr-price-table__flag {
  text-align: center;
  width: 1%;
  white-space: nowrap;
}

.jr-price-table__price {
  min-width: 6.5rem;
}

.jr-price-table :deep(.jr-select-addon) {
  min-width: 14rem;
}

.jr-price-table :deep(.p-inputtext),
.jr-price-table :deep(.p-select),
.jr-price-table :deep(.p-datepicker),
.jr-price-table :deep(.p-inputnumber),
.jr-price-table :deep(.p-inputnumber-input),
.jr-price-table :deep(.p-button:not(.p-button-sm)) {
  min-height: 2.25rem;
}

.jr-price-default {
  width: 1rem;
  height: 1rem;
  accent-color: var(--color-jr-primary, #2563eb);
}

.jr-price-default-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 2.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
}

.jr-price-sheet {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.jr-price-sheet__flags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1rem;
}

.jr-price-sheet__footer {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
</style>

<style>
.p-drawer.jr-price-row-drawer {
  width: min(28rem, 100vw);
}

@media (max-width: 767.98px) {
  .p-drawer.jr-price-row-drawer {
    width: 100vw;
    max-width: 100vw;
  }
}
</style>
