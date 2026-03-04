<template>
  <div class="container mt-4">
    <div class="text-center mb-4">
      <h3 class="text-warning">Transaction Types</h3>
    </div>

    <div class="card shadow" style="height: auto">
      <div class="card-header d-flex justify-content-center align-items-center">
        <h6 class="mb-0 w-100 text-center text-primary">
          {{
            isViewMode
              ? "View Document Type"
              : isEditMode
              ? "Edit Document Type"
              : "New Document Type"
          }}
        </h6>
      </div>

      <div class="card-body">
        <form @submit.prevent="handleSubmit">
          <!-- Basic Information -->
          <div class="form-section mb-4">
            <h6 class="section-title">
              <i class="fas fa-info-circle me-2"></i>
              Basic Information
            </h6>
            <div class="row g-3 text-start px-3">
              <div class="col-md-6">
                <label for="type_code" class="form-label">
                  Type Code
                  <span class="text-danger">*</span>
                </label>
                <input
                  id="type_code"
                  v-model="form.type_code"
                  type="text"
                  class="form-control uppercase"
                  placeholder="Ex: INCOME, SUPRET"
                  v-tt
                  data-title="Unique code to identify the document type"
                  :disabled="isViewMode || submitting" />
              </div>
              <div class="col-md-6">
                <label for="description" class="form-label">
                  Description
                  <span class="text-danger">*</span>
                </label>
                <input
                  id="description"
                  v-model="form.description"
                  type="text"
                  class="form-control"
                  placeholder="Document type description"
                  v-tt
                  data-title="Descriptive name for the document type"
                  :disabled="isViewMode || submitting" />
              </div>
            </div>
          </div>

          <!-- Inventory Configuration -->
          <div class="form-section mb-4">
            <h6 class="section-title">
              <i class="fas fa-boxes me-2"></i>
              Inventory Configuration
            </h6>
            <div class="row g-3 text-start px-3">
              <div class="col-12 col-md-6 col-lg-4">
                <label for="stock_movement" class="form-label">
                  Stock Movement
                </label>
                <select
                  id="stock_movement"
                  v-model="form.stock_movement"
                  class="form-select"
                  v-tt
                  data-title="Defines how this document type affects inventory (entry, exit, or neutral)"
                  :disabled="isViewMode || submitting">
                  <option :value="1">+1 Entry</option>
                  <option :value="-1">-1 Exit</option>
                  <option :value="0">0 Neutral</option>
                </select>
              </div>
            </div>
            <div class="row g-3 mt-2 switches-row">
              <div class="col-12 col-md-6 col-lg-3">
                <div class="form-check form-switch switch-row">
                  <input
                    id="affects_physical"
                    v-model="form.affects_physical"
                    class="form-check-input"
                    type="checkbox"
                    v-tt
                    data-title="Affects physical inventory count"
                    :disabled="isViewMode || submitting" />
                  <label class="form-check-label" for="affects_physical">
                    Physical Inventory
                  </label>
                </div>
              </div>
              <div class="col-12 col-md-6 col-lg-3">
                <div class="form-check form-switch switch-row">
                  <input
                    id="affects_logical"
                    v-model="form.affects_logical"
                    class="form-check-input"
                    type="checkbox"
                    v-tt
                    data-title="Affects logical inventory tracking"
                    :disabled="isViewMode || submitting" />
                  <label class="form-check-label" for="affects_logical">
                    Logical Inventory
                  </label>
                </div>
              </div>
              <div class="col-12 col-md-6 col-lg-3">
                <div class="form-check form-switch switch-row">
                  <input
                    id="affects_accounting"
                    v-model="form.affects_accounting"
                    class="form-check-input"
                    type="checkbox"
                    v-tt
                    data-title="Affects accounting records and financial reports"
                    :disabled="isViewMode || submitting" />
                  <label class="form-check-label" for="affects_accounting">
                    Affects Accounting
                  </label>
                </div>
              </div>
              <div class="col-12 col-md-6 col-lg-3">
                <div class="form-check form-switch switch-row">
                  <input
                    id="warehouse_required"
                    v-model="form.warehouse_required"
                    class="form-check-input"
                    type="checkbox"
                    v-tt
                    data-title="Requires warehouse selection for this document type"
                    :disabled="isViewMode || submitting" />
                  <label class="form-check-label" for="warehouse_required">
                    Warehouse Required
                  </label>
                </div>
              </div>
              <div class="col-12 col-md-6 col-lg-3">
                <div class="form-check form-switch switch-row">
                  <input
                    id="creates_serialized_items"
                    v-model="form.creates_serialized_items"
                    class="form-check-input"
                    type="checkbox"
                    v-tt
                    data-title="Document type that creates/registers serialized items; opens the asset tag assignment modal when the document has serialized items (e.g. GRN)"
                    :disabled="isViewMode || submitting" />
                  <label class="form-check-label" for="creates_serialized_items">
                    Creates Serialized Items
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Business Configuration -->
          <div class="form-section mb-4">
            <h6 class="section-title">
              <i class="fas fa-briefcase me-2"></i>
              Business Configuration
            </h6>
            <div class="row g-3 switches-row">
              <div class="col-12 col-md-6 col-lg-4">
                <div class="form-check form-switch switch-row">
                  <input
                    id="is_purchase"
                    v-model="form.is_purchase"
                    class="form-check-input"
                    type="checkbox"
                    v-tt
                    data-title="For transactions with suppliers"
                    :disabled="isViewMode || submitting" />
                  <label class="form-check-label" for="is_purchase">
                    Purchase Document
                  </label>
                </div>
              </div>
              <div class="col-12 col-md-6 col-lg-4">
                <div class="form-check form-switch switch-row">
                  <input
                    id="is_sales"
                    v-model="form.is_sales"
                    class="form-check-input"
                    type="checkbox"
                    v-tt
                    data-title="For transactions with customers"
                    :disabled="isViewMode || submitting" />
                  <label class="form-check-label" for="is_sales">
                    Sales Document
                  </label>
                </div>
              </div>
              <div class="col-12 col-md-6 col-lg-4">
                <div class="form-check form-switch switch-row">
                  <input
                    id="is_taxable"
                    v-model="form.is_taxable"
                    class="form-check-input"
                    type="checkbox"
                    v-tt
                    data-title="Applies taxes to the document"
                    :disabled="isViewMode || submitting" />
                  <label class="form-check-label" for="is_taxable">
                    Subject to Taxes
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Operational Configuration -->
          <div class="form-section mb-4">
            <h6 class="section-title">
              <i class="fas fa-cogs me-2"></i>
              Operational Configuration
            </h6>
            <div class="row g-3 switches-row">
              <div class="col-12 col-md-6">
                <div class="form-check form-switch switch-row">
                  <input
                    id="is_operational"
                    v-model="form.is_operational"
                    class="form-check-input"
                    type="checkbox"
                    v-tt
                    data-title="Requires Work Account selection instead of Builder/Party"
                    :disabled="isViewMode || submitting" />
                  <label class="form-check-label" for="is_operational">
                    Operational Document
                  </label>
                </div>
              </div>
              <div class="col-12 col-md-6">
                <div class="form-check form-switch switch-row">
                  <input
                    id="allow_negative_sales"
                    v-model="form.allow_negative_sales"
                    class="form-check-input"
                    type="checkbox"
                    v-tt
                    data-title="Allow sales transactions even when stock is insufficient"
                    :disabled="isViewMode || submitting" />
                  <label class="form-check-label" for="allow_negative_sales">
                    Allow Negative Sales
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Status -->
          <div class="form-section mb-4">
            <h6 class="section-title">
              <i class="fas fa-toggle-on me-2"></i>
              Status
            </h6>
            <div class="row switches-row">
              <div class="col-12 col-md-6">
                <div class="form-check form-switch switch-row">
                  <input
                    id="is_active"
                    v-model="form.is_active"
                    class="form-check-input"
                    type="checkbox"
                    v-tt
                    data-title="Allows using this type in transactions"
                    :disabled="isViewMode || submitting" />
                  <label class="form-check-label" for="is_active">
                    Active Document Type
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="row mt-4">
            <div class="col-12">
              <div class="d-flex gap-3 justify-content-center">
                <button
                  type="submit"
                  class="btn btn-primary btn-rounded"
                  :disabled="isViewMode || submitting">
                  <span
                    v-if="submitting"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"></span>
                  <i v-else class="fas fa-save me-2"></i>
                  {{ submitting ? "Saving..." : "Save" }}
                </button>
                <button
                  type="button"
                  class="btn btn-secondary btn-rounded"
                  :disabled="submitting"
                  @click="handleCancel">
                  <i class="fas fa-arrow-left me-2"></i>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import Swal from "sweetalert2";
