<template>
  <div class="onboarding-wizard">
    <div class="wizard-container">
      <!-- Progress Bar -->
      <div class="progress-container mb-4">
        <div class="progress" style="height: 8px;">
          <div class="progress-bar bg-primary" role="progressbar" :style="{ width: progressPercentage + '%' }"
            :aria-valuenow="currentStep" aria-valuemin="1" aria-valuemax="4"></div>
        </div>
        <div class="step-indicators d-flex justify-content-between mt-3">
          <div v-for="step in steps" :key="step.number" class="step-indicator"
            :class="{ 'active': step.number === currentStep, 'completed': step.number < currentStep }">
            <div class="step-number">
              <span v-if="step.number < currentStep" class="check-icon">
                <i class="fas fa-check"></i>
              </span>
              <span v-else>{{ step.number }}</span>
            </div>
            <div class="step-label d-none d-md-block">{{ step.label }}</div>
          </div>
        </div>
      </div>

      <!-- Wizard Card -->
      <div class="wizard-card card shadow-lg">
        <div class="card-body p-5">
          <!-- Step Content with Transitions -->
          <transition name="fade-slide" mode="out-in">
            <div :key="currentStep">
              <!-- Step 1: Company Information -->
              <StepCompanyInfo v-if="currentStep === 1" v-model="formData.companyInfo" :errors="stepErrors.companyInfo"
                @validate="validateStep1" />

              <!-- Step 2: Admin User -->
              <StepAdminUser v-if="currentStep === 2" v-model="formData.adminUser" :errors="stepErrors.adminUser"
                @validate="validateStep2" />

              <!-- Step 3: Preferences -->
              <StepPreferences v-if="currentStep === 3" v-model="formData.preferences"
                :errors="stepErrors.preferences" />

              <!-- Step 4: Review -->
              <StepReview v-if="currentStep === 4" :company-info="formData.companyInfo" :admin-user="formData.adminUser"
                :preferences="formData.preferences" :recommended-plan="recommendedPlan" :is-submitting="isSubmitting"
                :error-message="submitError" @submit="handleFinalSubmit" @go-back="goToPreviousStep" />
            </div>
          </transition>

          <!-- Navigation Buttons -->
          <div v-if="currentStep < 4" class="wizard-actions mt-5 pt-4 border-top">
            <div class="d-flex justify-content-between">
              <button v-if="currentStep > 1" type="button" class="btn btn-outline-secondary" @click="goToPreviousStep"
                :disabled="isSubmitting">
                <i class="fas fa-arrow-left me-2"></i>
                Previous
              </button>
              <div v-else></div>

              <button type="button" class="btn btn-primary" @click="goToNextStep"
                :disabled="isSubmitting || !canProceed">
                Next
                <i class="fas fa-arrow-right ms-2"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import StepCompanyInfo from './StepCompanyInfo.vue'
import StepAdminUser from './StepAdminUser.vue'
import StepPreferences from './StepPreferences.vue'
import StepReview from './StepReview.vue'
import { createTenantWorkspace } from '@/api/onboarding'

const router = useRouter()

const steps = [
  { number: 1, label: 'Company' },
  { number: 2, label: 'Admin' },
  { number: 3, label: 'Preferences' },
  { number: 4, label: 'Review' }
]

const currentStep = ref(1)
const isSubmitting = ref(false)
const submitError = ref('')

// Form data structure
const formData = reactive({
  companyInfo: {
    business_name: '',
    business_type: '',
    logo: null,
    address: '',
    monthly_operations: '',
    crew_count: null
  },
  adminUser: {
    name: '',
    email: '',
    password: '',
    password_confirm: ''
  },
  preferences: ['inventory', 'contracts', 'schedule', 'crews', 'notes']
})

// Errors for each step
const stepErrors = reactive({
  companyInfo: {},
  adminUser: {},
  preferences: {}
})

// Load from localStorage on mount
onMounted(() => {
  loadFromLocalStorage()

  // Auto-save on changes
  watch(() => formData, (newData) => {
    saveToLocalStorage()
  }, { deep: true })
})

