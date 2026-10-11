<template>
  <div class="jr-onboard">
    <div class="jr-onboard__form-pane">
      <header class="jr-onboard__chrome">
        <router-link
          to="/login"
          class="jr-onboard__brand"
          aria-label="JobRhythm">
          <img
            :src="brandLogoUrl"
            alt="JobRhythm"
            class="jr-onboard__brand-logo"
            width="220"
            height="56" />
        </router-link>
        <p class="jr-onboard__signin">
          Have an account?
          <router-link to="/login" class="jr-onboard__signin-link">
            Sign In
          </router-link>
        </p>
      </header>

      <div class="jr-onboard__body">
        <nav class="jr-onboard__steps" aria-label="Onboarding progress">
          <ol class="jr-onboard__step-list">
            <li
              v-for="step in steps"
              :key="step.number"
              class="jr-onboard__step"
              :class="{
                'jr-onboard__step--active': step.number === currentStep,
                'jr-onboard__step--done': step.number < currentStep,
              }">
              <span class="jr-onboard__step-marker" aria-hidden="true">
                <Check
                  v-if="step.number < currentStep"
                  class="jr-onboard__step-check" />
                <span v-else>{{ step.number }}</span>
              </span>
              <span class="jr-onboard__step-label">{{ step.label }}</span>
            </li>
          </ol>
          <div class="jr-onboard__progress" aria-hidden="true">
            <div
              class="jr-onboard__progress-fill"
              :style="{ transform: `scaleX(${progressRatio})` }" />
          </div>
        </nav>

        <div
          v-if="verificationPending"
          class="jr-onboard__verify"
          role="status">
          <h1 class="jr-onboard__title">Check your email</h1>
          <p class="jr-onboard__lead">
            We sent a confirmation link to
            <strong>{{ verificationEmail }}</strong>
            . Open it to create your workspace and start your trial.
          </p>
          <p v-if="debugVerifyUrl" class="jr-onboard__hint">
            Dev link:
            <a :href="debugVerifyUrl">{{ debugVerifyUrl }}</a>
          </p>
          <JRButton
            type="button"
            variant="secondary"
            @click="router.push('/login')">
            Go to Sign In
          </JRButton>
        </div>

        <template v-else>
          <header class="jr-onboard__intro">
            <h1 class="jr-onboard__title">{{ stepTitle }}</h1>
            <p class="jr-onboard__lead">{{ stepLead }}</p>
          </header>

          <div class="jr-onboard__panel">
            <transition name="jr-onboard-fade" mode="out-in">
              <div :key="currentStep" class="jr-onboard__step-panel">
                <StepCompanyInfo
                  v-if="currentStep === 1"
                  v-model="formData.companyInfo"
                  :errors="stepErrors.companyInfo"
                  @validate="validateStep1" />

                <StepAdminUser
                  v-if="currentStep === 2"
                  v-model="formData.adminUser"
                  :errors="stepErrors.adminUser"
                  @validate="validateStep2" />

                <StepPreferences
                  v-if="currentStep === 3"
                  :errors="stepErrors.preferences" />

                <StepReview
                  v-if="currentStep === 4"
                  :company-info="formData.companyInfo"
                  :admin-user="formData.adminUser"
                  :preferences="formData.preferences"
                  :recommended-plan="recommendedPlan"
                  :landing-selected-plan="landingSelectedPlan"
                  :is-submitting="isSubmitting"
                  :turnstile-site-key="turnstileSiteKey"
                  :error-message="submitError"
                  @submit="handleFinalSubmit"
                  @go-back="goToPreviousStep" />
              </div>
            </transition>

            <footer v-if="currentStep < 4" class="jr-onboard__actions">
              <JRButton
                v-if="currentStep > 1"
                type="button"
                variant="secondary"
                :disabled="isSubmitting"
                @click="goToPreviousStep">
                ← Back
              </JRButton>
              <span v-else class="jr-onboard__actions-spacer" />
              <JRButton
                type="button"
                variant="primary"
                :disabled="isSubmitting || !canProceed"
                @click="goToNextStep">
                Next Step →
              </JRButton>
            </footer>
          </div>
        </template>
      </div>
    </div>

    <aside class="jr-onboard__visual" aria-hidden="true">
      <img
        :src="heroImageUrl"
        alt=""
        class="jr-onboard__visual-img"
        width="900"
        height="1200" />
      <div class="jr-onboard__visual-scrim">
        <p class="jr-onboard__visual-quote">
          Run residential jobs with clear schedules, materials, and crews—in one
          workspace.
        </p>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import Check from "@primeicons/vue/check";
