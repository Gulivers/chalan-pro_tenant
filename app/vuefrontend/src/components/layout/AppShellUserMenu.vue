<template>
  <div class="jr-shell-user-menu" :class="`jr-shell-user-menu--${surface}`">
    <button
      type="button"
      class="jr-shell-topbar__user"
      :class="{ 'jr-shell-topbar__user--open': userMenuOpen }"
      :aria-label="accountMenuLabel"
      :aria-expanded="userMenuOpen"
      aria-haspopup="menu"
      @click="toggleUserMenu">
      <span class="jr-shell-topbar__avatar" aria-hidden="true">{{
        userInitials
      }}</span>
      <span class="jr-shell-topbar__user-label">{{ userName }}</span>
      <ChevronDown class="jr-shell-topbar__user-chevron" aria-hidden="true" />
    </button>
    <Menu
      ref="userMenu"
      :model="userMenuModel"
      :pt="userMenuPt"
      :base-z-index="1100"
      append-to="body"
      popup
      @show="userMenuOpen = true"
      @hide="userMenuOpen = false" />
  </div>
</template>

<script>
import ChevronDown from "@primeicons/vue/chevron-down";
import Menu from "primevue/menu";
import axios from "axios";
import { useTenantSetup } from "@/composables/useTenantSetup";
import { useAuthStore } from "@/stores/auth";
import i18n, { normalizeLocale } from "@/i18n";
import { applyPrimeVueLocale } from "@/i18n/primeLocale";

export default {
  name: "AppShellUserMenu",
  components: {
    ChevronDown,
    Menu,
  },
  props: {
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
    isStaff: {
      type: Boolean,
      default: false,
    },
    /** `topbar` = desktop header; `sidebar` = mobile drawer footer */
    surface: {
      type: String,
      default: "topbar",
      validator: (value) => ["topbar", "sidebar"].includes(value),
    },
  },
  emits: ["navigate", "logout"],
  data() {
    return {
      userMenuOpen: false,
      userMenuPt: {
        root: { class: "jr-overlay jr-shell-topbar-menu" },
      },
    };
  },
  computed: {
    accountMenuLabel() {
      const name = (this.userName || "").trim();
      return name
        ? this.$t("common.accountMenuFor", { name })
        : this.$t("common.accountMenu");
    },
    userMenuModel() {
      const items = [
        {
          label: this.$t("common.welcome"),
          class: "jr-shell-topbar-menu__heading",
          disabled: true,
        },
        {
          label: this.userName || this.$t("common.user"),
          class: "jr-shell-topbar-menu__name",
          disabled: true,
        },
        { separator: true },
        {
          label: this.$t("common.about"),
          command: () => this.$emit("navigate", "/about"),
        },
      ];

      if (this.isTenantOwner) {
        items.push({
          label: this.$t("common.billing"),
          command: () => this.$emit("navigate", "/billing"),
        });
        items.push({
          label: this.$t("nav.setupAssistant"),
          command: () => {
            const setup = useTenantSetup();
            setup.reopen().catch(() => {
              setup.openPanel();
            });
            this.$emit("navigate", "/");
          },
        });
      }

      items.push(
        { separator: true },
        {
          label: this.$t("common.configuration"),
          class: "jr-shell-topbar-menu__heading",
          disabled: true,
        },
        {
          label: this.$t("nav.transactionTypes"),
          command: () => this.$emit("navigate", "/document-types"),
        },
        {
          label: this.$t("nav.inventoryMasterDataSetup"),
          command: () => this.$emit("navigate", "/inventory-master-data-setup"),
        },
      );

      if (this.isStaff || this.isTenantOwner) {
        items.push({
          label: this.$t("nav.userPermissions"),
          command: () => this.$emit("navigate", "/user-permissions"),
        });
      }

      // Language: flat actions (no nested submenu). Nested PrimeVue Menu
      // items leave overlays and remount the model when locale changes.
      items.push(
        { separator: true },
        {
          label: `${this.$t("lang.toggleLabel")}: ${this.$t("lang.english")}`,
          command: () => this.setLanguage("en"),
        },
        {
          label: `${this.$t("lang.toggleLabel")}: ${this.$t("lang.spanish")}`,
          command: () => this.setLanguage("es"),
        },
        { separator: true },
        {
          label: this.$t("common.logOut"),
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
    async setLanguage(lang) {
      const next = normalizeLocale(lang);
      const current = normalizeLocale(i18n.global.locale.value);
      // Hide popup before locale swap so overlays/model don't stick.
      try {
        this.$refs.userMenu?.hide?.();
      } catch (_) {
        /* ignore */
      }
      this.userMenuOpen = false;
      if (current === next) return;

      i18n.global.locale.value = next;
      try {
        document.documentElement.lang = next;
      } catch (_) {
        /* ignore */
      }
      try {
        applyPrimeVueLocale(this.$primevue, next);
      } catch (_) {
        /* ignore */
      }
      try {
        const { data } = await axios.patch("/api/auth/me/", {
          preferred_language: next,
        });
        if (data) useAuthStore().setUser?.(data, { syncLocale: false });
      } catch (_) {
        /* keep local locale even if persist fails */
      }
    },
  },
};
</script>
