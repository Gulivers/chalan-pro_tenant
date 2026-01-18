<template>
  <div class="step-admin-user">
    <div class="step-header mb-4">
      <h3 class="fw-bold mb-2">Administrator User</h3>
      <p class="text-muted mb-0">Create the main administrator account</p>
    </div>

    <div class="step-content">
      <InputField
        id="admin_name"
        v-model="localData.name"
        label="Full Name"
        placeholder=""
        :error="errors.name"
        :required="true"
        :maxlength="150"
        @blur="validateField('name')"
      />

      <InputField
        id="admin_email"
        v-model="localData.email"
        type="email"
        label="Email Address"
        placeholder=""
        :error="errors.email"
        :required="true"
        :maxlength="254"
        hint="This will be your system access email"
        @blur="validateField('email')"
      />

      <div class="form-floating mb-3">
        <input
          id="admin_password"
          :type="showPassword ? 'text' : 'password'"
          v-model="localData.password"
          class="form-control"
          :class="{ 'is-invalid': errors.password, 'has-value': localData.password && localData.password.trim() !== '' }"
          placeholder=""
          required
          maxlength="128"
          @input="updatePassword"
          @blur="validateField('password')"
          aria-label="Admin password"
          :aria-describedby="errors.password ? 'admin_password-error' : undefined"
        />
        <label for="admin_password">
          Password <span class="text-danger">*</span>
        </label>
        <button
          type="button"
          class="btn btn-link position-absolute end-0 top-50 translate-middle-y pe-3"
          style="z-index: 10; border: none; background: none;"
          @click="togglePasswordVisibility"
          :aria-label="showPassword ? 'Hide password' : 'Show password'"
        >
          <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
        </button>
        <div v-if="errors.password" id="admin_password-error" class="invalid-feedback d-block mt-1">
          {{ errors.password }}
        </div>
      </div>

      <!-- Password Strength Meter -->
      <div v-if="localData.password" class="password-strength mb-3">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <small class="text-muted">Password strength:</small>
          <span class="badge" :class="strengthClass">{{ strengthLabel }}</span>
        </div>
        <div class="progress" style="height: 6px;">
          <div
            class="progress-bar"
            :class="strengthBarClass"
            :style="{ width: strengthPercentage + '%' }"
            role="progressbar"
            :aria-valuenow="strengthPercentage"
            aria-valuemin="0"
            aria-valuemax="100"
          ></div>
        </div>
      </div>

      <div class="form-floating mb-3">
        <input
          id="admin_password_confirm"
          :type="showPasswordConfirm ? 'text' : 'password'"
          v-model="localData.password_confirm"
          class="form-control"
          :class="{ 'is-invalid': errors.password_confirm, 'has-value': localData.password_confirm && localData.password_confirm.trim() !== '' }"
          placeholder=""
          required
          maxlength="128"
          @input="validateField('password_confirm')"
          @blur="validateField('password_confirm')"
          aria-label="Confirm password"
          :aria-describedby="errors.password_confirm ? 'admin_password_confirm-error' : undefined"
        />
        <label for="admin_password_confirm">
          Confirm Password <span class="text-danger">*</span>
        </label>
        <button
          type="button"
          class="btn btn-link position-absolute end-0 top-50 translate-middle-y pe-3"
          style="z-index: 10; border: none; background: none;"
          @click="togglePasswordConfirmVisibility"
          :aria-label="showPasswordConfirm ? 'Hide confirmation' : 'Show confirmation'"
        >
          <i :class="showPasswordConfirm ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
        </button>
        <div v-if="errors.password_confirm" id="admin_password_confirm-error" class="invalid-feedback d-block mt-1">
          {{ errors.password_confirm }}
        </div>
      </div>

      <!-- Password Requirements -->
      <div class="password-requirements">
        <small class="text-muted d-block mb-2">Password must contain:</small>
        <ul class="list-unstyled small mb-0">
          <li :class="{ 'text-success': hasMinLength }">
            <i :class="hasMinLength ? 'fas fa-check-circle' : 'far fa-circle'" class="me-2"></i>
            At least 8 characters
          </li>
          <li :class="{ 'text-success': hasUpperCase }">
            <i :class="hasUpperCase ? 'fas fa-check-circle' : 'far fa-circle'" class="me-2"></i>
            One uppercase letter
          </li>
          <li :class="{ 'text-success': hasLowerCase }">
            <i :class="hasLowerCase ? 'fas fa-check-circle' : 'far fa-circle'" class="me-2"></i>
            One lowercase letter
          </li>
          <li :class="{ 'text-success': hasNumber }">
            <i :class="hasNumber ? 'fas fa-check-circle' : 'far fa-circle'" class="me-2"></i>
            One number
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, watch, ref } from 'vue'
import InputField from './InputField.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  errors: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'validate'])

