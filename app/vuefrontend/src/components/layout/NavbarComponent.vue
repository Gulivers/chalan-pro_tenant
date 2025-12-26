<template>
  <BNavbar
    v-if="shouldShowNavbar"
    v-b-color-mode="'dark'"
    toggleable="xl"
    variant="primary"
    class="navbar-modern">
    <BNavbarBrand to="/">CHALAN-PRO</BNavbarBrand>
    
    <!-- Botón de mensajes -->
    <div v-if="shouldShowNavbar" class="d-flex align-items-center me-2">
      <NavbarMessagesDropdown v-if="shouldShowNavbar" />
    </div>
    
    <BNavbarToggle target="nav-collapse" />
    
    <BCollapse
      id="nav-collapse"
      is-nav>
      <BNavbarNav>
        <template v-for="(item, index) in menuItems" :key="index">
          <BNavItemDropdown
            v-if="item.children"
            :text="item.text"
            :class="{ 'text-orange': isDropdownActive(item), 'dropdown-active': isDropdownActive(item) }"
            :data-active="isDropdownActive(item)">
            <BDropdownItem
              v-for="(subItem, subIndex) in item.children"
              :key="subIndex"
              :to="subItem.route"
              :active="$route.path === subItem.route"
              @click="closeNavbar">
              {{ subItem.text }}
            </BDropdownItem>
          </BNavItemDropdown>
          <BNavItem
            v-else
            :to="item.route"
            :active="$route.path === item.route"
            @click="closeNavbar">
            {{ item.text }}
          </BNavItem>
        </template>
      </BNavbarNav>
      
      <!-- Menú derecho -->
      <BNavbarNav class="ms-auto">
        <!-- User Dropdown -->
        <BNavItemDropdown
          v-if="isLoggedIn"
          right
          class="user-dropdown">
          <template #button-content>
            <img :src="constructorIcon" alt="User" class="user-icon" />
          </template>
          <BDropdownItem disabled class="user-dropdown-header">
            <div>
              <strong>Welcome</strong>
              <div class="user-name">{{ userName }}</div>
            </div>
          </BDropdownItem>
          <BDropdownDivider />
          <BDropdownItem to="/logout" @click="logout">Logout</BDropdownItem>
        </BNavItemDropdown>
        <BNavItem v-if="!isLoggedIn" to="/login" @click="closeNavbar">
          Log In
        </BNavItem>
      </BNavbarNav>
    </BCollapse>
  </BNavbar>
</template>

<script>
  import { BNavbar, BNavbarBrand, BNavbarToggle, BCollapse, BNavbarNav, BNavItem, BNavItemDropdown, BDropdownItem, BDropdownDivider } from 'bootstrap-vue-next';
  import NavbarMessagesDropdown from './NavbarMessagesDropdown.vue';
  import constructorIcon from '@/assets/img/user.svg';

  export default {
    components: {
      BNavbar,
      BNavbarBrand,
      BNavbarToggle,
      BCollapse,
      BNavbarNav,
      BNavItem,
      BNavItemDropdown,
      BDropdownItem,
      BDropdownDivider,
      NavbarMessagesDropdown,
    },
    data() {
      return {
        constructorIcon,
        isLoggedIn: false,
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
      shouldShowNavbar() {
        return !this.$route.meta.hideNavbar;
      },
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
              this.userName = user.first_name && user.last_name 
                ? `${user.first_name} ${user.last_name}`
                : user.username || 'User';
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
      closeNavbar() {
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
  /* Resaltar dropdown activo con :deep() para penetrar en componentes de BootstrapVueNext */
  :deep(.nav-item.dropdown.text-orange .dropdown-toggle),
  :deep(.nav-item.dropdown.text-orange .nav-link),
  :deep(.nav-item.dropdown.text-orange button),
  :deep(.nav-item.dropdown.text-orange a),
  :deep(.nav-item.dropdown.text-orange .btn),
  :deep(.nav-item.dropdown.text-orange .btn-link),
  :deep(.nav-item.dropdown.dropdown-active .dropdown-toggle),
  :deep(.nav-item.dropdown.dropdown-active .nav-link),
  :deep(.nav-item.dropdown.dropdown-active button),
  :deep(.nav-item.dropdown.dropdown-active a),
  :deep(.nav-item.dropdown[data-active="true"] .dropdown-toggle),
  :deep(.nav-item.dropdown[data-active="true"] .nav-link),
  :deep(.nav-item.dropdown[data-active="true"] button),
  :deep(.nav-item.dropdown[data-active="true"] a),
  :deep(.nav-item.dropdown[data-active="true"] .btn) {
    color: #ffffff !important;
    background-color: rgba(255, 255, 255, 0.15) !important;
    font-weight: 600 !important;
  }
  
  /* Selector más específico para el toggle button */
  :deep(.navbar-nav .nav-item.dropdown.text-orange > .nav-link),
  :deep(.navbar-nav .nav-item.dropdown.dropdown-active > .nav-link),
  :deep(.navbar-nav .nav-item.dropdown[data-active="true"] > .nav-link) {
    color: #ffffff !important;
    background-color: rgba(255, 255, 255, 0.15) !important;
    font-weight: 600 !important;
  }
  
  /* User Dropdown Styles */
  .user-dropdown .user-icon {
    width: 28px;
    height: 28px;
    filter: brightness(0) invert(1);
    transition: opacity 0.2s ease;
  }
  
  .user-dropdown:hover .user-icon {
    opacity: 0.9;
  }
  
  .user-dropdown-header {
    padding: 0.75rem 1.25rem !important;
    color: #4b5563 !important;
    cursor: default;
  }
  
  .user-dropdown-header strong {
    display: block;
    color: #1f2937;
    font-weight: 600;
    margin-bottom: 0.25rem;
  }
  
  .user-dropdown-header .user-name {
    font-size: 0.95rem;
    color: #6b7280;
    font-weight: 500;
  }
</style>
