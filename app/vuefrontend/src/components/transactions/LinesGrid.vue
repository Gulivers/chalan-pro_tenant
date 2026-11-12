<template>
  <div class="jr-lines">
    <div v-if="!hideToolbar" class="jr-lines__toolbar">
      <div class="jr-lines__toolbar-actions">
        <Button
          type="button"
          class="jr-button jr-lines__maint"
          severity="primary"
          outlined
          size="small"
          :disabled="disabled"
          :title="$t('transactions.lines.addRowTitle')"
          @click="addLineFromToolbar">
          <Plus class="jr-lines__maint-icon" aria-hidden="true" />
          <span class="p-button-label">{{ $t('transactions.lines.addRow') }}</span>
        </Button>
        <Button
          type="button"
          class="jr-button jr-lines__maint"
          severity="info"
          outlined
          size="small"
          :disabled="disabled || !hasSelection"
          :title="$t('transactions.lines.duplicateSelectedTitle')"
          @click="duplicateSelected">
          <Copy class="jr-lines__maint-icon" aria-hidden="true" />
          <span class="p-button-label">{{ $t('transactions.lines.duplicateSelected') }}</span>
        </Button>
        <Button
          type="button"
          class="jr-button jr-lines__maint"
          severity="danger"
          outlined
          size="small"
          :disabled="disabled || !hasSelection"
          :title="$t('transactions.lines.deleteSelectedTitle')"
          @click="removeSelected">
          <Trash class="jr-lines__maint-icon" aria-hidden="true" />
          <span class="p-button-label">{{ $t('transactions.lines.deleteSelected') }}</span>
        </Button>
        <JRButton
          v-if="documentId && documentTypeCreatesSerializedItems"
          type="button"
          variant="secondary"
          size="sm"
          :disabled="disabled"
          :title="$t('transactions.lines.assignSerialTitle')"
          @click="$emit('open-asset-tags')">
          {{ $t('transactions.lines.assignSerialNumbers') }}
        </JRButton>
      </div>
      <span class="jr-lines__count">{{
        $t('transactions.lines.rowsCount', { count: linesLocal?.length || 0 })
      }}</span>
    </div>

    <div v-if="isCompact" class="jr-lines__compact">
      <JREmptyState
        v-if="!linesLocal.length"
        :title="$t('transactions.lines.noLinesTitle')"
        :description="$t('transactions.lines.noLinesDesc')">
        <Button
          v-if="!disabled && !hideToolbar"
          type="button"
          class="jr-button"
          severity="primary"
          outlined
          size="small"
          @click="addLineFromToolbar">
          <Plus class="jr-lines__maint-icon" aria-hidden="true" />
          <span class="p-button-label">{{ $t('transactions.lines.addRow') }}</span>
        </Button>
      </JREmptyState>
      <ul v-else class="jr-lines-list">
        <li
          v-for="(row, idx) in linesLocal"
          :key="row.__key"
          class="jr-lines-item"
          :class="{ 'jr-lines-item--error': rowHasErrors(row) }">
          <div class="jr-lines-item__main">
            <div class="jr-lines-product-cell">
              <button
                type="button"
                class="jr-lines-product-cell__thumb"
                :disabled="!row.product"
                :aria-label="
                  row.product
                    ? `View images of ${row.product_label || 'product'}`
                    : 'No product selected'
                "
                @click="openImageGallery(row)">
                <img
                  v-if="lineImageSrc(row)"
                  :src="lineImageSrc(row)"
                  alt=""
                  class="jr-lines-product-cell__img"
                  width="40"
                  height="40"
                  loading="lazy"
                  decoding="async"
                  @error="onLineImageError(row)" />
                <span v-else class="jr-lines-product-cell__ph" aria-hidden="true" />
              </button>
              <span class="jr-lines-item__title">
                {{
                  row.product_label ||
                  (row.product ? `Product #${row.product}` : "Product")
                }}
              </span>
            </div>
            <span class="jr-lines-item__meta">
              <span>{{ row.quantity ?? 0 }} {{ unitLabel(row) }}</span>
              <span class="jr-lines-item__sep" aria-hidden="true">·</span>
              <span class="jr-lines-item__total">
                {{ currency(lineTotalAfterDiscount(row)) }}
              </span>
              <JRBadge
                v-if="isSerializedRow(row)"
                value="SERIALIZED"
                severity="info" />
            </span>
            <p
              v-if="
                rowErrorText(row._errors?.product) ||
                rowErrorText(row._errors?.quantity)
              "
              class="jr-lines-item__error"
              role="alert">
              {{
                rowErrorText(row._errors?.product) ||
                rowErrorText(row._errors?.quantity)
              }}
            </p>
          </div>
          <div class="jr-lines-item__actions">
            <JRCheckbox
              v-if="!disabled"
              class="jr-lines-item__check"
              :modelValue="!!row.selected"
              :inputId="`line-select-m-${row.__key}`"
              ariaLabel="Select line"
              :disabled="disabled"
              @update:modelValue="(v) => (row.selected = !!v)" />
            <JRRowActions
              :compact="false"
              :entity-label="lineEntityLabel(row)"
              :actions="rowPrimaryActions(idx)" />
            <JRRowActions
              v-if="!disabled"
              :compact="true"
              :entity-label="lineEntityLabel(row)"
              :actions="rowMaintenanceActions(idx)" />
          </div>
        </li>
      </ul>
    </div>

    <div v-else class="jr-lines__table-wrap">
      <JREmptyState
        v-if="!linesLocal.length"
        :title="$t('transactions.lines.noLinesTitle')"
        :description="$t('transactions.lines.noLinesDesc')">
        <Button
          v-if="!disabled && !hideToolbar"
          type="button"
          class="jr-button"
          severity="primary"
          outlined
          size="small"
          @click="addLineFromToolbar">
          <Plus class="jr-lines__maint-icon" aria-hidden="true" />
          <span class="p-button-label">{{ $t('transactions.lines.addRow') }}</span>
        </Button>
      </JREmptyState>
      <div v-else class="jr-lines-table-scroll">
        <table class="jr-lines-table">
          <thead>
            <tr>
              <th v-if="!disabled" class="jr-lines-table__check">
                <JRCheckbox
                  :modelValue="selectAll"
                  inputId="lines-select-all"
                  ariaLabel="Select all lines"
                  :disabled="disabled || !linesLocal.length"
                  @update:modelValue="onSelectAll" />
              </th>
              <th class="jr-lines-table__thumb">{{ $t('transactions.lines.colImg') }}</th>
              <th class="jr-lines-table__product">{{ $t('transactions.lines.colProduct') }}</th>
              <th class="jr-lines-table__qty">{{ $t('transactions.lines.colQty') }}</th>
              <th class="jr-lines-table__unit">{{ $t('transactions.lines.colUnit') }}</th>
              <th class="jr-lines-table__price">{{ $t('transactions.lines.colUnitPrice') }}</th>
              <th class="jr-lines-table__disc">{{ $t('transactions.lines.colDisc') }}</th>
              <th>{{ $t('transactions.lines.colWarehouse') }}</th>
              <th>{{ $t('transactions.lines.colPriceType') }}</th>
              <th v-if="documentTypeIsSales">{{ $t('transactions.lines.colMargin') }}</th>
              <th class="jr-lines-table__end">{{ $t('transactions.lines.colLineTotal') }}</th>
              <th class="jr-lines-table__actions">{{ $t('transactions.lines.colActions') }}</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(row, idx) in linesLocal" :key="row.__key">
              <tr
                :class="{
                  'jr-lines-table__row--error': rowHasErrors(row),
                  'jr-lines-table__row--selected': !!row.selected,
                }">
                <td v-if="!disabled" class="jr-lines-table__check">
                  <JRCheckbox
                    :modelValue="!!row.selected"
                    :inputId="`line-select-${row.__key}`"
                    ariaLabel="Select line"
                    :disabled="disabled"
                    @update:modelValue="(v) => (row.selected = !!v)" />
                </td>
                <td class="jr-lines-table__thumb">
                  <button
                    type="button"
                    class="jr-lines-product-cell__thumb"
                    :disabled="!row.product"
                    :aria-label="
                      row.product
                        ? `View images of ${row.product_label || 'product'}`
                        : 'No product selected'
                    "
                    @click="openImageGallery(row)">
                    <img
                      v-if="lineImageSrc(row)"
                      :src="lineImageSrc(row)"
                      alt=""
                      class="jr-lines-product-cell__img"
                      width="40"
                      height="40"
                      loading="lazy"
                      decoding="async"
                      @error="onLineImageError(row)" />
                    <span
                      v-else
                      class="jr-lines-product-cell__ph"
                      aria-hidden="true" />
                  </button>
                </td>
                <td class="jr-lines-table__product">
                  <Select
                    class="jr-control"
                    :inputId="`product-${idx}`"
                    :modelValue="row.product"
                    :options="optionsForProduct(row)"
                    optionLabel="label"
                    optionValue="value"
                    :placeholder="$t('transactions.lines.searchProductPlaceholder')"
                    filter
                    :filterPlaceholder="$t('transactions.lines.filterMinChars')"
                    :emptyFilterMessage="$t('transactions.lines.emptyFilterMessage')"
                    :loading="!!loading.products[idx]"
                    :disabled="disabled"
                    :invalid="!!row._errors?.product"
                    showClear
                    fluid
                    @filter="(e) => onProductFilter(idx, e)"
                    @show="() => onProductShow(idx, row)"
                    @update:modelValue="(val) => onProductModel(idx, val)" />
                  <JRBadge
                    v-if="isSerializedRow(row)"
                    class="jr-lines-table__serial"
                    value="SERIALIZED"
                    severity="info" />
                  <p
                    v-if="rowErrorText(row._errors?.product)"
                    class="jr-lines-field-error"
                    role="alert">
                    {{ rowErrorText(row._errors.product) }}
                  </p>
                </td>
                <td class="jr-lines-table__qty">
                  <div @focusout="onQuantityBlurMerge(idx)">
                    <JRInput
                      :inputId="`quantity-${idx}`"
                      type="number"
                      mode="decimal"
                      :modelValue="emptyToNull(row.quantity)"
                      :min="0"
                      :minFractionDigits="0"
                      :maxFractionDigits="2"
                      :showButtons="true"
                      buttonLayout="stacked"
                      placeholder="0"
                      :disabled="disabled"
                      :invalid="!!row._errors?.quantity"
                      @update:modelValue="
                        (v) => {
                          setNumeric(row, 'quantity', v);
                          onQuantityInput(idx);
                        }
                      " />
                  </div>
                  <p
                    v-if="rowErrorText(row._errors?.quantity)"
                    class="jr-lines-field-error"
                    role="alert">
                    {{ rowErrorText(row._errors.quantity) }}
                  </p>
                </td>
                <td class="jr-lines-table__unit">
                  <JRSelect
                    :inputId="`unit-${idx}`"
                    v-model="row.unit"
                    :options="unitsOptions"
                    optionLabel="label"
                    optionValue="value"
                    :placeholder="$t('transactions.lines.unitPlaceholder')"
                    filter
                    :disabled="disabled"
                    :invalid="!!row._errors?.unit"
                    @update:modelValue="onUnitUpdated(idx)" />
                  <p
                    v-if="rowErrorText(row._errors?.unit)"
                    class="jr-lines-field-error"
                    role="alert">
                    {{ rowErrorText(row._errors.unit) }}
                  </p>
                </td>
                <td class="jr-lines-table__price">
                  <JRInput
                    :inputId="`unit_price-${idx}`"
                    type="number"
                    mode="currency"
                    currency="USD"
                    locale="en-US"
                    :modelValue="emptyToNull(row.unit_price)"
                    :min="0"
                    :minFractionDigits="2"
                    :maxFractionDigits="2"
                    placeholder="0.00"
                    :disabled="disabled"
                    :invalid="!!row._errors?.unit_price"
                    @update:modelValue="
                      (v) => {
                        setNumeric(row, 'unit_price', v);
                        onUnitPriceInput(idx);
                      }
                    " />
                  <p
                    v-if="rowErrorText(row._errors?.unit_price)"
                    class="jr-lines-field-error"
                    role="alert">
                    {{ rowErrorText(row._errors.unit_price) }}
                  </p>
                </td>
                <td class="jr-lines-table__disc">
                  <JRInput
                    :inputId="`discount_percentage-${idx}`"
                    type="number"
                    mode="decimal"
                    prefix="% "
                    :modelValue="emptyToNull(row.discount_percentage)"
                    :min="0"
                    :max="100"
                    :minFractionDigits="0"
                    :maxFractionDigits="2"
                    :useGrouping="false"
                    placeholder="0"
                    :disabled="disabled"
                    :invalid="!!row._errors?.discount_percentage"
                    @update:modelValue="
                      (v) => {
                        setNumeric(row, 'discount_percentage', v);
                        onDiscountPercentageInput(idx);
                      }
                    " />
                </td>
                <td>
                  <JRSelect
                    :inputId="`warehouse-${idx}`"
                    v-model="row.warehouse"
                    :options="warehousesOptions"
                    optionLabel="label"
                    optionValue="value"
                    :placeholder="$t('transactions.lines.warehousePlaceholder')"
                    filter
                    showClear
                    :disabled="disabled"
                    :invalid="!!row._errors?.warehouse" />
                  <p
                    v-if="rowErrorText(row._errors?.warehouse)"
                    class="jr-lines-field-error"
                    role="alert">
                    {{ rowErrorText(row._errors.warehouse) }}
                  </p>
                </td>
                <td>
                  <JRSelect
                    :inputId="`price_type-${idx}`"
                    v-model="row.price_type"
                    :options="priceTypesOptions"
                    optionLabel="label"
                    optionValue="value"
                    :placeholder="$t('transactions.lines.priceTypePlaceholder')"
                    filter
                    showClear
                    :disabled="disabled"
                    @update:modelValue="onPriceTypeUpdated(idx)" />
                  <p
                    v-if="documentTypeIsSales && pricingHint(row)"
                    class="jr-lines-hint">
                    {{ pricingHint(row) }}
                  </p>
                </td>
                <td v-if="documentTypeIsSales">
                  <JRInput
                    :inputId="`margin_percent-${idx}`"
                    type="number"
                    :modelValue="emptyToNull(row.margin_percent)"
                    :min="0"
                    :max="100"
                    :minFractionDigits="0"
                    :maxFractionDigits="2"
                    placeholder="0"
                    :disabled="disabled || !canEditLineMargin"
                    :invalid="!!row._errors?.margin_percent"
                    @update:modelValue="
                      (v) => {
                        row.margin_percent =
                          v == null || v === '' ? null : Number(v);
                        onMarginPercentInput(idx);
                      }
                    " />
                </td>
                <td class="jr-lines-table__end jr-lines-table__total">
                  {{ currency(lineTotalAfterDiscount(row)) }}
                </td>
                <td class="jr-lines-table__actions">
                  <JRRowActions
                    :compact="false"
                    :entity-label="lineEntityLabel(row)"
                    :actions="rowLineActions(idx)" />
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
      <p
        v-if="hideToolbar && linesLocal.length"
        class="jr-lines__count jr-lines__count--footer">
        {{ $t("transactions.lines.rowsCount", { count: linesLocal.length }) }}
      </p>
    </div>

    <JRDrawer
      class="jr-lines-drawer"
      :visible="sheetOpen"
      :header="
        disabled
          ? $t('transactions.lines.sheetHeaderLine')
          : $t('transactions.lines.sheetHeaderEdit')
      "
      position="right"
      @update:visible="onSheetVisible">
      <div v-if="sheetRow" class="jr-lines-sheet">
        <JRField
          :label="$t('transactions.lines.colProduct')"
          :inputId="`sheet-product`"
          required
          :error="rowErrorText(sheetRow._errors?.product)">
          <Select
            class="jr-control"
            inputId="sheet-product"
            :modelValue="sheetRow.product"
            :options="optionsForProduct(sheetRow)"
            optionLabel="label"
            optionValue="value"
            :placeholder="$t('transactions.lines.searchProductPlaceholder')"
            filter
            :filterPlaceholder="$t('transactions.lines.filterMinChars')"
            :emptyFilterMessage="$t('transactions.lines.emptyFilterMessage')"
            :loading="sheetIndex != null && !!loading.products[sheetIndex]"
            :disabled="disabled"
            :invalid="!!sheetRow._errors?.product"
            showClear
            fluid
            @filter="
              (e) => sheetIndex != null && onProductFilter(sheetIndex, e)
            "
            @show="
              () => sheetIndex != null && onProductShow(sheetIndex, sheetRow)
            "
            @update:modelValue="
              (val) => sheetIndex != null && onProductModel(sheetIndex, val)
            " />
          <JRBadge
            v-if="isSerializedRow(sheetRow)"
            class="jr-lines-sheet__badge"
            value="SERIALIZED"
            severity="info" />
        </JRField>

        <div class="jr-lines-sheet__grid">
          <JRField
            :label="$t('transactions.lines.colQty')"
            inputId="sheet-qty"
            :error="rowErrorText(sheetRow._errors?.quantity)">
            <div
              @focusout="sheetIndex != null && onQuantityBlurMerge(sheetIndex)">
              <JRInput
                inputId="sheet-qty"
                type="number"
                mode="decimal"
                :modelValue="emptyToNull(sheetRow.quantity)"
                :min="0"
                :minFractionDigits="0"
                :maxFractionDigits="2"
                :showButtons="true"
                buttonLayout="stacked"
                :disabled="disabled"
                @update:modelValue="
                  (v) => {
                    setNumeric(sheetRow, 'quantity', v);
                    if (sheetIndex != null) onQuantityInput(sheetIndex);
                  }
                " />
            </div>
          </JRField>
          <JRField
            :label="$t('transactions.lines.colUnit')"
            inputId="sheet-unit"
            :error="rowErrorText(sheetRow._errors?.unit)">
            <JRSelect
              inputId="sheet-unit"
              v-model="sheetRow.unit"
              :options="unitsOptions"
              optionLabel="label"
              optionValue="value"
              :placeholder="$t('transactions.lines.unitPlaceholder')"
              filter
              :disabled="disabled"
              @update:modelValue="
                sheetIndex != null && onUnitUpdated(sheetIndex)
              " />
          </JRField>
          <JRField
            :label="$t('transactions.lines.colUnitPrice')"
            inputId="sheet-unit-price"
            :error="rowErrorText(sheetRow._errors?.unit_price)">
            <JRInput
              inputId="sheet-unit-price"
              type="number"
              mode="currency"
              currency="USD"
              locale="en-US"
              :modelValue="emptyToNull(sheetRow.unit_price)"
              :min="0"
              :minFractionDigits="2"
              :maxFractionDigits="2"
              :disabled="disabled"
              @update:modelValue="
                (v) => {
                  setNumeric(sheetRow, 'unit_price', v);
                  if (sheetIndex != null) onUnitPriceInput(sheetIndex);
                }
              " />
          </JRField>
          <JRField :label="$t('transactions.lines.colDisc')" inputId="sheet-disc">
            <JRInput
              inputId="sheet-disc"
              type="number"
              mode="decimal"
              prefix="% "
              :modelValue="emptyToNull(sheetRow.discount_percentage)"
              :min="0"
              :max="100"
              :minFractionDigits="0"
              :maxFractionDigits="2"
              :useGrouping="false"
              :disabled="disabled"
              @update:modelValue="
                (v) => {
                  setNumeric(sheetRow, 'discount_percentage', v);
                  if (sheetIndex != null) onDiscountPercentageInput(sheetIndex);
                }
              " />
          </JRField>
        </div>

        <JRField
          :label="$t('transactions.lines.colWarehouse')"
          inputId="sheet-warehouse"
          :error="rowErrorText(sheetRow._errors?.warehouse)">
          <JRSelect
            inputId="sheet-warehouse"
            v-model="sheetRow.warehouse"
            :options="warehousesOptions"
            optionLabel="label"
            optionValue="value"
            :placeholder="$t('transactions.lines.warehousePlaceholder')"
            filter
            showClear
            :disabled="disabled" />
        </JRField>

        <JRField :label="$t('transactions.lines.colPriceType')" inputId="sheet-price-type">
          <JRSelect
            inputId="sheet-price-type"
            v-model="sheetRow.price_type"
            :options="priceTypesOptions"
            optionLabel="label"
            optionValue="value"
            :placeholder="$t('transactions.lines.priceTypePlaceholder')"
            filter
            showClear
            :disabled="disabled"
            @update:modelValue="
              sheetIndex != null && onPriceTypeUpdated(sheetIndex)
            " />
          <p
            v-if="documentTypeIsSales && pricingHint(sheetRow)"
            class="jr-lines-hint">
            {{ pricingHint(sheetRow) }}
          </p>
        </JRField>

        <JRField
          v-if="documentTypeIsSales"
          :label="$t('transactions.lines.colMargin')"
          inputId="sheet-margin">
          <JRInput
            inputId="sheet-margin"
            type="number"
            :modelValue="emptyToNull(sheetRow.margin_percent)"
            :min="0"
            :max="100"
            :minFractionDigits="0"
            :maxFractionDigits="2"
            :disabled="disabled || !canEditLineMargin"
            @update:modelValue="
              (v) => {
                sheetRow.margin_percent =
                  v == null || v === '' ? null : Number(v);
                if (sheetIndex != null) onMarginPercentInput(sheetIndex);
              }
            " />
        </JRField>

        <p class="jr-lines-sheet__total">
          {{ $t("transactions.lines.sheetLineTotal") }}
          <strong>{{ currency(lineTotalAfterDiscount(sheetRow)) }}</strong>
        </p>
      </div>
      <template #footer>
        <div class="jr-lines-sheet__footer">
          <JRButton type="button" variant="primary" @click="closeSheet">
            {{ $t("common.done") }}
          </JRButton>
          <JRRowActions
            v-if="!disabled && sheetIndex != null"
            :compact="false"
            :solid="true"
            :entity-label="lineEntityLabel(sheetRow)"
            :actions="rowMaintenanceActions(sheetIndex)" />
        </div>
      </template>
    </JRDrawer>

    <JRDialog
      :visible="deleteDialogVisible"
      :header="$t('transactions.lines.deleteDialogHeader')"
      :message="$t('transactions.lines.deleteDialogMessage')"
      :confirmLabel="$t('common.delete')"
      confirmVariant="danger"
      @update:visible="onDeleteVisible"
      @confirm="confirmPendingDelete" />

    <JRDialog
      :visible="galleryVisible"
      :header="galleryHeader"
      size="square"
      :showFooter="false"
      @update:visible="onGalleryVisible">
      <ProductBrandImages
        v-if="galleryProductId"
        :product-id="galleryProductId"
        :readonly="true" />
    </JRDialog>
  </div>
