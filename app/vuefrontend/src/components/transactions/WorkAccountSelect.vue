<template>
  <component :is="pageWrapper" v-bind="pageWrapperProps">
    <JRPageHeader
      v-if="usePageChrome"
      :title="pageTitle"
      :description="pageDescription">
      <template v-if="isViewMode && canEditFromView" #actions>
        <JRButton variant="primary" size="sm" @click="goToEdit">
          Edit Work Account
        </JRButton>
      </template>
    </JRPageHeader>

    <div :class="panelClass">
      <p v-if="loading" class="jr-wa-form__status" role="status">
        Loading work account…
      </p>

      <form
        v-else
        class="jr-wa-form__form"
        @submit.prevent="handleSubmit"
        novalidate>
        <div
          v-if="formBannerMessage"
          ref="formBannerRef"
          class="jr-form-banner"
          role="alert"
          tabindex="-1">
          {{ formBannerMessage }}
        </div>

        <JRSection title="Context">
          <BuilderJobHouseSelect
            v-model="builderJobHouseData"
            :is-editing="canEditContext"
            :is-absence="isDisabled"
            :stacked="!usePageChrome"
            @update:builder="onBuilderChanged($event)"
            @update:job="onJobChanged($event)"
            @update:houseModel="onHouseModelChanged($event)" />
        </JRSection>

        <JRSection title="Identity">
          <div class="jr-form-grid jr-form-grid--identity">
            <JRField
              v-slot="{ describedby, invalid }"
              label="Lot"
              inputId="wa-lot"
              :error="lotFieldError">
              <JRInput
                inputId="wa-lot"
                :modelValue="local.lot"
                maxlength="100"
                autocomplete="off"
                :placeholder="
                  canEditLotAddr
                    ? 'Enter lot…'
                    : 'Select Builder and Community first'
                "
                :disabled="!canEditLotAddr || isDisabled"
                :invalid="invalid"
                :ariaDescribedby="describedby"
                @update:modelValue="onLotInput"
                @blur="onLotBlur" />
            </JRField>

            <JRField
              label="Active"
              inputId="wa-active"
              class="jr-wa-form__active">
              <JRCheckbox
                inputId="wa-active"
                v-model="local.is_active"
                ariaLabel="Active"
                :disabled="isDisabled" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Address"
              inputId="wa-address"
              :error="addrFieldError"
              class="jr-form-grid__full">
              <JRInput
                inputId="wa-address"
                :modelValue="local.address"
                maxlength="255"
                autocomplete="off"
                :placeholder="
                  canEditLotAddr
                    ? 'Street, City ST ZIP'
                    : 'Select Builder and Community first'
                "
                :disabled="!canEditLotAddr || isDisabled"
                :invalid="invalid"
                :ariaDescribedby="describedby"
                @update:modelValue="onAddressInput"
                @blur="onAddressBlur" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Title"
              required
              inputId="wa-title"
              :hint="
                isDisabled
                  ? ''
                  : 'Stored in UPPERCASE. Fills from Lot or Address + Community.'
              "
              :error="fieldError('title')"
              class="jr-form-grid__full">
              <JRInput
                inputId="wa-title"
                class="jr-wa-form__title-input"
                :modelValue="local.title"
                maxlength="200"
                autocomplete="off"
                placeholder="Will auto-fill from Lot/Address + Community"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="onTitleInput" />
            </JRField>
          </div>
        </JRSection>

        <JRSection title="Pricing and location">
          <div class="jr-form-grid jr-form-grid--details">
            <JRField
              v-slot="{ describedby, invalid }"
              label="Default Price Type"
              inputId="wa-price-type"
              :error="fieldError('default_price_type')"
              class="jr-form-grid__price">
              <JRSelect
                inputId="wa-price-type"
                v-model="local.default_price_type"
                :options="priceTypeOptions"
                optionLabel="name"
                optionValue="id"
                placeholder="Select a price type"
                filter
                showClear
                :disabled="isDisabled"
                :invalid="invalid"
                :ariaDescribedby="describedby"
                @show="onSearchPriceTypes('')" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="City"
              inputId="wa-city"
              :error="fieldError('city')">
              <JRInput
                inputId="wa-city"
                v-model="local.city"
                maxlength="100"
                autocomplete="off"
                :disabled="isDisabled"
                :invalid="invalid"
                :ariaDescribedby="describedby" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="State"
              inputId="wa-state"
              :error="fieldError('state')">
              <JRInput
                inputId="wa-state"
                v-model="local.state"
                maxlength="50"
                autocomplete="off"
                :disabled="isDisabled"
                :invalid="invalid"
                :ariaDescribedby="describedby" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="ZIP Code"
              inputId="wa-zip"
              :error="fieldError('zipcode')">
              <JRInput
                inputId="wa-zip"
                v-model="local.zipcode"
                maxlength="20"
                autocomplete="off"
                :disabled="isDisabled"
                :invalid="invalid"
                :ariaDescribedby="describedby" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Notes"
              inputId="wa-notes"
              :error="fieldError('notes')"
              class="jr-form-grid__full">
              <JRTextarea
                inputId="wa-notes"
                v-model="local.notes"
                :rows="3"
                :disabled="isDisabled"
                :invalid="invalid"
                :ariaDescribedby="describedby" />
            </JRField>
          </div>
        </JRSection>

        <div class="jr-wa-form__actions jr-wa-form__actions--sticky">
          <template v-if="!isDisabled">
            <JRButton type="submit" variant="primary" :disabled="submitting">
              {{
                submitting
                  ? "Saving..."
                  : isEditMode
                    ? "Update"
                    : "Save"
              }}
            </JRButton>
            <JRButton
              type="button"
              variant="secondary"
              :disabled="submitting"
              @click="onCancel">
              Cancel
            </JRButton>
          </template>
          <JRButton
            v-else-if="isViewMode"
            type="button"
            variant="secondary"
            @click="onCancel">
            {{ usePageChrome ? "Back to list" : "Back" }}
          </JRButton>
        </div>
      </form>
    </div>
  </component>
