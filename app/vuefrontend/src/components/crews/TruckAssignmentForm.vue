<template>
  <JRPage>
    <JRPageHeader :title="pageTitle">
      <template v-if="canEditFromView" #actions>
        <JRButton variant="primary" size="sm" @click="goToEdit">
          Edit truck assignment
        </JRButton>
      </template>
    </JRPageHeader>

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
              :error="fieldErrors.trucks || fieldErrors.truck_readings">
              <JRSelect
                v-if="!isViewMode"
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
                @update:modelValue="onTrucksChange" />
              <p
                v-if="!isViewMode"
                class="jr-truck-links__note jr-truck-links__note--below-select">
                Select one or more trucks, then enter mileage for each.
              </p>
              <ul
                v-if="selectedTruckLinks.length"
                class="jr-truck-links">
                <li
                  v-for="truck in selectedTruckLinks"
                  :key="truck.id"
                  class="jr-truck-links__item">
                  <router-link
                    class="jr-master-row__name jr-master-row__name--link"
                    :to="truckViewTo(truck.id)"
                    :aria-label="`View truck ${truck.unit_number || truck.plate_number}`">
                    {{ truck.unit_number || "—" }}
                    <span class="jr-truck-links__plate"
                      >· {{ truck.plate_number || "—" }}</span
                    >
                  </router-link>
                  <span
                    v-if="truck.make || truck.model"
                    class="jr-truck-links__meta">
                    {{ [truck.make, truck.model].filter(Boolean).join(" ") }}
                  </span>
                </li>
              </ul>
              <p
                v-else-if="isViewMode"
                class="jr-truck-assignment-form__status">
                No trucks assigned.
              </p>
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
              inputId="ta-unassigned-date"
              hint="When set, ending mileage is required for each truck.">
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

        <JRSection
          v-if="mileageRows.length"
          title="Odometer readings (miles)">
          <Message
            severity="info"
            :closable="false"
            class="jr-truck-assignment-form__info">
            Enter starting mileage for each truck. Ending mileage is required
            when registering the return (unassigned date).
          </Message>
          <div
            v-for="row in mileageRows"
            :key="row.truck"
            class="jr-mileage-card">
            <div class="jr-mileage-card__title">
              <router-link
                class="jr-master-row__name jr-master-row__name--link"
                :to="truckViewTo(row.truck)"
                :aria-label="`View truck ${row.unit_number || row.plate_number}`">
                <strong>{{ row.unit_number || "—" }}</strong>
                <span class="jr-mileage-card__plate"
                  >· {{ row.plate_number || "—" }}</span
                >
              </router-link>
              <span class="jr-mileage-card__meta">
                {{ [row.make, row.model].filter(Boolean).join(" ") }}
              </span>
            </div>
            <div class="jr-form-grid">
              <JRField
                v-slot="{ describedby, invalid }"
                label="Starting Mileage"
                :inputId="`ta-start-${row.truck}`"
                required
                :error="row.startError">
                <JRInput
                  :inputId="`ta-start-${row.truck}`"
                  v-model="row.starting_mileage"
                  type="number"
                  :min="0"
                  :step="1"
                  :disabled="isDisabled"
                  :invalid="invalid"
                  required
                  :ariaDescribedby="describedby"
                  @update:modelValue="row.startError = ''" />
              </JRField>
              <JRField
                v-slot="{ describedby, invalid }"
                label="Ending Mileage"
                :inputId="`ta-end-${row.truck}`"
                :required="!!form.unassigned_date"
                :error="row.endError">
                <JRInput
                  :inputId="`ta-end-${row.truck}`"
                  v-model="row.ending_mileage"
                  type="number"
                  :min="0"
                  :step="1"
                  :disabled="isDisabled"
                  :invalid="invalid"
                  :ariaDescribedby="describedby"
                  @update:modelValue="row.endError = ''" />
              </JRField>
            </div>
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
import Message from "primevue/message";
import { onMounted, ref, computed, getCurrentInstance, watch } from "vue";
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
const mileageRows = ref([]);
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
      ? `${t.unit_number || "—"} · ${t.plate_number || ""} — ${[t.make, t.model].filter(Boolean).join(" ")}`.trim()
      : "",
  }))
);

