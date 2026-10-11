<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" />

    <div class="jr-truck-assignment-form">
      <p
        v-if="loading"
        class="jr-truck-assignment-form__status"
        role="status">
        Loading truck assignment…
      </p>

      <form
        v-else
        class="jr-truck-assignment-form__form"
        @submit.prevent="handleSubmit"
        novalidate>
        <JRSection title="Assignment">
          <div class="jr-form-grid">
            <JRField
              v-slot="{ describedby, invalid }"
              label="Assigned Crew"
              inputId="ta-crew"
              required
              :error="fieldErrors.crew">
              <JRSelect
                inputId="ta-crew"
                v-model="form.crew"
                :options="crews"
                optionLabel="name"
                optionValue="id"
                placeholder="Select crew"
                filter
                showClear
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('crew')" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Assigned Trucks"
              inputId="ta-trucks"
              required
              class="jr-form-grid__full"
              :error="fieldErrors.trucks">
              <JRSelect
                inputId="ta-trucks"
                v-model="form.trucks"
                :options="trucksOptions"
                optionLabel="label"
                optionValue="id"
                placeholder="Select truck(s)"
                multiple
                filter
                showClear
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('trucks')" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Assigned Date"
              inputId="ta-assigned-date"
              required
              :error="fieldErrors.assigned_date">
              <JRInput
                inputId="ta-assigned-date"
                v-model="form.assigned_date"
                type="date"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('assigned_date')" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Assigned Time"
              inputId="ta-assigned-time"
              required
              :error="fieldErrors.assigned_time">
              <JRInput
                inputId="ta-assigned-time"
                v-model="form.assigned_time"
                type="time"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('assigned_time')" />
            </JRField>

            <JRField
              v-slot="{ describedby }"
              label="Unassigned Date"
              inputId="ta-unassigned-date">
              <JRInput
                inputId="ta-unassigned-date"
                v-model="form.unassigned_date"
                type="date"
                :disabled="isDisabled"
                :ariaDescribedby="describedby" />
            </JRField>

            <JRField
              v-slot="{ describedby }"
              label="Unassigned Time"
              inputId="ta-unassigned-time"
              hint="Uses current time if empty when an unassigned date is set">
              <JRInput
                inputId="ta-unassigned-time"
                v-model="form.unassigned_time"
                type="time"
                :disabled="isDisabled"
                :ariaDescribedby="describedby" />
            </JRField>
          </div>
        </JRSection>

        <div
          class="jr-truck-assignment-form__actions jr-truck-assignment-form__actions--sticky">
          <template v-if="!isViewMode">
            <JRButton type="submit" variant="primary" :disabled="isDisabled">
              {{ submitting ? "Saving..." : "Save" }}
            </JRButton>
            <JRButton
              type="button"
              variant="secondary"
              :disabled="submitting"
              @click="goList">
              Cancel
            </JRButton>
          </template>
          <JRButton
            v-else
            type="button"
            variant="secondary"
            :disabled="submitting"
            @click="goList">
            Back
          </JRButton>
        </div>
      </form>
    </div>
  </JRPage>
</template>

<script setup>
import axios from "axios";
import Swal from "sweetalert2";
import { onMounted, ref, computed, getCurrentInstance } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRInput,
  JRSelect,
  JRButton,
} from "@ui";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(
  () => route.name === "crew-truck-assignment-view"
);
const isEditMode = computed(() => !!id && !isViewMode.value);

const submitting = ref(false);
const loading = ref(false);
const fieldErrors = ref({});
const crews = ref([]);
const trucks = ref([]);
const form = ref({
  crew: null,
  trucks: [],
  assigned_date: "",
  assigned_time: "",
  unassigned_date: "",
  unassigned_time: "",
});

const trucksOptions = computed(() =>
  trucks.value.map((t) => ({
    ...t,
    label: t
      ? `${t.plate_number || ""} - ${t.model || ""}`.trim()
      : "",
  }))
);

const isDisabled = computed(() => isViewMode.value || submitting.value);
const pageTitle = computed(() => {
  if (isViewMode.value) return "View Truck Assignment";
  if (isEditMode.value) return "Edit Truck Assignment";
  return "Add Truck Assignment";
});

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
}