</template>

<script setup>
import {
  ref,
  watch,
  computed,
  nextTick,
  onMounted,
  onBeforeUnmount,
} from "vue";
import axios from "axios";
import Select from "primevue/select";
import Button from "primevue/button";
import PencilIcon from "@primevue/icons/pencil";
import TrashIcon from "@primevue/icons/trash";
import Plus from "@primeicons/vue/plus";
import Copy from "@primeicons/vue/copy";
import Trash from "@primeicons/vue/trash";
import ProductBrandImages from "@components/inventory/ProductBrandImages.vue";
import {
  JRButton,
  JRSelect,
  JRInput,
  JRField,
  JRBadge,
  JREmptyState,
  JRDialog,
  JRDrawer,
  JRRowActions,
  JRCheckbox,
} from "@ui";

const PHONE_MQ = "(max-width: 767.98px)";
const TABLET_MQ = "(min-width: 768px) and (max-width: 1023.98px)";

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
  /** When true, disables Add Row and line inputs only (no full overlay). */
  disabled: { type: Boolean, default: false },
  /** When true, parent JRSection owns Add / Serial actions. */
  hideToolbar: { type: Boolean, default: false },
});
const emit = defineEmits(["update:lines", "recalc", "open-asset-tags"]);

const linesLocal = ref([]);
const selectAll = ref(false);
const productOptions = ref([]);
const loading = ref({ products: {} });
const isUpdatingFromProps = ref(false);
const defaultWarehouse = ref(null);
const productFilterTimers = {};
const isPhone = ref(false);
const isTablet = ref(false);
const sheetOpen = ref(false);
const sheetIndex = ref(null);
const deleteDialogVisible = ref(false);
const pendingDeleteIndex = ref(null);
const deleteResolved = ref(false);
const galleryVisible = ref(false);
const galleryProductId = ref(null);
const galleryProductLabel = ref("");
const brokenImageIds = ref({});

