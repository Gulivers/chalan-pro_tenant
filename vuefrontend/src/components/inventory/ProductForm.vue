<template>
  <div class="container mt-4">
    <div class="text-center">
      <h3 class="text-warning">Product Form</h3>
    </div>
    <div class="card shadow" style="height: auto">
      <div class="card-header d-flex justify-content-center align-items-center">
        <h6 class="mb-0 ms-5 w-100 text-center text-primary">{{ pageTitle }}</h6>
        <button class="btn btn-outline-secondary btn-sm" @click="cancelForm">Back</button>
      </div>

      <div class="card-body">
        <form @submit.prevent="handleSubmit" novalidate>
          <!-- Product fields -->
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label d-flex align-items-center gap-2">Name</label>
              <input
                v-model.trim="product.name"
                type="text"
                class="form-control"
                :class="{ 'is-invalid': fieldErrors.name }"
                :disabled="isReadOnly"
                required
                minlength="3"
                maxlength="255"
                v-tt
                data-title="Product name for identification and display purposes" />
              <div v-if="fieldErrors.name" class="invalid-feedback">{{ fieldErrors.name }}</div>
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label d-flex align-items-center gap-2">
                SKU
                <i
                  v-tt
                  class="fas fa-info-circle text-muted"
                  data-title="Required (min 3). Unique identifier for warehouse/purchasing."></i>
              </label>
              <input
                v-model.trim="product.sku"
                type="text"
                class="form-control"
                :class="{ 'is-invalid': fieldErrors.sku }"
                :disabled="isReadOnly"
                required
                minlength="3"
                maxlength="100"
                v-tt
                data-title="Unique identifier for warehouse and purchasing operations" />
              <div v-if="fieldErrors.sku" class="invalid-feedback">{{ fieldErrors.sku }}</div>
            </div>

            <!-- Category -->
            <div class="col-md-6 mb-3">
              <label class="form-label d-flex align-items-center gap-2">
                Category
                <i
                  v-tt
                  class="fas fa-info-circle text-muted"
                  data-title="Required. Group products for filtering and analytics."></i>
              </label>
              <div class="d-flex align-items-center">
                <v-select
                  :options="categories"
                  v-model="product.category"
                  :reduce="cat => cat.id"
                  label="name"
                  placeholder="Select Category"
                  class="flex-grow-1"
                  :class="{ 'is-invalid': fieldErrors.category }"
                  :disabled="isReadOnly || !hasPermission('appinventory.add_productcategory')"
                  @open="loadCategories"
                  v-tt
                  data-title="Required field for product categorization" />
                <button
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="openCategoryModal('add')"
                  :disabled="isReadOnly || !hasPermission('appinventory.add_productcategory')"
                  v-tt
                  data-title="Add a new category to the system">
                  <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15" />
                </button>
                <button
                  v-if="product.category"
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="openCategoryModal('edit', product.category)"
                  :disabled="isReadOnly || !hasPermission('appinventory.change_productcategory')"
                  v-tt
                  data-title="Edit the currently selected category">
                  <img src="@assets/img/icon-changelink.svg" alt="Edit" width="15" height="15" />
                </button>
              </div>
              <div v-if="fieldErrors.category" class="invalid-feedback d-block">{{ fieldErrors.category }}</div>
            </div>

            <!-- Brands (multiple selection) -->
            <div class="col-md-6 mb-3">
              <label class="form-label d-flex align-items-center gap-2">
                Brands
                <i
                  v-tt
                  class="fas fa-info-circle text-muted"
                  data-title="Required for product traceability and brand management"></i>
              </label>
              <div class="d-flex align-items-center">
                <v-select
                  :options="brands"
                  label="name"
                  :reduce="brand => brand.id"
                  v-model="product.brands"
                  placeholder="Select Brands"
                  class="flex-grow-1"
                  :class="{ 'is-invalid': fieldErrors.brands }"
                  :disabled="isReadOnly || !hasPermission('appinventory.add_productcategory')"
                  multiple
                  :close-on-select="false"
                  :clearable="true"
                  @open="loadBrands"
                  v-tt
                  data-title="Required field - select one or more brands" />
                <button
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="openBrandModal('add')"
                  :disabled="isReadOnly || !hasPermission('appinventory.add_productbrand')"
                  v-tt
                  data-title="Add a new brand to the system">
                  <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15" />
                </button>
              </div>
              <div v-if="fieldErrors.brands" class="invalid-feedback d-block">{{ fieldErrors.brands }}</div>
              <div v-if="product.brands && product.brands.length > 0" class="small text-muted mt-1">
                <strong>Default Brand:</strong>
                {{ getDefaultBrandName() || 'Will be auto-assigned' }}
              </div>
            </div>

            <!-- Default Unit -->
            <div class="col-md-6 mb-3">
              <label class="form-label d-flex align-items-center gap-2">
                Default Unit
                <i
                  v-tt
                  class="fas fa-info-circle text-muted"
                  data-title="Required. Primary unit used for stock and valuations (e.g., EA, FT)."></i>
              </label>
              <div class="d-flex align-items-center">
                <v-select
                  :options="units"
                  v-model="product.unit_default"
                  :reduce="unit => unit.id"
                  label="name"
                  placeholder="Select Unit"
                  class="flex-grow-1"
                  :class="{ 'is-invalid': fieldErrors.unit_default }"
                  :disabled="isReadOnly || !hasPermission('appinventory.add_productcategory')"
                  @open="loadUnits"
                  v-tt
                  data-title="Required field for unit selection" />
                <button
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="openUnitModal('add')"
                  :disabled="isReadOnly || !hasPermission('appinventory.add_unitofmeasure')"
                  v-tt
                  data-title="Add a new unit of measure to the system">
                  <img src="@assets/img/icon-addlink.svg" alt="Add" width="15" height="15" />
                </button>
                <button
                  v-if="product.unit_default"
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="openUnitModal('edit', product.unit_default)"
                  :disabled="isReadOnly || !hasPermission('appinventory.change_unitofmeasure')"
                  v-tt
                  data-title="Edit the currently selected unit">
                  <img src="@assets/img/icon-changelink.svg" alt="Edit" width="15" height="15" />
                </button>
              </div>
              <div v-if="fieldErrors.unit_default" class="invalid-feedback d-block">{{ fieldErrors.unit_default }}</div>
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label d-flex align-items-center gap-2">
                Reorder Level
                <i
                  v-tt
                  class="fas fa-info-circle text-muted"
                  data-title="Alert threshold to trigger restock notifications"></i>
              </label>
              <input
                v-model.number="product.reorder_level"
                type="number"
                step="0.01"
                class="form-control"
                :disabled="isReadOnly"
                min="0"
                v-tt
                data-title="Optional. Used for low-stock alerts and inventory management" />
            </div>

            <div class="col-md-6 mb-1 d-flex align-items-center gap-2">
              <input
                v-model="product.is_active"
                type="checkbox"
                class="form-check-input"
                id="isActive"
                :disabled="isReadOnly" />
              <label
                for="isActive"
                class="form-check-label"
                v-tt
                data-title="Toggle product availability in the system">
                Active
              </label>
            </div>
          </div>

          <!-- Combined ProductUnit + ProductPrice table -->
          <ProductPriceUnitTable
            v-model="productPriceUnits"
            :priceTypes="priceTypes"
            :units="units"
            @open-modal="handleOpenModal"
            @edit-modal="handleEditModal"
            @refresh-priceTypes="loadPriceTypes"
            @refresh-units="loadUnits"
            :readonly="isReadOnly" />

          <div class="mt-4 d-flex gap-2">
            <button type="submit" class="btn btn-primary" :disabled="isReadOnly || submitting">
              <i v-if="!submitting" class="fas fa-save me-1"></i>
              <i v-else class="fas fa-spinner fa-spin me-1"></i>
              {{ submitting ? 'Saving...' : $route?.query?.id || $route?.params?.id || objectId ? 'Update' : 'Save' }}
            </button>
            <button type="button" class="btn btn-outline-secondary" @click="cancelForm">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modals for Category, Brand, Unit, PriceType -->
    <CategoryModal ref="categoryModal" :objectId="modalObjectId" @refreshCategories="loadCategories" />
    <BrandModal ref="brandModal" :objectId="modalObjectId" @refreshBrands="loadBrands" />
    <UnitModal ref="unitModal" :objectId="modalObjectId" @refreshUnits="loadUnits" />
    <PriceTypeModal ref="priceTypeModal" :objectId="modalObjectId" @refresh="loadPriceTypes" />
  </div>