const selectedTruckLinks = computed(() => {
  const ids = (form.value.trucks || []).map((t) =>
    typeof t === "object" && t !== null && "id" in t ? Number(t.id) : Number(t)
  );
  return ids
    .map((tid) => {
      const fromCatalog = trucks.value.find((x) => Number(x.id) === tid);
      const fromRows = mileageRows.value.find((r) => Number(r.truck) === tid);
      if (fromCatalog) {
        return {
          id: tid,
          unit_number: fromCatalog.unit_number || "",
          plate_number: fromCatalog.plate_number || "",
          make: fromCatalog.make || "",
          model: fromCatalog.model || "",
        };
      }
      if (fromRows) {
        return {
          id: tid,
          unit_number: fromRows.unit_number || "",
          plate_number: fromRows.plate_number || "",
          make: fromRows.make || "",
          model: fromRows.model || "",
        };
      }
      return {
        id: tid,
        unit_number: "",
        plate_number: `#${tid}`,
        make: "",
        model: "",
      };
    })
    .filter((t) => Number.isFinite(t.id));
});

function truckViewTo(truckId) {
  return { name: "crew-truck-view", params: { id: truckId } };
}

const isDisabled = computed(() => isViewMode.value || submitting.value);
const pageTitle = computed(() => {
  if (isViewMode.value) return "View Truck Assignment";
  if (isEditMode.value) return "Edit Truck Assignment";
  return "Add Truck Assignment";
});
const canEditFromView = computed(
  () =>
    isViewMode.value &&
    !!id &&
    !!proxy?.hasPermission?.("crewsapp.change_truckassignment")
);

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
}

function truckMeta(truckId) {
  const t = trucks.value.find((x) => x.id === truckId);
  return {
    unit_number: t?.unit_number || "",
    plate_number: t?.plate_number || "",
    make: t?.make || "",
    model: t?.model || "",
  };
}

function syncMileageRows(truckIds, existingReadings = []) {
  const byTruck = new Map(
    (existingReadings || []).map((r) => [Number(r.truck), r])
  );
  const prevByTruck = new Map(
    mileageRows.value.map((r) => [Number(r.truck), r])
  );
  mileageRows.value = (truckIds || []).map((tid) => {
    const idNum = Number(tid);
    const prev = prevByTruck.get(idNum);
    const fromApi = byTruck.get(idNum);
    const meta = truckMeta(idNum);
    return {
      truck: idNum,
      ...meta,
      starting_mileage:
        prev?.starting_mileage ??
        (fromApi?.starting_mileage != null
          ? String(fromApi.starting_mileage)
          : ""),
      ending_mileage:
        prev?.ending_mileage ??
        (fromApi?.ending_mileage != null && fromApi.ending_mileage !== null
          ? String(fromApi.ending_mileage)
          : ""),
      startError: "",
      endError: "",
    };
  });
}

function onTrucksChange(value) {
  clearFieldError("trucks");
  clearFieldError("truck_readings");
  const ids = (value || []).map((t) =>
    typeof t === "object" && t !== null && "id" in t ? t.id : t
  );
  form.value.trucks = ids;
  syncMileageRows(ids);
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

function goToEdit() {
  if (!id) return;
  router.push({ name: "crew-truck-assignment-edit", params: { id } });
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
    const truckIds = Array.isArray(data.trucks)
      ? data.trucks
      : data.trucks
        ? [data.trucks]
        : (data.truck_readings || []).map((r) => r.truck);
    form.value = {
      crew: data.crew ?? null,
      trucks: truckIds,
      assigned_date: toDatePart(data.assigned_at),
      assigned_time: toTimePart(data.assigned_at),
      unassigned_date: data.unassigned_at
        ? toDatePart(data.unassigned_at)
        : "",
      unassigned_time: data.unassigned_at
        ? toTimePart(data.unassigned_at)
        : "",
    };
    syncMileageRows(truckIds, data.truck_readings || []);
  } catch (err) {
    console.error("Load error:", err);
    await Swal.fire("Oops!", "Error loading the truck assignment.", "error");
  }
}

