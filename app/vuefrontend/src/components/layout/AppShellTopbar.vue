<template>
  <header class="jr-shell-topbar" aria-label="Application header">
    <nav class="jr-shell-topbar__nav" aria-label="Primary navigation">
      <router-link
        to="/"
        class="jr-shell-topbar__brand"
        :aria-label="brandLogoAlt">
        <img
          :src="brandLogoSrc"
          alt=""
          class="jr-shell-topbar__brand-logo"
          @error="$emit('brand-logo-error')" />
      </router-link>

      <router-link
        to="/"
        class="jr-shell-topbar__nav-link"
        :class="{ 'jr-shell-topbar__nav-link--active': dashboardActive }">
        <Home class="jr-shell-topbar__nav-icon" aria-hidden="true" />
        <span>Dashboard</span>
      </router-link>

      <button
        v-if="showAssistant"
        type="button"
        class="jr-shell-topbar__nav-link"
        @click="$emit('open-assistant')">
        <Sparkles class="jr-shell-topbar__nav-icon" aria-hidden="true" />
        <span>Assistant</span>
      </button>

      <NavbarMessagesDropdown variant="topbar" />
    </nav>

    <div class="jr-shell-topbar__actions">
      <AppShellUserMenu
        v-if="isLoggedIn"
        surface="topbar"
        :user-name="userName"
        :user-initials="userInitials"
        :is-tenant-owner="isTenantOwner"
        @navigate="$emit('navigate', $event)"
        @logout="$emit('logout')" />
      <router-link
        v-else
        to="/login"
        class="jr-shell-topbar__login">
        Log In
      </router-link>
    </div>
  </header>
</template>

<script>
import Home from "@primeicons/vue/home";
import Sparkles from "@primeicons/vue/sparkles";
import AppShellUserMenu from "./AppShellUserMenu.vue";
import NavbarMessagesDropdown from "./NavbarMessagesDropdown.vue";

export default {
  name: "AppShellTopbar",
  components: {
    AppShellUserMenu,
    Home,
    NavbarMessagesDropdown,
    Sparkles,
  },
  props: {
    dashboardActive: {
      type: Boolean,
      default: false,
    },
    showAssistant: {
      type: Boolean,
      default: false,
    },
    isLoggedIn: {
      type: Boolean,
      default: false,
    },
    userName: {
      type: String,
      default: "",
    },
    userInitials: {
      type: String,
      default: "JR",
    },
    isTenantOwner: {
      type: Boolean,
      default: false,
    },
    brandLogoSrc: {
      type: String,
      default: "",
    },
    brandLogoAlt: {
      type: String,
      default: "JobRhythm",
    },
  },
  emits: ["navigate", "logout", "open-assistant", "brand-logo-error"],
};
</script>
