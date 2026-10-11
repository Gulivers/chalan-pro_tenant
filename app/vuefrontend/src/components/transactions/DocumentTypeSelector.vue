<template>
  <div class="jr-doctype-selector">
    <JRSelectAddon
      :inputId="inputId"
      :modelValue="selectedValue"
      :options="options"
      optionLabel="description"
      optionValue="id"
      placeholder="Select document type..."
      filter
      :disabled="disabled"
      :invalid="hasError"
      :required="required"
      :ariaDescribedby="ariaDescribedby"
      :showAdd="true"
      :showEdit="!!selectedValue"
      :addDisabled="disabled || !canAdd"
      :editDisabled="disabled || !canEdit"
      addLabel="Add a new document type to the system"
      editLabel="Edit the currently selected document type"
      @update:modelValue="onSelect"
      @show="onShow"
      @add="openDialog('add')"
      @edit="openDialog('edit', selectedValue)" />

    <JRDrawer
      class="jr-catalog-drawer jr-catalog-drawer--wide"
      :visible="dialogVisible"
      :header="dialogHeader"
      position="right"
      @update:visible="onDialogVisible">
      <DocTypeForm
        v-if="dialogVisible"
        :key="`doctype-${editId || 'new'}-${formNonce}`"
        :id="editId"
        :is-modal="true"
        @saved="handleSaved"
        @cancel="closeDialog" />
    </JRDrawer>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, getCurrentInstance } from "vue";
import axios from "axios";
import DocTypeForm from "./DocTypeForm.vue";
import { JRSelectAddon, JRDrawer } from "@ui";

const props = defineProps({
  modelValue: {
    type: [Number, String],
    default: null,
  },
  error: {
    type: [String, Array],
    default: null,
  },
  required: {
    type: Boolean,
    default: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  inputId: {
    type: String,
    default: "document-type",
  },
  ariaDescribedby: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["update:modelValue", "change"]);

const { proxy } = getCurrentInstance() || {};

const selectedValue = ref(props.modelValue);
const options = ref([]);
const loading = ref(false);
const editMode = ref(false);
const editId = ref(null);
const formNonce = ref(0);
const dialogVisible = ref(false);

const hasError = computed(() => !!props.error);
const dialogHeader = computed(() =>
  editMode.value ? `Edit Document Type #${editId.value}` : "New Document Type"
);
const canAdd = computed(
  () => !!proxy?.hasPermission?.("apptransactions.add_documenttype")
);
const canEdit = computed(
  () => !!proxy?.hasPermission?.("apptransactions.change_documenttype")
);

watch(
  () => props.modelValue,
  async (newValue) => {
    selectedValue.value = newValue;
    if (newValue) await ensureDocTypeInOptions(newValue);
  }
);

function onSelect(value) {
  selectedValue.value = value;
  emit("update:modelValue", value);
  emit("change", value);
}

async function loadOptions() {
  loading.value = true;
  try {
    const { data } = await axios.get("/api/document-types/?is_active=true");
    const list = Array.isArray(data) ? data : data?.results || [];
    options.value = list.map((d) => ({
      id: d.id,
      description: d.description,
    }));
    if (selectedValue.value) {
      await ensureDocTypeInOptions(selectedValue.value);
    }
  } catch (error) {
    console.error("Error loading document types:", error);
    options.value = [];
  } finally {
    loading.value = false;
  }
}

function onShow() {
  if (!options.value.length) loadOptions();
}

function openDialog(mode, id = null) {
  editMode.value = mode === "edit";
  editId.value = id;
  formNonce.value += 1;
  dialogVisible.value = true;
}

function closeDialog() {
  dialogVisible.value = false;
  if (!editMode.value) editId.value = null;
}

function onDialogVisible(visible) {
  dialogVisible.value = visible;
  if (!visible && !editMode.value) editId.value = null;
}

function handleSaved(newDocType) {
  if (!newDocType?.id) return;
  const existing = options.value.find((opt) => opt.id === newDocType.id);
  const row = {
    id: newDocType.id,
    description: newDocType.description,
  };
  if (!existing) {
    options.value = [...options.value, row];
  } else {
    options.value = options.value.map((opt) =>
      opt.id === newDocType.id ? row : opt
    );
  }
  onSelect(newDocType.id);
  closeDialog();
}

async function ensureDocTypeInOptions(docTypeId) {
  if (options.value.some((opt) => opt.id === docTypeId)) return;
  try {
    const { data } = await axios.get(`/api/document-types/${docTypeId}/`);
    options.value = [
      ...options.value,
      { id: data.id, description: data.description },
    ];
  } catch (error) {
    if (error.response?.status === 404) {
      selectedValue.value = null;
      emit("update:modelValue", null);
      emit("change", null);
      return;
    }
    console.error("Error ensuring document type in options:", error);
  }
}

onMounted(async () => {
  try {
    await loadOptions();
  } catch (error) {
    console.warn("Could not preload document types:", error);
  }
  if (props.modelValue) {
    await ensureDocTypeInOptions(props.modelValue);
  }
});
</script>
