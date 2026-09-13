<template>
  <SidebarLayout v-if="shouldShowNavbar" class="jr-app-shell">
    <SidebarBackdrop v-if="isMobile && sidebarOpen" class="jr-shell-sidebar__backdrop" />

    <Sidebar
      id="jr-main-sidebar"
      class="jr-shell-sidebar"
      variant="sidebar"
      side="left"
      :collapsible="isMobile ? 'offcanvas' : 'icon'"
      :overlay="true"
      :open-on-hover="!isMobile"
      v-model:open="sidebarOpen"
      width="17rem"
      icon-width="3.25rem">
      <SidebarSpacer />
      <SidebarAside>
        <SidebarPanel>
          <SidebarHeader class="jr-shell-sidebar__header">
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  as-child
                  v-slot="{ class: btnClass, a11yAttrs }">
                  <router-link
                    to="/"
                    v-bind="a11yAttrs"
                    :class="[btnClass, 'jr-shell-sidebar__brand-btn']"
                    :aria-label="brandLogoAlt"
                    @click="closeSidebar">
                    <img
                      :src="brandLogoSrc"
                      alt=""
                      class="jr-shell-sidebar__brand-logo"
                      @error="onTenantLogoError" />
                  </router-link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarHeader>

          <SidebarContent class="jr-shell-sidebar__content">
            <SidebarGroup>
              <SidebarGroupLabel>Modules</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem
                    v-for="item in moduleMenuItems"
                    :key="item.text"
                    :collapsible="true"
                    :open="openModuleKey === item.text"
                    @update:open="(value) => onModuleOpenChange(item.text, value)">
                    <SidebarMenuButton :is-active="isDropdownActive(item)">
                      <component :is="iconFor(item.icon)" />
                      <span>{{ item.text }}</span>
                      <ChevronDown class="jr-shell-sidebar__chevron" />
                    </SidebarMenuButton>
                    <SidebarMenuSub>
                      <SidebarMenuSubItem
                        v-for="subItem in item.children"
                        :key="subItem.route">
                        <SidebarMenuSubButton
                          :is-active="isRouteActive(subItem.route)"
                          @click="navigateTo(subItem.route)">
                          <span>{{ subItem.text }}</span>
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    </SidebarMenuSub>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>

          <SidebarRail />
        </SidebarPanel>
      </SidebarAside>
    </Sidebar>

    <SidebarMain class="jr-app-shell__main">
      <AppShellTopbar
        :dashboard-active="isRouteActive('/')"
        :show-assistant="showAssistantButton"
        :is-logged-in="isLoggedIn"
        :user-name="userName"
        :user-initials="userInitials"
        :is-tenant-owner="isTenantOwner"
        @navigate="navigateTo"
        @logout="logout"
        @open-assistant="openAssistant" />

      <header class="jr-shell-mobile-bar" aria-label="App navigation">
        <SidebarTrigger
          class="jr-shell-mobile-bar__menu"
          target="jr-main-sidebar"
          aria-label="Open navigation menu">
          <Bars />
        </SidebarTrigger>

        <router-link
          class="jr-shell-mobile-bar__brand"
          to="/"
          @click="closeSidebar">
          <img
            :src="brandLogoSrc"
            :alt="brandLogoAlt"
            class="jr-shell-mobile-bar__logo"
            @error="onTenantLogoError" />
        </router-link>

        <div class="jr-shell-mobile-bar__actions">
          <button
            v-if="showAssistantButton"
            type="button"
            class="jr-shell-mobile-bar__action"
            aria-label="Open JobRhythm Assistant"
            @click="openAssistant">
            <Sparkles />
          </button>
          <NavbarMessagesDropdown variant="rail" />
        </div>
      </header>

      <main class="jr-app-shell__content">
        <slot />
      </main>
      <FooterComponent />
    </SidebarMain>
  </SidebarLayout>
</template>

<script>
import Box from "@primeicons/vue/box";
import Building from "@primeicons/vue/building";
import Bars from "@primeicons/vue/bars";
import ChevronDown from "@primeicons/vue/chevron-down";
import File from "@primeicons/vue/file";
import Home from "@primeicons/vue/home";
import List from "@primeicons/vue/list";
import MapMarker from "@primeicons/vue/map-marker";
import Sparkles from "@primeicons/vue/sparkles";
import Users from "@primeicons/vue/users";
import AppShellTopbar from "./AppShellTopbar.vue";
import Sidebar from "primevue/sidebar";
import SidebarAside from "primevue/sidebaraside";
import SidebarBackdrop from "primevue/sidebarbackdrop";
import SidebarContent from "primevue/sidebarcontent";
import SidebarGroup from "primevue/sidebargroup";
import SidebarGroupContent from "primevue/sidebargroupcontent";
import SidebarGroupLabel from "primevue/sidebargrouplabel";
import SidebarHeader from "primevue/sidebarheader";
import SidebarLayout from "primevue/sidebarlayout";
import SidebarMain from "primevue/sidebarmain";
import SidebarMenu from "primevue/sidebarmenu";
import SidebarMenuButton from "primevue/sidebarmenubutton";
import SidebarMenuItem from "primevue/sidebarmenuitem";
import SidebarMenuSub from "primevue/sidebarmenusub";
import SidebarMenuSubButton from "primevue/sidebarmenusubbutton";
import SidebarMenuSubItem from "primevue/sidebarmenusubitem";
import SidebarPanel from "primevue/sidebarpanel";
import SidebarRail from "primevue/sidebarrail";
import SidebarSpacer from "primevue/sidebarspacer";
import SidebarTrigger from "primevue/sidebartrigger";
import FooterComponent from "./FooterComponent.vue";
import NavbarMessagesDropdown from "./NavbarMessagesDropdown.vue";
import { openAssistant } from "@/utils/assistantBus";

