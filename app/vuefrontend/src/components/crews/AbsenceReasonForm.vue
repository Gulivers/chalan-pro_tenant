<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" />

    <div class="jr-absence-reason-form">
      <p v-if="loading" class="jr-absence-reason-form__status" role="status">
        Loading absence reason…
      </p>

      <form
        v-else
        class="jr-absence-reason-form__form"
        @submit.prevent="handleSubmit"
        novalidate>
        <JRSection title="Details">
          <div class="jr-form-grid">
            <JRField
              v-slot="{ describedby, invalid }"
              label="Name"
              inputId="absence-reason-name"
              required
              :error="fieldErrors.name">
              <JRInput
                inputId="absence-reason-name"
                v-model="form.name"
                maxlength="100"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('name')" />
            </JRField>

            <JRField label="Active" inputId="absence-reason-active">
              <JRCheckbox
                v-model="form.is_active"
                inputId="absence-reason-active"
                ariaLabel="Active"
                :disabled="isDisabled" />
            </JRField>

            <JRField
              class="jr-form-grid__full"
              v-slot="{ describedby, invalid }"
              label="Description"
              inputId="absence-reason-description"
              :error="fieldErrors.description">
              <JRTextarea
                inputId="absence-reason-description"
                v-model="form.description"
                :rows="4"
                :disabled="isDisabled"
                :invalid="invalid"
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('description')" />
            </JRField>
          </div>
        </JRSection>

        <div
          class="jr-absence-reason-form__actions jr-absence-reason-form__actions--sticky">
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
import { onMounted, ref, computed, getCurrentInstance } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRInput,
  JRTextarea,
  JRCheckbox,
  JRButton,
} from "@ui";

const ENDPOINT = "/api/absence-reasons/";
const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === "absence-reason-view");
const isEditMode = computed(() => !!id && !isViewMode.value);

const submitting = ref(false);
const loading = ref(false);
const fieldErrors = ref({});
const form = ref({
  name: "",
  description: "",
  is_active: true,
});

const isDisabled = computed(() => isViewMode.value || submitting.value);
const pageTitle = computed(() => {
  if (isViewMode.value) return "View Absence Reason";
  if (isEditMode.value) return "Edit Absence Reason";
  return "Add Absence Reason";
});

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
}

function focusFirstError() {
  if (typeof document === "undefined") return;
  const el = document.querySelector(".jr-field__error");
  el?.scrollIntoView?.({ behavior: "smooth", block: "center" });
}

function goList() {
  router.push({ name: "absence-reasons" });
}

async function loadData() {
  if (!id) return;
  loading.value = true;
  try {
    const { data } = await axios.get(`${ENDPOINT}${id}/`);
    form.value = {
      name: data.name || "",
      description: data.description || "",
      is_active: data.is_active !== false,
    };
  } catch (err) {
    console.error("Load error:", err);
    proxy?.notifyError?.("Error loading the absence reason.");
  } finally {
    loading.value = false;
  }
}

function validate() {
  const name = (form.value.name || "").trim();
  form.value.name = name;
  form.value.description = (form.value.description || "").trim();
  if (!name) {
    fieldErrors.value = { name: "Name is required." };
    proxy?.notifyError?.("Name is required.");
    focusFirstError();
    return false;
  }
  if (name.length > 100) {
    fieldErrors.value = { name: "Name must be at most 100 characters." };
    proxy?.notifyError?.("Name must be at most 100 characters.");
    focusFirstError();
    return false;
  }
  return true;
}

async function handleSubmit() {
  if (!validate()) return;
  submitting.value = true;
  fieldErrors.value = {};
  const payload = {
    name: form.value.name,
    description: form.value.description || "",
    is_active: !!form.value.is_active,
  };
  try {
    if (id) {
      await axios.patch(`${ENDPOINT}${id}/`, payload);
      proxy?.notifyToastSuccess?.("Absence reason updated.");
    } else {
      await axios.post(ENDPOINT, payload);
      proxy?.notifyToastSuccess?.("Absence reason created.");
    }
    router.push({ name: "absence-reasons" });
  } catch (err) {
    console.error("Save error:", err);
    const data = err.response?.data || {};
    const next = {};
    if (data.name?.[0]) next.name = data.name[0];
    if (data.description?.[0]) next.description = data.description[0];
    fieldErrors.value = next;
    const detail =
      data.name?.[0] ||
      data.description?.[0] ||
      data.detail ||
      "Error saving absence reason.";
    proxy?.notifyError?.(detail);
    focusFirstError();
  } finally {
    submitting.value = false;
  }
}

onMounted(loadData);
</script>

<style scoped>
.jr-absence-reason-form__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-absence-reason-form__status {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1rem;
}

.jr-form-grid__full {
  grid-column: 1 / -1;
}

@media (min-width: 768px) {
  .jr-form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.jr-absence-reason-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.jr-absence-reason-form__actions--sticky {
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.25rem;
  margin-top: 0.5rem;
  background: var(--color-jr-page, #f3f4f6);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}
</style>
