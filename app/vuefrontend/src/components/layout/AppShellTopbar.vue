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
      <template v-if="isLoggedIn">
        <button
          type="button"
          class="jr-shell-topbar__user"
          :class="{ 'jr-shell-topbar__user--open': userMenuOpen }"
          :aria-expanded="userMenuOpen"
          aria-haspopup="menu"
          @click="toggleUserMenu">
          <span class="jr-shell-topbar__avatar">{{ userInitials }}</span>
          <span class="jr-shell-topbar__user-label">{{ userName }}</span>
          <ChevronDown class="jr-shell-topbar__user-chevron" aria-hidden="true" />
        </button>
        <Menu
          ref="userMenu"
          :model="userMenuModel"
          :pt="userMenuPt"
          :base-z-index="1050"
          popup
          @show="userMenuOpen = true"
          @hide="userMenuOpen = false" />
      </template>
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
import ChevronDown from "@primeicons/vue/chevron-down";
import Home from "@primeicons/vue/home";
import Sparkles from "@primeicons/vue/sparkles";
import Menu from "primevue/menu";
import NavbarMessagesDropdown from "./NavbarMessagesDropdown.vue";

export default {
  name: "AppShellTopbar",
  components: {
    ChevronDown,
    Home,
    Menu,
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
  data() {
    return {
      userMenuOpen: false,
      userMenuPt: {
        root: { class: "jr-overlay jr-shell-topbar-menu" },
      },
    };
  },
  computed: {
    userMenuModel() {
      const items = [
        {
          label: "Welcome",
          class: "jr-shell-topbar-menu__heading",
          disabled: true,
        },
        {
          label: this.userName || "User",
          class: "jr-shell-topbar-menu__name",
          disabled: true,
        },
        { separator: true },
        {
          label: "About",
          command: () => this.$emit("navigate", "/about"),
        },
      ];

      if (this.isTenantOwner) {
        items.push({
          label: "Billing",
          command: () => this.$emit("navigate", "/billing"),
        });
      }

      items.push(
        { separator: true },
        {
          label: "Configuration",
          class: "jr-shell-topbar-menu__heading",
          disabled: true,
        },
        {
          label: "Transactions Types",
          command: () => this.$emit("navigate", "/document-types"),
        },
        {
          label: "Inventory Master Data Setup",
          command: () => this.$emit("navigate", "/inventory-master-data-setup"),
        },
        { separator: true },
        {
          label: "Log Out",
          class: "jr-menu-danger",
          command: () => this.$emit("logout"),
        }
      );

      return items;
    },
  },
  methods: {
    toggleUserMenu(event) {
      this.userMenuOpen = !this.userMenuOpen;
      this.$refs.userMenu?.toggle?.(event);
    },
  },
};
</script>
