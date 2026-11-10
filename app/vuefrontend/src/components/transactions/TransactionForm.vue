<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" :description="pageDescription">
      <template v-if="statusBadgeVisible" #title-end>
        <button
          type="button"
          class="jr-tx-form__status-badge-btn"
          :aria-expanded="statusDrawerOpen ? 'true' : 'false'"
          aria-controls="jr-doc-status-drawer"
          :aria-label="
            $t('transactions.form.openStatusPanel', { label: statusBadgeLabel })
          "
          @click="openStatusDrawer">
          <JRBadge
            :value="statusBadgeLabel"
            :severity="statusBadgeSeverity" />
        </button>
      </template>
      <template #actions>
        <JRButton
          v-if="statusDrawerTriggerVisible"
          type="button"
          size="sm"
          :variant="statusDrawerOpen ? 'primary' : 'secondary'"
          :aria-expanded="statusDrawerOpen ? 'true' : 'false'"
          aria-controls="jr-doc-status-drawer"
          @click="openStatusDrawer">
          <svg
            class="jr-tx-form__status-drawer-icon"
            width="18"
            height="18"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true">
            <rect x="1.75" y="2" width="12.5" height="12" rx="0" />
            <line x1="10.5" y1="2" x2="10.5" y2="14" />
            <path
              d="M10.5 2H14.25V14H10.5Z"
              :fill="statusDrawerOpen ? 'currentColor' : 'transparent'"
              :opacity="statusDrawerOpen ? '0.35' : '0'"
              stroke="none" />
          </svg>
          {{ statusTriggerLabel }}
        </JRButton>
        <JRButton
          v-if="
            isViewMode &&
            idParam &&
            hasPermission('apptransactions.change_document')
          "
          variant="primary"
          size="sm"
          @click="goToEdit">
          {{ $t('transactions.form.editTransaction') }}
        </JRButton>
      </template>
    </JRPageHeader>

    <form class="jr-tx-form" @submit.prevent="handleSubmit" novalidate>
      <div
        v-if="formBannerMessage"
        ref="formBanner"
        class="jr-form-banner"
        role="alert"
        tabindex="-1">
        {{ formBannerMessage }}
      </div>

      <p v-if="loadingDocument" class="jr-tx-form__loading" role="status">
        {{ $t('transactions.form.loadingDocument') }}
      </p>

      <JRSection
        v-if="!loadingDocument"
        :title="$t('transactions.form.sectionDocument')">
        <template #actions>
          <JRCheckbox
            class="jr-tx-form__doc-active"
            v-model="form.is_active"
            inputId="tx-is-active"
            :label="
              form.is_active ? $t('common.active') : $t('common.voided')
            "
            :disabled="isReadOnly" />
        </template>
        <div class="jr-form-grid jr-form-grid--document">
          <JRField
            v-slot="{ describedby }"
            :label="$t('transactions.form.documentType')"
            required
            inputId="tx-document-type"
            :error="fieldError('document_type')">
            <DocumentTypeSelector
              inputId="tx-document-type"
              v-model="form.document_type"
              :error="errors.document_type"
              :required="true"
              :disabled="isReadOnly"
              :ariaDescribedby="describedby" />
          </JRField>

          <JRField
            v-if="isFromSchedule && workAccountTitle"
            :label="$t('transactions.form.workAccount')"
            inputId="tx-work-account-ro"
            :hint="$t('transactions.form.workAccountFromScheduleHint')">
            <p class="jr-tx-form__readonly" id="tx-work-account-ro">
              {{ workAccountTitle }}
            </p>
          </JRField>

          <JRField
            v-else-if="!isOperationalDocument && !isFromSchedule"
            v-slot="{ describedby }"
            :label="$t('transactions.form.party')"
            inputId="tx-party"
            :error="fieldError('builder')">
            <BuilderSelector
              inputId="tx-party"
              v-model="form.builder"
              :error="errors.builder"
              :disabled="isReadOnly"
              :ariaDescribedby="describedby" />
          </JRField>

          <JRField
            v-else-if="isOperationalDocument && !isFromSchedule"
            v-slot="{ describedby }"
            :label="$t('transactions.form.workAccount')"
            inputId="tx-work-account"
            :error="fieldError('work_account')">
            <WorkAccountSelector
              inputId="tx-work-account"
              v-model="form.work_account"
              :showLabel="false"
              :error="errors.work_account"
              :disabled="isReadOnly"
              :ariaDescribedby="describedby" />
          </JRField>

          <JRField
            v-slot="{ describedby, invalid }"
            :label="$t('common.date')"
            required
            inputId="tx-date"
            :error="fieldError('date')">
            <JRDatePicker
              inputId="tx-date"
              :modelValue="isoToDate(form.date)"
              :disabled="isReadOnly"
              :invalid="invalid"
              :placeholder="$t('transactions.form.selectDate')"
              @update:modelValue="onDateChange" />
          </JRField>
        </div>
        <Message
          v-if="!form.is_active"
          class="jr-tx-form__info jr-tx-form__info--voided"
          severity="warn"
          :closable="false">
          {{ $t('transactions.form.voidedIgnoredReports') }}
        </Message>
      </JRSection>

      <JRSection
        v-if="!loadingDocument && !isViewMode"
        :title="$t('transactions.form.sectionImportFavorites')">
        <div class="jr-form-grid jr-form-grid--import">
          <div class="jr-tx-form__import-col jr-tx-form__import-col--favorites">
            <JRField
              :label="$t('transactions.form.addToFavorites')"
              inputId="tx-add-favorite"
              :hint="$t('transactions.form.favoritesMinLinesHint')">
              <JRButton
                type="button"
                variant="secondary"
                size="sm"
                class="jr-tx-form__fav-btn"
                :disabled="!canSaveAsFavorite"
                @click="openFavoriteModal">
                <Star class="jr-tx-form__fav-star" aria-hidden="true" />
                {{ $t('transactions.form.saveAsFavorite') }}
              </JRButton>
            </JRField>

            <div class="jr-tx-form__favorites">
              <JRField
                :label="$t('transactions.form.importFavorite')"
                inputId="favorite-transaction-select">
                <FavoriteTransactionSelector
                  ref="favoriteSelectorRef"
                  inputId="favorite-transaction-select"
                  v-model="selectedFavoriteId"
                  :is-edit-mode="isEditMode"
                  @favorite-selected="onFavoriteSelected"
                  @edit-favorite="onEditFavorite" />
              </JRField>
              <JRButton
                v-if="selectedFavoriteId && !isEditMode"
                type="button"
                variant="secondary"
                size="sm"
                class="jr-tx-form__update-fav"
                :disabled="!canUpdateFavorite"
                @click="updateFavoriteFromCurrentTransaction">
                {{ $t('transactions.form.updateFavorite') }}
              </JRButton>
            </div>
          </div>

          <div class="jr-tx-form__import-col jr-tx-form__import-col--excel">
            <JRField
              :label="$t('transactions.form.importFromExcel')"
              inputId="tx-excel-import"
              :hint="
                hasInventoryProducts
                  ? $t('transactions.form.excelImportHint')
                  : ''
              ">
              <JRCheckbox
                v-model="showExcelImportPanel"
                inputId="tx-excel-import"
                :ariaLabel="$t('transactions.form.importFromExcel')"
                :disabled="inventoryProductsLoading || !hasInventoryProducts" />
              <Message
                v-if="!inventoryProductsLoading && !hasInventoryProducts"
                class="jr-tx-form__info"
                severity="info"
                :closable="false">
                {{ $t('transactions.form.excelRequiresProducts') }}
              </Message>
            </JRField>

            <TransactionLinesExcelPanel
              v-if="hasInventoryProducts && showExcelImportPanel"
              class="jr-tx-form__excel"
              :units-options="unitsOptions"
              :warehouses-options="warehousesOptions"
              :price-types-options="priceTypesOptions"
              :brands-options="brandsOptions"
              @import-lines="onTransactionLinesImported" />
          </div>
        </div>
      </JRSection>

      <JRSection
        v-if="!loadingDocument"
        :title="$t('transactions.form.sectionLines')">
        <Message
          v-if="linesGridDisabled && !isViewMode"
          class="jr-tx-form__info"
          severity="info"
          :closable="false">
          {{ $t('transactions.form.linesDisabledHint') }}
        </Message>
        <div class="jr-tx-form__lines">
          <LinesGrid
            ref="linesGridRef"
            :disabled="linesGridDisabled"
            :lines="lines"
            @update:lines="lines = $event"
            :document-id="idParam"
            :document-type-creates-serialized-items="
              currentDocumentTypeCreatesSerializedItems
            "
            :documentTypeId="form.document_type"
            :document-type-is-sales="currentDocumentTypeIsSales"
            :workAccountId="form.work_account"
            :unitsOptions="unitsOptions || []"
            :warehousesOptions="warehousesOptions || []"
            :priceTypesOptions="priceTypesOptions || []"
            :brandsOptions="brandsOptions || []"
            :merge-duplicates="true"
            @recalc="syncTotals"
            @open-asset-tags="openAssetTagModalFromGrid" />
        </div>
      </JRSection>

      <JRSection
        v-if="!loadingDocument"
        :title="$t('transactions.form.sectionTotals')">
        <div class="jr-tx-form__totals-wrap">
          <dl class="jr-tx-form__totals">
            <div class="jr-tx-form__totals-row">
              <dt>{{ $t('transactions.form.subtotal') }}</dt>
              <dd>{{ currency(subtotal_gross) }}</dd>
            </div>
            <div class="jr-tx-form__totals-row">
              <dt>{{ $t('transactions.form.totalDiscount') }}</dt>
              <dd class="jr-tx-form__totals-discount">
                −{{ currency(total_discount) }}
              </dd>
            </div>
            <div class="jr-tx-form__totals-row jr-tx-form__totals-row--grand">
              <dt>{{ $t('transactions.form.grandTotal') }}</dt>
              <dd>{{ currency(grand_total) }}</dd>
            </div>
            <div
              v-if="currentDocumentTypeIsSales"
              class="jr-tx-form__totals-row jr-tx-form__totals-row--profit">
              <dt>
                {{ $t('transactions.form.estimatedProfit') }}
                <span class="jr-tx-form__totals-hint">
                  {{ $t('transactions.form.estimatedProfitHint') }}
                </span>
              </dt>
              <dd
                :class="
                  estimated_sale_profit >= 0
                    ? 'jr-tx-form__totals-ok'
                    : 'jr-tx-form__totals-bad'
                ">
                {{ currency(estimated_sale_profit) }}
              </dd>
            </div>
          </dl>

          <JRField
            class="jr-tx-form__notes"
            v-slot="{ describedby, invalid }"
            :label="$t('transactions.form.notes')"
            inputId="tx-notes"
            :error="fieldError('notes')">
            <JRTextarea
              inputId="tx-notes"
              :modelValue="form.notes"
              :rows="2"
              :placeholder="$t('transactions.form.notesPlaceholder')"
              :disabled="isReadOnly"
              :invalid="invalid"
              :ariaDescribedby="describedby"
              @update:modelValue="form.notes = ($event || '').trim()" />
          </JRField>
        </div>
      </JRSection>

      <div v-if="!loadingDocument" class="jr-tx-form__actions">
        <JRButton
          v-if="!isViewMode"
          type="submit"
          variant="primary"
          :disabled="formBusy">
          {{ saveButtonLabel }}
        </JRButton>
        <JRButton
          v-if="!isEditMode && !isViewMode"
          type="button"
          variant="secondary"
          :disabled="formBusy"
          @click="handleSaveAndAddAnother">
          {{ saveAndAddLabel }}
        </JRButton>
        <JRButton type="button" variant="secondary" @click="goBack">
          {{
            isViewMode ? $t('common.backToList') : $t('common.cancel')
          }}
        </JRButton>
      </div>
    </form>

    <AssetTagAssignmentModal
      :show="showAssetTagModal"
      :document-id="documentIdForAssetTagModal"
      :document-context="documentContextForAssetTagModal"
      @close="onAssetTagModalClose"
      @saved="onAssetTagModalSaved" />

    <TransactionFavoriteModal
      :visible="favoriteModalVisible"
      :transaction-data="currentTransactionData"
      :document-types-options="documentTypesOptions"
      :builders-options="buildersOptions"
      :work-accounts-options="workAccountsOptions"
      :is-edit-mode="favoriteModalEditMode"
      :favorite-to-edit="favoriteToEdit"
      @saved="onFavoriteSaved"
      @updated="onFavoriteUpdated"
      @deleted="onFavoriteDeleted"
      @update:visible="favoriteModalVisible = $event" />

    <JRDrawer
      id="jr-doc-status-drawer"
      class="jr-catalog-drawer"
      :visible="statusDrawerOpen"
      :header="statusDrawerHeader"
      position="right"
      @update:visible="statusDrawerOpen = $event">
      <DocumentStatusPanel
        v-if="statusDrawerOpen && idParam && documentUsesStatusTracking"
        :document-id="idParam"
        :document-type-id="form.document_type"
        :uses-status-tracking="documentUsesStatusTracking"
        :can-transition="hasPermission('apptransactions.view_document')"
        @update:tracking="onDocumentTrackingUpdate" />
    </JRDrawer>
  </JRPage>
