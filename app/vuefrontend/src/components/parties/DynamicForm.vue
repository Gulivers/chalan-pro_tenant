<template>
  <component :is="pageWrapper" v-bind="pageWrapperProps">
    <JRPageHeader v-if="usePageChrome" :title="pageHeading">
      <template v-if="isViewMode && canEditFromView" #actions>
        <JRButton variant="primary" size="sm" @click="goToEdit">
          Edit Party
        </JRButton>
      </template>
    </JRPageHeader>

    <div :class="panelClass">
      <p
        v-if="!schemaReady"
        class="jr-dynamic-form__loading"
        role="status">
        Loading form…
      </p>

      <form
        v-else
        class="jr-dynamic-form__form"
        @submit.prevent="handleSubmit"
        novalidate>
        <div
          v-if="formBanner"
          ref="formBannerRef"
          class="jr-form-banner"
          role="alert"
          tabindex="-1">
          {{ formBanner }}
        </div>

        <JRSection
          v-for="section in formSections"
          :key="section.title"
          :title="section.title">
          <div
            class="jr-form-grid"
            :class="section.gridClass">
            <template v-for="key in section.fields" :key="key">
              <JRField
                v-if="internalSchema[key] && internalSchema[key].type !== 'boolean'"
                v-slot="{ describedby, invalid }"
                :label="fieldLabel(key)"
                :required="!!internalSchema[key].required"
                :inputId="`dyn-${key}`"
                :hint="fieldHint(key)"
                :error="validationErrors[key]"
                :class="fieldClass(key, section)">
                <JRInput
                  v-if="
                    internalSchema[key].type === 'string' ||
                    internalSchema[key].type === 'text'
                  "
                  :inputId="`dyn-${key}`"
                  v-model="form[key]"
                  :disabled="isDisabled"
                  :invalid="invalid"
                  :required="!!internalSchema[key].required"
                  :ariaDescribedby="describedby" />

                <InputNumber
                  v-else-if="isDecimalField(internalSchema[key], key)"
                  :inputId="`dyn-${key}`"
                  v-model="form[key]"
                  mode="decimal"
                  locale="en-US"
                  :min="0"
                  :minFractionDigits="2"
                  :maxFractionDigits="2"
                  :disabled="isDisabled"
                  :invalid="invalid"
                  :inputProps="
                    decimalInputProps(
                      describedby,
                      invalid,
                      !!internalSchema[key].required
                    )
                  "
                  fluid
                  @update:modelValue="(v) => onDecimalUpdate(key, v)" />

                <JRTextarea
                  v-else-if="
                    internalSchema[key].type === 'textarea' ||
                    internalSchema[key].widget === 'textarea'
                  "
                  :inputId="`dyn-${key}`"
                  v-model="form[key]"
                  :rows="3"
                  :disabled="isDisabled"
                  :invalid="invalid"
                  :ariaDescribedby="describedby" />

                <JRSelect
                  v-else-if="internalSchema[key].type === 'select'"
                  :inputId="`dyn-${key}`"
                  v-model="form[key]"
                  :options="optionsMap[key] || []"
                  optionLabel="label"
                  optionValue="value"
                  :disabled="isDisabled"
                  :multiple="internalSchema[key].multiple || false"
                  filter
                  :placeholder="`Select ${fieldLabel(key)}`"
                  :showClear="true"
                  :invalid="invalid"
                  :required="!!internalSchema[key].required"
                  :ariaDescribedby="describedby" />
              </JRField>

              <JRField
                v-else-if="
                  internalSchema[key] && internalSchema[key].type === 'boolean'
                "
                v-slot="{ describedby, invalid }"
                :label="fieldLabel(key)"
                :required="isPartyRoleField(key)"
                :inputId="`dyn-${key}`"
                :hint="fieldHint(key)"
                :error="validationErrors[key]"
                class="jr-dynamic-form__flag">
                <JRCheckbox
                  :inputId="`dyn-${key}`"
                  v-model="form[key]"
                  :ariaLabel="fieldLabel(key)"
                  :invalid="invalid"
                  :ariaDescribedby="describedby"
                  :disabled="isDisabled"
                  @update:modelValue="onPartyRoleChange" />
              </JRField>
            </template>
          </div>
        </JRSection>

        <div
          :class="[
            'jr-dynamic-form__actions',
            {
              'jr-dynamic-form__actions--sticky': usePageChrome || isModal,
            },
          ]">
          <template v-if="!isViewMode">
            <JRButton type="submit" variant="primary" :disabled="isDisabled">
              {{
                submitting
                  ? "Saving..."
                  : isEditMode
                    ? "Update"
                    : "Save"
              }}
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
            {{ usePageChrome ? "Back to list" : "Back" }}
          </JRButton>
        </div>
      </form>
    </div>
  </component>
