<template>
  <JRDialog
    :visible="visible"
    :header="isEditMode ? 'Edit Favorite' : 'Save as Favorite'"
    size="wide"
    :showFooter="false"
    @update:visible="$emit('update:visible', $event)">
    <form class="jr-favorite-form" @submit.prevent="handleSubmit" novalidate>
      <p v-if="formBanner" class="jr-form-banner" role="alert">
        {{ formBanner }}
      </p>

      <JRField
        v-slot="{ describedby, invalid }"
        label="Name"
        required
        inputId="favorite-name"
        :error="fieldError('name')">
        <JRInput
          inputId="favorite-name"
          v-model="form.name"
          :invalid="invalid"
          :required="true"
          :ariaDescribedby="describedby"
          placeholder="Descriptive name for this favorite" />
      </JRField>

      <JRField
        v-slot="{ describedby, invalid }"
        label="Description"
        inputId="favorite-description"
        :error="fieldError('description')">
        <JRTextarea
          inputId="favorite-description"
          v-model="form.description"
          :rows="3"
          :invalid="invalid"
          :ariaDescribedby="describedby"
          placeholder="Optional description" />
      </JRField>

      <section class="jr-favorite-preview" aria-label="Transaction preview">
        <h3 class="jr-favorite-preview__title">Transaction preview</h3>
        <dl class="jr-favorite-preview__grid">
          <div>
            <dt>Document type</dt>
            <dd>{{ documentTypeName }}</dd>
          </div>
          <div>
            <dt>Lines</dt>
            <dd>{{ linesCount }} items</dd>
          </div>
          <div v-if="builderName">
            <dt>Party</dt>
            <dd>{{ builderName }}</dd>
          </div>
          <div v-if="workAccountName">
            <dt>Work account</dt>
            <dd>{{ workAccountName }}</dd>
          </div>
        </dl>
        <div v-if="linesPreview.length" class="jr-favorite-preview__products">
          <p class="jr-favorite-preview__label">Products</p>
          <ul class="jr-favorite-preview__list">
            <li v-for="(line, idx) in linesPreview" :key="idx">
              <JRBadge
                :value="`${line.product_name} (${line.quantity})`"
                severity="secondary" />
            </li>
          </ul>
        </div>
      </section>

      <Message
        v-if="isEditMode"
        class="jr-favorite-form__info"
        severity="warn"
        :closable="false">
        Update the name and description, or use Update data to refresh this
        favorite from the current transaction.
      </Message>

      <div class="jr-favorite-form__actions">
        <JRButton
          v-if="isEditMode"
          type="button"
          variant="danger"
          :disabled="
            submitting ||
            !hasPermission('apptransactions.delete_transactionfavorite')
          "
          @click="handleDelete">
          Delete
        </JRButton>
        <span class="jr-favorite-form__spacer" />
        <JRButton
          type="button"
          variant="secondary"
          :disabled="submitting"
          @click="closeDialog">
          Cancel
        </JRButton>
        <JRButton
          v-if="isEditMode"
          type="button"
          variant="secondary"
          :disabled="
            submitting ||
            !hasPermission('apptransactions.change_transactionfavorite')
          "
          @click="handleUpdateData">
          Update data
        </JRButton>
        <JRButton
          type="submit"
          variant="primary"
          :disabled="submitting || !form.name.trim() || !canSaveFavorite">
          {{
            submitting
              ? "Saving…"
              : isEditMode
              ? "Save changes"
              : "Save favorite"
          }}
        </JRButton>
      </div>
    </form>
  </JRDialog>

  <JRDialog
    :visible="deleteConfirmVisible"
    header="Delete favorite?"
    message="This favorite will be permanently deleted."
    confirmLabel="Delete"
    confirmVariant="danger"
    @update:visible="deleteConfirmVisible = $event"
    @confirm="confirmDelete" />

  <JRDialog
    :visible="updateConfirmVisible"
    header="Update favorite data?"
    message="Replace this favorite’s saved lines with the current transaction."
    confirmLabel="Update"
    @update:visible="updateConfirmVisible = $event"
    @confirm="confirmUpdateData" />