import * as bootstrap from "bootstrap";
// import { Tooltip } from 'bootstrap'
import "@assets/css/base.css";

const route = useRoute();
const router = useRouter();

const emit = defineEmits(["saved", "cancel"]);

const props = defineProps({
  id: {
    type: [String, Number],
    default: null,
  },
  isModal: {
    type: Boolean,
    default: false,
  },
});

const submitting = ref(false);
const id = computed(() => props.id || route.query.id);
const isViewMode = computed(() => route.query.mode === "view");
const isEditMode = computed(() => !!id.value && !isViewMode.value);

const form = ref({
  type_code: "",
  description: "",
  affects_physical: true,
  affects_logical: true,
  affects_accounting: false,
  is_taxable: false,
  is_purchase: false,
  is_sales: false,
  warehouse_required: true,
  creates_serialized_items: false,
  is_operational: false,
  allow_negative_sales: false,
  stock_movement: 0,
  is_active: true,
});

onMounted(async () => {
  // initialize bootstrap tooltips
  //const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  //tooltipTriggerList.map(el => new Tooltip(el))

  if (id.value) {
    try {
      const { data } = await axios.get(`/api/document-types/${id.value}/`);
      form.value = data;
    } catch (error) {
      console.error("Error loading data:", error);
      Swal.fire("Oops!", "Error loading the document type.", "error");
    }
  }
});

