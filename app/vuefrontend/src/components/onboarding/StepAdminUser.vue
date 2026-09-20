<template>
  <div class="jr-onboard-step">
    <div class="jr-onboard-step__fields">
      <JRField
        label="Full name"
        required
        inputId="admin_name"
        :error="errors.name || ''">
        <template #default="{ invalid, describedby }">
          <JRInput
            inputId="admin_name"
            v-model="localData.name"
            :invalid="invalid"
            :aria-describedby="describedby || undefined"
            maxlength="150"
            placeholder="Your full name"
            @blur="validateField('name')" />
        </template>
      </JRField>

      <JRField
        label="Work email"
        required
        inputId="admin_email"
        hint="You will use this email to sign in to JobRhythm."
        :error="errors.email || ''">
        <template #default="{ invalid, describedby }">
          <JRInput
            inputId="admin_email"
            type="email"
            v-model="localData.email"
            :invalid="invalid"
            :aria-describedby="describedby || undefined"
            maxlength="254"
            placeholder="you@company.com"
            @blur="validateField('email')" />
        </template>
      </JRField>

      <JRField
        label="Password"
        required
        inputId="admin_password"
        :error="errors.password || ''">
        <template #default="{ invalid, describedby }">
          <div class="jr-onboard-pw">
            <JRInput
              inputId="admin_password"
              :type="showPassword ? 'text' : 'password'"
              v-model="localData.password"
              :invalid="invalid"
              :aria-describedby="describedby || undefined"
              maxlength="128"
              autocomplete="new-password"
              @blur="validateField('password')" />
            <button
              type="button"
              class="jr-onboard-pw__toggle"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
              @click="showPassword = !showPassword">
              <EyeSlash v-if="showPassword" class="jr-onboard-pw__icon" />
              <Eye v-else class="jr-onboard-pw__icon" />
            </button>
          </div>
        </template>
      </JRField>

      <div v-if="localData.password" class="jr-onboard-strength" aria-live="polite">
        <div class="jr-onboard-strength__meta">
          <span class="jr-onboard-strength__label">Password strength</span>
          <span
            class="jr-onboard-strength__value"
            :data-level="passwordStrength">
            {{ strengthLabel }}
          </span>
        </div>
        <div class="jr-onboard-strength__track" aria-hidden="true">
          <div
            class="jr-onboard-strength__fill"
            :data-level="passwordStrength"
            :style="{ transform: `scaleX(${strengthRatio})` }" />
        </div>
      </div>

      <JRField
        label="Confirm password"
        required
        inputId="admin_password_confirm"
        :error="errors.password_confirm || ''"
        :hint="
          passwordsMatchSuccess && !errors.password_confirm
            ? 'Passwords match.'
            : ''
        ">
        <template #default="{ invalid, describedby }">
          <div class="jr-onboard-pw">
            <JRInput
              inputId="admin_password_confirm"
              :type="showPasswordConfirm ? 'text' : 'password'"
              v-model="localData.password_confirm"
              :invalid="invalid"
              :aria-describedby="describedby || undefined"
              maxlength="128"
              autocomplete="new-password"
              @blur="validateField('password_confirm')" />
            <button
              type="button"
              class="jr-onboard-pw__toggle"
              :aria-label="
                showPasswordConfirm ? 'Hide confirmation' : 'Show confirmation'
              "
              @click="showPasswordConfirm = !showPasswordConfirm">
              <EyeSlash v-if="showPasswordConfirm" class="jr-onboard-pw__icon" />
              <Eye v-else class="jr-onboard-pw__icon" />
            </button>
          </div>
        </template>
      </JRField>

      <ul class="jr-onboard-reqs" aria-label="Password requirements">
        <li :class="{ 'jr-onboard-reqs__item--ok': hasMinLength }">
          <CheckCircle
            v-if="hasMinLength"
            class="jr-onboard-reqs__icon" />
          <span v-else class="jr-onboard-reqs__dot" aria-hidden="true" />
          At least 8 characters
        </li>
        <li :class="{ 'jr-onboard-reqs__item--ok': hasUpperCase }">
          <CheckCircle
            v-if="hasUpperCase"
            class="jr-onboard-reqs__icon" />
          <span v-else class="jr-onboard-reqs__dot" aria-hidden="true" />
          An uppercase letter
        </li>
        <li :class="{ 'jr-onboard-reqs__item--ok': hasLowerCase }">
          <CheckCircle
            v-if="hasLowerCase"
            class="jr-onboard-reqs__icon" />
          <span v-else class="jr-onboard-reqs__dot" aria-hidden="true" />
          A lowercase letter
        </li>
        <li :class="{ 'jr-onboard-reqs__item--ok': hasNumber }">
          <CheckCircle
            v-if="hasNumber"
            class="jr-onboard-reqs__icon" />
          <span v-else class="jr-onboard-reqs__dot" aria-hidden="true" />
          A number
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, watch, ref } from 'vue'
import Eye from '@primeicons/vue/eye'
import EyeSlash from '@primeicons/vue/eye-slash'
import CheckCircle from '@primeicons/vue/check-circle'
import { JRField, JRInput } from '@ui'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
  },
  errors: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:modelValue', 'validate'])

