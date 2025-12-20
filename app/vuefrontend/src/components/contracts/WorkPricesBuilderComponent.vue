<template>
  <div class="container">
    <h3 class="pt-3">
      <p>Assign Work Prices per Builder</p>
    </h3>
    <div class="card shadow mb-4">
      <div class="card-header py-2">
        <h6 class="m-0 font-weight-bold text-primary">Manage Work Prices</h6>
      </div>
      <div class="card-body">
        <!-- Builder Selection Row -->
        <div class="row align-items-center mb-3">
          <!-- Label -->
          <div class="col-auto">
            <label for="builder" class="form-label mb-0">Select Builder:</label>
          </div>
          <!-- Input -->
          <div class="col">
            <v-select
              v-model="selectedBuilder"
              :options="builders"
              label="name"
              placeholder="Search Builder"
              @update:modelValue="fetchWorkPrices"
            />
          </div>
        </div>

        <div v-if="loading" class="loading">Loading work prices...</div>

        <!-- Work Prices List -->
        <div v-if="selectedBuilder && !loading">
          <h4 class="mb-3 text-black text-start">Work Prices</h4>

          <!-- Buttons -->
          <div class="row mb-3 text-start">
            <div class="col-lg-6 ms-3">
              <div class="btn-group" role="group">
                <button type="button" class="btn btn-sm btn-outline-primary" @click="selectAll">Select All</button>
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="clearAll">Deselect All</button>
              </div>
            </div>
          </div>

          <!-- Work Price Checkboxes -->
          <div class="row px-3 text-start">
            <div class="form-check form-switch col-xl-3 col-md-4 col-sm-6" v-for="workPrice in workPrices" :key="workPrice.id">
              <input class="form-check-input" type="checkbox" role="switch" :value="workPrice.id" v-model="selectedWorkPrices" />
              <label class="form-check-label">{{ workPrice.name }}</label>
            </div>
          </div>

          <!-- Save Button -->
          <div class="row mt-4">
            <div class="col">
              <button class="btn btn-primary" @click="updateWorkPriceAssignments">Save</button>
            </div>
          </div>
        </div>

        <div v-if="errorMessage" class="error mt-3">{{ errorMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Swal from "sweetalert2";
import VSelect from "vue-select";
import "vue-select/dist/vue-select.css";

export default {
  components: { VSelect },
  data() {
    return {
      builders: [],
      selectedBuilder: null,
      workPrices: [],
      selectedWorkPrices: [],
      loading: false,
      errorMessage: "",
    };
  },
  mounted() {
    this.fetchBuilders();
  },
  methods: {
    async fetchBuilders() {
      try {
        const response = await axios.get("/api/builder/");
        this.builders = response.data;
        console.log("Builders loaded:", this.builders);

        // Check if there is a builder ID in the URL and auto-select it
        const urlParams = new URLSearchParams(window.location.search);
        const builderId = urlParams.get("builder");
        if (builderId) {
          this.selectedBuilder = this.builders.find(builder => builder.id === parseInt(builderId));
          if (this.selectedBuilder) {
            this.fetchWorkPrices();
          }
        }
      } catch (error) {
        this.errorMessage = "Failed to load builders.";
        console.error("Error fetching builders:", error);
      }
    },
    async fetchWorkPrices() {
      if (!this.selectedBuilder) return;
      this.loading = true;
      try {
        const response = await axios.get(`/api/workprice/`);
        this.workPrices = response.data;

        const assignedResponse = await axios.get(`/api/builder/${this.selectedBuilder.id}/workprices/`);
        this.selectedWorkPrices = assignedResponse.data.map(wp => wp.id);
      } catch (error) {
        this.errorMessage = "Error loading work prices.";
        console.error("Error fetching work prices:", error);
      } finally {
        this.loading = false;
      }
    },
    async updateWorkPriceAssignments() {
      if (!this.selectedBuilder) return;

      try {
        await axios.post(`/api/builder/${this.selectedBuilder.id}/assign-workprices/`, {
          work_price_ids: this.selectedWorkPrices
        });

        // SweetAlert success message
        Swal.fire({
          icon: "success",
          title: "Success",
          text: "Assignments updated successfully!",
          confirmButtonText: "OK"
        });
      } catch (error) {
        this.errorMessage = "Error updating assignments.";
        console.error("Error updating assignments:", error);
      }
    },
    selectAll() {
      this.selectedWorkPrices = this.workPrices.map(wp => wp.id);
    },
    clearAll() {
      this.selectedWorkPrices = [];
    }
  }
};
</script>

<style>
.checkbox-container {
  display: flex;
  align-items: center;
  gap: 5px;
}

.loading {
  font-size: 14px;
  color: gray;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
