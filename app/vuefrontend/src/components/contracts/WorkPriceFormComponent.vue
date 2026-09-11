<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" />

    <form class="jr-workprice-form" @submit.prevent="createOrUpdatePrice" novalidate>
      <JRSection title="Details">
        <div class="jr-form-grid">
          <JRField
            v-slot="{ describedby, invalid }"
            label="Name"
            required
            inputId="workprice-name"
            :error="fieldErrors.name">
            <JRInput
              inputId="workprice-name"
              v-model="newPrice.name"
              placeholder="Enter description"
              :disabled="isReadOnly"
              :invalid="invalid"
              :ariaDescribedby="describedby" />
          </JRField>

          <JRField
            v-slot="{ describedby, invalid }"
            label="Trim"
            inputId="workprice-trim"
            :error="fieldErrors.trim"
            class="jr-workprice-form__money">
            <InputNumber
              v-model="newPrice.trim"
              inputId="workprice-trim"
              mode="decimal"
              locale="en-US"
              :min="0"
              :minFractionDigits="2"
              :maxFractionDigits="2"
              :disabled="isReadOnly"
              :invalid="invalid"
              :inputProps="moneyInputProps(describedby, invalid)"
              fluid
              @update:modelValue="onMoneyUpdate('trim', $event)" />
          </JRField>

          <JRField
            v-slot="{ describedby, invalid }"
            label="Rough"
            inputId="workprice-rough"
            :error="fieldErrors.rough"
            class="jr-workprice-form__money">
            <InputNumber
              v-model="newPrice.rough"
              inputId="workprice-rough"
              mode="decimal"
              locale="en-US"
              :min="0"
              :minFractionDigits="2"
              :maxFractionDigits="2"
              :disabled="isReadOnly"
              :invalid="invalid"
              :inputProps="moneyInputProps(describedby, invalid)"
              fluid
              @update:modelValue="onMoneyUpdate('rough', $event)" />
          </JRField>

          <JRField
            v-slot="{ describedby, invalid }"
            label="Unit Price Type"
            required
            inputId="workprice-unit"
            :error="fieldErrors.unit_price">
            <JRSelect
              inputId="workprice-unit"
              v-model="newPrice.unit_price"
              :options="unitPriceOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Select unit price type"
              :disabled="isReadOnly"
              :invalid="invalid"
              :ariaDescribedby="describedby" />
          </JRField>
        </div>
      </JRSection>

      <JRSection title="Builders">
        <p
          v-if="fieldErrors.builders"
          id="workprice-builders-error"
          class="jr-workprice-form__builders-error"
          role="alert">
          {{ fieldErrors.builders }}
        </p>
        <div class="jr-workprice-form__toolbar">
          <div class="jr-workprice-form__search">
            <label class="jr-sr-only" for="workprice-builder-filter">
              Filter builders
            </label>
            <JRInput
              inputId="workprice-builder-filter"
              v-model="builderFilter"
              type="search"
              placeholder="Filter builders..."
              autocomplete="off"
              :disabled="isReadOnly || buildersLoading" />
          </div>
          <div v-if="!isReadOnly" class="jr-workprice-form__bulk">
            <JRButton
              type="button"
              variant="ghost"
              size="sm"
              :disabled="buildersLoading || !filteredBuilders.length"
              @click="selectAll">
              Select All
            </JRButton>
            <JRButton
              type="button"
              variant="ghost"
              size="sm"
              :disabled="buildersLoading || !selectedIds.length"
              @click="clearAll">
              Clear
            </JRButton>
          </div>
        </div>

        <p v-if="buildersLoading" class="jr-workprice-form__status" role="status">
          Loading builders…
        </p>

        <div
          v-else-if="filteredBuilders.length"
          class="jr-assign-grid"
          :class="{ 'jr-assign-grid--invalid': !!fieldErrors.builders }"
          role="group"
          aria-label="Builders"
          :aria-describedby="fieldErrors.builders ? 'workprice-builders-error' : undefined">
          <JRCheckbox
            v-for="builder in filteredBuilders"
            :key="builder.id"
            :inputId="`workprice-builder-${builder.id}`"
            class="jr-assign-grid__item"
            :modelValue="isSelected(builder.id)"
            :disabled="isReadOnly"
            :label="builder.name"
            @update:modelValue="(checked) => toggleBuilder(builder.id, checked)" />
        </div>
        <JREmptyState
          v-else
          :title="buildersEmptyTitle"
          :description="buildersEmptyDescription" />
      </JRSection>

      <div class="jr-workprice-form__actions">
        <template v-if="!isReadOnly">
          <JRButton type="submit" variant="primary" :disabled="saving">
            {{ saving ? "Saving..." : "Save" }}
          </JRButton>
          <JRButton type="button" variant="secondary" :disabled="saving" @click="goList">
            Cancel
          </JRButton>
        </template>
        <JRButton v-else type="button" variant="secondary" @click="goList">
          Back to list
        </JRButton>
      </div>
    </form>
  </JRPage>
