<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" :description="pageDescription">
      <template #actions>
        <JRButton
          v-if="
            isViewMode &&
            idParam &&
            hasPermission('apptransactions.change_document')
          "
          variant="primary"
          size="sm"
          @click="goToEdit">
          Edit transaction
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
        Loading transaction…
      </p>

      <JRSection v-if="!loadingDocument" title="Document">
        <div class="jr-form-grid jr-form-grid--document">
          <JRField
            v-slot="{ describedby }"
            label="Document Type"
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
            label="Work Account"
            inputId="tx-work-account-ro"
            hint="Work account selected from the schedule">
            <p class="jr-tx-form__readonly" id="tx-work-account-ro">
              {{ workAccountTitle }}
            </p>
          </JRField>

          <JRField
            v-else-if="!isOperationalDocument && !isFromSchedule"
            v-slot="{ describedby }"
            label="Party"
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
            label="Work Account"
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
            label="Date"
            required
            inputId="tx-date"
            :error="fieldError('date')">
            <JRDatePicker
              inputId="tx-date"
              :modelValue="isoToDate(form.date)"
              :disabled="isReadOnly"
              :invalid="invalid"
              placeholder="Select date"
              @update:modelValue="onDateChange" />
          </JRField>

          <JRField
            :label="form.is_active ? 'Active' : 'Voided'"
            inputId="tx-is-active">
            <JRCheckbox
              v-model="form.is_active"
              inputId="tx-is-active"
              :ariaLabel="form.is_active ? 'Active' : 'Voided'"
              :disabled="isReadOnly" />
            <Message
              v-if="!form.is_active"
              class="jr-tx-form__info"
              severity="warn"
              :closable="false">
              This transaction is voided and will be ignored in reports.
            </Message>
          </JRField>

          <JRField
            class="jr-tx-form__notes"
            v-slot="{ describedby, invalid }"
            label="Notes"
            inputId="tx-notes"
            :error="fieldError('notes')">
            <JRTextarea
              inputId="tx-notes"
              :modelValue="form.notes"
              :rows="2"
              placeholder="Additional notes…"
              :disabled="isReadOnly"
              :invalid="invalid"
              :ariaDescribedby="describedby"
              @update:modelValue="form.notes = ($event || '').trim()" />
          </JRField>
        </div>
      </JRSection>

      <JRSection v-if="!loadingDocument && !isViewMode" title="Import & favorites">
        <div class="jr-form-grid jr-form-grid--import">
          <div class="jr-tx-form__import-col jr-tx-form__import-col--favorites">
            <JRField
              label="Add to favorites"
              inputId="tx-add-favorite"
              hint="Requires at least 2 lines with a product.">
              <JRButton
                type="button"
                variant="secondary"
                size="sm"
                class="jr-tx-form__fav-btn"
                :disabled="!canSaveAsFavorite"
                @click="openFavoriteModal">
                <Star class="jr-tx-form__fav-star" aria-hidden="true" />
                Save as favorite
              </JRButton>
            </JRField>

            <div class="jr-tx-form__favorites">
              <JRField
                label="Import favorite"
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
                Update favorite
              </JRButton>
            </div>
          </div>

          <div class="jr-tx-form__import-col jr-tx-form__import-col--excel">
            <JRField
              label="Import from Excel"
              inputId="tx-excel-import"
              :hint="
                hasInventoryProducts
                  ? 'Download the template and import lines from Excel.'
                  : ''
              ">
              <JRCheckbox
                v-model="showExcelImportPanel"
                inputId="tx-excel-import"
                ariaLabel="Import from Excel"
                :disabled="inventoryProductsLoading || !hasInventoryProducts" />
              <Message
                v-if="!inventoryProductsLoading && !hasInventoryProducts"
                class="jr-tx-form__info"
                severity="info"
                :closable="false">
                Import requires at least one active product in inventory.
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

      <JRSection v-if="!loadingDocument" title="Lines">
        <Message
          v-if="linesGridDisabled && !isViewMode"
          class="jr-tx-form__info"
          severity="info"
          :closable="false">
          Select a document type or import a favorite to edit lines.
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

      <JRSection v-if="!loadingDocument" title="Totals">
        <dl class="jr-tx-form__totals">
          <div class="jr-tx-form__totals-row">
            <dt>Subtotal</dt>
            <dd>{{ currency(subtotal_gross) }}</dd>
          </div>
          <div class="jr-tx-form__totals-row">
            <dt>Total discount</dt>
            <dd class="jr-tx-form__totals-discount">
              −{{ currency(total_discount) }}
            </dd>
          </div>
          <div class="jr-tx-form__totals-row jr-tx-form__totals-row--grand">
            <dt>Grand total</dt>
            <dd>{{ currency(grand_total) }}</dd>
          </div>
          <div
            v-if="currentDocumentTypeIsSales"
            class="jr-tx-form__totals-row jr-tx-form__totals-row--profit">
            <dt>
              Estimated profit
              <span class="jr-tx-form__totals-hint">
                Based on purchase cost per line (informational)
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
          {{ isViewMode ? "Back to list" : "Cancel" }}
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
import axios from "axios";
import Swal from "sweetalert2";