import { JRButton } from "@ui";
import StepCompanyInfo from "./StepCompanyInfo.vue";
import StepAdminUser from "./StepAdminUser.vue";
import StepPreferences from "./StepPreferences.vue";
import StepReview from "./StepReview.vue";
import { createTenantWorkspace, fetchOnboardingConfig } from "@/api/onboarding";
import { normalizeLandingPlan } from "./planFromQuery.js";
import {
  defaultOnboardingPreferences,
  normalizeStoredPreferences,
  ONBOARDING_MODULE_IDS,
} from "./onboardingModuleDefaults.js";
import brandLogoUrl from "@/assets/img/jobrhythm-logo-onboarding.png";
import heroImageUrl from "@/assets/img/onboarding-supervisor2.png";

const router = useRouter();
const route = useRoute();

const steps = [
  { number: 1, label: "Company" },
  { number: 2, label: "Admin" },
  { number: 3, label: "Modules" },
  { number: 4, label: "Review" },
];

const STEP_COPY = {
  1: {
    title: "Tell us about your company",
    lead: "A few details so we can size your workspace for residential trade operations in Florida and beyond.",
  },
  2: {
    title: "Create your admin account",
    lead: "This account owns settings, users, and data for your company subdomain.",
  },
  3: {
    title: "Modules for your trial",
    lead: "Your 30-day trial includes the full operational menu—so you can feel the real workflow.",
  },
  4: {
    title: "Review & launch",
    lead: "Confirm everything looks right. We email a verification link before your workspace goes live.",
  },
};

const landingSelectedPlan = ref(null);
const currentStep = ref(1);
const isSubmitting = ref(false);
const submitError = ref("");
const turnstileSiteKey = ref("");
const verificationPending = ref(false);
const verificationEmail = ref("");
const debugVerifyUrl = ref("");

const formData = reactive({
  companyInfo: {
    business_name: "",
    business_type: "",
    logo: null,
    address: "",
    monthly_operations: "",
    crew_count: null,
  },
  adminUser: {
    name: "",
    email: "",
    password: "",
    password_confirm: "",
  },
  preferences: defaultOnboardingPreferences(),
});

const stepErrors = reactive({
  companyInfo: {},
  adminUser: {},
  preferences: {},
});

onMounted(async () => {
  landingSelectedPlan.value = normalizeLandingPlan(route.query.plan);
  loadFromLocalStorage();

  try {
    const config = await fetchOnboardingConfig();
    turnstileSiteKey.value = config.turnstile_site_key || "";
  } catch (error) {
    console.warn("Could not load onboarding config:", error);
  }

  watch(
    () => formData,
    () => {
      saveToLocalStorage();
    },
    { deep: true }
  );

  watch(
    () => route.query.plan,
    (q) => {
      landingSelectedPlan.value = normalizeLandingPlan(q);
    }
  );

  watch(
    () => formData.companyInfo,
    () => {
      if (currentStep.value === 1) {
        stepErrors.companyInfo = getStep1Errors();
      }
    },
    { deep: true }
  );

  watch(
    () => formData.adminUser,
    () => {
      if (currentStep.value === 2) {
        stepErrors.adminUser = getStep2Errors();
      }
    },
    { deep: true }
  );
});

const recommendedPlan = computed(() => {
  const crewCount = formData.companyInfo.crew_count;
  if (!crewCount || crewCount < 1) return null;
  if (crewCount <= 3) return "Starter";
  if (crewCount >= 4 && crewCount <= 8) return "Professional";
  if (crewCount >= 9) return "Enterprise";
  return null;
});

const progressRatio = computed(() => currentStep.value / steps.length);

