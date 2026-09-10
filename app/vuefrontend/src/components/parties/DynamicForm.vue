<template>
  <component :is="pageWrapper" v-bind="pageWrapperProps">
    <JRPageHeader v-if="usePageChrome" :title="pageHeading" />

    <div :class="panelClass">
      <form
        v-if="Object.keys(internalSchema).length"
        class="jr-dynamic-form__form"
        @submit.prevent="handleSubmit"
        novalidate>
        <component
          :is="fieldsWrapper"
          v-bind="fieldsWrapperProps">
          <div class="jr-form-grid">
            <template v-for="(config, key) in internalSchema" :key="key">
              <JRField
                v-if="config.type !== 'boolean'"
                v-slot="{ describedby, invalid }"
                :label="config.label"
                :required="!!config.required"
                :inputId="`dyn-${key}`"
                :error="validationErrors[key]">
                <JRInput
                  v-if="config.type === 'string' || config.type === 'text'"
                  :inputId="`dyn-${key}`"
                  v-model="form[key]"
                  :placeholder="`Enter ${config.label}...`"
                  :disabled="isDisabled"
                  :invalid="invalid"
                  :required="!!config.required"
                  :ariaDescribedby="describedby" />

                <JRTextarea
                  v-else-if="
                    config.type === 'textarea' || config.widget === 'textarea'
                  "
                  :inputId="`dyn-${key}`"
                  v-model="form[key]"
                  :rows="3"
                  :placeholder="`Enter ${config.label}...`"
                  :disabled="isDisabled"
                  :invalid="invalid"
                  :ariaDescribedby="describedby" />

                <JRSelect
                  v-else-if="config.type === 'select'"
                  :inputId="`dyn-${key}`"
                  v-model="form[key]"
                  :options="optionsMap[key] || []"
                  optionLabel="label"
                  optionValue="value"
                  :disabled="isDisabled"
                  :multiple="config.multiple || false"
                  :placeholder="`Select ${config.label}...`"
                  :showClear="true"
                  :invalid="invalid"
                  :required="!!config.required"
                  :ariaDescribedby="describedby" />
              </JRField>

              <JRField
                v-else-if="config.type === 'boolean'"
                :label="config.label"
                :inputId="key">
                <JRCheckbox
                  :inputId="key"
                  v-model="form[key]"
                  :ariaLabel="config.label"
                  :disabled="isDisabled" />
              </JRField>
            </template>
          </div>
        </component>

        <div
          :class="[
            'jr-dynamic-form__actions',
            { 'jr-dynamic-form__actions--sticky': usePageChrome },
          ]">
          <template v-if="!isViewMode">
            <JRButton type="submit" variant="primary" :disabled="isDisabled">
              {{ submitting ? "Saving..." : "Save" }}
            </JRButton>
            <JRButton
              type="button"
              variant="secondary"
              :disabled="submitting"
              @click="cancelForm">
              Cancel
            </JRButton>
          </template>
          <JRButton
            v-else
            type="button"
            variant="secondary"
            :disabled="submitting"
            @click="cancelForm">
            Back
          </JRButton>
        </div>
      </form>

      <div v-else class="jr-dynamic-form__loading" role="status">
        <p>Loading schema and checking for fields…</p>
      </div>
    </div>
  </component>
</template>

<script>
import axios from "axios";
import selectMixin from "@/helpers/useSelectOptions";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRInput,
  JRTextarea,
  JRCheckbox,
  JRSelect,
  JRButton,
} from "@ui";

