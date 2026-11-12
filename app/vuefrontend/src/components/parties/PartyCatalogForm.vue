<template>
  <div class="jr-party-catalog-form">
    <p v-if="loading" class="jr-party-catalog-form__status" role="status">
      Loading…
    </p>

    <form
      v-else
      class="jr-party-catalog-form__form"
      @submit.prevent="handleSubmit"
      novalidate>
      <p
        v-if="formBanner"
        class="jr-form-banner"
        role="alert"
        tabindex="-1">
        {{ formBanner }}
      </p>

      <JRField
        v-slot="{ describedby, invalid }"
        :label="$t('parties.partyCatalogName')"
        inputId="party-catalog-name"
        required
        :error="fieldErrors.name">
        <JRInput
          inputId="party-catalog-name"
          v-model="form.name"
          maxlength="150"
          :disabled="submitting"
          :invalid="invalid"
          required
          :ariaDescribedby="describedby"
          @update:modelValue="clearFieldError('name')" />
      </JRField>

      <JRField
        v-slot="{ describedby }"
        :label="$t('parties.partyCatalogDescription')"
        inputId="party-catalog-description">
        <JRTextarea
          inputId="party-catalog-description"
          v-model="form.description"
          :rows="3"
          :placeholder="$t('parties.partyCatalogDescriptionPlaceholder')"
          :disabled="submitting"
          :ariaDescribedby="describedby" />
      </JRField>

      <JRField :label="$t('parties.partyCatalogActive')" inputId="party-catalog-active">
        <JRCheckbox
          inputId="party-catalog-active"
          v-model="form.is_active"
          :ariaLabel="$t('parties.partyCatalogActive')"
          :disabled="submitting" />
      </JRField>

      <div class="jr-party-catalog-form__actions">
        <JRButton type="submit" variant="primary" :disabled="submitting">
          {{ submitting ? $t("common.saving") : $t("common.save") }}
        </JRButton>
        <JRButton
          type="button"
          variant="secondary"
          :disabled="submitting"
          @click="$emit('cancel')">
          {{ $t("common.cancel") }}
        </JRButton>
      </div>
    </form>
  </div>
</template>

<script>
import axios from "axios";
import {
  JRField,
  JRInput,
  JRTextarea,
  JRCheckbox,
  JRButton,
} from "@ui";

const ENDPOINTS = {
  type: "/api/party-types/",
  category: "/api/party-categories/",
};

export default {
  name: "PartyCatalogForm",
  components: {
    JRField,
    JRInput,
    JRTextarea,
    JRCheckbox,
    JRButton,
  },
  props: {
    kind: {
      type: String,
      required: true,
      validator: (v) => v === "type" || v === "category",
    },
    objectId: {
      type: [String, Number],
      default: null,
    },
  },
  emits: ["saved", "cancel"],
  data() {
    return {
      loading: false,
      submitting: false,
      formBanner: "",
      fieldErrors: {},
      form: {
        name: "",
        description: "",
        is_active: true,
      },
    };
  },
  computed: {
    endpoint() {
      return ENDPOINTS[this.kind];
    },
    entityLabel() {
      return this.kind === "type" ? "party type" : "party category";
    },
  },
  async created() {
    if (!this.objectId) return;
    this.loading = true;
    try {
      const { data } = await axios.get(`${this.endpoint}${this.objectId}/`);
      this.form = {
        name: data.name || "",
        description: data.description || "",
        is_active: data.is_active !== false,
      };
    } catch (err) {
      console.error(`Error loading ${this.entityLabel}:`, err);
      this.formBanner = `Error loading the ${this.entityLabel}.`;
      this.notifyToastError?.(this.formBanner);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    clearFieldError(key) {
      if (!this.fieldErrors[key]) return;
      const next = { ...this.fieldErrors };
      delete next[key];
      this.fieldErrors = next;
    },
    async handleSubmit() {
      this.formBanner = "";
      this.fieldErrors = {};
      const name = (this.form.name || "").trim();
      const description = (this.form.description || "").trim();
      if (!name) {
        this.fieldErrors = { name: "Name is required." };
        this.formBanner = "Name is required.";
        return;
      }
      if (name.length > 150) {
        this.fieldErrors = { name: "Name cannot exceed 150 characters." };
        this.formBanner = "Name cannot exceed 150 characters.";
        return;
      }

      this.submitting = true;
      const payload = {
        name,
        description,
        is_active: !!this.form.is_active,
      };
      try {
        const url = this.objectId
          ? `${this.endpoint}${this.objectId}/`
          : this.endpoint;
        const method = this.objectId ? "put" : "post";
        const { data } = await axios[method](url, payload);
        this.notifyToastSuccess?.(
          this.objectId
            ? `${this.entityLabel[0].toUpperCase()}${this.entityLabel.slice(1)} updated.`
            : `${this.entityLabel[0].toUpperCase()}${this.entityLabel.slice(1)} created.`
        );
        this.$emit("saved", data);
      } catch (error) {
        console.error(`Error saving ${this.entityLabel}:`, error);
        const { status, data } = error?.response || {};
        if (status === 400 && data) {
          const next = {};
          Object.entries(data).forEach(([field, msgs]) => {
            if (field === "detail" || field === "non_field_errors") return;
            next[field] = Array.isArray(msgs) ? msgs.join(", ") : String(msgs);
          });
          this.fieldErrors = next;
          this.formBanner =
            next.name ||
            data.detail ||
            `There were validation errors saving the ${this.entityLabel}.`;
        } else if (status === 403) {
          this.formBanner = "You do not have permission for this action.";
        } else {
          this.formBanner = `Error saving the ${this.entityLabel}.`;
        }
        this.notifyToastError?.(this.formBanner);
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>

<style scoped>
.jr-party-catalog-form__form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-party-catalog-form__status {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-party-catalog-form__actions {
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