const stepTitle = computed(
  () => STEP_COPY[currentStep.value]?.title || "Start your free trial"
);
const stepLead = computed(() => STEP_COPY[currentStep.value]?.lead || "");

const getStep1Errors = () => {
  const errors = {};
  const bn = formData.companyInfo.business_name?.trim() || "";
  if (!bn || bn.length < 3) {
    errors.business_name = "Enter your company name (at least 3 characters).";
  }
  if (!formData.companyInfo.business_type) {
    errors.business_type =
      "Choose the trade that best describes your business.";
  }
  if (!formData.companyInfo.monthly_operations) {
    errors.monthly_operations =
      "Select how many jobs or homes you typically handle each month.";
  }
  const rawCrew = formData.companyInfo.crew_count;
  const crewParsed =
    rawCrew === "" || rawCrew === null || rawCrew === undefined
      ? null
      : Number(rawCrew);
  if (crewParsed === null || Number.isNaN(crewParsed)) {
    errors.crew_count =
      "Enter how many crews you run (whole number, at least 1).";
  } else if (!Number.isInteger(crewParsed)) {
    errors.crew_count = "Use a whole number for active crews.";
  } else if (crewParsed < 1) {
    errors.crew_count = "Enter at least 1 active crew.";
  }
  if (formData.companyInfo.logo) {
    const maxSize = 5 * 1024 * 1024;
    if (formData.companyInfo.logo.size > maxSize) {
      errors.logo = "Logo must be 5MB or smaller.";
    }
    const allowedTypes = ["image/png", "image/jpeg", "image/jpg", "image/gif"];
    if (!allowedTypes.includes(formData.companyInfo.logo.type)) {
      errors.logo = "Use a PNG, JPG, or GIF image.";
    }
  }
  return errors;
};

const validateStep1 = () => {
  const errors = getStep1Errors();
  stepErrors.companyInfo = errors;
  return Object.keys(errors).length === 0;
};

const getStep2Errors = () => {
  const errors = {};
  const name = formData.adminUser.name?.trim() || "";
  if (!name || name.length < 2) {
    errors.name = "Enter your full name (at least 2 characters).";
  }
  const email = (formData.adminUser.email || "").trim();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) {
    errors.email = "Enter your work email address.";
  } else if (!emailRegex.test(email)) {
    errors.email =
      "That does not look like a valid email address. Check for typos.";
  }
  const pwd = formData.adminUser.password || "";
  if (!pwd || pwd.length < 8) {
    errors.password = "Use at least 8 characters.";
  } else {
    const hasUpperCase = /[A-Z]/.test(pwd);
    const hasLowerCase = /[a-z]/.test(pwd);
    const hasNumber = /[0-9]/.test(pwd);
    if (!hasUpperCase || !hasLowerCase || !hasNumber) {
      errors.password = "Include uppercase, lowercase, and a number.";
    }
  }
  const pwd2 = formData.adminUser.password_confirm || "";
  if (!pwd2) {
    errors.password_confirm = "Confirm your password.";
  } else if (pwd !== pwd2) {
    errors.password_confirm = "Passwords do not match—try again.";
  }
  return errors;
};

const validateStep2 = () => {
  const errors = getStep2Errors();
  stepErrors.adminUser = errors;
  return Object.keys(errors).length === 0;
};

const getStep3Errors = () => {
  const errors = {};
  const p = formData.preferences || [];
  const missing = ONBOARDING_MODULE_IDS.some((id) => !p.includes(id));
  if (!p.length || p.length !== ONBOARDING_MODULE_IDS.length || missing) {
    errors.preferences =
      "Module list is incomplete. Refresh the page to continue—all trial modules should be listed.";
  }
  return errors;
};

const validateStep3 = () => {
  const errors = getStep3Errors();
  stepErrors.preferences = errors;
  return Object.keys(errors).length === 0;
};

const canProceed = computed(() => {
  if (currentStep.value === 1)
    return Object.keys(getStep1Errors()).length === 0;
  if (currentStep.value === 2)
    return Object.keys(getStep2Errors()).length === 0;
  if (currentStep.value === 3)
    return Object.keys(getStep3Errors()).length === 0;
  return true;
});