</template>

<script setup>
import { getAccessToken } from '@/auth/tokenHelpers';
import {
  ref,
  reactive,
  computed,
  onMounted,
  watch,
  nextTick,
  getCurrentInstance,
  defineAsyncComponent,
  defineComponent,
  h,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import axios from "axios";
import Swal from "sweetalert2";
import i18n from "@/i18n";

import Message from "primevue/message";
import Star from "@primeicons/vue/star";
import LinesGrid from "@/components/transactions/LinesGrid.vue";
import DocumentTypeSelector from "@/components/transactions/DocumentTypeSelector.vue";
import BuilderSelector from "@/components/parties/BuilderSelector.vue";
import WorkAccountSelector from "@/components/transactions/WorkAccountSelector.vue";
import TransactionFavoriteModal from "@/components/transactions/TransactionFavoriteModal.vue";
import AssetTagAssignmentModal from "@/components/transactions/AssetTagAssignmentModal.vue";
import FavoriteTransactionSelector from "@/components/transactions/FavoriteTransactionSelector.vue";
import DocumentStatusPanel from "@/components/transactions/DocumentStatusPanel.vue";
import { documentStatusSeverity } from "@/utils/documentStatus";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRButton,
  JRBadge,
  JRCheckbox,
  JRDatePicker,
  JRDrawer,
  JRTextarea,
} from "@ui";

const ExcelPanelLoading = defineComponent({
  name: "ExcelPanelLoading",
  setup() {
    return () =>
      h(
        "p",
        {
          class: "jr-tx-form__loading",
          role: "status",
        },
        i18n.global.t("transactions.form.loadingExcelImport")
      );
  },
});

const TransactionLinesExcelPanel = defineAsyncComponent({
  loader: () =>
    import("@/components/transactions/TransactionLinesExcelPanel.vue"),
  loadingComponent: ExcelPanelLoading,
  delay: 0,
  timeout: 60000,
});

const route = useRoute();
const router = useRouter();
const { t } = useI18n({ useScope: "global" });
const { proxy } = getCurrentInstance();

/** Local calendar date as YYYY-MM-DD (avoids UTC shift from toISOString). */
function todayLocalISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/** Keep API date as YYYY-MM-DD without timezone conversion. */
function toDateInputValue(value) {
  if (!value) return todayLocalISO();
  if (typeof value === "string") {
    const match = value.match(/^(\d{4}-\d{2}-\d{2})/);
    if (match) return match[1];
  }
  return todayLocalISO();
}

const idParam = route.query.id ? Number(route.query.id) : null;
// Leer work_account_id de query params (como en contracts)
const workAccountParam = route.query.work_account_id
  ? Number(route.query.work_account_id)
  : route.query.work_account
  ? Number(route.query.work_account)
  : null; // Fallback para compatibilidad
const isViewMode = computed(() => route.query.mode === "view");
const isEditMode = computed(() => !!idParam && !isViewMode.value);
const submitting = ref(false);
const loadingDocument = ref(!!idParam);
const formBusy = computed(() => submitting.value || loadingDocument.value);
const isReadOnly = computed(() => isViewMode.value || loadingDocument.value);

const pageTitle = computed(() => {
  if (isViewMode.value) return t("transactions.form.viewTitle");
  if (isEditMode.value) return t("transactions.form.editTitle");
  return t("transactions.form.newTitle");
});

const pageDescription = computed(() => {
  if (isViewMode.value) return t("transactions.form.viewDescription");
  if (isEditMode.value) return t("transactions.form.editDescription");
  return t("transactions.form.newDescription");
});

const documentUsesStatusTracking = ref(false);
const documentTracking = ref(null);
const statusDrawerOpen = ref(false);

const statusBadgeVisible = computed(
  () =>
    !!idParam &&
    documentUsesStatusTracking.value &&
    !!documentTracking.value?.status_name
);
const statusBadgeLabel = computed(
  () => documentTracking.value?.status_name || ""
);
const statusBadgeSeverity = computed(() =>
  documentStatusSeverity(documentTracking.value?.status_code, {
    isTerminal: !!documentTracking.value?.is_terminal,
  })
);
const statusDrawerTriggerVisible = computed(
  () => !!idParam && documentUsesStatusTracking.value
);
const statusTriggerLabel = computed(
  () => documentTracking.value?.status_name || t("transactions.form.statusDefault")
);
const statusDrawerHeader = computed(() => {
  const name = documentTracking.value?.status_name;
  return name
    ? t("transactions.form.statusDrawerHeaderNamed", { name })
    : t("transactions.form.statusDrawerHeader");
});

function openStatusDrawer() {
  statusDrawerOpen.value = true;
}

function onDocumentTrackingUpdate(tracking) {
  documentTracking.value = tracking;
  if (tracking) documentUsesStatusTracking.value = true;
}

async function loadDocumentStatus(documentId) {
  if (!documentId) {
    documentTracking.value = null;
    return;
  }
  try {
    const { data } = await axios.get(`/api/documents/${documentId}/status/`);
    documentTracking.value = data;
    documentUsesStatusTracking.value = true;
  } catch (err) {
    documentTracking.value = null;
    if (err?.response?.status === 404) {
      documentUsesStatusTracking.value = !!err.response?.data?.uses_status_tracking;
      return;
    }
    // Keep uses_status_tracking from document payload when status read fails.
  }
}

const saveButtonLabel = computed(() => {
  if (loadingDocument.value) return t("transactions.form.loadingEllipsis");
  if (submitting.value) return t("common.saving");
  return isEditMode.value ? t("common.update") : t("common.save");
});

