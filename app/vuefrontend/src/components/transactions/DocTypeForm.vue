<template>
  <JRPage :class="{ 'jr-doctype-form--modal': isModal }">
    <JRPageHeader v-if="!isModal" :title="pageTitle" />

    <div class="jr-doctype-form">
      <p v-if="loading" class="jr-doctype-form__status" role="status">
        Loading document type…
      </p>

      <form
        v-else
        class="jr-doctype-form__form"
        @submit.prevent="handleSubmit"
        novalidate>
        <p v-if="isProtectedType" class="jr-doctype-form__note" role="status">
          The Material Request document type is required by the system and cannot be edited or deleted.
        </p>
        <JRSection title="Basic Information">
          <div class="jr-form-grid">
            <JRField
              v-slot="{ describedby, invalid }"
              label="Type Code"
              inputId="doctype-type-code"
              required
              hint="Unique code to identify the document type"
              :error="fieldErrors.type_code">
              <JRInput
                inputId="doctype-type-code"
                :modelValue="form.type_code"
                maxlength="20"
                placeholder="Ex: INCOME, SUPRET"
                class="jr-doctype-form__code"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="onTypeCodeInput" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Description"
              inputId="doctype-description"
              required
              :error="fieldErrors.description">
              <JRInput
                inputId="doctype-description"
                v-model="form.description"
                maxlength="200"
                placeholder="Document type description"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('description')" />
            </JRField>
          </div>
        </JRSection>

        <JRSection title="Inventory Configuration">
          <div class="jr-form-grid">
            <JRField
              v-slot="{ describedby }"
              label="Stock Movement"
              inputId="doctype-stock-movement"
              hint="Defines how this document type affects inventory (entry, exit, or neutral)">
              <JRSelect
                inputId="doctype-stock-movement"
                v-model="form.stock_movement"
                :options="stockMovementOptions"
                optionLabel="label"
                optionValue="value"
                :disabled="isDisabled"
                :ariaDescribedby="describedby" />
            </JRField>
          </div>
          <div class="jr-form-checks">
            <JRField
              label="Physical Inventory"
              inputId="doctype-affects-physical"
              hint="Includes this document in the physical on-hand count.">
              <JRCheckbox
                inputId="doctype-affects-physical"
                v-model="form.affects_physical"
                ariaLabel="Physical Inventory"
                :disabled="isDisabled" />
            </JRField>
            <JRField
              label="Logical Inventory"
              inputId="doctype-affects-logical"
              hint="Includes this document in the logical available count.">
              <JRCheckbox
                inputId="doctype-affects-logical"
                v-model="form.affects_logical"
                ariaLabel="Logical Inventory"
                :disabled="isDisabled" />
            </JRField>
            <JRField
              label="Affects Accounting"
              inputId="doctype-affects-accounting"
              hint="Includes this document in accounting inventory.">
              <JRCheckbox
                inputId="doctype-affects-accounting"
                v-model="form.affects_accounting"
                ariaLabel="Affects Accounting"
                :disabled="isDisabled" />
            </JRField>
            <JRField
              label="Warehouse Required"
              inputId="doctype-warehouse-required"
              hint="A warehouse must be selected on the document.">
              <JRCheckbox
                inputId="doctype-warehouse-required"
                v-model="form.warehouse_required"
                ariaLabel="Warehouse Required"
                :disabled="isDisabled" />
            </JRField>
            <JRField
              label="Creates Serialized Items"
              inputId="doctype-creates-serialized"
              hint="Opens asset tag assignment when the document has serialized items (e.g. GRN)"
              class="jr-form-checks__full">
              <JRCheckbox
                inputId="doctype-creates-serialized"
                v-model="form.creates_serialized_items"
                ariaLabel="Creates Serialized Items"
                :disabled="isDisabled" />
            </JRField>
          </div>
        </JRSection>

        <JRSection title="Business Configuration">
          <div class="jr-form-checks">
            <JRField
              label="Purchase Document"
              inputId="doctype-is-purchase"
              hint="Marks the document as a purchase (vendor side).">
              <JRCheckbox
                inputId="doctype-is-purchase"
                v-model="form.is_purchase"
                ariaLabel="Purchase Document"
                :disabled="isDisabled" />
            </JRField>
            <JRField
              label="Sales Document"
              inputId="doctype-is-sales"
              hint="Marks the document as a sale (customer side).">
              <JRCheckbox
                inputId="doctype-is-sales"
                v-model="form.is_sales"
                ariaLabel="Sales Document"
                :disabled="isDisabled" />
            </JRField>
            <JRField
              label="Subject to Taxes"
              inputId="doctype-is-taxable"
              hint="Tax applies to the lines of this document.">
              <JRCheckbox
                inputId="doctype-is-taxable"
                v-model="form.is_taxable"
                ariaLabel="Subject to Taxes"
                :disabled="isDisabled" />
            </JRField>
          </div>
        </JRSection>

        <JRSection title="Operational Configuration">
          <div class="jr-form-checks">
            <JRField
              label="Operational Document"
              inputId="doctype-is-operational"
              hint="Requires a Work Account. Material Request uses this flag.">
              <JRCheckbox
                inputId="doctype-is-operational"
                v-model="form.is_operational"
                ariaLabel="Operational Document"
                :disabled="isDisabled" />
            </JRField>
            <JRField
              label="Allow Negative Sales"
              inputId="doctype-allow-negative-sales"
              hint="Allow sales even when stock is insufficient">
              <JRCheckbox
                inputId="doctype-allow-negative-sales"
                v-model="form.allow_negative_sales"
                ariaLabel="Allow Negative Sales"
                :disabled="isDisabled" />
            </JRField>
          </div>
        </JRSection>

        <JRSection title="JobRhythm Assistant">
          <p class="jr-doctype-form__note">
            Map this type to analytics meanings. Codes like PINV or PO-INV can
            differ per tenant; these flags tell the Assistant how to classify
            transactions.
          </p>
          <div class="jr-form-checks">
            <JRField
              label="Net invoiced spending"
              inputId="doctype-net-invoiced"
              hint="Counts toward Assistant net invoiced spending. Leave off for orders and returns.">
              <JRCheckbox
                inputId="doctype-net-invoiced"
                v-model="form.counts_as_net_invoiced_spend"
                ariaLabel="Net invoiced spending"
                :disabled="isDisabled"
                @update:modelValue="onSpendIntentionChange" />
            </JRField>
            <JRField
              label="Job material issue"
              inputId="doctype-job-material"
              hint="Counts as material issued to a job, such as a picking.">
              <JRCheckbox
                inputId="doctype-job-material"
                v-model="form.counts_as_job_material_issue"
                ariaLabel="Job material issue"
                :disabled="isDisabled" />
            </JRField>
            <JRField
              label="Purchase return"
              inputId="doctype-purchase-return"
              hint="Counts as a purchase return, separate from net invoiced spending.">
              <JRCheckbox
                inputId="doctype-purchase-return"
                v-model="form.counts_as_purchase_return"
                ariaLabel="Purchase return"
                :disabled="isDisabled"
                @update:modelValue="onReturnIntentionChange" />
            </JRField>
          </div>
        </JRSection>

        <JRSection title="Status">
          <div class="jr-form-checks">
            <JRField
              label="Active Document Type"
              inputId="doctype-is-active"
              hint="Inactive types cannot be selected on new documents.">
              <JRCheckbox
                inputId="doctype-is-active"
                v-model="form.is_active"
                ariaLabel="Active Document Type"
                :disabled="isDisabled" />
            </JRField>
          </div>
        </JRSection>

        <div
          :class="[
            'jr-doctype-form__actions',
            { 'jr-doctype-form__actions--sticky': !isModal },
          ]">
          <template v-if="!isViewMode && !isProtectedType">
            <JRButton type="submit" variant="primary" :disabled="isDisabled">
              {{ submitting ? "Saving..." : "Save" }}
            </JRButton>
            <JRButton
              type="button"
              variant="secondary"
              :disabled="submitting"
              @click="handleCancel">
              Cancel
            </JRButton>
          </template>
          <JRButton
            v-else
            type="button"
            variant="secondary"
            :disabled="submitting"
            @click="handleCancel">
            Back
          </JRButton>
        </div>
      </form>
    </div>
  </JRPage>
