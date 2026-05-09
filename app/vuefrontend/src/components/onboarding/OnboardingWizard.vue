<template>
  <div class="onboarding-wizard">
    <div class="wizard-container">
      <header class="onboarding-hero text-center mb-4">
        <h1 class="h3 fw-bold mb-2">Start your 30-day free trial</h1>
        <p class="text-muted mb-2 mb-md-3 onboarding-hero-lead">
          Set up your workspace and start tracking jobs, materials, crews, and field communication in one place—so you lose less money to disconnected scheduling, missing materials, and broken handoffs.
        </p>
        <p class="small text-muted mb-1 onboarding-hero-lead">
          Your trial includes all core modules so your team can experience the full workflow. Full access during trial. You can choose your plan later.
        </p>
      </header>

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
              <StepPreferences v-if="currentStep === 3" :errors="stepErrors.preferences" />

              <!-- Step 4: Review -->
              <StepReview v-if="currentStep === 4" :company-info="formData.companyInfo" :admin-user="formData.adminUser"
                :preferences="formData.preferences" :recommended-plan="recommendedPlan"
                :landing-selected-plan="landingSelectedPlan" :is-submitting="isSubmitting"
                :error-message="submitError" @submit="handleFinalSubmit" @go-back="goToPreviousStep" />
            </div>
          </transition>

          <!-- Navigation Buttons -->
          <div v-if="currentStep < 4" class="wizard-actions mt-5 pt-4 border-top">
            <div class="d-flex justify-content-between">
              <button v-if="currentStep > 1" type="button" class="btn btn-outline-secondary" @click="goToPreviousStep"
                :disabled="isSubmitting">
                <i class="fas fa-arrow-left me-2"></i>
                Back
              </button>
              <div v-else></div>

              <button type="button" class="btn btn-primary" @click="goToNextStep"
                :disabled="isSubmitting || !canProceed">
                Continue
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
import { useRouter, useRoute } from 'vue-router'
import StepCompanyInfo from './StepCompanyInfo.vue'
import StepAdminUser from './StepAdminUser.vue'
import StepPreferences from './StepPreferences.vue'
import StepReview from './StepReview.vue'
import { createTenantWorkspace } from '@/api/onboarding'
import { normalizeLandingPlan } from './planFromQuery.js'
import {
  defaultOnboardingPreferences,
  normalizeStoredPreferences,
  ONBOARDING_MODULE_IDS,
} from './onboardingModuleDefaults.js'

const router = useRouter()
const route = useRoute()

const steps = [
  { number: 1, label: 'Company' },
  { number: 2, label: 'Admin' },
  { number: 3, label: 'Modules' },
  { number: 4, label: 'Review' }
]

/** Plan from landing URL (?plan=), persisted on tenant as landing_selected_plan */
const landingSelectedPlan = ref(null)

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
  preferences: defaultOnboardingPreferences(),
})

// Errors for each step
const stepErrors = reactive({
  companyInfo: {},
  adminUser: {},
  preferences: {}
})