const saveAndAddLabel = computed(() => {
  if (loadingDocument.value) return t("transactions.form.loadingEllipsis");
  if (submitting.value) return t("common.saving");
  return t("common.saveAndAddAnother");
});

function fieldErrorLabels() {
  return {
    document_type: t("transactions.form.documentType"),
    builder: t("transactions.form.party"),
    work_account: t("transactions.form.workAccount"),
    date: t("common.date"),
    notes: t("transactions.form.notes"),
    detail: t("common.error"),
    non_field_errors: t("common.error"),
  };
}

function formatErrorValue(val) {
  if (val == null || val === "") return "";
  if (typeof val === "string") return val;
  if (Array.isArray(val)) return formatErrorValue(val[0]);
  if (typeof val === "object") {
    if (val.message != null) return formatErrorValue(val.message);
    if (val.string != null) return String(val.string);
    if (val.detail != null) return formatErrorValue(val.detail);
    if (
      val.error_type === "insufficient_stock" ||
      val.error_type?.string === "insufficient_stock"
    ) {
      const productName = val.product_name?.string ?? val.product_name;
      const available = val.available?.string ?? val.available;
      const requested = val.requested?.string ?? val.requested;
      if (available != null && requested != null) {
        const prefix = productName ? `${productName}: ` : "";
        return `${prefix}Insufficient stock (available: ${available}, requested: ${requested})`;
      }
    }
    try {
      return JSON.stringify(val);
    } catch {
      return "Invalid value";
    }
  }
  return String(val);
}

function collectValidationSummary(errData) {
  const parts = [];
  if (!errData || typeof errData !== "object" || Array.isArray(errData)) {
    return parts;
  }
  for (const [key, label] of Object.entries(fieldErrorLabels())) {
    if (key === "lines") continue;
    if (errData[key] == null || errData[key] === "") continue;
    const msg = formatErrorValue(errData[key]);
    if (msg) parts.push(`${label}: ${msg}`);
  }
  for (const key of Object.keys(errData)) {
    if (key === "lines" || fieldErrorLabels()[key]) continue;
    const msg = formatErrorValue(errData[key]);
    if (msg) parts.push(`${key}: ${msg}`);
  }
  const lineErrors = errData.lines;
  const pushLine = (item, idx) => {
    if (!item || (typeof item === "object" && !Object.keys(item).length)) return;
    if (typeof item !== "object") {
      const msg = formatErrorValue(item);
      if (msg) parts.push(`Line ${idx + 1}: ${msg}`);
      return;
    }
    Object.entries(item).forEach(([field, val]) => {
      const msg = formatErrorValue(val);
      if (msg) parts.push(`Line ${idx + 1} · ${field}: ${msg}`);
    });
  };
  if (Array.isArray(lineErrors)) {
    lineErrors.forEach((item, idx) => pushLine(item, idx));
  } else if (lineErrors && typeof lineErrors === "object") {
    Object.entries(lineErrors).forEach(([key, item]) => {
      const idx = parseInt(key, 10);
      pushLine(item, Number.isFinite(idx) ? idx : 0);
    });
  }
  return parts;
}

const formBannerMessage = computed(() => {
  const summary = collectValidationSummary(errors);
  const lineHits = (lines.value || []).filter(
    (l) => l?._errors && Object.keys(l._errors).length > 0
  ).length;
  if (lineHits && !summary.some((s) => s.startsWith("Line "))) {
    summary.push(
      t("transactions.form.linesNeedAttention", { count: lineHits })
    );
  }
  return summary.filter(Boolean).join(" · ");
});

function hasPermission(permission) {
  return !!proxy?.hasPermission?.(permission);
}

function fieldError(key) {
  const value = errors[key];
  if (!value) return "";
  return formatErrorValue(value);
}

async function focusFirstValidationIssue() {
  await nextTick();
  const banner = formBanner.value;
  if (banner && formBannerMessage.value) {
    try {
      banner.focus?.({ preventScroll: false });
      banner.scrollIntoView?.({ behavior: "smooth", block: "nearest" });
    } catch {
      /* ignore */
    }
  }
  const root = banner?.closest?.("form") || document.querySelector(".jr-tx-form");
  const target =
    root?.querySelector?.(
      ".jr-field__error, .jr-lines-table__row--error, .jr-lines-item--error, .p-invalid"
    ) || null;
  if (target?.scrollIntoView) {
    target.scrollIntoView({ behavior: "smooth", block: "center" });
  }
}

function isoToDate(value) {
  if (!value) return null;
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value;
  const text = String(value).slice(0, 10);
  const parts = text.split("-").map(Number);
  if (parts.length !== 3 || parts.some((n) => Number.isNaN(n))) return null;
  const [year, month, day] = parts;
  const date = new Date(year, month - 1, day);
  return Number.isNaN(date.getTime()) ? null : date;
}