const isCompact = computed(() => isPhone.value || isTablet.value);
const sheetRow = computed(() =>
  sheetIndex.value == null ? null : linesLocal.value[sheetIndex.value] || null,
);
const galleryHeader = computed(() =>
  galleryProductLabel.value
    ? `Images · ${galleryProductLabel.value}`
    : "Product images",
);

function syncViewport() {
  if (typeof window === "undefined" || !window.matchMedia) {
    isPhone.value = false;
    isTablet.value = false;
    return;
  }
  isPhone.value = window.matchMedia(PHONE_MQ).matches;
  isTablet.value = window.matchMedia(TABLET_MQ).matches;
}

function rowErrorText(err) {
  if (!err) return "";
  if (Array.isArray(err)) return rowErrorText(err[0]);
  if (typeof err === "object") {
    if (err.message != null) return rowErrorText(err.message);
    if (err.string != null) return String(err.string);
    if (err.detail != null) return rowErrorText(err.detail);
    if (err.error_type === "insufficient_stock" || err.error_type?.string === "insufficient_stock") {
      const productName = err.product_name?.string ?? err.product_name;
      const available = err.available?.string ?? err.available;
      const requested = err.requested?.string ?? err.requested;
      if (available != null && requested != null) {
        const prefix = productName ? `${productName}: ` : "";
        return `${prefix}Insufficient stock (available: ${available}, requested: ${requested})`;
      }
    }
    try {
      return JSON.stringify(err);
    } catch {
      return "Invalid value";
    }
  }
  return String(err);
}

