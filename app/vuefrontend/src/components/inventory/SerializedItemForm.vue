<template>
  <JRPage>
    <JRPageHeader :title="formTitle" :description="formDescription">
      <template #actions>
        <JRButton
          v-if="
            isViewMode &&
            id &&
            hasPermission('appinventory.change_serializeditem')
          "
          variant="primary"
          size="sm"
          @click="goToEdit">
          Edit item
        </JRButton>
      </template>
    </JRPageHeader>

    <p v-if="loadError" class="jr-form-banner" role="alert">{{ loadError }}</p>
    <p v-else-if="loading" class="jr-serialized-form__status" role="status">
      Loading serialized item…
    </p>

    <form
      v-else
      class="jr-serialized-form"
      @submit.prevent="handleSubmit"
      novalidate>
      <p
        v-if="formBanner"
        ref="formBannerEl"
        class="jr-form-banner"
        role="alert"
        tabindex="-1">
        {{ formBanner }}
      </p>

      <div class="jr-form-grid">
        <JRField
          v-slot="{ describedby, invalid }"
          label="Product"
          required
          inputId="serialized-product"
          hint="Product with SERIALIZED tracking (equipment/tool)."
          :error="fieldErrors.product">
          <JRInput
            v-if="id"
            inputId="serialized-product"
            :modelValue="form.product_name"
            disabled
            :ariaDescribedby="describedby" />
          <JRSelect
            v-else
            inputId="serialized-product"
            :modelValue="form.product"
            :options="productOptions"
            optionLabel="label"
            optionValue="id"
            placeholder="Select product"
            :disabled="submitting"
            :invalid="invalid"
            :required="true"
            :ariaDescribedby="describedby"
            filter
            @show="loadProducts"
            @update:modelValue="onField('product', $event)" />
        </JRField>

        <JRField
          v-slot="{ describedby }"
          label="Serial Number"
          inputId="serialized-asset-tag"
          :hint="serialHint"
          :error="fieldErrors.asset_tag">
          <JRInput
            inputId="serialized-asset-tag"
            v-model="form.asset_tag"
            maxlength="100"
            placeholder="e.g. LQCH020233"
            disabled
            :ariaDescribedby="describedby" />
        </JRField>

        <JRField
          v-slot="{ describedby, invalid }"
          label="Current warehouse"
          required
          inputId="serialized-warehouse"
          hint="Warehouse where the equipment is located."
          :error="fieldErrors.current_warehouse">
          <JRInput
            v-if="id"
            inputId="serialized-warehouse"
            :modelValue="form.current_warehouse_name || '—'"
            disabled
            :ariaDescribedby="describedby" />
          <JRSelect
            v-else
            inputId="serialized-warehouse"
            :modelValue="form.current_warehouse"
            :options="warehouses"
            optionLabel="name"
            optionValue="id"
            placeholder="Select warehouse"
            :disabled="submitting"
            :invalid="invalid"
            :required="true"
            :ariaDescribedby="describedby"
            filter
            @show="loadWarehouses"
            @update:modelValue="onField('current_warehouse', $event)" />
        </JRField>

        <JRField
          v-slot="{ describedby }"
          label="Document"
          inputId="serialized-document">
          <JRInput
            inputId="serialized-document"
            :modelValue="form.document_display || '—'"
            disabled
            :ariaDescribedby="describedby" />
        </JRField>

        <JRField
          v-slot="{ describedby }"
          label="Document line"
          inputId="serialized-document-line">
          <JRInput
            inputId="serialized-document-line"
            :modelValue="form.document_line_display || '—'"
            disabled
            :ariaDescribedby="describedby" />
        </JRField>

        <JRField
          v-slot="{ describedby, invalid }"
          label="Status"
          required
          inputId="serialized-status"
          :error="fieldErrors.status">
          <JRSelect
            inputId="serialized-status"
            :modelValue="form.status"
            :options="statusOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Select status"
            :disabled="isViewMode || submitting"
            :invalid="invalid"
            :required="true"
            :ariaDescribedby="describedby"
            @update:modelValue="onField('status', $event)" />
        </JRField>

        <JRField
          v-slot="{ describedby, invalid }"
          label="Condition"
          required
          inputId="serialized-condition"
          :error="fieldErrors.condition">
          <JRSelect
            inputId="serialized-condition"
            :modelValue="form.condition"
            :options="conditionOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Select condition"
            :disabled="isViewMode || submitting"
            :invalid="invalid"
            :required="true"
            :ariaDescribedby="describedby"
            @update:modelValue="onField('condition', $event)" />
        </JRField>

        <JRField
          v-slot="{ describedby }"
          label="Purchase date"
          inputId="serialized-purchase-date"
          :error="fieldErrors.purchase_date">
          <JRInput
            inputId="serialized-purchase-date"
            v-model="form.purchase_date"
            type="date"
            disabled
            :ariaDescribedby="describedby" />
        </JRField>

        <JRField
          class="jr-serialized-form__notes"
          v-slot="{ describedby, invalid }"
          label="Notes"
          inputId="serialized-notes"
          :error="fieldErrors.notes">
          <JRTextarea
            inputId="serialized-notes"
            :modelValue="form.notes"
            rows="7"
            placeholder="Notes here..."
            :disabled="isViewMode || submitting"
            :invalid="invalid"
            :ariaDescribedby="describedby"
            @update:modelValue="onField('notes', $event)" />
        </JRField>
      </div>

      <p v-if="form.created_at" class="jr-serialized-form__meta">
        Created at: {{ formatDateTime(form.created_at) }}
      </p>

      <div class="jr-serialized-form__actions">
        <JRButton
          v-if="!isViewMode"
          type="submit"
          variant="primary"
          :disabled="submitting">
          {{ submitting ? "Saving..." : "Save" }}
        </JRButton>
        <JRButton
          type="button"
          variant="secondary"
          :disabled="submitting"
          @click="goList">
          {{ isViewMode ? "Back to list" : "Cancel" }}
        </JRButton>
      </div>

      <p class="jr-serialized-form__required-note">
        <span class="jr-serialized-form__required-mark" aria-hidden="true">*</span>
        Indicates required fields.
      </p>
    </form>
  </JRPage>
