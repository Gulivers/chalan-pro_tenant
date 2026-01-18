<template>
  <div class="step-company-info">
    <div class="step-header mb-4">
      <h3 class="fw-bold mb-2">Company Information</h3>
      <p class="text-muted mb-0">Let's start with your business basic information</p>
    </div>

    <div class="step-content">
      <InputField
        id="business_name"
        v-model="localData.business_name"
        label="Business Name"
        placeholder=""
        :error="errors.business_name"
        :required="true"
        :maxlength="100"
        @blur="validateField('business_name')"
      />

      <SelectField
        id="business_type"
        v-model="localData.business_type"
        label="Business Type"
        placeholder=""
        :options="businessTypeOptions"
        :error="errors.business_type"
        :required="true"
        @blur="validateField('business_type')"
      />

      <UploadLogo
        v-model="localData.logo"
        :error="errors.logo"
      />

      <div class="form-floating mb-3">
        <textarea
          id="address"
          v-model="localData.address"
          class="form-control"
          :class="{ 'has-value': localData.address && localData.address.trim() !== '' }"
          placeholder=""
          rows="3"
          style="height: 100px;"
          maxlength="255"
          aria-label="Business address (optional)"
        ></textarea>
        <label for="address">
          Address <span class="text-muted small">(Optional)</span>
        </label>
      </div>

      <SelectField
        id="monthly_operations"
        v-model="localData.monthly_operations"
        label="How many projects or homes does your company usually handle each month?"
        placeholder=""
        :options="monthlyOperationsOptions"
        :error="errors.monthly_operations"
        :required="true"
        @blur="validateField('monthly_operations')"
      />

      <div class="form-floating mb-3">
        <input
          id="crew_count"
          type="number"
          v-model.number="localData.crew_count"
          class="form-control"
          :class="{ 'is-invalid': errors.crew_count, 'has-value': localData.crew_count && localData.crew_count > 0 }"
          placeholder=""
          required
          min="1"
          step="1"
          @input="handleCrewCountChange"
          @blur="validateField('crew_count')"
          aria-label="Number of active crews"
          :aria-describedby="errors.crew_count ? 'crew_count-error' : undefined"
        />
        <label for="crew_count">
          How many active crews does your company manage? <span class="text-danger">*</span>
        </label>
        <div v-if="errors.crew_count" id="crew_count-error" class="invalid-feedback d-block mt-1">
          {{ errors.crew_count }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import InputField from './InputField.vue'
import SelectField from './SelectField.vue'
import UploadLogo from './UploadLogo.vue'

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

const businessTypeOptions = [
  { value: 'electric', label: 'Electric' },
  { value: 'air_conditioning', label: 'Air Conditioning' },
  { value: 'solar', label: 'Solar' },
  { value: 'plumbing', label: 'Plumbing' },
  { value: 'hvac', label: 'HVAC (Heating, Ventilation, Air Conditioning)' },
  { value: 'general', label: 'General (Other)' }
]

const monthlyOperationsOptions = [
  { value: '0-10', label: '0–10 homes per month' },
  { value: '11-25', label: '11–25 homes per month' },
  { value: '26-50', label: '26–50 homes per month' },
  { value: '51-100', label: '51–100 homes per month' },
  { value: '100+', label: '100+ homes per month' }
]

const localData = reactive({
  business_name: props.modelValue.business_name || '',
  business_type: props.modelValue.business_type || '',
  logo: props.modelValue.logo || null,
  address: props.modelValue.address || '',
  monthly_operations: props.modelValue.monthly_operations || '',
  crew_count: props.modelValue.crew_count || null
})

// Watch for changes and emit updates
watch(() => localData.business_name, (val) => {
  emit('update:modelValue', { ...localData })
})

watch(() => localData.business_type, (val) => {
  emit('update:modelValue', { ...localData })
})

watch(() => localData.logo, (val) => {
  emit('update:modelValue', { ...localData })
})

watch(() => localData.address, (val) => {
  emit('update:modelValue', { ...localData })
})

watch(() => localData.monthly_operations, (val) => {
  emit('update:modelValue', { ...localData })
})

watch(() => localData.crew_count, (val) => {
  emit('update:modelValue', { ...localData })
})

const handleCrewCountChange = (event) => {
  const value = parseInt(event.target.value)
  localData.crew_count = isNaN(value) ? null : value
  emit('update:modelValue', { ...localData })
}

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

/* Estilos para form-floating (address textarea y crew_count input) */
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

.form-control {
  padding: 0.75rem 1rem;
  min-height: calc(3.5rem + 2px);
  line-height: 1.5;
}

/* Cuando el campo está vacío, la label está dentro */
.form-control:not(:focus):not(.has-value):placeholder-shown {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}

/* Cuando el campo tiene valor o está en focus, mover la label arriba */
.form-control:focus,
.form-control.has-value,
.form-control:not(:placeholder-shown) {
  padding-top: 2rem !important;
  padding-bottom: 0.75rem !important;
}

.form-control:focus ~ label,
.form-control.has-value ~ label,
.form-control:not(:placeholder-shown) ~ label {
  opacity: 0.65;
  transform: scale(0.85) translateY(-0.25rem) translateX(0.15rem);
  padding-top: 0.5rem;
}

.form-control:focus {
  border-color: var(--bs-primary);
  box-shadow: 0 0 0 0.2rem rgba(var(--bs-primary-rgb), 0.25);
}
</style>

