<template>
  <div class="onboarding-verify-view onboarding-wizard">
    <div class="wizard-container">
      <div class="wizard-card card shadow-lg">
        <div class="card-body p-5 text-center">
          <div v-if="status === 'loading'">
            <div class="spinner-border text-primary mb-3" role="status"></div>
            <h1 class="h4 fw-bold">Confirming your email…</h1>
            <p class="text-muted mb-0">Creating your JobRhythm workspace. This may take a minute.</p>
          </div>

          <div v-else-if="status === 'success'">
            <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
            <h1 class="h4 fw-bold">Workspace ready</h1>
            <p class="text-muted">Redirecting you to sign in…</p>
          </div>

          <div v-else>
            <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
            <h1 class="h4 fw-bold">Verification failed</h1>
            <p class="text-muted">{{ errorMessage }}</p>
            <router-link to="/onboarding" class="btn btn-primary mt-3">
              Start onboarding again
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { verifyOnboardingEmail } from '@/api/onboarding'

const route = useRoute()
const status = ref('loading')
const errorMessage = ref('')

onMounted(async () => {
  const token = (route.query.token || '').toString().trim()
  if (!token) {
    status.value = 'error'
    errorMessage.value = 'Missing verification token.'
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
    errorMessage.value = error.message || 'This verification link is invalid or expired.'
  }
})
</script>

<style scoped>
.onboarding-verify-view {
  min-height: 100vh;
  padding: 2rem 1rem;
}

.wizard-container {
  max-width: 640px;
  margin: 0 auto;
}
</style>
