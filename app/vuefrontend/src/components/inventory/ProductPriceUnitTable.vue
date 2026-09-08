<template>
  <div class="jr-price-unit">
    <div v-if="!hideToolbar" class="jr-price-unit__toolbar">
      <JRButton
        variant="secondary"
        size="sm"
        :disabled="readonly"
        @click="addRowFromToolbar">
        + Add Row
      </JRButton>
    </div>

    <div v-if="isCompact" class="jr-price-unit__compact">
      <JREmptyState
        v-if="!priceUnitRows.length"
        title="No price rows"
        description="Add a row to define purchase or sale prices.">
        <JRButton
          v-if="!readonly"
          variant="secondary"
          size="sm"
          @click="addRowFromToolbar">
          + Add Row
        </JRButton>
      </JREmptyState>
      <ul v-else class="jr-price-row-list">
        <li
          v-for="(row, index) in priceUnitRows"
          :key="'m-' + index"
          class="jr-price-row-item"
          :class="{ 'jr-price-row-item--error': !!rowError(index) }">
          <div class="jr-price-row-item__main">
            <span class="jr-price-row-item__title">
              {{ priceTypeLabel(row) || "Price type" }}
              <span class="jr-price-row-item__sep" aria-hidden="true">·</span>
              {{ unitLabel(row) || "Unit" }}
            </span>
            <span class="jr-price-row-item__meta">
              <span class="jr-price-row-item__price">{{
                formatPrice(row.price)
              }}</span>
              <JRBadge
                v-if="row.is_purchase"
                value="Purchase"
                severity="info" />
              <JRBadge v-if="row.is_sale" value="Sale" severity="success" />
              <JRBadge
                v-if="row.is_default"
                value="Default"
                severity="info" />
              <JRBadge
                v-if="row.is_active === false"
                value="Inactive"
                severity="secondary" />
              <span
                v-if="dateRangeLabel(row)"
                class="jr-price-row-item__dates">
                {{ dateRangeLabel(row) }}
              </span>
            </span>
            <p v-if="rowError(index)" class="jr-price-row-error" role="alert">
              {{ rowError(index) }}
            </p>
          </div>
          <div class="jr-price-row-item__actions">
            <JRRowActions
              :compact="false"
              :entity-label="rowEntityLabel(row)"
              :actions="rowPrimaryActions(index)" />
            <JRRowActions
              v-if="!readonly"
              :compact="true"
              :entity-label="rowEntityLabel(row)"
              :actions="rowMaintenanceActions(index)" />
          </div>
        </li>
      </ul>
    </div>

    <div v-else class="jr-price-unit__table">
      <JREmptyState
        v-if="!priceUnitRows.length"
        title="No price rows"
        description="Add a row to define purchase or sale prices.">
        <JRButton
          v-if="!readonly"
          variant="secondary"
          size="sm"
          @click="addRowFromToolbar">
          + Add Row
        </JRButton>
      </JREmptyState>
      <div v-else class="jr-price-table-scroll">
        <table class="jr-price-table jr-price-table--sentence">
          <colgroup>
            <col class="jr-price-col--type" />
            <col class="jr-price-col--unit" />
            <col class="jr-price-col--price" />
            <col class="jr-price-col--flag" />
            <col class="jr-price-col--flag" />
            <col class="jr-price-col--flag" />
            <col class="jr-price-col--actions" />
          </colgroup>
          <thead>
            <tr>
              <th>Price Type</th>
              <th>Unit</th>
              <th>Price</th>
              <th class="jr-price-table__flag">Sale</th>
              <th class="jr-price-table__flag">Purchase</th>
              <th class="jr-price-table__flag">Default</th>
              <th class="jr-price-table__actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(row, index) in priceUnitRows" :key="'d-' + index">
              <tr :class="{ 'jr-price-table__row--error': !!rowError(index) }">
                <td>
                  <JRSelect
                    v-model="row.price_type"
                    :options="priceTypes"
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Select Price Type"
                    :disabled="readonly"
                    :invalid="!!rowError(index)"
                    filter
                    @show="$emit('refresh-priceTypes')" />
                </td>
                <td>
                  <JRSelect
                    v-model="row.unit"
                    :options="units"
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Select Unit"
                    :disabled="readonly"
                    :invalid="!!rowError(index)"
                    filter
                    @show="$emit('refresh-units')" />
                </td>
                <td class="jr-price-table__price">
                  <div class="jr-price-input">
                    <JRInput
                      type="number"
                      :modelValue="emptyToNull(row.price)"
                      :disabled="readonly"
                      :invalid="!!rowError(index)"
                      :min="0"
                      :minFractionDigits="0"
                      :maxFractionDigits="2"
                      placeholder="Enter price"
                      @update:modelValue="setRowPrice(row, $event)" />
                    <span v-if="unitLabel(row)" class="jr-price-suffix">{{
                      unitLabel(row)
                    }}</span>
                    <JRBadge
                      v-if="row.is_active === false"
                      value="Inactive"
                      severity="secondary" />
                  </div>
                  <p
                    v-if="dateRangeLabel(row)"
                    class="jr-price-row-dates">
                    {{ dateRangeLabel(row) }}
                  </p>
                </td>
                <td class="jr-price-table__flag">
                  <JRCheckbox
                    :modelValue="row.is_sale"
                    :disabled="readonly"
                    ariaLabel="Sale"
                    @update:modelValue="setSale(row, $event)" />
                </td>
                <td class="jr-price-table__flag">
                  <JRCheckbox
                    v-model="row.is_purchase"
                    :disabled="readonly"
                    ariaLabel="Purchase" />
                </td>
                <td class="jr-price-table__flag">
                  <JRCheckbox
                    :modelValue="!!row.is_default"
                    :disabled="readonly || !row.is_sale"
                    ariaLabel="Default sale price"
                    @update:modelValue="onRowDefault(index, $event)" />
                </td>
                <td class="jr-price-table__actions">
                  <JRRowActions
                    :compact="false"
                    :entity-label="rowEntityLabel(row)"
                    :actions="rowLineActions(index)" />
                </td>
              </tr>
              <tr v-if="rowError(index)">
                <td colspan="7" class="jr-price-row-error" role="alert">
                  {{ rowError(index) }}
                </td>
              </tr>
            </template>
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
        <p v-if="sheetError" class="jr-price-sheet__banner" role="alert">
          {{ sheetError }}
        </p>
        <JRField label="Price Type" required inputId="price-sheet-type">
          <JRSelectAddon
            inputId="price-sheet-type"
            v-model="sheetRow.price_type"
            :options="priceTypes"
            optionLabel="name"
            optionValue="id"
            placeholder="Select Price Type"
            :disabled="readonly"
            :invalid="!!sheetError"
            :showAdd="true"
            :showEdit="!!sheetRow.price_type"
            :addDisabled="readonly || !hasPermission('appinventory.add_pricetype')"
            :editDisabled="readonly || !hasPermission('appinventory.change_pricetype')"
            addLabel="Add a new price type"
            editLabel="Edit selected price type"
            filter
            @show="$emit('refresh-priceTypes')"
            @add="openModal('priceType')"
            @edit="editModal('priceType', sheetRow.price_type)" />
        </JRField>
        <JRField label="Unit" required inputId="price-sheet-unit">
          <JRSelectAddon
            inputId="price-sheet-unit"
            v-model="sheetRow.unit"
            :options="units"
            optionLabel="name"
            optionValue="id"
            placeholder="Select Unit"
            :disabled="readonly"
            :invalid="!!sheetError"
            :showAdd="true"
            :showEdit="!!sheetRow.unit"
            :addDisabled="readonly || !hasPermission('appinventory.add_unitofmeasure')"
            :editDisabled="readonly || !hasPermission('appinventory.change_unitofmeasure')"
            addLabel="Add a new unit"
            editLabel="Edit selected unit"
            filter
            @show="$emit('refresh-units')"
            @add="openModal('unit')"
            @edit="editModal('unit', sheetRow.unit)" />
        </JRField>
        <div class="jr-price-sheet__flags">
          <JRCheckbox
            v-model="sheetRow.is_purchase"
            label="Purchase"
            :disabled="readonly" />
          <JRCheckbox
            :modelValue="sheetRow.is_sale"
            label="Sale"
            :disabled="readonly"
            @update:modelValue="setSale(sheetRow, $event)" />
          <JRCheckbox
            v-model="sheetRow.is_active"
            label="Active"
            :disabled="readonly" />
        </div>
        <JRField label="Price" inputId="price-sheet-price">
          <div class="jr-price-input">
            <JRInput
              inputId="price-sheet-price"
              type="number"
              :modelValue="emptyToNull(sheetRow.price)"
              :disabled="readonly"
              :min="0"
              :minFractionDigits="0"
              :maxFractionDigits="2"
              placeholder="Enter price"
              @update:modelValue="setRowPrice(sheetRow, $event)" />
            <span v-if="unitLabel(sheetRow)" class="jr-price-suffix">{{
              unitLabel(sheetRow)
            }}</span>
          </div>
        </JRField>
        <JRField label="Default sale price">
          <JRCheckbox
            :modelValue="!!sheetRow.is_default"
            label="Use as default sale price"
            :disabled="readonly || !sheetRow.is_sale"
            @update:modelValue="onDefaultCheck($event)" />
        </JRField>
        <JRField label="Valid From" inputId="price-sheet-from">
          <JRDatePicker
            inputId="price-sheet-from"
            :modelValue="isoToDate(sheetRow.valid_from)"
            :disabled="readonly"
            placeholder="Start date"
            @update:modelValue="setRowDate(sheetRow, 'valid_from', $event)" />
        </JRField>
        <JRField label="Valid Until" inputId="price-sheet-until">
          <JRDatePicker
            inputId="price-sheet-until"
            :modelValue="isoToDate(sheetRow.valid_until)"
            :disabled="readonly"
            placeholder="End date"
            @update:modelValue="setRowDate(sheetRow, 'valid_until', $event)" />
        </JRField>
      </div>
      <template #footer>
        <div class="jr-price-sheet__footer">
          <JRButton variant="primary" @click="closeSheet">Done</JRButton>
          <JRRowActions
            v-if="!readonly && sheetIndex != null"
            :compact="false"
            :solid="true"
            :entity-label="rowEntityLabel(sheetRow)"
            :actions="rowMaintenanceActions(sheetIndex)" />
        </div>
      </template>
    </JRDrawer>

    <JRDialog
      :visible="deleteDialogVisible"
      header="Delete price row"
      message="Delete this price row?"
      confirmLabel="Delete"
      confirmVariant="danger"
      @update:visible="onDeleteVisible"
      @confirm="confirmPendingDelete" />
  </div>