function dateToIso(value) {
  if (!value) return todayLocalISO();
  if (typeof value === "string") {
    const match = value.match(/^(\d{4}-\d{2}-\d{2})/);
    if (match) return match[1];
  }
  if (!(value instanceof Date) || Number.isNaN(value.getTime())) return todayLocalISO();
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function onDateChange(value) {
  form.date = dateToIso(value);
}

function goToEdit() {
  if (!idParam) return;
  router.push({ name: "transactions-form", query: { id: idParam } }).catch(() => {});
}
/** Muestra el panel de importación Excel solo si el usuario lo activa (carga diferida del chunk) */
const showExcelImportPanel = ref(false);
const loading = reactive({
  units: false,
  whs: false,
  priceTypes: false,
  brands: false,
});
// Variable para almacenar el título del work account cuando viene desde el schedule
const workAccountTitle = ref(null);
const showAssetTagModal = ref(false);
const documentIdForAssetTagModal = ref(null);
const documentContextForAssetTagModal = ref({});
const assetTagModalOpenedFromSave = ref(false);
// Computed para saber si viene desde el schedule (tiene workAccountParam en query)
const isFromSchedule = computed(() => !!workAccountParam);
// Header form
const form = reactive({
  document_type: null,
  builder: null,
  work_account: workAccountParam, // Prellenar desde query params si está disponible
  date: todayLocalISO(), // default today only for new documents
  notes: "",
  created_by: null, // opcional, normalmente lo setea el backend desde request.user
  is_active: true,
});

// Lines (v-model in child) - Initialize with one empty line
const lines = ref([
  {
    __key: "initial",
    selected: false,
    id: null,
    product: null,
    product_label: "",
    quantity: 1,
    unit: null,
    unit_price: 0,
    discount_percentage: 0,
    final_price: 0,
    warehouse: null,
    price_type: null,
    brand: null,
    _errors: {},
  },
]);

// Options for selects
const unitsOptions = ref([]);
const warehousesOptions = ref([]);
const priceTypesOptions = ref([]);
const brandsOptions = ref([]);
/** Catálogo con al menos un producto activo (para habilitar import Excel) */
const hasInventoryProducts = ref(false);
/** true hasta que termine GET /api/products/ — el switch se pinta de inmediato, deshabilitado mientras carga */
const inventoryProductsLoading = ref(true);

const errors = reactive({});

function currency(n) {
  const num = Number(n || 0);
  return num.toLocaleString("en-US", { style: "currency", currency: "USD" });
}

function cryptoRandom() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

/** Igual que LinesGrid.maybeMergeDuplicate: mismo product + unit + brand → sumar cantidades (ids normalizados). */
function lineMergeScalar(v) {
  if (v == null || v === "") return null;
  if (typeof v === "object" && v !== null && "id" in v) return v.id;
  return v;
}

function lineMergeKeyPart(v) {
  const x = lineMergeScalar(v);
  if (x == null || x === "") return null;
  return String(x);
}

function transactionLinesDuplicateMatch(a, b) {
  return (
    !!a?.product &&
    !!b?.product &&
    lineMergeKeyPart(a.product) === lineMergeKeyPart(b.product) &&
    lineMergeKeyPart(a.unit) === lineMergeKeyPart(b.unit) &&
    lineMergeKeyPart(a.brand) === lineMergeKeyPart(b.brand)
  );
}

/** Unifica líneas como al elegir producto en el grid con mergeDuplicates (primera fila gana orden). */
function mergeDuplicateTransactionLines(rows) {
  const out = [];
  for (const row of rows) {
    if (!row?.product) {
      out.push(row);
      continue;
    }
    const existing = out.find((o) => transactionLinesDuplicateMatch(o, row));
    if (existing) {
      existing.quantity =
        Number(existing.quantity || 0) + Number(row.quantity || 0);
      if (row.__favoriteImportReprice) {
        existing.__favoriteImportReprice = true;
      }
      if (!existing.product_image && row.product_image) {
        existing.product_image = row.product_image;
      }
    } else {
      out.push(row);
    }
  }
  return out;
}

/** Σ (qty × unit_price) antes de descuentos por línea */
const subtotal_gross = computed(() =>
  lines.value.reduce(
    (sum, l) => sum + Number(l.quantity || 0) * Number(l.unit_price || 0),
    0
  )
);

/** Σ importe descontado por línea (coincide con backend Document.calculate_totals) */
const total_discount = computed(() =>
  lines.value.reduce((sum, l) => {
    const disc =
      Number(l.unit_price || 0) *
      Number(l.quantity || 0) *
      (Number(l.discount_percentage || 0) / 100);
    return sum + disc;
  }, 0)
);

/** Total del documento: Σ final_price por línea (= subtotal_gross − total_discount salvo redondeo por línea) */
const grand_total = computed(() =>
  lines.value.reduce((sum, l) => sum + Number(l.final_price || 0), 0)
);

/** Costo estimado: Σ qty × _purchase_unit_cost donde el costo unitario es conocido */
const estimated_total_purchase_cost = computed(() =>
  lines.value.reduce((sum, l) => {
    if (!l.product) return sum;
    const c = Number(l._purchase_unit_cost);
    if (!Number.isFinite(c) || c < 0) return sum;
    return sum + Number(l.quantity || 0) * c;
  }, 0)
);

/** Beneficio aprox. (frontend): grand_total − costo estimado; la fila del total la muestra solo si es venta */
const estimated_sale_profit = computed(
  () => grand_total.value - estimated_total_purchase_cost.value
);

// Computed para determinar si el documento es operacional
const isOperationalDocument = computed(() => {
  if (!form.document_type) return false;
  // Buscar el document type en las opciones para obtener is_operational
  const docType = documentTypesOptions.value.find(
    (dt) => dt.value === form.document_type
  );
  return docType?.is_operational || false;
});

// Opciones de document types para acceder a is_operational
const documentTypesOptions = ref([]);

const currentDocumentTypeCreatesSerializedItems = computed(() => {
  const dt = documentTypesOptions.value.find(
    (d) => d.value === form.document_type
  );
  return !!dt?.creates_serialized_items;
});

const currentDocumentTypeIsSales = computed(() => {
  const dt = documentTypesOptions.value.find(
    (d) => d.value === form.document_type
  );
  return !!dt?.is_sales;
});

const excelImportSwitchTooltip = computed(() => {
  if (inventoryProductsLoading.value) {
    return "Checking product catalog…";
  }
  if (!hasInventoryProducts.value) {
    return "Import requires at least one active product in inventory.";
  }
  return "Show tools to download the template and import lines from Excel";
});

// Variables para favoritos
const selectedFavoriteId = ref(null);
const favoriteModalVisible = ref(false);
const favoriteModalEditMode = ref(false);
const favoriteToEdit = ref(null);
const favoriteSelectorRef = ref(null);
const linesGridRef = ref(null);
const formBanner = ref(null);
/** Permite usar la rejilla sin tipo de documento tras importar líneas desde un favorito */
const linesGridUnlockedByFavoriteImport = ref(false);
/** Índices UI de las líneas enviadas en el último submit (payload filtra vacías). */
const lastSubmittedLineIndexMap = ref([]);

const linesGridDisabled = computed(
  () =>
    isReadOnly.value ||
    (!form.document_type && !linesGridUnlockedByFavoriteImport.value)
);

// Opciones adicionales para los componentes
const buildersOptions = ref([]);
const workAccountsOptions = ref([]);

// Watcher para limpiar campos cuando cambie el tipo de documento
watch(
  () => form.document_type,
  (newDocType, oldDocType) => {
    if (newDocType !== oldDocType) {
      // Limpiar campos relacionados cuando cambie el tipo de documento
      form.builder = null;
      // NO limpiar work_account si viene desde el schedule (tiene workAccountParam)
      if (!isFromSchedule.value) {
        form.work_account = null;
      } else {
      }
    }
  }
);

// Watcher para debug work_account
watch(
  () => form.work_account,
  (newValue, oldValue) => {
  }
);

function syncTotals() {
  // placeholder in case we want extra side-effects; totals are computed above
}

async function loadHasInventoryProducts() {
  inventoryProductsLoading.value = true;
  try {
    const { data } = await axios.get("/api/products/", {
      params: { is_active: true, page_size: 1 },
    });
    const list = Array.isArray(data) ? data : data?.results || [];
    const count = typeof data?.count === "number" ? data.count : list.length;
    hasInventoryProducts.value = count > 0;
  } catch {
    hasInventoryProducts.value = false;
  } finally {
    inventoryProductsLoading.value = false;
  }
}

async function onTransactionLinesImported(newLines) {
  lines.value = newLines || [];
  syncTotals();
  await nextTick();
  try {
    if (
      linesGridRef.value?.hydrateImagesAfterImport &&
      typeof linesGridRef.value.hydrateImagesAfterImport === "function"
    ) {
      await linesGridRef.value.hydrateImagesAfterImport();
    }
  } catch (e) {
    console.warn("hydrateImagesAfterImport after Excel:", e);
  }
}

function countLinesWithProduct(rows) {
  return (rows || []).filter((line) => line?.product != null && line.product !== "").length;
}

// Favoritos: mínimo 2 líneas con producto (evita inconsistencias en el grid y refleja “kits”).
const canSaveAsFavorite = computed(() => {
  return (
    form.document_type &&
    countLinesWithProduct(lines.value) >= 2
  );
});

const canUpdateFavorite = computed(() => {
  return (
    selectedFavoriteId.value &&
    form.document_type &&
    countLinesWithProduct(lines.value) >= 2
  );
});

// Computed para obtener datos actuales de la transacción
const currentTransactionData = computed(() => {
  return {
    document_type: form.document_type,
    builder: form.builder,
    work_account: form.work_account,
    date: form.date,
    notes: form.notes,
    is_active: form.is_active,
    lines: lines.value.filter((line) => line.product), // Solo líneas con producto
  };
});

// Funciones para manejar favoritos
function openFavoriteModal() {
  favoriteModalEditMode.value = false;
  favoriteToEdit.value = null;
  favoriteModalVisible.value = true;
}

async function onFavoriteSelected(favoriteData) {
  if (!favoriteData) {
    // Limpiar selección
    selectedFavoriteId.value = null;
    return;
  }

  const incomingRaw =
    favoriteData.lines_data && Array.isArray(favoriteData.lines_data)
      ? favoriteData.lines_data
      : [];

  const importedLines = incomingRaw.map((line) => ({
    __key: cryptoRandom(),
    selected: false,
    id: null, // Nueva línea, no ID
    product: line.product,
    product_label: line.product_label || line.product_name || "",
    product_image: line.product_image || "",
    quantity: line.quantity || 1,
    unit: line.unit,
    // Precios desde JSON pueden estar desfasados — se reprecian con reglas vigentes antes de usar
    unit_price: line.unit_price ?? 0,
    discount_percentage: line.discount_percentage ?? 0,
    final_price: line.final_price ?? 0,
    warehouse: line.warehouse,
    price_type: line.price_type,
    brand: line.brand ?? null,
    brands: Array.isArray(line.brands) ? line.brands : [],
    pricing_rule: line.pricing_rule ?? null,
    margin_percent: line.margin_percent ?? null,
    price_manually_edited: false,
    _purchase_unit_cost: line._purchase_unit_cost ?? null,
    _suppressPriceEvent: false,
    __favoriteImportReprice: true,
    _errors: {},
  }));

  const hasExistingLineProducts = lines.value.some((line) => line.product);
  const hasIncomingLines = importedLines.length > 0;

  /** Si true: se concatenan líneas; si false: se reemplazan. Nunca se toca el encabezado. */
  let appendLinesOnly = false;

  if (hasExistingLineProducts && hasIncomingLines) {
    const result = await Swal.fire({
      title: t("transactions.form.swalLinesAlreadyLoadedTitle"),
      html: t("transactions.form.swalLinesAlreadyLoadedHtml"),
      icon: "question",
      showCancelButton: true,
      showDenyButton: true,
      confirmButtonText: t("transactions.form.swalAddToExistingLines"),
      denyButtonText: t("transactions.form.swalReplaceAllLines"),
      cancelButtonText: t("common.cancel"),
      confirmButtonColor: "#16a34a",
      denyButtonColor: "#4b5563",
      cancelButtonColor: "#d1d5db",
      reverseButtons: true,
    });

    if (result.isDismissed) {
      selectedFavoriteId.value = null;
      return;
    }
    appendLinesOnly = Boolean(result.isConfirmed);
  }

  // Import favorite: solo líneas — no Document Type / Work Account / Date / Party / notes
  if (hasIncomingLines) {
    if (appendLinesOnly) {
      const combined = [...lines.value, ...importedLines];
      lines.value = mergeDuplicateTransactionLines(combined);
    } else {
      lines.value = importedLines;
    }
  }

  if (hasIncomingLines) {
    await nextTick();
    try {
      if (
        linesGridRef.value?.rehydratePricingAfterFavoriteImport &&
        typeof linesGridRef.value.rehydratePricingAfterFavoriteImport ===
          "function"
      ) {
        await linesGridRef.value.rehydratePricingAfterFavoriteImport();
      }
    } catch (e) {
      console.error("❌ Rehydrate pricing after favorite import:", e);
    }
  }

  syncTotals();

  linesGridUnlockedByFavoriteImport.value =
    !!form.document_type || hasIncomingLines;

}

function onEditFavorite(favoriteData) {
  favoriteModalEditMode.value = true;
  favoriteToEdit.value = favoriteData;
  favoriteModalVisible.value = true;
}

function onFavoriteSaved(favorite) {
  // Refrescar el selector de favoritos para mostrar el nuevo favorito
  refreshFavoriteSelector();
}

function onFavoriteUpdated(favorite) {
  // Opcional: mostrar mensaje de éxito o actualizar UI
}

function onFavoriteDeleted(favoriteId) {
  // Limpiar selección si el favorito eliminado estaba seleccionado
  if (selectedFavoriteId.value === favoriteId) {
    selectedFavoriteId.value = null;
  }

  // Refrescar el selector de favoritos
  refreshFavoriteSelector();
}

// Función para refrescar el selector de favoritos
function refreshFavoriteSelector() {
  if (
    favoriteSelectorRef.value &&
    typeof favoriteSelectorRef.value.loadFavorites === "function"
  ) {
    favoriteSelectorRef.value.loadFavorites(true); // Forzar recarga
  }
}

// Función para actualizar favorito con datos de transacción actual
async function updateFavoriteFromCurrentTransaction() {
  if (!selectedFavoriteId.value) {
    console.warn("No favorite selected for update");
    return;
  }

  try {
    const updateData = {
      document_data: {
        document_type: form.document_type,
        builder: form.builder,
        work_account: form.work_account,
        date: form.date,
        notes: form.notes,
        is_active: form.is_active,
      },
      lines_data: lines.value
        .filter((line) => line.product) // Solo líneas con producto
        .map((line) => ({
          product: line.product,
          product_label: line.product_label || "",
          quantity: line.quantity || 1,
          unit: line.unit,
          unit_price: line.unit_price || 0,
          discount_percentage: line.discount_percentage || 0,
          final_price: line.final_price || 0,
          warehouse: line.warehouse,
          price_type: line.price_type,
          brand: line.brand,
        })),
    };

    const response = await axios.post(
      `/api/transaction-favorites/${selectedFavoriteId.value}/update-from-transaction/`,
      updateData
    );

    if (response.status === 200) {
      await Swal.fire({
        icon: "success",
        title: t("transactions.form.swalFavoriteUpdatedTitle"),
        text: t("transactions.form.swalFavoriteUpdatedText"),
        timer: 2000,
        showConfirmButton: false,
      });

    }
  } catch (error) {
    console.error("❌ Error updating favorite:", error);

    await Swal.fire({
      icon: "error",
      title: t("transactions.form.swalUpdateFailedTitle"),
      text: t("transactions.form.swalUpdateFailedText"),
      confirmButtonText: t("common.ok"),
    });
  }
}

function goBack() {
  router.push({ name: "transactions" }).catch(() => {});
}

// Función para resetear el formulario para una nueva transacción
function resetFormForNewTransaction() {
  // Resetear campos del formulario
  form.document_type = null;
  form.builder = null;
  form.work_account = null;
  form.date = todayLocalISO();
  form.notes = "";
  form.is_active = true;

  // Resetear líneas con una línea vacía
  lines.value = [
    {
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
      warehouse: null,
      price_type: null,
      brand: null,
      _errors: {},
    },
  ];

  // Limpiar errores
  clearErrors();

  // Limpiar selección de favorito
  selectedFavoriteId.value = null;
  linesGridUnlockedByFavoriteImport.value = false;
}

// Función para guardar y agregar otra transacción
async function handleSaveAndAddAnother() {
  if (formBusy.value) return;
  submitting.value = true;
  clearErrors();
  try {
    const payload = normalizePayload();

    const { data } = await axios.post("/api/documents/", payload);
    await Swal.fire({
      title: t("transactions.form.swalSavedTitle"),
      text: t("transactions.form.swalSavedAddAnotherText"),
      icon: "success",
      timer: 2000,
      showConfirmButton: false,
    });
    resetFormForNewTransaction();

  } catch (err) {
    console.error("❌ Error al guardar transacción:", err);

    const data = err?.response?.data;
    if (data) applyServerErrors(data);

    const summary = collectValidationSummary(data || errors);
    const errorTitle = t("common.validationError");
    const errorMessage =
      summary.length > 0
        ? `<div class="jr-pilot text-start"><p class="mb-2 text-sm">${t("transactions.form.swalReviewHighlightedListIntro")}</p><ul class="m-0 list-disc ps-4 text-sm">${summary
            .slice(0, 12)
            .map((s) => `<li>${s}</li>`)
            .join("")}${
            summary.length > 12 ? "<li>…</li>" : ""
          }</ul></div>`
        : t("transactions.form.swalReviewHighlightedFields");

    await Swal.fire({
      icon: "error",
      title: errorTitle,
      html: errorMessage,
      confirmButtonText: t("common.ok"),
    });
    await focusFirstValidationIssue();
  } finally {
    submitting.value = false;
  }
}

function openAssetTagModalFromGrid() {
  if (!idParam) return;
  assetTagModalOpenedFromSave.value = false;
  documentIdForAssetTagModal.value = idParam;
  const docType = documentTypesOptions.value.find(
    (d) => d.value === form.document_type
  );
  const builder = buildersOptions.value.find((b) => b.value === form.builder);
  documentContextForAssetTagModal.value = {
    id: idParam,
    document_type_code: docType?.type_code || "",
    builder_name: builder?.label || "",
    date: form.date,
  };
  showAssetTagModal.value = true;
}

function onAssetTagModalClose() {
  showAssetTagModal.value = false;
  const docId = documentIdForAssetTagModal.value;
  documentIdForAssetTagModal.value = null;
  documentContextForAssetTagModal.value = {};
  if (assetTagModalOpenedFromSave.value && docId) {
    assetTagModalOpenedFromSave.value = false;
    promptPrintAndRedirect(docId);
  }
}

function onAssetTagModalSaved() {
  proxy?.notifyToastSuccess?.(t("transactions.form.serialNumbersSaved"));
  onAssetTagModalClose();
}

// Prompt PDF and redirect (after save)
async function promptPrintAndRedirect(documentId) {
  const { value: shouldPrint } = await Swal.fire({
    title: t("transactions.form.swalSavedTitle"),
    text: t("transactions.form.swalPrintPromptText"),
    icon: "success",
    showCancelButton: true,
    confirmButtonColor: "#2563eb",
    cancelButtonColor: "#4b5563",
    confirmButtonText: t("common.yesPrint"),
    cancelButtonText: t("common.noContinue"),
    reverseButtons: true,
  });
  if (shouldPrint && documentId) {
    await downloadTransactionPDF(documentId);
  }
  router.push({ name: "transactions" }).catch(() => {});
}

// Función helper para detectar si es dispositivo móvil
function isMobileDevice() {
  return (
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    ) || window.innerWidth <= 768
  );
}

