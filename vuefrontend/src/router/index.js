
import { createRouter, createWebHistory } from 'vue-router';
import axios from 'axios';

// ───────────────────────────────────────────────────────────
// LAZY IMPORTS (ordenado por módulos)
// ───────────────────────────────────────────────────────────

const LoginView = () => import('@views/LoginView.vue');
const HomeView = () => import('@views/HomeView.vue');
const AboutView = () => import('@views/AboutView.vue');
const JobMap = () => import('@components/houses/JobMap.vue');
const SupervisorCommunitiesList = () => import('@components/houses/SupervisorCommunitiesList.vue');
const PasswordReset = () => import('@components/PasswordReset.vue');
const PasswordResetConfirm = () => import('@components/PasswordResetConfirm.vue');

// Contracts
const ContractListView = () => import('@views/contract/ContractListView.vue');
const ContractFormComponent = () => import('@components/contracts/ContractFormComponent.vue');
const WorkPricesView = () => import('@views/contract/WorkPricesView.vue');
const WorkPriceFormComponent = () => import('@components/contracts/WorkPriceFormComponent.vue');
const WorkPricesBuilderComponent = () => import('@components/contracts/WorkPricesBuilderComponent.vue');
const WeeklySummaryListComponent = () => import('@components/contracts/WeeklySummaryListComponent.vue');

// Schedule & Chat
const ScheduleComponent = () => import('@components/schedule/ScheduleComponent.vue');
const ScheduleHouseChatsGeneralComponent = () => import('@components/schedule/ScheduleHouseChatsGeneralComponent.vue');

// Inventory
const ProductForm = () => import('@components/inventory/ProductForm.vue');
const WarehouseListView = () => import('@views/inventory/WarehouseListView.vue');
const WareHouseFormComponent = () => import('@components/inventory/WarehouseFormComponent.vue');
const DynamicForm = () => import('@components/inventory/DynamicForm.vue');
const ProductCategoryView = () => import('@views/inventory/ProductCategoryView.vue');
const ProductBrandView = () => import('@views/inventory/ProductBrandView.vue');
// const ProductUnitView = () => import('@views/inventory/ProductUnitView.vue');
const UnitOfMeasureView = () => import('@views/inventory/UnitOfMeasureView.vue');
const UnitCategoryView = () => import('@views/inventory/UnitCategoryView.vue');
const PriceTypeView = () => import('@views/inventory/PriceTypeView.vue');
const ProductListView = () => import('@views/inventory/ProductListView.vue');
const InventoryDashboardView = () => import('@views/inventory/InventoryDashboardView.vue');

// Parties (Builder, Job, House Model)
const BuilderView = () => import('@views/parties/BuilderView.vue');
const BuilderFormView = () => import('@views/parties/BuilderFormView.vue');
const JobView = () => import('@views/parties/JobView.vue');
const JobFormView = () => import('@views/parties/JobFormView.vue');
const HouseModelView = () => import('@views/parties/HouseModelView.vue');
const HouseModelFormView = () => import('@views/parties/HouseModelFormView.vue');

// Transactions
const DocTypeListView = () => import('@views/transactions/DocTypeListView.vue');
const DocTypeForm = () => import('@components/transactions/DocTypeForm.vue');
const PartyTypeListView = () => import('@views/transactions/PartyTypeListView.vue');
const PartyTypeForm = () => import('@components/transactions/PartyTypeForm.vue');
const PartyCategoryListView = () => import('@views/transactions/PartyCategoryListView.vue');
const PartyCategoryForm = () => import('@components/transactions/PartyCategoryForm.vue');
const PartyForm = () => import('@components/transactions/PartyForm.vue');
const PartyListView = () => import('@views/transactions/PartyListView.vue');
const TransactionForm = () => import('@components/transactions/TransactionForm.vue');
const TransactionListView = () => import('@views/transactions/TransactionListView.vue');
const WorkAccountSelect = () => import('@components/transactions/WorkAccountSelect.vue');
const WorkAccountListView = () => import('@views/transactions/WorkAccountListView.vue');


