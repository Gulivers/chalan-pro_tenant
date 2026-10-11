<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" />

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
  JRCheckbox,
  JRButton,
} from "@ui";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === "crew-truck-view");
const isEditMode = computed(() => !!id && !isViewMode.value);

const submitting = ref(false);
const loading = ref(false);
const fieldErrors = ref({});
const form = ref({
  plate_number: "",
  model: "",
  year: new Date().getFullYear(),
  status: true,
});

const isDisabled = computed(() => isViewMode.value || submitting.value);
const pageTitle = computed(() => {
  if (isViewMode.value) return "View Truck";
  if (isEditMode.value) return "Edit Truck";
  return "Add Truck";
});

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
}

function goList() {
  router.push({ name: "crew-trucks" });
}

async function loadData() {
  if (!id) return;
  loading.value = true;
  try {
    const { data } = await axios.get(`/api/trucks/${id}/`);
    form.value = {
      plate_number: data.plate_number || "",
      model: data.model || "",
      year: data.year || new Date().getFullYear(),
      status: !!data.status,
    };
  } catch (err) {
    console.error("Load error:", err);
    await Swal.fire("Oops!", "Error loading the truck.", "error");
  } finally {
    loading.value = false;
  }
}

function validate() {
  const plate = (form.value.plate_number || "").trim();
  const model = (form.value.model || "").trim();
  form.value.plate_number = plate;
  form.value.model = model;
  if (!plate) {
    fieldErrors.value = { plate_number: "Plate number is required." };
    Swal.fire("Validation", "Plate number is required.", "warning");
    return false;
  }
  if (!model) {
    fieldErrors.value = { model: "Model is required." };
    Swal.fire("Validation", "Model is required.", "warning");
    return false;
  }
  const y = form.value.year;
  if (!y || y < 1900 || y > 2100) {
    fieldErrors.value = { year: "Year must be between 1900 and 2100." };
    Swal.fire("Validation", "Year must be between 1900 and 2100.", "warning");
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
      plate_number: form.value.plate_number.trim(),
      model: form.value.model.trim(),
      year: form.value.year,
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