</template>

<script>
import axios from "axios";
import InputNumber from "primevue/inputnumber";
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

/** Known money amount fields on Party/Builder (schema may still say string). */
const MONEY_FIELD_KEYS = new Set([
  "trim_amount",
  "rough_amount",
  "travel_price_amount",
]);

const LABEL_OVERRIDES = {
  zipcode: "ZIP Code",
};

const HINT_OVERRIDES = {
  name: "Must be unique within this organization.",
  trim_amount:
    "At least one of Trim, Rough, or Travel Amount must be greater than 0.",
  crews: "Assign supervisor crews that own this community.",
};

const PARTY_ROLE_KEYS = ["customer_rank", "supplier_rank"];

const PRICING_AMOUNT_KEYS = [
  "trim_amount",
  "rough_amount",
  "travel_price_amount",
];

function toMoney(value) {
  if (value === null || value === undefined || value === "") return 0.0;
  const n = Number(value);
  if (!Number.isFinite(n)) return 0.0;
  return Number(n.toFixed(2));
}

function normalizeSchema(schema) {
  const out = {};
  for (const [key, cfg] of Object.entries(schema || {})) {
    const next = { ...(cfg || {}) };
    if (
      MONEY_FIELD_KEYS.has(key) ||
      next.type === "number" ||
      next.type === "decimal" ||
      next.widget === "money"
    ) {
      next.type = "decimal";
    }
    if (LABEL_OVERRIDES[key]) {
      next.label = LABEL_OVERRIDES[key];
    }
    out[key] = next;
  }
  return out;
}