import Message from "primevue/message";
import Star from "@primeicons/vue/star";
import LinesGrid from "@/components/transactions/LinesGrid.vue";
import DocumentTypeSelector from "@/components/transactions/DocumentTypeSelector.vue";
import BuilderSelector from "@/components/parties/BuilderSelector.vue";
import WorkAccountSelector from "@/components/transactions/WorkAccountSelector.vue";
import TransactionFavoriteModal from "@/components/transactions/TransactionFavoriteModal.vue";
import AssetTagAssignmentModal from "@/components/transactions/AssetTagAssignmentModal.vue";
import FavoriteTransactionSelector from "@/components/transactions/FavoriteTransactionSelector.vue";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRButton,
  JRCheckbox,
  JRDatePicker,
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
        "Loading Excel import…"
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
  if (isViewMode.value) return "View Transaction";
  if (isEditMode.value) return "Edit Transaction";
  return "New Transaction";
});

const pageDescription = computed(() => {
  if (isViewMode.value) return "Review this transaction. Switch to Edit to make changes.";
  if (isEditMode.value) return "Update document header, lines, and totals.";
  return "Create a document with lines, parties or work account, and totals.";
});

const saveButtonLabel = computed(() => {
  if (loadingDocument.value) return "Loading...";
  if (submitting.value) return "Saving...";
  return isEditMode.value ? "Update" : "Save";
});

const saveAndAddLabel = computed(() => {
  if (loadingDocument.value) return "Loading...";
  if (submitting.value) return "Saving...";
  return "Save & add another";
});

const formBannerMessage = computed(() => {
  const nf = errors.non_field_errors;
  if (!nf) return "";
  return Array.isArray(nf) ? nf.filter(Boolean).join(" ") : String(nf);
});

function hasPermission(permission) {
  return !!proxy?.hasPermission?.(permission);
}