// Función para manejar PDF de transacción (abrir en nueva ventana o descargar)
async function downloadTransactionPDF(documentId) {
  try {
    const response = await axios.get(`/api/documents/${documentId}/pdf/`, {
      headers: {
        Authorization: `Bearer ${getAccessToken()}`,
      },
    });

    if (!response.data || !response.data.file) {
      throw new Error("No PDF file was returned from the server.");
    }

    // Decodificar base64 y crear blob
    const byteCharacters = atob(response.data.file);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: "application/pdf" });
    const url = window.URL.createObjectURL(blob);

    if (isMobileDevice()) {
      // En móvil: descargar directamente
      const link = document.createElement("a");
      link.href = url;
      link.download = response.data.filename || `transaction_${documentId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      // En desktop: abrir en nueva ventana
      const newWindow = window.open(url, "_blank");
      if (!newWindow) {
        // Si no se puede abrir nueva ventana (bloqueador de popups), descargar
        const link = document.createElement("a");
        link.href = url;
        link.download =
          response.data.filename || `transaction_${documentId}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    }

    // Limpiar la URL después de un tiempo
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 1000);

    return true;
  } catch (error) {
    console.error("Error al descargar PDF:", error);
    await Swal.fire({
      icon: "error",
      title: t("common.error"),
      text: t("transactions.form.swalPdfFailedText"),
      confirmButtonText: t("common.ok"),
    });
    return false;
  }
}

async function fetchStaticOptions() {
  // Document Types (necesario para is_operational)
  try {
    const { data } = await axios.get("/api/document-types/?is_active=true");
    const list = Array.isArray(data) ? data : data?.results || [];
    documentTypesOptions.value = list.map((dt) => ({
      value: dt.id,
      label: `${dt.type_code} — ${dt.description}`,
      type_code: dt.type_code,
      is_operational: dt.is_operational,
      creates_serialized_items: !!dt.creates_serialized_items,
      is_sales: !!dt.is_sales,
      is_purchase: !!dt.is_purchase,
    }));
  } catch (error) {
    console.error("Error loading document types:", error);
  }

  // Builders
  try {
    const { data } = await axios.get("/api/builder/?is_active=true");
    const list = Array.isArray(data) ? data : data?.results || [];
    buildersOptions.value = list.map((b) => ({
      value: b.id,
      label: b.name,
    }));
  } catch (error) {
    console.error("Error loading builders:", error);
  }

  // Work Accounts
  try {
    const { data } = await axios.get("/api/work-accounts/", {
      params: { active_only: true, page_size: 500 },
    });
    const list = Array.isArray(data) ? data : data?.results || [];
    workAccountsOptions.value = list.map((wa) => ({
      value: wa.id,
      label: wa.display || wa.title,
    }));
  } catch (error) {
    console.error("Error loading work accounts:", error);
  }

  // Units
  loading.units = true;
  try {
    const { data } = await axios.get("/api/unitsofmeasure/?is_active=true");
    const list = Array.isArray(data) ? data : data?.results || [];
    unitsOptions.value = list.map((u) => ({
      value: u.id,
      label: u.code,
      code: u.code,
      name: u.name || "",
    }));
  } finally {
    loading.units = false;
  }

  // Warehouses
  loading.whs = true;
  try {
    const { data } = await axios.get("/api/warehouses/?is_active=true");
    const list = Array.isArray(data) ? data : data?.results || [];
    warehousesOptions.value = list.map((w) => ({ value: w.id, label: w.name }));
  } finally {
    loading.whs = false;
  }

  // Price types
  loading.priceTypes = true;
  try {
    const { data } = await axios.get("/api/pricetypes/?is_active=true");
    const list = Array.isArray(data) ? data : data?.results || [];
    priceTypesOptions.value = list.map((pt) => ({
      value: pt.id,
      label: pt.name,
      pricing_method: pt.pricing_method || "NONE",
      margin_percent: pt.margin_percent,
    }));
  } finally {
    loading.priceTypes = false;
  }

  // Brands
  loading.brands = true;
  try {
    const { data } = await axios.get("/api/productbrand/?is_active=true");
    const list = Array.isArray(data) ? data : data?.results || [];
    brandsOptions.value = list.map((b) => ({ value: b.id, label: b.name }));
  } finally {
    loading.brands = false;
  }
}

