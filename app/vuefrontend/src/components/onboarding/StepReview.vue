<template>
  <div class="jr-onboard-review">
    <section class="jr-onboard-review__callout">
      <h2 class="jr-onboard-review__heading">Your 30-day free trial</h2>
      <p class="jr-onboard-review__text">
        You start with <strong>full access</strong> to the modules listed below.
        Connect scheduling, materials, contracts, and field updates so job
        progress is visible without the usual back-and-forth.
      </p>
      <p class="jr-onboard-review__note">
        Company details and modules can change later in Settings. Billing starts
        only when you choose a paid plan.
      </p>
    </section>

    <section v-if="landingSelectedPlan" class="jr-onboard-review__block">
      <h2 class="jr-onboard-review__heading">Selected plan</h2>
      <p class="jr-onboard-review__plan">{{ landingSelectedPlan }}</p>
      <p class="jr-onboard-review__note">
        Carried from pricing. You can confirm or change it when you upgrade.
      </p>
    </section>

    <section class="jr-onboard-review__block">
      <h2 class="jr-onboard-review__heading">Company</h2>
      <dl class="jr-onboard-review__dl">
        <div class="jr-onboard-review__row">
          <dt>Company name</dt>
          <dd>{{ companyInfo.business_name }}</dd>
        </div>
        <div class="jr-onboard-review__row">
          <dt>Trade / type</dt>
          <dd>{{ getBusinessTypeLabel(companyInfo.business_type) }}</dd>
        </div>
        <div v-if="companyInfo.address" class="jr-onboard-review__row">
          <dt>Address</dt>
          <dd>{{ companyInfo.address }}</dd>
        </div>
        <div class="jr-onboard-review__row">
          <dt>Monthly job volume</dt>
          <dd>{{ getMonthlyOperationsLabel(companyInfo.monthly_operations) }}</dd>
        </div>
        <div class="jr-onboard-review__row">
          <dt>Active crews</dt>
          <dd>{{ companyInfo.crew_count ?? '—' }}</dd>
        </div>
        <div v-if="companyInfo.logo && logoPreview" class="jr-onboard-review__row">
          <dt>Logo</dt>
          <dd>
            <img
              :src="logoPreview"
              alt="Company logo"
              class="jr-onboard-review__logo" />
          </dd>
        </div>
      </dl>
    </section>

    <section v-if="recommendedPlan" class="jr-onboard-review__block">
      <h2 class="jr-onboard-review__heading">Recommended plan (team size)</h2>
      <p class="jr-onboard-review__text">
        Based on active crews, a good fit is often
        <strong>{{ recommendedPlan }}</strong>. For reference when you
        subscribe—not a lock-in during trial.
      </p>
    </section>

    <section class="jr-onboard-review__block">
      <h2 class="jr-onboard-review__heading">Administrator</h2>
      <dl class="jr-onboard-review__dl">
        <div class="jr-onboard-review__row">
          <dt>Name</dt>
          <dd>{{ adminUser.name }}</dd>
        </div>
        <div class="jr-onboard-review__row">
          <dt>Email</dt>
          <dd>{{ (adminUser.email || '').trim() }}</dd>
        </div>
        <div class="jr-onboard-review__row">
          <dt>Password</dt>
          <dd>
            <span class="jr-onboard-review__masked">••••••••</span>
            <span class="jr-onboard-review__note"> (saved securely)</span>
          </dd>
        </div>
      </dl>
    </section>

    <section class="jr-onboard-review__block">
      <h2 class="jr-onboard-review__heading">Modules included</h2>
      <ul v-if="preferences.length" class="jr-onboard-review__modules">
        <li v-for="pref in preferences" :key="pref">
          {{ getModuleLabel(pref) }}
        </li>
      </ul>
      <p v-else class="jr-onboard-review__note">No modules selected</p>
    </section>

    <p v-if="errorMessage" class="jr-onboard-review__error" role="alert">
      {{ errorMessage }}
    </p>

    <p class="jr-onboard-review__secure">
      We email a confirmation link. Your workspace is created only after you
      verify your email.
    </p>

    <div class="jr-onboard-review__captcha">
      <TurnstileWidget
        :site-key="turnstileSiteKey"
        @update:token="onTurnstileToken"
        @error="onTurnstileError" />
      <p v-if="turnstileError" class="jr-onboard-review__error" role="alert">
        {{ turnstileError }}
      </p>
    </div>

    <footer class="jr-onboard-review__actions">
      <JRButton
        type="button"
        variant="secondary"
        :disabled="isSubmitting"
        @click="handleGoBack">
        ← Back
      </JRButton>
      <JRButton
        type="button"
        variant="primary"
        :disabled="isSubmitting"
        @click="handleSubmit">
        <span v-if="isSubmitting">Sending verification email…</span>
        <span v-else>Send verification email</span>
      </JRButton>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { JRButton } from '@ui'
