<template>
  <JRField
    :label="t('onboarding.logo.label')"
    inputId="company_logo"
    :hint="t('onboarding.logo.hint')"
    :error="localRejectMessage || error || ''">
    <div class="jr-onboard-logo">
      <input
        ref="fileInput"
        id="company_logo"
        type="file"
        accept="image/png,image/jpeg,image/jpg,image/gif"
        class="jr-onboard-logo__input"
        @change="handleFileChange" />

      <button
        v-if="!preview"
        type="button"
        class="jr-onboard-logo__drop"
        @click="triggerFileInput">
        <Upload class="jr-onboard-logo__icon" aria-hidden="true" />
        <span class="jr-onboard-logo__title">{{ t('onboarding.logo.upload') }}</span>
        <span class="jr-onboard-logo__hint">{{ t('onboarding.logo.clickHint') }}</span>
      </button>

      <div v-else class="jr-onboard-logo__preview">
        <img
          :src="preview"
          :alt="t('onboarding.logo.previewAlt')"
          class="jr-onboard-logo__img" />
        <div class="jr-onboard-logo__actions">
          <JRButton type="button" variant="secondary" size="sm" @click="triggerFileInput">
            {{ t('onboarding.logo.change') }}
          </JRButton>
          <JRButton type="button" variant="danger" size="sm" @click="removeLogo">
            {{ t('onboarding.logo.remove') }}
          </JRButton>
        </div>
      </div>
    </div>
  </JRField>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Upload from '@primeicons/vue/upload'
import { JRField, JRButton } from '@ui'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps({
  modelValue: {
    type: File,
    default: null,
  },
  error: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const preview = ref(null)
const localRejectMessage = ref('')

const triggerFileInput = () => {
  localRejectMessage.value = ''
  fileInput.value?.click()
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  localRejectMessage.value = ''

  if (!file) return

  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    localRejectMessage.value = t('onboarding.logo.tooLarge')
    emit('update:modelValue', null)
    preview.value = null
    return
  }

  const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    localRejectMessage.value = t('onboarding.logo.badType')
    emit('update:modelValue', null)
    preview.value = null
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    preview.value = e.target.result
  }
  reader.readAsDataURL(file)
  emit('update:modelValue', file)
}

const removeLogo = () => {
  localRejectMessage.value = ''
  emit('update:modelValue', null)
  preview.value = null
  if (fileInput.value) fileInput.value.value = ''
}

watch(
  () => props.modelValue,
  (newValue) => {
    if (!newValue && preview.value) preview.value = null
    if (newValue) localRejectMessage.value = ''
  }
)
</script>

<style scoped>
.jr-onboard-logo__input {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.jr-onboard-logo {
  position: relative;
}

.jr-onboard-logo__drop {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  min-height: 8.5rem;
  padding: 1.25rem;
  border: 1px dashed var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface-muted, #f9fafb);
  color: var(--color-jr-muted, #4b5563);
  cursor: pointer;
  text-align: center;
}

.jr-onboard-logo__drop:hover {
  border-color: var(--color-jr-primary, #2563eb);
  color: var(--color-jr-primary, #2563eb);
}

.jr-onboard-logo__icon {
  width: 1.5rem;
  height: 1.5rem;
  margin-bottom: 0.25rem;
}

.jr-onboard-logo__title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--color-jr-text, #111827);
}

.jr-onboard-logo__hint {
  font-size: 0.875rem;
}

.jr-onboard-logo__preview {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #fff);
}

.jr-onboard-logo__img {
  max-width: 10rem;
  max-height: 10rem;
  object-fit: contain;
}

.jr-onboard-logo__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
</style>