</template>

<script setup>
import {
  ref,
  reactive,
  watch,
  computed,
  onMounted,
  nextTick,
  getCurrentInstance,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import Swal from "sweetalert2";
import BuilderJobHouseSelect from "@/components/houses/BuilderJobHouseSelect.vue";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRInput,
  JRSelect,
  JRCheckbox,
  JRTextarea,
  JRButton,
} from "@ui";

const route = useRoute();
const router = useRouter();
const { proxy } = getCurrentInstance() || {};

const props = defineProps({
  id: {
    type: [String, Number],
    default: null,
  },
  modelValue: {
    type: Object,
    default: () => ({
      builder: null,
      job: null,
      house_model: null,
      lot: "",
      address: "",
      city: "",
      state: "",
      zipcode: "",
      default_price_type: null,
      title: "",
      notes: "",
      is_active: true,
    }),
  },
  isEditing: { type: Boolean, default: true },
  isAbsence: { type: Boolean, default: false },
  workAccountId: { type: [Number, String], default: null },
  endpoints: {
    type: Object,
    default: () => ({
      jobs: "/api/jobs/",
      priceTypes: "/api/pricetypes/",
      workAccounts: "/api/work-accounts/",
    }),
  },
  /** Route name to redirect after silent success (CRUD Pattern) */
  listRouteName: { type: String, default: "work-accounts" },
  /** When used inside a modal, disable router redirection on save/cancel */
  redirectOnSuccess: { type: Boolean, default: true },
});

const id = computed(
  () =>
    props.id ??
    (route.name === "work-accounts-form" ? route.query.id : null) ??
    null
);
const isViewMode = computed(
  () => route.query.mode === "view" && props.redirectOnSuccess
);
const isEditMode = computed(
  () =>
    !!id.value &&
    id.value !== null &&
    id.value !== "null" &&
    !isViewMode.value
);
const isCreateMode = computed(
  () => !id.value || id.value === null || id.value === "null"
);

const emit = defineEmits([
  "update:modelValue",
  "change",
  "warning",
  "success",
  "error",
  "cancel",
  "saved",
]);

