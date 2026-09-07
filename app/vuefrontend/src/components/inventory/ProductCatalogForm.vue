<template>
  <div class="jr-catalog-form">
    <p v-if="loadError" class="jr-form-banner" role="alert">{{ loadError }}</p>
    <p v-else-if="loading" class="jr-catalog-form__status">Loading…</p>

    <form
      v-else-if="fields.length"
      class="jr-catalog-form__fields"
      @submit.prevent="handleSubmit"
      novalidate>
      <p v-if="formBanner" class="jr-form-banner" role="alert">{{ formBanner }}</p>

      <JRField
        v-for="key in fields"
        :key="key"
        v-slot="{ describedby, invalid }"
        :label="schema[key].type === 'boolean' ? '' : schema[key].label"
        :required="!!schema[key].required && schema[key].type !== 'boolean'"
        :inputId="fieldId(key)"
        :error="fieldErrors[key]">
        <JRTextarea
          v-if="isTextarea(key)"
          :inputId="fieldId(key)"
          :modelValue="form[key]"
          :disabled="submitting"
          :invalid="invalid"
          :required="!!schema[key].required"
          :ariaDescribedby="describedby"
          :placeholder="`Enter ${schema[key].label}`"
          @update:modelValue="setField(key, $event)" />
        <JRCheckbox
          v-else-if="schema[key].type === 'boolean'"
          :inputId="fieldId(key)"
          :modelValue="!!form[key]"
          :label="schema[key].label"
          :disabled="submitting"
          @update:modelValue="setField(key, $event)" />
        <JRSelect
          v-else-if="schema[key].type === 'select'"
          :inputId="fieldId(key)"
          :modelValue="form[key]"
          :options="optionsMap[key] || []"
          optionLabel="label"
          optionValue="value"
          :placeholder="`Select ${schema[key].label}`"
          :disabled="submitting"
          :invalid="invalid"
          :required="!!schema[key].required"
          :ariaDescribedby="describedby"
          filter
          @update:modelValue="setField(key, $event)" />
        <JRInput
          v-else
          :inputId="fieldId(key)"
          :modelValue="form[key]"
          :disabled="submitting"
          :invalid="invalid"
          :required="!!schema[key].required"
          :ariaDescribedby="describedby"
          :placeholder="`Enter ${schema[key].label}`"
          @update:modelValue="setField(key, $event)" />
      </JRField>

      <div v-if="showPriceTypeHelp" class="jr-catalog-note">
        <p>Choose how sales lines get a unit price.</p>
        <p>None uses the list price on this SKU. Markup adds a percent on what you paid. Margin keeps a percent of the sale as profit.</p>
        <p>Enter a percent only when using Markup or Margin.</p>
      </div>

      <div class="jr-catalog-form__actions">
        <JRButton type="submit" variant="primary" :disabled="submitting">
          {{ submitting ? "Saving..." : "Save" }}
        </JRButton>
        <JRButton type="button" variant="secondary" :disabled="submitting" @click="$emit('cancel')">
          {{ backLabel }}
        </JRButton>
      </div>
    </form>
  </div>
</template>

<script>
import axios from "axios";
import { JRField, JRInput, JRSelect, JRCheckbox, JRButton, JRTextarea } from "@ui";

