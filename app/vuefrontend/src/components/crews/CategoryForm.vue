<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" />

    <div class="jr-category-form">
      <p v-if="loading" class="jr-category-form__status" role="status">
        Loading crew category…
      </p>

      <form
        v-else
        class="jr-category-form__form"
        @submit.prevent="handleSubmit"
        novalidate>
        <JRSection title="Details">
          <div class="jr-form-grid">
            <JRField
              v-slot="{ describedby, invalid }"
              label="Name"
              inputId="crew-category-name"
              required
              :error="fieldErrors.name">
              <JRInput
                inputId="crew-category-name"
                v-model="form.name"
                maxlength="100"
                :disabled="isDisabled"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('name')" />
            </JRField>
          </div>
        </JRSection>

        <div
          class="jr-category-form__actions jr-category-form__actions--sticky">
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
  JRButton,
} from "@ui";

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === "crew-category-view");
const isEditMode = computed(() => !!id && !isViewMode.value);

const submitting = ref(false);
const loading = ref(false);
const fieldErrors = ref({});
const form = ref({ name: "" });

const isDisabled = computed(() => isViewMode.value || submitting.value);
const pageTitle = computed(() => {
  if (isViewMode.value) return "View Category";
  if (isEditMode.value) return "Edit Category";
  return "Add Category";
});

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
}

function goList() {
  router.push({ name: "crew-categories" });
}

async function loadData() {
  if (!id) return;
  loading.value = true;
  try {
    const { data } = await axios.get(`/api/categories/${id}/`);
    form.value = { name: data.name || "" };
  } catch (err) {
    console.error("Load error:", err);
    await Swal.fire("Oops!", "Error loading the category.", "error");
  } finally {
    loading.value = false;
  }
}

function validate() {
  const name = (form.value.name || "").trim();
  form.value.name = name;
  if (!name) {
    fieldErrors.value = { name: "Name is required." };
    Swal.fire("Validation", "Name is required.", "warning");
    return false;
  }
  if (name.length > 100) {
    fieldErrors.value = { name: "Name must be at most 100 characters." };
    Swal.fire("Validation", "Name must be at most 100 characters.", "warning");
    return false;
  }
  return true;
}

async function handleSubmit() {
  if (!validate()) return;
  submitting.value = true;
  fieldErrors.value = {};
  try {
    if (id) {
      await axios.patch(`/api/categories/${id}/`, form.value);
      proxy?.notifyToastSuccess?.("Category updated.");
    } else {
      await axios.post("/api/categories/", form.value);
      proxy?.notifyToastSuccess?.("Category created.");
    }
    router.push({ name: "crew-categories" });
  } catch (err) {
    console.error("Save error:", err);
    const nameErr = err.response?.data?.name?.[0];
    if (nameErr) fieldErrors.value = { name: nameErr };
    Swal.fire("Error", nameErr || "Error saving category.", "error");
  } finally {
    submitting.value = false;
  }
}

onMounted(loadData);
</script>

<style scoped>
.jr-category-form__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-category-form__status {
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

.jr-category-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.jr-category-form__actions--sticky {
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.25rem;
  margin-top: 0.5rem;
  background: var(--color-jr-page, #f3f4f6);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}
</style>
