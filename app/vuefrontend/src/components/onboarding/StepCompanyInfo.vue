<template>
  <div class="jr-onboard-step">
    <div class="jr-onboard-step__fields">
      <JRField
        :label="t('onboarding.company.name')"
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
            :placeholder="t('onboarding.company.namePlaceholder')"
            @blur="validateField('business_name')" />
        </template>
      </JRField>

      <!-- TEMP: onboarding limited to Electric; restore Trade select when multi-trade opens.
      <JRField
        :label="t('onboarding.company.tradeType')"
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
            :placeholder="t('onboarding.company.tradePlaceholder')"
            :invalid="invalid"
            :aria-describedby="describedby || undefined"
            @update:modelValue="validateField('business_type')" />
        </template>
      </JRField>
      -->

      <UploadLogo v-model="localData.logo" :error="errors.logo || ''" />

      <JRField
        :label="t('onboarding.company.address')"
        inputId="company_address"
        :hint="t('onboarding.company.addressHint')"
        :error="errors.address || ''">
        <template #default="{ invalid, describedby }">
          <JRTextarea
            inputId="company_address"
            v-model="localData.address"
            :invalid="invalid"
            :aria-describedby="describedby || undefined"
            :rows="3"
            :placeholder="t('onboarding.company.addressPlaceholder')" />
        </template>
      </JRField>

      <JRField
        :label="t('onboarding.company.monthlyVolume')"
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
            :placeholder="t('onboarding.company.monthlyPlaceholder')"
            :invalid="invalid"
            :aria-describedby="describedby || undefined"
            @update:modelValue="validateField('monthly_operations')" />
        </template>
      </JRField>

      <JRField
        :label="t('onboarding.company.crewCount')"
        required
        inputId="crew_count"
        :hint="t('onboarding.company.crewHint')"
        :error="errors.crew_count || ''">
        <template #default="{ invalid, describedby }">
          <JRInput
            inputId="crew_count"
            :modelValue="crewCountDisplay"
            :invalid="invalid"
            :aria-describedby="describedby || undefined"
            inputmode="numeric"
            :placeholder="t('onboarding.company.crewPlaceholder')"
            @update:modelValue="onCrewCount" />
        </template>
      </JRField>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { JRField, JRInput, JRSelect, JRTextarea } from '@ui'
import UploadLogo from './UploadLogo.vue'

const { t } = useI18n({ useScope: 'global' })

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

/* TEMP: restore with Trade / business type JRField above.
const businessTypeOptions = computed(() => [
  { value: 'electric', label: t('onboarding.company.trades.electric') },
  { value: 'air_conditioning', label: t('onboarding.company.trades.air_conditioning') },
  { value: 'solar', label: t('onboarding.company.trades.solar') },
  { value: 'plumbing', label: t('onboarding.company.trades.plumbing') },
  { value: 'hvac', label: t('onboarding.company.trades.hvac') },
  { value: 'general', label: t('onboarding.company.trades.general') },
])
*/

const monthlyOperationsOptions = computed(() => [
  { value: '0-10', label: t('onboarding.company.monthly.0-10') },
  { value: '11-25', label: t('onboarding.company.monthly.11-25') },
  { value: '26-50', label: t('onboarding.company.monthly.26-50') },
  { value: '51-100', label: t('onboarding.company.monthly.51-100') },
  { value: '100+', label: t('onboarding.company.monthly.100+') },
])

const localData = reactive({
  business_name: props.modelValue.business_name || '',
  // TEMP default: Electric-only onboarding (client_type still editable in Django admin).
  business_type: props.modelValue.business_type || 'electric',
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