</template>

<script setup>
import { ref, computed, onMounted, getCurrentInstance } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRInput,
  JRSelect,
  JRCheckbox,
  JRButton,
} from "@ui";

const route = useRoute();
const router = useRouter();
const { proxy } = getCurrentInstance();

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
const loading = ref(false);
const fieldErrors = ref({});

const id = computed(() => props.id || route.query.id || null);
const isViewMode = computed(() => route.query.mode === "view");
const isEditMode = computed(() => !!id.value && !isViewMode.value);
const loadedTypeCode = ref("");
const PROTECTED_TYPE_CODES = ["MR"];
const isProtectedType = computed(() =>
  PROTECTED_TYPE_CODES.includes((loadedTypeCode.value || "").toUpperCase())
);
const isDisabled = computed(
  () => isViewMode.value || submitting.value || isProtectedType.value
);

const pageTitle = computed(() => {
  if (isViewMode.value) return "View Document Type";
  if (isEditMode.value) return "Edit Document Type";
  return "New Document Type";
});

const stockMovementOptions = [
  { value: 1, label: "+1 Entry" },
  { value: -1, label: "-1 Exit" },
  { value: 0, label: "0 Neutral" },
];

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
  counts_as_net_invoiced_spend: false,
  counts_as_job_material_issue: false,
  counts_as_purchase_return: false,
  is_active: true,
});

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
}