const local = reactive({ ...props.modelValue });
const meta = reactive({
  created_at: null,
});
const lotTouched = ref(false);
const addrTouched = ref(false);
const titleManuallyEdited = ref(false);
const submitting = ref(false);
const loading = ref(false);
const serverErrors = reactive({});
const formBannerMessage = ref("");
const formBannerRef = ref(null);

watch(formBannerMessage, (msg) => {
  if (!msg) return;
  nextTick(() => {
    formBannerRef.value?.focus?.();
  });
});

const builderJobHouseData = reactive({
  builder: local.builder,
  job: local.job,
  house_model: local.house_model,
});

const jobName = ref("");
const canEditLotAddr = computed(() => !!(local.builder && local.job));
const priceTypeOptions = ref([]);

const usePageChrome = computed(() => props.redirectOnSuccess);
const pageWrapper = computed(() => (usePageChrome.value ? JRPage : "div"));
const pageWrapperProps = computed(() =>
  usePageChrome.value ? {} : { class: "jr-embedded-form" }
);
const panelClass = computed(() => {
  const base = usePageChrome.value
    ? "jr-wa-form"
    : "jr-embedded-form__panel jr-wa-form";
  return usePageChrome.value ? base : `${base} jr-wa-form--drawer`;
});

const pageTitle = computed(() => {
  if (isCreateMode.value) return "New Work Account";
  if (isViewMode.value) return "View Work Account";
  return "Edit Work Account";
});

const pageDescription = computed(() => {
  if (!isViewMode.value || !meta.created_at) return "";
  return `Created: ${formatCreatedDate(meta.created_at)}`;
});

function formatCreatedDate(value) {
  if (!value) return "—";
  try {
    // DateField may arrive as YYYY-MM-DD
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return String(value);
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  } catch {
    return String(value);
  }
}

const isDisabled = computed(() => props.isAbsence || isViewMode.value);
const canEditContext = computed(
  () => props.isEditing && !isDisabled.value
);
const canEditFromView = computed(
  () => !!proxy?.hasPermission?.("apptransactions.change_workaccount")
);

function fieldError(key) {
  const errs = serverErrors[key];
  if (!errs) return "";
  return Array.isArray(errs) ? errs[0] : String(errs);
}

const lotFieldError = computed(() => {
  if (lotTouched.value && !canEditLotAddr.value) {
    return "Select both Builder and Community before entering Lot.";
  }
  return fieldError("lot");
});

const addrFieldError = computed(() => {
  if (addrTouched.value && !canEditLotAddr.value) {
    return "Select both Builder and Community before entering Address.";
  }
  return fieldError("address");
});

watch(
  () => props.modelValue,
  (val) => {
    Object.assign(local, val || {});
  }
);
watch(local, () => emitChange(), { deep: true });

watch(
  id,
  async (newId) => {
    if (newId && newId !== null && newId !== "null") {
      await loadWorkAccount();
    }
  }
);

function emitChange() {
  emit("update:modelValue", {
    ...local,
    title: (local.title || "").toUpperCase(),
  });
  emit("change", { ...local });
}

function onTitleInput(value) {
  titleManuallyEdited.value = true;
  local.title = (value || "").toUpperCase();
  emitChange();
}

function onLotInput(value) {
  local.lot = value ?? "";
  if (!titleManuallyEdited.value) autoFillTitle();
}

function onAddressInput(value) {
  local.address = value ?? "";
  if (!titleManuallyEdited.value) autoFillTitle();
}

function onLotBlur() {
  lotTouched.value = true;
  autoFillTitle();
}

function onAddressBlur() {
  addrTouched.value = true;
  autoFillTitle();
}

async function resolveJobName(jobId) {
  if (!jobId) {
    jobName.value = "";
    return;
  }
  try {
    const { data } = await axios.get(props.endpoints.jobs, {
      params: { id: jobId },
    });
    const obj = Array.isArray(data?.results)
      ? data.results.find((j) => j.id === jobId)
      : Array.isArray(data)
        ? data.find((j) => j.id === jobId)
        : data;
    jobName.value = (obj?.name || "").trim().toUpperCase();
  } catch (_) {
    jobName.value = "";
  }
}

