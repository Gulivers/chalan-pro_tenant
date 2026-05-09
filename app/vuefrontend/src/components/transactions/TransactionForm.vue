<template>
  <div class="container-fluid position-relative my-2">
    <h3 class="text-center text-warning mb-2">Transaction</h3>
    <div class="card shadow mb-2 mx-3">
      <div class="card-header">
        <!-- Desktop Layout -->
        <div
          class="d-none d-md-flex align-items-center justify-content-between">
          <h6 class="mb-0 text-primary">
            {{ isEditMode ? "Edit Transaction" : "New Transaction" }}
          </h6>
          <div class="d-flex align-items-center gap-3">
            <!-- is_active switch -->
            <div
              class="form-check form-switch m-0"
              v-tt="
                form.is_active
                  ? 'Active transaction'
                  : 'Voided (inactive) – it will be ignored in reports.'
              ">
              <input
                class="form-check-input"
                type="checkbox"
                role="switch"
                id="isActiveSwitch"
                v-model="form.is_active" />
              <label
                class="form-check-label"
                :class="{ 'text-danger': !form.is_active }"
                for="isActiveSwitch">
                {{ form.is_active ? "Active" : "Voided" }}
              </label>
            </div>
            <div class="d-flex gap-2">
              <button
                class="btn btn-outline-secondary"
                type="button"
                @click="goBack">
                Back
              </button>
              <button
                v-if="!isEditMode"
                class="btn btn-success"
                type="button"
                :disabled="submitting"
                @click="handleSaveAndAddAnother">
                <span v-if="!submitting">+</span>
                <span
                  v-else
                  class="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"></span>
                {{ submitting ? "Saving..." : "Save and Add Another" }}
              </button>
              <button
                class="btn btn-primary"
                type="button"
                :disabled="submitting"
                @click="handleSubmit">
                <span v-if="!submitting">💾</span>
                <span
                  v-else
                  class="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"></span>
                {{ submitting ? "Saving..." : "Save" }}
              </button>
            </div>
          </div>
        </div>

        <!-- Mobile Layout -->
        <div class="d-md-none">
          <!-- Title Row -->
          <div class="d-flex align-items-center justify-content-between mb-2">
            <h6 class="mb-0 text-primary">
              {{ isEditMode ? "Edit Transaction" : "New Transaction" }}
            </h6>
            <!-- is_active switch -->
            <div
              class="form-check form-switch m-0"
              v-tt="
                form.is_active
                  ? 'Active transaction'
                  : 'Voided (inactive) – it will be ignored in reports.'
              ">
              <input
                class="form-check-input"
                type="checkbox"
                role="switch"
                id="isActiveSwitchMobile"
                v-model="form.is_active" />
              <label
                class="form-check-label small"
                :class="{ 'text-danger': !form.is_active }"
                for="isActiveSwitchMobile">
                {{ form.is_active ? "Active" : "Voided" }}
              </label>
            </div>
          </div>

          <!-- Button Row -->
          <div class="d-flex gap-1 flex-wrap">
            <button
              class="btn btn-outline-secondary btn-sm flex-fill"
              type="button"
              @click="goBack">
              Back
            </button>
            <button
              v-if="!isEditMode"
              class="btn btn-success btn-sm flex-fill"
              type="button"
              :disabled="submitting"
              @click="handleSaveAndAddAnother">
              <span v-if="!submitting">+</span>
              <span
                v-else
                class="spinner-border spinner-border-sm me-1"
                role="status"
                aria-hidden="true"></span>
              <span class="d-none d-sm-inline">
                {{ submitting ? "Saving..." : "Save & Add" }}
              </span>
              <span class="d-sm-none">
                {{ submitting ? "Saving..." : "Add" }}
              </span>
            </button>
            <button
              class="btn btn-primary btn-sm flex-fill"
              type="button"
              :disabled="submitting"
              @click="handleSubmit">
              <span v-if="!submitting">💾</span>
              <span
                v-else
                class="spinner-border spinner-border-sm me-1"
                role="status"
                aria-hidden="true"></span>
              {{ submitting ? "Saving..." : "Save" }}
            </button>
          </div>
        </div>
      </div>

      <div class="card-body">
        <!-- Header: Document fields -->
        <div class="row g-3">
          <!-- Left Column: Document Type, Party, Work Account -->
          <div class="col-12 col-md-6">
            <div class="row g-3">
              <div class="col-12">
                <DocumentTypeSelector
                  v-model="form.document_type"
                  :error="errors.document_type"
                  :required="true" />
              </div>

              <div class="col-12">
                <!-- Si viene desde schedule, mostrar título del work account (independiente del tipo de documento) -->
                <div v-if="isFromSchedule && workAccountTitle" class="mb-3">
                  <label class="form-label">Work Account</label>
                  <div
                    class="form-control bg-light"
                    style="
                      padding: 0.375rem 0.75rem;
                      border: 1px solid #ced4da;
                      border-radius: 0.375rem;
                      min-height: 38px;
                      display: flex;
                      align-items: center;
                    ">
                    <strong>{{ workAccountTitle }}</strong>
                  </div>
                  <small class="form-text text-muted">
                    Work Account seleccionado desde el Schedule
                  </small>
                </div>

                <!-- Mostrar BuilderSelector si NO es operacional Y NO viene desde schedule -->
                <BuilderSelector
                  v-else-if="!isOperationalDocument && !isFromSchedule"
                  v-model="form.builder"
                  :error="errors.builder" />

                <!-- Mostrar WorkAccountSelector si ES operacional Y NO viene desde schedule -->
                <WorkAccountSelector
                  v-else-if="isOperationalDocument && !isFromSchedule"
                  v-model="form.work_account"
                  :error="errors.work_account" />
              </div>

              <div class="col-12 mt-1">
                <div
                  class="form-check form-switch mb-2 my-1 ms-2 d-flex align-items-center flex-wrap gap-2"
                  v-tt
                  :data-title="excelImportSwitchTooltip">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    role="switch"
                    id="excelImportSwitch"
                    :disabled="
                      inventoryProductsLoading || !hasInventoryProducts
                    "
                    v-model="showExcelImportPanel" />
                  <label class="form-check-label mb-0" for="excelImportSwitch">
                    Import from Excel
                  </label>
                  <span
                    v-if="inventoryProductsLoading"
                    class="spinner-border spinner-border-sm text-secondary"
                    role="status"
                    aria-label="Loading"></span>
                </div>
                <TransactionLinesExcelPanel
                  v-if="hasInventoryProducts && showExcelImportPanel"
                  :units-options="unitsOptions"
                  :warehouses-options="warehousesOptions"
                  :price-types-options="priceTypesOptions"
                  :brands-options="brandsOptions"
                  @import-lines="onTransactionLinesImported" />
              </div>
            </div>
          </div>

          <!-- Right Column: Date and Notes -->
          <div class="col-12 col-md-6">
            <div class="row g-2">
              <!-- Mobile: Stack favorites and date vertically, Desktop: Side by side -->
              <div class="col-12 col-sm-6">
                <label class="form-label d-flex gap-1">Add to favorites</label>
                <div class="d-flex flex-column align-items-start">
                  <button
                    class="btn btn-outline-secondary btn-sm mt-0"
                    type="button"
                    @click="openFavoriteModal"
                    :disabled="!canSaveAsFavorite"
                    v-tt
                    data-title="Add to favorites (requires at least 2 lines with a product — single-line kits are not saved as favorites).">
                    <img
                      src="@assets/img/star-svgrepo-com.svg"
                      alt="Favorite"
                      width="25"
                      height="25" />
                  </button>
                </div>
              </div>
              <div class="col-12 col-sm-6">
                <label
                  class="form-label d-flex align-items-center gap-2"
                  for="dateInput">
                  Date
                </label>
                <input
                  type="date"
                  class="form-control"
                  v-model="form.date"
                  id="dateInput" />
                <div class="text-danger small" v-if="errors.date">
                  {{ errors.date[0] }}
                </div>
              </div>

              <div class="col-12">
                <FavoriteTransactionSelector
                  ref="favoriteSelectorRef"
                  v-model="selectedFavoriteId"
                  :is-edit-mode="isEditMode"
                  @favorite-selected="onFavoriteSelected"
                  @edit-favorite="onEditFavorite" />
              </div>

              <!-- Botón para actualizar favorito cuando se ha importado uno -->
              <div class="col-12" v-if="selectedFavoriteId && !isEditMode">
                <div class="d-flex justify-content-end">
                  <button
                    class="btn btn-outline-warning btn-sm"
                    type="button"
                    @click="updateFavoriteFromCurrentTransaction"
                    :disabled="!canUpdateFavorite"
                    v-tt
                    data-title="Update the selected favorite">
                    Update Favorite
                  </button>
                </div>
              </div>

              <div class="col-12">
                <label
                  class="form-label d-flex align-items-center gap-2"
                  for="notesInput">
                  Notes
                </label>
                <textarea
                  rows="2"
                  class="form-control"
                  v-model.trim="form.notes"
                  placeholder="Additional notes..."
                  id="notesInput"></textarea>
                <div class="text-danger small" v-if="errors.notes">
                  {{ errors.notes[0] }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <hr class="my-4" />

        <p v-if="linesGridDisabled" class="text-muted small mb-2">
          Select a document type or import a favorite to edit lines.
        </p>

        <!-- Lines Grid -->
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

        <!-- Totals -->
        <div class="row mt-3">
          <div class="col-12 col-md-6 d-none d-md-block">&nbsp;</div>
          <div class="col-12 col-md-6">
            <div class="card bg-light">
              <div class="card-body p-3">
                <div class="d-flex justify-content-between">
                  <span class="fw-semibold">Subtotal</span>
                  <span>{{ currency(subtotal_gross) }}</span>
                </div>
                <div class="d-flex justify-content-between mt-1">
                  <span class="fw-semibold">Total discount</span>
                  <span class="text-danger">
                    -{{ currency(total_discount) }}
                  </span>
                </div>
                <div
                  class="d-flex justify-content-between fs-5 mt-2 pt-2 border-top">
                  <span class="fw-bold">Grand total</span>
                  <span class="fw-bold">{{ currency(grand_total) }}</span>
                </div>
                <div
                  v-if="currentDocumentTypeIsSales"
                  class="d-flex justify-content-between mt-2 pt-2 border-top">
                  <div>
                    <span class="fw-semibold text-success">Beneficio estimado</span>
                    <div class="small text-muted">
                      Según costo de compra por línea (informativo)
                    </div>
                  </div>
                  <span
                    class="fw-semibold align-self-start"
                    :class="
                      estimated_sale_profit >= 0 ? 'text-success' : 'text-danger'
                    ">
                    {{ currency(estimated_sale_profit) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Serial Number Assignment (post-save cuando hay SerializedItems) -->
    <AssetTagAssignmentModal
      :show="showAssetTagModal"
      :document-id="documentIdForAssetTagModal"
      :document-context="documentContextForAssetTagModal"
      @close="onAssetTagModalClose"
      @saved="onAssetTagModalSaved" />

    <!-- Modal para favoritos -->
    <TransactionFavoriteModal
      :transaction-data="currentTransactionData"
      :document-types-options="documentTypesOptions"
      :builders-options="buildersOptions"
      :work-accounts-options="workAccountsOptions"
      :is-edit-mode="favoriteModalEditMode"
      :favorite-to-edit="favoriteToEdit"
      @saved="onFavoriteSaved"
      @updated="onFavoriteUpdated"
      @deleted="onFavoriteDeleted" />
  </div>
</template>

<script setup>
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

import LinesGrid from "@/components/transactions/LinesGrid.vue";
import DocumentTypeSelector from "@/components/transactions/DocumentTypeSelector.vue";
import BuilderSelector from "@/components/parties/BuilderSelector.vue";
import WorkAccountSelector from "@/components/transactions/WorkAccountSelector.vue";
import TransactionFavoriteModal from "@/components/transactions/TransactionFavoriteModal.vue";
import AssetTagAssignmentModal from "@/components/transactions/AssetTagAssignmentModal.vue";
import FavoriteTransactionSelector from "@/components/transactions/FavoriteTransactionSelector.vue";

const ExcelPanelLoading = defineComponent({
  name: "ExcelPanelLoading",
  setup() {
    return () =>
      h(
        "div",
        {
          class:
            "d-flex align-items-center gap-2 py-2 text-muted small border rounded-3 px-3 bg-light",
        },
        [
          h("span", {
            class: "spinner-border spinner-border-sm",
            role: "status",
            "aria-hidden": "true",
          }),
          h("span", "Loading Excel import…"),
        ]
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

const idParam = route.query.id ? Number(route.query.id) : null;
// Leer work_account_id de query params (como en contracts)
const workAccountParam = route.query.work_account_id
  ? Number(route.query.work_account_id)
  : route.query.work_account
  ? Number(route.query.work_account)
  : null; // Fallback para compatibilidad
const isEditMode = !!idParam;
const submitting = ref(false);
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
console.log("🔑 Soy isEditMode", isEditMode);
console.log("🔑 Work Account ID from query:", workAccountParam);
console.log("🔑 Viene desde schedule:", isFromSchedule.value);
// Header form
const form = reactive({
  document_type: null,
  builder: null,
  work_account: workAccountParam, // Prellenar desde query params si está disponible
  date: new Date().toISOString().slice(0, 10), // date format (YYYY-MM-DD)
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
const favoriteModalEditMode = ref(false);
const favoriteToEdit = ref(null);
const favoriteSelectorRef = ref(null);
const linesGridRef = ref(null);
/** Permite usar la rejilla sin tipo de documento tras importar líneas desde un favorito */
const linesGridUnlockedByFavoriteImport = ref(false);

const linesGridDisabled = computed(
  () =>
    !form.document_type && !linesGridUnlockedByFavoriteImport.value
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
        console.log(
          "🔒 Manteniendo work_account desde schedule:",
          form.work_account
        );
      }
    }
  }
);

// Watcher para debug work_account
watch(
  () => form.work_account,
  (newValue, oldValue) => {
    console.log(
      "🔍 DEBUG TransactionForm: form.work_account changed from",
      oldValue,
      "to",
      newValue,
      "Type:",
      typeof newValue
    );
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

// Funciones helper para manejar modales
function showModal(modalId) {
  const modalElement = document.getElementById(modalId);
  if (modalElement) {
    if (typeof bootstrap !== "undefined" && bootstrap.Modal) {
      const modal = new bootstrap.Modal(modalElement);
      modal.show();
    } else if (typeof $ !== "undefined" && $.fn.modal) {
      $(modalElement).modal("show");
    } else {
      // Fallback: mostrar modal usando clases CSS
      modalElement.classList.add("show");
      modalElement.style.display = "block";
      modalElement.setAttribute("aria-modal", "true");
      modalElement.setAttribute("role", "dialog");

      // Agregar backdrop
      const backdrop = document.createElement("div");
      backdrop.className = "modal-backdrop fade show";
      backdrop.id = "modal-backdrop";
      document.body.appendChild(backdrop);

      // Agregar clase al body
      document.body.classList.add("modal-open");
    }
  }
}

// Funciones para manejar favoritos
function openFavoriteModal() {
  favoriteModalEditMode.value = false;
  favoriteToEdit.value = null;
  showModal("transactionFavoriteModal");
}

async function onFavoriteSelected(favoriteData) {
  if (!favoriteData) {
    // Limpiar selección
    selectedFavoriteId.value = null;
    return;
  }

  console.log("🔍 Importing favorite:", favoriteData);

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
    form.date = docData.date || new Date().toISOString().slice(0, 10);
    form.notes = docData.notes || "";
    form.is_active = docData.is_active !== undefined ? docData.is_active : true;
  }

  if (hasIncomingLines) {
    console.log("🔍 Original lines_data:", incomingRaw);
    console.log(
      "🔍 Imported lines with product_label:",
      importedLines.map((l) => ({
        product: l.product,
        product_label: l.product_label,
      }))
    );

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

  console.log("✅ Favorite imported successfully");
}

function onEditFavorite(favoriteData) {
  favoriteModalEditMode.value = true;
  favoriteToEdit.value = favoriteData;
  showModal("transactionFavoriteModal");
}

function onFavoriteSaved(favorite) {
  console.log("✅ Favorite saved:", favorite);
  // Refrescar el selector de favoritos para mostrar el nuevo favorito
  refreshFavoriteSelector();
}

function onFavoriteUpdated(favorite) {
  console.log("✅ Favorite updated:", favorite);
  // Opcional: mostrar mensaje de éxito o actualizar UI
}

function onFavoriteDeleted(favoriteId) {
  console.log("✅ Favorite deleted:", favoriteId);
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

    console.log(
      "🔄 Updating favorite with current transaction data:",
      updateData
    );

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

      console.log("✅ Favorite updated successfully:", response.data);
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
  form.date = new Date().toISOString().slice(0, 10);
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
  submitting.value = true;
  clearErrors();
  try {
    const payload = normalizePayload();

    console.log("🚀 Frontend: Guardando y agregando otra transacción...");

    const { data } = await axios.post("/api/documents/", payload);
    await Swal.fire({
      title: "Transaction Saved Successfully!",
      text: "The transaction has been saved. You can now create another one.",
      icon: "success",
      timer: 2000,
      showConfirmButton: false,
    });
    resetFormForNewTransaction();

    console.log(
      "✅ Transacción guardada, formulario reseteado para nueva transacción"
    );
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
        Authorization: `Token ${localStorage.getItem("authToken")}`,
      },
    });

    if (!response.data || !response.data.file) {
      throw new Error("No se recibió el archivo PDF");
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
      text: "No se pudo generar el PDF del documento. Por favor, intente nuevamente.",
      confirmButtonText: "Aceptar",
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
      params: { active_only: true },
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
  try {
    const { data } = await axios.get(`/api/documents/${id}/`);
    // console.log("💊Soy loadDocument")
    // console.log('🔍 TransactionForm: Document data received:', data)
    // console.log('🔍 TransactionForm: document_type from API:', data.document_type, typeof data.document_type)
    // console.log('🔍 TransactionForm: builder from API:', data.builder, typeof data.builder)
    // console.log('📍 TransactionForm: work_account from API:', data.work_account, typeof data.work_account)

    // Verificar que los datos relacionados existen
    if (!data.document_type) {
      console.warn("Document type not found, setting to null");
      form.document_type = null;
    } else {
      form.document_type = data.document_type;
      console.log(
        "🔍 TransactionForm: form.document_type set to:",
        form.document_type
      );
    }

    if (!data.builder) {
      console.warn("Builder not found, setting to null");
      form.builder = null;
    } else {
      // Verificar que el builder existe antes de asignarlo
      try {
        await axios.get(`/api/builder/${data.builder}/`);
        form.builder = data.builder;
        console.log("🔍 TransactionForm: form.builder set to:", form.builder);
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
      console.log("Work account is null/empty, setting to null");
      form.work_account = null;
    } else {
      console.log(
        "🔍 DEBUG: Work account found:",
        data.work_account,
        "Type:",
        typeof data.work_account
      );
      console.log("🔍 DEBUG: Document ID:", data.id, "Type:", typeof data.id);

      // Verificar que el work_account existe antes de asignarlo
      try {
        await axios.get(`/api/work-accounts/${data.work_account}/`);
        form.work_account = data.work_account;
        console.log(
          "🔍 TransactionForm: form.work_account set to:",
          form.work_account
        );
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

    form.date = data.date
      ? new Date(data.date).toISOString().slice(0, 10)
      : new Date().toISOString().slice(0, 10);
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
      console.log("🔍 Frontend: Línea cargada desde API:", {
        original: {
          product: l.product,
          unit: l.unit,
          warehouse: l.warehouse,
          price_type: l.price_type,
          brand: l.brand,
        },
        normalized: {
          product: normalizedLine.product,
          unit: normalizedLine.unit,
          warehouse: normalizedLine.warehouse,
          price_type: normalizedLine.price_type,
          brand: normalizedLine.brand,
        },
      });

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
  console.log("🔍 Frontend normalizePayload - work_account:", {
    original: form.work_account,
    workAccountToUse: workAccountToUse,
    workAccountParam: workAccountParam,
    isFromSchedule: isFromSchedule.value,
    type: typeof workAccountToUse,
    normalized: workAccountId,
    normalizedType: typeof workAccountId,
  });

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
        console.log("🔍 Frontend: Línea normalizada:", {
          original: {
            product: l.product,
            unit: l.unit,
            warehouse: l.warehouse,
            price_type: l.price_type,
            brand: l.brand,
          },
          normalized: {
            product: normalizedLine.product,
            unit: normalizedLine.unit,
            warehouse: normalizedLine.warehouse,
            price_type: normalizedLine.price_type,
            brand: normalizedLine.brand,
          },
        });

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
  console.log("🔍 Frontend: applyServerErrors called with:", errData);

  // High-level document errors
  for (const k in errData) {
    if (k !== "lines") {
      errors[k] = errData[k];
      console.log(`🔍 Frontend: Error for field ${k}:`, errData[k]);
    }
  }

  // Per-line errors (DRF devuelve lista alineada con índices)
  if (Array.isArray(errData.lines)) {
    console.log("🔍 Frontend: Processing line errors:", errData.lines);
    errData.lines.forEach((item, idx) => {
      if (!item) return;
      const target = lines.value[idx];
      if (!target) return;
      target._errors = { ...(item || {}) };
    });
  } else if (errData.lines && typeof errData.lines === "object") {
    // Formato objeto { "0": {...}, "1": {...} }
    console.log(
      "🔍 Frontend: Processing line errors (object format):",
      errData.lines
    );
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
  submitting.value = true;
  clearErrors();
  try {
    const payload = normalizePayload();

    // 🔍 DEBUG: Log del payload completo
    console.log(
      "🚀 Frontend: Enviando payload:",
      JSON.stringify(payload, null, 2)
    );
    console.log("📊 Frontend: Líneas a enviar:", payload.lines.length);
    payload.lines.forEach((line, idx) => {
      console.log(`📝 Frontend: Línea ${idx}:`, {
        id: line.id,
        product: line.product,
        quantity: line.quantity,
        unit: line.unit,
        unit_price: line.unit_price,
        warehouse: line.warehouse,
        price_type: line.price_type,
        brand: line.brand,
      });

      // 🔍 DEBUG: Verificar tipos de datos
      console.log(`🔍 Frontend: Tipos de datos línea ${idx}:`, {
        product_type: typeof line.product,
        unit_type: typeof line.unit,
        warehouse_type: typeof line.warehouse,
        price_type_type: typeof line.price_type,
        brand_type: typeof line.brand,
      });
    });

    const url = isEditMode ? `/api/documents/${idParam}/` : "/api/documents/";
    const method = isEditMode ? "put" : "post";
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
      console.log("💊 Frontend: errorMsg", errorMsg);

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
      console.log("✅ Work Account title loaded:", workAccountTitle.value);
    }
  } catch (error) {
    console.error("Error loading work account title:", error);
    workAccountTitle.value = `Work Account #${workAccountId}`;
  }
}

onMounted(async () => {
  console.log("TransactionForm mounted, loading data...");
  await Promise.all([fetchStaticOptions(), loadHasInventoryProducts()]);
  console.log("Units loaded:", unitsOptions.value.length);
  console.log("Warehouses loaded:", warehousesOptions.value.length);

  // Si hay work_account en query params (viene desde schedule), prellenarlo y cargar título
  if (workAccountParam) {
    console.log(
      "🔑 Prellenando work_account desde query params:",
      workAccountParam
    );
    form.work_account = workAccountParam;
    // Cargar el título del work account
    await loadWorkAccountTitle(workAccountParam);
  }

  if (isEditMode) {
    await loadDocument(idParam);
    // Si viene desde schedule y estamos editando, también cargar el título si no se cargó antes
    if (workAccountParam && !workAccountTitle.value && form.work_account) {
      await loadWorkAccountTitle(form.work_account);
    }
  }
});
</script>

<style scoped>
.card-header {
  background-color: #f3f3f3;
}
.v-select {
  --vs-border-color: #ced4da;
}
.table-sticky thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #f8f9fa;
}

/* Ensure form controls are visible */
.form-control,
.v-select {
  min-height: 38px;
}

/* Ensure buttons are visible and properly styled */
.btn {
  display: inline-block;
  padding: 0.375rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  border-radius: 0.25rem;
  border: 1px solid transparent;
}

.btn-outline-secondary {
  color: #6c757d;
  border-color: #6c757d;
}

.btn-outline-secondary:hover {
  color: #fff;
  background-color: #869099;
  border-color: #869099;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  border-radius: 0.2rem;
}

/* Flex layout for select + buttons */
.d-flex.align-items-center .v-select {
  flex: 1;
  min-width: 0;
}

.d-flex.align-items-center .btn {
  flex-shrink: 0;
}

/* Fix for vue-select validation */
:deep(.is-invalid .vs__dropdown-toggle) {
  border-color: #dc3545;
}

:deep(.is-invalid .vs__dropdown-toggle:focus) {
  box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
}

/* Debug styles */
.debug-info {
  background: #f8f9fa;
  padding: 10px;
  margin: 10px 0;
  border-radius: 4px;
  font-size: 12px;
}

/* Mobile Responsive Styles */
@media (max-width: 768px) {
  .container-fluid {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }

  .card {
    margin-left: 0.25rem !important;
    margin-right: 0.25rem !important;
  }

  .card-header {
    padding: 0.75rem;
  }

  .card-body {
    padding: 1rem;
  }

  /* Ensure buttons don't overflow on mobile */
  .btn-sm {
    font-size: 0.8rem;
    padding: 0.375rem 0.5rem;
  }

  /* Make form labels more compact */
  .form-label {
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
  }

  /* Adjust input sizes for mobile */
  .form-control {
    font-size: 0.9rem;
  }

  /* Ensure proper spacing for mobile */
  .row.g-3 {
    --bs-gutter-x: 1rem;
    --bs-gutter-y: 0.75rem;
  }

  /* Adjust gaps for mobile */
  .d-flex.gap-1 > * + * {
    margin-left: 0.25rem;
  }

  .d-flex.gap-2 > * + * {
    margin-left: 0.5rem;
  }

  /* Make textarea more compact */
  textarea.form-control {
    resize: vertical;
    min-height: 60px;
  }
}

/* Tablet responsive adjustments */
@media (max-width: 992px) and (min-width: 769px) {
  .card {
    margin-left: 1rem !important;
    margin-right: 1rem !important;
  }
}

/* Ensure spinner is properly sized */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}
</style>
