<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import * as Layout from "@components/layout";
import AssistantPanel from "@/components/assistant/AssistantPanel.vue";

const route = useRoute();
const showShellNav = computed(() => !route.meta.hideNavbar);
</script>

<template>
  <Layout.NavbarComponent v-if="showShellNav">
    <router-view />
  </Layout.NavbarComponent>
  <div v-else class="jr-app-shell--no-nav">
    <router-view />
    <Layout.FooterComponent />
  </div>
  <AssistantPanel />
</template>

<style>
.jr-app-shell--no-nav {
  min-height: 100vh;
  text-align: left;
  font-family: var(--font-jr-sans);
  color: var(--color-jr-text);
  background: var(--color-jr-page);
}

label {
  color: var(--color-jr-text, #111827);
}
</style>