export default {
  name: "DynamicForm",
  components: {
    JRPage,
    JRPageHeader,
    JRSection,
    JRField,
    JRInput,
    JRTextarea,
    JRCheckbox,
    JRSelect,
    JRButton,
  },
  mixins: [selectMixin],
  props: {
    schema: Object,
    schemaEndpoint: String,
    apiEndpoint: { type: String, required: true },
    objectId: { type: [String, Number], default: null },
    formTitle: { type: String, default: "Form" },
    readOnly: { type: Boolean, default: false },
    redirectAfterSave: { type: String, default: null },
    isModal: { type: Boolean, default: false },
  },
  emits: ["saved", "cancel"],
  data() {
    return {
      internalSchema: {},
      form: {},
      fields: [],
      submitting: false,
      validationErrors: {},
    };
  },
  computed: {
    usePageChrome() {
      return !this.isModal;
    },
    pageWrapper() {
      return this.usePageChrome ? "JRPage" : "div";
    },
    pageWrapperProps() {
      return this.usePageChrome ? {} : { class: "jr-embedded-form" };
    },
    panelClass() {
      return this.usePageChrome
        ? "jr-dynamic-form"
        : "jr-embedded-form__panel jr-dynamic-form";
    },
    fieldsWrapper() {
      return this.usePageChrome ? "JRSection" : "div";
    },
    fieldsWrapperProps() {
      return this.usePageChrome ? { title: "Details" } : {};
    },
    isViewMode() {
      if (this.isModal) return this.readOnly;
      return this.readOnly || this.$route?.query?.mode === "view";
    },
    isEditMode() {
      return !!this.objectId && !this.isViewMode;
    },
    isDisabled() {
      return this.isViewMode || this.submitting;
    },
    cleanFormTitle() {
      return this.formTitle
        .replace(/^Create\s+/i, "")
        .replace(/^Edit\s+/i, "")
        .replace(/^View\s+/i, "")
        .trim();
    },
    pageHeading() {
      return this.formTitle || this.cleanFormTitle;
    },
  },
  watch: {
    objectId: {
      immediate: true,
      async handler() {
        if (this.internalSchema && Object.keys(this.internalSchema).length) {
          await this.loadRecord();
        }
      },
    },
  },
  async created() {
    try {
      if (this.schema && Object.keys(this.schema).length) {
        this.internalSchema = this.schema;
      } else if (this.schemaEndpoint) {
        const response = await axios.get(this.schemaEndpoint);
        this.internalSchema = response.data || {};
      }

      this.fields = Object.keys(this.internalSchema);

      await this.loadOptionsForSchema(this.internalSchema);
      await this.loadRecord();
    } catch (err) {
      console.error("❌ Error initializing schema:", err);
      this.notifyToastError?.("Error initializing the form schema.");
    }
  },
  methods: {
    _emptySelectDefault(config) {
      return config?.multiple ? [] : "";
    },

    _normalizeSelectValue(value) {
      if (Array.isArray(value)) {
        return value.map((item) =>
          item && typeof item === "object" ? item.id ?? item.value ?? item : item
        );
      }
      if (value && typeof value === "object") {
        return value.id ?? value.value ?? "";
      }
      return value;
    },

    async loadRecord() {
      if (!this.internalSchema || !Object.keys(this.internalSchema).length)
        return;
      try {
        if (this.objectId) {
          const res = await axios.get(`${this.apiEndpoint}${this.objectId}/`);
          this.form = res.data;
        } else {
          this.form = Object.fromEntries(
            this.fields.map((f) => {
              const cfg = this.internalSchema[f] || {};
              const type = cfg.type;
              const def = cfg.default;
              if (def !== undefined) return [f, def];
              if (type === "boolean") return [f, false];
              if (type === "select") return [f, this._emptySelectDefault(cfg)];
              return [f, ""];
            })
          );
        }
      } catch (err) {
        console.error("❌ Error loading record:", err);
        this.notifyToastError?.("Error loading the record.");
      }
    },

    _buildCleanPayload() {
      const cleaned = { ...this.form };

      for (const key of this.fields) {
        const cfg = this.internalSchema[key] || {};

        if (
          ["string", "text"].includes(cfg.type) ||
          cfg.type === "textarea" ||
          cfg.widget === "textarea"
        ) {
          cleaned[key] = (cleaned[key] ?? "").toString().trim();
        }

        if (cfg.type === "select" && cfg.optionsEndpoint) {
          cleaned[key] = this._normalizeSelectValue(cleaned[key]);
        }
      }
      return cleaned;
    },

    validateForm() {
      this.validationErrors = {};
      let hasErrors = false;

      for (const [key, config] of Object.entries(this.internalSchema)) {
        const value = this.form[key];
        const label = config.label || key;

        const isEmpty =
          value === null ||
          value === undefined ||
          value === "" ||
          (typeof value === "string" && value.trim() === "") ||
          (Array.isArray(value) && value.length === 0);

        if (config.required && isEmpty) {
          this.validationErrors[key] = `${label} is required.`;
          hasErrors = true;
          continue;
        }

        if (value && typeof value === "string") {
          const trimmedValue = value.trim();

          if (
            key === "name" &&
            trimmedValue.length > 0 &&
            trimmedValue.length < 2
          ) {
            this.validationErrors[key] = "Must be at least 2 characters.";
            hasErrors = true;
          }

          if (key === "email" && trimmedValue.length > 0) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(trimmedValue)) {
              this.validationErrors[key] = "Enter a valid email address.";
              hasErrors = true;
            }
          }

          if (key === "rfc" && trimmedValue.length > 50) {
            this.validationErrors[key] = "Must be 50 characters or fewer.";
            hasErrors = true;
          }
        }
      }

      return !hasErrors;
    },

    async validateUniqueness() {
      const name = this.form.name?.trim();
      const rfc = this.form.rfc?.trim();

      if (!name && !rfc) return true;

      try {
        const params = new URLSearchParams();
        if (name) params.append("name", name);
        if (rfc) params.append("rfc", rfc);
        if (this.objectId) params.append("exclude_id", this.objectId);

        const response = await axios.get(
          `${this.apiEndpoint}?${params.toString()}`
        );
        const existingBuilders = Array.isArray(response.data)
          ? response.data
          : response.data.results || [];

        if (existingBuilders.length > 0) {
          const duplicateBuilder = existingBuilders[0];
          const errors = [];

          if (
            name &&
            duplicateBuilder.name?.toLowerCase() === name.toLowerCase()
          ) {
            errors.push(`Name "${name}" already exists.`);
          }

          if (rfc && duplicateBuilder.rfc === rfc) {
            errors.push(`RFC "${rfc}" already exists.`);
          }

          if (errors.length > 0) {
            this.notifyToastError?.(errors.join(" "));
            return false;
          }
        }

        return true;
      } catch (error) {
        console.error("Error validating uniqueness:", error);
        return true;
      }
    },

    async handleSubmit() {
      if (this.isViewMode) return;

      if (!this.validateForm()) {
        return;
      }

      if (!(await this.validateUniqueness())) {
        return;
      }

      this.submitting = true;

      const payload = this._buildCleanPayload();
      const url = this.objectId
        ? `${this.apiEndpoint}${this.objectId}/`
        : this.apiEndpoint;
      const method = this.objectId ? "put" : "post";

      try {
        const response = await axios[method](url, payload);

        this.notifyToastSuccess?.(
          this.objectId ? "Record updated." : "Record created."
        );

        if (this.redirectAfterSave) {
          if (this.redirectAfterSave.startsWith("/")) {
            this.$router.push(this.redirectAfterSave);
          } else {
            this.$router.push({ name: this.redirectAfterSave });
          }
        } else {
          this.$emit("saved", response.data);
        }
      } catch (error) {
        console.error("❌ Save error:", error);
        const { status, data } = error?.response || {};

        if (status === 400 && data) {
          const messages = Object.entries(data)
            .map(([field, msgs]) => {
              const label = this.internalSchema[field]?.label || field;
              const message = Array.isArray(msgs) ? msgs.join(", ") : msgs;
              return `${label}: ${message}`;
            })
            .join(" ");
          this.notifyToastError?.(messages || "Validation errors.");
        } else if (status === 403) {
          this.notifyToastError?.(
            "You do not have permission for this action."
          );
        } else {
          const errorMessage =
            data?.detail || data?.message || "Error saving the record.";
          this.notifyToastError?.(errorMessage);
        }
      } finally {
        this.submitting = false;
      }
    },

    cancelForm() {
      if (this.isModal) {
        this.$emit("cancel");
      } else {
        if (this.$router && this.$route.name) {
          this.$router.back();
        } else {
          this.$emit("cancel");
        }
      }
    },
  },
};
</script>

<style scoped>
.jr-dynamic-form__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

.jr-dynamic-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.jr-dynamic-form__actions--sticky {
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.25rem;
  margin-top: 0.5rem;
  background: var(--color-jr-page, #f3f4f6);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-dynamic-form__loading {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-dynamic-form :deep(.jr-checkbox) {
  column-gap: 0.85rem;
  align-items: center;
}
</style>
