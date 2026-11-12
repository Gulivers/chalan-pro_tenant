<template>
  <JRPage>
    <JRPageHeader :title="pageTitle">
      <template v-if="canEditFromView" #actions>
        <JRButton variant="primary" size="sm" @click="goToEdit">
          {{ $t('crews.form.editCrew') }}
        </JRButton>
      </template>
    </JRPageHeader>

    <div class="jr-crew-form">
      <p v-if="loading" class="jr-crew-form__status" role="status">
        {{ $t('crews.form.loadingCrew') }}
      </p>

      <form
        v-else
        class="jr-crew-form__form"
        @submit.prevent="handleSubmit"
        novalidate>
        <JRSection :title="$t('common.sectionDetails')">
          <div class="jr-form-grid">
            <JRField
              v-slot="{ describedby, invalid }"
              :label="$t('crews.form.crewName')"
              inputId="crew-name"
              required
              :error="fieldErrors.name">
              <JRInput
                inputId="crew-name"
                v-model="form.name"
                maxlength="255"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('name')" />
            </JRField>

            <JRField
              v-slot="{ describedby }"
              :label="$t('crews.colCategory')"
              inputId="crew-category">
              <JRSelect
                inputId="crew-category"
                v-model="form.category"
                :options="categories"
                optionLabel="name"
                optionValue="id"
                :placeholder="$t('crews.form.selectCategory')"
                filter
                showClear
                :disabled="isDisabled"
                :ariaDescribedby="describedby" />
            </JRField>

            <JRField
              v-slot="{ describedby }"
              :label="$t('crews.form.crewMembers')"
              inputId="crew-members"
              class="jr-form-grid__full">
              <JRSelect
                inputId="crew-members"
                v-model="form.members"
                :options="users"
                optionLabel="username"
                optionValue="id"
                :placeholder="$t('crews.form.selectCrewMembers')"
                multiple
                filter
                showClear
                :disabled="isDisabled"
                :ariaDescribedby="describedby" />
            </JRField>

            <JRField :label="$t('common.active')" inputId="crew-status">
              <JRCheckbox
                inputId="crew-status"
                v-model="form.status"
                :ariaLabel="$t('common.active')"
                :disabled="isDisabled" />
            </JRField>

            <JRField
              :label="$t('crews.form.canCreateSchedule')"
              inputId="crew-permission-create-event"
              :hint="$t('crews.form.canCreateScheduleHint')">
              <JRCheckbox
                inputId="crew-permission-create-event"
                v-model="form.permission_create_event"
                :ariaLabel="$t('crews.form.canCreateSchedule')"
                :disabled="isDisabled" />
            </JRField>
          </div>
        </JRSection>

        <JRSection :title="$t('crews.form.sectionCrewType')">
          <div class="jr-form-grid">
            <JRField
              v-slot="{ describedby }"
              inputId="crew-type"
              class="jr-form-grid__full"
              :hint="$t('crews.form.crewTypeHint')">
              <JRSelect
                inputId="crew-type"
                :modelValue="crewType"
                :options="crewTypeOptions"
                optionLabel="label"
                optionValue="value"
                :disabled="isDisabled"
                :ariaDescribedby="describedby"
                ariaLabel="Crew type"
                @update:modelValue="onCrewTypeUpdate" />
              <Message
                v-if="crewType === 'piece_work'"
                class="jr-crew-form__info"
                severity="info"
                :closable="false">
                {{ $t("crews.form.pieceWorkNoCommunities") }}
              </Message>
            </JRField>
          </div>
        </JRSection>

        <JRSection v-if="crewType === 'supervisor'" :title="$t('parties.communitiesTitle')">
          <div class="jr-form-grid">
            <JRField
              v-slot="{ describedby }"
              inputId="crew-jobs"
              class="jr-form-grid__full"
              :hint="$t('crews.form.assignCommunitiesHint')">
              <div
                id="crew-jobs"
                class="jr-crew-form__jobs"
                role="group"
                :aria-label="$t('parties.communitiesTitle')"
                :aria-describedby="
                  [describedby, 'crew-jobs-builder-hint'].filter(Boolean).join(' ')
                ">
                <div class="jr-crew-form__jobs-unit">
                  <div class="jr-crew-form__jobs-toolbar">
                    <label
                      class="jr-crew-form__jobs-toolbar-label"
                      for="crew-jobs-builder"
                      >{{ $t("parties.colBuilder") }}</label
                    >
                    <div class="jr-crew-form__jobs-toolbar-select">
                      <JRSelect
                        inputId="crew-jobs-builder"
                        v-model="jobsBuilderFilter"
                        :options="customerBuilders"
                        optionLabel="name"
                        optionValue="id"
                        :placeholder="$t('crews.form.allCustomers')"
                        filter
                        showClear
                        :disabled="isDisabled"
                        ariaDescribedby="crew-jobs-builder-hint" />
                    </div>
                    <p id="crew-jobs-builder-hint" class="jr-crew-form__jobs-toolbar-hint">
                      {{ $t("crews.form.showAvailableForCustomer") }}
                    </p>
                  </div>

                  <PickList
                    v-model="jobsPickList"
                    dataKey="id"
                    filterBy="searchText"
                    :disabled="isDisabled"
                    :showSourceControls="false"
                    :showTargetControls="false"
                    breakpoint="768px"
                    scrollHeight="18rem"
                    :sourceFilterPlaceholder="$t('crews.form.searchAvailable')"
                    :targetFilterPlaceholder="$t('crews.form.searchChosen')"
                    class="jr-crew-form__picklist"
                    :aria-label="$t('parties.communitiesTitle')"
                    @update:modelValue="onJobsPickListUpdate">
                    <template #sourceheader>
                      <span class="jr-crew-form__pick-header">{{
                        $t("crews.form.available")
                      }}</span>
                    </template>
                    <template #targetheader>
                      <span class="jr-crew-form__pick-header">{{
                        $t("crews.form.chosen")
                      }}</span>
                    </template>
                    <template #option="{ option }">
                      <div class="jr-crew-form__pick-option">
                        <span class="jr-crew-form__pick-option-name">{{
                          option.name
                        }}</span>
                        <span
                          v-if="option.builderName || builderLabel(option.builder)"
                          class="jr-crew-form__pick-option-builder"
                          >{{
                            option.builderName || builderLabel(option.builder)
                          }}</span
                        >
                      </div>
                    </template>
                  </PickList>
                </div>
              </div>
            </JRField>
          </div>
        </JRSection>

        <div class="jr-crew-form__actions jr-crew-form__actions--sticky">
          <template v-if="!isViewMode">
            <JRButton type="submit" variant="primary" :disabled="isDisabled">
              {{ submitting ? $t('common.saving') : $t('common.save') }}
            </JRButton>
            <JRButton
              type="button"
              variant="secondary"
              :disabled="submitting"
              @click="goList">
              {{ $t('common.cancel') }}
            </JRButton>
          </template>
          <JRButton
            v-else
            type="button"
            variant="secondary"
            :disabled="submitting"
            @click="goList">
            {{ $t('common.back') }}
          </JRButton>
        </div>
      </form>
    </div>

    <JRDialog
      :visible="pieceWorkConfirmVisible"
      :header="$t('crews.form.pieceWorkConfirmHeader')"
      :message="$t('crews.form.pieceWorkConfirmMessage')"
      :confirmLabel="$t('crews.form.clearAndSwitch')"
      :cancelLabel="$t('common.cancel')"
      confirmVariant="danger"
      @update:visible="onPieceWorkConfirmVisible"
      @confirm="confirmPieceWorkSwitch" />
  </JRPage>