function rowHasErrors(row) {
  return Object.keys(row?._errors || {}).length > 0;
}

function isSerializedRow(row) {
  if (!row?.product) return false;
  const opt = optionsForProduct(row).find((o) => o.value === row.product);
  return opt?.product?.tracking_mode === "SERIALIZED";
}

function unitLabel(row) {
  const opt = props.unitsOptions.find((o) => o.value === row?.unit);
  return opt?.label || "";
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
          tracking_mode: row._tracking_mode,
        },
      });
    }
  }
  return opts;
}

function lineImageSrc(row) {
  const productId = row?.product;
  if (!productId || brokenImageIds.value[productId]) return "";
  return row.product_image || "";
}

function onLineImageError(row) {
  const productId = row?.product;
  if (!productId) return;
  brokenImageIds.value = { ...brokenImageIds.value, [productId]: true };
}

function openImageGallery(row) {
  if (!row?.product) return;
  galleryProductId.value = row.product;
  galleryProductLabel.value =
    row.product_label || row.product_name || `Product #${row.product}`;
  galleryVisible.value = true;
}

function onGalleryVisible(visible) {
  galleryVisible.value = visible;
  if (!visible) {
    galleryProductId.value = null;
    galleryProductLabel.value = "";
  }
}

function applyProductBrandAndImage(row, productLike) {
  if (!row) return;
  const brandId =
    productLike?.brand ??
    productLike?.default_brand?.id ??
    productLike?.default_brand ??
    null;
  if (brandId != null && brandId !== "") {
    row.brand = brandId;
  }
  if (productLike?.image) {
    row.product_image = productLike.image;
    if (row.product && brokenImageIds.value[row.product]) {
      const next = { ...brokenImageIds.value };
      delete next[row.product];
      brokenImageIds.value = next;
    }
  }
}

function lineEntityLabel(row) {
  return (
    row?.product_label || (row?.product ? `Product #${row.product}` : "Line")
  );
}

function emptyToNull(value) {
  return value === "" || value === undefined ? null : value;
}

function round2(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.round((n + Number.EPSILON) * 100) / 100;
}

function setNumeric(row, field, value) {
  if (value === null || value === undefined || value === "") {
    row[field] = 0;
    return;
  }
  // Money / qty fields: keep 2 dp so payload never trips Django decimal_places
  if (
    field === "unit_price" ||
    field === "quantity" ||
    field === "discount_percentage" ||
    field === "margin_percent"
  ) {
    row[field] = round2(value);
    return;
  }
  row[field] = Number(value);
}

function hasPermission(permission) {
  try {
    const userPermissions = JSON.parse(
      localStorage.getItem("userPermissions") || "{}",
    );
    const permissions = Array.isArray(userPermissions?.permissions)
      ? userPermissions.permissions
      : [];
    return permissions.includes(permission);
  } catch {
    return false;
  }
}

const canEditLineMargin = computed(
  () =>
    props.documentTypeIsSales &&
    (hasPermission("appinventory.add_pricetype") ||
      hasPermission("appinventory.change_pricetype")),
);

