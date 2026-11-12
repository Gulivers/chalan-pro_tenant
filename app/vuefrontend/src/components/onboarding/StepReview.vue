<template>
  <div class="jr-onboard-review">
    <section class="jr-onboard-review__callout">
      <h2 class="jr-onboard-review__heading">
        {{ t('onboarding.review.trialTitle') }}
      </h2>
      <p class="jr-onboard-review__text">
        {{ t('onboarding.review.trialTextBefore') }}
        <strong>{{ t('onboarding.review.trialTextStrong') }}</strong>
        {{ t('onboarding.review.trialTextAfter') }}
      </p>
      <p class="jr-onboard-review__note">
        {{ t('onboarding.review.trialNote') }}
      </p>
    </section>

    <section v-if="landingSelectedPlan" class="jr-onboard-review__block">
      <h2 class="jr-onboard-review__heading">
        {{ t('onboarding.review.selectedPlan') }}
      </h2>
      <p class="jr-onboard-review__plan">{{ landingSelectedPlan }}</p>
      <p class="jr-onboard-review__note">
        {{ t('onboarding.review.selectedPlanNote') }}
      </p>
    </section>

    <section class="jr-onboard-review__block">
      <h2 class="jr-onboard-review__heading">
        {{ t('onboarding.review.companyHeading') }}
      </h2>
      <dl class="jr-onboard-review__dl">
        <div class="jr-onboard-review__row">
          <dt>{{ t('onboarding.review.companyName') }}</dt>
          <dd>{{ companyInfo.business_name }}</dd>
        </div>
        <!-- TEMP: still show fixed Electric while multi-trade onboarding is paused. -->
        <div class="jr-onboard-review__row">
          <dt>{{ t('onboarding.review.tradeType') }}</dt>
          <dd>{{ getBusinessTypeLabel(companyInfo.business_type || 'electric') }}</dd>
        </div>
        <div v-if="companyInfo.address" class="jr-onboard-review__row">
          <dt>{{ t('onboarding.review.address') }}</dt>
          <dd>{{ companyInfo.address }}</dd>
        </div>
        <div class="jr-onboard-review__row">
          <dt>{{ t('onboarding.review.monthlyVolume') }}</dt>
          <dd>{{ getMonthlyOperationsLabel(companyInfo.monthly_operations) }}</dd>
        </div>
        <div class="jr-onboard-review__row">
          <dt>{{ t('onboarding.review.activeCrews') }}</dt>
          <dd>{{ companyInfo.crew_count ?? '—' }}</dd>
        </div>
        <div v-if="companyInfo.logo && logoPreview" class="jr-onboard-review__row">
          <dt>{{ t('onboarding.review.logo') }}</dt>
          <dd>
            <img
              :src="logoPreview"
              :alt="t('onboarding.review.logoAlt')"
              class="jr-onboard-review__logo" />
          </dd>
        </div>
      </dl>
    </section>

    <section v-if="recommendedPlan" class="jr-onboard-review__block">
      <h2 class="jr-onboard-review__heading">
        {{ t('onboarding.review.recommendedHeading') }}
      </h2>
      <p class="jr-onboard-review__text">
        {{ t('onboarding.review.recommendedBefore') }}
        <strong>{{ recommendedPlan }}</strong>{{ t('onboarding.review.recommendedAfter') }}
      </p>
    </section>

    <section class="jr-onboard-review__block">
      <h2 class="jr-onboard-review__heading">
        {{ t('onboarding.review.adminHeading') }}
      </h2>
      <dl class="jr-onboard-review__dl">
        <div class="jr-onboard-review__row">
          <dt>{{ t('onboarding.review.name') }}</dt>
          <dd>{{ adminUser.name }}</dd>
        </div>
        <div class="jr-onboard-review__row">
          <dt>{{ t('onboarding.review.email') }}</dt>
          <dd>{{ (adminUser.email || '').trim() }}</dd>
        </div>
        <div class="jr-onboard-review__row">
          <dt>{{ t('onboarding.review.password') }}</dt>
          <dd>
            <span class="jr-onboard-review__masked">••••••••</span>
            <span class="jr-onboard-review__note">
              {{ t('onboarding.review.passwordSaved') }}
            </span>
          </dd>
        </div>
      </dl>
    </section>

    <section class="jr-onboard-review__block">
      <h2 class="jr-onboard-review__heading">
        {{ t('onboarding.review.modulesHeading') }}
      </h2>
      <ul v-if="preferences.length" class="jr-onboard-review__modules">
        <li v-for="pref in preferences" :key="pref">
          {{ getModuleLabel(pref) }}
        </li>
      </ul>
      <p v-else class="jr-onboard-review__note">
        {{ t('onboarding.review.noModules') }}
      </p>
    </section>

    <p v-if="errorMessage" class="jr-onboard-review__error" role="alert">
      {{ errorMessage }}
    </p>

    <p class="jr-onboard-review__secure">
      {{ t('onboarding.review.secureNote') }}
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
        {{ t('onboarding.back') }}
      </JRButton>
      <JRButton
        type="button"
        variant="primary"
        :disabled="isSubmitting"
        @click="handleSubmit">
        <span v-if="isSubmitting">{{ t('onboarding.review.sendingEmail') }}</span>
        <span v-else>{{ t('onboarding.review.sendEmail') }}</span>
      </JRButton>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { JRButton } from '@ui'
import TurnstileWidget from './TurnstileWidget.vue'

const { t, te } = useI18n({ useScope: 'global' })

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

const getBusinessTypeLabel = (value) => {
  const key = `onboarding.company.trades.${value}`
  return te(key) ? t(key) : value
}

const getMonthlyOperationsLabel = (value) => {
  if (!value) return t('onboarding.review.notSpecified')
  const key = `onboarding.company.monthly.${value}`
  return te(key) ? t(key) : value
}

const getModuleLabel = (id) => {
  const key = `onboarding.modules.labels.${id}`
  return te(key) ? t(key) : id
}

const handleSubmit = () => {
  turnstileError.value = ''
  if (props.turnstileSiteKey && !turnstileToken.value) {
    turnstileError.value = t('onboarding.review.captchaRequired')
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
