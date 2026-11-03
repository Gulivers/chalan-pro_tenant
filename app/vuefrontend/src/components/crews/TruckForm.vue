<template>
  <JRPage>
    <JRPageHeader :title="pageTitle">
      <template v-if="canEditFromView" #actions>
        <JRButton variant="primary" size="sm" @click="goToEdit">
          Edit truck
        </JRButton>
      </template>
    </JRPageHeader>

    <div class="jr-truck-form">
      <p v-if="loading" class="jr-truck-form__status" role="status">
        Loading truck…
      </p>

      <form
        v-else
        class="jr-truck-form__form"
        @submit.prevent="handleSubmit"
        novalidate>
        <JRSection title="Details">
          <div class="jr-form-grid">
            <JRField
              v-slot="{ describedby, invalid }"
              label="Unit Number"
              inputId="truck-unit-number"
              required
              hint="Internal identifier, e.g. TRK-001."
              :error="fieldErrors.unit_number">
              <JRInput
                inputId="truck-unit-number"
                v-model="form.unit_number"
                maxlength="32"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('unit_number')" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Plate Number"
              inputId="truck-plate-number"
              required
              :error="fieldErrors.plate_number">
              <JRInput
                inputId="truck-plate-number"
                v-model="form.plate_number"
                maxlength="20"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('plate_number')" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="VIN"
              inputId="truck-vin"
              required
              hint="17 alphanumeric characters. Saved in uppercase."
              :error="fieldErrors.vin">
              <JRInput
                inputId="truck-vin"
                v-model="form.vin"
                maxlength="17"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="onVinInput" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Make"
              inputId="truck-make"
              required
              :error="fieldErrors.make">
              <JRInput
                inputId="truck-make"
                v-model="form.make"
                maxlength="100"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('make')" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Model"
              inputId="truck-model"
              required
              :error="fieldErrors.model">
              <JRInput
                inputId="truck-model"
                v-model="form.model"
                maxlength="255"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('model')" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Year"
              inputId="truck-year"
              required
              :error="fieldErrors.year">
              <JRInput
                inputId="truck-year"
                v-model="form.year"
                type="number"
                :min="1900"
                :max="2100"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('year')" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Status"
              inputId="truck-fleet-status"
              required
              :error="fieldErrors.fleet_status">
              <JRSelect
                inputId="truck-fleet-status"
                v-model="form.fleet_status"
                :options="fleetStatusOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Select status"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('fleet_status')" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Registration Expiration"
              inputId="truck-reg-exp"
              required
              :error="fieldErrors.registration_expiration">
              <JRDatePicker
                inputId="truck-reg-exp"
                :modelValue="isoToDate(form.registration_expiration)"
                :disabled="isDisabled"
                :invalid="invalid"
                placeholder="Select date"
                @update:modelValue="
                  onDateField('registration_expiration', $event)
                " />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              label="Insurance Expiration"
              inputId="truck-ins-exp"
              required
              :error="fieldErrors.insurance_expiration">
              <JRDatePicker
                inputId="truck-ins-exp"
                :modelValue="isoToDate(form.insurance_expiration)"
                :disabled="isDisabled"
                :invalid="invalid"
                placeholder="Select date"
                @update:modelValue="
                  onDateField('insurance_expiration', $event)
                " />
            </JRField>

            <JRField
              label="Current Mileage"
              inputId="truck-current-mileage"
              hint="Latest reading by date from assignments (start or return).">
              <JRInput
                inputId="truck-current-mileage"
                :modelValue="currentMileageLabel"
                disabled
                ariaLabel="Current mileage" />
            </JRField>

            <JRField label="Active" inputId="truck-status">
              <JRCheckbox
                inputId="truck-status"
                v-model="form.status"
                ariaLabel="Active"
                :disabled="isDisabled" />
            </JRField>
          </div>
        </JRSection>

        <div class="jr-truck-form__actions jr-truck-form__actions--sticky">
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
  JRCheckbox,
  JRButton,
  JRDatePicker,
} from "@ui";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === "crew-truck-view");
const isEditMode = computed(() => !!id && !isViewMode.value);

const fleetStatusOptions = [
  { value: "available", label: "Available" },
  { value: "maintenance", label: "Maintenance" },
  { value: "out_of_service", label: "Out of Service" },
  { value: "sold", label: "Sold" },
];

const submitting = ref(false);
const loading = ref(false);
const fieldErrors = ref({});
const currentMileageDisplay = ref("Not recorded");
const form = ref({
  unit_number: "",
  plate_number: "",
  vin: "",
  make: "",
  model: "",
  year: new Date().getFullYear(),
  fleet_status: "available",
  registration_expiration: "",
  insurance_expiration: "",
  status: true,
});

const isDisabled = computed(() => isViewMode.value || submitting.value);
const pageTitle = computed(() => {
  if (isViewMode.value) return "View Truck";
  if (isEditMode.value) return "Edit Truck";
  return "Add Truck";
});
const canEditFromView = computed(
  () =>
    isViewMode.value &&
    !!id &&
    !!proxy?.hasPermission?.("crewsapp.change_truck")
);
const currentMileageLabel = computed(() => {
  const v = currentMileageDisplay.value;
  if (v === "Not recorded" || v === null || v === undefined || v === "") {
    return "Not recorded";
  }
  return `${v} mi`;
});

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
}

function onVinInput(value) {
  form.value.vin = (value || "").toString().toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, 17);
  clearFieldError("vin");
}

function isoToDate(value) {
  if (!value) return null;
  if (value instanceof Date) return value;
  const s = String(value).slice(0, 10);
  const [y, m, d] = s.split("-").map(Number);
  if (!y || !m || !d) return null;
  return new Date(y, m - 1, d);
}