function lineStructureKey(l) {
  const p = l?.product;
  const prod =
    p != null && typeof p === "object" && !Array.isArray(p) && "id" in p
      ? p.id
      : p;
  return `${l?.id ?? ""}|${l?.__key ?? ""}|${prod ?? ""}`;
}

function linesStructureSignature(rows) {
  return (rows || []).map(lineStructureKey).join("\n");
}

watch(
  () => props.lines,
  async (val) => {
    isUpdatingFromProps.value = true;

    const newLines = (val || []).map((x) => ({
      ...x,
      __key: x.__key || x.id || cryptoRandom(),
      selected: !!x.selected,
      brands: x.brands || [],
      product_image: x.product_image || "",
      product_label: x.product_label || x.product_name || "",
      price_manually_edited:
        x.price_manually_edited ?? x.pricing_rule === "MANUAL",
      _purchase_unit_cost: x._purchase_unit_cost ?? null,
      _suppressPriceEvent: false,
    }));

    // Comparar también contenido cuando todos los ids son null (importar favoritos, etc.)
    const currentLength = linesLocal.value.length;
    const newLength = newLines.length;
    const currentIds = linesLocal.value.map((l) => l.id).sort();
    const newIds = newLines.map((l) => l.id).sort();
    const structureChanged =
      linesStructureSignature(linesLocal.value) !==
      linesStructureSignature(newLines);

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
    } else {
      // Same structure: still sync validation errors from parent (Save 400, etc.)
      // and adopt product_image if local still lacks one (favorite import race).
      newLines.forEach((incoming, idx) => {
        const local = linesLocal.value[idx];
        if (!local) return;
        const nextErrors = incoming._errors || {};
        const prevErrors = local._errors || {};
        const nextKey = JSON.stringify(nextErrors);
        const prevKey = JSON.stringify(prevErrors);
        if (nextKey !== prevKey) {
          local._errors = { ...nextErrors };
        }
        if (!local.product_image && incoming.product_image) {
          local.product_image = incoming.product_image;
        }
      });
    }

    nextTick(() => {
      isUpdatingFromProps.value = false;
    });
  },
  { immediate: true, deep: true },
);

watch(
  linesLocal,
  (val) => {
    // Don't emit if we're updating from props to avoid infinite loops
    if (!isUpdatingFromProps.value) {
      nextTick(() => {
        emit("update:lines", val);
        emit("recalc");
      });
    }
  },
  { deep: true },
);

// Watcher para asignar warehouse por defecto cuando esté disponible
watch(defaultWarehouse, (newWarehouse) => {
  if (newWarehouse && linesLocal.value.length > 0) {
    linesLocal.value.forEach((line) => {
      if (!line.warehouse) {
        line.warehouse = newWarehouse;
      }
    });
  }
});

// Watch for document type changes to validate warehouse requirements
watch(
  () => props.documentTypeId,
  async (newDocTypeId) => {
    if (newDocTypeId) {
      try {
        const { data } = await axios.get(
          `/api/document-types/${newDocTypeId}/`,
        );
        const requiresWarehouse = data.warehouse_required;

        // Clear warehouse validation errors if warehouse is no longer required
        if (!requiresWarehouse) {
          linesLocal.value.forEach((line) => {
            if (line._errors?.warehouse) {
              delete line._errors.warehouse;
            }
          });
        }
      } catch (error) {
        console.warn("Could not fetch document type info:", error);
      }
    }
  },
);

/** Recalcular totales si cambia venta/no venta (columna Margin y reglas). */
watch(
  () => props.documentTypeIsSales,
  () => {
    nextTick(() => recalcAllRows());
  },
);

function cryptoRandom() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function currency(n) {
  const num = Number(n || 0);
  return num.toLocaleString("en-US", { style: "currency", currency: "USD" });
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
  if (pricingMethod === "MARKUP") return +(c * (1 + f)).toFixed(2);
  if (pricingMethod === "MARGIN") {
    if (f >= 1) return null;
    return +(c / (1 - f)).toFixed(2);
  }
  return null;
}

function pricingHint(row) {
  if (!props.documentTypeIsSales) return "";
  if (row.pricing_rule === "MANUAL") {
    if (row.margin_percent != null && row.margin_percent !== "")
      return `Manual · ref. ${Number(row.margin_percent).toFixed(2)}%`;
    return "Manual";
  }
  if (
    row.pricing_rule === "MARKUP" &&
    row.margin_percent != null &&
    row.margin_percent !== ""
  )
    return `Mkup ${Number(row.margin_percent).toFixed(2)}%`;
  if (
    row.pricing_rule === "MARGIN" &&
    row.margin_percent != null &&
    row.margin_percent !== ""
  )
    return `Margen ${Number(row.margin_percent).toFixed(2)}%`;
  return "";
}

/** Margen/markup por defecto del Price Type seleccionado (solo ventas). */
function syncPriceTypeMetadataToRow(idx) {
  const r = linesLocal.value[idx];
  if (!r || !props.documentTypeIsSales || !r.price_type) return;
  const meta = props.priceTypesOptions.find((o) => o.value === r.price_type);
  if (!meta) return;

  if (meta.pricing_method === "MARKUP" || meta.pricing_method === "MARGIN") {
    if (meta.margin_percent != null && meta.margin_percent !== "") {
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
    const { data } = await axios.get(
      `/api/products/${r.product}/default-price/`,
      { params },
    );
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
    console.warn("applyDefaultCatalogPrice:", e);
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
    const { data } = await axios.get(
      `/api/products/${r.product}/purchase-cost/`,
      { params },
    );
    r._purchase_unit_cost =
      data.unit_cost != null ? Number(data.unit_cost) : null;
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
  const meta = props.priceTypesOptions.find((o) => o.value === r.price_type);
  if (!meta || !meta.pricing_method || meta.pricing_method === "NONE")
    return false;
  const cost = r._purchase_unit_cost;
  if (cost == null || cost <= 0) return false;
  const pct = r.margin_percent ?? meta.margin_percent;
  if (pct == null || pct === "") return false;
  const price = salePriceFromCost(cost, meta.pricing_method, Number(pct));
  if (price == null) return false;
  r._suppressPriceEvent = true;
  r.unit_price = price;
  r.pricing_rule = meta.pricing_method === "MARKUP" ? "MARKUP" : "MARGIN";
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

  if (
    r.margin_percent === "" ||
    r.margin_percent === null ||
    r.margin_percent === undefined
  ) {
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

  if (r.pricing_rule !== "MANUAL") {
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
  const r = linesLocal.value[idx];
  if (r?._errors?.quantity) {
    delete r._errors.quantity;
  }
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
      nextTick(() => focusNextField(survivorIdx, "unit"));
      return;
    }
  }
  focusNextField(idx, "unit");
}

function onUnitPriceInput(idx) {
  const r = linesLocal.value[idx];
  if (r._errors?.unit_price) {
    delete r._errors.unit_price;
  }
  if (r._suppressPriceEvent) {
    recalcRow(idx);
    return;
  }
  r.price_manually_edited = true;
  r.pricing_rule = "MANUAL";
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
    const { data } = await axios.get("/api/default-warehouse/");
    if (data.id) {
      defaultWarehouse.value = data.id;
    }
  } catch (error) {
    console.warn("Could not fetch default warehouse:", error);
  }
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
    brands: [],
    brand: null, // Autofill desde Product.brand (sin columna UI)
    product_image: "",
    _errors: {},
  };

  linesLocal.value.push(newLine);
}