export default {
  name: "ProductCatalogForm",
  components: { JRField, JRInput, JRSelect, JRCheckbox, JRButton, JRTextarea },
  props: {
    schemaEndpoint: { type: String, required: true },
    apiEndpoint: { type: String, required: true },
    objectId: { type: [String, Number], default: null },
    backLabel: { type: String, default: "Cancel" },
  },
  emits: ["saved", "cancel"],
  data() {
    return {
      schema: {},
      form: {},
      fields: [],
      optionsMap: {},
      fieldErrors: {},
      formBanner: "",
      loadError: "",
      loading: true,
      submitting: false,
    };
  },
  computed: {
    showPriceTypeHelp() {
      return !!(this.schema && this.schema.pricing_method);
    },
  },
  watch: {
    objectId: {
      immediate: false,
      async handler() {
        if (this.fields.length) await this.loadRecord();
      },
    },
  },
  async created() {
    await this.initialize();
  },
  methods: {
    fieldId(key) {
      return `catalog-${key}`;
    },
    isTextarea(key) {
      const cfg = this.schema[key] || {};
      return cfg.type === "textarea" || cfg.widget === "textarea";
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
        const response = await axios.get(this.schemaEndpoint);
        this.schema = response.data || {};
        this.fields = Object.keys(this.schema);
        await this.loadOptionsForSchema(this.schema);
        await this.loadRecord();
      } catch (err) {
        console.error("Failed to initialize catalog form", err);
        this.loadError = "Could not load this form. Try again.";
      } finally {
        this.loading = false;
      }
    },
    async loadOptionsForSchema(schema) {
      const next = {};
      for (const [key, config] of Object.entries(schema)) {
        if (config.type === "select" && config.optionsEndpoint) {
          try {
            const res = await axios.get(config.optionsEndpoint);
            const rawOptions = res.data;
            next[key] = (rawOptions || []).map((opt) => ({
              value: opt.id || opt.value,
              label: opt.name || opt.label,
            }));
          } catch (err) {
            console.error(`Error loading options for ${key}`, err);
            next[key] = [];
          }
        } else if (config.options && Array.isArray(config.options)) {
          next[key] = config.options;
        }
      }
      this.optionsMap = next;
    },
    async loadRecord() {
      if (!this.fields.length) return;
      try {
        if (this.objectId) {
          const res = await axios.get(`${this.apiEndpoint}${this.objectId}/`);
          const record = res.data || {};
          const next = {};
          this.fields.forEach((key) => {
            const cfg = this.schema[key] || {};
            let value = record[key];
            if (cfg.type === "select" && value && typeof value === "object") {
              value = value.id ?? value.value ?? "";
            }
            if (cfg.type === "boolean") value = !!value;
            if (value == null) {
              value = cfg.default !== undefined ? cfg.default : cfg.type === "boolean" ? false : "";
            }
            next[key] = value;
          });
          this.form = next;
        } else {
          this.form = Object.fromEntries(
            this.fields.map((key) => {
              const type = this.schema[key]?.type;
              const def = this.schema[key]?.default;
              if (def !== undefined) return [key, def];
              return [key, type === "boolean" ? false : ""];
            })
          );
        }
        this.fieldErrors = {};
        this.formBanner = "";
      } catch (err) {
        console.error("Error loading catalog record", err);
        this.loadError = "Could not load this record.";
      }
    },
    buildCleanPayload() {
      const cleaned = { ...this.form };
      for (const key of this.fields) {
        const cfg = this.schema[key] || {};
        if (
          ["string", "text"].includes(cfg.type) ||
          cfg.type === "textarea" ||
          cfg.widget === "textarea"
        ) {
          cleaned[key] = (cleaned[key] ?? "").toString().trim();
        }
        if (cfg.type === "select" && cfg.optionsEndpoint) {
          const v = cleaned[key];
          cleaned[key] = v && typeof v === "object" ? v.id ?? v.value ?? "" : v;
        }
      }
      if (this.schema.margin_percent && "margin_percent" in cleaned) {
        const v = cleaned.margin_percent;
        if (v === "" || v === undefined || v === null) cleaned.margin_percent = null;
        else {
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
        else if (["detail", "__all__", "non_field_errors"].includes(key)) leftover.push(msg);
        else leftover.push(msg);
      }
      this.fieldErrors = next;
      this.formBanner = leftover.filter(Boolean).join(" ");
    },
    async handleSubmit() {
      this.submitting = true;
      this.formBanner = "";
      this.fieldErrors = {};
      const payload = this.buildCleanPayload();
      const url = this.objectId
        ? `${this.apiEndpoint}${this.objectId}/`
        : this.apiEndpoint;
      const method = this.objectId ? "put" : "post";
      try {
        await axios[method](url, payload);
        this.$emit("saved");
      } catch (error) {
        console.error("Catalog save error", error);
        const status = error?.response?.status;
        const data = error?.response?.data;
        if (status === 400 && data) this.mapApiErrors(data);
        else if (status === 403) this.formBanner = "You do not have permission for this action.";
        else this.formBanner = "Could not save. Try again.";
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>

<style scoped>
.jr-catalog-form__fields {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.jr-catalog-form__status {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-catalog-form :deep(.jr-checkbox) {
  column-gap: 0.85rem;
  align-items: center;
}

.jr-catalog-form :deep(.jr-checkbox__label) {
  margin-inline-start: 0.15rem;
}

.jr-catalog-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.jr-catalog-note {
  margin: 0;
  padding: 0.65rem 0.75rem;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-jr-text, #111827);
  background: var(--color-jr-surface-muted, #f9fafb);
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
}

.jr-catalog-note p {
  margin: 0 0 0.35rem;
}

.jr-catalog-note p:last-child {
  margin-bottom: 0;
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