function dateToIso(value) {
  if (!value) return "";
  const dt = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(dt.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}`;
}

function onDateField(key, value) {
  form.value[key] = dateToIso(value);
  clearFieldError(key);
}

function goList() {
  router.push({ name: "crew-trucks" });
}

function goToEdit() {
  if (!id) return;
  router.push({ name: "crew-truck-edit", params: { id } });
}

async function loadData() {
  if (!id) return;
  loading.value = true;
  try {
    const { data } = await axios.get(`/api/trucks/${id}/`);
    form.value = {
      unit_number: data.unit_number || "",
      plate_number: data.plate_number || "",
      vin: data.vin || "",
      make: data.make || "",
      model: data.model || "",
      year: data.year || new Date().getFullYear(),
      fleet_status: data.fleet_status || "available",
      registration_expiration: data.registration_expiration || "",
      insurance_expiration: data.insurance_expiration || "",
      status: !!data.status,
    };
    currentMileageDisplay.value =
      data.current_mileage_display ??
      (data.current_mileage == null ? "Not recorded" : data.current_mileage);
  } catch (err) {
    console.error("Load error:", err);
    await Swal.fire("Oops!", "Error loading the truck.", "error");
  } finally {
    loading.value = false;
  }
}

function validate() {
  const next = {};
  const unit = (form.value.unit_number || "").trim();
  const plate = (form.value.plate_number || "").trim();
  const vin = (form.value.vin || "").trim().toUpperCase();
  const make = (form.value.make || "").trim();
  const model = (form.value.model || "").trim();
  form.value.unit_number = unit;
  form.value.plate_number = plate;
  form.value.vin = vin;
  form.value.make = make;
  form.value.model = model;

  if (!unit) next.unit_number = "Unit number is required.";
  if (!plate) next.plate_number = "Plate number is required.";
  if (!vin || vin.length !== 17 || !/^[A-Z0-9]{17}$/.test(vin)) {
    next.vin = "VIN must be exactly 17 alphanumeric characters.";
  }
  if (!make) next.make = "Make is required.";
  if (!model) next.model = "Model is required.";
  const y = Number(form.value.year);
  if (!y || y < 1900 || y > 2100) {
    next.year = "Year must be between 1900 and 2100.";
  }
  if (!form.value.fleet_status) next.fleet_status = "Status is required.";
  if (!form.value.registration_expiration) {
    next.registration_expiration = "Registration expiration is required.";
  }
  if (!form.value.insurance_expiration) {
    next.insurance_expiration = "Insurance expiration is required.";
  }
  fieldErrors.value = next;
  if (Object.keys(next).length) {
    Swal.fire(
      "Validation",
      Object.values(next)[0] || "Please check the form.",
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
    const payload = {
      unit_number: form.value.unit_number.trim(),
      plate_number: form.value.plate_number.trim(),
      vin: form.value.vin.trim().toUpperCase(),
      make: form.value.make.trim(),
      model: form.value.model.trim(),
      year: Number(form.value.year),
      fleet_status: form.value.fleet_status,
      registration_expiration: form.value.registration_expiration,
      insurance_expiration: form.value.insurance_expiration,
      status: form.value.status,
    };
    if (id) {
      await axios.patch(`/api/trucks/${id}/`, payload);
      proxy?.notifyToastSuccess?.("Truck updated.");
      router.push({ name: "crew-trucks" });
    } else {
      const { data } = await axios.post("/api/trucks/", payload);
      proxy?.notifyToastSuccess?.("Truck created.");

      const result = await Swal.fire({
        title: "Create mobile warehouse for this truck?",
        text: "Do you want to create a mobile warehouse to track equipment assets and serial numbers for this truck?",
        icon: "question",
        showCancelButton: true,
        confirmButtonText: "Yes",
        cancelButtonText: "No",
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#6c757d",
      });

      if (result.isConfirmed) {
        try {
          const res = await axios.post(
            `/api/trucks/${data.id}/create-mobile-warehouse/`
          );
          const msg =
            res.data?.message ||
            (res.status === 201
              ? "Mobile warehouse created."
              : "Mobile warehouse already exists.");
          proxy?.notifyToastSuccess?.(msg);
        } catch (whErr) {
          console.error("Create mobile warehouse error:", whErr);
          const detail = whErr.response?.data?.detail;
          const msg =
            typeof detail === "string"
              ? detail
              : Object.values(detail || {}).flat().join(" ") ||
                "Error creating mobile warehouse.";
          Swal.fire("Error", msg, "error");
        }
      }
      router.push({ name: "crew-trucks" });
    }
  } catch (err) {
    console.error("Save error:", err);
    const data = err.response?.data;
    if (data && typeof data === "object") {
      const next = {};
      Object.entries(data).forEach(([field, msgs]) => {
        if (field === "detail" || field === "non_field_errors") return;
        next[field] = Array.isArray(msgs) ? msgs.join(", ") : String(msgs);
      });
      fieldErrors.value = next;
    }
    const msg = data
      ? Object.values(data).flat().join(" ") || "Error saving truck."
      : "Error saving truck.";
    Swal.fire("Error", msg, "error");
  } finally {
    submitting.value = false;
  }
}

onMounted(loadData);
</script>

<style scoped>
.jr-truck-form__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-truck-form__status {
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
}

.jr-truck-form :deep(.jr-checkbox) {
  column-gap: 0.85rem;
  align-items: center;
}

.jr-truck-form :deep(.jr-checkbox__label) {
  margin-inline-start: 0.15rem;
}

.jr-truck-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.jr-truck-form__actions--sticky {
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.25rem;
  margin-top: 0.5rem;
  background: var(--color-jr-page, #f3f4f6);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}
</style>
