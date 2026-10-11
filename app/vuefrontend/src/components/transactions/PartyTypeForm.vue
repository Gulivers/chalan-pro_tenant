<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" />

    <div class="jr-party-form">
      <p v-if="loading" class="jr-party-form__status" role="status">
        Loading party type…
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
              inputId="party-type-name"
              required
              :error="fieldErrors.name">
              <JRInput
                inputId="party-type-name"
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
              inputId="party-type-description"
              class="jr-form-grid__full">
              <JRTextarea
                inputId="party-type-description"
                v-model="form.description"
                :rows="3"
                placeholder="Optional description..."
                :disabled="isDisabled"
                :ariaDescribedby="describedby" />
            </JRField>

            <JRField label="Active" inputId="party-type-is-active">
              <JRCheckbox
                inputId="party-type-is-active"
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

const id = route.query.id || null;
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
  if (isViewMode.value) return "View Party Type";
  if (isEditMode.value) return "Edit Party Type";
  return "New Party Type";
});

function clearFieldError(key) {
  if (!fieldErrors.value[key]) return;
  const next = { ...fieldErrors.value };
  delete next[key];
  fieldErrors.value = next;
}

function goList() {
  router.push({ name: "party-types" }).catch(() => {
    router.push("/party-types");
  });
}

onMounted(async () => {
  if (isViewMode.value && !id) {
    await Swal.fire("Info", "No record to view.", "info");
    goList();
    return;
  }

  if (id) {
    loading.value = true;
    try {
      const { data } = await axios.get(`/api/party-types/${id}/`);
      form.value = {
        name: data.name || "",
        description: data.description || "",
        is_active: !!data.is_active,
      };
    } catch (error) {
      console.error("Error loading party type:", error);
      await Swal.fire("Oops!", "Error loading the party type.", "error");
      goList();
    } finally {
      loading.value = false;
    }
  }
});

const handleSubmit = async () => {
  if (isViewMode.value) return;

  try {
    submitting.value = true;
    fieldErrors.value = {};

    form.value.name = (form.value.name ?? "").trim();
    form.value.description = (form.value.description ?? "").trim();

    if (!form.value.name) {
      fieldErrors.value = { name: "Name is required." };
      await Swal.fire("Validation", "Name is required.", "warning");
      return;
    }
    if (form.value.name.length > 150) {
      fieldErrors.value = { name: "Name cannot exceed 150 characters." };
      await Swal.fire(
        "Validation",
        "Name cannot exceed 150 characters.",
        "warning"
      );
      return;
    }

    if (isEditMode.value) {
      await axios.put(`/api/party-types/${id}/`, form.value);
    } else {
      await axios.post("/api/party-types/", form.value);
    }

    goList();
  } catch (error) {
    console.error("Error saving party type:", error);
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
      await Swal.fire("Oops!", "Error saving the party type.", "error");
    }
  } finally {
    submitting.value = false;
  }
};
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
