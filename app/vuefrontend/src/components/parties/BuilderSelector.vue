<template>
  <div class="jr-builder-selector">
    <JRSelectAddon
      :inputId="inputId"
      :modelValue="selectedValue"
      :options="options"
      optionLabel="name"
      optionValue="id"
      placeholder="Search party..."
      filter
      showClear
      :disabled="disabled"
      :invalid="hasError"
      :required="required"
      :ariaDescribedby="ariaDescribedby"
      :showAdd="true"
      :showEdit="!!selectedValue"
      :addDisabled="disabled || !canAdd"
      :editDisabled="disabled || !canEdit"
      addLabel="Add a new party to the system"
      editLabel="Edit the currently selected party"
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
      <DynamicForm
        v-if="dialogVisible"
        :key="`builder-${editId || 'new'}-${formNonce}`"
        :schema-endpoint="'/api/schema/builder/'"
        :api-endpoint="'/api/builder/'"
        :object-id="editId"
        :form-title="dialogHeader"
        :is-modal="true"
        @saved="handleSaved"
        @cancel="closeDialog" />
    </JRDrawer>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, getCurrentInstance } from "vue";
import axios from "axios";
import DynamicForm from "./DynamicForm.vue";
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
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  inputId: {
    type: String,
    default: "party-builder",
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
  editMode.value ? `Edit Party #${editId.value}` : "New Party"
);
const canAdd = computed(
  () => !!proxy?.hasPermission?.("ctrctsapp.add_builder")
);
const canEdit = computed(
  () => !!proxy?.hasPermission?.("ctrctsapp.change_builder")
);

watch(
  () => props.modelValue,
  async (newValue) => {
    selectedValue.value = newValue;
    if (newValue) await ensureBuilderInOptions(newValue);
  }
);

function onSelect(value) {
  selectedValue.value = value;
  emit("update:modelValue", value);
  emit("change", value);
}

async function loadBuilders(search = "") {
  loading.value = true;
  try {
    const { data } = await axios.get("/api/builder/?is_active=true", {
      params: { search, page_size: 50 },
    });
    const list = Array.isArray(data) ? data : data?.results || [];
    options.value = list.map((b) => ({ id: b.id, name: b.name }));
    if (selectedValue.value) {
      await ensureBuilderInOptions(selectedValue.value);
    }
  } catch (error) {
    console.error("Error searching builders:", error);
    options.value = [];
  } finally {
    loading.value = false;
  }
}

function onShow() {
  loadBuilders("");
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

function handleSaved(newBuilder) {
  if (!newBuilder?.id) return;
  const existing = options.value.find((opt) => opt.id === newBuilder.id);
  const row = { id: newBuilder.id, name: newBuilder.name };
  if (!existing) {
    options.value = [...options.value, row];
  } else {
    options.value = options.value.map((opt) =>
      opt.id === newBuilder.id ? row : opt
    );
  }
  onSelect(newBuilder.id);
  closeDialog();
}

async function ensureBuilderInOptions(builderId) {
  if (options.value.some((opt) => opt.id === builderId)) return;
  try {
    const { data } = await axios.get(`/api/builder/${builderId}/`);
    options.value = [...options.value, { id: data.id, name: data.name }];
  } catch (error) {
    if (error.response?.status === 404) {
      selectedValue.value = null;
      emit("update:modelValue", null);
      emit("change", null);
      return;
    }
    console.error("Error ensuring builder in options:", error);
  }
}

onMounted(async () => {
  try {
    await loadBuilders("");
  } catch (error) {
    console.warn("Could not preload parties:", error);
  }
  if (props.modelValue) {
    await ensureBuilderInOptions(props.modelValue);
  }
});
</script>