</template>

<script>
import EyeIcon from "@primevue/icons/eye";
import PencilIcon from "@primevue/icons/pencil";
import TrashIcon from "@primevue/icons/trash";
import {
  JRButton,
  JRSelect,
  JRSelectAddon,
  JRCheckbox,
  JRInput,
  JRDatePicker,
  JRDrawer,
  JRField,
  JRBadge,
  JREmptyState,
  JRDialog,
  JRRowActions,
} from "@ui";
import CopyIcon from "@/ui/CopyIcon.vue";

const PHONE_MQ = "(max-width: 767.98px)";
const TABLET_MQ = "(min-width: 768px) and (max-width: 1023.98px)";

export default {
  name: "ProductPriceUnitTable",
  components: {
    JRButton,
    JRSelect,
    JRSelectAddon,
    JRCheckbox,
    JRInput,
    JRDatePicker,
    JRDrawer,
    JRField,
    JRBadge,
    JREmptyState,
    JRDialog,
    JRRowActions,
  },
  props: {
    modelValue: { type: Array, required: true },
    priceTypes: { type: Array, default: () => [] },
    units: { type: Array, default: () => [] },
    readonly: { type: Boolean, default: false },
    hideToolbar: { type: Boolean, default: false },
    rowErrors: { type: Array, default: () => [] },
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
      isPhone: false,
      isTablet: false,
      sheetOpen: false,
      sheetIndex: null,
      deleteDialogVisible: false,
      pendingDeleteIndex: null,
      deleteResolved: false,
    };
  },

  computed: {
    isCompact() {
      return this.isPhone || this.isTablet;
    },
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
    sheetError() {
      return this.rowError(this.sheetIndex);
    },
  },

  created() {
    this.syncViewport();
  },

  mounted() {
    if (typeof window === "undefined" || !window.matchMedia) return;
    this._phoneMq = window.matchMedia(PHONE_MQ);
    this._tabletMq = window.matchMedia(TABLET_MQ);
    this._onMedia = () => {
      this.syncViewport();
    };
    [this._phoneMq, this._tabletMq].forEach((mq) => {
      if (mq.addEventListener) mq.addEventListener("change", this._onMedia);
      else mq.addListener(this._onMedia);
    });
  },

  beforeUnmount() {
    [this._phoneMq, this._tabletMq].forEach((mq) => {
      if (!mq || !this._onMedia) return;
      if (mq.removeEventListener) mq.removeEventListener("change", this._onMedia);
      else mq.removeListener(this._onMedia);
    });
  },

  methods: {
    syncViewport() {
      if (typeof window === "undefined" || !window.matchMedia) {
        this.isPhone = false;
        this.isTablet = false;
        return;
      }
      this.isPhone = window.matchMedia(PHONE_MQ).matches;
      this.isTablet = window.matchMedia(TABLET_MQ).matches;
    },
    rowError(index) {
      if (index == null) return "";
      return this.rowErrors[index] || "";
    },
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

    rowEntityLabel(row) {
      const type = this.priceTypeLabel(row) || "Price type";
      const unit = this.unitLabel(row) || "unit";
      return `${type} · ${unit}`;
    },
    rowPrimaryActions(index) {
      const viewing = this.readonly;
      return [
        {
          key: viewing ? "view" : "edit",
          label: viewing ? "View" : "Edit",
          severity: viewing ? "success" : "primary",
          icon: viewing ? EyeIcon : PencilIcon,
          command: () => this.openSheet(index),
        },
      ];
    },
    rowLineActions(index) {
      const actions = [...this.rowPrimaryActions(index)];
      if (!this.readonly) {
        actions.push(...this.rowMaintenanceActions(index));
      }
      return actions;
    },
    rowMaintenanceActions(index) {
      return [
        {
          key: "duplicate",
          label: "Duplicate",
          severity: "secondary",
          icon: CopyIcon,
          command: () => this.duplicateRow(index),
        },
        {
          key: "delete",
          label: "Delete",
          severity: "danger",
          icon: TrashIcon,
          command: () => this.requestDelete(index),
        },
      ];
    },
    duplicateRow(index) {
      const source = this.priceUnitRows[index];
      if (!source || this.readonly) return;
      const copy = {
        id: null,
        price_type: source.price_type,
        unit: source.unit,
        is_purchase: !!source.is_purchase,
        is_sale: !!source.is_sale,
        price: source.price,
        is_default: false,
        valid_from: source.valid_from || "",
        valid_until: source.valid_until || "",
        is_active: source.is_active !== false,
      };
      this.priceUnitRows.splice(index + 1, 0, copy);
    },
    removeRowAt(index) {
      this.priceUnitRows.splice(index, 1);
      if (this.sheetIndex === index) this.closeSheet();
      else if (this.sheetIndex != null && this.sheetIndex > index) {
        this.sheetIndex -= 1;
      }
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
      this.priceUnitRows.push(row);
    },
    rowNeedsDeleteConfirm(row) {
      if (!row) return false;
      return !!(row.id || row.price || row.price_type || row.unit);
    },
    requestDelete(index) {
      const row = this.priceUnitRows[index];
      if (!this.rowNeedsDeleteConfirm(row)) {
        this.removeRowAt(index);
        return;
      }
      this.pendingDeleteIndex = index;
      this.deleteResolved = false;
      this.deleteDialogVisible = true;
    },
    confirmPendingDelete() {
      const index = this.pendingDeleteIndex;
      this.deleteResolved = true;
      this.pendingDeleteIndex = null;
      this.deleteDialogVisible = false;
      if (index == null) return;
      this.removeRowAt(index);
    },
    onDeleteVisible(visible) {
      this.deleteDialogVisible = visible;
      if (visible) return;
      if (this.deleteResolved) {
        this.deleteResolved = false;
        return;
      }
      this.pendingDeleteIndex = null;
    },
    removeRow(index) {
      this.requestDelete(index);
    },
    setDefault(index) {
      this.priceUnitRows.forEach((row, i) => {
        row.is_default = i === index;
      });
    },
    onDefaultCheck(value) {
      if (this.sheetIndex == null) return;
      this.onRowDefault(this.sheetIndex, value);
    },
    onRowDefault(index, value) {
      if (index == null) return;
      if (value) this.setDefault(index);
      else if (this.priceUnitRows[index]) {
        this.priceUnitRows[index].is_default = false;
      }
    },
    setSale(row, value) {
      row.is_sale = !!value;
      if (!row.is_sale && row.is_default) row.is_default = false;
    },
    openModal(type) {
      if (this.readonly) return;
      const fromSheet = this.sheetOpen;
      const sheetIndex = this.sheetIndex;
      if (fromSheet) this.closeSheet();
      this.$emit("open-modal", { type, fromSheet, sheetIndex });
    },
    editModal(type, id) {
      if (this.readonly || !id) return;
      const fromSheet = this.sheetOpen;
      const sheetIndex = this.sheetIndex;
      if (fromSheet) this.closeSheet();
      this.$emit("edit-modal", { type, id, fromSheet, sheetIndex });
    },

    addRowFromToolbar() {
      this.addRow();
      if (this.isCompact && !this.readonly) {
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
    labelById(list, id) {
      const nid = typeof id === "object" ? id?.id : id;
      if (nid === null || nid === undefined || nid === "") return "";
      const found = (list || []).find(
        (item) => String(item.id) === String(nid)
      );
      return found ? found.name : "";
    },
    formatShortDate(value) {
      const date = this.isoToDate(value);
      if (!date) return "";
      return date.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    },
    dateRangeLabel(row) {
      if (!row) return "";
      const from = this.formatShortDate(row.valid_from);
      const until = this.formatShortDate(row.valid_until);
      if (!from && !until) return "";
      if (from && until) return `${from} – ${until}`;
      if (from) return `From ${from}`;
      return `Until ${until}`;
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

.jr-price-row-item--error {
  border-color: var(--color-jr-danger);
}

.jr-price-row-item__main {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
}

.jr-price-row-item__title {
  font-size: 0.9375rem;
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
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
}

.jr-price-row-item__dates,
.jr-price-row-dates {
  margin: 0.3rem 0 0;
  font-size: 0.75rem;
  line-height: 1.3;
  color: var(--color-jr-muted, #4b5563);
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
  table-layout: fixed;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.jr-price-table--sentence {
  min-width: 50rem;
}

.jr-price-col--type {
  width: 18%;
}

.jr-price-col--unit {
  width: 16%;
}

.jr-price-col--price {
  width: 18%;
}

.jr-price-col--flag {
  width: 8%;
}

.jr-price-col--actions {
  width: 26%;
}

.jr-price-th {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.jr-price-table th,
.jr-price-table td {
  padding: 0.55rem 0.6rem;
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
  min-width: 0;
}

.jr-price-input {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.jr-price-suffix {
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
  white-space: nowrap;
}

.jr-price-table th.jr-price-table__actions,
.jr-price-table td.jr-price-table__actions {
  text-align: center;
  white-space: nowrap;
}

.jr-price-table td.jr-price-table__actions :deep(.jr-row-actions) {
  justify-content: center;
  width: 100%;
}

.jr-price-row-item__actions {
  display: flex;
  align-items: center;
  gap: 0.15rem;
  flex-shrink: 0;
}

.jr-price-table :deep(.p-select.jr-control) {
  min-width: 0;
  width: 100%;
}

.jr-price-table :deep(.p-inputnumber) {
  width: 6.25rem;
  max-width: 7rem;
  min-width: 5.25rem;
  flex: 0 0 auto;
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
  width: 1.25rem;
  height: 1.25rem;
  accent-color: var(--color-jr-primary, #2563eb);
}

.jr-price-default-hit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 2.75rem;
  min-height: 2.75rem;
  margin: 0;
}

.jr-price-default-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 2.75rem;
  font-size: 0.9375rem;
  font-weight: 600;
}

.jr-price-row-error,
.jr-price-sheet__banner {
  margin: 0;
  padding: 0.35rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
  background: var(--color-jr-danger-subtle);
}

.jr-price-sheet {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.jr-price-sheet__flags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1.5rem;
}

.jr-price-sheet__flags :deep(.jr-checkbox),
.jr-price-sheet :deep(.jr-checkbox) {
  column-gap: 0.85rem;
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

@media (max-width: 1023.98px) {
  .p-drawer.jr-price-row-drawer {
    width: 100vw;
    max-width: 100vw;
  }
}
</style>