function fieldError(key) {
  const value = errors[key];
  if (!value) return "";
  return Array.isArray(value) ? value[0] || "" : String(value);
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
/** Permite usar la rejilla sin tipo de documento tras importar líneas desde un favorito */
const linesGridUnlockedByFavoriteImport = ref(false);

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

function onTransactionLinesImported(newLines) {
  lines.value = newLines;
  syncTotals();
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
    product_label: line.product_label || "",
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

  /** Si true: solo se concatenan líneas; cabecera del documento no se sobrescribe */
  let appendLinesOnly = false;

  if (hasExistingLineProducts && hasIncomingLines) {
    const result = await Swal.fire({
      title: "Lines already loaded",
      html:
        "This transaction already has line items.<br><br>" +
        "<strong>Add to existing lines</strong> appends this favorite’s lines (e.g. combine kits on one pick ticket). " +
        "Header fields stay as they are.<br><br>" +
        "<strong>Replace all lines</strong> loads this favorite’s header and replaces every line.",
      icon: "question",
      showCancelButton: true,
      showDenyButton: true,
      confirmButtonText: "Add to existing lines",
      denyButtonText: "Replace all lines",
      cancelButtonText: "Cancel",
      confirmButtonColor: "#198754",
      denyButtonColor: "#6c757d",
      cancelButtonColor: "#adb5bd",
      reverseButtons: true,
    });

    if (result.isDismissed) {
      selectedFavoriteId.value = null;
      return;
    }
    appendLinesOnly = Boolean(result.isConfirmed);
  }

  if (!appendLinesOnly && favoriteData.document_data) {
    const docData = favoriteData.document_data;

    form.document_type = docData.document_type;
    form.builder = docData.builder;
    form.work_account = docData.work_account;
    form.date = toDateInputValue(docData.date);
    form.notes = docData.notes || "";
    form.is_active = docData.is_active !== undefined ? docData.is_active : true;
  }

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
        title: "Favorite Updated",
        text: "The favorite has been updated with current transaction data.",
        timer: 2000,
        showConfirmButton: false,
      });

    }
  } catch (error) {
    console.error("❌ Error updating favorite:", error);

    await Swal.fire({
      icon: "error",
      title: "Update Failed",
      text: "Failed to update the favorite. Please try again.",
      confirmButtonText: "OK",
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
      title: "Transaction Saved Successfully!",
      text: "The transaction has been saved. You can now create another one.",
      icon: "success",
      timer: 2000,
      showConfirmButton: false,
    });
    resetFormForNewTransaction();

  } catch (err) {
    console.error("❌ Error al guardar transacción:", err);

    const data = err?.response?.data;
    if (data) applyServerErrors(data);

    // Mostrar error (reutilizar la lógica de handleSubmit)
    let errorMessage = "Please review highlighted fields.";
    let errorTitle = "Validation Error";

    await Swal.fire({
      icon: "error",
      title: errorTitle,
      text: errorMessage,
      confirmButtonText: "OK",
    });
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
  proxy?.notifyToastSuccess?.("Serial numbers saved.");
  onAssetTagModalClose();
}

