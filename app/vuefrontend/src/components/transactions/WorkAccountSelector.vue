<template>
  <div class="jr-wa-selector">
    <JRSelectAddon
      :inputId="inputId"
      :modelValue="selectedValue"
      :options="options"
      optionLabel="title"
      optionValue="id"
      placeholder="Search work account..."
      filter
      showClear
      :disabled="disabled"
      :invalid="hasError"
      :ariaDescribedby="ariaDescribedby"
      :showAdd="true"
      :showEdit="!!selectedValue"
      :addDisabled="disabled || !canAdd"
      :editDisabled="disabled || !canEdit"
      addLabel="Add a new work account to the system"
      editLabel="Edit the currently selected work account"
      @update:modelValue="onSelect"
      @show="onShow"
      @add="openDialog('add')"
      @edit="openDialog('edit', selectedValue)" />

    <p v-if="hasError" class="jr-wa-selector__error" role="alert">
      {{ errorMessage }}
    </p>

    <JRDrawer
      class="jr-catalog-drawer jr-catalog-drawer--wide"
      :visible="dialogVisible"
      :header="dialogHeader"
      position="right"
      @update:visible="onDialogVisible">
      <WorkAccountSelect
        v-if="dialogVisible"
        ref="workAccountForm"
        :key="`workaccount-${editId || 'new'}-${formNonce}`"
        :id="editId"
        :redirect-on-success="false"
        @saved="handleSaved"
        @cancel="closeDialog" />
    </JRDrawer>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, getCurrentInstance } from "vue";
import axios from "axios";
import WorkAccountSelect from "./WorkAccountSelect.vue";
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
  /** @deprecated Label is owned by JRField parent; kept for call-site compat */
  showLabel: {
    type: Boolean,
    default: true,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  inputId: {
    type: String,
    default: "work-account",
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
const errorMessage = computed(() => {
  if (Array.isArray(props.error)) return props.error[0];
  return props.error;
});
const dialogHeader = computed(() =>
  editMode.value ? `Edit Work Account #${editId.value}` : "New Work Account"
);
const canAdd = computed(
  () => !!proxy?.hasPermission?.("apptransactions.add_workaccount")
);
const canEdit = computed(
  () => !!proxy?.hasPermission?.("apptransactions.change_workaccount")
);

watch(
  () => props.modelValue,
  async (newValue) => {
    selectedValue.value = newValue;
    if (newValue) await ensureWorkAccountInOptions(newValue);
  }
);

function onSelect(value) {
  selectedValue.value = value;
  emit("update:modelValue", value);
  emit("change", value);
}

async function loadWorkAccounts(search = "") {
  loading.value = true;
  try {
    const { data } = await axios.get("/api/work-accounts/", {
      params: { search, page_size: 50, active_only: 1 },
    });
    const list = Array.isArray(data) ? data : data?.results || [];
    options.value = list.map((wa) => ({ id: wa.id, title: wa.title }));
    if (selectedValue.value) {
      await ensureWorkAccountInOptions(selectedValue.value);
    }
  } catch (error) {
    console.error("Error searching work accounts:", error);
    options.value = [];
  } finally {
    loading.value = false;
  }
}

function onShow() {
  loadWorkAccounts("");
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

function handleSaved(newWorkAccount) {
  const existing = options.value.find((opt) => opt.id === newWorkAccount.id);
  if (!existing) {
    options.value = [
      ...options.value,
      { id: newWorkAccount.id, title: newWorkAccount.title },
    ];
  } else {
    options.value = options.value.map((opt) =>
      opt.id === newWorkAccount.id
        ? { id: newWorkAccount.id, title: newWorkAccount.title }
        : opt
    );
  }
  onSelect(newWorkAccount.id);
  closeDialog();
}

async function ensureWorkAccountInOptions(workAccountId) {
  if (options.value.some((opt) => opt.id === workAccountId)) return;
  try {
    const { data } = await axios.get(`/api/work-accounts/${workAccountId}/`);
    options.value = [...options.value, { id: data.id, title: data.title }];
  } catch (error) {
    if (error.response?.status === 404) {
      selectedValue.value = null;
      emit("update:modelValue", null);
      emit("change", null);
      return;
    }
    console.error("Error ensuring work account in options:", error);
  }
}

onMounted(async () => {
  try {
    await loadWorkAccounts("");
  } catch (error) {
    console.warn("Could not preload work accounts:", error);
  }
  if (props.modelValue) {
    await ensureWorkAccountInOptions(props.modelValue);
  }
});
</script>

<style scoped>
.jr-wa-selector__error {
  margin: 0.25rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-jr-danger-text);
}
</style>