function onTypeCodeInput(value) {
  form.value.type_code = (value ?? "").toString().toUpperCase();
  clearFieldError("type_code");
}

function onSpendIntentionChange(value) {
  form.value.counts_as_net_invoiced_spend = !!value;
  if (form.value.counts_as_net_invoiced_spend) {
    form.value.counts_as_purchase_return = false;
  }
}

function onReturnIntentionChange(value) {
  form.value.counts_as_purchase_return = !!value;
  if (form.value.counts_as_purchase_return) {
    form.value.counts_as_net_invoiced_spend = false;
  }
}

/** Suggest Assistant intentions from code/flags for new types only. */
function applyIntentionSuggestions() {
  if (id.value) return;
  const code = (form.value.type_code || "")
    .trim()
    .toUpperCase()
    .replace(/\s+/g, "");
  const compact = code.replace(/[-_]/g, "");
  if (compact === "PINV" || compact === "POINV" || code === "PO-INV") {
    form.value.counts_as_net_invoiced_spend = true;
    form.value.counts_as_purchase_return = false;
  } else if (compact === "PK" || compact === "PICK" || compact === "PICKING") {
    form.value.counts_as_job_material_issue = true;
  } else if (compact === "PRN" || compact === "PRET" || compact === "PURRET") {
    form.value.counts_as_purchase_return = true;
    form.value.counts_as_net_invoiced_spend = false;
  } else if (
    form.value.is_purchase &&
    !form.value.is_sales &&
    !form.value.is_operational &&
    form.value.affects_physical &&
    Number(form.value.stock_movement) === 1 &&
    compact !== "INIINV"
  ) {
    form.value.counts_as_net_invoiced_spend = true;
  } else if (
    form.value.is_operational &&
    Number(form.value.stock_movement) === -1
  ) {
    form.value.counts_as_job_material_issue = true;
  } else if (
    form.value.is_purchase &&
    !form.value.is_sales &&
    form.value.affects_physical &&
    Number(form.value.stock_movement) === -1
  ) {
    form.value.counts_as_purchase_return = true;
  }
}

function goList() {
  router.push({ name: "document-types" }).catch(() => {
    router.push("/document-types");
  });
}

function handleCancel() {
  if (props.isModal) {
    emit("cancel");
  } else {
    goList();
  }
}

onMounted(async () => {
  if (isViewMode.value && !id.value) {
    proxy?.notifyToastError?.("No record to view.");
    if (!props.isModal) goList();
    return;
  }

  if (id.value) {
    loading.value = true;
    try {
      const { data } = await axios.get(`/api/document-types/${id.value}/`);
      loadedTypeCode.value = data.type_code || "";
      form.value = {
        type_code: data.type_code || "",
        description: data.description || "",
        affects_physical: !!data.affects_physical,
        affects_logical: !!data.affects_logical,
        affects_accounting: !!data.affects_accounting,
        is_taxable: !!data.is_taxable,
        is_purchase: !!data.is_purchase,
        is_sales: !!data.is_sales,
        warehouse_required: !!data.warehouse_required,
        creates_serialized_items: !!data.creates_serialized_items,
        is_operational: !!data.is_operational,
        allow_negative_sales: !!data.allow_negative_sales,
        stock_movement: Number(data.stock_movement ?? 0),
        counts_as_net_invoiced_spend: !!data.counts_as_net_invoiced_spend,
        counts_as_job_material_issue: !!data.counts_as_job_material_issue,
        counts_as_purchase_return: !!data.counts_as_purchase_return,
        is_active: !!data.is_active,
      };
    } catch (error) {
      console.error("Error loading data:", error);
      proxy?.notifyToastError?.("Error loading the document type.");
      if (!props.isModal) goList();
    } finally {
      loading.value = false;
    }
  }
});

