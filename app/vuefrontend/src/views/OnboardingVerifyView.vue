<template>
  <JRPage>
    <div class="mx-auto flex min-h-screen max-w-xl items-center px-4 py-8">
      <div class="w-full rounded-jr-panel border border-jr-border bg-jr-surface px-6 py-10 text-center">
        <div v-if="status === 'loading'">
          <ProgressSpinner
            class="mb-4"
            style="width: 2.5rem; height: 2.5rem"
            strokeWidth="4"
            :aria-label="t('onboarding.verifyPage.confirmingAria')" />
          <h1 class="mb-2 text-xl font-semibold">
            {{ t('onboarding.verifyPage.confirmingTitle') }}
          </h1>
          <p class="mb-0 text-jr-muted">
            {{ t('onboarding.verifyPage.confirmingLead') }}
          </p>
        </div>

        <div v-else-if="status === 'success'">
          <span class="mb-3 inline-flex text-jr-success" aria-hidden="true">
            <CheckCircle :size="36" />
          </span>
          <h1 class="mb-2 text-xl font-semibold">
            {{ t('onboarding.verifyPage.readyTitle') }}
          </h1>
          <p class="text-jr-muted">{{ t('onboarding.verifyPage.readyLead') }}</p>
        </div>

        <div v-else>
          <span class="mb-3 inline-flex text-jr-danger" aria-hidden="true">
            <ExclamationTriangle :size="36" />
          </span>
          <h1 class="mb-2 text-xl font-semibold">
            {{ t('onboarding.verifyPage.failedTitle') }}
          </h1>
          <p class="text-jr-muted">{{ errorMessage }}</p>
          <JRButton
            type="button"
            class="mt-4"
            variant="primary"
            @click="router.push('/onboarding')">
            {{ t('onboarding.verifyPage.startAgain') }}
          </JRButton>
        </div>
      </div>
    </div>
  </JRPage>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ProgressSpinner from 'primevue/progressspinner'
import CheckCircle from '@primeicons/vue/check-circle'
import ExclamationTriangle from '@primeicons/vue/exclamation-triangle'
import { JRPage, JRButton } from '@/ui'
import { verifyOnboardingEmail } from '@/api/onboarding'

const { t } = useI18n({ useScope: 'global' })
const route = useRoute()
const router = useRouter()
const status = ref('loading')
const errorMessage = ref('')

onMounted(async () => {
  const token = (route.query.token || '').toString().trim()
  if (!token) {
    status.value = 'error'
    errorMessage.value = t('onboarding.verifyPage.missingToken')
    return
  }

  try {
    const response = await verifyOnboardingEmail(token)
    status.value = 'success'
    if (response.url) {
      window.location.href = response.url
    } else if (response.tenant?.domain) {
      const protocol = window.location.protocol
      window.location.href = `${protocol}//${response.tenant.domain}/login/`
    }
  } catch (error) {
    status.value = 'error'
    errorMessage.value =
      error.message || t('onboarding.verifyPage.invalidLink')
  }
})
</script>
