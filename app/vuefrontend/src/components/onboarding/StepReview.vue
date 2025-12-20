<template>
  <div class="step-review">
    <div class="step-header mb-4">
      <h3 class="fw-bold mb-2">Review & Create</h3>
      <p class="text-muted mb-0">Review the information before creating your workspace</p>
    </div>

    <div class="step-content">
      <div class="review-card card shadow-sm mb-4">
        <div class="card-header bg-primary text-white">
          <h5 class="mb-0">
            <i class="fas fa-building me-2"></i>
            Company Information
          </h5>
        </div>
        <div class="card-body">
          <div class="row mb-2">
            <div class="col-sm-4 fw-semibold text-muted review-label">Business Name:</div>
            <div class="col-sm-8 review-value">{{ companyInfo.business_name }}</div>
          </div>
          <div class="row mb-2">
            <div class="col-sm-4 fw-semibold text-muted review-label">Business Type:</div>
            <div class="col-sm-8 review-value">{{ getBusinessTypeLabel(companyInfo.business_type) }}</div>
          </div>
          <div v-if="companyInfo.address" class="row mb-2">
            <div class="col-sm-4 fw-semibold text-muted review-label">Address:</div>
            <div class="col-sm-8 review-value">{{ companyInfo.address }}</div>
          </div>
          <div class="row mb-2">
            <div class="col-sm-4 fw-semibold text-muted review-label">Monthly Operations:</div>
            <div class="col-sm-8 review-value">{{ getMonthlyOperationsLabel(companyInfo.monthly_operations) }}</div>
          </div>
          <div class="row mb-2">
            <div class="col-sm-4 fw-semibold text-muted review-label">Active Crews:</div>
            <div class="col-sm-8 review-value">{{ companyInfo.crew_count || 'Not specified' }}</div>
          </div>
          <div v-if="companyInfo.logo" class="row">
            <div class="col-sm-4 fw-semibold text-muted review-label">Logo:</div>
            <div class="col-sm-8 review-value">
              <img
                :src="logoPreview"
                alt="Company logo"
                class="review-logo"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Recommended Plan Card -->
      <div v-if="recommendedPlan" class="review-card card shadow-sm mb-4 border-warning">
        <div class="card-header bg-warning text-dark">
          <h5 class="mb-0">
            <i class="fas fa-star me-2"></i>
            Recommended Plan
          </h5>
        </div>
        <div class="card-body">
          <div class="d-flex align-items-center">
            <div class="flex-grow-1">
              <p class="mb-0 fw-semibold">
                Recommended plan for your company: <span class="text-primary fs-5">{{ recommendedPlan }}</span>
              </p>
              <small class="text-muted">Based on your number of active crews</small>
            </div>
            <div class="ms-3">
              <i class="fas fa-check-circle fa-2x text-success"></i>
            </div>
          </div>
        </div>
      </div>

      <div class="review-card card shadow-sm mb-4">
        <div class="card-header bg-success text-white">
          <h5 class="mb-0">
            <i class="fas fa-user-shield me-2"></i>
            Administrator User
          </h5>
        </div>
        <div class="card-body">
          <div class="row mb-2">
            <div class="col-sm-4 fw-semibold text-muted review-label">Name:</div>
            <div class="col-sm-8 review-value">{{ adminUser.name }}</div>
          </div>
          <div class="row mb-2">
            <div class="col-sm-4 fw-semibold text-muted review-label">Email:</div>
            <div class="col-sm-8 review-value">{{ adminUser.email }}</div>
          </div>
          <div class="row">
            <div class="col-sm-4 fw-semibold text-muted review-label">Password:</div>
            <div class="col-sm-8 review-value">
              <span class="text-muted">••••••••</span>
              <small class="ms-2 text-muted">(Hidden for security)</small>
            </div>
          </div>
        </div>
      </div>

      <div class="review-card card shadow-sm mb-4">
        <div class="card-header bg-info text-white">
          <h5 class="mb-0">
            <i class="fas fa-cogs me-2"></i>
            Selected Modules
          </h5>
        </div>
        <div class="card-body">
          <div v-if="preferences.length === 0" class="text-muted text-center py-3">
            <i class="fas fa-info-circle me-2"></i>
            No modules selected
          </div>
          <div v-else class="row g-2">
            <div
              v-for="pref in preferences"
              :key="pref"
              class="col-md-6"
            >
              <div class="badge bg-primary p-2 w-100 text-start">
                <i :class="getModuleIcon(pref)" class="me-2"></i>
                {{ getModuleLabel(pref) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="errorMessage" class="alert alert-danger" role="alert">
        <i class="fas fa-exclamation-triangle me-2"></i>
        {{ errorMessage }}
      </div>

      <div class="wizard-actions mt-5 pt-4 border-top">
        <div class="d-flex justify-content-between">
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="handleGoBack"
            :disabled="isSubmitting"
          >
            <i class="fas fa-arrow-left me-2"></i>
            Previous
          </button>

          <button
            type="button"
            class="btn btn-primary btn-lg px-5"
            :disabled="isSubmitting"
            @click="handleSubmit"
          >
            <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            <i v-else class="fas fa-rocket me-2"></i>
            <span v-if="isSubmitting">Creating Workspace...</span>
            <span v-else>Create Tenant Workspace</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  companyInfo: {
    type: Object,
    required: true
  },
  adminUser: {
    type: Object,
    required: true
  },
  preferences: {
    type: Array,
    default: () => []
  },
  recommendedPlan: {
    type: String,
    default: null
  },
  isSubmitting: {
    type: Boolean,
    default: false
  },
  errorMessage: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['submit', 'go-back'])

const logoPreview = ref(null)

// Create logo preview if logo exists
if (props.companyInfo.logo) {
  const reader = new FileReader()
  reader.onload = (e) => {
    logoPreview.value = e.target.result
  }
  reader.readAsDataURL(props.companyInfo.logo)
}

const businessTypeLabels = {
  electric: 'Electric',
  air_conditioning: 'Air Conditioning',
  solar: 'Solar',
  plumbing: 'Plumbing',
  hvac: 'HVAC (Heating, Ventilation, Air Conditioning)',
  general: 'General (Other)'
}

const getBusinessTypeLabel = (value) => {
  return businessTypeLabels[value] || value
}

const monthlyOperationsLabels = {
  '0-10': '0–10 homes per month',
  '11-25': '11–25 homes per month',
  '26-50': '26–50 homes per month',
  '51-100': '51–100 homes per month',
  '100+': '100+ homes per month'
}

const getMonthlyOperationsLabel = (value) => {
  return monthlyOperationsLabels[value] || value || 'Not specified'
}

const moduleLabels = {
  inventory: 'Inventory',
  contracts: 'Contracts',
  schedule: 'Schedule',
  crews: 'Crews',
  notes: 'Notes'
}

const moduleIcons = {
  inventory: 'fas fa-boxes',
  contracts: 'fas fa-file-contract',
  schedule: 'fas fa-calendar-alt',
  crews: 'fas fa-users',
  notes: 'fas fa-sticky-note'
}

const getModuleLabel = (id) => {
  return moduleLabels[id] || id
}

const getModuleIcon = (id) => {
  return moduleIcons[id] || 'fas fa-circle'
}

const handleSubmit = () => {
  emit('submit')
}

const handleGoBack = () => {
  emit('go-back')
}
</script>

<style scoped>
.step-header {
  text-align: center;
}

.step-header h3 {
  color: var(--bs-dark);
  font-size: 1.75rem;
}

.step-content {
  max-width: 800px;
  margin: 0 auto;
}

.review-card {
  border-radius: 0.5rem;
  overflow: hidden;
}

.review-card .card-header {
  border: none;
  padding: 1rem 1.5rem;
}

.review-card .card-body {
  padding: 1.5rem;
}

.review-label {
  font-size: 0.9rem;
  letter-spacing: 0.01em;
  opacity: 0.85;
  padding-right: 1rem;
}

.review-value {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--bs-dark);
  word-break: break-word;
}

.review-logo {
  max-width: 150px;
  max-height: 150px;
  object-fit: contain;
  border-radius: 0.5rem;
  border: 2px solid var(--bs-border-color);
  padding: 0.5rem;
}

.step-review .btn-lg {
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
}

.step-review .btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--bs-primary-rgb), 0.4);
  transition: all 0.2s ease;
}

/* Recommended Plan Card Styles */
.review-card.border-warning {
  border-width: 2px !important;
  border-color: var(--bs-warning) !important;
}

.review-card.border-warning .card-header {
  background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%) !important;
  color: #000 !important;
  font-weight: 600;
}

.review-card.border-warning .card-body {
  background-color: rgba(255, 193, 7, 0.05);
}
</style>

