<template>
  <div class="container mt-3">
    <div class="text-center">
      <h3 class="text-warning">Serialized Item</h3>
    </div>
    <div class="card shadow" style="height: auto">
      <div class="card-header d-flex justify-content-center align-items-center">
        <h6 class="mb-0 w-100 text-center text-primary">{{ formTitle }}</h6>
      </div>
      <div class="card-body text-start">
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="row">
            <!-- Columna izquierda -->
            <div class="col-md-6">
              <!-- Product: solo lectura (informativo) -->
              <div class="mb-3">
                <label class="form-label d-flex align-items-center gap-2">
                  Product <span class="text-danger">*</span>
                  <i
                    v-tt
                    class="fas fa-info-circle text-muted"
                    data-title="Product with SERIALIZED tracking (equipment/tool)"></i>
                </label>
                <input
                  v-if="id"
                  type="text"
                  class="form-control bg-light"
                  :value="form.product_name"
                  readonly
                  v-tt
                  data-title="Read-only. Product cannot be changed" />
                <v-select
                  v-else
                  :options="products"
                  v-model="form.product"
                  :reduce="(p) => p.id"
                  :label="(p) => (p ? `${p.name} (${p.sku || ''})` : '')"
                  placeholder="Select product"
                  :disabled="submitting"
                  :clearable="false"
                  @open="loadProducts"
                  v-tt
                  data-title="Required. Select a serialized product (equipment or tool)" />
              </div>

              <div class="mb-3">
                <label class="form-label d-flex align-items-center gap-2">
                  Asset tag
                  <i
                    v-tt
                    class="fas fa-info-circle text-muted"
                    data-title="Unique tag or QR identifier for this unit"></i>
                </label>
                <input
                  v-model.trim="form.asset_tag"
                  type="text"
                  class="form-control bg-light"
                  maxlength="100"
                  placeholder="e.g. LQCH020233"
                  disabled
                  v-tt
                  data-title="Unique tag/QR identifier for the equipment (cannot be changed)" />
                <small class="text-muted">Unique tag/QR identifier</small>
              </div>

              <!-- Current warehouse: input informativo en edición, selector en alta -->
              <div class="mb-3">
                <label class="form-label d-flex align-items-center gap-2">
                  Current warehouse <span class="text-danger">*</span>
                  <i
                    v-tt
                    class="fas fa-info-circle text-muted"
                    data-title="Warehouse where the equipment is located"></i>
                </label>
                <input
                  v-if="id"
                  type="text"
                  class="form-control bg-light"
                  :value="form.current_warehouse_name || '—'"
                  readonly
                  v-tt
                  data-title="Read-only. Warehouse where the equipment is stored" />
                <v-select
                  v-else
                  :options="warehouses"
                  v-model="form.current_warehouse"
                  :reduce="(w) => w.id"
                  label="name"
                  placeholder="Select warehouse"
                  :disabled="submitting"
                  @open="loadWarehouses"
                  v-tt
                  data-title="Required. Warehouse where the equipment is stored" />
              </div>

              <!-- Document: solo lectura (informativo) -->
              <div class="mb-3">
                <label class="form-label d-flex align-items-center gap-2">
                  Document
                  <i
                    v-tt
                    class="fas fa-info-circle text-muted"
                    data-title="Purchase or transaction document that created this item"></i>
                </label>
                <input
                  type="text"
                  class="form-control bg-light"
                  :value="form.document_display || '—'"
                  readonly
                  v-tt
                  data-title="Read-only. Document cannot be changed" />
              </div>

              <!-- Document line: solo lectura (informativo) -->
              <div class="mb-3">
                <label class="form-label d-flex align-items-center gap-2">
                  Document line
                  <i
                    v-tt
                    class="fas fa-info-circle text-muted"
                    data-title="Line of the document that created this serialized item"></i>
                </label>
                <input
                  type="text"
                  class="form-control bg-light"
                  :value="form.document_line_display || '—'"
                  readonly
                  v-tt
                  data-title="Read-only. Document line cannot be changed" />
              </div>
            </div>

            <!-- Columna derecha: Status, Condition, Purchase date (seguimiento) -->
            <div class="col-md-6">
              <div class="mb-3">
                <label class="form-label d-flex align-items-center gap-2">
                  Status <span class="text-danger">*</span>
                  <i
                    v-tt
                    class="fas fa-info-circle text-muted"
                    data-title="Current status of the equipment"></i>
                </label>
                <v-select
                  :options="statusOptions"
                  v-model="form.status"
                  :reduce="(s) => s.value"
                  label="label"
                  placeholder="Select status"
                  :disabled="isViewMode || submitting"
                  v-tt
                  data-title="Active, Maintenance, Lost, or Retired">
                  <template #option="option">
                    <span class="badge" :class="statusBadgeClass(option.value)">{{ option.label }}</span>
                  </template>
                  <template #selected-option="option">
                    <span v-if="option" class="badge" :class="statusBadgeClass(option.value)">{{ option.label }}</span>
                  </template>
                </v-select>
              </div>

              <div class="mb-3">
                <label class="form-label d-flex align-items-center gap-2">
                  Condition <span class="text-danger">*</span>
                  <i
                    v-tt
                    class="fas fa-info-circle text-muted"
                    data-title="Physical condition of the equipment"></i>
                </label>
                <v-select
                  :options="conditionOptions"
                  v-model="form.condition"
                  :reduce="(c) => c.value"
                  label="label"
                  placeholder="Select condition"
                  :disabled="isViewMode || submitting"
                  v-tt
                  data-title="OK, Damaged, or Needs repair">
                  <template #option="option">
                    <span class="badge" :class="conditionBadgeClass(option.value)">{{ option.label }}</span>
                  </template>
                  <template #selected-option="option">
                    <span v-if="option" class="badge" :class="conditionBadgeClass(option.value)">{{ option.label }}</span>
                  </template>
                </v-select>
              </div>

              <div class="mb-3">
                <label class="form-label d-flex align-items-center gap-2">
                  Purchase date
                  <i
                    v-tt
                    class="fas fa-info-circle text-muted"
                    data-title="Date when the equipment was acquired"></i>
                </label>
                <BFormInput
                  v-model="form.purchase_date"
                  type="date"
                  class="bg-light"
                  disabled
                  v-tt
                  data-title="Read-only. Use this form for status/condition tracking" />
              </div>

              <div class="mb-3">
                <label class="form-label d-flex align-items-center gap-2">
                  Notes
                  <i
                    v-tt
                    class="fas fa-info-circle text-muted"
                    data-title="Additional notes about this equipment"></i>
                </label>
                <textarea
                  v-model.trim="form.notes"
                  class="form-control"
                  rows="7"
                  placeholder="Notes here..."
                  :disabled="isViewMode || submitting"
                  v-tt
                  data-title="Additional notes about the equipment" />
              </div>

              <div v-if="form.created_at" class="mb-3 small text-muted">
                Created at: {{ formatDateTime(form.created_at) }}
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-center gap-2 mt-3">
            <button
              type="button"
              class="btn btn-secondary"
              :disabled="submitting"
              @click="goList">
              Cancel
            </button>
            <button
              v-if="!isViewMode"
              type="submit"
              class="btn btn-primary"
              :disabled="submitting">
              <span
                v-if="submitting"
                class="spinner-border spinner-border-sm me-1"
                role="status"></span>
              {{ submitting ? "Saving..." : "Save" }}
            </button>
          </div>
          <p class="small text-muted mt-3 mb-0">
            <span class="text-danger">*</span> Indicates required fields.
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import Swal from "sweetalert2";
import { onMounted, ref, computed, getCurrentInstance } from "vue";
import { useRoute, useRouter } from "vue-router";
import { BFormInput } from "bootstrap-vue-next";
import vSelect from "vue-select";
import "vue-select/dist/vue-select.css";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === "serialized-item-view");
const isEditMode = computed(() => !!id && !isViewMode.value);