function onBuilderChanged(v) {
  builderJobHouseData.builder = v;
  local.builder = v;
  builderJobHouseData.job = null;
  builderJobHouseData.house_model = null;
  local.job = null;
  local.house_model = null;
  lotTouched.value = false;
  addrTouched.value = false;
  autoFillTitle();
  emitChange();
}

function onJobChanged(v) {
  builderJobHouseData.job = v;
  local.job = v;
  builderJobHouseData.house_model = null;
  local.house_model = null;
  lotTouched.value = false;
  addrTouched.value = false;
  resolveJobName(v);
  autoFillTitle();
  emitChange();
}

function onHouseModelChanged(v) {
  builderJobHouseData.house_model = v;
  local.house_model = v;
  autoFillTitle();
  emitChange();
}

function autoFillTitle() {
  if (titleManuallyEdited.value) return;
  const builder = local.builder;
  const job = local.job;
  const lot = (local.lot || "").trim().toUpperCase();
  const address = (local.address || "").trim().toUpperCase();

  if ((lot || address) && (!builder || !job)) {
    if (props.isEditing) {
      emit(
        "warning",
        "You must select both a Builder and a Community before entering Lot or Address."
      );
    }
    local.title = "";
    return;
  }

  const jobLabel = (jobName.value || "").toUpperCase();
  if (lot) {
    local.title = jobLabel ? `${lot} ${jobLabel}` : `${lot}`;
  } else if (address) {
    local.title = jobLabel ? `${address} ${jobLabel}` : `${address}`;
  } else {
    local.title = jobLabel || (local.title || "").toUpperCase();
  }
}

watch(jobName, () => {
  if (!titleManuallyEdited.value) autoFillTitle();
});

watch(
  () => [local.lot, local.address, local.job, local.builder],
  () => {
    if (!titleManuallyEdited.value) autoFillTitle();
  }
);
if (local.job) resolveJobName(local.job);

async function onSearchPriceTypes(search = "") {
  try {
    const { data } = await axios.get(props.endpoints.priceTypes, {
      params: { search },
    });
    priceTypeOptions.value = data?.results || data || [];
  } catch (_) {
    priceTypeOptions.value = [];
  }
}
onSearchPriceTypes("");

const loadWorkAccount = async () => {
  const loadId = id.value;
  if (!loadId || loadId === null || loadId === "null") return;

  loading.value = true;
  formBannerMessage.value = "";
  Object.keys(serverErrors).forEach((k) => delete serverErrors[k]);

  try {
    const response = await axios.get(`/api/work-accounts/${loadId}/`);
    const data = response.data;

    // Preserve API title; set before assign so watchers skip autoFillTitle.
    titleManuallyEdited.value = true;

    Object.assign(local, {
      builder: data.builder,
      job: data.job,
      house_model: data.house_model,
      lot: data.lot || "",
      address: data.address || "",
      city: data.city || "",
      state: data.state || "",
      zipcode: data.zipcode || "",
      default_price_type: data.default_price_type,
      title: data.title || "",
      notes: data.notes || "",
      is_active: data.is_active !== false,
    });

    meta.created_at = data.created_at || null;

    builderJobHouseData.builder = data.builder;
    builderJobHouseData.job = data.job;
    builderJobHouseData.house_model = data.house_model;

    if (data.job) {
      await resolveJobName(data.job);
    }
  } catch (error) {
    if (error.response?.status === 404) {
      loading.value = false;
      return;
    }

    if (props.redirectOnSuccess) {
      await Swal.fire({
        icon: "error",
        title: "Error",
        text: "Error loading work account data.",
        confirmButtonText: "OK",
      });
      goList();
    } else {
      formBannerMessage.value = "Error loading work account data.";
    }
  } finally {
    loading.value = false;
  }
};