</template>

<script setup>
import axios from "axios";
import Swal from "sweetalert2";
import Message from "primevue/message";
import PickList from "primevue/picklist";
import { onMounted, ref, computed, watch, getCurrentInstance } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRInput,
  JRSelect,
  JRCheckbox,
  JRButton,
  JRDialog,
} from "@ui";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const { t } = useI18n({ useScope: "global" });
const id = route.params.id;
const isViewMode = computed(() => route.name === "crew-view");
const isEditMode = computed(() => !!id && !isViewMode.value);

const submitting = ref(false);
const loading = ref(false);
const fieldErrors = ref({});
const categories = ref([]);
const users = ref([]);
const jobs = ref([]);
const builders = ref([]);
const jobsBuilderFilter = ref(null);
/** PickList model: [available jobs, chosen jobs] as job objects */
const jobsPickList = ref([[], []]);
/** UI-only: 'supervisor' (Crew supervisor or Punch-out work) | 'piece_work' — derived from form.jobs, not sent to API */
const crewType = ref("piece_work");
const pieceWorkConfirmVisible = ref(false);
const crewTypeOptions = [
  { label: "Crew supervisor or Punch-out work", value: "supervisor" },
  { label: "Crew piece work", value: "piece_work" },
];
const form = ref({
  name: "",
  category: null,
  members: [],
  jobs: [],
  status: true,
  permission_create_event: false,
});

