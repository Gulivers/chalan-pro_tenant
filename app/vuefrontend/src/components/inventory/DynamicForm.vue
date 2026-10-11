<template>
  <component :is="pageWrapper" v-bind="pageWrapperProps">
    <JRPageHeader v-if="usePageChrome" :title="cleanFormTitle" />

    <div :class="panelClass">
      <p v-if="loadError" class="jr-form-banner" role="alert">{{ loadError }}</p>
      <p v-else-if="loading" class="jr-dynamic-form__status">Loading…</p>

      <form
        v-else-if="fields.length"
        class="jr-dynamic-form__form"
        @submit.prevent="handleSubmit"
        novalidate>
        <p v-if="formBanner" class="jr-form-banner" role="alert">{{ formBanner }}</p>

        <div class="jr-form-grid">
          <JRField
            v-for="key in fields"
            :key="key"
            v-slot="{ describedby, invalid }"
            :label="internalSchema[key].type === 'boolean' ? '' : internalSchema[key].label"
            :required="!!internalSchema[key].required && internalSchema[key].type !== 'boolean'"
            :inputId="fieldId(key)"
            :hint="fieldHint(key)"
            :error="fieldErrors[key]">
            <JRTextarea
              v-if="isTextarea(key)"
              :inputId="fieldId(key)"
              :modelValue="form[key]"
              :disabled="isDisabled"
              :invalid="invalid"
              :required="!!internalSchema[key].required"
              :ariaDescribedby="describedby"
              :placeholder="`Enter ${internalSchema[key].label}`"
              @update:modelValue="setField(key, $event)" />
            <JRCheckbox
              v-else-if="internalSchema[key].type === 'boolean'"
              :inputId="fieldId(key)"
              :modelValue="!!form[key]"
              :label="internalSchema[key].label"
              :disabled="isDisabled"
              @update:modelValue="setField(key, $event)" />
            <JRSelect
              v-else-if="internalSchema[key].type === 'select'"
              :inputId="fieldId(key)"
              :modelValue="form[key]"
              :options="optionsMap[key] || []"
              optionLabel="label"
              optionValue="value"
              :placeholder="`Select ${internalSchema[key].label}`"
              :disabled="isDisabled"
              :invalid="invalid"
              :required="!!internalSchema[key].required"
              :ariaDescribedby="describedby"
              filter
              @update:modelValue="setField(key, $event)" />
            <JRInput
              v-else
              :inputId="fieldId(key)"
              :modelValue="form[key]"
              :disabled="isDisabled"
              :invalid="invalid"
              :required="!!internalSchema[key].required"
              :ariaDescribedby="describedby"
              :placeholder="`Enter ${internalSchema[key].label}`"
              @update:modelValue="setField(key, $event)" />
          </JRField>
        </div>

        <PriceTypePricingGuide v-if="showPriceTypePricingGuide" />

        <div class="jr-dynamic-form__actions">
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
    </div>
  </component>
</template>

<script>
import axios from "axios";
import selectMixin from "@/helpers/useSelectOptions";
import PriceTypePricingGuide from "./PriceTypePricingGuide.vue";
import {
  PRICING_METHOD_FIELD_TOOLTIP,
  MARGIN_PERCENT_FIELD_TOOLTIP,
} from "./priceTypePricingHelp";
import {
  JRPage,
  JRPageHeader,
  JRField,
  JRInput,
  JRSelect,
  JRCheckbox,
  JRTextarea,
  JRButton,
} from "@ui";

