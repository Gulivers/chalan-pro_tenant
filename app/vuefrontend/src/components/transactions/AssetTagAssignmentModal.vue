<template>
  <JRDialog
    :visible="show"
    header="Assign Serial Numbers"
    size="xl"
    :showFooter="false"
    @update:visible="onVisible">
    <div class="jr-asset-modal">
      <p v-if="contextLoaded" class="jr-asset-modal__meta">
        <span>
          <strong>Document:</strong> {{ headerDocument }} — {{ headerDate }}
        </span>
        <span>
          <strong>Serialized units:</strong> {{ items.length }} —
          <strong>Missing tags:</strong> {{ missingCount }}
        </span>
      </p>

      <p v-if="!loading && items.length > 0" class="jr-asset-modal__hint">
        This purchase includes serialized equipment. Assign serial numbers now
        or skip to complete later.
      </p>

      <Message
        v-if="errorMessage"
        class="jr-asset-modal__msg"
        severity="error"
        :closable="true"
        @close="errorMessage = ''">
        {{ errorMessage }}
      </Message>

      <p v-if="loading" class="jr-asset-modal__loading" role="status">
        Loading items…
      </p>

      <Message
        v-else-if="items.length === 0"
        class="jr-asset-modal__msg"
        severity="warn"
        :closable="false">
        No serialized items found for this document.
      </Message>

      <div v-else class="jr-asset-table-scroll">
        <table class="jr-asset-table">
          <thead>
            <tr>
              <th class="jr-asset-table__num">#</th>
              <th>Line</th>
              <th>Product</th>
              <th>Serial number</th>
              <th>Status</th>
              <th>Condition</th>
              <th>Warehouse</th>
              <th>Purchase date</th>
              <th>Document</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(item, idx) in sortedItems"
              :key="item.id"
              :class="{ 'jr-asset-table__row--error': !!item._error }">
              <td class="jr-asset-table__num">{{ idx + 1 }}</td>
              <td>{{ item.document_line || "—" }}</td>
              <td>{{ item.product_name }}</td>
              <td>
                <div class="jr-asset-table__tag">
                  <JRInput
                    :inputId="`asset-tag-${idx}`"
                    :modelValue="item._asset_tag"
                    placeholder="Optional"
                    :invalid="item._validation === 'invalid'"
                    @update:modelValue="
                      (v) => {
                        item._asset_tag = (v || '').trim();
                        validateRow(item);
                      }
                    "
                    @keydown.enter.prevent="focusNext(idx)" />
                  <JRBadge
                    v-if="item._validation === 'valid'"
                    value="OK"
                    severity="success" />
                  <JRBadge
                    v-else-if="item._validation === 'invalid'"
                    value="!"
                    severity="danger" />
                </div>
                <p
                  v-if="item._error"
                  class="jr-asset-table__error"
                  role="alert">
                  {{ item._error }}
                </p>
              </td>
              <td>
                <JRBadge :value="item.status || '—'" severity="secondary" />
              </td>
              <td>
                <JRBadge
                  :value="conditionLabel(item.condition)"
                  :severity="conditionBadgeSeverity(item.condition)" />
              </td>
              <td>{{ item.current_warehouse_name || "—" }}</td>
              <td>{{ formatDate(item.purchase_date) }}</td>
              <td>{{ item.document_id || "—" }}</td>
              <td>
                <JRInput
                  :inputId="`asset-notes-${idx}`"
                  :modelValue="item._notes"
                  placeholder="Notes"
                  @update:modelValue="
                    (v) => {
                      item._notes = (v || '').trim();
                    }
                  " />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="jr-asset-modal__actions">
        <JRButton type="button" variant="secondary" @click="onClose">
          Close
        </JRButton>
        <JRButton type="button" variant="secondary" @click="onSkip">
          Skip for now
        </JRButton>
        <JRButton
          type="button"
          variant="primary"
          :disabled="saving || loading"
          @click="onSave">
          {{ saving ? "Saving…" : "Save tags" }}
        </JRButton>
      </div>
    </div>
  </JRDialog>

  <JRDialog
    :visible="emptyConfirmVisible"
    header="Save without all tags?"
    :message="emptyConfirmMessage"
    confirmLabel="Save anyway"
    @update:visible="emptyConfirmVisible = $event"
    @confirm="confirmSaveEmpty" />
</template>

<script setup>
import { ref, computed, watch, nextTick } from "vue";
import axios from "axios";
import Message from "primevue/message";
import { JRDialog, JRButton, JRInput, JRBadge } from "@ui";