const isDisabled = computed(() => isViewMode.value || submitting.value);
const canEditFromView = computed(
  () =>
    isViewMode.value &&
    !!id &&
    !!proxy?.hasPermission?.("crewsapp.change_crew")
);
const buildersById = computed(() => {
  const map = new Map();
  for (const b of builders.value || []) {
    if (b?.id != null) map.set(b.id, b);
  }
  return map;
});
/** Builders with Is Customer (API: customer_rank boolean from customer_rank > 0). */
const customerBuilders = computed(() =>
  (builders.value || []).filter((b) => !!b?.customer_rank)
);
const pageTitle = computed(() => {
  if (isViewMode.value) return t("crews.form.viewCrew");
  if (isEditMode.value) return t("crews.form.editCrewTitle");
  return t("crews.form.addCrew");
});
function deriveCrewTypeFromJobs(jobIds) {
  return (jobIds || []).length > 0 ? "supervisor" : "piece_work";
}

function onCrewTypeUpdate(next) {
  if (next === crewType.value) return;
  if (next === "supervisor") {
    crewType.value = "supervisor";
    return;
  }
  // Pending switch to piece_work — do not flip select until confirmed if jobs exist
  if ((form.value.jobs || []).length > 0) {
    pieceWorkConfirmVisible.value = true;
    return;
  }
  crewType.value = "piece_work";
}

function confirmPieceWorkSwitch() {
  form.value.jobs = [];
  rebuildJobsPickList();
  crewType.value = "piece_work";
  pieceWorkConfirmVisible.value = false;
  proxy?.notifyToastSuccess?.(t("crews.form.communitiesCleared"));
}

function onPieceWorkConfirmVisible(visible) {
  pieceWorkConfirmVisible.value = visible;
  // Cancel / dismiss keeps crewType as supervisor (select never flipped)
}

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
}

function goList() {
  router.push({ name: "crew-list" });
}

function goToEdit() {
  if (!id) return;
  router.push({ name: "crew-edit", params: { id } });
}

function builderLabel(builderId) {
  if (builderId == null) return "";
  return buildersById.value.get(builderId)?.name || "";
}

/** Enrich job for PickList display + search (name and builder). */
function toJobOption(job) {
  if (!job) return null;
  const name = job.name || "";
  const builderName = builderLabel(job.builder);
  return {
    ...job,
    builderName,
    searchText: [name, builderName].filter(Boolean).join(" "),
  };
}

function matchesBuilderFilter(job) {
  if (jobsBuilderFilter.value == null || jobsBuilderFilter.value === "") {
    return true;
  }
  return Number(job?.builder) === Number(jobsBuilderFilter.value);
}

/**
 * Rebuild PickList lists from catalog + form.jobs ids.
 * Source is filtered by Builder; chosen (target) always reflects form.jobs.
 */
function rebuildJobsPickList() {
  const selectedIds = new Set(form.value.jobs || []);
  const byId = new Map((jobs.value || []).map((j) => [j.id, j]));
  const target = (form.value.jobs || [])
    .map((jobId) => toJobOption(byId.get(jobId)))
    .filter(Boolean);
  const source = (jobs.value || [])
    .filter((j) => !selectedIds.has(j.id) && matchesBuilderFilter(j))
    .map(toJobOption);
  jobsPickList.value = [source, target];
}