</template>

<script>
  // Options API to keep consistency with current codebase
  import axios from 'axios';
  import VSelect from 'vue-select';
  import 'vue-select/dist/vue-select.css';
  import Swal from 'sweetalert2';
  import ProductPriceUnitTable from '@/components/inventory/ProductPriceUnitTable.vue';
  import CategoryModal from '@/components/inventory/CategoryModal.vue';
  import BrandModal from '@/components/inventory/BrandModal.vue';
  import UnitModal from '@/components/inventory/UnitModal.vue';
  import PriceTypeModal from '@/components/inventory/PriceTypeModal.vue';

  const LIST_ROUTE = '/products'; // redirect target per Chalan-Pro CRUD pattern

  export default {
    name: 'ProductForm',
    components: {
      ProductPriceUnitTable,
      VSelect,
      CategoryModal,
      BrandModal,
      UnitModal,
      PriceTypeModal,
    },
    props: {
      objectId: {
        type: [Number, String],
        default: null,
      },
    },
    data() {
      return {
        product: {
          name: '',
          sku: '',
          category: '',
          brands: [],
          unit_default: '',
          reorder_level: 0,
          is_active: true,
        },
        productPriceUnits: [],
        categories: [],
        brands: [],
        units: [],
        priceTypes: [],
        modalObjectId: null,
        submitting: false,
        isReadOnly: false, // view mode lock
        fieldErrors: {}, // per-field validation feedback mapping
      };
    },
    computed: {
      pageTitle() {
        if (this.isReadOnly) return 'View Product';
        const id = this.objectId || this.$route?.params?.id || this.$route?.query?.id;
        return id ? 'Edit Product' : 'Create Product';
      },
    },
    created() {
      // Support query-based navigation from ProductList: ?mode=view|edit&id=XX
      this.isReadOnly = this.$route?.query?.mode === 'view' || this.isReadOnly;

      this.loadInitialData();

      const id = this.objectId || this.$route?.params?.id || this.$route?.query?.id;
      if (id) this.loadProduct();
    },
    watch: {
      '$route.query.mode'(val) {
        this.isReadOnly = val === 'view';
      },
      '$route.query.id'(val, oldVal) {
        if (val && val !== oldVal) this.loadProduct();
      },
    },
    methods: {
      // --- Loaders ---
      async loadInitialData() {
        try {
          const [catRes, brandRes, unitRes, priceTypeRes] = await Promise.all([
            axios.get('/api/productcategory/'),
            axios.get('/api/productbrand/'),
            axios.get('/api/unitsofmeasure/'),
            axios.get('/api/pricetypes/'),
          ]);

          this.categories = catRes.data;
          this.brands = brandRes.data;
          this.units = unitRes.data;
          this.priceTypes = priceTypeRes.data;
        } catch (err) {
          console.error('Failed to load select options', err);
          this.notifyToastError?.('Failed to load lists');
        }
      },
      async loadProduct() {
        try {
          const id = this.objectId || this.$route?.params?.id || this.$route?.query?.id;
          if (!id) return;
          const res = await axios.get(`/api/products/${id}/`);
          this.product = res.data;

          // Convert brands response to array of IDs
          if (res.data.brands && Array.isArray(res.data.brands)) {
            this.product.brands = res.data.brands.map(brand => (typeof brand === 'object' ? brand.id : brand));
          } else {
            // Ensure brands is always an array
            this.product.brands = [];
          }

          const prices = Array.isArray(res.data.prices) ? res.data.prices : [];
          const unitsFlags = Array.isArray(res.data.price_units) ? res.data.price_units : [];

          // Map unit → flags (purchase/sale)
          const flagsByUnit = new Map();
          unitsFlags.forEach(u => {
            const uid = this.normalizeId(u.unit);
            if (uid) flagsByUnit.set(uid, { is_purchase: !!u.is_purchase, is_sale: !!u.is_sale });
          });

          // Build one table row per PRICE record (unit, price_type)
          const rows = prices.map(p => {
            const uid = typeof p.unit === 'object' ? p.unit?.id : p.unit;
            const ptid = typeof p.price_type === 'object' ? p.price_type?.id : p.price_type;
            const fb = flagsByUnit.get(uid) || { is_purchase: false, is_sale: false };
            return {
              price_type: ptid,
              unit: uid,
              is_purchase: typeof p.is_purchase !== 'undefined' ? !!p.is_purchase : fb.is_purchase,
              is_sale: typeof p.is_sale !== 'undefined' ? !!p.is_sale : fb.is_sale,
              price: p.price,
              is_default: !!p.is_default,
              valid_from: p.valid_from || null,
              valid_until: p.valid_until || null,
              is_active: p.is_active !== false,
            };
          });

          // If there are unit flags without price rows, show placeholders for visibility
          unitsFlags.forEach(u => {
            const uid = this.normalizeId(u.unit);
            if (uid && !rows.some(r => r.unit === uid)) {
              rows.push({
                price_type: '',
                unit: uid,
                is_purchase: !!u.is_purchase,
                is_sale: !!u.is_sale,
                price: '',
                is_default: false,
                valid_from: '',
                valid_until: '',
                is_active: true,
              });
            }
          });

          this.productPriceUnits = rows.length ? rows : [];
          if (!this.productPriceUnits.length && !this.isReadOnly) {
            // ensure at least one empty row for UX on fresh create
            this.productPriceUnits.push({
              price_type: '',
              unit: '',
              is_purchase: false,
              is_sale: false,
              price: '',
              is_default: false,
              valid_from: '',
              valid_until: '',
              is_active: true,
            });
          }
        } catch (err) {
          console.error('Error loading product:', err);
          this.notifyToastError?.('Failed to load product');
        }
      },

      // --- Helpers ---
      normalizeId(value) {
        return typeof value === 'object' ? value?.id : value;
      },
      pushFieldError(field, msg) {
        this.fieldErrors[field] = msg;
      },
      clearFieldErrors() {
        this.fieldErrors = {};
      },
      validateMinimal() {
        // Trim and minimal client validations per Chalan‑Pro Standard Form Pattern
        this.product.name = (this.product.name || '').trim();
        this.product.sku = (this.product.sku || '').trim();

        if (!this.product.name) this.pushFieldError('name', 'Name is required.');
        if (!this.product.sku) this.pushFieldError('sku', 'SKU is required.');
        if (this.product.name && this.product.name.length < 3) this.pushFieldError('name', 'Min length is 3.');
        if (this.product.sku && this.product.sku.length < 3) this.pushFieldError('sku', 'Min length is 3.');
        if (this.product.name && this.product.name.length > 255) this.pushFieldError('name', 'Max length is 255.');
        if (this.product.sku && this.product.sku.length > 100) this.pushFieldError('sku', 'Max length is 100.');

        // Required selects
        if (!this.normalizeId(this.product.category)) this.pushFieldError('category', 'Category is required.');

        if (!this.product.brands || !Array.isArray(this.product.brands) || this.product.brands.length === 0) {
          this.pushFieldError('brands', 'At least one brand is required.');
        }
        if (!this.normalizeId(this.product.unit_default))
          this.pushFieldError('unit_default', 'Default Unit is required.');
      },
      validatePriceMatrix() {
        // Enforce uniqueness of (unit, price_type) rows and numeric price
        const comboSet = new Set();
        const errors = [];

        this.productPriceUnits.forEach((pu, idx) => {
          const unitId = this.normalizeId(pu.unit);
          const priceTypeId = this.normalizeId(pu.price_type);

          if (!unitId && (pu.is_purchase || pu.is_sale || pu.price)) {
            errors.push(`Row ${idx + 1}: Unit is required when defining price or flags.`);
          }

          if (priceTypeId && unitId) {
            const key = `${unitId}|${priceTypeId}`;
            if (comboSet.has(key)) errors.push(`Row ${idx + 1}: Duplicate (Unit, PriceType).`);
            comboSet.add(key);
          }

          if (pu.price !== null && pu.price !== undefined && pu.price !== '') {
            const num = Number(pu.price);
            if (Number.isNaN(num) || num < 0) errors.push(`Row ${idx + 1}: Price must be a non‑negative number.`);
          }
        });

        if (errors.length) {
          Swal.fire({
            icon: 'error',
            title: 'Price table errors',
            html: `<ul style=\"text-align:left\">${errors.map(e => `<li>${e}</li>`).join('')}</ul>`,
          });
          return false;
        }
        return true;
      },

      // --- Submit ---
      async handleSubmit() {
        if (this.isReadOnly) return; // locked in View mode

        this.submitting = true;
        this.clearFieldErrors();

        try {
          // 1) Minimal validations (client‑side)
          this.validateMinimal();
          if (Object.keys(this.fieldErrors).length) {
            this.submitting = false;
            return;
          }
          if (!this.validatePriceMatrix()) {
            this.submitting = false;
            return;
          }

          // 2) Clean payload (per Chalan‑Pro Policy: sanitize before sending)
          const cleanedPriceUnits = [];
          const cleanedPrices = [];
          const unitSeen = new Set();

          this.productPriceUnits.forEach(pu => {
            const unitId = this.normalizeId(pu.unit);
            const priceTypeId = this.normalizeId(pu.price_type);

            // units table for flags (dedupe per unit)
            if (unitId && !unitSeen.has(unitId)) {
              cleanedPriceUnits.push({
                unit: unitId,
                is_purchase: !!pu.is_purchase,
                is_sale: !!pu.is_sale,
              });
              unitSeen.add(unitId);
            }

            // prices table (complete entries only)
            const priceValue = pu.price === '' || pu.price === null || pu.price === undefined ? null : Number(pu.price);
            if (unitId && priceTypeId && priceValue !== null && !Number.isNaN(priceValue)) {
              cleanedPrices.push({
                unit: unitId,
                price_type: priceTypeId,
                price: priceValue,
                is_purchase: !!pu.is_purchase,
                is_sale: !!pu.is_sale,
                is_default: !!pu.is_default,
                valid_from: pu.valid_from || null,
                valid_until: pu.valid_until || null,
                is_active: pu.is_active !== false,
              });
            }
          });

          const payload = {
            name: this.product.name,
            sku: this.product.sku,
            category: this.normalizeId(this.product.category),
            brands_data: this.product.brands || [],
            unit_default: this.normalizeId(this.product.unit_default),
            reorder_level: this.product.reorder_level,
            is_active: !!this.product.is_active,
            price_units: cleanedPriceUnits,
            prices: cleanedPrices,
          };

          // 3) Send
          const id = this.objectId || this.$route?.params?.id || this.$route?.query?.id;
          const url = id ? `/api/products/${id}/` : '/api/products/';
          const method = id ? 'put' : 'post';

          await axios({ method, url, data: payload });

          // Success per Chalan‑Pro CRUD Pattern: silent success + redirect
          this.notifyToastSuccess?.(id ? 'Product updated' : 'Product created');
          this.$router.push(LIST_ROUTE);
        } catch (err) {
          console.error('Failed to save product:', err);

          const status = err?.response?.status;
          const data = err?.response?.data;

          // Map DRF 400 field errors to inputs
          if (status === 400 && data && typeof data === 'object') {
            for (const [key, value] of Object.entries(data)) {
              const msg = Array.isArray(value) ? value.join(' ') : String(value);
              if (['name', 'sku', 'category', 'brands', 'brands_data', 'unit_default'].includes(key)) {
                const fieldKey = key === 'brands_data' ? 'brands' : key;
                this.pushFieldError(fieldKey, msg);
              }
            }

            const nonField = data.non_field_errors || data.detail;
            if (nonField) {
              const msg = Array.isArray(nonField) ? nonField.join(' ') : String(nonField);
              Swal.fire({ icon: 'error', title: 'Validation Error', text: msg });
            }

            if (!Object.keys(this.fieldErrors).length && !data.non_field_errors && !data.detail) {
              Swal.fire({
                icon: 'error',
                title: 'Validation Error',
                html: `<pre style=\"text-align:left\">${this.escapeHtml(JSON.stringify(data, null, 2))}</pre>`,
              });
            }
          } else {
            Swal.fire('Error', 'Failed to save product', 'error');
          }
        } finally {
          this.submitting = false;
        }
      },

      cancelForm() {
        // Per pattern: always allow back/escape to list
        if (window.history.length > 1) this.$router.back();
        else this.$router.push(LIST_ROUTE);
      },

      // --- Modal open helpers ---
      openCategoryModal(mode, id = null) {
        this.modalObjectId = mode === 'edit' ? id : null;
        this.$refs.categoryModal.openModal();
      },
      openBrandModal(mode, id = null) {
        this.modalObjectId = mode === 'edit' ? id : null;
        this.$refs.brandModal.openModal();
      },
      openUnitModal(mode, id = null) {
        this.modalObjectId = mode === 'edit' ? id : null;
        this.$refs.unitModal.openModal();
      },

      loadCategories() {
        axios.get('/api/productcategory/').then(res => {
          this.categories = res.data;
        });
      },
      loadBrands() {
        axios.get('/api/productbrand/').then(res => {
          this.brands = res.data;
        });
      },
      loadUnits() {
        axios.get('/api/unitsofmeasure/').then(res => {
          this.units = res.data;
        });
      },
      loadPriceTypes() {
        axios.get('/api/pricetypes/').then(res => {
          this.priceTypes = res.data;
        });
      },

      handleOpenModal(type) {
        this.modalObjectId = null;
        if (type === 'priceType') this.$refs.priceTypeModal.openModal();
        if (type === 'unit') this.$refs.unitModal.openModal();
      },
      handleEditModal({ type, id }) {
        this.modalObjectId = id;
        if (type === 'priceType') this.$refs.priceTypeModal.openModal();
        if (type === 'unit') this.$refs.unitModal.openModal();
      },

      // --- Utils ---
      getDefaultBrandName() {
        if (!this.product.brands || this.product.brands.length === 0) return null;

        // Find the brand object that matches the first brand ID (which should be default)
        const firstBrandId = this.product.brands[0];
        const brandObj = this.brands.find(b => b.id === firstBrandId);
        return brandObj ? brandObj.name : null;
      },

      escapeHtml(str) {
        return String(str)
          .replaceAll('&', '&amp;')
          .replaceAll('<', '&lt;')
          .replaceAll('>', '&gt;')
          .replaceAll('"', '&quot;')
          .replaceAll("'", '&#039;');
      },
    },
  };
</script>

<style scoped>
  .card-header h5 {
    font-weight: 600;
  }
  /* Optional: add a red border on invalid vue-select to match Bootstrap */
  :deep(.is-invalid .vs__dropdown-toggle) {
    border-color: #dc3545;
  }
  :deep(.is-invalid .vs__dropdown-toggle:focus) {
    box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
  }
</style>