</template>

<script setup>
import { ref, reactive, computed, watch, getCurrentInstance } from "vue";
import Message from "primevue/message";
import { JRDialog, JRField, JRInput, JRTextarea, JRButton, JRBadge } from "@ui";

const props = defineProps({
  visible: { type: Boolean, default: false },
  transactionData: { type: Object, required: true },
  documentTypesOptions: { type: Array, default: () => [] },
  buildersOptions: { type: Array, default: () => [] },
  workAccountsOptions: { type: Array, default: () => [] },
  isEditMode: { type: Boolean, default: false },
  favoriteToEdit: { type: Object, default: null },
});

const emit = defineEmits(["update:visible", "saved", "updated", "deleted"]);

const { proxy } = getCurrentInstance() || {};
const submitting = ref(false);
const formBanner = ref("");
const deleteConfirmVisible = ref(false);
const updateConfirmVisible = ref(false);
const errors = reactive({});

const form = reactive({
  name: "",
  description: "",
});

function hasPermission(permission) {
  return !!proxy?.hasPermission?.(permission);
}

const canSaveFavorite = computed(() =>
  props.isEditMode
    ? hasPermission("apptransactions.change_transactionfavorite")
    : hasPermission("apptransactions.add_transactionfavorite")
);

const documentTypeName = computed(() => {
  if (!props.transactionData.document_type) return "Not selected";
  const docType = props.documentTypesOptions.find(
    (dt) => dt.value === props.transactionData.document_type
  );
  return docType ? docType.label : "Unknown";
});

const builderName = computed(() => {
  if (!props.transactionData.builder) return null;
  const builder = props.buildersOptions.find(
    (b) => b.value === props.transactionData.builder
  );
  return builder ? builder.label : "Unknown";
});

const workAccountName = computed(() => {
  if (!props.transactionData.work_account) return null;
  const workAccount = props.workAccountsOptions.find(
    (wa) => wa.value === props.transactionData.work_account
  );
  return workAccount ? workAccount.label : "Unknown";
});

const linesCount = computed(
  () => props.transactionData.lines?.length || 0
);

const linesPreview = computed(() => {
  if (!props.transactionData.lines) return [];
  return props.transactionData.lines
    .filter((line) => line.product)
    .slice(0, 5)
    .map((line) => ({
      product_name: line.product_label || "Unknown product",
      quantity: line.quantity || 0,
    }));
});

watch(
  () => props.favoriteToEdit,
  (newFavorite) => {
    if (newFavorite && props.isEditMode) {
      form.name = newFavorite.name || "";
      form.description = newFavorite.description || "";
    }
  },
  { immediate: true }
);

watch(
  () => [props.visible, props.isEditMode],
  ([visible, editMode]) => {
    if (!visible) return;
    formBanner.value = "";
    clearErrors();
    if (!editMode) {
      form.name = "";
      form.description = "";
    } else if (props.favoriteToEdit) {
      form.name = props.favoriteToEdit.name || "";
      form.description = props.favoriteToEdit.description || "";
    }
  }
);

function fieldError(key) {
  const value = errors[key];
  if (!value) return "";
  return Array.isArray(value) ? value[0] || "" : String(value);
}

function clearErrors() {
  Object.keys(errors).forEach((key) => delete errors[key]);
}

function closeDialog() {
  emit("update:visible", false);
}

function validateForm() {
  clearErrors();
  if (!form.name.trim()) {
    errors.name = ["Name is required."];
    return false;
  }
  return true;
}

function countTransactionLinesWithProduct() {
  const lines = props.transactionData?.lines;
  if (!Array.isArray(lines)) return 0;
  return lines.filter(
    (line) => line?.product != null && line.product !== ""
  ).length;
}