const goToNextStep = () => {
  let ok = true;
  if (currentStep.value === 1) ok = validateStep1();
  else if (currentStep.value === 2) ok = validateStep2();
  else if (currentStep.value === 3) ok = validateStep3();
  if (!ok) {
    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }
  if (currentStep.value < steps.length) {
    currentStep.value++;
    saveToLocalStorage();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
};

const goToPreviousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
    saveToLocalStorage();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
};

const saveToLocalStorage = () => {
  try {
    const dataToSave = {
      currentStep: currentStep.value,
      formData: {
        companyInfo: {
          ...formData.companyInfo,
          logo: null,
        },
        adminUser: {
          ...formData.adminUser,
          password: "",
          password_confirm: "",
        },
        preferences: formData.preferences,
      },
    };
    localStorage.setItem("onboarding_progress", JSON.stringify(dataToSave));
  } catch (error) {
    console.warn("Could not save onboarding progress:", error);
  }
};

const loadFromLocalStorage = () => {
  try {
    const saved = localStorage.getItem("onboarding_progress");
    if (saved) {
      const data = JSON.parse(saved);
      currentStep.value = data.currentStep || 1;
      if (data.formData) {
        if (data.formData.companyInfo) {
          Object.assign(formData.companyInfo, data.formData.companyInfo);
        }
        if (data.formData.adminUser) {
          Object.assign(formData.adminUser, {
            ...data.formData.adminUser,
            password: "",
            password_confirm: "",
          });
        }
        if (data.formData.preferences != null) {
          formData.preferences = normalizeStoredPreferences(
            data.formData.preferences
          );
        }
      }
    }
  } catch (error) {
    console.warn("Could not load onboarding progress:", error);
  }
};