function parseMiles(value) {
  if (value === "" || value === null || value === undefined) return null;
  const n = Number(value);
  if (!Number.isFinite(n) || !Number.isInteger(n) || n < 0) return NaN;
  return n;
}

function validate() {
  mileageRows.value.forEach((r) => {
    r.startError = "";
    r.endError = "";
  });
  if (!form.value.crew) {
    fieldErrors.value = { crew: "Assigned crew is required." };
    Swal.fire("Validation", "Assigned crew is required.", "warning");
    return false;
  }
  if (!form.value.trucks?.length || !mileageRows.value.length) {
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

  const returnRequired = !!form.value.unassigned_date;
  let ok = true;
  for (const row of mileageRows.value) {
    const start = parseMiles(row.starting_mileage);
    if (start === null || Number.isNaN(start)) {
      row.startError = "Starting mileage is required (whole miles ≥ 0).";
      ok = false;
    }
    const endRaw = row.ending_mileage;
    const end =
      endRaw === "" || endRaw === null || endRaw === undefined
        ? null
        : parseMiles(endRaw);
    if (returnRequired) {
      if (end === null || Number.isNaN(end)) {
        row.endError = "Ending mileage is required when returning the truck.";
        ok = false;
      } else if (start !== null && !Number.isNaN(start) && end < start) {
        row.endError = "Ending mileage cannot be less than starting mileage.";
        ok = false;
      }
    } else if (end !== null) {
      if (Number.isNaN(end)) {
        row.endError = "Ending mileage must be a whole number of miles ≥ 0.";
        ok = false;
      } else if (start !== null && !Number.isNaN(start) && end < start) {
        row.endError = "Ending mileage cannot be less than starting mileage.";
        ok = false;
      }
    }
  }
  if (!ok) {
    fieldErrors.value = {
      truck_readings: "Check odometer readings for each truck.",
    };
    Swal.fire(
      "Validation",
      "Check starting/ending mileage for each truck.",
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

    const truck_readings = mileageRows.value.map((row) => {
      const start = parseMiles(row.starting_mileage);
      const endRaw = row.ending_mileage;
      const end =
        endRaw === "" || endRaw === null || endRaw === undefined
          ? null
          : parseMiles(endRaw);
      return {
        truck: row.truck,
        starting_mileage: start,
        ending_mileage: end,
      };
    });

    const payload = {
      crew: form.value.crew,
      assigned_at,
      unassigned_at,
      truck_readings,
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

watch(
  () => trucks.value,
  () => {
    if (mileageRows.value.length) {
      mileageRows.value = mileageRows.value.map((row) => ({
        ...row,
        ...truckMeta(row.truck),
      }));
    }
  }
);

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

.jr-truck-assignment-form__info {
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

  .jr-form-grid__full {
    grid-column: 1 / -1;
  }
}

.jr-mileage-card {
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  padding: 0.85rem 1rem;
  margin-bottom: 0.75rem;
  background: var(--color-jr-surface, #fff);
}

.jr-truck-links__note {
  margin: 0 0 0.4rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted, #6b7280);
}

.jr-truck-links__note--below-select {
  margin-top: 0.65rem;
}

.jr-truck-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.jr-truck-links__item {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: baseline;
  font-size: 0.875rem;
}

.jr-truck-links__plate {
  font-weight: 400;
}

.jr-truck-links__meta {
  color: var(--color-jr-muted, #6b7280);
  font-size: 0.8125rem;
}

.jr-mileage-card__title {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: baseline;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.jr-mileage-card__title .jr-master-row__name--link {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: baseline;
}

.jr-mileage-card__plate {
  color: var(--color-jr-text, #111827);
  font-weight: 400;
}

.jr-mileage-card__meta {
  color: var(--color-jr-muted, #6b7280);
  font-size: 0.8125rem;
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