</template>

<script setup>
import axios from "axios";
import { onMounted, ref, computed, getCurrentInstance } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  JRPage,
  JRPageHeader,
  JRField,
  JRInput,
  JRSelect,
  JRTextarea,
  JRButton,
} from "@ui";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === "serialized-item-view");
const isEditMode = computed(() => !!id && !isViewMode.value);

const loading = ref(!!id);
const loadError = ref("");
const submitting = ref(false);
const formBanner = ref("");
const fieldErrors = ref({});
const formBannerEl = ref(null);
const products = ref([]);
const warehouses = ref([]);

const statusOptions = [
  { value: "Active", label: "Active" },
  { value: "Maintenance", label: "Maintenance" },
  { value: "Lost", label: "Lost" },
  { value: "Retired", label: "Retired" },
];

const conditionOptions = [
  { value: "ok", label: "OK" },
  { value: "damaged", label: "Damaged" },
  { value: "needs_repair", label: "Needs repair" },
];

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

const formDescription = computed(() => {
  if (isViewMode.value) return "Review equipment status and location details.";
  if (isEditMode.value) return "Update status, condition, and notes.";
  return "Create a serialized equipment unit.";
});

const serialHint = computed(() =>
  id
    ? "Unique serial; cannot be changed."
    : "Assigned when the item is created from a purchase."
);

const productOptions = computed(() =>
  (products.value || []).map((p) => ({
    id: p.id,
    label: p ? `${p.name} (${p.sku || ""})` : "",
  }))
);

function toDatePart(d) {
  if (!d) return "";
  const date = new Date(d);
  if (Number.isNaN(date.getTime())) return "";
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

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
}

function onField(key, value) {
  form.value[key] = value;
  clearFieldError(key);
}

function focusBanner() {
  const el = formBannerEl.value;
  if (el && typeof el.focus === "function") {
    el.focus();
  }
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
  loading.value = true;
  loadError.value = "";
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
    loadError.value = "Error loading the serialized item.";
  } finally {
    loading.value = false;
  }
}

function validate() {
  const next = {};
  if (!form.value.product) {
    next.product = "Product is required.";
  }
  if (!form.value.current_warehouse) {
    next.current_warehouse = "Current warehouse is required.";
  }
  fieldErrors.value = next;
  if (Object.keys(next).length) {
    formBanner.value = `${Object.keys(next).length} ${
      Object.keys(next).length === 1 ? "field needs" : "fields need"
    } attention`;
    return false;
  }
  formBanner.value = "";
  return true;
}

function mapApiErrors(data) {
  const next = {};
  const leftover = [];
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    formBanner.value =
      typeof data === "string" ? data : "Could not save. Try again.";
    return;
  }
  const known = [
    "product",
    "asset_tag",
    "status",
    "condition",
    "purchase_date",
    "current_warehouse",
    "notes",
  ];
  for (const [key, value] of Object.entries(data)) {
    if (value == null) continue;
    const msg = Array.isArray(value)
      ? value.map(String).join(" ")
      : typeof value === "object"
        ? Object.values(value).flat().map(String).join(" ")
        : String(value);
    if (known.includes(key)) next[key] = msg;
    else if (["detail", "__all__", "non_field_errors"].includes(key))
      leftover.push(msg);
    else leftover.push(msg);
  }
  fieldErrors.value = next;
  formBanner.value =
    leftover.filter(Boolean).join(" ") ||
    (Object.keys(next).length
      ? `${Object.keys(next).length} ${
          Object.keys(next).length === 1 ? "field needs" : "fields need"
        } attention`
      : "Could not save. Try again.");
}

async function handleSubmit() {
  if (isViewMode.value) return;
  if (!validate()) {
    focusBanner();
    return;
  }
  submitting.value = true;
  formBanner.value = "";
  fieldErrors.value = {};
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
    const status = err.response?.status;
    const data = err.response?.data;
    if (status === 400 && data) mapApiErrors(data);
    else if (status === 403)
      formBanner.value = "You do not have permission for this action.";
    else formBanner.value = "Error saving serialized item.";
    focusBanner();
  } finally {
    submitting.value = false;
  }
}

function goList() {
  router.push({ name: "serialized-item-list" });
}

function goToEdit() {
  if (!id) return;
  router.push({ name: "serialized-item-edit", params: { id } });
}

onMounted(async () => {
  if (id) {
    await Promise.all([loadData(), loadWarehouses()]);
  } else {
    loading.value = true;
    try {
      await Promise.all([loadProducts(), loadWarehouses()]);
    } finally {
      loading.value = false;
    }
  }
});
</script>

<style scoped>
.jr-serialized-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-serialized-form__status {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1rem;
}

@media (min-width: 768px) {
  .jr-form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .jr-serialized-form__notes {
    grid-column: 1 / -1;
  }
}

@media (min-width: 1024px) {
  .jr-form-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.jr-serialized-form__meta {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-serialized-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.jr-serialized-form__required-note {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-serialized-form__required-mark {
  color: var(--color-jr-danger-text);
}

.jr-form-banner {
  margin: 0;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
  background: var(--color-jr-danger-subtle);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
}
</style>
