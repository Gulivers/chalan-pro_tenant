<template>
  <JRPage>
    <JRPageHeader :title="formTitle">
      <template #actions>
        <JRButton
          type="button"
          variant="secondary"
          size="sm"
          :disabled="submitting"
          @click="goBack">
          Back
        </JRButton>
        <JRButton
          v-if="!isViewMode && !isReverted"
          type="button"
          variant="primary"
          size="sm"
          :disabled="submitting || loading"
          @click="handleSubmit">
          {{ submitting ? "Saving..." : "Save" }}
        </JRButton>
      </template>
    </JRPageHeader>

    <div class="jr-transfer-form">
      <p v-if="loadError" class="jr-form-banner" role="alert">{{ loadError }}</p>
      <p v-else-if="loading" class="jr-transfer-form__status" role="status">
        Loading inventory transfer…
      </p>

      <form
        v-else
        class="jr-transfer-form__form"
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
            label="From Warehouse"
            inputId="transfer-from-warehouse"
            required
            hint="Origin warehouse. Must differ from To Warehouse."
            :error="fieldErrors.from_warehouse">
            <JRSelect
              inputId="transfer-from-warehouse"
              v-model="form.from_warehouse"
              :options="warehousesOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Select warehouse…"
              :disabled="isReadOnly"
              :invalid="invalid"
              :required="true"
              :ariaDescribedby="describedby"
              filter
              @update:modelValue="clearFieldError('from_warehouse')" />
          </JRField>

          <JRField
            v-slot="{ describedby, invalid }"
            label="To Warehouse"
            inputId="transfer-to-warehouse"
            required
            hint="Destination warehouse. Must differ from From Warehouse."
            :error="fieldErrors.to_warehouse">
            <JRSelect
              inputId="transfer-to-warehouse"
              v-model="form.to_warehouse"
              :options="warehousesOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Select warehouse…"
              :disabled="isReadOnly"
              :invalid="invalid"
              :required="true"
              :ariaDescribedby="describedby"
              filter
              @update:modelValue="clearFieldError('to_warehouse')" />
          </JRField>

          <JRField
            v-slot="{ describedby, invalid }"
            label="Description"
            inputId="transfer-description"
            hint="Optional reference for this transfer."
            :error="fieldErrors.description">
            <JRInput
              inputId="transfer-description"
              v-model="form.description"
              placeholder="Description of the transfer"
              :disabled="isReadOnly"
              :invalid="invalid"
              :ariaDescribedby="describedby"
              @update:modelValue="clearFieldError('description')" />
          </JRField>
        </div>

        <div v-if="form.id" class="jr-transfer-form__meta">
          <JRBadge
            v-if="form.status === 'completed' || form.status === 'reverted'"
            :value="form.status"
            :severity="form.status === 'reverted' ? 'danger' : 'success'" />
          <span v-else-if="form.status" class="jr-transfer-form__meta-text">
            Status: {{ form.status }}
          </span>
          <span v-if="form.created_at" class="jr-transfer-form__meta-text">
            Created: {{ formatDateTime(form.created_at) }}
          </span>
          <span v-if="form.last_updated" class="jr-transfer-form__meta-text">
            Updated: {{ formatDateTime(form.last_updated) }}
          </span>
          <span
            v-if="form.created_by_username"
            class="jr-transfer-form__meta-text">
            By: {{ form.created_by_username }}
          </span>
        </div>

        <Message
          v-if="isReverted"
          severity="warn"
          :closable="false"
          class="jr-transfer-form__message">
          This transfer is reverted and cannot be edited.
        </Message>

        <section class="jr-transfer-form__lines" aria-labelledby="transfer-lines-heading">
          <h2 id="transfer-lines-heading" class="jr-transfer-form__lines-title">
            Lines
          </h2>
          <p class="jr-transfer-form__lines-hint">
            Each line creates an OUT movement from the origin warehouse and an
            IN movement to the destination warehouse.
          </p>

          <TransferLinesGrid
            v-if="canShowLines"
            ref="linesGridRef"
            v-model:lines="form.lines"
            :from-warehouse-id="form.from_warehouse"
            :to-warehouse-id="form.to_warehouse"
            :warehouses-options="warehousesOptions"
            :units-options="unitsOptions"
            :is-read-only="isReadOnly" />
          <Message
            v-else
            severity="info"
            :closable="false"
            class="jr-transfer-form__message">
            Select From Warehouse and To Warehouse (they must be different) to
            add lines.
          </Message>
        </section>

        <div class="jr-transfer-form__actions">
          <JRButton
            v-if="!isViewMode && !isReverted"
            type="submit"
            variant="primary"
            :disabled="submitting">
            {{ submitting ? "Saving..." : "Save" }}
          </JRButton>
          <JRButton
            type="button"
            variant="secondary"
            :disabled="submitting"
            @click="goBack">
            {{ isViewMode || isReverted ? "Back" : "Cancel" }}
          </JRButton>
        </div>

        <p class="jr-transfer-form__required-note">
          <span class="jr-transfer-form__required-mark" aria-hidden="true"
            >*</span
          >
          Indicates required fields.
        </p>
      </form>
    </div>
  </JRPage>
