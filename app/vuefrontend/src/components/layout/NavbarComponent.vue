<template>
  <nav
    v-if="shouldShowNavbar"
    class="navbar navbar-expand-xl navbar-dark bg-dark border-bottom border-body py-1 navbar-modern"
    :class="{ 'navbar-modern--menu-open': isNavbarOpen }">
    <!-- Móvil/tablet: atenúa el contenido detrás; no empuja el layout (ver skin-modern.css) -->
    <div
      v-show="isNavbarOpen"
      class="navbar-modern-backdrop"
      aria-hidden="true"
      @click="closeNavbar" />
    <div
      class="container-fluid navbar-modern-inner d-flex align-items-center ps-2 pe-3">
      <!-- Marca (JobRhythm logo — mismo asset que la landing en public/img) -->
      <router-link
        class="navbar-brand py-0 d-flex align-items-center"
        to="/"
        @click="closeNavbar">
        <img
          :src="brandLogoSrc"
          :alt="brandLogoAlt"
          class="navbar-brand-logo"
          width="200"
          height="50"
          @error="onTenantLogoError" />
      </router-link>
      <!-- Botón de mensajes (fuera del collapsible, se mantiene) -->
      <ul v-if="shouldShowNavbar" class="navbar-nav me-2">
        <li class="nav-item d-flex align-items-center">
          <NavbarMessagesDropdown v-if="shouldShowNavbar" />
        </li>
      </ul>
      <button
        class="navbar-toggler"
        type="button"
        @click="toggleNavbar"
        aria-controls="navbarNav"
        :aria-expanded="isNavbarOpen"
        aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div
        :class="['collapse', 'navbar-collapse', { show: isNavbarOpen }]"
        id="navbarNav">
        <!-- Menú izquierdo -->
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li
            v-for="(item, index) in menuItems"
            :key="index"
            :class="['nav-item', { dropdown: item.children }]">
            <template v-if="item.children">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                role="button"
                :class="{ 'text-orange': isDropdownActive(item) }"
                @click.prevent="toggleDropdown(index)">
                {{ item.text }}
              </a>
              <ul class="dropdown-menu" :class="{ show: item.isOpen }">
                <li
                  v-for="(subItem, subIndex) in item.children"
                  :key="subIndex">
                  <router-link
                    :to="subItem.route"
                    class="dropdown-item"
                    @click="closeNavbar">
                    {{ subItem.text }}
                  </router-link>
                </li>
              </ul>
            </template>
            <template v-else>
              <router-link
                :to="item.route"
                class="nav-link"
                @click="closeNavbar">
                {{ item.text }}
              </router-link>
            </template>
          </li>
        </ul>

        <!-- Menú derecho -->
        <ul class="navbar-nav ms-auto d-flex align-items-center">
          <!-- Dynamic Messages Dropdown Component -->
          <li class="nav-item" v-if="isLoggedIn">
            <div class="nav-item dropdown user-dropdown">
              <a
                class="nav-link dropdown-toggle user-dropdown-toggle d-flex align-items-center"
                href="#"
                role="button"
                @click.prevent="toggleUserDropdown"
                aria-expanded="false">
                <img
                  src="@/assets/img/user.svg"
                  alt="User"
                  class="user-icon me-2" />
              </a>
              <ul
                class="dropdown-menu dropdown-menu-end user-dropdown-menu"
                :class="{ show: isUserDropdownOpen }">
                <li class="user-dropdown-header">
                  <strong>Welcome</strong>
                  <div class="user-name">{{ userName }}</div>
                </li>
                <li>
                  <router-link
                    to="/about"
                    class="dropdown-item"
                    @click="closeNavbar">
                    About
                  </router-link>
                </li>
                <li v-if="isTenantOwner">
                  <router-link
                    to="/billing"
                    class="dropdown-item"
                    @click="closeNavbar">
                    Billing
                  </router-link>
                </li>
                <li>
                  <h6
                    class="dropdown-header text-muted mb-0 mt-1 px-3 py-1 small">
                    Configuration
                  </h6>
                </li>
                <li class="mx-1">
                  <router-link
                    to="/document-types"
                    class="dropdown-item"
                    @click="closeNavbar">
                    Transactions Types
                  </router-link>
                </li>
                <li class="mx-1">
                  <router-link
                    to="/inventory-master-data-setup"
                    class="dropdown-item"
                    @click="closeNavbar">
                    Inventory Master Data Setup
                  </router-link>
                </li>
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <router-link
                    to="/logout"
                    class="dropdown-item"
                    @click="logout">
                    Log Out
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link to="/login" class="nav-link" @click="closeNavbar">
              Log In
            </router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import NavbarMessagesDropdown from "./NavbarMessagesDropdown.vue";