// ───────────────────────────────────────────────────────────
// EXPORT ROUTER
// ───────────────────────────────────────────────────────────

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { hideNavbar: true },
  },
  {
    path: '/logout',
    name: 'logout',
    beforeEnter: (to, from, next) => {
      localStorage.removeItem('authToken');
      localStorage.removeItem('userPermissions');
      next({ name: 'login' });
    }
  },
  {
    path: "/map",
    name: "JobMap",
    component: JobMap,
    meta: { requiresAuth: true, requiredPermissions: [] }
  },
  {
    path: "/supervisor-communities",
    name: "SupervisorCommunitiesList",
    component: SupervisorCommunitiesList,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.add_contract'] }
  },
  {
    path: '/reset_password',
    name: 'reset_password',
    component: PasswordReset,
  },
  {
    path: '/reset-password-confirm',
    component: PasswordResetConfirm,
  },
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true, requiredPermissions: [] }
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView,
    meta: { requiresAuth: false, requiredPermissions: [], }
  },
  {
    path: '/contracts',
    name: 'contracts',
    component: ContractListView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.view_contract'] }
  },
  {
    path: '/contract-form',
    name: 'contract-form',
    component: ContractFormComponent,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.add_contract'] }
  },
  {
    path: '/contract-edit/edit/:id',
    name: 'contract-edit',
    component: ContractFormComponent,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.change_contract'] }
  },
  {
    path: '/contract-view/view/:id',
    name: 'contract-view',
    component: ContractFormComponent,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.view_contract'] }
  },
  {
    path: '/work-prices',
    name: 'work-prices',
    component: WorkPricesView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.view_workprice'] }
  },
  {
    path: '/work-prices-form',
    name: 'work-prices-form',
    component: WorkPriceFormComponent,
    // props: true,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.add_workprice'] }
  },
  {
    path: '/work-prices/edit/:id',
    name: 'work-prices-edit',
    component: WorkPriceFormComponent,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.change_workprice'] }
  },
  {
    path: '/work-prices/view/:id',
    name: 'work-prices-view',
    component: WorkPriceFormComponent,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.view_workprice'] }
  },
  {
    path: '/work-prices-builders',
    name: 'work-prices-builders',
    component: WorkPricesBuilderComponent,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.change_workprice'] }
  },
  {
    path: '/weekly-summary-list/',
    name: 'weekly-summary-list',
    component: WeeklySummaryListComponent,
    // props: true,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.view_contract'] }
  },
  {
    path: '/schedule',
    name: 'schedule',
    component: ScheduleComponent,
    meta: { requiresAuth: true, requiredPermissions: ['appschedule.view_event'] }
  },
  {
    path: '/chat-general',
    name: 'chat-general',
    component: ScheduleHouseChatsGeneralComponent,
    meta: { requiresAuth: true, requiredPermissions: ['appschedule.view_event'] }
  },

  
  // ───────────────────────────────────────────────────────────
  // INVENTORY MODULE                                        
  // ───────────────────────────────────────────────────────────
  {
    path: '/inventory-dashboard',
    name: 'inventory-dashboard',
    component: InventoryDashboardView,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_product'] },
  },
  {
    path: '/warehouses',
    name: 'warehouses',
    component: WarehouseListView,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_warehouse'] },
  },
  {
    path: '/warehouse-form',
    name: 'warehouse-form',
    component: WareHouseFormComponent,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.add_warehouse'] },
  },
  {
    path: '/warehouse/view/:id',
    name: 'warehouse-view',
    component: WareHouseFormComponent,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_warehouse'] },
  },
  {
    path: '/warehouse/edit/:id',
    name: 'warehouse-edit',
    component: WareHouseFormComponent,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.change_warehouse'] },
  },
  {
    path: '/product-categories',
    name: 'product-categories',
    component: ProductCategoryView,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_productcategory'] },
  },
  {
    path: '/product-category/form',
    name: 'product-category-form',
    component: DynamicForm,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.add_productcategory'] },
    props: () => ({
      schemaEndpoint: '/api/schema/product-category/',
      apiEndpoint: '/api/productcategory/',
      formTitle: 'Create Product Category',
      redirectAfterSave: '/product-categories',
      readOnly: false,
      objectId: null,
    }),
  },
  {
    path: '/product-category/view/:id',
    name: 'product-category-view',
    component: DynamicForm,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_productcategory'] },
    props: route => ({
      schemaEndpoint: '/api/schema/productcategory/',
      apiEndpoint: '/api/productcategory/',
      objectId: route.params.id,
      formTitle: 'View Product Category',
      readOnly: true,
    }),
  },
  {
    path: '/product-category/edit/:id',
    name: 'product-category-edit',
    component: DynamicForm,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.change_productcategory'] },
    props: route => ({
      schemaEndpoint: '/api/schema/productcategory/',
      apiEndpoint: '/api/productcategory/',
      objectId: route.params.id,
      formTitle: 'Edit Product Category',
      redirectAfterSave: '/product-categories',
      readOnly: false,
    }),
  },
  {
    path: '/product-brands',
    name: 'product-brands',
    component: ProductBrandView,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_productbrand'] },
  },
  {
    path: '/product-brand/form',
    name: 'product-brand-form',
    component: DynamicForm,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.add_productbrand'] },
    props: {
      schemaEndpoint: '/api/schema/productbrand/',
      apiEndpoint: '/api/productbrand/',
      formTitle: 'Create Product Brand',
      readOnly: false,
      objectId: null,
      redirectAfterSave: '/product-brands',
    },
  },
  {
    path: '/product-brand/edit/:id',
    name: 'product-brand-edit',
    component: DynamicForm,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.change_productbrand'] },
    props: route => ({
      schemaEndpoint: '/api/schema/productbrand/',
      apiEndpoint: '/api/productbrand/',
      objectId: route.params.id,
      formTitle: 'Edit Product Brand',
      readOnly: false,
      redirectAfterSave: '/product-brands',
    }),
  },
  {
    path: '/product-brand/view/:id',
    name: 'product-brand-view',
    component: DynamicForm,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_productbrand'] },
    props: route => ({
      schemaEndpoint: '/api/schema/productbrand/',
      apiEndpoint: '/api/productbrand/',
      objectId: route.params.id,
      formTitle: 'View Product Brand',
      readOnly: true,
      redirectAfterSave: '/product-brands',
    }),
  },
  {
    path: '/unit-measures',
    name: 'unit-measures',
    component: UnitOfMeasureView,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_unitofmeasure'] },
  },
  {
    path: '/unit-measure/form',
    name: 'unit-measure-form',
    component: DynamicForm,
    props: {
      schemaEndpoint: '/api/schema/unitofmeasure/',
      apiEndpoint: '/api/unitsofmeasure/',
      formTitle: 'Create Unit of Measure',
      redirectAfterSave: '/unit-measures',
      readOnly: false,
    },
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.add_unitofmeasure'] },
  },
  {
    path: '/unit-measure/view/:id',
    name: 'unit-measure-view',
    component: DynamicForm,
    props: route => ({
      schemaEndpoint: '/api/schema/unitofmeasure/',
      apiEndpoint: '/api/unitsofmeasure/',
      objectId: route.params.id,
      formTitle: 'View Unit of Measure',
      redirectAfterSave: '/unit-measures',
      readOnly: true,
    }),
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_unitofmeasure'] },
  },
  {
    path: '/unit-measure/edit/:id',
    name: 'unit-measure-edit',
    component: DynamicForm,
    props: route => ({
      schemaEndpoint: '/api/schema/unitofmeasure/',
      apiEndpoint: '/api/unitsofmeasure/',
      objectId: route.params.id,
      formTitle: 'Edit Unit of Measure',
      redirectAfterSave: '/unit-measures',
      readOnly: false,
    }),
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.change_unitofmeasure'] },
  },
  {
    path: '/unit-categories',
    name: 'unit-categories',
    component: UnitCategoryView,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_unitcategory'] },
  },
  {
    path: '/unit-category/form',
    name: 'unit-category-form',
    component: DynamicForm,
    props: {
      schemaEndpoint: '/api/schema/unitcategory/',
      apiEndpoint: '/api/unitcategory/',
      formTitle: 'Create Unit Category',
      redirectAfterSave: '/unit-categories',
      readOnly: false,
    },
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.add_unitcategory'] },
  },
  {
    path: '/unit-category/view/:id',
    name: 'unit-category-view',
    component: DynamicForm,
    props: route => ({
      schemaEndpoint: '/api/schema/unitcategory/',
      apiEndpoint: '/api/unitcategory/',
      objectId: route.params.id,
      formTitle: 'View Unit Category',
      redirectAfterSave: '/unit-categories',
      readOnly: true,
    }),
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_unitcategory'] },
  },
  {
    path: '/unit-category/edit/:id',
    name: 'unit-category-edit',
    component: DynamicForm,
    props: route => ({
      schemaEndpoint: '/api/schema/unitcategory/',
      apiEndpoint: '/api/unitcategory/',
      objectId: route.params.id,
      formTitle: 'Edit Unit Category',
      redirectAfterSave: '/unit-categories',
      readOnly: false,
    }),
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.change_unitcategory'] },
  },
  {
    path: '/price-types',
    name: 'price-types',
    component: PriceTypeView,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_pricetype'] },
  },
  {
    path: '/price-type/form',
    name: 'price-type-form',
    component: DynamicForm,
    props: {
      schemaEndpoint: '/api/schema/pricetype/',
      apiEndpoint: '/api/pricetypes/',
      formTitle: 'Create Price Type',
      redirectAfterSave: '/price-types',
      readOnly: false,
    },
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.add_pricetype'] },
  },
  {
    path: '/price-type/view/:id',
    name: 'price-type-view',
    component: DynamicForm,
    props: route => ({
      schemaEndpoint: '/api/schema/pricetype/',
      apiEndpoint: '/api/pricetypes/',
      objectId: route.params.id,
      formTitle: 'View Price Type',
      redirectAfterSave: '/price-types',
      readOnly: true,
    }),
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_pricetype'] },
  },
  {
    path: '/price-type/edit/:id',
    name: 'price-type-edit',
    component: DynamicForm,
    props: route => ({
      schemaEndpoint: '/api/schema/pricetype/',
      apiEndpoint: '/api/pricetypes/',
      objectId: route.params.id,
      formTitle: 'Edit Price Type',
      redirectAfterSave: '/price-types',
      readOnly: false,
    }),
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.change_pricetype'] },
  },
  {
    path: '/products',
    name: 'product-list',
    component: ProductListView,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_product'] },
    props: true,
  },
  {
    path: '/products/form',
    name: 'product-form',
    component: ProductForm,
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.add_product'] },
    props: true,
  },
  {
    path: '/products/view/:id',
    name: 'product-view',
    component: ProductForm,
    props: route => ({ objectId: route.params.id }), // así lo pasas como prop
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.view_product'] },
  },
  {
    path: '/products/edit/:id',
    name: 'product-edit',
    component: ProductForm,
    props: route => ({ objectId: route.params.id }), // también aquí 
    meta: { requiresAuth: true, requiredPermissions: ['appinventory.change_product'] },
  },

  // ───────────────────────────────────────────────────────────
  // PARTIES MODULE (Builder, Job, House Model)                 
  // ───────────────────────────────────────────────────────────

  // Builder routes
  {
    path: '/builders',
    name: 'builder-list',
    component: BuilderView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.view_builder'] },
  },
  {
    path: '/builder/form',
    name: 'builder-form',
    component: BuilderFormView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.add_builder'] },
  },
  {
    path: '/builder/view/:id',
    name: 'builder-view',
    component: BuilderFormView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.view_builder'] },
  },
  {
    path: '/builder/edit/:id',
    name: 'builder-edit',
    component: BuilderFormView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.change_builder'] },
  },

  // Job routes
  {
    path: '/jobs',
    name: 'job-list',
    component: JobView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.view_job'] },
  },
  {
    path: '/job/form',
    name: 'job-form',
    component: JobFormView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.add_job'] },
  },
  {
    path: '/job/view/:id',
    name: 'job-view',
    component: JobFormView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.view_job'] },
  },
  {
    path: '/job/edit/:id',
    name: 'job-edit',
    component: JobFormView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.change_job'] },
  },

  // House Model routes
  {
    path: '/house-models',
    name: 'house-model-list',
    component: HouseModelView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.view_housemodel'] },
  },
  {
    path: '/house-model/form',
    name: 'house-model-form',
    component: HouseModelFormView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.add_housemodel'] },
  },
  {
    path: '/house-model/view/:id',
    name: 'house-model-view',
    component: HouseModelFormView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.view_housemodel'] },
  },
  {
    path: '/house-model/edit/:id',
    name: 'house-model-edit',
    component: HouseModelFormView,
    meta: { requiresAuth: true, requiredPermissions: ['ctrctsapp.change_housemodel'] },
  },

  // ───────────────────────────────────────────────────────────
  // TRANSACTIONS MODULE                                        
  // ───────────────────────────────────────────────────────────

  {
    path: '/document-types',
    name: 'document-types',
    component: DocTypeListView,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.view_documenttype'] },
  },
  {
    path: '/document-types/form',
    name: 'document-types-form',
    component: DocTypeForm,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.add_documenttype'] },
  },
  {
    path: '/party-types',
    name: 'party-types',
    component: PartyTypeListView,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.view_partytype'] },
  },
  {
    path: '/party-types/form',
    name: 'party-types-form',
    component: PartyTypeForm,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.add_partytype'] },
  },
  {
    path: '/party-categories',
    name: 'party-categories',
    component: PartyCategoryListView,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.view_partycategory'] },
  },
  {
    path: '/party-categories/form',
    name: 'party-categories-form',
    component: PartyCategoryForm,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.add_partycategory'] },
  },
  {
    path: '/parties',
    name: 'parties',
    component: PartyListView,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.view_party'] },
  },
  {
    path: '/parties/form',
    name: 'parties-form',
    component: PartyForm,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.add_party'] },
  },
  {
    path: '/transactions/form',
    name: 'transactions-form',
    component: TransactionForm,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.add_document'] },
  },
  {
    path: '/transactions',
    name: 'transactions',
    component: TransactionListView,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.view_document'] },
  },
  {
    path: '/work-accounts',
    name: 'work-accounts',
    component: WorkAccountListView,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.view_workaccount'] },
  },
  {
    path: '/work-accounts/form',
    name: 'work-accounts-form',
    component: WorkAccountSelect,
    meta: { requiresAuth: true, requiredPermissions: ['apptransactions.add_workaccount'] },
  },

];