async function handleSubmit() {
  if (isViewMode.value) return;

  try {
    submitting.value = true;
    formBannerMessage.value = "";
    Object.keys(serverErrors).forEach((k) => delete serverErrors[k]);

    const trimmedData = {
      builder: local.builder,
      job: local.job,
      house_model: local.house_model,
      lot: (local.lot ?? "").trim(),
      address: (local.address ?? "").trim(),
      city: (local.city ?? "").trim(),
      state: (local.state ?? "").trim(),
      zipcode: (local.zipcode ?? "").trim(),
      default_price_type: local.default_price_type,
      title: (local.title ?? "").trim().toUpperCase(),
      notes: (local.notes ?? "").trim(),
      is_active: local.is_active,
    };

    if (!trimmedData.builder) {
      formBannerMessage.value = "Builder is required.";
      await Swal.fire("Validation", "Builder is required.", "warning");
      return;
    }
    if (!trimmedData.job) {
      formBannerMessage.value = "Community is required.";
      await Swal.fire("Validation", "Community is required.", "warning");
      return;
    }
    // Spot Lot: empty lot OK when address is present
    if (!trimmedData.lot && !trimmedData.address) {
      formBannerMessage.value = "Either Lot or Address is required.";
      await Swal.fire(
        "Validation",
        "Either Lot or Address is required.",
        "warning"
      );
      return;
    }
    if (!trimmedData.title) {
      formBannerMessage.value = "Title is required.";
      await Swal.fire("Validation", "Title is required.", "warning");
      return;
    }

    if (trimmedData.lot.length > 100) {
      await Swal.fire(
        "Validation",
        "Lot cannot exceed 100 characters.",
        "warning"
      );
      return;
    }
    if (trimmedData.address.length > 255) {
      await Swal.fire(
        "Validation",
        "Address cannot exceed 255 characters.",
        "warning"
      );
      return;
    }
    if (trimmedData.title.length > 200) {
      await Swal.fire(
        "Validation",
        "Title cannot exceed 200 characters.",
        "warning"
      );
      return;
    }
    if (trimmedData.city.length > 100) {
      await Swal.fire(
        "Validation",
        "City cannot exceed 100 characters.",
        "warning"
      );
      return;
    }
    if (trimmedData.state.length > 50) {
      await Swal.fire(
        "Validation",
        "State cannot exceed 50 characters.",
        "warning"
      );
      return;
    }
    if (trimmedData.zipcode.length > 20) {
      await Swal.fire(
        "Validation",
        "ZIP Code cannot exceed 20 characters.",
        "warning"
      );
      return;
    }
    if (trimmedData.notes.length > 500) {
      await Swal.fire(
        "Validation",
        "Notes cannot exceed 500 characters.",
        "warning"
      );
      return;
    }

    let savedData;
    const saveId = id.value;
    if (isEditMode.value) {
      const response = await axios.put(
        `/api/work-accounts/${saveId}/`,
        trimmedData
      );
      savedData = response.data;
    } else {
      const response = await axios.post("/api/work-accounts/", trimmedData);
      savedData = response.data;
    }

    emit("saved", savedData);

    if (isEditMode.value) {
      const { isConfirmed } = await Swal.fire({
        title: "Update schedule titles?",
        text: "Do you want to propagate this title change to all related schedule events? This will overwrite customized titles.",
        icon: "question",
        showCancelButton: true,
        confirmButtonText: "Yes, update",
        cancelButtonText: "No, keep as is",
      });

      if (isConfirmed) {
        try {
          const waId = saveId;
          if (waId) {
            const syncResp = await axios.post(
              `/api/work-accounts/${waId}/sync-schedule-titles/`
            );
            await Swal.fire({
              icon: "success",
              title: "Schedule Updated",
              text: `Updated ${syncResp.data?.updated_events || 0} events and ${
                syncResp.data?.updated_drafts || 0
              } drafts.`,
              timer: 2500,
              showConfirmButton: false,
            });
          }
        } catch (e) {
          await Swal.fire({
            icon: "error",
            title: "Sync Failed",
            text: "Could not synchronize schedule titles. You can try again later from Work Accounts.",
          });
        }
      }
    }

    if (props.redirectOnSuccess) {
      goList();
    }
  } catch (error) {
    const { status, data } = error?.response || {};

    if (status === 400 && data) {
      Object.assign(serverErrors, data);
      const messages = Object.entries(data)
        .map(
          ([field, msgs]) =>
            `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`
        )
        .join("\n");
      formBannerMessage.value = "There were validation errors.";
      await Swal.fire(
        "Oops!",
        messages || "There were validation errors.",
        "error"
      );
    } else if (status === 403) {
      formBannerMessage.value =
        "You do not have permission for this action.";
      await Swal.fire(
        "Forbidden",
        "You do not have permission for this action.",
        "error"
      );
    } else if (status === 409) {
      formBannerMessage.value =
        "This work account is in use and cannot be modified.";
      await Swal.fire(
        "Protected",
        "This work account is in use and cannot be modified.",
        "error"
      );
    } else {
      formBannerMessage.value = "Error saving the work account.";
      await Swal.fire("Oops!", "Error saving the work account.", "error");
    }
  } finally {
    submitting.value = false;
  }
}