const hasSelection = computed(() => linesLocal.value.some((r) => !!r.selected));

function onSelectAll(checked) {
  selectAll.value = !!checked;
  linesLocal.value.forEach((r) => {
    r.selected = !!checked;
  });
}

function removeSelected() {
  if (props.disabled || !hasSelection.value) return;
  linesLocal.value = linesLocal.value.filter((r) => !r.selected);
  selectAll.value = false;
  if (sheetOpen.value) closeSheet();
}

function duplicateSelected() {
  if (props.disabled || !hasSelection.value) return;
  const selectedLines = linesLocal.value.filter((r) => r.selected);
  const start = linesLocal.value.length;
  selectedLines.forEach((line) => {
    linesLocal.value.push({
      ...line,
      __key: cryptoRandom(),
      selected: false,
      id: null,
      quantity: 1,
      final_price: 0,
      _errors: {},
    });
  });
  for (let i = start; i < linesLocal.value.length; i++) {
    recalcRow(i);
  }
  selectAll.value = false;
  linesLocal.value.forEach((r) => {
    r.selected = false;
  });
}

function removeRowAt(idx) {
  linesLocal.value.splice(idx, 1);
  if (sheetIndex.value === idx) closeSheet();
  else if (sheetIndex.value != null && sheetIndex.value > idx) {
    sheetIndex.value -= 1;
  }
}

function rowNeedsDeleteConfirm(row) {
  if (!row) return false;
  return !!(
    row.id ||
    row.product ||
    (row.quantity != null && Number(row.quantity) !== 1) ||
    (row.unit_price != null && Number(row.unit_price) !== 0) ||
    row.unit ||
    row.brand
  );
}

function requestDelete(idx) {
  if (props.disabled) return;
  const row = linesLocal.value[idx];
  if (!rowNeedsDeleteConfirm(row)) {
    removeRowAt(idx);
    return;
  }
  pendingDeleteIndex.value = idx;
  deleteResolved.value = false;
  deleteDialogVisible.value = true;
}

function confirmPendingDelete() {
  const index = pendingDeleteIndex.value;
  deleteResolved.value = true;
  pendingDeleteIndex.value = null;
  deleteDialogVisible.value = false;
  if (index == null) return;
  removeRowAt(index);
}

function onDeleteVisible(visible) {
  deleteDialogVisible.value = visible;
  if (visible) return;
  if (deleteResolved.value) {
    deleteResolved.value = false;
    return;
  }
  pendingDeleteIndex.value = null;
}

function removeRow(idx) {
  requestDelete(idx);
}

function duplicateRow(idx) {
  if (props.disabled) return;
  const originalLine = linesLocal.value[idx];
  const duplicatedLine = {
    ...originalLine,
    __key: cryptoRandom(),
    selected: false,
    id: null,
    quantity: 1,
    final_price: 0,
    _errors: {},
  };
  const newIdx = idx + 1;
  linesLocal.value.splice(newIdx, 0, duplicatedLine);
  recalcRow(newIdx);
  if (isCompact.value) openSheet(newIdx);
}

function openSheet(idx) {
  sheetIndex.value = idx;
  sheetOpen.value = true;
}

function closeSheet() {
  sheetOpen.value = false;
  sheetIndex.value = null;
}

function onSheetVisible(visible) {
  sheetOpen.value = visible;
  if (!visible) sheetIndex.value = null;
}

function addLineFromToolbar() {
  addLine();
  if (isCompact.value && !props.disabled) {
    nextTick(() => openSheet(linesLocal.value.length - 1));
  }
}

function rowPrimaryActions(idx) {
  return [
    {
      key: "edit",
      label: "Edit",
      severity: "secondary",
      icon: PencilIcon,
      command: () => openSheet(idx),
    },
  ];
}

function rowMaintenanceActions(idx) {
  if (props.disabled) return [];
  return [
    {
      key: "delete",
      label: "Delete",
      severity: "danger",
      icon: TrashIcon,
      command: () => requestDelete(idx),
    },
  ];
}

function rowLineActions(idx) {
  return rowMaintenanceActions(idx);
}

function onProductFilter(idx, event) {
  const query = event?.value ?? "";
  if (productFilterTimers[idx]) clearTimeout(productFilterTimers[idx]);
  productFilterTimers[idx] = setTimeout(() => {
    searchProducts(idx, query);
  }, 250);
}

function onProductShow(idx, row) {
  if (
    row?.product_label &&
    (!productOptions.value || !productOptions.value.length)
  ) {
    productOptions.value = optionsForProduct(row);
  }
}

async function onProductModel(idx, val) {
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
  if (option) {
    if (option.product?.tracking_mode)
      r._tracking_mode = option.product.tracking_mode;
    await onProductSelected(idx, option);
  } else {
    await onProductChanged(idx);
  }
}

