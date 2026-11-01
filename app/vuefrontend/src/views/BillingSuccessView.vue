<template>
  <JRPage>
    <div class="mx-auto flex min-h-[50vh] max-w-xl flex-col items-center justify-center px-4 py-12 text-center">
      <h1 class="mb-3 text-2xl font-semibold text-jr-success">Payment received</h1>
      <p class="mb-6 text-jr-muted">
        Thank you. Your subscription is being activated. This may take a minute.
      </p>
      <div class="flex flex-wrap items-center justify-center gap-2">
        <JRButton type="button" variant="primary" @click="router.push('/')">
          Go to dashboard
        </JRButton>
        <JRButton type="button" variant="secondary" @click="router.push('/billing')">
          View billing
        </JRButton>
      </div>
    </div>
  </JRPage>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { JRPage, JRButton } from '@/ui'
import { fetchBillingStatus } from '@/api/billing'

const router = useRouter()

onMounted(async () => {
  try {
    await fetchBillingStatus()
  } catch {
    /* ignore */
  }
})
</script>
