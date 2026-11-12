<template>
  <div class="turnstile-widget">
    <div ref="containerRef" class="turnstile-container"></div>
    <p v-if="loadError" class="jr-pilot">
      <span class="m-0 block text-sm text-jr-danger">{{ loadError }}</span>
    </p>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps({
  siteKey: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:token', 'error', 'ready'])

const containerRef = ref(null)
const loadError = ref('')
let widgetId = null

const loadTurnstileScript = () => new Promise((resolve, reject) => {
  if (window.turnstile) {
    resolve()
    return
  }
  const existing = document.querySelector('script[data-turnstile="1"]')
  if (existing) {
    existing.addEventListener('load', () => resolve(), { once: true })
    existing.addEventListener(
      'error',
      () => reject(new Error(t('onboarding.review.captchaLoadFailed'))),
      { once: true }
    )
    return
  }
  const script = document.createElement('script')
  script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'
  script.async = true
  script.defer = true
  script.dataset.turnstile = '1'
  script.onload = () => resolve()
  script.onerror = () => reject(new Error(t('onboarding.review.captchaLoadFailed')))
  document.head.appendChild(script)
})

const destroyWidget = () => {
  if (widgetId != null && window.turnstile) {
    try {
      window.turnstile.remove(widgetId)
    } catch (_) {
      /* ignore */
    }
    widgetId = null
  }
}

const renderWidget = async () => {
  loadError.value = ''
  destroyWidget()
  if (!props.siteKey) {
    loadError.value = t('onboarding.review.captchaNotConfigured')
    emit('error', loadError.value)
    return
  }
  if (!containerRef.value) {
    return
  }
  try {
    await loadTurnstileScript()
    widgetId = window.turnstile.render(containerRef.value, {
      sitekey: props.siteKey,
      callback: (token) => emit('update:token', token),
      'expired-callback': () => emit('update:token', ''),
      'error-callback': () => {
        loadError.value = t('onboarding.review.captchaVerifyFailed')
        emit('error', loadError.value)
        emit('update:token', '')
      },
    })
    emit('ready')
  } catch (error) {
    loadError.value = error.message || t('onboarding.review.captchaLoadFailed')
    emit('error', loadError.value)
  }
}

onMounted(renderWidget)
watch(() => props.siteKey, renderWidget)
onBeforeUnmount(destroyWidget)

defineExpose({
  reset: () => {
    if (widgetId != null && window.turnstile) {
      window.turnstile.reset(widgetId)
      emit('update:token', '')
    }
  },
})
</script>

<style scoped>
.turnstile-container {
  min-height: 65px;
}
</style>