function syncFormJobsFromPickList(value) {
  const target = Array.isArray(value?.[1]) ? value[1] : [];
  form.value.jobs = target.map((j) => j.id).filter((jobId) => jobId != null);
}

function onJobsPickListUpdate(value) {
  syncFormJobsFromPickList(value);
  // Re-apply builder filter on source so removed jobs only reappear if they match.
  const selectedIds = new Set(form.value.jobs || []);
  const target = (Array.isArray(value?.[1]) ? value[1] : [])
    .map((j) => toJobOption(j))
    .filter(Boolean);
  const source = (jobs.value || [])
    .filter((j) => !selectedIds.has(j.id) && matchesBuilderFilter(j))
    .map(toJobOption);
  jobsPickList.value = [source, target];
}

watch(jobsBuilderFilter, () => {
  rebuildJobsPickList();
});

async function loadOptions() {
  try {
    const [catRes, usersRes, jobsRes, buildersRes] = await Promise.all([
      axios.get("/api/categories/"),
      axios.get("/api/crew-users/"),
      axios.get("/api/jobs/"),
      axios.get("/api/builders/"),
    ]);
    categories.value = catRes.data.results ?? catRes.data;
    users.value = usersRes.data;
    jobs.value = jobsRes.data.results ?? jobsRes.data;
    builders.value = buildersRes.data.results ?? buildersRes.data;
  } catch (err) {
    console.error("Load options error:", err);
  }
}

async function loadData() {
  if (!id) return;
  try {
    const { data } = await axios.get(`/api/crews/${id}/`);
    form.value = {
      name: data.name || "",
      category: data.category ?? null,
      members: Array.isArray(data.members) ? data.members : [],
      jobs: Array.isArray(data.jobs) ? data.jobs : [],
      status: !!data.status,
      permission_create_event: !!data.permission_create_event,
    };
    crewType.value = deriveCrewTypeFromJobs(form.value.jobs);
  } catch (err) {
    console.error("Load error:", err);
    await Swal.fire(
      t("common.error"),
      t("crews.form.swalLoadCrewError"),
      "error"
    );
  }
}

function validate() {
  const name = (form.value.name || "").trim();
  form.value.name = name;
  if (!name) {
    fieldErrors.value = { name: "Crew name is required." };
    Swal.fire(
      t("common.validationError"),
      t("crews.form.swalNameRequired"),
      "warning"
    );
    return false;
  }
  return true;
}

async function handleSubmit() {
  if (!validate()) return;
  submitting.value = true;
  fieldErrors.value = {};
  try {
    // Piece-work truth: empty jobs; supervisor/punch-out may have zero or more communities
    const payloadJobs =
      crewType.value === "piece_work" ? [] : form.value.jobs || [];
    if (crewType.value === "piece_work") {
      form.value.jobs = [];
    }
    const payload = {
      name: form.value.name.trim(),
      category: form.value.category,
      members: form.value.members || [],
      jobs: payloadJobs,
      status: form.value.status,
      permission_create_event: form.value.permission_create_event,
    };
    if (id) {
      await axios.patch(`/api/crews/${id}/`, payload);
      proxy?.notifyToastSuccess?.(t("crews.form.swalCrewUpdated"));
    } else {
      await axios.post("/api/crews/", payload);
      proxy?.notifyToastSuccess?.(t("crews.form.swalCrewCreated"));
    }
    router.push({ name: "crew-list" });
  } catch (err) {
    console.error("Save error:", err);
    const data = err.response?.data;
    let msg = "Error saving crew.";
    if (data) {
      if (typeof data === "string") msg = data;
      else if (data.detail)
        msg = Array.isArray(data.detail) ? data.detail.join(" ") : data.detail;
      else if (data.non_field_errors) msg = data.non_field_errors.join(" ");
      else msg = Object.values(data).flat().join(" ") || msg;
      const next = {};
      Object.entries(data).forEach(([field, msgs]) => {
        if (field === "detail" || field === "non_field_errors") return;
        next[field] = Array.isArray(msgs) ? msgs.join(", ") : String(msgs);
      });
      fieldErrors.value = next;
    }
    await Swal.fire(t("common.validationError"), msg, "error");
  } finally {
    submitting.value = false;
  }
}

