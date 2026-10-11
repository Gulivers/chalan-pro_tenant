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
      return name ? `Account menu for ${name}` : "Account menu";
    },
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