// Load from localStorage on mount; honor ?plan= from marketing site
onMounted(() => {
  landingSelectedPlan.value = normalizeLandingPlan(route.query.plan)
  loadFromLocalStorage()

  watch(() => formData, () => {
    saveToLocalStorage()
  }, { deep: true })

  watch(() => route.query.plan, (q) => {
    landingSelectedPlan.value = normalizeLandingPlan(q)
  })
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

// Validation (silent getters avoid flashing errors on every keystroke via computed side effects)
const getStep1Errors = () => {
  const errors = {}
  const bn = formData.companyInfo.business_name?.trim() || ''
  if (!bn || bn.length < 3) {
    errors.business_name = 'Enter your company name (at least 3 characters).'
  }

  if (!formData.companyInfo.business_type) {
    errors.business_type = 'Choose the trade that best describes your business.'
  }

  if (!formData.companyInfo.monthly_operations) {
    errors.monthly_operations = 'Select how many jobs or homes you typically handle each month.'
  }

  const rawCrew = formData.companyInfo.crew_count
  const crewParsed =
    rawCrew === '' || rawCrew === null || rawCrew === undefined ? null : Number(rawCrew)
  if (crewParsed === null || Number.isNaN(crewParsed)) {
    errors.crew_count = 'Enter how many crews you run (whole number, at least 1).'
  } else if (!Number.isInteger(crewParsed)) {
    errors.crew_count = 'Use a whole number for active crews.'
  } else if (crewParsed < 1) {
    errors.crew_count = 'Enter at least 1 active crew.'
  }

  if (formData.companyInfo.logo) {
    const maxSize = 5 * 1024 * 1024
    if (formData.companyInfo.logo.size > maxSize) {
      errors.logo = 'Logo must be 5MB or smaller.'
    }
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif']
    if (!allowedTypes.includes(formData.companyInfo.logo.type)) {
      errors.logo = 'Use a PNG, JPG, or GIF image.'
    }
  }

  return errors
}

const validateStep1 = () => {
  const errors = getStep1Errors()
  stepErrors.companyInfo = errors
  return Object.keys(errors).length === 0
}

const getStep2Errors = () => {
  const errors = {}
  const name = formData.adminUser.name?.trim() || ''
  if (!name || name.length < 2) {
    errors.name = 'Enter your full name (at least 2 characters).'
  }

  const email = (formData.adminUser.email || '').trim()
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email) {
    errors.email = 'Enter your work email address.'
  } else if (!emailRegex.test(email)) {
    errors.email = 'That does not look like a valid email address. Check for typos.'
  }

  const pwd = formData.adminUser.password || ''
  if (!pwd || pwd.length < 8) {
    errors.password = 'Use at least 8 characters.'
  } else {
    const hasUpperCase = /[A-Z]/.test(pwd)
    const hasLowerCase = /[a-z]/.test(pwd)
    const hasNumber = /[0-9]/.test(pwd)
    if (!hasUpperCase || !hasLowerCase || !hasNumber) {
      errors.password = 'Include uppercase, lowercase, and a number.'
    }
  }

  const pwd2 = formData.adminUser.password_confirm || ''
  if (!pwd2) {
    errors.password_confirm = 'Confirm your password.'
  } else if (pwd !== pwd2) {
    errors.password_confirm = 'Passwords do not match—try again.'
  }

  return errors
}

const validateStep2 = () => {
  const errors = getStep2Errors()
  stepErrors.adminUser = errors
  return Object.keys(errors).length === 0
}

const getStep3Errors = () => {
  const errors = {}
  const p = formData.preferences || []
  const missing = ONBOARDING_MODULE_IDS.some((id) => !p.includes(id))
  if (!p.length || p.length !== ONBOARDING_MODULE_IDS.length || missing) {
    errors.preferences =
      'Module list is incomplete. Refresh the page to continue—all trial modules should be listed.'
  }
  return errors
}

const validateStep3 = () => {
  const errors = getStep3Errors()
  stepErrors.preferences = errors
  return Object.keys(errors).length === 0
}

const canProceed = computed(() => {
  if (currentStep.value === 1) return Object.keys(getStep1Errors()).length === 0
  if (currentStep.value === 2) return Object.keys(getStep2Errors()).length === 0
  if (currentStep.value === 3) return Object.keys(getStep3Errors()).length === 0
  return true
})

const goToNextStep = () => {
  let ok = true
  if (currentStep.value === 1) ok = validateStep1()
  else if (currentStep.value === 2) ok = validateStep2()
  else if (currentStep.value === 3) ok = validateStep3()
  if (!ok) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }
  if (currentStep.value < steps.length) {
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
        if (data.formData.preferences != null) {
          formData.preferences = normalizeStoredPreferences(data.formData.preferences)
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
    submitError.value = 'Please fix the highlighted fields before continuing.'
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
    formData.preferences = normalizeStoredPreferences(formData.preferences)
    const payload = {
      business_name: formData.companyInfo.business_name.trim(),
      business_type: formData.companyInfo.business_type,
      logo: formData.companyInfo.logo,
      address: formData.companyInfo.address,
      monthly_operations: formData.companyInfo.monthly_operations,
      crew_count: formData.companyInfo.crew_count,
      recommended_plan: recommendedPlan.value,
      landing_selected_plan: landingSelectedPlan.value,
      admin: {
        name: formData.adminUser.name.trim(),
        email: formData.adminUser.email.trim(),
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
    submitError.value = error.message || 'We could not create your workspace. Please try again in a moment.'
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

.onboarding-hero h1 {
  color: var(--bs-dark);
}

/* Match hero copy width to wizard column (same as .wizard-container max-width) */
.onboarding-hero-lead {
  width: 100%;
  max-width: 100%;
  margin-left: auto;
  margin-right: auto;
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
