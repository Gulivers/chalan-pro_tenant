<template>
  <div class="container mt-3">
    <div class="text-center">
      <h3 class="text-warning">Truck Assignment</h3>
    </div>
    <div class="card shadow-sm mx-auto" style="max-width: 720px">
      <div class="card-header d-flex justify-content-center align-items-center">
        <h6 class="mb-0 w-100 text-center text-primary">{{ formTitle }}</h6>
      </div>
      <div class="card-body text-start">
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="mb-3">
            <label class="form-label d-flex align-items-center gap-2">
              Assigned Crew <span class="text-danger">*</span>
              <i
                v-tt
                class="fas fa-info-circle text-muted"
                data-title="Crew that will be assigned to the truck"></i>
            </label>
            <v-select
              :options="crews"
              v-model="form.crew"
              :reduce="(c) => c.id"
              label="name"
              placeholder="Select crew"
              :disabled="isViewMode || submitting"
              :clearable="true"
              v-tt
              data-title="Required. Select the crew for this assignment" />
          </div>
          <div class="mb-3">
            <label class="form-label d-flex align-items-center gap-2">
              Assigned Trucks <span class="text-danger">*</span>
              <i
                v-tt
                class="fas fa-info-circle text-muted"
                data-title="One or more trucks to assign to the crew"></i>
            </label>
            <v-select
              :options="trucksOptions"
              v-model="form.trucks"
              :reduce="(t) => t.id"
              label="label"
              placeholder="Select truck(s)"
              :disabled="isViewMode || submitting"
              multiple
              :close-on-select="false"
              :clearable="true"
              v-tt
              data-title="Required. Select one or more trucks for this assignment" />
          </div>
          <div class="mb-3">
            <label class="form-label d-flex align-items-center gap-2">
              Assigned At <span class="text-danger">*</span>
              <i
                v-tt
                class="fas fa-info-circle text-muted"
                data-title="Date and time when the assignment starts"></i>
            </label>
            <BInputGroup>
              <BFormInput
                v-model="form.assigned_date"
                type="date"
                :disabled="isViewMode || submitting"
                required
                v-tt
                data-title="Date when the crew is assigned to the truck" />
              <BFormInput
                v-model="form.assigned_time"
                type="time"
                :disabled="isViewMode || submitting"
                required
                v-tt
                data-title="Time when the assignment starts" />
            </BInputGroup>
          </div>
          <div class="mb-3">
            <label class="form-label d-flex align-items-center gap-2">
              Unassigned At
              <i
                v-tt
                class="fas fa-info-circle text-muted"
                data-title="Date and time when the assignment ends (optional)"></i>
            </label>
            <BInputGroup>
              <BFormInput
                v-model="form.unassigned_date"
                type="date"
                :disabled="isViewMode || submitting"
                v-tt
                data-title="Date when the crew is unassigned from the truck" />
              <BFormInput
                v-model="form.unassigned_time"
                type="time"
                :disabled="isViewMode || submitting"
                v-tt
                data-title="Time when the assignment ends. Uses current time if empty" />
            </BInputGroup>
          </div>
          <div class="d-flex justify-content-center gap-2">
            <button
              type="button"
              class="btn btn-secondary"
              :disabled="submitting"
              @click="goList"
            >
              Cancel
            </button>
            <button
              v-if="!isViewMode"
              type="submit"
              class="btn btn-primary"
              :disabled="submitting"
            >
              <span
                v-if="submitting"
                class="spinner-border spinner-border-sm me-1"
                role="status"
              ></span>
              {{ submitting ? "Saving..." : "Save" }}
            </button>
          </div>
          <p class="small text-muted mt-3 mb-0">
            <span class="text-danger">*</span> Indicates required fields.
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios";
import Swal from "sweetalert2";
import { onMounted, ref, computed, getCurrentInstance } from "vue";
import { useRoute, useRouter } from "vue-router";
import { BFormInput, BInputGroup } from "bootstrap-vue-next";
import vSelect from "vue-select";
import "vue-select/dist/vue-select.css";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === "crew-truck-assignment-view");
const isEditMode = computed(() => !!id && !isViewMode.value);

const submitting = ref(false);
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
    label: t ? `${t.plate_number || ""} - ${t.model || ""}`.trim() : "",
  })),
);

const formTitle = computed(() => {
  if (isViewMode.value) return "View Truck Assignment";
  if (isEditMode.value) return "Edit Truck Assignment";
  return "Add Truck Assignment";
});

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
      trucks: Array.isArray(data.trucks) ? data.trucks : data.trucks ? [data.trucks] : [],
      assigned_date: toDatePart(data.assigned_at),
      assigned_time: toTimePart(data.assigned_at),
      unassigned_date: data.unassigned_at ? toDatePart(data.unassigned_at) : "",
      unassigned_time: data.unassigned_at ? toTimePart(data.unassigned_at) : "",
    };
  } catch (err) {
    console.error("Load error:", err);
    await Swal.fire("Oops!", "Error loading the truck assignment.", "error");
  }
}

function validate() {
  if (!form.value.crew) {
    Swal.fire("Validation", "Assigned crew is required.", "warning");
    return false;
  }
  if (!form.value.trucks?.length) {
    Swal.fire("Validation", "At least one truck is required.", "warning");
    return false;
  }
  if (!form.value.assigned_date || !form.value.assigned_time) {
    Swal.fire("Validation", "Assigned at (date and time) is required.", "warning");
    return false;
  }
  return true;
}

async function handleSubmit() {
  if (!validate()) return;
  submitting.value = true;
  try {
    const assigned_at = toISOString(form.value.assigned_date, form.value.assigned_time);
    let unassigned_at = null;
    if (form.value.unassigned_date) {
      const time = form.value.unassigned_time || toTimePart(new Date());
      unassigned_at = toISOString(form.value.unassigned_date, time);
    }

    const truckIds = (form.value.trucks || []).map((t) =>
      typeof t === "object" && t !== null && "id" in t ? t.id : t,
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
      else if (data.detail) msg = Array.isArray(data.detail) ? data.detail.join(" ") : data.detail;
      else if (data.non_field_errors) msg = data.non_field_errors.join(" ");
      else msg = Object.values(data).flat().join(" ") || msg;
    }
    await Swal.fire("Validation Error", msg, "error");
  } finally {
    submitting.value = false;
  }
}

function goList() {
  router.push({ name: "crew-truck-assignments" });
}

onMounted(async () => {
  await loadOptions();
  await loadData();
});
</script>
