<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark border-bottom border-body py-1">
    <div class="container d-flex align-items-center">
      <!-- Marca -->
      <a class="navbar-brand py-0" href="/">CHALAN-PRO</a>
      <!-- Botón de mensajes (fuera del collapsible, se mantiene) -->
      <ul class="navbar-nav me-2">
        <li class="nav-item d-flex align-items-center">
          <NavbarMessagesDropdown />
        </li>
      </ul>
      <button
        class="navbar-toggler"
        type="button"
        @click="toggleNavbar"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div :class="['collapse', 'navbar-collapse', { show: isNavbarOpen }]" id="navbarNav">
        <!-- Menú izquierdo -->
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li v-for="(item, index) in menuItems" :key="index" :class="{ dropdown: item.children }">
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
                <li v-for="(subItem, subIndex) in item.children" :key="subIndex">
                  <router-link :to="subItem.route" class="dropdown-item" @click="closeNavbar">
                    {{ subItem.text }}
                  </router-link>
                </li>
              </ul>
            </template>
            <template v-else>
              <router-link :to="item.route" class="nav-link" @click="closeNavbar">{{ item.text }}</router-link>
            </template>
          </li>
        </ul>

        <!-- Menú derecho -->
        <ul class="navbar-nav ms-auto d-flex align-items-center">
          <!-- Dynamic Messages Dropdown Component -->
          <li class="nav-item" v-if="isLoggedIn">
            <span class="nav-link">Welcome, {{ userName }}</span>
          </li>
          <li class="nav-item" v-if="isLoggedIn">
            <router-link to="/logout" class="nav-link" @click="logout">Log Out</router-link>
          </li>
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link to="/login" class="nav-link" @click="closeNavbar">Log In</router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
  import NavbarMessagesDropdown from './NavbarMessagesDropdown.vue';

  export default {
    components: {
      NavbarMessagesDropdown,
    },
    data() {
      return {
        isLoggedIn: false,
        isNavbarOpen: false,
        menuItems: [
          { text: 'Dashboard', route: '/' },
          {
            text: 'Operations',
            isOpen: false,
            children: [
              { text: 'Schedule', route: '/schedule' },
              { text: 'Job Communications', route: '/chat-general' },
              { text: 'Transactions', route: '/transactions', permission: 'apptransactions.view_transaction' },
              { text: 'Work Accounts', route: '/work-accounts', permission: 'apptransactions.view_workaccount' },
            ],
          },
          {
            text: 'Inventory',
            isOpen: false,
            children: [
              { text: 'Dashboard', route: '/inventory-dashboard', permission: 'appinventory.view_product' },
              { text: 'Products', route: '/products', permission: 'appinventory.view_product' },
              { text: 'Warehouses', route: '/warehouses', permission: 'appinventory.view_warehouse' },
              { text: 'Product Categories', route: '/product-categories', permission: 'appinventory.view_productcategory' },
              { text: 'Product Brands', route: '/product-brands', permission: 'appinventory.view_productbrand' },
              { text: 'Price Types', route: '/price-types', permission: 'appinventory.view_pricetype' },
              { text: 'Unit Measures', route: '/unit-measures', permission: 'appinventory.view_unitofmeasure' },
              { text: 'Unit Categories', route: '/unit-categories', permission: 'appinventory.view_unitcategory' },
            ],
          },
          {
            text: 'Contracts & Pricing',
            isOpen: false,
            children: [
              { text: 'Contracts', route: '/contracts' },
              { text: 'Piece Work Prices', route: '/work-prices' },
              { text: 'Work Prices per Builder', route: '/work-prices-builders' },
            ],
          },
          {
            text: 'Entities',
            isOpen: false,
            children: [
              { text: 'Builders & Parties', route: '/builders', permission: 'ctrctsapp.view_builder' },
              { text: 'Party Types', route: '/party-types', permission: 'apptransactions.view_partytype' },
              { text: 'Party Categories', route: '/party-categories', permission: 'apptransactions.view_partycategory' },
            ],
          },
          {
            text: 'Communities',
            isOpen: false,
            children: [
              { text: 'Communities Map', route: '/map' },
              { text: 'Supervisor Communities', route: '/supervisor-communities' },
            ],
          },
          {
            text: 'Configuration',
            isOpen: false,
            children: [
              { text: 'Transactions Types', route: '/document-types', permission: 'apptransactions.view_documenttype' },
            ],
          },
          { text: 'About', route: '/about' },
        ],
        userName: '',
      };
    },
    computed: {
      isDropdownActive() {
        return item => {
          return item.children && item.children.some(subItem => this.$route.path === subItem.route);
        };
      },
    },
    mounted() {
      this.checkUserIdentity();
    },
    methods: {
      checkUserIdentity() {
        const token = localStorage.getItem('authToken');
        this.isLoggedIn = !!token;
        if (this.isLoggedIn) {
          this.getAuthenticatedUser().then(user => {
            if (user) {
              this.userName = user.username;
            }
          });
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
      },
      logout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userPermissions');
        this.isLoggedIn = false;
        this.$router.push('/login');
        this.closeNavbar();
      },
      toggleNavbar() {
        this.isNavbarOpen = !this.isNavbarOpen;
      },
      closeNavbar() {
        this.isNavbarOpen = false;
        this.menuItems.forEach(item => {
          if (item.children) {
            item.isOpen = false;
          }
        });
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
  .text-orange {
    color: #ff931e !important;
    font-weight: bold;
  }
  .dropdown-item.router-link-exact-active {
    color: #ff931e !important;
    font-weight: bold;
  }
</style>

