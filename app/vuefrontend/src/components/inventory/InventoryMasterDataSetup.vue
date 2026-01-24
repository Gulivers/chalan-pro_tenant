<template>
  <div class="container">
    <h3 class="text-warning pt-3">
      <p>Inventory Master Data Setup</p>
    </h3>

    <div class="card shadow mb-4">
      <div class="card-header py-2">
        <h6 class="ms-1 font-weight-bold text-primary">
          <i class="fas fa-cog mr-2"></i>Inventory Master Data Configuration
        </h6>
      </div>

      <div class="card-body text-start">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-warning mb-3" role="status"
            style="width: 3rem; height: 3rem; border-width: 0.25em;">
            <span class="sr-only">Loading...</span>
          </div>
          <p class="text-muted mb-0">Verifying status...</p>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          <i class="fas fa-exclamation-triangle mr-2"></i>{{ error }}
        </div>

        <div v-else-if="!seedDone">
          <div class="alert alert-info mb-4">
            <i class="fas fa-info-circle mr-2"></i>
            <strong>Important:</strong> You can download an Excel file with inventory master data (Products, Brands,
            Categories, Units, Price Types, Warehouses, Product Prices).
            Review and adjust the data if necessary before importing it to your tenant.
          </div>

          <div class="mb-4">
            <h6 class="font-weight-bold text-primary mb-3">
              <i class="fas fa-file-excel mr-2 text-success"></i>Step 1: Download Excel File (.xlsx)
            </h6>
            <p class="text-muted small mb-3">
              Download a real Excel file (.xlsx) containing the inventory master data (Products, Brands, Categories,
              Units, Price Types, Warehouses, Product Prices) from the <code>masters_inventory.json</code> fixture file.
              The Excel file is organized in tabs by model for easy review offline.
            </p>
            <button class="btn btn-success" @click="downloadExcel" :disabled="downloading">
              <span v-if="downloading" class="spinner-border spinner-border-sm me-1" role="status"
                aria-hidden="true"></span>
              <i v-else class="fas fa-download mr-1"></i>
              <span v-if="downloading">Downloading...</span>
              <span v-else>Download Master Data Excel</span>
            </button>
          </div>

          <div class="border-top pt-4">
            <h6 class="font-weight-bold text-primary mb-3">
              <i class="fas fa-upload mr-2 text-primary"></i>Step 2: Import Data
            </h6>
            <p class="text-muted small mb-3">
              After reviewing the Excel file offline (using Microsoft Excel or similar), you can import the master data
              to your tenant.
              <strong>Note:</strong> The import will be performed from the system's JSON fixture file
              (<code>masters_inventory.json</code>), not from the downloaded Excel file. The Excel file is provided for
              your review only.
            </p>

            <div class="form-check form-switch mb-3 d-flex align-items-center gap-2">
              <input class="form-check-input" type="checkbox" id="confirmImport" v-model="confirmCheck" role="switch" />
              <label class="form-check-label mb-0" for="confirmImport">
                <strong>I confirm: Import masters into my tenant</strong>
              </label>
            </div>

            <div class="d-flex flex-column flex-sm-row justify-content-center align-items-center gap-2">
              <button class="btn btn-primary" @click="importMasterData" :disabled="!confirmCheck || importing">
                <span v-if="importing" class="spinner-border spinner-border-sm me-1" role="status"
                  aria-hidden="true"></span>
                <i v-else class="fas fa-upload mr-1"></i>
                <span v-if="importing">Importing...</span>
                <span v-else>Import Master Data</span>
              </button>

              <button type="button" class="btn btn-secondary" @click="goBack" :disabled="importing">Cancel</button>
            </div>
          </div>
        </div>

        <div v-else class="alert alert-success mb-0">
          <i class="fas fa-check-circle mr-2"></i>
          <strong>Inventory masters imported.</strong>
          <p class="mb-0 mt-2">The inventory master data has been successfully imported to this tenant. Import cannot be
            performed more than once.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import axios from 'axios';
import Swal from 'sweetalert2';

export default defineComponent({
  name: 'InventoryMasterDataSetup',
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
        const token = localStorage.getItem('authToken');
        const response = await axios.get('/api/master-data/preview/', {
          headers: {
            Authorization: `Token ${token}`,
          },
        });
        this.seedDone = response.data.seed_done || false;
      } catch (error) {
        console.error('Error loading preview:', error);
        if (error.response?.status === 403) {
          this.seedDone = true;
        } else {
          this.error = error.response?.data?.error || 'Error verifying master data status.';
        }
      } finally {
        this.loading = false;
      }
    },
    async downloadExcel() {
      try {
        this.downloading = true;
        const token = localStorage.getItem('authToken');
        const response = await axios.get('/api/master-data/download-excel/', {
          headers: {
            Authorization: `Token ${token}`,
          },
          responseType: 'blob',
        });

        // Create temporary link to download file
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        const contentDisposition = response.headers['content-disposition'];
        let filename = 'masters_inventory.xlsx';
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        Swal.fire({
          icon: 'success',
          title: 'Download Successful',
          text: 'The Excel file has been downloaded successfully.',
        });
      } catch (error) {
        console.error('Error downloading Excel:', error);
        Swal.fire({
          icon: 'error',
          title: 'Download Error',
          text: error.response?.data?.error || 'An error occurred while downloading the Excel file.',
        });
      } finally {
        this.downloading = false;
      }
    },
    async importMasterData() {
      if (!this.confirmCheck) {
        Swal.fire({
          icon: 'warning',
          title: 'Confirmation Required',
          text: 'You must confirm the import before continuing.',
        });
        return;
      }

      try {
        this.importing = true;
        const token = localStorage.getItem('authToken');
        const response = await axios.post(
          '/api/master-data/import/',
          { confirm: true },
          {
            headers: {
              Authorization: `Token ${token}`,
            },
          }
        );

        if (response.data.success) {
          Swal.fire({
            icon: 'success',
            title: 'Import Successful!',
            text: response.data.message || 'The inventory master data has been imported successfully.',
          });
          this.seedDone = true;
          this.confirmCheck = false;
        }
      } catch (error) {
        console.error('Error importing master data:', error);
        Swal.fire({
          icon: 'error',
          title: 'Import Error',
          text: error.response?.data?.error || 'An error occurred while importing the master data.',
        });
      } finally {
        this.importing = false;
      }
    },
    goBack() {
      if (this.$router && this.$route.name) {
        this.$router.back();
      } else {
        this.$router.push('/');
      }
    },
  },
});
</script>

<style scoped>
.form-check-input:checked {
  background-color: #ffc107;
  border-color: #ffc107;
}

.form-check-input:checked:focus {
  background-color: #ffc107;
  border-color: #ffc107;
  box-shadow: 0 0 0 0.25rem rgba(255, 193, 7, 0.25);
}

.text-warning {
  color: #ffc107 !important;
}
</style>