const handleSubmit = async () => {
  if (isViewMode.value) return;

  try {
    submitting.value = true;

    // 1) Trim + validación mínima
    const trimmedData = {
      type_code: (form.value.type_code ?? "").trim(),
      description: (form.value.description ?? "").trim(),
      affects_physical: form.value.affects_physical,
      affects_logical: form.value.affects_logical,
      affects_accounting: form.value.affects_accounting,
      is_taxable: form.value.is_taxable,
      is_purchase: form.value.is_purchase,
      is_sales: form.value.is_sales,
      warehouse_required: form.value.warehouse_required,
      creates_serialized_items: form.value.creates_serialized_items,
      is_operational: form.value.is_operational,
      allow_negative_sales: form.value.allow_negative_sales,
      stock_movement: form.value.stock_movement,
      is_active: form.value.is_active,
    };

    // Validaciones requeridas
    if (!trimmedData.type_code) {
      await Swal.fire("Validation", "Type Code is required.", "warning");
      return;
    }
    if (!trimmedData.description) {
      await Swal.fire("Validation", "Description is required.", "warning");
      return;
    }

    // Validaciones de longitud
    if (trimmedData.type_code.length > 10) {
      await Swal.fire(
        "Validation",
        "Type Code cannot exceed 10 characters.",
        "warning"
      );
      return;
    }
    if (trimmedData.description.length > 200) {
      await Swal.fire(
        "Validation",
        "Description cannot exceed 200 characters.",
        "warning"
      );
      return;
    }

    // 2) Guardar
    let savedData;
    if (isEditMode.value) {
      const response = await axios.put(
        `/api/document-types/${id.value}/`,
        trimmedData
      );
      savedData = response.data;
    } else {
      const response = await axios.post("/api/document-types/", trimmedData);
      savedData = response.data;
    }

    // Emit saved event for modal usage
    emit("saved", savedData);

    // Solo redirigir si NO estamos en modal
    if (!props.isModal) {
      goList();
    }
  } catch (error) {
    console.error("Error saving document type:", error);
    const { status, data } = error?.response || {};

    if (status === 400 && data) {
      const messages = Object.entries(data)
        .map(
          ([field, msgs]) =>
            `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`
        )
        .join("\n");
      await Swal.fire(
        "Oops!",
        messages || "There were validation errors.",
        "error"
      );
    } else if (status === 403) {
      await Swal.fire(
        "Forbidden",
        "You do not have permission for this action.",
        "error"
      );
    } else if (status === 409) {
      await Swal.fire(
        "Protected",
        "This document type is in use and cannot be modified.",
        "error"
      );
    } else {
      await Swal.fire("Oops!", "Error saving the document type.", "error");
    }
  } finally {
    submitting.value = false;
  }
};

const goList = () => {
  // Redirección por NOMBRE 'document-types' (con fallback al path)
  router.push({ name: "document-types" }).catch(() => {
    router.push("/document-types");
  });
};

const handleCancel = () => {
  if (props.isModal) {
    // En modal, emitir evento para cerrar
    emit("cancel");
  } else {
    // En página normal, redirigir a lista
    goList();
  }
};
</script>

<style scoped>
/* Espaciado adicional para secciones */
.form-section {
  padding: 1.5rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.form-section:last-of-type {
  border-bottom: none;
}

/* Título de sección: margen inferior para separar del contenido */
.form-section .section-title {
  margin-bottom: 1rem;
}

/* Filas de switches: margen izquierdo para indentar respecto al título */
.form-section .row.switches-row {
  margin-left: 0;
  margin-right: 0;
  margin-top: 0.5rem;
  padding-left: 2rem;
}
.form-section .row.switches-row > [class*="col"] {
  padding-left: 0;
  padding-right: 0.75rem;
  margin-bottom: 0.5rem;
}

/* Switch y label pegados: poco espacio entre toggle y texto */
.switch-row {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: nowrap;
}
.switch-row .form-check-input {
  flex-shrink: 0;
}
.switch-row .form-check-label {
  cursor: pointer;
  white-space: nowrap;
}

/* Mejoras de accesibilidad y contraste */
.text-danger {
  color: #dc2626 !important;
  font-weight: 600;
}

/* Ajustes responsive */
@media (max-width: 768px) {
  .card-modern,
  .card {
    padding: 1.5rem 1.25rem;
  }

  .section-title {
    font-size: 1.1rem;
  }

  .main-title {
    font-size: 1.75rem;
  }
}
</style>