function goList() {
  router.push({ name: props.listRouteName || "work-accounts" }).catch(() => {
    router.push("/work-accounts");
  });
}

function goToEdit() {
  if (!id.value) return;
  router.push({
    name: "work-accounts-form",
    query: { id: id.value, mode: "edit" },
  });
}

function onCancel() {
  if (props.redirectOnSuccess) {
    goList();
  } else {
    emit("cancel");
  }
}

onMounted(async () => {
  if (id.value && id.value !== null && id.value !== "null") {
    await loadWorkAccount();
  }
});
</script>

<style scoped>
.jr-wa-form {
  width: 100%;
  min-width: 0;
  max-width: 100%;
}

.jr-embedded-form {
  width: 100%;
}

.jr-embedded-form__panel {
  width: 100%;
}

.jr-wa-form__status {
  margin: 0;
  padding: 1rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-form-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .jr-wa-form:not(.jr-wa-form--drawer) .jr-form-grid--identity {
    grid-template-columns: minmax(12rem, 20rem) max-content;
    align-items: start;
    column-gap: 1.5rem;
  }

  .jr-wa-form:not(.jr-wa-form--drawer) .jr-form-grid--details {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .jr-wa-form:not(.jr-wa-form--drawer) .jr-form-grid__price {
    grid-column: 1 / -1;
    max-width: 22rem;
  }

  .jr-wa-form__active {
    justify-self: start;
  }
}

.jr-wa-form--drawer .jr-form-grid {
  gap: 0.85rem;
}

.jr-wa-form--drawer .jr-form-grid--identity,
.jr-wa-form--drawer .jr-form-grid--details {
  grid-template-columns: minmax(0, 1fr);
}

.jr-wa-form--drawer .jr-form-grid__full,
.jr-wa-form--drawer .jr-form-grid__price {
  grid-column: auto;
  max-width: none;
}

.jr-form-grid__full {
  grid-column: 1 / -1;
}

.jr-wa-form__active :deep(.jr-checkbox) {
  min-height: 2.5rem;
}

.jr-form-banner {
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
  background: var(--color-jr-danger-subtle);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
}

.jr-form-banner:focus {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-wa-form :deep(.jr-wa-form__title-input),
.jr-wa-form :deep(#wa-title) {
  text-transform: uppercase;
}

.jr-wa-form :deep(.jr-wa-form__title-input::placeholder),
.jr-wa-form :deep(#wa-title::placeholder) {
  text-transform: none;
}

.jr-wa-form__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.jr-wa-form__actions--sticky {
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.25rem;
  margin-top: 0.5rem;
  background: var(--color-jr-page, #f3f4f6);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-embedded-form .jr-wa-form__actions--sticky {
  background: var(--color-jr-surface, #fff);
}

@media (max-width: 767px) {
  .jr-wa-form__actions--sticky {
    padding-bottom: calc(0.25rem + env(safe-area-inset-bottom, 0px));
  }
}

</style>