</template>

<script>
import axios from "axios";
import InputNumber from "primevue/inputnumber";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRInput,
  JRSelect,
  JRButton,
  JRCheckbox,
  JREmptyState,
} from "@ui";

/** Coerce to 2-decimal money; null/empty → 0.00 for DecimalField. */
function toMoney(value) {
  if (value === null || value === undefined || value === "") return 0.0;
  const n = Number(value);
  if (!Number.isFinite(n)) return 0.0;
  return Number(n.toFixed(2));
}

export default {
  name: "WorkPricesFormView",
  components: {
    InputNumber,
    JRPage,
    JRPageHeader,
    JRSection,
    JRField,
    JRInput,
    JRSelect,
    JRButton,
    JRCheckbox,
    JREmptyState,
  },
  data() {
    return {
      newPrice: {
        name: "",
        trim: 0,
        rough: 0,
        unit_price: "",
      },
      isNewPrice: true,
      availableBuilders: [],
      selectedIds: [],
      builderFilter: "",
      fieldErrors: {},
      saving: false,
      buildersLoading: false,
      unitPriceOptions: [
        { label: "Ea", value: "Ea" },
        { label: "Total", value: "Total" },
      ],
    };
  },
  computed: {
    isReadOnly() {
      return this.$route.name === "work-prices-view";
    },
    pageTitle() {
      if (this.isReadOnly) return "View Piece Work Price";
      return this.isNewPrice ? "New Piece Work Price" : "Edit Piece Work Price";
    },
    filteredBuilders() {
      const q = this.builderFilter.trim().toLowerCase();
      if (!q) return this.availableBuilders;
      return this.availableBuilders.filter((b) =>
        (b.name || "").toLowerCase().includes(q)
      );
    },
    buildersEmptyTitle() {
      if (this.builderFilter.trim() && this.availableBuilders.length) {
        return "No matching builders";
      }
      return "No builders";
    },
    buildersEmptyDescription() {
      if (this.builderFilter.trim() && this.availableBuilders.length) {
        return `No builders match “${this.builderFilter.trim()}”.`;
      }
      return "No builders available yet.";
    },
  },
  mounted() {
    this.fetchAvailableBuilders();
    this.fetchPriceToUpdate();
  },
  methods: {
    moneyInputProps(describedby, invalid) {
      const props = {};
      if (describedby) props["aria-describedby"] = describedby;
      if (invalid) props["aria-invalid"] = "true";
      return Object.keys(props).length ? props : undefined;
    },
    onMoneyUpdate(field, value) {
      this.newPrice[field] = toMoney(value);
    },
    goList() {
      this.$router.push({ name: "work-prices" });
    },
    isSelected(id) {
      return this.selectedIds.includes(id);
    },
    toggleBuilder(id, checked) {
      if (checked) {
        if (!this.selectedIds.includes(id)) {
          this.selectedIds = [...this.selectedIds, id];
        }
        if (this.fieldErrors.builders) {
          const next = { ...this.fieldErrors };
          delete next.builders;
          this.fieldErrors = next;
        }
        return;
      }
      this.selectedIds = this.selectedIds.filter((x) => x !== id);
    },
    selectAll() {
      const ids = new Set(this.selectedIds);
      this.filteredBuilders.forEach((b) => ids.add(b.id));
      this.selectedIds = Array.from(ids);
      if (this.fieldErrors.builders) {
        const next = { ...this.fieldErrors };
        delete next.builders;
        this.fieldErrors = next;
      }
    },
    clearAll() {
      if (!this.builderFilter.trim()) {
        this.selectedIds = [];
        return;
      }
      const filteredIds = new Set(this.filteredBuilders.map((b) => b.id));
      this.selectedIds = this.selectedIds.filter((id) => !filteredIds.has(id));
    },
    fetchPriceToUpdate() {
      const idToUpdate = this.$route.params.id;
      if (!idToUpdate) return;
      this.isNewPrice = false;
      axios
        .get(`/api/workprice/${idToUpdate}/`)
        .then((response) => {
          const editData = response.data;
          this.newPrice = {
            name: editData.name,
            trim: toMoney(editData.trim),
            rough: toMoney(editData.rough),
            unit_price: editData.unit_price,
          };
          this.applySelectedBuilderIds(editData.builders || []);
        })
        .catch((error) => {
          console.error("Error fetching data for editing:", error);
          this.notifyError?.("Error loading piece work price.");
        });
    },
    fetchAvailableBuilders() {
      this.buildersLoading = true;
      axios
        .get("/api/builder/")
        .then((response) => {
          this.availableBuilders = Array.isArray(response.data)
            ? response.data
            : response.data?.results || [];
        })
        .catch((error) => {
          console.error("Error fetching available builders:", error);
          this.notifyError?.("Error loading builders.");
        })
        .finally(() => {
          this.buildersLoading = false;
        });
    },
    applySelectedBuilderIds(ids) {
      this.selectedIds = (ids || [])
        .map((id) => (typeof id === "object" ? id.id : id))
        .filter((id) => id != null);
    },
    focusFirstInvalid() {
      this.$nextTick(() => {
        if (this.fieldErrors.name) {
          document.getElementById("workprice-name")?.focus();
          return;
        }
        if (this.fieldErrors.unit_price) {
          document.getElementById("workprice-unit")?.focus();
          return;
        }
        if (this.fieldErrors.builders) {
          document.getElementById("workprice-builder-filter")?.focus();
        }
      });
    },
    validate() {
      this.fieldErrors = {};
      let ok = true;
      if (!this.newPrice.name || !String(this.newPrice.name).trim()) {
        this.fieldErrors.name = "Name is required";
        ok = false;
      }
      if (!this.newPrice.unit_price) {
        this.fieldErrors.unit_price = "Unit price type is required";
        ok = false;
      }
      // New Piece Work Price must assign at least one builder
      if (this.isNewPrice && !this.selectedIds.length) {
        this.fieldErrors.builders = "Select at least one builder.";
        ok = false;
      }
      return ok;
    },
    createOrUpdatePrice() {
      if (this.isReadOnly) return;
      if (!this.validate()) {
        const msg =
          this.fieldErrors.builders ||
          "Please fix the highlighted fields.";
        this.notifyError?.(msg);
        this.focusFirstInvalid();
        return;
      }

      const idToUpdate = this.$route.params.id;
      const url = idToUpdate ? `/api/workprice/${idToUpdate}/` : "/api/workprice/";
      const dataToSend = {
        name: String(this.newPrice.name).trim(),
        trim: toMoney(this.newPrice.trim),
        rough: toMoney(this.newPrice.rough),
        unit_price: this.newPrice.unit_price,
        builders: [...this.selectedIds],
      };

      this.saving = true;
      axios[idToUpdate ? "put" : "post"](url, dataToSend)
        .then(() => {
          this.notifyToastSuccess?.(
            idToUpdate ? "Piece work price updated." : "Piece work price created."
          );
          this.$router.push("/work-prices");
        })
        .catch((error) => {
          console.error("Error saving price:", error);
          const data = error?.response?.data;
          let detail = "Error saving piece work price.";
          if (data) {
            if (typeof data === "string") detail = data;
            else if (data.detail)
              detail = Array.isArray(data.detail)
                ? data.detail.join(" ")
                : String(data.detail);
            else if (data.non_field_errors)
              detail = [].concat(data.non_field_errors).join(" ");
            else {
              const parts = Object.entries(data).flatMap(([field, msgs]) => {
                const text = Array.isArray(msgs) ? msgs.join(", ") : String(msgs);
                return text ? [`${field}: ${text}`] : [];
              });
              if (parts.length) detail = parts.join(" ");
            }
          }
          this.notifyError?.(detail);
        })
        .finally(() => {
          this.saving = false;
        });
    },
  },
};
</script>