const localData = reactive({
  name: props.modelValue.name || '',
  email: props.modelValue.email || '',
  password: props.modelValue.password || '',
  password_confirm: props.modelValue.password_confirm || '',
})

const showPassword = ref(false)
const showPasswordConfirm = ref(false)

watch(
  localData,
  () => {
    emit('update:modelValue', { ...localData })
  },
  { deep: true }
)

const passwordStrength = computed(() => {
  const password = localData.password
  if (!password) return 0
  let strength = 0
  if (password.length >= 8) strength += 1
  if (password.length >= 12) strength += 1
  if (/[a-z]/.test(password)) strength += 1
  if (/[A-Z]/.test(password)) strength += 1
  if (/[0-9]/.test(password)) strength += 1
  if (/[^a-zA-Z0-9]/.test(password)) strength += 1
  return Math.min(strength, 5)
})

const strengthRatio = computed(() => passwordStrength.value / 5)

const strengthLabel = computed(() => {
  const strength = passwordStrength.value
  if (strength <= 1) return 'Very weak'
  if (strength <= 2) return 'Weak'
  if (strength <= 3) return 'Fair'
  if (strength <= 4) return 'Strong'
  return 'Very strong'
})

const hasMinLength = computed(() => localData.password.length >= 8)
const hasUpperCase = computed(() => /[A-Z]/.test(localData.password))
const hasLowerCase = computed(() => /[a-z]/.test(localData.password))
const hasNumber = computed(() => /[0-9]/.test(localData.password))

const passwordMeetsPolicy = computed(
  () =>
    hasMinLength.value &&
    hasUpperCase.value &&
    hasLowerCase.value &&
    hasNumber.value
)

const passwordsMatchSuccess = computed(
  () =>
    passwordMeetsPolicy.value &&
    localData.password_confirm.length > 0 &&
    localData.password === localData.password_confirm
)

const validateField = (fieldName) => {
  emit('validate', fieldName)
}
</script>

<style scoped>
.jr-onboard-step__fields {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.jr-onboard-pw {
  position: relative;
}

.jr-onboard-pw :deep(.jr-control),
.jr-onboard-pw :deep(input) {
  padding-right: 2.75rem;
}

.jr-onboard-pw__toggle {
  position: absolute;
  top: 50%;
  right: 0.5rem;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--color-jr-muted, #4b5563);
  cursor: pointer;
}

.jr-onboard-pw__toggle:hover {
  color: var(--color-jr-primary, #2563eb);
}

.jr-onboard-pw__icon {
  width: 1rem;
  height: 1rem;
}

.jr-onboard-strength__meta {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.jr-onboard-strength__label,
.jr-onboard-strength__value {
  font-size: 0.875rem;
  font-weight: 600;
}

.jr-onboard-strength__label {
  color: var(--color-jr-muted, #4b5563);
}

.jr-onboard-strength__value[data-level='1'],
.jr-onboard-strength__value[data-level='2'] {
  color: var(--color-jr-danger, #dc2626);
}

.jr-onboard-strength__value[data-level='3'] {
  color: var(--color-jr-warning, #d97706);
}

.jr-onboard-strength__value[data-level='4'],
.jr-onboard-strength__value[data-level='5'] {
  color: var(--color-jr-success, #16a34a);
}

.jr-onboard-strength__track {
  height: 0.25rem;
  background: var(--color-jr-border, #e5e7eb);
  overflow: hidden;
}

.jr-onboard-strength__fill {
  height: 100%;
  width: 100%;
  transform-origin: left center;
  transform: scaleX(0);
  transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1),
    background-color 0.2s ease;
  background: var(--color-jr-danger, #dc2626);
}

.jr-onboard-strength__fill[data-level='3'] {
  background: var(--color-jr-warning, #d97706);
}

.jr-onboard-strength__fill[data-level='4'],
.jr-onboard-strength__fill[data-level='5'] {
  background: var(--color-jr-success, #16a34a);
}

.jr-onboard-reqs {
  list-style: none;
  margin: 0;
  padding: 1rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface-muted, #f9fafb);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.jr-onboard-reqs li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-onboard-reqs__item--ok {
  color: var(--color-jr-success, #16a34a);
  font-weight: 600;
}

.jr-onboard-reqs__icon {
  width: 0.95rem;
  height: 0.95rem;
  flex-shrink: 0;
}

.jr-onboard-reqs__dot {
  width: 0.95rem;
  height: 0.95rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: 0;
  flex-shrink: 0;
}
</style>