async function loadDocument(id) {
  loadingDocument.value = true;
  try {
    const { data } = await axios.get(`/api/documents/${id}/`);
    documentUsesStatusTracking.value = !!data.uses_status_tracking;

    // Verificar que los datos relacionados existen
    if (!data.document_type) {
      console.warn("Document type not found, setting to null");
      form.document_type = null;
    } else {
      form.document_type = data.document_type;
    }

    if (!data.builder) {
      console.warn("Builder not found, setting to null");
      form.builder = null;
    } else {
      // Verificar que el builder existe antes de asignarlo
      try {
        await axios.get(`/api/builder/${data.builder}/`);
        form.builder = data.builder;
      } catch (error) {
        if (error.response?.status === 404) {
          console.warn(`Builder ${data.builder} not found, setting to null`);
          form.builder = null;
        } else {
          console.error("Error verifying builder:", error);
          form.builder = data.builder; // Asignar de todos modos si es otro tipo de error
        }
      }
    }

    if (!data.work_account) {
      form.work_account = null;
    } else {
      // Verificar que el work_account existe antes de asignarlo
      try {
        await axios.get(`/api/work-accounts/${data.work_account}/`);
        form.work_account = data.work_account;
      } catch (error) {
        if (error.response?.status === 404) {
          console.warn(
            `WorkAccount ${data.work_account} not found, setting to null`
          );
          form.work_account = null;
        } else {
          console.error("Error verifying work account:", error);
          form.work_account = data.work_account; // Asignar de todos modos si es otro tipo de error
        }
      }
    }

    // Edit/view: keep stored document date (do not reset to today).
    form.date = toDateInputValue(data.date);
    form.notes = data.notes || "";
    form.is_active = data.is_active;

    // Normalize incoming lines
    const normalizedLines = (data.lines || []).map((l) => {
      // Función helper para extraer ID de un valor (puede ser objeto o ID)
      function extractId(value) {
        if (value === null || value === undefined) return null;
        if (typeof value === "object" && value !== null) {
          return value.id || null;
        }
        return value;
      }

      const normalizedLine = {
        __key: l.id || cryptoRandom(),
        id: l.id,
        selected: false,
        product: extractId(l.product),
        product_label: l.product_name || "",
        product_image: l.product_image || "",
        quantity: l.quantity,
        unit: extractId(l.unit),
        unit_price: l.unit_price,
        discount_percentage: l.discount_percentage,
        final_price: l.final_price,
        warehouse: extractId(l.warehouse),
        price_type: extractId(l.price_type),
        brand: extractId(l.brand),
        pricing_rule: l.pricing_rule ?? null,
        margin_percent:
          l.margin_percent != null && l.margin_percent !== ""
            ? Number(l.margin_percent)
            : null,
        price_manually_edited: l.pricing_rule === "MANUAL",
        _purchase_unit_cost: null,
        _suppressPriceEvent: false,
        _errors: {},
      };

      // 🔍 DEBUG: Log de la línea cargada
      return normalizedLine;
    });

    // If no lines exist, add one empty line
    if (normalizedLines.length === 0) {
      normalizedLines.push({
        __key: cryptoRandom(),
        selected: false,
        id: null,
        product: null,
        product_label: "",
        product_image: "",
        quantity: 1,
        unit: null,
        unit_price: 0,
        discount_percentage: 0,
        final_price: 0,
        warehouse: null,
        price_type: null,
        brand: null,
        pricing_rule: null,
        margin_percent: null,
        price_manually_edited: false,
        _purchase_unit_cost: null,
        _suppressPriceEvent: false,
        _errors: {},
      });
    }

    lines.value = normalizedLines;
    if (data.uses_status_tracking) {
      await loadDocumentStatus(id);
    } else {
      documentTracking.value = null;
    }
  } catch (error) {
    console.error("Error loading document:", error);
    await Swal.fire({
      icon: "error",
      title: t("common.error"),
      text: t("transactions.form.swalDocumentNotFound"),
      confirmButtonText: t("common.ok"),
    });
    router.push({ name: "transactions" }).catch(() => {});
    return;
  } finally {
    loadingDocument.value = false;
  }
}

function normalizePayload() {
  // Si viene desde schedule y form.work_account es null, usar workAccountParam como fallback
  let workAccountToUse = form.work_account;
  if (
    isFromSchedule.value &&
    (!workAccountToUse || workAccountToUse === null)
  ) {
    console.warn(
      "⚠️ form.work_account es null pero viene desde schedule, usando workAccountParam:",
      workAccountParam
    );
    workAccountToUse = workAccountParam;
    form.work_account = workAccountParam; // Restaurar el valor
  }

  // Para documentos operacionales, obtener el builder del work_account
  let builderToSend = form.builder;
  if (isOperationalDocument.value && workAccountToUse && !form.builder) {
    // Si es operacional y tenemos work_account pero no builder,
    // necesitamos obtener el builder del work_account
    // Esto se manejará en el backend automáticamente
    builderToSend = null; // El backend lo resolverá desde work_account
  }

  // Función helper para extraer ID de un valor (puede ser objeto o ID)
  function extractId(value) {
    if (value === null || value === undefined) return null;
    if (typeof value === "object" && value !== null) {
      return value.id || null;
    }
    return value;
  }

  const workAccountId = extractId(workAccountToUse);

  /** Round to 2 dp and return a decimal string so JSON never reintroduces float noise. */
  function money2(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return "0.00";
    return (Math.round((n + Number.EPSILON) * 100) / 100).toFixed(2);
  }

  // Solo líneas con producto; mapear índices payload → UI para errores del servidor
  const submittedLineIndexMap = [];
  const normalizedLines = [];
  lines.value.forEach((l, originalIdx) => {
    if (!l.product) return;
    submittedLineIndexMap.push(originalIdx);
    normalizedLines.push({
      id: l.id,
      product: extractId(l.product),
      quantity: money2(l.quantity || 0),
      unit: extractId(l.unit),
      unit_price: money2(l.unit_price || 0),
      discount_percentage: money2(l.discount_percentage || 0),
      warehouse: extractId(l.warehouse),
      price_type: extractId(l.price_type),
      brand: extractId(l.brand),
      pricing_rule: l.pricing_rule ?? null,
      margin_percent:
        l.margin_percent != null && l.margin_percent !== ""
          ? money2(l.margin_percent)
          : null,
    });
  });
  lastSubmittedLineIndexMap.value = submittedLineIndexMap;

  return {
    document_type: form.document_type,
    builder: builderToSend ? extractId(builderToSend) : null,
    work_account: workAccountId,
    date: form.date,
    notes: form.notes?.trim() || "",
    is_active: form.is_active,
    lines: normalizedLines,
  };
}

function clearErrors() {
  Object.keys(errors).forEach((k) => delete errors[k]);
  lines.value.forEach((l) => (l._errors = {}));
}

function applyServerErrors(errData) {
  if (!errData || typeof errData !== "object" || Array.isArray(errData)) {
    // Respuesta HTML (500) o no-JSON: no iterar como objeto
    console.warn(
      "🔍 Frontend: applyServerErrors - errData no es objeto válido (¿respuesta HTML?):",
      typeof errData
    );
    if (typeof errData === "string" && errData.length > 200) {
      errors.non_field_errors = [
        "Server error. Please try again or contact support.",
      ];
    } else if (errData && typeof errData === "string") {
      errors.non_field_errors = [errData];
    }
    return;
  }
  // High-level document errors
  for (const k in errData) {
    if (k !== "lines") {
      errors[k] = errData[k];
    }
  }

  // Per-line errors: índices del payload (solo líneas con producto) → índice UI
  const mapPayloadIdx = (payloadIdx) => {
    const mapped = lastSubmittedLineIndexMap.value?.[payloadIdx];
    return mapped != null ? mapped : payloadIdx;
  };

  if (Array.isArray(errData.lines)) {
    errData.lines.forEach((item, payloadIdx) => {
      if (!item || (typeof item === "object" && !Object.keys(item).length)) {
        return;
      }
      const target = lines.value[mapPayloadIdx(payloadIdx)];
      if (!target) return;
      target._errors = { ...(item || {}) };
    });
  } else if (errData.lines && typeof errData.lines === "object") {
    // Formato objeto { "0": {...}, "1": {...} }
    Object.entries(errData.lines).forEach(([key, item]) => {
      const payloadIdx = parseInt(key, 10);
      if (isNaN(payloadIdx) || !item) return;
      if (typeof item === "object" && !Object.keys(item).length) return;
      const target = lines.value[mapPayloadIdx(payloadIdx)];
      if (!target) return;
      target._errors = {
        ...(typeof item === "object" ? item : { _: String(item) }),
      };
    });
  }
}