const NAV_ICONS = {
  home: Home,
  operations: List,
  inventory: Box,
  contracts: File,
  entities: Building,
  crews: Users,
  communities: MapMarker,
};

const MOBILE_BREAKPOINT = 1024;

export default {
  name: "NavbarComponent",
  components: {
    Bars,
    Box,
    Building,
    ChevronDown,
    File,
    AppShellTopbar,
    FooterComponent,
    Home,
    List,
    MapMarker,
    NavbarMessagesDropdown,
    Sidebar,
    SidebarAside,
    SidebarBackdrop,
    SidebarContent,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarLayout,
    SidebarMain,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarMenuSub,
    SidebarMenuSubButton,
    SidebarMenuSubItem,
    SidebarPanel,
    SidebarRail,
    SidebarSpacer,
    SidebarTrigger,
    Sparkles,
    Users,
  },
  data() {
    return {
      isLoggedIn: false,
      isMobile: false,
      sidebarOpen: false,
      menuItems: [
        { text: "Dashboard", route: "/", icon: "home" },
        {
          text: "Operations",
          icon: "operations",
          children: [
            { text: "Schedule", route: "/schedule" },
            { text: "Work Order Viewer", route: "/chat-general" },
            {
              text: "Transactions",
              route: "/transactions",
              permission: "apptransactions.view_transaction",
            },
            {
              text: "Work Accounts",
              route: "/work-accounts",
              permission: "apptransactions.view_workaccount",
            },
          ],
        },
        {
          text: "Inventory",
          icon: "inventory",
          children: [
            {
              text: "Dashboard",
              route: "/inventory-dashboard",
              permission: "appinventory.view_product",
            },
            {
              text: "Products",
              route: "/products",
              permission: "appinventory.view_product",
            },
            {
              text: "Serialized Items",
              route: "/serialized-items",
              permission: "appinventory.view_serializeditem",
            },
            {
              text: "Inventory Transfers",
              route: "/inventory-transfers",
              permission: "appinventory.view_inventorytransfer",
            },
            {
              text: "Warehouses",
              route: "/warehouses",
              permission: "appinventory.view_warehouse",
            },
            {
              text: "Product Categories",
              route: "/product-categories",
              permission: "appinventory.view_productcategory",
            },
            {
              text: "Product Brands",
              route: "/product-brands",
              permission: "appinventory.view_productbrand",
            },
            {
              text: "Price Types",
              route: "/price-types",
              permission: "appinventory.view_pricetype",
            },
            {
              text: "Unit Measures",
              route: "/unit-measures",
              permission: "appinventory.view_unitofmeasure",
            },
            {
              text: "Unit Categories",
              route: "/unit-categories",
              permission: "appinventory.view_unitcategory",
            },
          ],
        },
        {
          text: "Contracts & Pricing",
          icon: "contracts",
          children: [
            { text: "Contracts", route: "/contracts" },
            { text: "Piece Work Prices", route: "/work-prices" },
            { text: "Work Prices per Builder", route: "/work-prices-builders" },
          ],
        },
        {
          text: "Entities",
          icon: "entities",
          children: [
            {
              text: "Builders & Parties",
              route: "/builders",
              permission: "ctrctsapp.view_builder",
            },
            {
              text: "Communities",
              route: "/jobs",
              permission: "ctrctsapp.view_job",
            },
            {
              text: "House Models",
              route: "/house-models",
              permission: "ctrctsapp.view_housemodel",
            },
            {
              text: "Party Types",
              route: "/party-types",
              permission: "apptransactions.view_partytype",
            },
            {
              text: "Party Categories",
              route: "/party-categories",
              permission: "apptransactions.view_partycategory",
            },
          ],
        },
        {
          text: "Crews and Fleet",
          icon: "crews",
          children: [
            {
              text: "Categories",
              route: "/crews/categories",
              permission: "crewsapp.view_category",
            },
            {
              text: "Crews",
              route: "/crews",
              permission: "crewsapp.view_crew",
            },
            {
              text: "Trucks",
              route: "/crews/trucks",
              permission: "crewsapp.view_truck",
            },
            {
              text: "Truck Assignments",
              route: "/crews/truck-assignments",
              permission: "crewsapp.view_truckassignment",
            },
          ],
        },
        {
          text: "Communities",
          icon: "communities",
          children: [
            { text: "Communities Map", route: "/map" },
            {
              text: "Supervisor Communities",
              route: "/supervisor-communities",
            },
          ],
        },
      ],
      userName: "",
      isTenantOwner: false,
      tenantLogoUrl: null,
      tenantName: null,
      tenantLogoFailed: false,
      openModuleKey: null,
    };
  },
  computed: {
    jobrhythmLogoUrl() {
      const base = process.env.BASE_URL || "/";
      return `${base}img/jobrhythm-logo.png`;
    },
    brandLogoSrc() {
      if (this.tenantLogoFailed) {
        return this.jobrhythmLogoUrl;
      }
      return this.tenantLogoUrl || this.jobrhythmLogoUrl;
    },
    brandLogoAlt() {
      return this.tenantName || "JobRhythm";
    },
    shouldShowNavbar() {
      return !this.$route.meta.hideNavbar;
    },
    moduleMenuItems() {
      return this.menuItems.filter((item) => item.children);
    },
    userInitials() {
      const name = (this.userName || "JR").trim();
      if (!name) return "JR";
      const parts = name.split(/\s+/).filter(Boolean);
      if (parts.length === 1) {
        return parts[0].slice(0, 2).toUpperCase();
      }
      return `${parts[0][0] || ""}${parts[1][0] || ""}`.toUpperCase();
    },
    showAssistantButton() {
      if (!this.isLoggedIn) return false;
      try {
        const raw = localStorage.getItem("userPermissions");
        if (!raw) return true;
        const parsed = JSON.parse(raw);
        const perms = parsed?.permissions;
        if (!Array.isArray(perms)) return true;
        return perms.includes("apptransactions.view_document");
      } catch {
        return true;
      }
    },
  },
  mounted() {
    this.syncViewport();
    this.checkUserIdentity();
    this.syncOpenModule();
    this._onResize = () => this.syncViewport();
    window.addEventListener("resize", this._onResize, { passive: true });
  },
  beforeUnmount() {
    if (this._onResize) {
      window.removeEventListener("resize", this._onResize);
    }
    document.body.style.overflow = "";
  },
  methods: {
    iconFor(name) {
      return NAV_ICONS[name] || Home;
    },
    syncViewport() {
      const mobile = window.innerWidth < MOBILE_BREAKPOINT;
      if (!mobile && this.isMobile) {
        this.sidebarOpen = false;
      }
      if (mobile && !this.isMobile) {
        this.sidebarOpen = false;
      }
      this.isMobile = mobile;
      document.body.style.overflow =
        mobile && this.sidebarOpen ? "hidden" : "";
    },
    checkUserIdentity() {
      const token = localStorage.getItem("authToken");
      this.isLoggedIn = !!token;
      if (!this.isLoggedIn) {
        this.userName = "";
        this.isTenantOwner = false;
        this.tenantLogoUrl = null;
        this.tenantName = null;
        this.tenantLogoFailed = false;
        return;
      }
      this.getAuthenticatedUser().then((user) => {
        if (user) {
          this.userName = user.username;
          this.isTenantOwner = !!user.is_tenant_owner;
          this.tenantLogoUrl = user.tenant_logo_url || null;
          this.tenantName = user.tenant_name || null;
          this.tenantLogoFailed = false;
        }
      });
    },
    onTenantLogoError() {
      if (this.tenantLogoUrl) {
        this.tenantLogoFailed = true;
      }
    },
    isRouteActive(route) {
      if (!route) return false;
      if (route === "/") {
        return this.$route.path === "/";
      }
      return this.$route.path === route || this.$route.path.startsWith(`${route}/`);
    },
    isDropdownActive(item) {
      return (
        item.children &&
        item.children.some((subItem) => this.isRouteActive(subItem.route))
      );
    },
    syncOpenModule() {
      const active = this.moduleMenuItems.find((item) => this.isDropdownActive(item));
      this.openModuleKey = active ? active.text : null;
    },
    onModuleOpenChange(text, isOpen) {
      this.openModuleKey = isOpen ? text : null;
    },
    navigateTo(route) {
      if (!route) return;
      this.$router.push(route);
      this.closeSidebar();
    },
    closeSidebar() {
      if (this.isMobile) {
        this.sidebarOpen = false;
        document.body.style.overflow = "";
      }
    },
    logout() {
      localStorage.removeItem("authToken");
      localStorage.removeItem("userPermissions");
      this.isLoggedIn = false;
      this.$router.push("/login");
      this.closeSidebar();
    },
    openAssistant() {
      this.closeSidebar();
      openAssistant();
    },
  },
  watch: {
    sidebarOpen(open) {
      if (this.isMobile) {
        document.body.style.overflow = open ? "hidden" : "";
      }
    },
    $route() {
      this.checkUserIdentity();
      this.syncOpenModule();
      this.closeSidebar();
    },
  },
};
</script>