export default {
  name: "DynamicForm",
  components: {
    InputNumber,
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
    /**
     * Optional section map for Operational forms.
     * [{ title, fields: string[], grid?: 'default'|'identity'|'pricing'|'address'|'contact'|'flags' }]
     */
    sections: {
      type: Array,
      default: null,
    },
    editRouteName: {
      type: String,
      default: null,
    },
  },
  emits: ["saved", "cancel"],
  data() {
    return {
      internalSchema: {},
      form: {},
      fields: [],
      submitting: false,
      validationErrors: {},
      formBanner: "",
      schemaReady: false,
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
      const base = this.usePageChrome
        ? "jr-dynamic-form"
        : "jr-embedded-form__panel jr-dynamic-form";
      return this.isModal ? `${base} jr-dynamic-form--drawer` : base;
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
    canEditFromView() {
      return (
        this.isViewMode &&
        !!this.objectId &&
        !!this.editRouteName &&
        !this.isModal
      );
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
    formSections() {
      const keys = Object.keys(this.internalSchema || {});
      if (!keys.length) return [];

      const gridClassFor = (grid) => {
        switch (grid) {
          case "identity":
            return "jr-form-grid--identity";
          case "pricing":
            return "jr-form-grid--pricing";
          case "address":
            return "jr-form-grid--address";
          case "contact":
            return "jr-form-grid--contact";
          case "flags":
            return "jr-form-grid--flags";
          default:
            return "jr-form-grid--default";
        }
      };

      if (Array.isArray(this.sections) && this.sections.length) {
        const used = new Set();
        const mapped = this.sections
          .map((section) => {
            const fields = (section.fields || []).filter((key) => {
              if (!this.internalSchema[key]) return false;
              used.add(key);
              return true;
            });
            if (!fields.length) return null;
            return {
              title: section.title || "Details",
              fields,
              gridClass: gridClassFor(section.grid || "default"),
            };
          })
          .filter(Boolean);

        const leftover = keys.filter((key) => !used.has(key));
        if (leftover.length) {
          mapped.push({
            title: "Other",
            fields: leftover,
            gridClass: gridClassFor("default"),
          });
        }
        return mapped;
      }

      return [
        {
          title: this.isModal ? "" : "Details",
          fields: keys,
          gridClass: gridClassFor("default"),
        },
      ];
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
        this.internalSchema = normalizeSchema(this.schema);
      } else if (this.schemaEndpoint) {
        const response = await axios.get(this.schemaEndpoint);
        this.internalSchema = normalizeSchema(response.data || {});
      }

      this.fields = Object.keys(this.internalSchema);

      await this.loadOptionsForSchema(this.internalSchema);
      await this.loadRecord();
      this.schemaReady = Object.keys(this.internalSchema).length > 0;
    } catch (err) {
      console.error("Error initializing schema:", err);
      this.schemaReady = false;
      this.notifyToastError?.("Error initializing the form schema.");
    }
  },
  methods: {
    fieldLabel(key) {
      return this.internalSchema[key]?.label || key;
    },
    fieldHint(key) {
      if (this.isViewMode) return "";
      if (this.isPartyRoleField(key)) {
        return "At least one role is required.";
      }
      return HINT_OVERRIDES[key] || "";
    },
    isPartyRoleField(key) {
      return this.hasPartyRoleFields() && PARTY_ROLE_KEYS.includes(key);
    },
    fieldClass(key, section) {
      if (section.gridClass?.includes("address") && key === "street") {
        return "jr-form-grid__full";
      }
      if (key === "crews" && this.internalSchema[key]?.multiple) {
        return "jr-form-grid__full";
      }
      return undefined;
    },
    isDecimalField(config, key) {
      return (
        config?.type === "decimal" ||
        config?.widget === "money" ||
        MONEY_FIELD_KEYS.has(key)
      );
    },
    decimalInputProps(describedby, invalid, required) {
      const props = {};
      if (describedby) props["aria-describedby"] = describedby;
      if (invalid) props["aria-invalid"] = "true";
      if (required) props["aria-required"] = "true";
      return Object.keys(props).length ? props : undefined;
    },
    onDecimalUpdate(key, value) {
      this.form[key] = toMoney(value);
    },
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
          const data = { ...(res.data || {}) };
          for (const key of this.fields) {
            const cfg = this.internalSchema[key] || {};
            if (this.isDecimalField(cfg, key)) {
              data[key] = toMoney(data[key]);
            }
            if (cfg.type === "boolean") {
              // customer_rank / supplier_rank may arrive as ints from API
              if (key === "customer_rank" || key === "supplier_rank") {
                data[key] = Number(data[key]) > 0;
              } else {
                data[key] = !!data[key];
              }
            }
          }
          this.form = data;
        } else {
          this.form = Object.fromEntries(
            this.fields.map((f) => {
              const cfg = this.internalSchema[f] || {};
              const type = cfg.type;
              const def = cfg.default;
              if (def !== undefined) return [f, def];
              if (type === "boolean") return [f, f === "is_active"];
              if (type === "select") return [f, this._emptySelectDefault(cfg)];
              if (this.isDecimalField(cfg, f)) return [f, 0.0];
              return [f, ""];
            })
          );
        }
      } catch (err) {
        console.error("Error loading record:", err);
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

        if (this.isDecimalField(cfg, key)) {
          cleaned[key] = toMoney(cleaned[key]);
        }

        if (cfg.type === "boolean") {
          if (key === "customer_rank" || key === "supplier_rank") {
            cleaned[key] = cleaned[key] ? 1 : 0;
          } else {
            cleaned[key] = !!cleaned[key];
          }
        }

        if (cfg.type === "select" && cfg.optionsEndpoint) {
          cleaned[key] = this._normalizeSelectValue(cleaned[key]);
        }
      }
      return cleaned;
    },

    hasBuilderPricingFields() {
      return PRICING_AMOUNT_KEYS.every((key) => this.internalSchema[key]);
    },

    validatePricingAmounts() {
      if (!this.hasBuilderPricingFields()) return true;

      const hasPositive = PRICING_AMOUNT_KEYS.some(
        (key) => toMoney(this.form[key]) > 0
      );
      if (hasPositive) return true;

      const message =
        "Enter at least one amount greater than 0 for Trim, Rough, or Travel.";
      PRICING_AMOUNT_KEYS.forEach((key) => {
        this.validationErrors[key] = message;
      });
      return false;
    },

    hasPartyRoleFields() {
      return PARTY_ROLE_KEYS.every((key) => this.internalSchema[key]);
    },

    validatePartyRoles() {
      if (!this.hasPartyRoleFields()) return true;

      if (this.form.customer_rank || this.form.supplier_rank) return true;

      PARTY_ROLE_KEYS.forEach((key) => {
        this.validationErrors[key] = `${this.fieldLabel(key)} is required.`;
      });
      return false;
    },

    onPartyRoleChange() {
      if (!this.hasPartyRoleFields()) return;
      if (!this.form.customer_rank && !this.form.supplier_rank) return;

      const next = { ...this.validationErrors };
      let changed = false;
      PARTY_ROLE_KEYS.forEach((key) => {
        if (next[key]) {
          delete next[key];
          changed = true;
        }
      });
      if (changed) {
        this.validationErrors = next;
        if (this.formBanner) {
          this.formBanner = "";
        }
      }
    },

    _mapUniqueConstraintDetail(message) {
      const fieldErrors = {};
      const lower = String(message || "").toLowerCase();

      if (
        lower.includes("pkey") ||
        lower.includes("primary key") ||
        lower.includes("sequence")
      ) {
        return fieldErrors;
      }

      if (lower.includes("rfc") && this.internalSchema.rfc) {
        fieldErrors.rfc = "A party with this RFC already exists.";
      }
      if (
        (lower.includes("name") ||
          lower.includes("uniq_builder_name") ||
          (lower.includes("unique") && !fieldErrors.rfc)) &&
        this.internalSchema.name
      ) {
        fieldErrors.name = "A party with this name already exists.";
      }

      return fieldErrors;
    },

    validateForm() {
      this.validationErrors = {};
      this.formBanner = "";
      let hasErrors = false;

      for (const [key, config] of Object.entries(this.internalSchema)) {
        const value = this.form[key];
        const label = this.fieldLabel(key);

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

      if (!hasErrors && !this.validatePricingAmounts()) {
        hasErrors = true;
      }

      if (!hasErrors && !this.validatePartyRoles()) {
        hasErrors = true;
      }

      if (hasErrors) {
        this.formBanner = "Fix the highlighted fields before saving.";
        this.$nextTick(() => {
          this.$refs.formBannerRef?.focus?.();
        });
      }

      return !hasErrors;
    },

    async _findDuplicateRecord(params) {
      const response = await axios.get(
        `${this.apiEndpoint}?${params.toString()}`
      );
      const rows = Array.isArray(response.data)
        ? response.data
        : response.data?.results || [];
      return rows[0] || null;
    },

    async validateUniqueness() {
      const name = this.form.name?.trim();
      const rfc = this.form.rfc?.trim();

      if (!name && !rfc) return true;

      try {
        const errors = [];

        if (name) {
          const params = new URLSearchParams({ name });
          if (this.objectId) params.append("exclude_id", this.objectId);
          const duplicate = await this._findDuplicateRecord(params);
          if (
            duplicate &&
            duplicate.name?.toLowerCase() === name.toLowerCase()
          ) {
            const message = "A party with this name already exists.";
            errors.push(message);
            this.validationErrors = {
              ...this.validationErrors,
              name: message,
            };
          }
        }

        if (rfc) {
          const params = new URLSearchParams({ rfc });
          if (this.objectId) params.append("exclude_id", this.objectId);
          const duplicate = await this._findDuplicateRecord(params);
          if (duplicate && duplicate.rfc === rfc) {
            const message = "A party with this RFC already exists.";
            errors.push(message);
            this.validationErrors = {
              ...this.validationErrors,
              rfc: message,
            };
          }
        }

        if (errors.length > 0) {
          this.formBanner = errors.join(" ");
          this.notifyToastError?.(errors.join(" "));
          return false;
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
      this.formBanner = "";

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
        console.error("Save error:", error);
        const { status, data } = error?.response || {};

        if (status === 400 && data) {
          const fieldErrors = {};
          const messages = [];

          for (const [field, msgs] of Object.entries(data)) {
            const message = Array.isArray(msgs)
              ? msgs.map(String).join(", ")
              : String(msgs);

            if (field === "detail" || field === "non_field_errors") {
              Object.assign(
                fieldErrors,
                this._mapUniqueConstraintDetail(message)
              );
              continue;
            }

            if (this.internalSchema[field]) {
              fieldErrors[field] = message;
              messages.push(`${this.fieldLabel(field)}: ${message}`);
            } else {
              messages.push(`${field}: ${message}`);
            }
          }

          this.validationErrors = {
            ...this.validationErrors,
            ...fieldErrors,
          };
          const banner =
            messages.filter(Boolean).join(" ") ||
            fieldErrors.name ||
            fieldErrors.rfc ||
            fieldErrors.customer_rank ||
            "There were validation errors.";
          this.formBanner = banner;
          this.notifyToastError?.(banner);
        } else if (status === 403) {
          this.formBanner = "You do not have permission for this action.";
          this.notifyToastError?.(
            "You do not have permission for this action."
          );
        } else {
          const errorMessage =
            data?.detail || data?.message || "Error saving the record.";
          this.formBanner = errorMessage;
          this.notifyToastError?.(errorMessage);
        }
      } finally {
        this.submitting = false;
      }
    },

    goToEdit() {
      if (!this.objectId || !this.editRouteName) return;
      this.$router.push({
        name: this.editRouteName,
        params: { id: this.objectId },
      });
    },

    cancelForm() {
      if (this.isModal) {
        this.$emit("cancel");
      } else if (this.redirectAfterSave) {
        if (this.redirectAfterSave.startsWith("/")) {
          this.$router.push(this.redirectAfterSave);
        } else {
          this.$router.push({ name: this.redirectAfterSave });
        }
      } else if (this.$router && this.$route.name) {
        this.$router.back();
      } else {
        this.$emit("cancel");
      }
    },
  },
};
</script>