</template>

<script setup>
import { ref, computed, onMounted, getCurrentInstance } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import Message from "primevue/message";
import {
  JRPage,
  JRPageHeader,
  JRField,
  JRInput,
  JRSelect,
  JRButton,
  JRBadge,
} from "@ui";
import TransferLinesGrid from "./TransferLinesGrid.vue";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === "inventory-transfer-view");
const isEditMode = computed(
  () => !!id && route.name === "inventory-transfer-edit"
);

const submitting = ref(false);
const loading = ref(false);
const loadError = ref("");
const formBanner = ref("");
const formBannerEl = ref(null);
const warehousesOptions = ref([]);
const unitsOptions = ref([]);
const linesGridRef = ref(null);
const fieldErrors = ref({});

const form = ref({
  id: null,
  from_warehouse: null,
  to_warehouse: null,
  description: "",
  status: "",
  created_at: null,
  last_updated: null,
  created_by_username: null,
  lines: [],
});

const isReverted = computed(() => form.value.status === "reverted");
const isReadOnly = computed(
  () => isViewMode.value || isReverted.value || submitting.value
);
const canShowLines = computed(
  () =>
    form.value.from_warehouse &&
    form.value.to_warehouse &&
    form.value.from_warehouse !== form.value.to_warehouse
);

const formTitle = computed(() => {
  if (isViewMode.value) return "View Inventory Transfer";
  if (isEditMode.value) return "Edit Inventory Transfer";
  return "New Inventory Transfer";
});

function formatDateTime(val) {
  if (!val) return "—";
  const d = new Date(val);
  if (Number.isNaN(d.getTime())) return val;
  return d.toLocaleString();
}

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
  if (formBanner.value) formBanner.value = "";
}

function focusBanner() {
  if (!formBannerEl.value) return;
  formBannerEl.value.focus?.();
}

function goBack() {
  router.push({ name: "inventory-transfer-list" });
}

function buildPayload() {
  const payload = {
    from_warehouse: form.value.from_warehouse,
    to_warehouse: form.value.to_warehouse,
    description: form.value.description || "",
  };
  const lines = (form.value.lines || []).filter(
    (l) =>
      l.product &&
      ((l.isSerialized && l.serialized_item) ||
        (!l.isSerialized && l.quantity > 0))
  );
  payload.lines = lines.map((l) => ({
    product_id: l.product,
    quantity: Number(l.quantity) || 1,
    unit_id: l.unit || null,
    serialized_item_id: l.isSerialized ? l.serialized_item : null,
  }));
  return payload;
}

function applyServerErrors(data) {
  const next = {};
  if (data && typeof data === "object") {
    Object.entries(data).forEach(([field, msgs]) => {
      if (field === "detail" || field === "error" || field === "lines") return;
      const text = Array.isArray(msgs) ? msgs.join(", ") : String(msgs);
      if (text) next[field] = text;
    });
  }
  fieldErrors.value = next;
  const detail =
    (data && (data.detail || data.error || data.non_field_errors)) ||
    Object.values(next).join(" ");
  formBanner.value =
    (Array.isArray(detail) ? detail.join(", ") : detail) ||
    "There were validation errors.";
}