function toDatePart(d) {
  if (!d) return "";
  const date = new Date(d);
  if (isNaN(date.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

function toTimePart(d) {
  if (!d) return "";
  const date = new Date(d);
  if (isNaN(date.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function toISOString(dateStr, timeStr) {
  if (!dateStr || !timeStr) return null;
  const time = timeStr.length === 5 ? `${timeStr}:00` : timeStr;
  const dt = new Date(`${dateStr}T${time}`);
  return isNaN(dt.getTime()) ? null : dt.toISOString();
}

function goList() {
  router.push({ name: "crew-truck-assignments" });
}

async function loadOptions() {
  try {
    const [crewsRes, trucksRes] = await Promise.all([
      axios.get("/api/crews/"),
      axios.get("/api/trucks/"),
    ]);
    crews.value = crewsRes.data.results ?? crewsRes.data;
    trucks.value = trucksRes.data.results ?? trucksRes.data;
  } catch (err) {
    console.error("Load options error:", err);
  }
}

async function loadData() {
  if (!id) {
    const now = new Date();
    form.value.assigned_date = toDatePart(now);
    form.value.assigned_time = toTimePart(now);
    return;
  }
  try {
    const { data } = await axios.get(`/api/truck-assignments/${id}/`);
    form.value = {
      crew: data.crew ?? null,
      trucks: Array.isArray(data.trucks)
        ? data.trucks
        : data.trucks
          ? [data.trucks]
          : [],
      assigned_date: toDatePart(data.assigned_at),
      assigned_time: toTimePart(data.assigned_at),
      unassigned_date: data.unassigned_at
        ? toDatePart(data.unassigned_at)
        : "",
      unassigned_time: data.unassigned_at
        ? toTimePart(data.unassigned_at)
        : "",
    };
  } catch (err) {
    console.error("Load error:", err);
    await Swal.fire("Oops!", "Error loading the truck assignment.", "error");
  }
}

function validate() {
  if (!form.value.crew) {
    fieldErrors.value = { crew: "Assigned crew is required." };
    Swal.fire("Validation", "Assigned crew is required.", "warning");
    return false;
  }
  if (!form.value.trucks?.length) {
    fieldErrors.value = { trucks: "At least one truck is required." };
    Swal.fire("Validation", "At least one truck is required.", "warning");
    return false;
  }
  if (!form.value.assigned_date || !form.value.assigned_time) {
    fieldErrors.value = {
      assigned_date: !form.value.assigned_date
        ? "Assigned date is required."
        : undefined,
      assigned_time: !form.value.assigned_time
        ? "Assigned time is required."
        : undefined,
    };
    Swal.fire(
      "Validation",
      "Assigned at (date and time) is required.",
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
    const assigned_at = toISOString(
      form.value.assigned_date,
      form.value.assigned_time
    );
    let unassigned_at = null;
    if (form.value.unassigned_date) {
      const time = form.value.unassigned_time || toTimePart(new Date());
      unassigned_at = toISOString(form.value.unassigned_date, time);
    }

    const truckIds = (form.value.trucks || []).map((t) =>
      typeof t === "object" && t !== null && "id" in t ? t.id : t
    );
    const payload = {
      crew: form.value.crew,
      trucks: truckIds,
      assigned_at,
      unassigned_at,
    };
    if (id) {
      await axios.patch(`/api/truck-assignments/${id}/`, payload);
      proxy?.notifyToastSuccess?.("Truck assignment updated.");
    } else {
      await axios.post("/api/truck-assignments/", payload);
      proxy?.notifyToastSuccess?.("Truck assignment created.");
    }
    router.push({ name: "crew-truck-assignments" });
  } catch (err) {
    console.error("Save error:", err);
    const data = err.response?.data;
    let msg = "Error saving truck assignment.";
    if (data) {
      if (typeof data === "string") msg = data;
      else if (data.detail)
        msg = Array.isArray(data.detail) ? data.detail.join(" ") : data.detail;
      else if (data.non_field_errors) msg = data.non_field_errors.join(" ");
      else msg = Object.values(data).flat().join(" ") || msg;
      if (typeof data === "object") {
        const next = {};
        Object.entries(data).forEach(([field, msgs]) => {
          if (field === "detail" || field === "non_field_errors") return;
          next[field] = Array.isArray(msgs) ? msgs.join(", ") : String(msgs);
        });
        fieldErrors.value = next;
      }
    }
    await Swal.fire("Validation Error", msg, "error");
  } finally {
    submitting.value = false;
  }
}

onMounted(async () => {
  loading.value = true;
  try {
    await loadOptions();
    await loadData();
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.jr-truck-assignment-form__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-truck-assignment-form__status {
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

.jr-truck-assignment-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.jr-truck-assignment-form__actions--sticky {
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.25rem;
  margin-top: 0.5rem;
  background: var(--color-jr-page, #f3f4f6);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}
</style>