const localData = reactive({
  name: props.modelValue.name || '',
  email: props.modelValue.email || '',
  password: props.modelValue.password || '',
  password_confirm: props.modelValue.password_confirm || ''
})

const showPassword = ref(false)
const showPasswordConfirm = ref(false)

// Watch for changes and emit updates
watch(() => localData.name, () => {
  emit('update:modelValue', { ...localData })
})

watch(() => localData.email, () => {
  emit('update:modelValue', { ...localData })
})

watch(() => localData.password, () => {
  emit('update:modelValue', { ...localData })
})

watch(() => localData.password_confirm, () => {
  emit('update:modelValue', { ...localData })
})

const updatePassword = (event) => {
  localData.password = event.target.value
  emit('update:modelValue', { ...localData })
}

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const togglePasswordConfirmVisibility = () => {
  showPasswordConfirm.value = !showPasswordConfirm.value
}

// Password strength calculation
const passwordStrength = computed(() => {
  const password = localData.password
  if (!password) return 0

  let strength = 0
  
  // Length check
  if (password.length >= 8) strength += 1
  if (password.length >= 12) strength += 1
  
  // Character type checks
  if (/[a-z]/.test(password)) strength += 1
  if (/[A-Z]/.test(password)) strength += 1
  if (/[0-9]/.test(password)) strength += 1
  if (/[^a-zA-Z0-9]/.test(password)) strength += 1
  
  return Math.min(strength, 5)
})

const strengthPercentage = computed(() => {
  return (passwordStrength.value / 5) * 100
})

const strengthLabel = computed(() => {
  const strength = passwordStrength.value
  if (strength <= 1) return 'Very Weak'
  if (strength <= 2) return 'Weak'
  if (strength <= 3) return 'Fair'
  if (strength <= 4) return 'Strong'
  return 'Very Strong'
})

const strengthClass = computed(() => {
  const strength = passwordStrength.value
  if (strength <= 1) return 'bg-danger'
  if (strength <= 2) return 'bg-warning'
  if (strength <= 3) return 'bg-info'
  if (strength <= 4) return 'bg-primary'
  return 'bg-success'
})

const strengthBarClass = computed(() => {
  return strengthClass.value
})

// Password requirements
const hasMinLength = computed(() => localData.password.length >= 8)
const hasUpperCase = computed(() => /[A-Z]/.test(localData.password))
const hasLowerCase = computed(() => /[a-z]/.test(localData.password))
const hasNumber = computed(() => /[0-9]/.test(localData.password))

const validateField = (fieldName) => {
  emit('validate', fieldName)
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
  max-width: 600px;
  margin: 0 auto;
}

.password-strength {
  margin-top: -0.5rem;
}

.password-requirements {
  background-color: var(--bs-light);
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.password-requirements ul li {
  margin-bottom: 0.5rem;
  transition: color 0.2s ease;
}

.password-requirements ul li:last-child {
  margin-bottom: 0;
}

.form-floating > .btn-link {
  color: var(--bs-secondary);
  text-decoration: none;
}

.form-floating > .btn-link:hover {
  color: var(--bs-primary);
}

/* Estilos para form-floating (password inputs) */
.form-floating {
  position: relative;
}

.form-floating > label {
  padding: 0.75rem 1rem;
  font-weight: 500;
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  pointer-events: none;
  border: 1px solid transparent;
  transform-origin: 0 0;
  transition: opacity 0.1s ease-in-out, transform 0.1s ease-in-out;
}

.form-floating .form-control {
  padding: 0.75rem 1rem;
  min-height: calc(3.5rem + 2px);
  line-height: 1.5;
}

/* Cuando el input está vacío, la label está dentro */
.form-floating .form-control:not(:focus):not(:not(:placeholder-shown)):placeholder-shown {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}

/* Cuando el input tiene valor o está en focus, mover la label arriba */
.form-floating .form-control:focus,
.form-floating .form-control.has-value,
.form-floating .form-control:not(:placeholder-shown) {
  padding-top: 2rem !important;
  padding-bottom: 0.75rem !important;
}

.form-floating .form-control:focus ~ label,
.form-floating .form-control.has-value ~ label,
.form-floating .form-control:not(:placeholder-shown) ~ label {
  opacity: 0.65;
  transform: scale(0.85) translateY(-0.25rem) translateX(0.15rem);
  padding-top: 0.5rem;
}

.form-floating .form-control:focus {
  border-color: var(--bs-primary);
  box-shadow: 0 0 0 0.2rem rgba(var(--bs-primary-rgb), 0.25);
}
</style>