async function handleSubmit() {
  if (isViewMode.value || isReverted.value) return;

  fieldErrors.value = {};
  formBanner.value = "";

  if (!form.value.from_warehouse) {
    fieldErrors.value = { from_warehouse: "From Warehouse is required" };
    formBanner.value = "From Warehouse is required";
    focusBanner();
    return;
  }
  if (!form.value.to_warehouse) {
    fieldErrors.value = { to_warehouse: "To Warehouse is required" };
    formBanner.value = "To Warehouse is required";
    focusBanner();
    return;
  }
  if (form.value.from_warehouse === form.value.to_warehouse) {
    fieldErrors.value = {
      to_warehouse: "To Warehouse must be different from From Warehouse",
    };
    formBanner.value =
      "To Warehouse must be different from From Warehouse";
    focusBanner();
    return;
  }
  if (!linesGridRef.value?.validateLines?.()) {
    formBanner.value = "Fix the line errors before saving.";
    focusBanner();
    return;
  }

  const payload = buildPayload();
  if (!payload.lines.length) {
    formBanner.value = "Add at least one line.";
    focusBanner();
    return;
  }

  submitting.value = true;
  try {
    const url = id
      ? `/api/inventory-transfers/${id}/`
      : "/api/inventory-transfers/";
    const method = id ? "put" : "post";
    await axios[method](url, payload);
    proxy?.notifyToastSuccess?.(id ? "Transfer updated." : "Transfer created.");
    router.push({ name: "inventory-transfer-list" });
  } catch (err) {
    if (err.response?.data) {
      const d = err.response.data;
      if (typeof d === "object") {
        applyServerErrors(d);
        if (d.lines) {
          (form.value.lines || []).forEach((row, i) => {
            if (d.lines[i])
              row._errors = { ...(row._errors || {}), ...d.lines[i] };
          });
        }
      } else {
        formBanner.value = "Error saving transfer.";
      }
    } else {
      formBanner.value = "Error saving transfer.";
    }
    focusBanner();
  } finally {
    submitting.value = false;
  }
}

async function loadOptions() {
  try {
    const [whRes, uRes] = await Promise.all([
      axios.get("/api/warehouses/?is_active=true"),
      axios.get("/api/unitsofmeasure/?is_active=true"),
    ]);
    const whList = Array.isArray(whRes.data)
      ? whRes.data
      : whRes.data?.results || [];
    const uList = Array.isArray(uRes.data)
      ? uRes.data
      : uRes.data?.results || [];
    warehousesOptions.value = whList.map((w) => ({
      value: w.id,
      label: w.name,
    }));
    unitsOptions.value = uList.map((u) => ({
      value: u.id,
      label: u.code || u.name,
    }));
  } catch (e) {
    console.error("Error loading options:", e);
    formBanner.value = "Error loading warehouses or units.";
  }
}

async function loadTransfer() {
  if (!id) return;
  loading.value = true;
  loadError.value = "";
  try {
    const { data } = await axios.get(`/api/inventory-transfers/${id}/`);
    form.value = {
      id: data.id,
      from_warehouse: data.from_warehouse,
      to_warehouse: data.to_warehouse,
      description: data.description || "",
      status: data.status || "",
      created_at: data.created_at,
      last_updated: data.last_updated,
      created_by_username: data.created_by_username,
      lines: (data.lines || []).map((l) => ({
        __key: `line-${l.product_id}-${l.serialized_item_id || 0}`,
        product: l.product_id,
        product_label: l.product_name,
        quantity: l.quantity,
        unit: l.unit_id,
        serialized_item: l.serialized_item_id,
        isSerialized: !!l.serialized_item_id,
        serializedOptions: l.serialized_item_asset_tag
          ? [
              {
                value: l.serialized_item_id,
                label: l.serialized_item_asset_tag,
                status: l.serialized_item_status,
                condition: l.serialized_item_condition,
              },
            ]
          : [],
      })),
    };
  } catch (e) {
    loadError.value = "Error loading transfer.";
    proxy?.notifyToastError?.("Error loading transfer.");
    router.push({ name: "inventory-transfer-list" });
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  loading.value = !!id;
  await loadOptions();
  await loadTransfer();
  if (!id) loading.value = false;
});
</script>

<style scoped>
.jr-transfer-form__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-transfer-form__status {
  margin: 0;
  font-size: 0.8125rem;
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
}

@media (min-width: 1024px) {
  .jr-form-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.jr-transfer-form__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem 0.75rem;
}

.jr-transfer-form__meta-text {
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-transfer-form__message {
  margin: 0;
}

.jr-transfer-form__lines-title {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-transfer-form__lines-hint {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-transfer-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.jr-transfer-form__required-note {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-transfer-form__required-mark {
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
