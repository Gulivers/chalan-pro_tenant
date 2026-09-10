<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" />

    <div class="jr-party-form">
      <p v-if="loading" class="jr-party-form__status" role="status">
        Loading party category…
      </p>

      <form
        v-else
        class="jr-party-form__form"
        @submit.prevent="handleSubmit"
        novalidate>
        <JRSection title="Details">
          <div class="jr-form-grid">
            <JRField
              v-slot="{ describedby, invalid }"
              label="Name"
              inputId="party-category-name"
              required
              :error="fieldErrors.name">
              <JRInput
                inputId="party-category-name"
                v-model="form.name"
                maxlength="150"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('name')" />
            </JRField>

            <JRField
              v-slot="{ describedby }"
              label="Description"
              inputId="party-category-description"
              class="jr-form-grid__full">
              <JRTextarea
                inputId="party-category-description"
                v-model="form.description"
                :rows="3"
                placeholder="Optional description..."
                :disabled="isDisabled"
                :ariaDescribedby="describedby" />
            </JRField>

            <JRField label="Active" inputId="party-category-is-active">
              <JRCheckbox
                inputId="party-category-is-active"
                v-model="form.is_active"
                ariaLabel="Active"
                :disabled="isDisabled" />
            </JRField>
          </div>
        </JRSection>

        <div class="jr-party-form__actions">
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
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import Swal from "sweetalert2";
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

const route = useRoute();
const router = useRouter();

const id = route.query.id;
const isViewMode = computed(() => route.query.mode === "view");
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
  if (isViewMode.value) return "View Party Category";
  if (isEditMode.value) return "Edit Party Category";
  return "New Party Category";
});

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
}

function goList() {
  router.push({ name: "party-categories" });
}

async function loadData() {
  if (!id) return;
  loading.value = true;
  try {
    const { data } = await axios.get(`/api/party-categories/${id}/`);
    form.value = {
      name: data.name || "",
      description: data.description || "",
      is_active: !!data.is_active,
    };
  } catch (error) {
    console.error("Load error:", error);
    await Swal.fire("Oops!", "Error loading the category.", "error");
  } finally {
    loading.value = false;
  }
}

function validateLocal() {
  const name = (form.value.name || "").trim();
  form.value.name = name;
  form.value.description = (form.value.description || "").trim();
  if (!name) {
    fieldErrors.value = { name: "Name is required." };
    Swal.fire("Validation", "Name is required.", "warning");
    return false;
  }
  if (name.length > 150) {
    fieldErrors.value = { name: "Name must be at most 150 characters." };
    Swal.fire("Validation", "Name must be at most 150 characters.", "warning");
    return false;
  }
  return true;
}

async function handleSubmit() {
  if (!validateLocal()) return;

  submitting.value = true;
  fieldErrors.value = {};
  try {
    if (isEditMode.value) {
      await axios.put(`/api/party-categories/${id}/`, form.value);
    } else {
      await axios.post("/api/party-categories/", form.value);
    }
    goList();
  } catch (error) {
    console.error("Error saving party category:", error);
    const { status, data } = error?.response || {};

    if (status === 400 && data) {
      const next = {};
      Object.entries(data).forEach(([field, msgs]) => {
        if (field === "detail" || field === "non_field_errors") return;
        next[field] = Array.isArray(msgs) ? msgs.join(", ") : String(msgs);
      });
      fieldErrors.value = next;
      const messages = Object.entries(data)
        .map(
          ([field, msgs]) =>
            `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`
        )
        .join("\n");
      await Swal.fire(
        "Oops!",
        messages || "There were validation errors.",
        "error"
      );
    } else if (status === 403) {
      await Swal.fire(
        "Forbidden",
        "You do not have permission for this action.",
        "error"
      );
    } else {
      await Swal.fire("Oops!", "Error saving the party category.", "error");
    }
  } finally {
    submitting.value = false;
  }
}

onMounted(loadData);
</script>

<style scoped>
.jr-party-form__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-party-form__status {
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

.jr-party-form :deep(.jr-checkbox) {
  column-gap: 0.85rem;
  align-items: center;
}

.jr-party-form :deep(.jr-checkbox__label) {
  margin-inline-start: 0.15rem;
}

.jr-party-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}
</style>
