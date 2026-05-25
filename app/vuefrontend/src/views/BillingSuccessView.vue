<template>
  <div class="container py-5 text-center">
    <h1 class="h3 fw-bold text-success mb-3">Payment received</h1>
    <p class="text-muted mb-4">
      Thank you. Your subscription is being activated. This may take a minute.
    </p>
    <router-link class="btn btn-primary" to="/">Go to dashboard</router-link>
    <router-link class="btn btn-outline-secondary ms-2" to="/billing">
      View billing
    </router-link>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { fetchBillingStatus } from '@/api/billing'

onMounted(async () => {
  try {
    await fetchBillingStatus()
  } catch {
    /* ignore */
  }
})
</script>