const submitting = ref(false);
const products = ref([]);
const warehouses = ref([]);

const statusOptions = [
  { value: "Active", label: "Active" },
  { value: "Maintenance", label: "Maintenance" },
  { value: "Lost", label: "Lost" },
  { value: "Retired", label: "Retired" },
];

function statusBadgeClass(value) {
  const v = (value || "").trim();
  if (v === "Active") return "bg-success";
  if (v === "Maintenance") return "bg-warning text-dark";
  if (v === "Lost") return "bg-danger";
  if (v === "Retired") return "bg-secondary";
  return "bg-secondary";
}

const conditionOptions = [
  { value: "ok", label: "OK" },
  { value: "damaged", label: "Damaged" },
  { value: "needs_repair", label: "Needs repair" },
];

function conditionBadgeClass(value) {
  const v = (value || "").toLowerCase();
  if (v === "ok") return "bg-success";
  if (v === "damaged") return "bg-warning text-dark";
  if (v === "needs_repair") return "bg-danger";
  return "bg-secondary";
}

const form = ref({
  product: null,
  product_name: "",
  asset_tag: "",
  status: "Active",
  condition: "ok",
  purchase_date: "",
  current_warehouse: null,
  current_warehouse_name: "",
  document: null,
  document_display: "",
  document_line: null,
  document_line_display: "",
  notes: "",
  created_at: null,
});