export default {
  components: {
    NavbarMessagesDropdown,
  },
  data() {
    return {
      isLoggedIn: false,
      isNavbarOpen: false,
      isUserDropdownOpen: false,
      menuItems: [
        { text: "Dashboard", route: "/" },
        {
          text: "Operations",
          isOpen: false,
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
          isOpen: false,
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
          isOpen: false,
          children: [
            { text: "Contracts", route: "/contracts" },
            { text: "Piece Work Prices", route: "/work-prices" },
            { text: "Work Prices per Builder", route: "/work-prices-builders" },
          ],
        },
        {
          text: "Entities",
          isOpen: false,
          children: [
            {
              text: "Builders & Parties",
              route: "/builders",
              permission: "ctrctsapp.view_builder",
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
          isOpen: false,
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
          isOpen: false,
          children: [
            { text: "Communities Map", route: "/map" },
            {
              text: "Supervisor Communities",
              route: "/supervisor-communities",
            },
          ],
        },
        /* About y Configuration solo en el menú de usuario (evita desborde en pantallas medianas) */
      ],
      userName: "",
      isTenantOwner: false,
      /** URL absoluta del logo del tenant (desde /api/user_detail/) */
      tenantLogoUrl: null,
      tenantName: null,
      /** Si falla la carga del logo del tenant, usar JobRhythm */
      tenantLogoFailed: false,
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
      // Verificar si la ruta actual tiene hideNavbar en su meta
      return !this.$route.meta.hideNavbar;
    },
    isDropdownActive() {
      return (item) => {
        return (
          item.children &&
          item.children.some((subItem) => this.$route.path === subItem.route)
        );
      };
    },
  },
  mounted() {
    this.checkUserIdentity();
    this._onResizeNavbar = () => {
      if (window.innerWidth >= 1200) {
        this.closeNavbar();
      } else {
        this.syncMobileMenuBodyScroll();
      }
    };
    window.addEventListener("resize", this._onResizeNavbar, { passive: true });
  },
  beforeUnmount() {
    if (this._onResizeNavbar) {
      window.removeEventListener("resize", this._onResizeNavbar);
    }
    document.body.style.overflow = "";
  },
  methods: {
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
    toggleDropdown(index) {
      this.menuItems.forEach((item, i) => {
        if (i === index) {
          item.isOpen = !item.isOpen;
        } else {
          item.isOpen = false;
        }
      });
      this.isUserDropdownOpen = false;
    },
    toggleUserDropdown() {
      this.isUserDropdownOpen = !this.isUserDropdownOpen;
      this.menuItems.forEach((item) => {
        if (item.children) {
          item.isOpen = false;
        }
      });
    },
    logout() {
      localStorage.removeItem("authToken");
      localStorage.removeItem("userPermissions");
      this.isLoggedIn = false;
      this.$router.push("/login");
      this.closeNavbar();
    },
    syncMobileMenuBodyScroll() {
      if (typeof document === "undefined") return;
      const mobile = window.innerWidth < 1200;
      if (mobile && this.isNavbarOpen) {
        document.body.style.overflow = "hidden";
      } else {
        document.body.style.overflow = "";
      }
    },
    toggleNavbar() {
      this.isNavbarOpen = !this.isNavbarOpen;
      // Al abrir o cerrar el menú móvil, ningún submenú desplegado (solo se abren con un toque)
      this.isUserDropdownOpen = false;
      this.menuItems.forEach((item) => {
        if (item.children) {
          item.isOpen = false;
        }
      });
      this.syncMobileMenuBodyScroll();
    },
    closeNavbar() {
      this.isNavbarOpen = false;
      this.isUserDropdownOpen = false;
      this.menuItems.forEach((item) => {
        if (item.children) {
          item.isOpen = false;
        }
      });
      this.syncMobileMenuBodyScroll();
    },
  },
  watch: {
    $route() {
      this.checkUserIdentity();
      this.closeNavbar();
    },
  },
};
</script>

<style scoped>
/* Los estilos del navbar se manejan completamente en skin-modern.css */
</style>
