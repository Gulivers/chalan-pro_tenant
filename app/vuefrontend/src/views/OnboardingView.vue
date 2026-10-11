<template>
  <div class="onboarding-view">
    <OnboardingWizard />
  </div>
</template>

<script setup>
import OnboardingWizard from '@/components/onboarding/OnboardingWizard.vue'
</script>

<style scoped>
.onboarding-view {
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--color-jr-surface, #fff);
}
</style>