const formTitle = computed(() => {
  if (isViewMode.value) return "View Serialized Item";
  if (isEditMode.value) return "Edit Serialized Item";
  return "Add Serialized Item";
});

function toDatePart(d) {
  if (!d) return "";
  const date = new Date(d);
  if (isNaN(date.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(
    date.getDate()
  )}`;
}

function formatDateTime(val) {
  if (!val) return "—";
  const d = new Date(val);
  return d.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function loadProducts() {
  if (products.value.length) return;
  try {
    const { data } = await axios.get("/api/products/", {
      params: { tracking_mode: "SERIALIZED", is_active: true },
    });
    products.value = data.results ?? data;
  } catch (err) {
    console.error("Load products error:", err);
  }
}

async function loadWarehouses() {
  if (warehouses.value.length) return;
  try {
    const { data } = await axios.get("/api/warehouses/", {
      params: { is_active: true },
    });
    warehouses.value = data.results ?? data;
  } catch (err) {
    console.error("Load warehouses error:", err);
  }
}

async function loadData() {
  if (!id) return;
  try {
    const { data } = await axios.get(`/api/serialized-items/${id}/`);
    form.value = {
      product: data.product ?? null,
      product_name: data.product_name ?? "",
      asset_tag: data.asset_tag ?? "",
      status: data.status ?? "Active",
      condition: data.condition ?? "ok",
      purchase_date: toDatePart(data.purchase_date),
      current_warehouse: data.current_warehouse ?? null,
      current_warehouse_name: data.current_warehouse_name ?? "",
      document: data.document ?? null,
      document_display: data.document_display ?? "",
      document_line: data.document_line ?? null,
      document_line_display: data.document_line_display ?? "",
      notes: data.notes ?? "",
      created_at: data.created_at ?? null,
    };
  } catch (err) {
    console.error("Load error:", err);
    await Swal.fire("Oops!", "Error loading the serialized item.", "error");
  }
}

function validate() {
  if (!form.value.product) {
    Swal.fire("Validation", "Product is required.", "warning");
    return false;
  }
  if (!form.value.current_warehouse) {
    Swal.fire("Validation", "Current warehouse is required.", "warning");
    return false;
  }
  return true;
}

async function handleSubmit() {
  if (!validate()) return;
  submitting.value = true;
  try {
    const payload = {
      asset_tag: form.value.asset_tag || null,
      status: form.value.status,
      condition: form.value.condition,
      purchase_date: form.value.purchase_date || null,
      current_warehouse: form.value.current_warehouse,
      notes: form.value.notes || null,
    };
    if (id) {
      await axios.patch(`/api/serialized-items/${id}/`, payload);
      proxy?.notifyToastSuccess?.("Serialized item updated.");
    } else {
      payload.product = form.value.product;
      await axios.post("/api/serialized-items/", payload);
      proxy?.notifyToastSuccess?.("Serialized item created.");
    }
    router.push({ name: "serialized-item-list" });
  } catch (err) {
    console.error("Save error:", err);
    const data = err.response?.data;
    let msg = "Error saving serialized item.";
    if (data) {
      if (typeof data === "string") msg = data;
      else if (data.detail)
        msg = Array.isArray(data.detail) ? data.detail.join(" ") : data.detail;
      else if (data.non_field_errors) msg = data.non_field_errors.join(" ");
      else msg = Object.values(data).flat().join(" ") || msg;
    }
    await Swal.fire("Validation Error", msg, "error");
  } finally {
    submitting.value = false;
  }
}

function goList() {
  router.push({ name: "serialized-item-list" });
}

onMounted(async () => {
  if (id) {
    // Edit/View: solo necesitamos el item y warehouses (Product es read-only)
    await Promise.all([loadData(), loadWarehouses()]);
  } else {
    // Add: productos y warehouses en paralelo
    await Promise.all([loadProducts(), loadWarehouses()]);
  }
});
</script>

<style scoped>
.v-select {
  --vs-border-color: #ced4da;
}
</style>