// Calculate recommended plan based on crew_count
const recommendedPlan = computed(() => {
  const crewCount = formData.companyInfo.crew_count
  if (!crewCount || crewCount < 1) return null

  if (crewCount <= 3) {
    return 'Starter'
  } else if (crewCount >= 4 && crewCount <= 8) {
    return 'Professional'
  } else if (crewCount >= 9) {
    return 'Enterprise'
  }
  return null
})

// Progress calculation
const progressPercentage = computed(() => {
  return (currentStep.value / steps.length) * 100
})

// Validation for each step
const validateStep1 = () => {
  const errors = {}

  if (!formData.companyInfo.business_name || formData.companyInfo.business_name.trim().length < 3) {
    errors.business_name = 'Business name must be at least 3 characters long'
  }

  if (!formData.companyInfo.business_type) {
    errors.business_type = 'Please select a business type'
  }

  if (!formData.companyInfo.monthly_operations) {
    errors.monthly_operations = 'Please select monthly operations volume'
  }

  if (!formData.companyInfo.crew_count || formData.companyInfo.crew_count < 1) {
    errors.crew_count = 'Please enter a valid number of active crews (minimum 1)'
  } else if (!Number.isInteger(formData.companyInfo.crew_count)) {
    errors.crew_count = 'Number of crews must be a whole number'
  }

  if (formData.companyInfo.logo) {
    const maxSize = 5 * 1024 * 1024 // 5MB
    if (formData.companyInfo.logo.size > maxSize) {
      errors.logo = 'Logo must not exceed 5MB'
    }

    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif']
    if (!allowedTypes.includes(formData.companyInfo.logo.type)) {
      errors.logo = 'Logo must be an image (PNG, JPG, GIF)'
    }
  }

  stepErrors.companyInfo = errors
  return Object.keys(errors).length === 0
}

const validateStep2 = () => {
  const errors = {}

  if (!formData.adminUser.name || formData.adminUser.name.trim().length < 2) {
    errors.name = 'Name must be at least 2 characters long'
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!formData.adminUser.email || !emailRegex.test(formData.adminUser.email)) {
    errors.email = 'Please enter a valid email address'
  }

  if (!formData.adminUser.password || formData.adminUser.password.length < 8) {
    errors.password = 'Password must be at least 8 characters long'
  } else {
    // Check password strength
    const hasUpperCase = /[A-Z]/.test(formData.adminUser.password)
    const hasLowerCase = /[a-z]/.test(formData.adminUser.password)
    const hasNumber = /[0-9]/.test(formData.adminUser.password)

    if (!hasUpperCase || !hasLowerCase || !hasNumber) {
      errors.password = 'Password must contain uppercase letters, lowercase letters, and numbers'
    }
  }

  if (formData.adminUser.password !== formData.adminUser.password_confirm) {
    errors.password_confirm = 'Passwords do not match'
  }

  stepErrors.adminUser = errors
  return Object.keys(errors).length === 0
}

const validateStep3 = () => {
  const errors = {}

  if (!formData.preferences || formData.preferences.length === 0) {
    errors.preferences = 'Please select at least one module'
  }

  stepErrors.preferences = errors
  return Object.keys(errors).length === 0
}

// Can proceed to next step
const canProceed = computed(() => {
  if (currentStep.value === 1) {
    return validateStep1()
  } else if (currentStep.value === 2) {
    return validateStep2()
  } else if (currentStep.value === 3) {
    return validateStep3()
  }
  return true
})