const handleSubmit = async () => {
  if (isViewMode.value || isProtectedType.value) return;

  try {
    submitting.value = true;
    fieldErrors.value = {};

    if (!id.value) {
      applyIntentionSuggestions();
    }

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
      counts_as_net_invoiced_spend: !!form.value.counts_as_net_invoiced_spend,
      counts_as_job_material_issue: !!form.value.counts_as_job_material_issue,
      counts_as_purchase_return: !!form.value.counts_as_purchase_return,
      is_active: form.value.is_active,
    };

    if (!trimmedData.type_code) {
      fieldErrors.value = { type_code: "Type Code is required." };
      proxy?.notifyToastError?.("Type Code is required.");
      return;
    }
    if (!trimmedData.description) {
      fieldErrors.value = { description: "Description is required." };
      proxy?.notifyToastError?.("Description is required.");
      return;
    }
    if (trimmedData.type_code.length > 20) {
      fieldErrors.value = {
        type_code: "Type Code cannot exceed 20 characters.",
      };
      proxy?.notifyToastError?.("Type Code cannot exceed 20 characters.");
      return;
    }
    if (trimmedData.description.length > 200) {
      fieldErrors.value = {
        description: "Description cannot exceed 200 characters.",
      };
      proxy?.notifyToastError?.(
        "Description cannot exceed 200 characters."
      );
      return;
    }

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

    emit("saved", savedData);
    proxy?.notifyToastSuccess?.(
      isEditMode.value ? "Document type updated." : "Document type created."
    );

    if (!props.isModal) {
      goList();
    }
  } catch (error) {
    console.error("Error saving document type:", error);
    const { status, data } = error?.response || {};

    if (status === 400 && data) {
      const next = {};
      Object.entries(data).forEach(([field, msgs]) => {
        if (field === "detail" || field === "non_field_errors") return;
        next[field] = Array.isArray(msgs) ? msgs.join(", ") : String(msgs);
      });
      fieldErrors.value = next;
      const messages = Object.entries(data)
        .map(
          ([field, msgs]) =>
            `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`
        )
        .join("\n");
      proxy?.notifyToastError?.(
        messages || "There were validation errors."
      );
    } else if (status === 403) {
      proxy?.notifyToastError?.(
        "You do not have permission for this action."
      );
    } else if (status === 409) {
      proxy?.notifyToastError?.(
        "This document type is in use and cannot be modified."
      );
    } else {
      proxy?.notifyToastError?.("Error saving the document type.");
    }
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
:deep(.jr-page.jr-doctype-form--modal),
.jr-page.jr-doctype-form--modal {
  padding: 0;
  min-height: 0;
}

.jr-doctype-form__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-doctype-form__status,
.jr-doctype-form__note {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-doctype-form__note {
  margin-bottom: 0.75rem;
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

.jr-form-checks {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.75rem 1rem;
  margin-top: 1rem;
}

@media (min-width: 768px) {
  .jr-form-checks {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .jr-form-checks__full {
    grid-column: 1 / -1;
  }
}

@media (min-width: 1024px) {
  .jr-form-checks {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.jr-doctype-form :deep(.jr-checkbox) {
  column-gap: 0.85rem;
  align-items: center;
}

.jr-doctype-form :deep(.jr-checkbox__label) {
  margin-inline-start: 0.15rem;
}

.jr-doctype-form__code :deep(.p-inputtext) {
  text-transform: uppercase;
}

.jr-doctype-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.jr-doctype-form__actions--sticky {
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.25rem;
  margin-top: 0.5rem;
  background: var(--color-jr-page, #f3f4f6);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}
</style>
