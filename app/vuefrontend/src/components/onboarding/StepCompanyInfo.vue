<template>
  <div class="jr-onboard-step">
    <div class="jr-onboard-step__fields">
      <JRField
        label="Company name"
        required
        inputId="business_name"
        :error="errors.business_name || ''">
        <template #default="{ invalid, describedby }">
          <JRInput
            inputId="business_name"
            v-model="localData.business_name"
            :invalid="invalid"
            :aria-describedby="describedby || undefined"
            :maxlength="150"
            placeholder="e.g. Sunshine Electric LLC"
            @blur="validateField('business_name')" />
        </template>
      </JRField>

      <JRField
        label="Trade / business type"
        required
        inputId="business_type"
        :error="errors.business_type || ''">
        <template #default="{ invalid, describedby }">
          <JRSelect
            inputId="business_type"
            v-model="localData.business_type"
            :options="businessTypeOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Select your trade"
            :invalid="invalid"
            :aria-describedby="describedby || undefined"
            @update:modelValue="validateField('business_type')" />
        </template>
      </JRField>

      <UploadLogo v-model="localData.logo" :error="errors.logo || ''" />

      <JRField
        label="Company address"
        inputId="company_address"
        hint="Optional — helps personalize your workspace later."
        :error="errors.address || ''">
        <template #default="{ invalid, describedby }">
          <JRTextarea
            inputId="company_address"
            v-model="localData.address"
            :invalid="invalid"
            :aria-describedby="describedby || undefined"
            :rows="3"
            placeholder="Street, city, state" />
        </template>
      </JRField>

      <JRField
        label="Monthly job volume"
        required
        inputId="monthly_operations"
        :error="errors.monthly_operations || ''">
        <template #default="{ invalid, describedby }">
          <JRSelect
            inputId="monthly_operations"
            v-model="localData.monthly_operations"
            :options="monthlyOperationsOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="Homes / jobs per month"
            :invalid="invalid"
            :aria-describedby="describedby || undefined"
            @update:modelValue="validateField('monthly_operations')" />
        </template>
      </JRField>

      <JRField
        label="Active crews"
        required
        inputId="crew_count"
        hint="Used to suggest a plan size—not locked during trial."
        :error="errors.crew_count || ''">
        <template #default="{ invalid, describedby }">
          <JRInput
            inputId="crew_count"
            :modelValue="crewCountDisplay"
            :invalid="invalid"
            :aria-describedby="describedby || undefined"
            inputmode="numeric"
            placeholder="e.g. 4"
            @update:modelValue="onCrewCount" />
        </template>
      </JRField>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch, computed } from 'vue'
import { JRField, JRInput, JRSelect, JRTextarea } from '@ui'
import UploadLogo from './UploadLogo.vue'

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

const businessTypeOptions = [
  { value: 'electric', label: 'Electric' },
  { value: 'air_conditioning', label: 'Air Conditioning' },
  { value: 'solar', label: 'Solar' },
  { value: 'plumbing', label: 'Plumbing' },
  {
    value: 'hvac',
    label: 'HVAC (Heating, Ventilation, Air Conditioning)',
  },
  { value: 'general', label: 'General (Other)' },
]

const monthlyOperationsOptions = [
  { value: '0-10', label: '0–10 homes per month' },
  { value: '11-25', label: '11–25 homes per month' },
  { value: '26-50', label: '26–50 homes per month' },
  { value: '51-100', label: '51–100 homes per month' },
  { value: '100+', label: '100+ homes per month' },
]

const localData = reactive({
  business_name: props.modelValue.business_name || '',
  business_type: props.modelValue.business_type || '',
  logo: props.modelValue.logo || null,
  address: props.modelValue.address || '',
  monthly_operations: props.modelValue.monthly_operations || '',
  crew_count: props.modelValue.crew_count || null,
})

watch(
  localData,
  () => {
    emit('update:modelValue', { ...localData })
  },
  { deep: true }
)

const crewCountDisplay = computed(() =>
  localData.crew_count === null || localData.crew_count === undefined
    ? ''
    : String(localData.crew_count)
)

const onCrewCount = (val) => {
  const raw = val === null || val === undefined ? '' : String(val).trim()
  if (!raw) {
    localData.crew_count = null
  } else {
    const n = Number(raw)
    localData.crew_count = Number.isNaN(n) ? null : n
  }
  emit('update:modelValue', { ...localData })
  emit('validate', 'crew_count')
}

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
</style>