async function searchProducts(idx, query) {
  if (!query || query.length < 2) {
    productOptions.value = [];
    return;
  }

  loading.value.products[idx] = true;
  try {
    const { data } = await axios.get("/api/products/", {
      params: {
        search: query,
        page_size: 20,
        is_active: true,
      },
    });
    const list = Array.isArray(data) ? data : data?.results || [];
    productOptions.value = list.map((p) => {
      const option = {
        value: p.id,
        label: `${p.name} (${p.sku})`,
        product: p,
      };
      return option;
    });
  } catch (error) {
    console.error("Error searching products:", error);
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
    console.warn("Could not fetch product brands:", error);
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
      // Marcas para el select JR (value / label)
      r.brands = brands.map((b) => ({ value: b.id, label: b.name }));

      // Si no hay marca seleccionada, usar la default
      if (!r.brand) {
        const defaultBrand = brands.find((b) => b.is_default) || brands[0];
        r.brand = defaultBrand.id;
      }
    }
  } catch (error) {
    console.warn("Error updating brands for product:", error);
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
  const r = linesLocal.value[idx];
  r.product_label = option?.product?.name || option?.label || "";
  r.price_manually_edited = false;
  applyProductBrandAndImage(r, option?.product);

  // Auto-fill fields from ProductPrice predeterminado
  if (option?.value) {
    try {
      // Construir params con document_type_id si está disponible
      const params = {};
      if (props.documentTypeId) {
        params.document_type_id = props.documentTypeId;
      }

      const { data } = await axios.get(
        `/api/products/${option.value}/default-price/`,
        { params },
      );

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

      // Brand FK de Product (sin selector en UI)
      applyProductBrandAndImage(r, {
        brand: data.default_brand?.id,
        image: r.product_image || option?.product?.image,
      });
      if (!r.brand) {
        await updateBrandsForProduct(idx, option.value);
      }

      if (data.purchase_unit_cost != null) {
        r._purchase_unit_cost = Number(data.purchase_unit_cost);
      }

      if (!r.product_image) {
        await ensureProductImage(idx);
      }
    } catch (error) {
      console.warn("Could not fetch product default price:", error);

      // Fallback: Auto-fill default unit from product if available
      if (option?.product?.unit_default) {
        r.unit = option.product.unit_default.id || option.product.unit_default;
      }

      await updateBrandsForProduct(idx, option.value);
      await ensureProductImage(idx);
      await refreshPurchaseCost(idx);
    }
  }

  // Auto-fill default price type from work account if available (fallback)
  if (props.workAccountId && props.workAccountId !== null && !r.price_type) {
    try {
      const { data } = await axios.get(
        `/api/work-accounts/${props.workAccountId}/`,
      );
      if (data.default_price_type) {
        r.price_type = data.default_price_type;
      }
    } catch (error) {
      // Manejar específicamente el caso de work account no encontrado (404)
      if (error.response?.status === 404) {
        console.warn(
          `Work account ${props.workAccountId} not found, skipping default price type`,
        );
      } else {
        console.warn("Could not fetch work account default price type:", error);
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

async function ensureProductImage(idx) {
  const r = linesLocal.value[idx];
  if (!r?.product || r.product_image) return;
  try {
    const { data } = await axios.get(`/api/products/${r.product}/images/`);
    const images = data?.images || [];
    const primary = images.find((img) => img.is_primary) || images[0] || null;
    if (primary?.image_url) {
      r.product_image = primary.image_url;
      if (brokenImageIds.value[r.product]) {
        const next = { ...brokenImageIds.value };
        delete next[r.product];
        brokenImageIds.value = next;
      }
    }
  } catch (error) {
    console.warn("Could not load product image:", error);
  }
}

function onProductCleared(idx) {
  const r = linesLocal.value[idx];
  r.product_label = "";
  r.product = null;
  r.product_image = "";
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
  if (
    !r ||
    props.workAccountId === null ||
    props.workAccountId === undefined ||
    r.price_type
  )
    return;
  try {
    const { data } = await axios.get(
      `/api/work-accounts/${props.workAccountId}/`,
    );
    if (data.default_price_type) {
      r.price_type = data.default_price_type;
    }
  } catch (error) {
    if (error.response?.status === 404) {
      console.warn(
        `Work account ${props.workAccountId} not found, skipping default price type`,
      );
    } else {
      console.warn("Could not fetch work account default price type:", error);
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
    const { data } = await axios.get(
      `/api/products/${r.product}/default-price/`,
      { params },
    );

    if (!r.unit && data.unit) r.unit = data.unit;
    if (data.price_type != null && data.price_type !== undefined) {
      r.price_type = data.price_type;
    }
    if (data.default_brand?.id != null && (r.brand == null || r.brand === "")) {
      r.brand = data.default_brand.id;
    }
    if (data.purchase_unit_cost != null) {
      r._purchase_unit_cost = Number(data.purchase_unit_cost);
    }
  } catch (e) {
    console.warn("rehydratePricingForRow default-price:", e);
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
  // Dos ticks: el watch de props deja isUpdatingFromProps=false antes de mutar.
  await nextTick();
  await nextTick();
  for (let i = 0; i < linesLocal.value.length; i++) {
    const row = linesLocal.value[i];
    if (!row?.product || !row.__favoriteImportReprice) continue;
    try {
      await rehydratePricingForRow(i);
    } catch (error) {
      console.warn("rehydratePricingForRow after favorite:", error);
    }
    try {
      await ensureProductImage(i);
    } finally {
      delete row.__favoriteImportReprice;
    }
  }
  emit("recalc");
}

/** Tras Excel/favoritos: completar miniaturas ausentes vía /images/. */
async function hydrateImagesAfterImport() {
  await nextTick();
  await nextTick();
  for (let i = 0; i < linesLocal.value.length; i++) {
    const row = linesLocal.value[i];
    if (!row?.product) continue;
    if (row.product_image && !row.__importHydrateImages) {
      delete row.__importHydrateImages;
      continue;
    }
    try {
      await ensureProductImage(i);
    } finally {
      delete row.__importHydrateImages;
    }
  }
  emit("recalc");
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
    if (
      o.product === r.product &&
      (o.unit || null) === (r.unit || null) &&
      (o.brand || null) === (r.brand || null)
    ) {
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
      line._errors.product = ["Product is required"];
      isValid = false;
    }

    if (!line.quantity || line.quantity <= 0) {
      line._errors.quantity = ["Quantity must be greater than 0"];
      isValid = false;
    }

    // unit es opcional según la estructura de la tabla (unit_id DEFAULT NULL)
    // if (!line.unit) {
    //   line._errors.unit = ['Unit is required'];
    //   isValid = false;
    // }

    if (
      line.unit_price === null ||
      line.unit_price === undefined ||
      line.unit_price < 0
    ) {
      line._errors.unit_price = ["Unit price must be 0 or greater"];
      isValid = false;
    }

    if (props.documentTypeIsSales) {
      if (
        line.margin_percent !== null &&
        line.margin_percent !== undefined &&
        line.margin_percent !== ""
      ) {
        const mp = Number(line.margin_percent);
        if (!Number.isFinite(mp) || mp < 0 || mp > 100) {
          line._errors.margin_percent = ["Margin % must be between 0 and 100"];
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
      quantity: "quantity",
      unit_price: "unit_price",
      discount_percentage: "discount_percentage",
      unit: "unit",
      warehouse: "warehouse",
      price_type: "price_type",
      margin_percent: "margin_percent",
      brand: "brand",
    };
    const fieldId = fieldMap[fieldName];
    if (!fieldId) return;
    const element = document.getElementById(`${fieldId}-${rowIndex}`);
    if (!element) return;
    if (element.tagName === "INPUT") {
      element.focus();
      element.select?.();
      return;
    }
    const inner =
      element.querySelector("input") ||
      element.closest(".p-select")?.querySelector("input");
    if (inner) {
      inner.focus();
      inner.select?.();
    } else {
      element.focus?.();
    }
  });
}

function focusNextRow(currentRowIndex) {
  nextTick(() => {
    const nextRowIndex = currentRowIndex + 1;
    const focusProduct = (idx) => {
      const el = document.getElementById(`product-${idx}`);
      const inner =
        el?.querySelector?.("input") ||
        el?.closest?.(".p-select")?.querySelector("input");
      if (inner) inner.focus();
      else if (isCompact.value) openSheet(idx);
    };
    if (nextRowIndex < linesLocal.value.length) {
      focusProduct(nextRowIndex);
    } else if (!props.disabled) {
      addLine();
      nextTick(() => {
        if (isCompact.value) openSheet(linesLocal.value.length - 1);
        else focusProduct(linesLocal.value.length - 1);
      });
    }
  });
}

let _phoneMq = null;
let _tabletMq = null;
let _onMedia = null;

// Cargar warehouse predeterminado al montar el componente
onMounted(async () => {
  syncViewport();
  if (typeof window !== "undefined" && window.matchMedia) {
    _phoneMq = window.matchMedia(PHONE_MQ);
    _tabletMq = window.matchMedia(TABLET_MQ);
    _onMedia = () => syncViewport();
    [_phoneMq, _tabletMq].forEach((mq) => {
      if (mq.addEventListener) mq.addEventListener("change", _onMedia);
      else mq.addListener(_onMedia);
    });
  }

  await loadDefaultWarehouse();

  if (linesLocal.value.length > 0 && defaultWarehouse.value) {
    linesLocal.value.forEach((line) => {
      if (!line.warehouse) {
        line.warehouse = defaultWarehouse.value;
      }
    });
  }
});

onBeforeUnmount(() => {
  [_phoneMq, _tabletMq].forEach((mq) => {
    if (!mq || !_onMedia) return;
    if (mq.removeEventListener) mq.removeEventListener("change", _onMedia);
    else mq.removeListener(_onMedia);
  });
  Object.values(productFilterTimers).forEach((t) => clearTimeout(t));
});

defineExpose({
  validateLines,
  rehydratePricingAfterFavoriteImport,
  hydrateImagesAfterImport,
  rehydratePricingForRow,
  addLine,
  addLineFromToolbar,
});
</script>

<style scoped>
.jr-lines {
  caret-color: var(--color-jr-primary);
}

.jr-lines ::selection {
  background: color-mix(in srgb, var(--color-jr-primary) 28%, transparent);
  color: var(--color-jr-text);
}

.jr-lines__toolbar {
  position: sticky;
  /* Mobile shell bar is fixed; stick just below it. */
  top: var(--jr-shell-mobile-bar, 3rem);
  z-index: 5;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin: 0 0 0.75rem;
  padding: 0.5rem 0 0.65rem;
  background: var(--color-jr-page, #f3f4f6);
  border-bottom: 1px solid var(--color-jr-border);
  box-shadow: 0 2px 8px color-mix(in srgb, var(--color-jr-text) 6%, transparent);
}

@media (min-width: 1024px) {
  .jr-lines__toolbar {
    /* Desktop topbar is sticky in-flow; offset by its height. */
    top: var(--jr-shell-topbar, 3.5rem);
  }
}

.jr-lines__toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
}

.jr-lines__maint {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  flex: 0 0 auto;
}

.jr-lines__maint-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.jr-lines__count {
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-lines__count--footer {
  margin: 0.5rem 0 0;
  text-align: right;
}

.jr-lines-table__check {
  width: 2.25rem;
  text-align: center;
  vertical-align: top;
}

.jr-lines-table__row--selected {
  background: color-mix(
    in srgb,
    var(--color-jr-primary) 6%,
    var(--color-jr-surface)
  );
}

.jr-lines-item__check {
  align-self: center;
  margin-right: 0.15rem;
}

.jr-lines-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.jr-lines-item {
  display: flex;
  align-items: stretch;
  gap: 0.5rem;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
}

.jr-lines-item--error {
  border-color: var(--color-jr-danger);
}

.jr-lines-item__main {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.jr-lines-product-cell {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  min-width: 0;
}

.jr-lines-product-cell__thumb {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  padding: 0;
  border: 0;
  background: none;
  line-height: 0;
  cursor: pointer;
  border-radius: var(--radius-jr-control);
}

.jr-lines-product-cell__thumb:disabled {
  cursor: default;
  opacity: 0.7;
}

.jr-lines-product-cell__thumb:hover:not(:disabled) .jr-lines-product-cell__img,
.jr-lines-product-cell__thumb:hover:not(:disabled) .jr-lines-product-cell__ph {
  border-color: var(--color-jr-hover-border);
}

.jr-lines-product-cell__thumb:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-lines-product-cell__img,
.jr-lines-product-cell__ph {
  width: 2.5rem;
  height: 2.5rem;
  flex-shrink: 0;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-control);
  background: var(--color-jr-surface-muted);
  object-fit: cover;
}

.jr-lines-product-cell__ph {
  display: block;
  border-style: dashed;
}

.jr-lines-table__thumb {
  width: 3.25rem;
  min-width: 3.25rem;
  text-align: center;
  vertical-align: middle;
}

.jr-lines-item__title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jr-lines-item__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-lines-item__sep {
  color: var(--color-jr-muted);
}

.jr-lines-item__total {
  font-weight: 600;
  color: var(--color-jr-text);
  font-variant-numeric: tabular-nums;
}

.jr-lines-item__error,
.jr-lines-field-error {
  margin: 0.25rem 0 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
}

.jr-lines-item__actions {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
}

.jr-lines-table-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
  scrollbar-width: thin;
  scrollbar-color: var(--color-jr-hover-border) transparent;
}

.jr-lines-table {
  width: 100%;
  min-width: 70rem;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.jr-lines-table th,
.jr-lines-table td {
  padding: 0.3rem 0.5rem;
  border-bottom: 1px solid var(--color-jr-border);
  vertical-align: top;
  text-align: left;
}

.jr-lines-table thead th {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-jr-text);
  background: var(--color-jr-surface-muted, var(--color-jr-page));
  position: sticky;
  top: 0;
  z-index: 1;
}

.jr-lines-table__row--error td {
  background: var(--color-jr-danger-subtle);
}

.jr-lines-table__end {
  text-align: right;
}

.jr-lines-table__total {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.jr-lines-table__actions {
  width: 5.25rem;
  white-space: nowrap;
}

.jr-lines-table__product {
  min-width: 20rem;
  width: 24%;
}

/* Qty: ####.## (+2 digits) + stacked steppers; tight gap before button-group. */
.jr-lines-table__qty {
  min-width: 8rem;
  width: 8rem;
}

.jr-lines-table__qty :deep(.p-inputnumber) {
  min-width: 0;
  width: 100%;
}

.jr-lines-table__qty :deep(.p-inputnumber-input) {
  min-width: 0;
  width: 100%;
  padding-inline-end: 0.2rem;
  font-variant-numeric: tabular-nums;
}

.jr-lines-table__qty :deep(.p-inputnumber-button) {
  width: 1.25rem;
  border-radius: var(--radius-jr-control, 0);
}

.jr-lines-table__qty :deep(.p-inputnumber-button-group) {
  min-width: 1.25rem;
}

.jr-lines-table__unit {
  min-width: 5.5rem;
  width: 6rem;
}

.jr-lines-table__price {
  min-width: 9.5rem;
  width: 9.5rem;
}

.jr-lines-table__price :deep(.p-inputnumber),
.jr-lines-table__price :deep(.p-inputtext) {
  min-width: 8rem;
  width: 100%;
}

.jr-lines-table__price :deep(.p-inputnumber-input) {
  font-variant-numeric: tabular-nums;
}

.jr-lines-table__disc {
  min-width: 5.75rem;
  width: 5.75rem;
}

.jr-lines-table__disc :deep(.p-inputnumber),
.jr-lines-table__disc :deep(.p-inputtext) {
  min-width: 5.25rem;
  width: 100%;
}

.jr-lines-table__disc :deep(.p-inputnumber-input) {
  font-variant-numeric: tabular-nums;
}

.jr-lines-table__product :deep(.p-select) {
  min-width: 0;
  width: 100%;
}

@media (min-width: 1024px) and (max-width: 1399.98px) {
  /* ThinkPad-class: Qty −1rem vs prior 7rem; Disc % reserved. */
  .jr-lines-table {
    min-width: 68rem;
  }

  .jr-lines-table__product {
    min-width: 16rem;
    width: 24%;
  }

  .jr-lines-table__qty {
    min-width: 7.25rem;
    width: 7.25rem;
  }

  .jr-lines-table__disc {
    min-width: 5.5rem;
    width: 5.5rem;
  }

  .jr-lines-table__price {
    min-width: 9rem;
    width: 9.5rem;
  }
}

.jr-lines-table__serial,
.jr-lines-sheet__badge {
  margin-top: 0.35rem;
}

.jr-lines-hint {
  margin: 0.25rem 0 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-lines-sheet {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.jr-lines-sheet__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.jr-lines-sheet__total {
  margin: 0.25rem 0 0;
  font-size: 0.9375rem;
  color: var(--color-jr-text);
}

.jr-lines-sheet__footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
}
</style>

<style>
.p-drawer.jr-lines-drawer {
  width: min(28rem, 100vw);
}

@media (max-width: 767.98px) {
  .p-drawer.jr-lines-drawer {
    width: 100vw;
    max-width: 100vw;
  }
}
</style>