const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

router.beforeEach(async (to, from, next) => {
  const authToken = localStorage.getItem('authToken');
  console.log(`Auth Token in Router>>: ${authToken ? 'true' : 'false'}`);
  const userPermissions = JSON.parse(localStorage.getItem('userPermissions') || '[]');
  //console.log(`User Permissions in Router>>: ${JSON.stringify(userPermissions)}`);

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!authToken) {
      next({ name: 'login' });
    } else {
      try {
        const response = await axios.get('/api/validate-token/', {
          headers: { 'Authorization': `Token ${authToken}` }
        });

        if (response.data.valid) {
          const requiredPermissions = to.meta.requiredPermissions || [];
          const userPermissionsArray = userPermissions.permissions || [];
          const userPermissionsSet = new Set(userPermissionsArray);

          const hasPermission = requiredPermissions.length === 0 ||
            requiredPermissions.every(permission => userPermissionsSet.has(permission));
          console.log('Has permission:', hasPermission);

          if (hasPermission) {
            next();
          } else {
            alert('You do not have permission to access this page');
            next(false);
          }
        } else {
          localStorage.removeItem('authToken');
          localStorage.removeItem('userPermissions');
          next({ name: 'login' });
        }
      } catch (error) {
        console.error('Error validating token:', error);
        localStorage.removeItem('authToken');
        localStorage.removeItem('userPermissions');
        next({ name: 'login' });
      }
    }
  } else {
    next();
  }
});

export default router;