const handleFinalSubmit = async (turnstileToken) => {
  if (!validateStep1() || !validateStep2() || !validateStep3()) {
    submitError.value = "Please fix the highlighted fields before continuing.";
    if (!validateStep1()) currentStep.value = 1;
    else if (!validateStep2()) currentStep.value = 2;
    else if (!validateStep3()) currentStep.value = 3;
    return;
  }

  isSubmitting.value = true;
  submitError.value = "";

  try {
    formData.preferences = normalizeStoredPreferences(formData.preferences);
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
        password: formData.adminUser.password,
      },
      preferences: formData.preferences,
    };

    const response = await createTenantWorkspace(payload, turnstileToken);
    localStorage.removeItem("onboarding_progress");

    if (response.verification_required) {
      verificationPending.value = true;
      verificationEmail.value = response.email || formData.adminUser.email;
      debugVerifyUrl.value = response.debug_verify_url || "";
      submitError.value = "";
      return;
    }

    if (response.url) {
      window.location.href = response.url;
    } else if (response.tenant && response.tenant.domain) {
      const protocol = window.location.protocol;
      window.location.href = `${protocol}//${response.tenant.domain}/login/`;
    } else {
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    }
  } catch (error) {
    console.error("Error creating tenant:", error);
    submitError.value =
      error.message ||
      "We could not create your workspace. Please try again in a moment.";
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.jr-onboard {
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  background: var(--color-jr-surface, #fff);
  color: var(--color-jr-text, #111827);
  font-family: var(--font-jr-sans, Inter, system-ui, sans-serif);
  caret-color: var(--color-jr-primary, #2563eb);
}

.jr-onboard ::selection {
  background: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 28%,
    transparent
  );
  color: var(--color-jr-text, #111827);
}

.jr-onboard__form-pane {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 100vh;
  min-height: 100dvh;
}

.jr-onboard__chrome {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-onboard__brand {
  display: inline-flex;
  line-height: 0;
  text-decoration: none;
}

.jr-onboard__brand-logo {
  height: 3.25rem;
  width: auto;
  max-width: 14rem;
  object-fit: contain;
}

.jr-onboard__signin {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-onboard__signin-link {
  color: var(--color-jr-primary, #2563eb);
  font-weight: 600;
  text-decoration: none;
}

.jr-onboard__signin-link:hover {
  text-decoration: underline;
}

.jr-onboard__body {
  flex: 1;
  width: 100%;
  max-width: 42rem;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 2rem;
}

.jr-onboard__steps {
  margin-bottom: 1.75rem;
}

.jr-onboard__step-list {
  list-style: none;
  margin: 0 0 0.65rem;
  padding: 0;
  display: flex;
  justify-content: space-between;
  gap: 0.35rem;
}

.jr-onboard__step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
}

.jr-onboard__step-marker {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border: 2px solid var(--color-jr-border, #e5e7eb);
  border-radius: 0;
  background: var(--color-jr-surface, #fff);
  color: var(--color-jr-muted, #4b5563);
  font-size: 0.875rem;
  font-weight: 700;
}

.jr-onboard__step--active .jr-onboard__step-marker,
.jr-onboard__step--done .jr-onboard__step-marker {
  border-color: var(--color-jr-primary, #2563eb);
  background: var(--color-jr-primary, #2563eb);
  color: #fff;
}

.jr-onboard__step-check {
  width: 0.875rem;
  height: 0.875rem;
}

.jr-onboard__step-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-muted, #4b5563);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.jr-onboard__step--active .jr-onboard__step-label,
.jr-onboard__step--done .jr-onboard__step-label {
  color: var(--color-jr-text, #111827);
}

.jr-onboard__progress {
  height: 0.25rem;
  background: var(--color-jr-border, #e5e7eb);
  overflow: hidden;
}

.jr-onboard__progress-fill {
  height: 100%;
  width: 100%;
  transform-origin: left center;
  transform: scaleX(0.25);
  background: var(--color-jr-primary, #2563eb);
  transition: transform 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

.jr-onboard__intro {
  margin-bottom: 1.5rem;
}

.jr-onboard__title {
  margin: 0 0 0.5rem;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: var(--color-jr-text, #111827);
}

.jr-onboard__lead {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--color-jr-muted, #4b5563);
}

.jr-onboard__panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.jr-onboard__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-onboard__actions-spacer {
  flex: 1;
}

.jr-onboard__verify {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.5rem 0 2rem;
}

.jr-onboard__hint {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted, #4b5563);
  word-break: break-all;
}

.jr-onboard__visual {
  display: none;
}

.jr-onboard-fade-enter-active,
.jr-onboard-fade-leave-active {
  transition: opacity 0.22s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.22s cubic-bezier(0.22, 1, 0.36, 1);
}

.jr-onboard-fade-enter-from {
  opacity: 0;
  transform: translateY(0.35rem);
}

.jr-onboard-fade-leave-to {
  opacity: 0;
  transform: translateY(-0.25rem);
}

@media (min-width: 1024px) {
  .jr-onboard {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }

  .jr-onboard__chrome {
    padding: 1.25rem 2rem;
    border-bottom: 0;
  }

  .jr-onboard__body {
    max-width: 34rem;
    margin: 0;
    padding: 0.5rem 2.75rem 2.5rem;
    align-self: center;
    width: 100%;
  }

  .jr-onboard__brand-logo {
    height: 3.5rem;
    max-width: 15.5rem;
  }

  .jr-onboard__form-pane {
    justify-content: flex-start;
  }

  .jr-onboard__visual {
    display: block;
    position: relative;
    min-height: 100vh;
    min-height: 100dvh;
    overflow: hidden;
    background: var(--color-jr-primary-deep, #1e3a8a);
  }

  .jr-onboard__visual-img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center top;
  }

  .jr-onboard__visual-scrim {
    position: absolute;
    inset: auto 0 0;
    padding: 2rem 2rem 2.25rem;
    background: linear-gradient(
      to top,
      color-mix(in srgb, #0f172a 78%, transparent) 0%,
      transparent 100%
    );
  }

  .jr-onboard__visual-quote {
    margin: 0;
    max-width: 22rem;
    font-size: 0.95rem;
    font-weight: 600;
    line-height: 1.4;
    color: #fff;
    text-shadow: 0 1px 2px rgba(15, 23, 42, 0.35);
  }
}
</style>