async function handleSubmit() {
  if (isViewMode.value || formBusy.value) return;
  submitting.value = true;
  clearErrors();
  try {
    const payload = normalizePayload();

    // 🔍 DEBUG: Log del payload completo
    payload.lines.forEach((line, idx) => {
      // 🔍 DEBUG: Verificar tipos de datos
    });

    const url = isEditMode.value
      ? `/api/documents/${idParam}/`
      : "/api/documents/";
    const method = isEditMode.value ? "put" : "post";
    const { data } = await axios[method](url, payload);
    const documentId = data.id || idParam;

    const hasSerializedItems = data?.serialized_items?.length > 0;
    const docTypeCreatesSerialized =
      !!data?.document_type_creates_serialized_items;
    if (hasSerializedItems && docTypeCreatesSerialized) {
      assetTagModalOpenedFromSave.value = true;
      documentIdForAssetTagModal.value = documentId;
      documentContextForAssetTagModal.value = {
        id: data.id,
        document_type_code: data.document_type_code,
        builder_name: data.builder_name,
        date: data.date,
      };
      showAssetTagModal.value = true;
    } else {
      await promptPrintAndRedirect(documentId);
    }
  } catch (err) {
    const data = err?.response?.data;
    const status = err?.response?.status;

    // Si la respuesta es HTML (500, etc.), no intentar procesar como JSON
    if (typeof data === "string") {
      console.error(
        "❌ Frontend: Error del servidor (respuesta HTML/texto):",
        status,
        data?.slice?.(0, 200)
      );
      applyServerErrors(null); // no procesar
      await Swal.fire({
        icon: "error",
        title: t("common.serverError"),
        text:
          status >= 500
            ? t("transactions.form.swalServerErrorText")
            : t("transactions.form.swalUnexpectedResponse"),
        confirmButtonText: t("common.ok"),
      });
      return;
    }

    if (data?.lines) {
      if (Array.isArray(data.lines)) {
        data.lines.forEach((lineError, idx) => {
          console.error(`📋 Frontend: Error en línea ${idx}:`, lineError);
        });
      } else {
        Object.keys(data.lines).forEach((field) => {
          console.error(
            `📋 Frontend: Error en campo ${field}:`,
            data.lines[field]
          );
        });
      }
    }

    if (data) applyServerErrors(data);

    let errorMessage = t("transactions.form.swalReviewHighlightedFields");
    let errorTitle = t("common.validationError");
    const stockErrors = [];
    const validationSummary = collectValidationSummary(data || errors);

    // Mensaje claro cuando falta Party (builder) o Work Account
    const builderError =
      data?.builder &&
      (Array.isArray(data.builder) ? data.builder[0] : data.builder);
    const workAccountError =
      data?.work_account &&
      (Array.isArray(data.work_account)
        ? data.work_account[0]
        : data.work_account);
    if (status === 400 && (builderError || workAccountError)) {
      if (builderError) {
        errorMessage = t("transactions.form.swalPartyRequiredText");
        errorTitle = t("transactions.form.swalPartyRequiredTitle");
      } else if (workAccountError) {
        errorMessage = t("transactions.form.swalWorkAccountRequiredText");
        errorTitle = t("transactions.form.swalWorkAccountRequiredTitle");
      }
    } else if (validationSummary.length > 0) {
      errorMessage = `<div class="jr-pilot text-start"><p class="mb-2 text-sm">${t("transactions.form.swalReviewHighlightedListIntro")}</p><ul class="m-0 list-disc ps-4 text-sm">${validationSummary
        .slice(0, 12)
        .map((s) => `<li>${s}</li>`)
        .join("")}${
        validationSummary.length > 12 ? "<li>…</li>" : ""
      }</ul></div>`;
    }

    // Verificar si hay non_field_errors primero
    if (data?.non_field_errors) {
      const nonFieldErrors = Array.isArray(data.non_field_errors)
        ? data.non_field_errors
        : [data.non_field_errors];
      errorMessage = nonFieldErrors
        .map((e) => formatErrorValue(e))
        .filter(Boolean)
        .join("<br>");
      errorTitle = t("common.serverError");
      console.error(
        "🔍 Frontend: non_field_errors encontrados:",
        nonFieldErrors
      );
    }

    function unwrapErr(val) {
      if (Array.isArray(val)) return unwrapErr(val[0]);
      return val;
    }

    function errField(obj, key) {
      if (!obj || typeof obj !== "object") return null;
      let v = obj[key];
      if (v == null) return null;
      v = unwrapErr(v);
      if (v == null) return null;
      if (typeof v === "object" && v.string != null) return String(v.string);
      if (typeof v === "object") return null;
      return v;
    }

    function isInsufficientStockPayload(payload) {
      if (!payload || typeof payload !== "object") return false;
      return errField(payload, "error_type") === "insufficient_stock";
    }

    function looksLikeRawErrorDump(text) {
      return (
        typeof text === "string" &&
        (/ErrorDetail\s*\(/.test(text) ||
          /'error_type'\s*:/.test(text) ||
          /"error_type"\s*:/.test(text))
      );
    }

    function parseStockDump(text) {
      if (typeof text !== "string") return null;
      const productName =
        text.match(/product_name['"]?\s*[:=]\s*(?:ErrorDetail\(string=)?['"]([^'"]+)['"]/i)?.[1] ||
        text.match(/^(.+?):\s*(?:Stock insuficiente|Insufficient stock)/i)?.[1] ||
        null;
      const available =
        text.match(/available['"]?\s*[:=]\s*(?:ErrorDetail\(string=)?['"]([^'"]+)['"]/i)?.[1] ||
        text.match(/Disponible:\s*([0-9]+(?:\.[0-9]+)?)/i)?.[1] ||
        text.match(/Available:\s*([0-9]+(?:\.[0-9]+)?)/i)?.[1] ||
        null;
      const requested =
        text.match(/requested['"]?\s*[:=]\s*(?:ErrorDetail\(string=)?['"]([^'"]+)['"]/i)?.[1] ||
        text.match(/solicitado(?:\(ref\))?:\s*([0-9]+(?:\.[0-9]+)?)/i)?.[1] ||
        text.match(/Requested:\s*([0-9]+(?:\.[0-9]+)?)/i)?.[1] ||
        null;
      const documentType =
        text.match(/document_type['"]?\s*[:=]\s*(?:ErrorDetail\(string=)?['"]([^'"]+)['"]/i)?.[1] ||
        text.match(/tipo de documento\s*'([^']+)'/i)?.[1] ||
        text.match(/Document type\s*'([^']+)'/i)?.[1] ||
        null;
      if (!productName && available == null && requested == null) return null;
      return { productName, available, requested, documentType };
    }

    function productNameFromLineIndex(lineIndex) {
      const uiIdx =
        lastSubmittedLineIndexMap.value?.[lineIndex] != null
          ? lastSubmittedLineIndexMap.value[lineIndex]
          : lineIndex;
      const line = lines.value?.[uiIdx];
      return (
        line?.product_label ||
        line?.product_name ||
        (line?.product != null ? `Product #${line.product}` : null)
      );
    }

    function resolveStockProductName(payload, lineIndex, fallbackMessage) {
      const fromPayload = errField(payload, "product_name");
      if (fromPayload && String(fromPayload).trim()) {
        return String(fromPayload).trim();
      }

      const msg =
        errField(payload, "message") ||
        (typeof fallbackMessage === "string" ? fallbackMessage : "") ||
        (typeof payload === "string" ? payload : "");
      if (typeof msg === "string" && msg.trim()) {
        const fromDump = parseStockDump(msg);
        if (fromDump?.productName) return fromDump.productName.trim();
        const named = msg.match(
          /^(.+?):\s*(?:Stock insuficiente|Insufficient stock)/i
        );
        if (named?.[1]?.trim() && named[1].trim().toLowerCase() !== "product") {
          return named[1].trim();
        }
      }

      return productNameFromLineIndex(lineIndex) || "Unknown product";
    }

    function pushFriendlyStockError({
      productName,
      available,
      requested,
      documentType,
      lineIndex,
    }) {
      stockErrors.push({
        productName:
          (productName && String(productName).trim()) ||
          productNameFromLineIndex(lineIndex) ||
          "Unknown product",
        available: available != null ? String(available) : null,
        requested: requested != null ? String(requested) : null,
        documentType: documentType != null ? String(documentType) : null,
      });
    }

    function pushStructuredStockError(payload, lineIndex) {
      pushFriendlyStockError({
        productName: resolveStockProductName(payload, lineIndex),
        available: errField(payload, "available"),
        requested: errField(payload, "requested"),
        documentType: errField(payload, "document_type"),
        lineIndex,
      });
    }

    function pushFromStockText(text, lineIndex) {
      const parsed = parseStockDump(text) || {};
      pushFriendlyStockError({
        productName:
          parsed.productName ||
          resolveStockProductName(null, lineIndex, text),
        available: parsed.available,
        requested: parsed.requested,
        documentType: parsed.documentType,
        lineIndex,
      });
    }

    // Verificar si hay errores de stock insuficiente
    if (data?.lines) {
      if (Array.isArray(data.lines)) {
        data.lines.forEach((lineError, idx) => {
          if (!lineError) return;

          if (
            typeof lineError === "string" &&
            (/Stock insuficiente|Insufficient stock|error_type/i.test(
              lineError
            ) ||
              looksLikeRawErrorDump(lineError))
          ) {
            pushFromStockText(lineError, idx);
            return;
          }

          const quantityError = unwrapErr(lineError?.quantity);
          if (isInsufficientStockPayload(quantityError)) {
            pushStructuredStockError(quantityError, idx);
            return;
          }
          if (isInsufficientStockPayload(lineError)) {
            pushStructuredStockError(lineError, idx);
            return;
          }

          const qtyText =
            typeof quantityError === "string"
              ? quantityError
              : quantityError?.string;
          if (
            typeof qtyText === "string" &&
            (/Stock insuficiente|Insufficient stock/i.test(qtyText) ||
              looksLikeRawErrorDump(qtyText))
          ) {
            pushFromStockText(qtyText, idx);
          }
        });
      } else {
        Object.keys(data.lines).forEach((field) => {
          const errorData = unwrapErr(data.lines[field]);
          const lineIndex = Number.isFinite(Number(field))
            ? Number(field)
            : null;

          if (typeof errorData === "string") {
            if (
              /Stock insuficiente|Insufficient stock|error_type/i.test(
                errorData
              ) ||
              looksLikeRawErrorDump(errorData)
            ) {
              pushFromStockText(errorData, lineIndex);
            }
            return;
          }

          if (isInsufficientStockPayload(errorData)) {
            pushStructuredStockError(errorData, lineIndex);
            return;
          }

          const quantityError = unwrapErr(errorData?.quantity);
          if (isInsufficientStockPayload(quantityError)) {
            pushStructuredStockError(quantityError, lineIndex);
          }
        });
      }
    }

    // También verificar errores directos en el nivel principal (no en lines)
    if (data && stockErrors.length === 0) {
      Object.keys(data).forEach((field) => {
        if (
          data[field] &&
          typeof data[field] === "string" &&
          (/Stock insuficiente|Insufficient stock/i.test(data[field]) ||
            looksLikeRawErrorDump(data[field]))
        ) {
          pushFromStockText(data[field], null);
        } else if (Array.isArray(data[field])) {
          data[field].forEach((errorMsg) => {
            if (
              typeof errorMsg === "string" &&
              (/Stock insuficiente|Insufficient stock/i.test(errorMsg) ||
                looksLikeRawErrorDump(errorMsg))
            ) {
              pushFromStockText(errorMsg, null);
            }
          });
        }
      });
    }

    if (stockErrors.length > 0) {
      errorTitle = t("transactions.form.swalInsufficientStockTitle");
      const stockErrorsHTML = stockErrors
        .map((error) => {
          const name = error.productName || "Unknown product";
          const available = error.available ?? "—";
          const requested = error.requested ?? "—";
          const docType = error.documentType
            ? `<br>${t("transactions.form.swalNoNegativeSales", {
                docType: error.documentType,
              })}`
            : "";
          return `
            <div class="mb-2 border-s-2 border-jr-danger p-2 text-start">
              <p class="m-0 text-sm font-medium text-jr-danger">${name}</p>
              <p class="m-0 text-sm text-jr-muted">
                ${t("transactions.form.swalStockAvailableRequested", {
                  available,
                  requested,
                })}${docType}
              </p>
            </div>
          `;
        })
        .join("");

      errorMessage = `
        <div class="jr-pilot">
          <div class="text-start">
          <p class="mb-3 text-sm">${t("transactions.form.swalInsufficientStockIntro")}</p>
          ${stockErrorsHTML}
          <div class="mt-3 rounded-jr-panel bg-jr-surface-muted p-2">
            <p class="m-0 text-sm text-jr-muted">
              ${t("transactions.form.swalInsufficientStockHelp")}
            </p>
          </div>
          </div>
        </div>
      `;
    }

    await Swal.fire({
      icon: "error",
      title: errorTitle,
      html: errorMessage,
      width: "700px",
      confirmButtonText: t("common.ok"),
      confirmButtonColor: "#dc2626",
    });
    await focusFirstValidationIssue();
  } finally {
    submitting.value = false;
  }
}

// Función para cargar el título del work account cuando viene desde el schedule
async function loadWorkAccountTitle(workAccountId) {
  if (!workAccountId) return;
  try {
    const { data } = await axios.get(`/api/work-accounts/${workAccountId}/`);
    if (data && data.title) {
      workAccountTitle.value = data.title;
    }
  } catch (error) {
    console.error("Error loading work account title:", error);
    workAccountTitle.value = t("transactions.form.workAccountFallback", {
      id: workAccountId,
    });
  }
}

onMounted(async () => {
  await Promise.all([fetchStaticOptions(), loadHasInventoryProducts()]);
  // Si hay work_account en query params (viene desde schedule), prellenarlo y cargar título
  if (workAccountParam) {
    form.work_account = workAccountParam;
    // Cargar el título del work account
    await loadWorkAccountTitle(workAccountParam);
  }

  if (idParam) {
    await loadDocument(idParam);
    // Si viene desde schedule y estamos editando, también cargar el título si no se cargó antes
    if (workAccountParam && !workAccountTitle.value && form.work_account) {
      await loadWorkAccountTitle(form.work_account);
    }
  }
});
</script>

<style scoped>
.jr-form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1rem;
}

@media (min-width: 768px) {
  .jr-form-grid--document {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .jr-form-grid--import {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .jr-form-grid--document {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.jr-form-banner {
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
  background: var(--color-jr-danger-subtle);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
}

.jr-form-banner:focus {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-tx-form__loading {
  margin: 0 0 1rem;
  font-size: 0.9375rem;
  line-height: 1.45;
  color: var(--color-jr-text);
}

.jr-tx-form__readonly {
  margin: 0;
  padding: 0.55rem 0.75rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text);
  background: var(--color-jr-surface-muted, var(--color-jr-page));
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-control, 0);
}

.jr-tx-form__info {
  margin: 0.5rem 0 0;
  --p-message-info-background: var(--color-jr-info-subtle);
  --p-message-info-border-color: var(--color-jr-border);
  --p-message-info-color: var(--color-jr-info-text);
  --p-message-warn-background: var(--color-jr-warning-subtle);
  --p-message-warn-border-color: var(--color-jr-border);
  --p-message-warn-color: var(--color-jr-warning-text);
  --p-message-border-radius: var(--radius-jr-control, 0);
}

.jr-tx-form__fav-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.jr-tx-form__fav-star {
  /* Favorite affordance: clear yellow (DESIGN.md warning token). */
  color: var(--color-jr-warning);
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
}

.jr-tx-form__import-col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 0;
}

@media (min-width: 768px) {
  .jr-tx-form__import-col--favorites {
    padding-right: 1.25rem;
    border-right: 1px solid var(--color-jr-border);
  }

  .jr-tx-form__import-col--excel {
    padding-left: 0.25rem;
  }
}

.jr-tx-form__favorites {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.5rem;
}

.jr-tx-form__update-fav {
  align-self: flex-start;
}

.jr-tx-form__excel {
  margin: 0;
}

.jr-tx-form__lines {
  margin-top: 0.35rem;
}

.jr-tx-form {
  caret-color: var(--color-jr-primary);
}

.jr-tx-form ::selection {
  background: color-mix(in srgb, var(--color-jr-primary) 28%, transparent);
  color: var(--color-jr-text);
}

.jr-tx-form__doc-active {
  flex-shrink: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-tx-form__info--voided {
  margin-top: 0.75rem;
}

.jr-tx-form__totals-wrap {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: stretch;
}

.jr-tx-form__notes {
  min-width: 0;
  width: 100%;
  padding-top: 0.35rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-tx-form__notes :deep(textarea) {
  min-height: 0;
  resize: vertical;
}

.jr-tx-form__totals {
  margin: 0;
  width: 100%;
  max-width: 24rem;
  margin-left: auto;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.jr-tx-form__totals-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin: 0;
}

.jr-tx-form__totals-row dt,
.jr-tx-form__totals-row dd {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-jr-text);
}

.jr-tx-form__totals-row dt {
  font-weight: 600;
}

.jr-tx-form__totals-row dd {
  font-variant-numeric: tabular-nums;
  text-align: right;
}

.jr-tx-form__totals-discount {
  color: var(--color-jr-danger-text);
}

.jr-tx-form__totals-row--grand {
  padding-top: 0.55rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-tx-form__totals-row--grand dt,
.jr-tx-form__totals-row--grand dd {
  font-size: 0.9375rem;
  font-weight: 700;
}

.jr-tx-form__totals-row--profit {
  padding-top: 0.55rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-tx-form__totals-hint {
  display: block;
  margin-top: 0.15rem;
  font-size: 0.75rem;
  font-weight: 400;
  color: var(--color-jr-muted);
}

.jr-tx-form__totals-ok {
  color: var(--color-jr-success-text, var(--color-jr-text));
  font-weight: 600;
}

.jr-tx-form__totals-bad {
  color: var(--color-jr-danger-text);
  font-weight: 600;
}

.jr-tx-form__status-badge-btn {
  display: inline-flex;
  align-items: center;
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  border-radius: var(--radius-jr-control, 0);
}

.jr-tx-form__status-badge-btn:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-tx-form__status-drawer-icon {
  flex-shrink: 0;
  margin-inline-end: 0.35rem;
  vertical-align: -0.2em;
}

.jr-tx-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.35rem;
  margin-top: 0.75rem;
  background: var(--color-jr-page);
  border-top: 1px solid var(--color-jr-border);
  box-shadow: 0 -2px 10px color-mix(in srgb, var(--color-jr-text) 6%, transparent);
}
</style>