<style scoped>
.jr-dynamic-form {
  width: 100%;
  min-width: 0;
  max-width: 100%;
}

.jr-dynamic-form__form {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
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
  .jr-form-grid--default,
  .jr-form-grid--identity,
  .jr-form-grid--pricing,
  .jr-form-grid--address,
  .jr-form-grid--contact {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .jr-form-grid--flags {
    grid-template-columns: repeat(2, max-content);
    column-gap: 1.5rem;
  }
}

@media (min-width: 1024px) {
  .jr-form-grid--default,
  .jr-form-grid--identity,
  .jr-form-grid--pricing,
  .jr-form-grid--address {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .jr-form-grid--contact {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    max-width: 40rem;
  }

  .jr-form-grid--flags {
    grid-template-columns: repeat(2, max-content);
    column-gap: 2rem;
  }
}

.jr-dynamic-form--drawer .jr-form-grid {
  gap: 0.85rem;
}

.jr-dynamic-form--drawer .jr-form-grid,
.jr-dynamic-form--drawer .jr-form-grid--default,
.jr-dynamic-form--drawer .jr-form-grid--identity,
.jr-dynamic-form--drawer .jr-form-grid--pricing,
.jr-dynamic-form--drawer .jr-form-grid--address,
.jr-dynamic-form--drawer .jr-form-grid--contact,
.jr-dynamic-form--drawer .jr-form-grid--flags {
  grid-template-columns: minmax(0, 1fr);
}

.jr-dynamic-form--drawer .jr-form-grid__full {
  grid-column: auto;
}

.jr-dynamic-form--drawer .jr-form-grid--contact {
  max-width: none;
}

.jr-dynamic-form--drawer .jr-form-grid--flags {
  justify-items: start;
}

.jr-dynamic-form__flag :deep(.jr-checkbox) {
  min-height: 2.5rem;
}

.jr-form-banner {
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
  background: var(--color-jr-danger-subtle);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
}

.jr-form-banner:focus {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
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

.jr-embedded-form .jr-dynamic-form__actions--sticky {
  background: var(--color-jr-surface, #fff);
  padding-bottom: calc(0.25rem + env(safe-area-inset-bottom, 0px));
}

.jr-dynamic-form__loading {
  margin: 0;
  padding: 1rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-dynamic-form :deep(.jr-checkbox) {
  column-gap: 0.85rem;
  align-items: center;
}

.jr-dynamic-form :deep(.p-inputnumber),
.jr-dynamic-form :deep(.p-inputnumber .p-inputtext) {
  width: 100%;
}
</style>