async function enforceMinimumFavoriteLines(actionLabel = "save") {
  if (countTransactionLinesWithProduct() >= 2) return true;
  formBanner.value = `You need at least 2 lines with a product to ${actionLabel} a favorite.`;
  return false;
}

async function handleSubmit() {
  if (!validateForm()) return;
  if (!(await enforceMinimumFavoriteLines("save"))) return;

  submitting.value = true;
  formBanner.value = "";
  try {
    const payload = {
      name: form.name.trim(),
      description: form.description.trim(),
      document_data: props.transactionData,
      lines_data: props.transactionData.lines || [],
    };

    if (props.isEditMode && props.favoriteToEdit) {
      const response = await axios.put(
        `/api/transaction-favorites/${props.favoriteToEdit.id}/`,
        payload
      );
      emit("updated", response.data);
    } else {
      const response = await axios.post(
        "/api/transaction-favorites/create-from-transaction/",
        payload
      );
      emit("saved", response.data.favorite);
    }
    closeDialog();
  } catch (error) {
    console.error("Error saving favorite:", error);
    if (error.response?.data?.details) {
      Object.assign(errors, error.response.data.details);
    } else {
      formBanner.value =
        error.response?.data?.error ||
        "Error saving favorite. Please try again.";
    }
  } finally {
    submitting.value = false;
  }
}

function handleUpdateData() {
  if (!props.favoriteToEdit) return;
  updateConfirmVisible.value = true;
}

async function confirmUpdateData() {
  updateConfirmVisible.value = false;
  if (!(await enforceMinimumFavoriteLines("update"))) return;

  submitting.value = true;
  formBanner.value = "";
  try {
    const payload = {
      document_data: props.transactionData,
      lines_data: props.transactionData.lines || [],
    };
    const response = await axios.post(
      `/api/transaction-favorites/${props.favoriteToEdit.id}/update-from-transaction/`,
      payload
    );
    emit("updated", response.data.favorite);
    closeDialog();
  } catch (error) {
    console.error("Error updating favorite data:", error);
    formBanner.value =
      error.response?.data?.error ||
      "Error updating favorite data. Please try again.";
  } finally {
    submitting.value = false;
  }
}

function handleDelete() {
  if (!props.favoriteToEdit) return;
  deleteConfirmVisible.value = true;
}

async function confirmDelete() {
  deleteConfirmVisible.value = false;
  if (!props.favoriteToEdit) return;
  submitting.value = true;
  formBanner.value = "";
  try {
    await axios.delete(
      `/api/transaction-favorites/${props.favoriteToEdit.id}/`
    );
    emit("deleted", props.favoriteToEdit.id);
    closeDialog();
  } catch (error) {
    console.error("Error deleting favorite:", error);
    formBanner.value =
      error.response?.data?.error ||
      "Error deleting favorite. Please try again.";
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.jr-favorite-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-form-banner {
  margin: 0;
  padding: 0.75rem 1rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
  background: var(--color-jr-danger-subtle);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
}

.jr-favorite-preview {
  padding: 0.85rem 1rem;
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface-muted);
}

.jr-favorite-preview__title {
  margin: 0 0 0.65rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-favorite-preview__grid {
  margin: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem 1rem;
}

.jr-favorite-preview__grid dt {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-favorite-preview__grid dd {
  margin: 0.15rem 0 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-favorite-preview__label {
  margin: 0.75rem 0 0.35rem;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-favorite-preview__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.jr-favorite-form__info {
  margin: 0;
  --p-message-warn-background: var(--color-jr-warning-subtle);
  --p-message-warn-border-color: var(--color-jr-border);
  --p-message-warn-color: var(--color-jr-warning-text);
  --p-message-border-radius: var(--radius-jr-control, 0);
}

.jr-favorite-form__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  padding-top: 0.25rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-favorite-form__spacer {
  flex: 1 1 auto;
}

@media (max-width: 767.98px) {
  .jr-favorite-preview__grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
