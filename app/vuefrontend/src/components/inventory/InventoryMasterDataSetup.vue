<template>
  <JRPage>
    <JRPageHeader
      title="Inventory Master Data Setup"
      description="Import products, brands, categories, units, price types, warehouses, and product prices into your tenant." />

    <div class="jr-master-data-setup">
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
          <strong>Important:</strong> You can download an Excel file with
          inventory master data (products, brands, categories, units, price
          types, warehouses, product prices). Review and adjust the data if
          necessary before importing it to your tenant.
        </Message>

        <JRSection title="Download Excel file">
          <p class="jr-master-data-setup__copy">
            Download a real Excel file (.xlsx) containing the inventory master
            data from the
            <code class="jr-master-data-setup__code">masters_inventory.json</code>
            fixture file. The file is organized in tabs by model for easy review
            offline.
          </p>
          <JRButton
            type="button"
            variant="secondary"
            :disabled="downloading"
            @click="downloadExcel">
            {{ downloading ? "Downloading…" : "Download Master Data Excel" }}
          </JRButton>
        </JRSection>

        <JRSection title="Import data">
          <p class="jr-master-data-setup__copy">
            After reviewing the Excel file offline, you can import the master
            data to your tenant (including product images when available in the
            fixture media).
            <strong>Note:</strong> The import runs from the system JSON fixture
            (<code class="jr-master-data-setup__code">masters_inventory.json</code>),
            not from the downloaded Excel file. The Excel file is for review only.
          </p>

          <JRCheckbox
            v-model="confirmCheck"
            inputId="confirm-import-masters"
            class="jr-master-data-setup__confirm"
            :disabled="importing">
            I confirm: import masters into my tenant
          </JRCheckbox>

          <div class="jr-master-data-setup__actions">
            <JRButton
              type="button"
              variant="primary"
              :disabled="!confirmCheck || importing"
              @click="importMasterData">
              {{ importing ? "Importing…" : "Import Master Data" }}
            </JRButton>
            <JRButton
              type="button"
              variant="secondary"
              :disabled="importing"
              @click="goBack">
              Cancel
            </JRButton>
          </div>
        </JRSection>
      </template>

      <Message
        v-else
        class="jr-master-data-setup__message jr-master-data-setup__message--success"
        severity="success"
        :closable="false">
        <strong>Inventory masters imported.</strong>
        The inventory master data (products, brands, categories, prices, and
        product images when available) has been successfully imported to this
        tenant. Import cannot be performed more than once.
      </Message>
    </div>
  </JRPage>
</template>

<script>
import { getAccessToken } from '@/auth/tokenHelpers';
import { defineComponent } from "vue";
import axios from "axios";
import Swal from "sweetalert2";
import Message from "primevue/message";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRButton,
  JRCheckbox,
} from "@ui";

export default defineComponent({
  name: "InventoryMasterDataSetup",
  components: {
    Message,
    JRPage,
    JRPageHeader,
    JRSection,
    JRButton,
    JRCheckbox,
  },
  data() {
    return {
      loading: true,
      error: null,
      seedDone: false,
      confirmCheck: false,
      importing: false,
      downloading: false,
    };
  },
  mounted() {
    this.loadPreview();
  },
  methods: {
    async loadPreview() {
      try {
        this.loading = true;
        this.error = null;
        const token = getAccessToken();
        const response = await axios.get("/api/master-data/preview/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.seedDone = response.data.seed_done || false;
      } catch (error) {
        console.error("Error loading preview:", error);
        if (error.response?.status === 403) {
          this.seedDone = true;
        } else {
          this.error =
            error.response?.data?.error ||
            "Error verifying master data status.";
        }
      } finally {
        this.loading = false;
      }
    },
    async downloadExcel() {
      try {
        this.downloading = true;
        const token = getAccessToken();
        const response = await axios.get("/api/master-data/download-excel/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          responseType: "blob",
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        const contentDisposition = response.headers["content-disposition"];
        let filename = "masters_inventory.xlsx";
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        Swal.fire({
          icon: "success",
          title: "Download Successful",
          text: "The Excel file has been downloaded successfully.",
        });
      } catch (error) {
        console.error("Error downloading Excel:", error);
        Swal.fire({
          icon: "error",
          title: "Download Error",
          text:
            error.response?.data?.error ||
            "An error occurred while downloading the Excel file.",
        });
      } finally {
        this.downloading = false;
      }
    },
    async importMasterData() {
      if (!this.confirmCheck) {
        Swal.fire({
          icon: "warning",
          title: "Confirmation Required",
          text: "You must confirm the import before continuing.",
        });
        return;
      }

      try {
        this.importing = true;
        const token = getAccessToken();
        const response = await axios.post(
          "/api/master-data/import/",
          { confirm: true },
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.data.success) {
          Swal.fire({
            icon: "success",
            title: "Import Successful!",
            text:
              response.data.message ||
              "The inventory master data has been imported successfully.",
          });
          this.seedDone = true;
          this.confirmCheck = false;
        }
      } catch (error) {
        console.error("Error importing master data:", error);
        Swal.fire({
          icon: "error",
          title: "Import Error",
          text:
            error.response?.data?.error ||
            "An error occurred while importing the master data.",
        });
      } finally {
        this.importing = false;
      }
    },
    goBack() {
      if (this.$router && this.$route.name) {
        this.$router.back();
      } else {
        this.$router.push("/");
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

.jr-master-data-setup__copy {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-jr-muted);
}

.jr-master-data-setup__code {
  padding: 0.1rem 0.35rem;
  font-size: 0.75rem;
  background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
  color: var(--color-jr-text);
}

.jr-master-data-setup__confirm {
  margin-bottom: 0.75rem;
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
