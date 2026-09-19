<template>
  <SidebarLayout v-if="shouldShowNavbar" class="jr-app-shell">
    <SidebarBackdrop
      v-if="isMobile && sidebarOpen"
      class="jr-shell-sidebar__backdrop" />

    <Sidebar
      id="jr-main-sidebar"
      class="jr-shell-sidebar"
      variant="sidebar"
      side="left"
      :collapsible="isMobile ? 'offcanvas' : 'icon'"
      :overlay="isMobile"
      v-model:open="sidebarOpen"
      width="17rem"
      icon-width="3.25rem">
      <SidebarSpacer />
      <SidebarAside>
        <SidebarPanel>
          <SidebarHeader class="jr-shell-sidebar__header">
            <SidebarMenu>
              <SidebarMenuItem>
                <!-- Desktop: collapse / expand to icon mode -->
                <SidebarTrigger
                  v-if="!isMobile"
                  as="button"
                  class="jr-shell-sidebar__trigger"
                  target="jr-main-sidebar"
                  aria-label="Toggle navigation sidebar">
                  <Bars />
                  <span class="jr-shell-sidebar__trigger-label">MENU</span>
                </SidebarTrigger>
                <!-- Mobile: tenant brand (unchanged) -->
                <SidebarMenuButton
                  v-else
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

          <!-- Desktop: native sidebar groups -->
          <SidebarContent v-if="!isMobile" class="jr-shell-sidebar__content">
            <SidebarGroup v-if="workflowMenuItems.length">
              <SidebarGroupLabel>Workflow</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem
                    v-for="item in workflowMenuItems"
                    :key="item.text">
                    <SidebarMenuButton
                      :is-active="isSubRouteActive(item, workflowMenuItems)"
                      @click="navigateTo(item.route)">
                      <component :is="iconFor(item.icon)" />
                      <span>{{ item.text }}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>

            <SidebarGroup v-if="moduleMenuItems.length">
              <SidebarGroupLabel>Modules</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem
                    v-for="item in moduleMenuItems"
                    :key="item.text"
                    :collapsible="true"
                    :open="openModuleKey === item.text"
                    @update:open="
                      (value) => onModuleOpenChange(item.text, value)
                    ">
                    <SidebarMenuButton
                      as-child
                      :is-active="isDropdownActive(item)"
                      v-slot="{ class: btnClass, a11yAttrs }">
                      <button
                        type="button"
                        :class="btnClass"
                        v-bind="moduleButtonAttrs(a11yAttrs)"
                        @click="onModuleButtonClick(item)">
                        <component :is="iconFor(item.icon)" />
                        <span>{{ item.text }}</span>
                        <ChevronDown class="jr-shell-sidebar__chevron" />
                      </button>
                    </SidebarMenuButton>
                    <SidebarMenuSub>
                      <SidebarMenuSubItem
                        v-for="subItem in visibleChildren(item)"
                        :key="subItem.route">
                        <SidebarMenuSubButton
                          :is-active="
                            isSubRouteActive(subItem, visibleChildren(item))
                          "
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

          <!-- Mobile: VirtualScroller + account footer -->
          <SidebarContent
            v-else
            class="jr-shell-sidebar__content jr-shell-sidebar__content--virtual">
            <VirtualScroller
              :items="mobileNavRows"
              :item-size="MOBILE_NAV_ITEM_SIZE"
              class="jr-shell-sidebar__virtual"
              :pt="{ root: { class: 'jr-shell-sidebar__virtual-root' } }">
              <template #item="{ item, options }">
                <div
                  :key="item.key"
                  :class="[
                    'jr-shell-sidebar__vs-row',
                    `jr-shell-sidebar__vs-row--${item.type}`,
                  ]"
                  :style="options.style">
                  <div
                    v-if="item.type === 'label'"
                    class="jr-shell-sidebar__vs-label"
                    role="presentation">
                    {{ item.text }}
                  </div>
                  <button
                    v-else-if="item.type === 'link'"
                    type="button"
                    class="jr-shell-sidebar__vs-btn"
                    :data-active="item.active ? 'true' : null"
                    :aria-current="item.active ? 'page' : null"
                    @click="navigateTo(item.route)">
                    <component :is="iconFor(item.icon)" aria-hidden="true" />
                    <span>{{ item.text }}</span>
                  </button>
                  <button
                    v-else-if="item.type === 'module'"
                    type="button"
                    class="jr-shell-sidebar__vs-btn"
                    :data-active="item.active ? 'true' : null"
                    :aria-expanded="item.open"
                    @click="onModuleButtonClick(item.source)">
                    <component :is="iconFor(item.icon)" aria-hidden="true" />
                    <span>{{ item.text }}</span>
                    <ChevronDown
                      class="jr-shell-sidebar__chevron"
                      :class="{
                        'jr-shell-sidebar__chevron--open': item.open,
                      }"
                      aria-hidden="true" />
                  </button>
                  <button
                    v-else-if="item.type === 'sub'"
                    type="button"
                    class="jr-shell-sidebar__vs-btn jr-shell-sidebar__vs-btn--sub"
                    :data-active="item.active ? 'true' : null"
                    :aria-current="item.active ? 'page' : null"
                    @click="navigateTo(item.route)">
                    <span>{{ item.text }}</span>
                  </button>
                </div>
              </template>
            </VirtualScroller>
          </SidebarContent>

          <SidebarFooter
            v-if="isMobile"
            class="jr-shell-sidebar__footer">
            <SidebarMenu>
              <SidebarMenuItem>
                <AppShellUserMenu
                  v-if="isLoggedIn"
                  surface="sidebar"
                  :user-name="userName"
                  :user-initials="userInitials"
                  :is-tenant-owner="isTenantOwner"
                  @navigate="navigateTo"
                  @logout="logout" />
                <SidebarMenuButton
                  v-else
                  as-child
                  v-slot="{ class: btnClass, a11yAttrs }">
                  <router-link
                    to="/login"
                    v-bind="a11yAttrs"
                    :class="[btnClass, 'jr-shell-topbar__login--sidebar']"
                    @click="closeSidebar">
                    Log In
                  </router-link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarFooter>

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
        :brand-logo-src="brandLogoSrc"
        :brand-logo-alt="brandLogoAlt"
        @navigate="navigateTo"
        @logout="logout"
        @open-assistant="openAssistant"
        @brand-logo-error="onTenantLogoError" />

          <header class="jr-shell-mobile-bar" aria-label="App navigation">
        <SidebarTrigger
          class="jr-shell-mobile-bar__menu"
          target="jr-main-sidebar"
          :aria-label="
            sidebarOpen ? 'Close navigation menu' : 'Open navigation menu'
          "
          :aria-expanded="sidebarOpen">
          <Bars />
          <span class="jr-shell-mobile-bar__menu-label">MENU</span>
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
import BuildingColumns from "@primeicons/vue/building-columns";
import Bars from "@primeicons/vue/bars";
import CalendarPlus from "@primeicons/vue/calendar-plus";
import ChartBar from "@primeicons/vue/chart-bar";
import ChevronDown from "@primeicons/vue/chevron-down";
import Eye from "@primeicons/vue/eye";
import File from "@primeicons/vue/file";
import Home from "@primeicons/vue/home";
import List from "@primeicons/vue/list";
import MapMarker from "@primeicons/vue/map-marker";
import Sparkles from "@primeicons/vue/sparkles";
import Users from "@primeicons/vue/users";
import AppShellTopbar from "./AppShellTopbar.vue";
import AppShellUserMenu from "./AppShellUserMenu.vue";
import Sidebar from "primevue/sidebar";
import SidebarAside from "primevue/sidebaraside";
import SidebarBackdrop from "primevue/sidebarbackdrop";
import SidebarContent from "primevue/sidebarcontent";
import SidebarFooter from "primevue/sidebarfooter";
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
import VirtualScroller from "primevue/virtualscroller";
import FooterComponent from "./FooterComponent.vue";
import NavbarMessagesDropdown from "./NavbarMessagesDropdown.vue";
import { openAssistant } from "@/utils/assistantBus";