<style scoped>
.jr-form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.75rem 1rem;
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

.jr-workprice-form__money :deep(.p-inputnumber),
.jr-workprice-form__money :deep(.p-inputtext) {
  width: 100%;
}

.jr-workprice-form__builders-error {
  margin: 0 0 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-jr-danger-text);
}

.jr-workprice-form__status {
  margin: 0.5rem 0;
  color: var(--color-jr-muted);
  font-size: 0.875rem;
}

.jr-workprice-form__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.jr-workprice-form__search {
  flex: 1 1 14rem;
  min-width: 0;
  max-width: 24rem;
}

.jr-workprice-form__bulk {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.jr-assign-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.25rem 1rem;
  max-height: min(28rem, 55vh);
  overflow: auto;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
}

.jr-assign-grid--invalid {
  border-color: var(--color-jr-danger);
}

@media (min-width: 640px) {
  .jr-assign-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 900px) {
  .jr-assign-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1200px) {
  .jr-assign-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.jr-assign-grid__item {
  min-width: 0;
}

/* Unlayered scoped rules beat Bootstrap `label { display }` over DS @layer. */
.jr-assign-grid :deep(.jr-checkbox) {
  display: inline-flex;
  align-items: flex-start;
  column-gap: 0.85rem;
  width: 100%;
  min-height: 2.25rem;
  text-align: left;
}

.jr-assign-grid :deep(.jr-checkbox .p-checkbox) {
  flex: 0 0 auto;
  margin-top: 0.15rem;
}

.jr-assign-grid :deep(.jr-checkbox__label) {
  margin-inline-start: 0.15rem;
  overflow-wrap: anywhere;
  line-height: 1.3;
}

.jr-workprice-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.25rem;
  margin-top: 0.5rem;
  background: var(--color-jr-page);
  border-top: 1px solid var(--color-jr-border);
}
</style>