onMounted(async () => {
  loading.value = true;
  try {
    await loadOptions();
    await loadData();
    if (!id) {
      crewType.value = "piece_work";
    }
    rebuildJobsPickList();
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.jr-crew-form__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-crew-form__status {
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

  .jr-form-grid__full {
    grid-column: 1 / -1;
  }
}

.jr-crew-form :deep(.jr-checkbox) {
  column-gap: 0.85rem;
  align-items: center;
}

.jr-crew-form :deep(.jr-checkbox__label) {
  margin-inline-start: 0.15rem;
}

.jr-crew-form__info {
  margin: 0.5rem 0 0;
  --p-message-info-background: var(--color-jr-info-subtle);
  --p-message-info-border-color: var(--color-jr-border);
  --p-message-info-color: var(--color-jr-info-text);
  --p-message-border-radius: var(--radius-jr-control, 0);
}

.jr-crew-form__jobs {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.jr-crew-form__jobs-unit {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #ffffff);
  overflow: hidden;
}

.jr-crew-form__jobs-toolbar {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 0.35rem 0.75rem;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: var(--color-jr-surface-muted, #f9fafb);
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-crew-form__jobs-toolbar-label {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-text, #111827);
  white-space: nowrap;
}

.jr-crew-form__jobs-toolbar-select {
  min-width: 0;
  width: 100%;
  max-width: 22rem;
}

.jr-crew-form__jobs-toolbar-hint {
  grid-column: 1 / -1;
  margin: 0;
  font-size: 0.75rem;
  font-weight: 400;
  line-height: 1.4;
  color: var(--color-jr-muted, #4b5563);
}

.jr-crew-form__pick-header {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-text, #111827);
}

.jr-crew-form__pick-option {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.35rem;
  min-width: 0;
}

.jr-crew-form__pick-option-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-jr-text, #111827);
}

.jr-crew-form__pick-option-builder {
  font-size: 0.75rem;
  font-weight: 400;
  color: var(--color-jr-muted, #4b5563);
}

.jr-crew-form__pick-option-builder::before {
  content: "· ";
}

.jr-crew-form__picklist {
  width: 100%;
}

.jr-crew-form__picklist :deep(.p-picklist) {
  gap: 0.75rem;
  padding: 0.5rem 0.75rem 0.75rem;
}

.jr-crew-form__picklist :deep(.p-picklist-list-container),
.jr-crew-form__picklist :deep(.p-picklist-list),
.jr-crew-form__picklist :deep(.p-picklist-filter-container),
.jr-crew-form__picklist :deep(.p-inputtext),
.jr-crew-form__picklist :deep(.p-button) {
  border-radius: var(--radius-jr-control, 0);
}

.jr-crew-form__picklist :deep(.p-picklist-list-container) {
  border-color: var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #ffffff);
}

.jr-crew-form__picklist :deep(.p-picklist-header) {
  padding: 0.4rem 0.65rem;
  background: var(--color-jr-surface-muted, #f9fafb);
  border-color: var(--color-jr-border, #e5e7eb);
}

.jr-crew-form__picklist :deep(.p-picklist-option) {
  border-radius: var(--radius-jr-control, 0);
}

@media (max-width: 767px) {
  .jr-crew-form__jobs-toolbar {
    grid-template-columns: 1fr;
  }

  .jr-crew-form__jobs-toolbar-select {
    max-width: none;
  }

  .jr-crew-form__actions--sticky {
    padding-bottom: calc(0.25rem + env(safe-area-inset-bottom, 0px));
  }
}

.jr-crew-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.jr-crew-form__actions--sticky {
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.25rem;
  margin-top: 0.5rem;
  background: var(--color-jr-page, #f3f4f6);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}
</style>