// Prompt PDF and redirect (after save)
async function promptPrintAndRedirect(documentId) {
  const { value: shouldPrint } = await Swal.fire({
    title: "Transaction Saved Successfully!",
    text: "Do you want to print the PDF?",
    icon: "success",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#6c757d",
    confirmButtonText: "Yes, Print",
    cancelButtonText: "No, Continue",
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
      title: "Error",
      text: "Could not generate the document PDF. Please try again.",
      confirmButtonText: "OK",
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
  } catch (error) {
    console.error("Error loading document:", error);
    await Swal.fire({
      icon: "error",
      title: "Error",
      text: "Document not found or has invalid references. Please check the data.",
      confirmButtonText: "OK",
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

  // 🔍 DEBUG: Log para verificar work_account
  const normalizedPayload = {
    document_type: form.document_type,
    builder: builderToSend ? extractId(builderToSend) : null,
    work_account: workAccountId,
    date: form.date,
    notes: form.notes?.trim() || "",
    is_active: form.is_active,
    lines: lines.value
      .filter((l) => l.product) // Solo enviar líneas que tengan producto
      .map((l) => {
        const normalizedLine = {
          id: l.id,
          product: extractId(l.product),
          quantity: Number(l.quantity || 0),
          unit: extractId(l.unit),
          unit_price: Number(l.unit_price || 0),
          discount_percentage: Number(l.discount_percentage || 0),
          warehouse: extractId(l.warehouse),
          price_type: extractId(l.price_type),
          brand: extractId(l.brand),
          pricing_rule: l.pricing_rule ?? null,
          margin_percent:
            l.margin_percent != null && l.margin_percent !== ""
              ? Number(l.margin_percent)
              : null,
        };

        // 🔍 DEBUG: Log de la línea normalizada
        return normalizedLine;
      }),
  };

  return normalizedPayload;
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

  // Per-line errors (DRF devuelve lista alineada con índices)
  if (Array.isArray(errData.lines)) {
    errData.lines.forEach((item, idx) => {
      if (!item) return;
      const target = lines.value[idx];
      if (!target) return;
      target._errors = { ...(item || {}) };
    });
  } else if (errData.lines && typeof errData.lines === "object") {
    // Formato objeto { "0": {...}, "1": {...} }
    Object.entries(errData.lines).forEach(([key, item]) => {
      const idx = parseInt(key, 10);
      if (isNaN(idx) || !item) return;
      const target = lines.value[idx];
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
        title: "Server Error",
        text:
          status >= 500
            ? "An error occurred on the server. Please try again or contact support."
            : "Unexpected response from server.",
        confirmButtonText: "OK",
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

    let errorMessage = "Please review highlighted fields.";
    let errorTitle = "Validation Error";
    const stockErrors = [];

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
        errorMessage =
          "Please select a Party (supplier for purchases, customer for sales) before saving. The Serial Numbers modal will appear after a successful save when the transaction has serialized items.";
        errorTitle = "Party required";
      } else if (workAccountError) {
        errorMessage = "Please select a Work Account before saving.";
        errorTitle = "Work Account required";
      }
    }

    // Verificar si hay non_field_errors primero
    if (data?.non_field_errors) {
      const nonFieldErrors = Array.isArray(data.non_field_errors)
        ? data.non_field_errors
        : [data.non_field_errors];
      errorMessage = nonFieldErrors.join("<br>");
      errorTitle = "Server Error";
      console.error(
        "🔍 Frontend: non_field_errors encontrados:",
        nonFieldErrors
      );
    }

    // Función para extraer información del producto del mensaje de error
    function extractProductInfo(errorMsg, lineIndex = null) {
      // Extraer directamente del errorMsg
      try {
        if (errorMsg && errorMsg.quantity && errorMsg.quantity.product_name) {
          const productName =
            errorMsg.quantity.product_name.string ||
            errorMsg.quantity.product_name;
          return productName;
        }
      } catch (e) {
        // Error silencioso
      }

      return "Product";
    }

    // Verificar si hay errores de stock insuficiente
    if (data?.lines) {
      if (Array.isArray(data.lines)) {
        data.lines.forEach((lineError, idx) => {
          const quantityError = lineError?.quantity;

          // Caso 1: Error estructurado del backend (nuevo formato)
          if (
            typeof quantityError === "object" &&
            quantityError.error_type === "insufficient_stock"
          ) {
            stockErrors.push({
              productName: quantityError.product_name,
              available: quantityError.available,
              requested: quantityError.requested,
              documentType: quantityError.document_type,
              message: quantityError.message,
            });
          }
          // Caso 1b: Error estructurado anidado en quantity (formato DRF)
          else if (
            typeof quantityError === "object" &&
            quantityError.error_type &&
            quantityError.error_type.string === "insufficient_stock"
          ) {
            stockErrors.push({
              productName:
                quantityError.product_name.string || quantityError.product_name,
              available:
                quantityError.available.string || quantityError.available,
              requested:
                quantityError.requested.string || quantityError.requested,
              documentType:
                quantityError.document_type.string ||
                quantityError.document_type,
              message: quantityError.message.string || quantityError.message,
            });
          }
          // Caso 2: ErrorDetail con string (formato anterior)
          else if (
            typeof quantityError === "object" &&
            quantityError.string &&
            quantityError.string.includes("Stock insuficiente")
          ) {
            const productName = extractProductInfo(quantityError, idx);
            stockErrors.push(`• ${productName}: ${quantityError.string}`);
          }
          // Caso 3: String directo (formato anterior)
          else if (
            typeof quantityError === "string" &&
            quantityError.includes("Stock insuficiente")
          ) {
            const productName = extractProductInfo(quantityError, idx);
            stockErrors.push(`• ${productName}: ${quantityError}`);
          }
        });
      } else {
        // Si es un objeto, buscar errores de cantidad
        Object.keys(data.lines).forEach((field) => {
          const errorData = data.lines[field];

          // Caso 1: Error estructurado del backend (nuevo formato)
          if (
            typeof errorData === "object" &&
            errorData.error_type === "insufficient_stock"
          ) {
            stockErrors.push({
              productName: errorData.product_name,
              available: errorData.available,
              requested: errorData.requested,
              documentType: errorData.document_type,
              message: errorData.message,
            });
          }
          // Caso 1b: Error estructurado anidado (formato DRF)
          else if (
            typeof errorData === "object" &&
            errorData.error_type &&
            errorData.error_type.string === "insufficient_stock"
          ) {
            stockErrors.push({
              productName:
                errorData.product_name.string || errorData.product_name,
              available: errorData.available.string || errorData.available,
              requested: errorData.requested.string || errorData.requested,
              documentType:
                errorData.document_type.string || errorData.document_type,
              message: errorData.message.string || errorData.message,
            });
          }
          // Caso 2: ErrorDetail con string (formato anterior)
          else if (
            field === "quantity" &&
            typeof errorData === "object" &&
            errorData.string &&
            errorData.string.includes("Stock insuficiente")
          ) {
            const productName = extractProductInfo(errorData);
            stockErrors.push(`• ${productName}: ${errorData.string}`);
          }
          // Caso 3: String directo (formato anterior)
          else if (
            field === "quantity" &&
            typeof errorData === "string" &&
            errorData.includes("Stock insuficiente")
          ) {
            const productName = extractProductInfo(errorData);
            stockErrors.push(`• ${productName}: ${errorData}`);
          }
        });
      }
    }

    // También verificar errores directos en el nivel principal (no en lines)
    if (data && stockErrors.length === 0) {
      // Buscar errores de stock en cualquier campo del nivel principal
      Object.keys(data).forEach((field) => {
        if (
          data[field] &&
          typeof data[field] === "string" &&
          data[field].includes("Stock insuficiente")
        ) {
          const productName = extractProductInfo(data[field]);
          stockErrors.push(`• ${productName}: ${data[field]}`);
        } else if (Array.isArray(data[field])) {
          // Si es un array de errores
          data[field].forEach((errorMsg) => {
            if (
              typeof errorMsg === "string" &&
              errorMsg.includes("Stock insuficiente")
            ) {
              const productName = extractProductInfo(errorMsg);
              stockErrors.push(`• ${productName}: ${errorMsg}`);
            }
          });
        }
      });
    }

    if (stockErrors.length > 0) {
      errorTitle = "Insufficient Stock";
      // Crear HTML para mejor formato con información más específica
      const stockErrorsHTML = stockErrors
        .map((error) => {
          // Caso 1: Error estructurado del backend (nuevo formato)
          if (typeof error === "object" && error.productName) {
            return `
            <div class="text-start mb-2 p-2 border-start border-danger border-2">
              <small class="text-danger">${error.productName}</small><br>
              <small class="text-muted">
                Available: ${error.available} | 
                Requested: ${error.requested}<br>
                Document Type: ${error.documentType} (does not allow negative sales)
              </small>
            </div>
          `;
          }
          // Caso 2: Error en formato string (formato anterior)
          else if (typeof error === "string") {
            // Intentar extraer información del mensaje de error
            const match = error.match(
              /Stock insuficiente\. Disponible: (\d+(?:\.\d+)?), solicitado\(ref\): (\d+(?:\.\d+)?)\. El tipo de documento '([^']+)' no permite ventas sin stock\./
            );
            if (match) {
              const [, available, requested, docType] = match;
              const productName = error.split(":")[0].replace("• ", "");
              return `
              <div class="text-start mb-2 p-2 border-start border-danger border-2">
                <small class="text-danger">${productName}</small><br>
                <small class="text-muted">
                  Available: ${available} | 
                  Requested: ${requested}<br>
                  Document Type: ${docType} (does not allow negative sales)
                </small>
              </div>
            `;
            }
            // Si no se puede parsear, mostrar el error tal como está
            return `
            <div class="text-start mb-1">
              <small class="text-danger">${error}</small>
            </div>
          `;
          }
          // Caso 3: Fallback
          return `
          <div class="text-start mb-1">
            <small class="text-danger">${String(error)}</small>
          </div>
        `;
        })
        .join("");

      errorMessage = `
        <div class="text-start">
          <small class="mb-3">⚠️ The following products have insufficient stock:</small>
          ${stockErrorsHTML}
          <div class="mt-3 p-2 bg-light rounded">
            <small class="text-muted">
              ℹ️ 
              Solutions:<br>
              • Check inventory in other warehouses<br>
              • Adjust quantities to available stock<br>
              • Enable "Allow Negative Sales" in document type settings
            </small>
          </div>
        </div>
      `;
    }

    await Swal.fire({
      icon: "error",
      title: errorTitle,
      html: errorMessage,
      width: "700px",
      confirmButtonText: "OK",
      confirmButtonColor: "#dc3545",
    });
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
    workAccountTitle.value = `Work Account #${workAccountId}`;
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

  .jr-tx-form__notes {
    grid-column: 1 / -1;
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
  color: #ffc107;
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

.jr-tx-form__totals {
  margin: 0;
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