// Navigation
const goToNextStep = () => {
  if (canProceed.value && currentStep.value < steps.length) {
    currentStep.value++
    saveToLocalStorage()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const goToPreviousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
    saveToLocalStorage()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// LocalStorage management
const saveToLocalStorage = () => {
  try {
    const dataToSave = {
      currentStep: currentStep.value,
      formData: {
        companyInfo: {
          ...formData.companyInfo,
          logo: null // Don't save file to localStorage
        },
        adminUser: {
          ...formData.adminUser,
          password: '', // Don't save password
          password_confirm: ''
        },
        preferences: formData.preferences
      }
    }
    localStorage.setItem('onboarding_progress', JSON.stringify(dataToSave))
  } catch (error) {
    console.warn('Could not save onboarding progress:', error)
  }
}

const loadFromLocalStorage = () => {
  try {
    const saved = localStorage.getItem('onboarding_progress')
    if (saved) {
      const data = JSON.parse(saved)
      currentStep.value = data.currentStep || 1

      if (data.formData) {
        if (data.formData.companyInfo) {
          Object.assign(formData.companyInfo, data.formData.companyInfo)
        }
        if (data.formData.adminUser) {
          Object.assign(formData.adminUser, {
            ...data.formData.adminUser,
            password: '',
            password_confirm: ''
          })
        }
        if (data.formData.preferences) {
          formData.preferences = data.formData.preferences
        }
      }
    }
  } catch (error) {
    console.warn('Could not load onboarding progress:', error)
  }
}

// Final submit
const handleFinalSubmit = async () => {
  // Validate all steps before submitting
  if (!validateStep1() || !validateStep2() || !validateStep3()) {
    submitError.value = 'Please complete all required fields'
    // Go to first step with errors
    if (!validateStep1()) {
      currentStep.value = 1
    } else if (!validateStep2()) {
      currentStep.value = 2
    } else if (!validateStep3()) {
      currentStep.value = 3
    }
    return
  }

  isSubmitting.value = true
  submitError.value = ''

  try {
    const payload = {
      business_name: formData.companyInfo.business_name,
      business_type: formData.companyInfo.business_type,
      logo: formData.companyInfo.logo,
      address: formData.companyInfo.address,
      monthly_operations: formData.companyInfo.monthly_operations,
      crew_count: formData.companyInfo.crew_count,
      recommended_plan: recommendedPlan.value,
      admin: {
        name: formData.adminUser.name,
        email: formData.adminUser.email,
        password: formData.adminUser.password
      },
      preferences: formData.preferences
    }

    const response = await createTenantWorkspace(payload)

    // Clear localStorage on success
    localStorage.removeItem('onboarding_progress')

    // Redirect based on response
    if (response.url) {
      window.location.href = response.url
    } else if (response.tenant && response.tenant.domain) {
      const protocol = window.location.protocol
      window.location.href = `${protocol}//${response.tenant.domain}/login/`
    } else {
      // Fallback: redirect to login
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    }
  } catch (error) {
    console.error('Error creating tenant:', error)
    submitError.value = error.message || 'Error creating workspace. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.onboarding-wizard {
  min-height: 100vh;
  padding: 2rem 1rem;
}

.wizard-container {
  max-width: 1000px;
  margin: 0 auto;
}

.progress-container {
  margin-bottom: 2rem;
}

.step-indicators {
  margin-top: 1rem;
}

.step-indicator {
  flex: 1;
  text-align: center;
  position: relative;
}

.step-indicator::before {
  content: '';
  position: absolute;
  top: 15px;
  left: 50%;
  width: 100%;
  height: 2px;
  background-color: var(--bs-border-color);
  z-index: 0;
}

.step-indicator:first-child::before {
  display: none;
}

.step-indicator.completed::before {
  background-color: var(--bs-primary);
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--bs-light);
  border: 2px solid var(--bs-border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 0.5rem;
  font-weight: 600;
  color: var(--bs-secondary);
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

.step-indicator.active .step-number {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
  color: white;
  transform: scale(1.1);
}

.step-indicator.completed .step-number {
  background-color: var(--bs-success);
  border-color: var(--bs-success);
  color: white;
}

.check-icon {
  font-size: 0.875rem;
}

.step-label {
  font-size: 0.875rem;
  color: var(--bs-secondary);
  font-weight: 500;
}

.step-indicator.active .step-label {
  color: var(--bs-primary);
  font-weight: 600;
}

.step-indicator.completed .step-label {
  color: var(--bs-success);
}

.wizard-card {
  border-radius: 1rem;
  border: none;
  min-height: 500px;
}

.wizard-actions {
  border-top: 1px solid var(--bs-border-color);
}

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.btn-primary {
  min-width: 120px;
}

@media (max-width: 768px) {
  .onboarding-wizard {
    padding: 1rem 0.5rem;
  }

  .wizard-card .card-body {
    padding: 2rem 1.5rem !important;
  }

  .step-label {
    font-size: 0.75rem;
  }
}
</style>
