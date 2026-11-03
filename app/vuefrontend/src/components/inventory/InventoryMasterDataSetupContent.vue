<template>
  <div
    class="jr-master-data-setup"
    :class="{ 'jr-master-data-setup--embedded': embedded }">
    <p v-if="loading" class="jr-master-data-setup__status" role="status">
      Verifying status…
    </p>

    <Message
      v-else-if="error"
      class="jr-master-data-setup__message jr-master-data-setup__message--error"
      severity="error"
      :closable="false">
      {{ error }}
    </Message>

    <template v-else-if="!seedDone">
      <Message
        class="jr-master-data-setup__message jr-master-data-setup__message--info"
        severity="info"
        :closable="false">
        <strong>Important:</strong>
        Download the Excel file first to review which products, brands,
        categories, units, price types, warehouses, product prices, absence
        reasons, and Transaction Favorites will be imported.
      </Message>

      <div class="jr-master-data-setup__block">
        <h3 class="jr-master-data-setup__block-title">Download Excel file</h3>
        <JRButton
          type="button"
          variant="secondary"
          :disabled="downloading"
          @click="downloadExcel">
          {{ downloading ? "Downloading…" : "Download Master Data Excel" }}
        </JRButton>
      </div>

      <div class="jr-master-data-setup__block">
        <h3 class="jr-master-data-setup__block-title">Import data</h3>
        <p class="jr-master-data-setup__copy">
          After reviewing the Excel file offline, import the master data into
          your tenant (including product images when available in the fixture
          media).
          <strong>Note:</strong>
          The import runs from the system JSON fixture, not from the downloaded
          Excel file. The Excel file is for review only.
        </p>

        <div class="jr-master-data-setup__checks">
          <JRCheckbox
            v-model="confirmCheck"
            :inputId="confirmId"
            class="jr-master-data-setup__confirm"
            :disabled="importing">
            I confirm: import masters into my tenant
          </JRCheckbox>

          <JRCheckbox
            v-model="includeFavorites"
            :inputId="favoritesId"
            class="jr-master-data-setup__confirm"
            :disabled="importing">
            Also import Transaction Favorites (Import Favorites)
          </JRCheckbox>
        </div>

        <div class="jr-master-data-setup__actions">
          <JRButton
            type="button"
            variant="primary"
            :disabled="!confirmCheck || importing"
            @click="importMasterData">
            {{
              importing
                ? "Importing…"
                : compact
                  ? "Import Florida inventory masters"
                  : "Import Master Data"
            }}
          </JRButton>
          <JRButton
            v-if="!embedded"
            type="button"
            variant="secondary"
            :disabled="importing"
            @click="$emit('cancel')">
            Cancel
          </JRButton>
        </div>
      </div>
    </template>

    <Message
      v-else
      class="jr-master-data-setup__message jr-master-data-setup__message--success"
      severity="success"
      :closable="false">
      <strong>Inventory masters imported.</strong>
      The inventory master data (products, brands, categories, prices, absence
      reasons, product images when available, and Import Favorites if selected)
      has been successfully imported to this tenant. Import cannot be performed
      more than once.
    </Message>
  </div>
</template>

<script>
import { getAccessToken } from "@/auth/tokenHelpers";
import { defineComponent } from "vue";
import axios from "axios";
import Message from "primevue/message";
import { JRButton, JRCheckbox } from "@/ui";

let idSeq = 0;

export default defineComponent({
  name: "InventoryMasterDataSetupContent",
  components: {
    Message,
    JRButton,
    JRCheckbox,
  },
  props: {
    embedded: {
      type: Boolean,
      default: false,
    },
    /** Wizard: shorter copy + Florida CTA label */
    compact: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["imported", "cancel", "status"],
  data() {
    idSeq += 1;
    return {
      loading: true,
      error: null,
      seedDone: false,
      confirmCheck: false,
      includeFavorites: true,
      importing: false,
      downloading: false,
      confirmId: `confirm-import-masters-${idSeq}`,
      favoritesId: `include-import-favorites-${idSeq}`,
    };
  },
  mounted() {
    this.loadPreview();
  },
  methods: {
    emitStatus() {
      this.$emit("status", { seedDone: this.seedDone, loading: this.loading });
    },
    async loadPreview() {
      try {
        this.loading = true;
        this.error = null;
        const token = getAccessToken();
        const response = await axios.get("/api/master-data/preview/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.seedDone = response.data.seed_done || false;
      } catch (error) {
        if (error.response?.status === 403) {
          this.seedDone = true;
        } else {
          this.error =
            error.response?.data?.error ||
            "Error verifying master data status.";
        }
      } finally {
        this.loading = false;
        this.emitStatus();
      }
    },
    async downloadExcel() {
      try {
        this.downloading = true;
        const token = getAccessToken();
        const response = await axios.get("/api/master-data/download-excel/", {
          headers: { Authorization: `Bearer ${token}` },
          responseType: "blob",
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        const contentDisposition = response.headers["content-disposition"];
        let filename = "masters_inventory.xlsx";
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch) filename = filenameMatch[1];
        }
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (error) {
        this.error =
          error.response?.data?.error ||
          "An error occurred while downloading the Excel file.";
      } finally {
        this.downloading = false;
      }
    },
    async importMasterData() {
      if (!this.confirmCheck) {
        this.error = "You must confirm the import before continuing.";
        return;
      }

      try {
        this.importing = true;
        this.error = null;
        const token = getAccessToken();
        const response = await axios.post(
          "/api/master-data/import/",
          {
            confirm: true,
            include_favorites: this.includeFavorites,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          },
        );

        if (response.data.success) {
          this.seedDone = true;
          this.confirmCheck = false;
          this.includeFavorites = true;
          this.emitStatus();
          this.$emit("imported", response.data);
        }
      } catch (error) {
        this.error =
          error.response?.data?.error ||
          "An error occurred while importing the master data.";
      } finally {
        this.importing = false;
      }
    },
  },
});
</script>

<style scoped>
.jr-master-data-setup {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-master-data-setup__status {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-master-data-setup__block-title {
  margin: 0 0 0.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-text);
}

.jr-master-data-setup__copy {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-jr-muted);
  max-width: none;
}

.jr-master-data-setup__code {
  padding: 0.1rem 0.35rem;
  font-size: 0.75rem;
  background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
  color: var(--color-jr-text);
}

.jr-master-data-setup__checks {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.65rem;
  margin-bottom: 0.75rem;
}

.jr-master-data-setup__confirm {
  margin: 0;
}

.jr-master-data-setup :deep(.jr-checkbox) {
  column-gap: 0.85rem;
  align-items: flex-start;
}

.jr-master-data-setup :deep(.jr-checkbox__label) {
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.35;
  color: var(--color-jr-text);
}

.jr-master-data-setup__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.jr-master-data-setup__message {
  margin: 0;
  --p-message-border-radius: var(--radius-jr-control, 0);
}

.jr-master-data-setup__message--info {
  --p-message-info-background: var(--color-jr-info-subtle);
  --p-message-info-border-color: var(--color-jr-border);
  --p-message-info-color: var(--color-jr-info-text);
}

.jr-master-data-setup__message--success {
  --p-message-success-background: var(--color-jr-success-subtle);
  --p-message-success-border-color: var(--color-jr-border);
  --p-message-success-color: var(--color-jr-success-text);
}

.jr-master-data-setup__message--error {
  --p-message-error-background: var(--color-jr-danger-subtle);
  --p-message-error-border-color: var(--color-jr-border);
  --p-message-error-color: var(--color-jr-danger-text);
}
</style>
