<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" />

    <div class="jr-warehouse-form">
      <p v-if="loadError" class="jr-form-banner" role="alert">{{ loadError }}</p>
      <p v-else-if="loading" class="jr-warehouse-form__status" role="status">
        Loading warehouse…
      </p>

      <form
        v-else
        class="jr-warehouse-form__form"
        @submit.prevent="saveWarehouse"
        novalidate>
        <p v-if="formBanner" class="jr-form-banner" role="alert">
          {{ formBanner }}
        </p>

        <div class="jr-form-grid">
          <JRField
            v-slot="{ describedby, invalid }"
            label="Name"
            inputId="warehouse-name"
            required
            :error="fieldErrors.name">
            <JRInput
              inputId="warehouse-name"
              v-model="warehouse.name"
              placeholder="Warehouse name"
              :disabled="isDisabled"
              :invalid="invalid"
              required
              :ariaDescribedby="describedby"
              @update:modelValue="clearFieldError('name')" />
          </JRField>

          <JRField
            v-slot="{ describedby, invalid }"
            label="Location"
            inputId="warehouse-location"
            :error="fieldErrors.location">
            <JRInput
              inputId="warehouse-location"
              v-model="warehouse.location"
              placeholder="Warehouse location"
              :disabled="isDisabled"
              :invalid="invalid"
              :ariaDescribedby="describedby"
              @update:modelValue="clearFieldError('location')" />
          </JRField>

          <JRField label="Active" inputId="warehouse-is-active">
            <JRCheckbox
              inputId="warehouse-is-active"
              v-model="warehouse.is_active"
              ariaLabel="Active"
              :disabled="isDisabled" />
          </JRField>

          <JRField
            label="Default warehouse"
            inputId="warehouse-is-default"
            hint="Only one warehouse can be default"
            :error="fieldErrors.is_default">
            <JRCheckbox
              inputId="warehouse-is-default"
              v-model="warehouse.is_default"
              ariaLabel="Default warehouse"
              :disabled="isDisabled"
              @update:modelValue="onDefaultChange" />
          </JRField>
        </div>

        <div class="jr-warehouse-form__actions">
          <template v-if="!isViewMode">
            <JRButton
              type="submit"
              variant="primary"
              :disabled="isDisabled">
              {{
                submitting
                  ? isEditMode
                    ? "Updating..."
                    : "Saving..."
                  : isEditMode
                    ? "Update"
                    : "Save"
              }}
            </JRButton>
            <JRButton
              type="button"
              variant="secondary"
              :disabled="submitting"
              @click="goBack">
              Cancel
            </JRButton>
          </template>
          <JRButton
            v-else
            type="button"
            variant="secondary"
            :disabled="submitting"
            @click="goBack">
            Back
          </JRButton>
        </div>
      </form>
    </div>
  </JRPage>
</template>

<script>
import axios from "axios";
import { JRPage, JRPageHeader, JRField, JRInput, JRCheckbox, JRButton } from "@ui";

export default {
  name: "WarehouseForm",
  components: {
    JRPage,
    JRPageHeader,
    JRField,
    JRInput,
    JRCheckbox,
    JRButton,
  },
  data() {
    return {
      warehouse: {
        name: "",
        location: "",
        is_active: true,
        is_default: false,
      },
      submitting: false,
      loading: false,
      loadError: "",
      formBanner: "",
      fieldErrors: {},
    };
  },
  computed: {
    id() {
      return this.$route.params.id;
    },
    isViewMode() {
      return (
        this.$route.name === "warehouse-view" || this.$route.query.mode === "view"
      );
    },
    isEditMode() {
      return !!this.id && !this.isViewMode;
    },
    isDisabled() {
      return this.isViewMode || this.submitting;
    },
    pageTitle() {
      if (this.isViewMode) return "View Warehouse";
      if (this.isEditMode) return "Edit Warehouse";
      return "New Warehouse";
    },
  },
  mounted() {
    if (this.id) this.loadWarehouse();
  },
  methods: {
    clearFieldError(key) {
      if (!this.fieldErrors[key]) return;
      const next = { ...this.fieldErrors };
      delete next[key];
      this.fieldErrors = next;
      if (this.formBanner) this.formBanner = "";
    },

    applyServerErrors(data) {
      const next = {};
      if (data && typeof data === "object") {
        Object.entries(data).forEach(([field, msgs]) => {
          if (field === "detail" || field === "non_field_errors") return;
          const text = Array.isArray(msgs) ? msgs.join(", ") : String(msgs);
          if (text) next[field] = text;
        });
      }
      this.fieldErrors = next;
      const detail =
        (data && (data.detail || data.non_field_errors)) ||
        Object.values(next).join(" ");
      this.formBanner =
        (Array.isArray(detail) ? detail.join(", ") : detail) ||
        "There were validation errors.";
    },

    async loadWarehouse() {
      this.loading = true;
      this.loadError = "";
      try {
        const { data } = await axios.get(`/api/warehouses/${this.id}/`);
        this.warehouse = {
          name: data.name ?? "",
          location: data.location ?? "",
          is_active: !!data.is_active,
          is_default: !!data.is_default,
        };
      } catch (error) {
        console.error("Error fetching warehouse:", error);
        this.loadError = "Error loading the warehouse.";
      } finally {
        this.loading = false;
      }
    },

    async onDefaultChange(value) {
      this.clearFieldError("is_default");
      if (!value) return;
      try {
        await axios.patch("/api/warehouses/clear-default/");
      } catch (error) {
        console.error("Error clearing default warehouses:", error);
        this.warehouse.is_default = false;
        this.formBanner = "Could not update default warehouse status.";
      }
    },

    async saveWarehouse() {
      if (this.isViewMode) return;

      this.formBanner = "";
      this.fieldErrors = {};

      if (!this.warehouse.name?.trim()) {
        this.fieldErrors = { name: "Name is required." };
        this.formBanner = "Name is required.";
        return;
      }

      this.submitting = true;
      const url = this.id ? `/api/warehouses/${this.id}/` : "/api/warehouses/";
      const method = this.id ? "put" : "post";

      try {
        if (this.warehouse.is_default) {
          await axios.patch("/api/warehouses/clear-default/");
        }

        await axios[method](url, this.warehouse);
        this.$router.push("/warehouses");
      } catch (error) {
        console.error("Error saving warehouse:", error);
        const { status, data } = error?.response || {};
        if (status === 400 && data) {
          this.applyServerErrors(data);
        } else if (status === 403) {
          this.formBanner = "You do not have permission for this action.";
        } else {
          this.formBanner = "Error saving the warehouse.";
        }
      } finally {
        this.submitting = false;
      }
    },

    goBack() {
      if (this.$router && this.$route.name) {
        this.$router.back();
      } else {
        this.$router.push("/warehouses");
      }
    },
  },
};
</script>

<style scoped>
.jr-warehouse-form__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-warehouse-form__status {
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

@media (min-width: 1024px) {
  .jr-form-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.jr-warehouse-form :deep(.jr-checkbox) {
  column-gap: 0.85rem;
  align-items: center;
}

.jr-warehouse-form :deep(.jr-checkbox__label) {
  margin-inline-start: 0.15rem;
}

.jr-warehouse-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.jr-form-banner {
  margin: 0;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
  background: var(--color-jr-danger-subtle);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
}
</style>