import TurnstileWidget from './TurnstileWidget.vue'

const props = defineProps({
  companyInfo: {
    type: Object,
    required: true,
  },
  adminUser: {
    type: Object,
    required: true,
  },
  preferences: {
    type: Array,
    default: () => [],
  },
  recommendedPlan: {
    type: String,
    default: null,
  },
  landingSelectedPlan: {
    type: String,
    default: null,
  },
  isSubmitting: {
    type: Boolean,
    default: false,
  },
  errorMessage: {
    type: String,
    default: '',
  },
  turnstileSiteKey: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['submit', 'go-back'])

const turnstileToken = ref('')
const turnstileError = ref('')
const logoPreview = ref(null)

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
  general: 'General (Other)',
}

const getBusinessTypeLabel = (value) => businessTypeLabels[value] || value

const monthlyOperationsLabels = {
  '0-10': '0–10 homes per month',
  '11-25': '11–25 homes per month',
  '26-50': '26–50 homes per month',
  '51-100': '51–100 homes per month',
  '100+': '100+ homes per month',
}

const getMonthlyOperationsLabel = (value) =>
  monthlyOperationsLabels[value] || value || 'Not specified'

const moduleLabels = {
  operations: 'Operations',
  inventory: 'Inventory',
  contracts_pricing: 'Contracts & Pricing (piece work)',
  entities: 'Entities',
  crews_fleet: 'Crews and Fleet',
  communities: 'Communities',
  contracts: 'Contracts',
  schedule: 'Schedule',
  crews: 'Crews',
  notes: 'Notes',
}

const getModuleLabel = (id) => moduleLabels[id] || id

const handleSubmit = () => {
  turnstileError.value = ''
  if (props.turnstileSiteKey && !turnstileToken.value) {
    turnstileError.value = 'Please complete the CAPTCHA verification.'
    return
  }
  emit('submit', turnstileToken.value)
}

const onTurnstileToken = (token) => {
  turnstileToken.value = token || ''
  if (token) turnstileError.value = ''
}

const onTurnstileError = (message) => {
  turnstileError.value = message
}

const handleGoBack = () => {
  emit('go-back')
}
</script>

<style scoped>
.jr-onboard-review {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.jr-onboard-review__callout,
.jr-onboard-review__block {
  padding: 1rem 1.1rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #fff);
}

.jr-onboard-review__callout {
  border-color: color-mix(in srgb, var(--color-jr-success, #16a34a) 35%, #e5e7eb);
  background: color-mix(in srgb, var(--color-jr-success, #16a34a) 6%, #fff);
}

.jr-onboard-review__heading {
  margin: 0 0 0.5rem;
  font-size: 0.95rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--color-jr-text, #111827);
}

.jr-onboard-review__text,
.jr-onboard-review__note,
.jr-onboard-review__secure {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-jr-muted, #4b5563);
}

.jr-onboard-review__text + .jr-onboard-review__note,
.jr-onboard-review__plan + .jr-onboard-review__note {
  margin-top: 0.5rem;
}

.jr-onboard-review__plan {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-jr-primary, #2563eb);
}

.jr-onboard-review__dl {
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.jr-onboard-review__row {
  display: grid;
  grid-template-columns: minmax(7rem, 34%) minmax(0, 1fr);
  gap: 0.75rem;
  align-items: start;
}

.jr-onboard-review__row dt {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-muted, #4b5563);
}

.jr-onboard-review__row dd {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--color-jr-text, #111827);
  word-break: break-word;
}

.jr-onboard-review__logo {
  max-width: 7.5rem;
  max-height: 7.5rem;
  object-fit: contain;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  padding: 0.35rem;
  background: #fff;
}

.jr-onboard-review__masked {
  letter-spacing: 0.08em;
}

.jr-onboard-review__modules {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.jr-onboard-review__modules li {
  padding: 0.35rem 0.65rem;
  border: 1px solid color-mix(in srgb, var(--color-jr-primary, #2563eb) 28%, #e5e7eb);
  background: color-mix(in srgb, var(--color-jr-primary, #2563eb) 8%, #fff);
  color: var(--color-jr-primary-deep, #1e3a8a);
  font-size: 0.875rem;
  font-weight: 600;
}

.jr-onboard-review__error {
  margin: 0;
  padding: 0.75rem 1rem;
  border: 1px solid color-mix(in srgb, var(--color-jr-danger, #dc2626) 35%, transparent);
  background: color-mix(in srgb, var(--color-jr-danger, #dc2626) 8%, #fff);
  color: var(--color-jr-danger, #dc2626);
  font-size: 0.875rem;
  font-weight: 600;
}

.jr-onboard-review__captcha {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.jr-onboard-review__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}
</style>