const props = defineProps({
  show: { type: Boolean, default: false },
  documentId: { type: Number, default: null },
  documentContext: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(["close", "saved"]);

const items = ref([]);
const loading = ref(false);
const saving = ref(false);
const contextLoaded = ref(false);
const errorMessage = ref("");
const emptyConfirmVisible = ref(false);
const emptyConfirmMessage = ref("");

const headerDocument = computed(() => {
  const ctx = props.documentContext;
  const code = ctx.document_type_code || "DOC";
  const id = ctx.id ?? props.documentId;
  const party = ctx.builder_name || ctx.party_name || "—";
  return `${code} #${id} (${party})`;
});

const headerDate = computed(() => {
  const d = props.documentContext?.date;
  if (!d) return "";
  return formatDate(d);
});

const missingCount = computed(() =>
  items.value.filter((i) => !i._asset_tag?.trim()).length
);

const sortedItems = computed(() => {
  const list = [...items.value];
  list.sort((a, b) => {
    const pa = (a.product_name || "").toLowerCase();
    const pb = (b.product_name || "").toLowerCase();
    return pa.localeCompare(pb) || a.id - b.id;
  });
  return list;
});

watch(
  () => [props.show, props.documentId],
  async ([show, docId]) => {
    contextLoaded.value = !!props.documentContext?.document_type_code;
    errorMessage.value = "";
    if (show && docId) {
      await loadItems();
    } else if (!show) {
      items.value = [];
    }
  },
  { immediate: true }
);

function onVisible(visible) {
  if (!visible) emit("close");
}

function conditionBadgeSeverity(value) {
  const v = (value || "").toLowerCase();
  if (v === "ok") return "success";
  if (v === "damaged") return "warn";
  if (v === "needs_repair") return "danger";
  return "secondary";
}

function conditionLabel(value) {
  const labels = {
    ok: "OK",
    damaged: "Damaged",
    needs_repair: "Needs repair",
  };
  const v = (value || "").toLowerCase().replace(/\s/g, "_");
  return labels[v] || value || "—";
}

function formatDate(dateString) {
  if (!dateString) return "—";
  const d = new Date(dateString);
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function validateRow(item) {
  const tag = (item._asset_tag || "").trim();
  if (!tag) {
    item._validation = null;
    item._error = null;
    return;
  }
  const seen = new Map();
  items.value.forEach((i) => {
    const t = (i._asset_tag || "").trim();
    if (t) seen.set(t.toLowerCase(), (seen.get(t.toLowerCase()) || 0) + 1);
  });
  const count = seen.get(tag.toLowerCase()) || 0;
  if (count > 1) {
    item._validation = "invalid";
    item._error = "Duplicate tag";
    return;
  }
  item._validation = "valid";
  item._error = null;
}

function hasDuplicates() {
  const seen = new Map();
  items.value.forEach((i) => {
    const t = (i._asset_tag || "").trim();
    if (t) seen.set(t.toLowerCase(), (seen.get(t.toLowerCase()) || 0) + 1);
  });
  return [...seen.values()].some((c) => c > 1);
}

function validateAll() {
  items.value.forEach((i) => validateRow(i));
}

function focusNext(currentIdx) {
  nextTick(() => {
    const next = document.getElementById(`asset-tag-${currentIdx + 1}`);
    next?.focus?.();
  });
}

async function loadItems() {
  if (!props.documentId) return;
  loading.value = true;
  items.value = [];
  try {
    const { data } = await axios.get("/api/serialized-items/", {
      params: { document: props.documentId },
    });
    const list = Array.isArray(data) ? data : data?.results || [];
    items.value = list.map((i) => ({
      ...i,
      _asset_tag: i.asset_tag || "",
      _notes: i.notes || "",
      _validation: null,
      _error: null,
    }));
  } catch (err) {
    console.error("Error loading serialized items:", err);
    items.value = [];
    errorMessage.value = "Could not load serialized items.";
  } finally {
    loading.value = false;
    nextTick(() => validateAll());
  }
}

function onClose() {
  emit("close");
}

function onSkip() {
  emit("close");
}

async function onSave() {
  validateAll();
  if (hasDuplicates()) {
    errorMessage.value = "Resolve duplicate serial numbers before saving.";
    return;
  }
  const emptyCount = items.value.filter(
    (i) => !(i._asset_tag || "").trim()
  ).length;
  if (emptyCount > 0) {
    emptyConfirmMessage.value = `${emptyCount} item(s) have no serial number. Save anyway?`;
    emptyConfirmVisible.value = true;
    return;
  }
  await performSave();
}

async function confirmSaveEmpty() {
  emptyConfirmVisible.value = false;
  await performSave();
}

async function performSave() {
  const payload = items.value.map((i) => ({
    id: i.id,
    asset_tag: i._asset_tag?.trim() || "",
    notes: i._notes?.trim() || "",
  }));

  saving.value = true;
  errorMessage.value = "";
  try {
    await axios.patch("/api/serialized-items/bulk-update-tags/", {
      items: payload,
    });
    emit("saved");
    emit("close");
  } catch (err) {
    const errData = err?.response?.data;
    const errors = errData?.errors || [];
    items.value.forEach((i) => (i._error = null));
    errors.forEach((e) => {
      const item = items.value.find((i) => i.id === e.id);
      if (item) {
        item._error = e.detail || "Error";
        item._validation = "invalid";
      }
    });
    if (errors.length === 0) {
      errorMessage.value = errData?.detail || "Could not save serial numbers.";
    }
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.jr-asset-modal {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.jr-asset-modal__meta {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-asset-modal__hint,
.jr-asset-modal__loading {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-jr-text);
}

.jr-asset-modal__msg {
  margin: 0;
  --p-message-border-radius: var(--radius-jr-control, 0);
}

.jr-asset-table-scroll {
  overflow: auto;
  max-height: min(60vh, 32rem);
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface);
}

.jr-asset-table {
  width: 100%;
  min-width: 56rem;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.jr-asset-table th,
.jr-asset-table td {
  padding: 0.45rem 0.5rem;
  border-bottom: 1px solid var(--color-jr-border);
  vertical-align: top;
  text-align: left;
}

.jr-asset-table thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  font-size: 0.8125rem;
  font-weight: 600;
  background: var(--color-jr-page);
  color: var(--color-jr-text);
}

.jr-asset-table__num {
  width: 2.5rem;
  text-align: center;
}

.jr-asset-table__row--error td {
  background: var(--color-jr-danger-subtle);
}

.jr-asset-table__tag {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.jr-asset-table__error {
  margin: 0.25rem 0 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
}

.jr-asset-modal__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 0.35rem;
  border-top: 1px solid var(--color-jr-border);
}
</style>