const NAV_ICONS = {
  home: Home,
  schedule: CalendarPlus,
  transactions: List,
  contracts: File,
  workAccounts: BuildingColumns,
  workOrderViewer: Eye,
  reports: ChartBar,
  inventory: Box,
  pricing: File,
  entities: Building,
  crews: Users,
  communities: MapMarker,
};

const MOBILE_BREAKPOINT = 1024;
/** Match .jr-shell-sidebar__vs-row / vs-btn height (2.75rem). */
const MOBILE_NAV_ITEM_SIZE = 44;

export default {
  name: "NavbarComponent",
  components: {
    AppShellUserMenu,
    Bars,
    Box,
    Building,
    BuildingColumns,
    CalendarPlus,
    ChartBar,
    ChevronDown,
    Eye,
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
    SidebarFooter,
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
    VirtualScroller,
  },
  data() {
    return {
      MOBILE_NAV_ITEM_SIZE,
      isLoggedIn: false,
      isMobile: false,
      sidebarOpen: false,
      menuItems: [
        {
          text: "Schedule",
          route: "/schedule",
          icon: "schedule",
          permission: "appschedule.view_event",
          group: "workflow",
        },
        {
          text: "Transactions",
          route: "/transactions",
          icon: "transactions",
          permission: "apptransactions.view_document",
          group: "workflow",
        },
        {
          text: "Piece Work Contracts",
          route: "/contracts",
          icon: "contracts",
          permission: "ctrctsapp.view_contract",
          group: "workflow",
        },
        {
          text: "Work Accounts",
          route: "/work-accounts",
          icon: "workAccounts",
          permission: "apptransactions.view_workaccount",
          group: "workflow",
        },
        {
          text: "Work Order Viewer",
          route: "/work-accounts/viewer",
          icon: "workOrderViewer",
          permission: "apptransactions.view_workaccount",
          group: "workflow",
        },
        {
          text: "Measure the Operation",
          route: "/reports-exports",
          icon: "reports",
          permission: "apptransactions.change_workaccount",
          group: "workflow",
        },
        {
          text: "Inventory",
          icon: "inventory",
          group: "modules",
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
          text: "Piece Work Pricing",
          icon: "pricing",
          group: "modules",
          children: [
            {
              text: "Piece Work Prices",
              route: "/work-prices",
              permission: "ctrctsapp.view_workprice",
            },
            {
              text: "Work Prices per Builder",
              route: "/work-prices-builders",
              permission: "ctrctsapp.change_workprice",
            },
          ],
        },
        {
          text: "Entities",
          icon: "entities",
          group: "modules",
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
          group: "modules",
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
          group: "modules",
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
      return this.menuItems.filter(
        (item) =>
          item.group === "modules" &&
          item.children &&
          this.visibleChildren(item).length > 0
      );
    },
    workflowMenuItems() {
      return this.menuItems.filter(
        (item) => item.group === "workflow" && this.canAccessMenuItem(item)
      );
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
    /** Flattened nav rows for mobile VirtualScroller. */
    mobileNavRows() {
      const rows = [];

      if (this.workflowMenuItems.length) {
        rows.push({
          type: "label",
          key: "label-workflow",
          text: "Workflow",
        });
        for (const item of this.workflowMenuItems) {
          rows.push({
            type: "link",
            key: `wf-${item.route}`,
            text: item.text,
            route: item.route,
            icon: item.icon,
            active: this.isSubRouteActive(item, this.workflowMenuItems),
          });
        }
      }

      if (this.moduleMenuItems.length) {
        rows.push({
          type: "label",
          key: "label-modules",
          text: "Modules",
        });
        for (const item of this.moduleMenuItems) {
          const children = this.visibleChildren(item);
          const open = this.openModuleKey === item.text;
          rows.push({
            type: "module",
            key: `mod-${item.text}`,
            text: item.text,
            icon: item.icon,
            open,
            active: this.isDropdownActive(item),
            source: item,
          });
          if (open) {
            for (const sub of children) {
              rows.push({
                type: "sub",
                key: `sub-${sub.route}`,
                text: sub.text,
                route: sub.route,
                active: this.isSubRouteActive(sub, children),
              });
            }
          }
        }
      }

      return rows;
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
    canAccessMenuItem(item) {
      if (!item?.permission) return true;
      try {
        return !!this.hasPermission?.(item.permission);
      } catch {
        return false;
      }
    },
    visibleChildren(item) {
      return (item?.children || []).filter((child) =>
        this.canAccessMenuItem(child)
      );
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
      document.body.style.overflow = mobile && this.sidebarOpen ? "hidden" : "";
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
      const path = this.$route.path;
      return path === route || path.startsWith(`${route}/`);
    },
    /**
     * Among sibling menu routes, only the most specific match is active
     * (e.g. /crews/trucks → Trucks, not also Crews at /crews).
     */
    isSubRouteActive(subItem, siblings = []) {
      if (!subItem?.route || !this.isRouteActive(subItem.route)) return false;
      const path = this.$route.path;
      const betterMatch = (siblings || []).some((other) => {
        if (!other?.route || other.route === subItem.route) return false;
        if (other.route.length <= subItem.route.length) return false;
        return path === other.route || path.startsWith(`${other.route}/`);
      });
      return !betterMatch;
    },
    isDropdownActive(item) {
      return this.visibleChildren(item).some((subItem) =>
        this.isRouteActive(subItem.route)
      );
    },
    syncOpenModule() {
      const active = this.moduleMenuItems.find((item) =>
        this.isDropdownActive(item)
      );
      this.openModuleKey = active ? active.text : null;
    },
    /** Drop PrimeVue toggle onClick so we own expand + open-module behavior. */
    moduleButtonAttrs(a11yAttrs = {}) {
      const { onClick, ...rest } = a11yAttrs;
      return rest;
    },
    onModuleButtonClick(item) {
      if (!item?.text) return;
      // PC icon rail: expand sidebar and open the clicked module group
      if (!this.isMobile && !this.sidebarOpen) {
        this.sidebarOpen = true;
        this.openModuleKey = item.text;
        return;
      }
      // Expanded (or mobile): accordion toggle for this module
      this.openModuleKey = this.openModuleKey === item.text ? null : item.text;
    },
    onModuleOpenChange(text, isOpen) {
      // Fallback if something else toggles the item
      if (!this.isMobile && !this.sidebarOpen) {
        this.sidebarOpen = true;
        this.openModuleKey = text;
        return;
      }
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