export default {
  name: "DynamicForm",
  components: {
    PriceTypePricingGuide,
    JRPage,
    JRPageHeader,
    JRField,
    JRInput,
    JRSelect,
    JRCheckbox,
    JRTextarea,
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
    /** Skip page chrome when hosted inside modal/drawer. */
    embedded: { type: Boolean, default: false },
  },
  emits: ["saved", "cancel"],
  data() {
    return {
      internalSchema: {},
      form: {},
      fields: [],
      fieldErrors: {},
      formBanner: "",
      loadError: "",
      loading: true,
      submitting: false,
    };
  },
  computed: {
    usePageChrome() {
      return !this.isModal && !this.embedded;
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
    isViewMode() {
      if (this.isModal || this.embedded) return this.readOnly;
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
    showPriceTypePricingGuide() {
      return !!(this.internalSchema && this.internalSchema.pricing_method);
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
    await this.initialize();
  },
  methods: {
    fieldId(key) {
      return `dynamic-${key}`;
    },
    isTextarea(key) {
      const cfg = this.internalSchema[key] || {};
      return cfg.type === "textarea" || cfg.widget === "textarea";
    },
    fieldHint(key) {
      if (key === "pricing_method") return PRICING_METHOD_FIELD_TOOLTIP;
      if (key === "margin_percent") return MARGIN_PERCENT_FIELD_TOOLTIP;
      return "";
    },
    setField(key, value) {
      this.form[key] = value;
      if (this.fieldErrors[key]) this.clearFieldError(key);
    },
    clearFieldError(key) {
      const next = { ...this.fieldErrors };
      delete next[key];
      this.fieldErrors = next;
    },
    async initialize() {
      this.loading = true;
      this.loadError = "";
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
        console.error("Error initializing schema:", err);
        this.loadError = "Could not load this form. Try again.";
      } finally {
        this.loading = false;
      }
    },

    async loadRecord() {
      if (!this.internalSchema || !Object.keys(this.internalSchema).length) {
        return;
      }
      try {
        if (this.objectId) {
          const res = await axios.get(`${this.apiEndpoint}${this.objectId}/`);
          const record = res.data || {};
          const next = {};
          this.fields.forEach((key) => {
            const cfg = this.internalSchema[key] || {};
            let value = record[key];
            if (cfg.type === "select" && value && typeof value === "object") {
              value = value.id ?? value.value ?? "";
            }
            if (cfg.type === "boolean") value = !!value;
            if (value == null) {
              value =
                cfg.default !== undefined
                  ? cfg.default
                  : cfg.type === "boolean"
                    ? false
                    : "";
            }
            next[key] = value;
          });
          this.form = next;
        } else {
          this.form = Object.fromEntries(
            this.fields.map((f) => {
              const type = this.internalSchema[f]?.type;
              const def = this.internalSchema[f]?.default;
              if (def !== undefined) return [f, def];
              return [f, type === "boolean" ? false : ""];
            })
          );
        }
        this.fieldErrors = {};
        this.formBanner = "";
      } catch (err) {
        console.error("Error loading record:", err);
        this.loadError = "Could not load this record.";
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
          const v = cleaned[key];
          cleaned[key] =
            v && typeof v === "object" ? v.id ?? v.value ?? "" : v;
        }
      }
      if (this.internalSchema.margin_percent && "margin_percent" in cleaned) {
        const v = cleaned.margin_percent;
        if (v === "" || v === undefined || v === null) {
          cleaned.margin_percent = null;
        } else {
          const n = Number(String(v).replace(",", "."));
          cleaned.margin_percent = Number.isFinite(n) ? n : null;
        }
      }
      return cleaned;
    },

    mapApiErrors(data) {
      const next = {};
      const leftover = [];
      if (!data || typeof data !== "object" || Array.isArray(data)) {
        this.formBanner = "Could not save. Try again.";
        return;
      }
      for (const [key, value] of Object.entries(data)) {
        if (value == null) continue;
        const msg = Array.isArray(value)
          ? value.map(String).join(" ")
          : typeof value === "object"
            ? Object.values(value).flat().map(String).join(" ")
            : String(value);
        if (this.fields.includes(key)) next[key] = msg;
        else if (["detail", "__all__", "non_field_errors"].includes(key)) {
          leftover.push(msg);
        } else leftover.push(msg);
      }
      this.fieldErrors = next;
      this.formBanner = leftover.filter(Boolean).join(" ");
    },

    async handleSubmit() {
      if (this.isViewMode) return;
      this.submitting = true;
      this.formBanner = "";
      this.fieldErrors = {};

      const payload = this._buildCleanPayload();
      const url = this.objectId
        ? `${this.apiEndpoint}${this.objectId}/`
        : this.apiEndpoint;
      const method = this.objectId ? "put" : "post";

      try {
        await axios[method](url, payload);

        if (this.redirectAfterSave) {
          if (this.redirectAfterSave.startsWith("/")) {
            this.$router.push(this.redirectAfterSave);
          } else {
            this.$router.push({ name: this.redirectAfterSave });
          }
        } else {
          this.$emit("saved");
        }
      } catch (error) {
        console.error("Save error:", error);
        const { status, data } = error?.response || {};
        if (status === 400 && data) this.mapApiErrors(data);
        else if (status === 403) {
          this.formBanner = "You do not have permission for this action.";
        } else {
          this.formBanner = "Could not save. Try again.";
        }
      } finally {
        this.submitting = false;
      }
    },

    cancelForm() {
      if (this.isModal) {
        this.$emit("cancel");
      } else if (this.$router && this.$route?.name) {
        this.$router.back();
      } else {
        this.$emit("cancel");
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

.jr-dynamic-form__status {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted, #4b5563);
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

.jr-dynamic-form :deep(.jr-checkbox) {
  column-gap: 0.85rem;
  align-items: center;
}

.jr-dynamic-form :deep(.jr-checkbox__label) {
  margin-inline-start: 0.15rem;
}

.jr-dynamic-form__actions {
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

.jr-embedded-form {
  width: 100%;
}

.jr-embedded-form__panel {
  width: 100%;
}
</style>
