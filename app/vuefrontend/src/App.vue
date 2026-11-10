<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import * as Layout from "@components/layout";
import AssistantPanel from "@/components/assistant/AssistantPanel.vue";
import SetupAssistantWizard from "@/components/setup/SetupAssistantWizard.vue";

const route = useRoute();
const { locale } = useI18n({ useScope: "global" });
const showShellNav = computed(() => !route.meta.hideNavbar);
const showShellFooter = computed(() => !route.meta.hideFooter);
/** Remount shell chrome when language changes so PrimeVue layout state resets. */
const shellLocaleKey = computed(() => `shell-${locale.value}`);
</script>

<template>
  <Layout.NavbarComponent
    v-if="showShellNav"
    :key="shellLocaleKey" />
  <div
    v-else
    class="jr-app-shell--no-nav"
    :class="{ 'jr-app-shell--onboard': route.meta.hideFooter }">
    <router-view :key="route.fullPath" />
    <Layout.FooterComponent v-if="showShellFooter" />
  </div>
  <AssistantPanel />
  <SetupAssistantWizard />
</template>

<style>
.jr-app-shell--no-nav {
  min-height: 100vh;
  text-align: left;
  font-family: var(--font-jr-sans);
  color: var(--color-jr-text);
  background: var(--color-jr-page);
}

.jr-app-shell--onboard {
  background: var(--color-jr-surface, #fff);
}

label {
  color: var(--color-jr-text, #111827);
}
</style>
