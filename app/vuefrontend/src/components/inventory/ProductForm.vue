<template>
  <div class="container-fluid position-relative my-2">
    <h3 class="text-center text-warning mb-2">Product Form</h3>
    <div class="card shadow mb-2 mx-3">
      <div class="card-header d-flex align-items-center justify-content-between flex-wrap gap-2">
        <div class="flex-grow-1 text-center px-2">
          <h6 class="mb-0 text-primary">{{ pageTitle }}</h6>
        </div>
        <div class="d-flex align-items-center gap-2 ms-auto">
          <button
            v-if="
              isReadOnly &&
              currentProductId &&
              hasPermission('appinventory.change_product')
            "
            type="button"
            class="btn btn-primary btn-sm"
            @click="goToEdit"
            v-tt
            data-title="Switch to edit mode for this product">
            <i class="fas fa-pen me-1" aria-hidden="true"></i>
            Edit product
          </button>
          <button class="btn btn-outline-secondary btn-sm" @click="cancelForm">
            Back
          </button>
        </div>
      </div>

      <div class="card-body">
        <form @submit.prevent="handleSubmit" novalidate>
          <!-- Product fields -->
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label d-flex align-items-center gap-2">
                Name
              </label>
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
              <div v-if="fieldErrors.name" class="invalid-feedback">
                {{ fieldErrors.name }}
              </div>
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
              <div v-if="fieldErrors.sku" class="invalid-feedback">
                {{ fieldErrors.sku }}
              </div>
            </div>

            <div class="col-md-6 mb-3">
              <label class="form-label d-flex align-items-center gap-2">
                Model #
                <i
                  v-tt
                  class="fas fa-info-circle text-muted"
                  data-title="Optional. Manufacturer or catalog model (e.g. 14A19060W6CCT02-02)."></i>
              </label>
              <input
                v-model.trim="product.model_number"
                type="text"
                class="form-control"
                maxlength="128"
                :class="{ 'is-invalid': fieldErrors.model_number }"
                :disabled="isReadOnly"
                autocomplete="off"
                v-tt
                data-title="Manufacturer or catalog model reference" />
              <div v-if="fieldErrors.model_number" class="invalid-feedback">
                {{ fieldErrors.model_number }}
              </div>
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
                  :reduce="(cat) => cat.id"
                  label="name"
                  placeholder="Select Category"
                  class="flex-grow-1"
                  :class="{ 'is-invalid': fieldErrors.category }"
                  :disabled="
                    isReadOnly ||
                    !hasPermission('appinventory.add_productcategory')
                  "
                  @open="loadCategories"
                  v-tt
                  data-title="Required field for product categorization" />
                <button
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="openCategoryModal('add')"
                  :disabled="
                    isReadOnly ||
                    !hasPermission('appinventory.add_productcategory')
                  "
                  v-tt
                  data-title="Add a new category to the system">
                  <img
                    src="@assets/img/icon-addlink.svg"
                    alt="Add"
                    width="15"
                    height="15" />
                </button>
                <button
                  v-if="product.category"
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="openCategoryModal('edit', product.category)"
                  :disabled="
                    isReadOnly ||
                    !hasPermission('appinventory.change_productcategory')
                  "
                  v-tt
                  data-title="Edit the currently selected category">
                  <img
                    src="@assets/img/icon-changelink.svg"
                    alt="Edit"
                    width="15"
                    height="15" />
                </button>
              </div>
              <div v-if="fieldErrors.category" class="invalid-feedback d-block">
                {{ fieldErrors.category }}
              </div>
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
                  :reduce="(brand) => brand.id"
                  v-model="product.brands"
                  placeholder="Select Brands"
                  class="flex-grow-1"
                  :class="{ 'is-invalid': fieldErrors.brands }"
                  :disabled="
                    isReadOnly ||
                    !hasPermission('appinventory.add_productcategory')
                  "
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
                  :disabled="
                    isReadOnly ||
                    !hasPermission('appinventory.add_productbrand')
                  "
                  v-tt
                  data-title="Add a new brand to the system">
                  <img
                    src="@assets/img/icon-addlink.svg"
                    alt="Add"
                    width="15"
                    height="15" />
                </button>
              </div>
              <div v-if="fieldErrors.brands" class="invalid-feedback d-block">
                {{ fieldErrors.brands }}
              </div>
              <div
                v-if="product.brands && product.brands.length > 0"
                class="small text-muted mt-1">
                <strong>Default Brand:</strong>
                {{ getDefaultBrandName() || "Will be auto-assigned" }}
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
                  :reduce="(unit) => unit.id"
                  label="name"
                  placeholder="Select Unit"
                  class="flex-grow-1"
                  :class="{ 'is-invalid': fieldErrors.unit_default }"
                  :disabled="
                    isReadOnly ||
                    !hasPermission('appinventory.add_productcategory')
                  "
                  @open="loadUnits"
                  v-tt
                  data-title="Required field for unit selection" />
                <button
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="openUnitModal('add')"
                  :disabled="
                    isReadOnly ||
                    !hasPermission('appinventory.add_unitofmeasure')
                  "
                  v-tt
                  data-title="Add a new unit of measure to the system">
                  <img
                    src="@assets/img/icon-addlink.svg"
                    alt="Add"
                    width="15"
                    height="15" />
                </button>
                <button
                  v-if="product.unit_default"
                  class="btn btn-outline-secondary btn-sm ms-1"
                  type="button"
                  @click="openUnitModal('edit', product.unit_default)"
                  :disabled="
                    isReadOnly ||
                    !hasPermission('appinventory.change_unitofmeasure')
                  "
                  v-tt
                  data-title="Edit the currently selected unit">
                  <img
                    src="@assets/img/icon-changelink.svg"
                    alt="Edit"
                    width="15"
                    height="15" />
                </button>
              </div>
              <div
                v-if="fieldErrors.unit_default"
                class="invalid-feedback d-block">
                {{ fieldErrors.unit_default }}
              </div>
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

            <!-- Tracking Mode -->
            <div class="col-md-6 mb-3">
              <label class="form-label d-flex align-items-center gap-2">
                Tracking Mode
                <i
                  v-tt
                  class="fas fa-info-circle text-muted"
                  data-title="QUANTITY = stock by quantity; SERIALIZED = track by individual units (equipment/tools)."></i>
              </label>
              <v-select
                v-model="product.tracking_mode"
                :options="trackingModeOptions"
                :reduce="(o) => o.value"
                label="label"
                class="flex-grow-1"
                :disabled="isReadOnly"
                placeholder="Select tracking mode..." />
              <div
                v-if="product.tracking_mode === 'SERIALIZED'"
                class="alert alert-info small mt-2 mb-0 py-2">
                Serialized products create one unit (SerializedItem) per
                quantity on purchase.
              </div>
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
            ref="productPriceUnitTable"
            v-model="productPriceUnits"
            :priceTypes="priceTypes"
            :units="units"
            @open-modal="handleOpenModal"
            @edit-modal="handleEditModal"
            @refresh-priceTypes="loadPriceTypes"
            @refresh-units="loadUnits"
            :readonly="isReadOnly" />

          <div class="mt-4 d-flex gap-2">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isReadOnly || submitting">
              <i v-if="!submitting" class="fas fa-save me-1"></i>
              <i v-else class="fas fa-spinner fa-spin me-1"></i>
              {{
                submitting
                  ? "Saving..."
                  : $route?.query?.id || $route?.params?.id || objectId
                  ? "Update"
                  : "Save"
              }}
            </button>
            <button
              type="button"
              class="btn btn-outline-secondary"
              @click="cancelForm">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modals for Category, Brand, Unit, PriceType -->
    <CategoryModal
      ref="categoryModal"
      :objectId="modalObjectId"
      @refreshCategories="loadCategories" />
    <BrandModal
      ref="brandModal"
      :objectId="modalObjectId"
      @refreshBrands="loadBrands" />
    <UnitModal
      ref="unitModal"
      :objectId="modalObjectId"
      @refreshUnits="loadUnits" />
    <PriceTypeModal
      ref="priceTypeModal"
      :objectId="modalObjectId"
      @refresh="loadPriceTypes" />
  </div>
</template>

<script>
// Options API to keep consistency with current codebase
import axios from "axios";
import VSelect from "vue-select";
import "vue-select/dist/vue-select.css";
import Swal from "sweetalert2";
import ProductPriceUnitTable from "@/components/inventory/ProductPriceUnitTable.vue";
import CategoryModal from "@/components/inventory/CategoryModal.vue";
import BrandModal from "@/components/inventory/BrandModal.vue";
import UnitModal from "@/components/inventory/UnitModal.vue";
import PriceTypeModal from "@/components/inventory/PriceTypeModal.vue";

const LIST_ROUTE_NAME = "product-list"; // ProductListView (/products)

export default {
  name: "ProductForm",
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
        name: "",
        sku: "",
        model_number: "",
        category: "",
        brands: [],
        unit_default: "",
        reorder_level: 0,
        tracking_mode: "QUANTITY",
        is_active: true,
      },
      trackingModeOptions: [
        { value: "QUANTITY", label: "QUANTITY (Inventory item)" },
        { value: "SERIALIZED", label: "SERIALIZED (Equipment/Tool)" },
      ],
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
      if (this.isReadOnly) return "View Product";
      const id =
        this.objectId || this.$route?.params?.id || this.$route?.query?.id;
      return id ? "Edit Product" : "Create Product";
    },
    /** Id del producto cargado (query, params o prop), para navegar a edición desde vista */
    currentProductId() {
      const raw =
        this.objectId ?? this.$route?.params?.id ?? this.$route?.query?.id;
      if (raw === undefined || raw === null || raw === "") return null;
      return String(raw);
    },
  },
  created() {
    // Support query-based navigation from ProductList: ?mode=view|edit&id=XX
    this.isReadOnly = this.$route?.query?.mode === "view" || this.isReadOnly;

    this.loadInitialData();

    const id =
      this.objectId || this.$route?.params?.id || this.$route?.query?.id;
    if (id) this.loadProduct();
  },
  watch: {
    "$route.query.mode"(val) {
      this.isReadOnly = val === "view";
    },
    "$route.query.id"(val, oldVal) {
      if (val && val !== oldVal) this.loadProduct();
    },
  },
  methods: {
    // --- Loaders ---
    async loadInitialData() {
      try {
        const [catRes, brandRes, unitRes, priceTypeRes] = await Promise.all([
          axios.get("/api/productcategory/"),
          axios.get("/api/productbrand/"),
          axios.get("/api/unitsofmeasure/"),
          axios.get("/api/pricetypes/"),
        ]);

        this.categories = catRes.data;
        this.brands = brandRes.data;
        this.units = unitRes.data;
        this.priceTypes = priceTypeRes.data;
      } catch (err) {
        console.error("Failed to load select options", err);
        this.notifyToastError?.("Failed to load lists");
      }
    },
    async loadProduct() {
      try {
        const id =
          this.objectId || this.$route?.params?.id || this.$route?.query?.id;
        if (!id) return;
        const res = await axios.get(`/api/products/${id}/`);
        this.product = res.data;
        if (this.product.model_number == null) this.product.model_number = "";

        // Convert brands response to array of IDs
        if (res.data.brands && Array.isArray(res.data.brands)) {
          this.product.brands = res.data.brands.map((brand) =>
            typeof brand === "object" ? brand.id : brand
          );
        } else {
          // Ensure brands is always an array
          this.product.brands = [];
        }

        const prices = Array.isArray(res.data.prices) ? res.data.prices : [];
        const unitsFlags = Array.isArray(res.data.price_units)
          ? res.data.price_units
          : [];

        // Map unit → flags (purchase/sale)
        const flagsByUnit = new Map();
        unitsFlags.forEach((u) => {
          const uid = this.normalizeId(u.unit);
          if (uid)
            flagsByUnit.set(uid, {
              is_purchase: !!u.is_purchase,
              is_sale: !!u.is_sale,
            });
        });

        // Build one table row per PRICE record (unit, price_type)
        const rows = prices.map((p) => {
          const uid = typeof p.unit === "object" ? p.unit?.id : p.unit;
          const ptid =
            typeof p.price_type === "object" ? p.price_type?.id : p.price_type;
          const fb = flagsByUnit.get(uid) || {
            is_purchase: false,
            is_sale: false,
          };
          return {
            id: p.id || null,
            price_type: ptid,
            unit: uid,
            is_purchase:
              typeof p.is_purchase !== "undefined"
                ? !!p.is_purchase
                : fb.is_purchase,
            is_sale:
              typeof p.is_sale !== "undefined" ? !!p.is_sale : fb.is_sale,
            price: p.price,
            is_default: !!p.is_default,
            valid_from: p.valid_from || null,
            valid_until: p.valid_until || null,
            is_active: p.is_active !== false,
          };
        });

        // If there are unit flags without price rows, show placeholders for visibility
        unitsFlags.forEach((u) => {
          const uid = this.normalizeId(u.unit);
          if (uid && !rows.some((r) => r.unit === uid)) {
            rows.push({
              id: null,
              price_type: "",
              unit: uid,
              is_purchase: !!u.is_purchase,
              is_sale: !!u.is_sale,
              price: "",
              is_default: false,
              valid_from: "",
              valid_until: "",
              is_active: true,
            });
          }
        });

        this.productPriceUnits = rows.length ? rows : [];
        if (!this.productPriceUnits.length && !this.isReadOnly) {
          // ensure at least one empty row for UX on fresh create
          this.productPriceUnits.push({
            id: null,
            price_type: "",
            unit: "",
            is_purchase: false,
            is_sale: false,
            price: "",
            is_default: false,
            valid_from: "",
            valid_until: "",
            is_active: true,
          });
        }
      } catch (err) {
        console.error("Error loading product:", err);
        this.notifyToastError?.("Failed to load product");
      }
    },

    // --- Helpers ---
    normalizeId(value) {
      return typeof value === "object" ? value?.id : value;
    },
    pushFieldError(field, msg) {
      this.fieldErrors[field] = msg;
    },
    clearFieldErrors() {
      this.fieldErrors = {};
    },
    validateMinimal() {
      // Trim and minimal client validations per Chalan‑Pro Standard Form Pattern
      this.product.name = (this.product.name || "").trim();
      this.product.sku = (this.product.sku || "").trim();
      this.product.model_number = (this.product.model_number || "").trim();

      if (!this.product.name) this.pushFieldError("name", "Name is required.");
      if (!this.product.sku) this.pushFieldError("sku", "SKU is required.");
      if (this.product.name && this.product.name.length < 3)
        this.pushFieldError("name", "Min length is 3.");
      if (this.product.sku && this.product.sku.length < 3)
        this.pushFieldError("sku", "Min length is 3.");
      if (this.product.name && this.product.name.length > 255)
        this.pushFieldError("name", "Max length is 255.");
      if (this.product.sku && this.product.sku.length > 100)
        this.pushFieldError("sku", "Max length is 100.");
      if (this.product.model_number && this.product.model_number.length > 128)
        this.pushFieldError("model_number", "Max length is 128.");

      // Required selects
      if (!this.normalizeId(this.product.category))
        this.pushFieldError("category", "Category is required.");

      if (
        !this.product.brands ||
        !Array.isArray(this.product.brands) ||
        this.product.brands.length === 0
      ) {
        this.pushFieldError("brands", "At least one brand is required.");
      }
      if (!this.normalizeId(this.product.unit_default))
        this.pushFieldError("unit_default", "Default Unit is required.");
    },
    validatePriceMatrix() {
      // Enforce uniqueness of (unit, price_type) rows and numeric price
      const comboSet = new Set();
      const strictFlagErrors =
        this.$refs.productPriceUnitTable?.validateStrictPurchaseSaleFlags?.() ||
        [];
      const errors = [...strictFlagErrors];

      this.productPriceUnits.forEach((pu, idx) => {
        const unitId = this.normalizeId(pu.unit);
        const priceTypeId = this.normalizeId(pu.price_type);

        if (!unitId && (pu.is_purchase || pu.is_sale || pu.price)) {
          errors.push(
            `Row ${idx + 1}: Unit is required when defining price or flags.`
          );
        }

        if (priceTypeId && unitId) {
          const key = [
            unitId,
            priceTypeId,
            pu.is_purchase ? 1 : 0,
            pu.is_sale ? 1 : 0,
            pu.valid_from || null,
            pu.valid_until || null,
          ].join("|");
          if (comboSet.has(key))
            errors.push(
              `Row ${
                idx + 1
              }: Duplicate combination (Unit, Price Type, Flags, Dates).`
            );
          comboSet.add(key);
        }

        if (pu.price !== null && pu.price !== undefined && pu.price !== "") {
          const num = Number(pu.price);
          if (Number.isNaN(num) || num < 0)
            errors.push(`Row ${idx + 1}: Price must be a non‑negative number.`);
        }
      });

      if (errors.length) {
        Swal.fire({
          icon: "error",
          title: "Price table errors",
          html: `<ul style=\"text-align:left\">${errors
            .map((e) => `<li>${e}</li>`)
            .join("")}</ul>`,
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
        const unitFlags = new Map();

        this.productPriceUnits.forEach((pu) => {
          const unitId = this.normalizeId(pu.unit);
          const priceTypeId = this.normalizeId(pu.price_type);
          const priceId =
            pu.id === undefined || pu.id === null
              ? null
              : this.normalizeId(pu.id);

          // units table for flags (agrupar por unidad con OR lógico)
          if (unitId) {
            const prev = unitFlags.get(unitId) || {
              is_purchase: false,
              is_sale: false,
            };
            unitFlags.set(unitId, {
              is_purchase: prev.is_purchase || !!pu.is_purchase,
              is_sale: prev.is_sale || !!pu.is_sale,
            });
          }

          // prices table (complete entries only)
          const priceValue =
            pu.price === "" || pu.price === null || pu.price === undefined
              ? null
              : Number(pu.price);
          if (
            unitId &&
            priceTypeId &&
            priceValue !== null &&
            !Number.isNaN(priceValue)
          ) {
            cleanedPrices.push({
              id: priceId,
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

        unitFlags.forEach((flags, unitId) => {
          cleanedPriceUnits.push({
            unit: unitId,
            is_purchase: flags.is_purchase,
            is_sale: flags.is_sale,
          });
        });

        const payload = {
          name: this.product.name,
          sku: this.product.sku,
          model_number: this.product.model_number || "",
          category: this.normalizeId(this.product.category),
          brands_data: this.product.brands || [],
          unit_default: this.normalizeId(this.product.unit_default),
          reorder_level: this.product.reorder_level,
          tracking_mode: this.product.tracking_mode || "QUANTITY",
          is_active: !!this.product.is_active,
          price_units: cleanedPriceUnits,
          prices: cleanedPrices,
        };

        // 3) Send
        const id =
          this.objectId || this.$route?.params?.id || this.$route?.query?.id;
        const url = id ? `/api/products/${id}/` : "/api/products/";
        const method = id ? "put" : "post";

        const res = await axios({ method, url, data: payload });
        const savedId =
          id || (res?.data?.id != null ? String(res.data.id) : null);

        // Success per Chalan‑Pro CRUD Pattern: silent success + redirect
        this.notifyToastSuccess?.(id ? "Product updated" : "Product created");

        if (savedId) {
          await this.$router.push({
            path: "/products/form",
            query: { mode: "view", id: String(savedId) },
          });
        } else {
          this.$router.push({ name: LIST_ROUTE_NAME }).catch(() => {});
        }
      } catch (err) {
        console.error("Failed to save product:", err);

        const status = err?.response?.status;
        const data = err?.response?.data;

        if (this.responseLooksLikeHtmlPayload(err)) {
          this.showProductSaveError(err);
          return;
        }

        // Map DRF / Django-validation 400 JSON to inputs & Swal
        if (
          status === 400 &&
          data &&
          typeof data === "object" &&
          !Array.isArray(data)
        ) {
          const skipFieldMapKeys = new Set([
            "non_field_errors",
            "detail",
            "__all__",
          ]);

          for (const [key, value] of Object.entries(data)) {
            if (skipFieldMapKeys.has(key)) continue;
            const msg = Array.isArray(value) ? value.join(" ") : String(value);
            if (
              [
                "name",
                "sku",
                "model_number",
                "category",
                "brands",
                "brands_data",
                "unit_default",
                "tracking_mode",
              ].includes(key)
            ) {
              const fieldKey = key === "brands_data" ? "brands" : key;
              this.pushFieldError(fieldKey, msg);
            }
          }

          const nonFieldCombined = this.combineNonFieldApiMessages(data);
          if (nonFieldCombined) {
            Swal.fire({
              icon: "error",
              title: "Validation Error",
              text: nonFieldCombined,
            });
          }

          const hasUnhandledKeys = Object.entries(data).some(
            ([k, v]) =>
              !skipFieldMapKeys.has(k) &&
              v != null &&
              ![
                "name",
                "sku",
                "model_number",
                "category",
                "brands",
                "brands_data",
                "unit_default",
                "tracking_mode",
              ].includes(k)
          );

          if (
            !Object.keys(this.fieldErrors).length &&
            !nonFieldCombined &&
            hasUnhandledKeys
          ) {
            Swal.fire({
              icon: "error",
              title: "Validation Error",
              html: `<pre style=\"text-align:left\">${this.escapeHtml(
                JSON.stringify(data, null, 2)
              )}</pre>`,
            });
          }
        } else {
          this.showProductSaveError(err);
        }
      } finally {
        this.submitting = false;
      }
    },

    cancelForm() {
      this.$router.push({ name: LIST_ROUTE_NAME }).catch(() => {});
    },

    goToEdit() {
      const id = this.currentProductId;
      if (!id) return;
      this.$router.push({
        path: "/products/form",
        query: { mode: "edit", id },
      });
    },

    // --- Modal open helpers ---
    openCategoryModal(mode, id = null) {
      this.modalObjectId = mode === "edit" ? id : null;
      this.$refs.categoryModal.openModal();
    },
    openBrandModal(mode, id = null) {
      this.modalObjectId = mode === "edit" ? id : null;
      this.$refs.brandModal.openModal();
    },
    openUnitModal(mode, id = null) {
      this.modalObjectId = mode === "edit" ? id : null;
      this.$refs.unitModal.openModal();
    },

    loadCategories() {
      axios.get("/api/productcategory/").then((res) => {
        this.categories = res.data;
      });
    },
    loadBrands() {
      axios.get("/api/productbrand/").then((res) => {
        this.brands = res.data;
      });
    },
    loadUnits() {
      axios.get("/api/unitsofmeasure/").then((res) => {
        this.units = res.data;
      });
    },
    loadPriceTypes() {
      axios.get("/api/pricetypes/").then((res) => {
        this.priceTypes = res.data;
      });
    },

    handleOpenModal(type) {
      this.modalObjectId = null;
      if (type === "priceType") this.$refs.priceTypeModal.openModal();
      if (type === "unit") this.$refs.unitModal.openModal();
    },
    handleEditModal({ type, id }) {
      this.modalObjectId = id;
      if (type === "priceType") this.$refs.priceTypeModal.openModal();
      if (type === "unit") this.$refs.unitModal.openModal();
    },

    // --- Utils ---
    getDefaultBrandName() {
      if (!this.product.brands || this.product.brands.length === 0) return null;

      // Find the brand object that matches the first brand ID (which should be default)
      const firstBrandId = this.product.brands[0];
      const brandObj = this.brands.find((b) => b.id === firstBrandId);
      return brandObj ? brandObj.name : null;
    },

    escapeHtml(str) {
      return String(str)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    },

    /** True when Axios got an HTML debug page (e.g. Django DEBUG ValidationError trace). */
    responseLooksLikeHtmlPayload(err) {
      const ctype = String(
        err?.response?.headers?.["content-type"] ??
          err?.response?.headers?.["Content-Type"] ??
          ""
      ).toLowerCase();
      if (ctype.includes("text/html")) return true;
      const d = err?.response?.data;
      if (typeof d !== "string" || !d.length) return false;
      const head = d.trim().slice(0, 500).toLowerCase();
      return head.startsWith("<!doctype html") || head.includes("<html");
    },

    /** Django/DRF non-field payloads → single line for alerts (detail, __all__, non_field_errors). */
    combineNonFieldApiMessages(data) {
      if (!data || typeof data !== "object") return "";
      const parts = [];
      for (const key of ["detail", "__all__", "non_field_errors"]) {
        const raw = data[key];
        if (raw == null || raw === "") continue;
        if (Array.isArray(raw)) parts.push(raw.map(String).join(" "));
        else parts.push(String(raw));
      }
      return parts.filter(Boolean).join(" ").trim();
    },

    /** Safe body text from JSON error payloads (never embeds HTML). */
    summarizeApiErrorData(data) {
      if (data == null) return "";
      if (typeof data === "string") {
        const s = data.trim();
        if (
          s.toLowerCase().startsWith("<!doctype html") ||
          s.toLowerCase().includes("<html")
        ) {
          return "";
        }
        return s;
      }
      if (typeof data !== "object" || Array.isArray(data))
        return String(data);

      const nonFieldOnly = this.combineNonFieldApiMessages(data);
      const fieldKeys = Object.keys(data).filter(
        (k) =>
          !["detail", "__all__", "non_field_errors"].includes(k) &&
          data[k] != null
      );
      if (!fieldKeys.length && nonFieldOnly) return nonFieldOnly;

      if (data.detail != null) {
        const d = data.detail;
        const dStr = Array.isArray(d)
          ? d.map(String).join(" ")
          : String(d);
        if (dStr.trim()) return dStr;
      }
      if (data.__all__ != null) {
        const a = data.__all__;
        return Array.isArray(a) ? a.map(String).join(" ") : String(a);
      }

      const lines = [];
      for (const [key, value] of Object.entries(data)) {
        if (value == null) continue;
        if (["detail", "__all__", "non_field_errors"].includes(key)) continue;
        let msg;
        if (Array.isArray(value)) msg = value.map(String).join(" ");
        else if (typeof value === "object") msg = JSON.stringify(value);
        else msg = String(value);
        lines.push(`${key}: ${msg}`);
      }
      if (nonFieldOnly) lines.unshift(nonFieldOnly);
      return lines.join("\n").trim();
    },

    /** Non‑400‑JSON failures: avoids dumping HTML debug pages into Swal. */
    showProductSaveError(err) {
      if (this.responseLooksLikeHtmlPayload(err)) {
        Swal.fire({
          icon: "error",
          title: "Failed to save product",
          html: `<div style="text-align:left" class="small">${this.escapeHtml(
            "The server returned an HTML error page instead of JSON. Typical causes: Django DEBUG=true with an unhandled exception, or a middleware/proxy returning HTML."
          )}</div><div class="small text-muted mt-2">${this.escapeHtml(
            "Turn off DEBUG or fix the failing validation on the API so responses use JSON."
          )}</div>`,
        });
        return;
      }

      const res = err?.response;
      const status = res?.status;
      const summary = this.summarizeApiErrorData(res?.data);

      if (!res) {
        Swal.fire({
          icon: "error",
          title: "Could not reach the server",
          text:
            err?.message ||
            "Check your connection and try again.",
        });
        return;
      }

      if (status === 401) {
        Swal.fire({
          icon: "error",
          title: "Sign-in required",
          text: summary || "Your session may have expired.",
        });
        return;
      }
      if (status === 403) {
        Swal.fire({
          icon: "error",
          title: "Permission denied",
          text: summary || "You cannot save this product with your current user.",
        });
        return;
      }
      if (status === 404) {
        Swal.fire({
          icon: "error",
          title: "Product not found",
          text: summary || "Open the product again from the list.",
        });
        return;
      }
      if (status === 409) {
        Swal.fire({
          icon: "error",
          title: "Conflict",
          text:
            summary ||
            "Conflict with existing data (for example SKU or FK in use).",
        });
        return;
      }
      if (status >= 500) {
        Swal.fire({
          icon: "error",
          title: "Server error",
          text:
            summary ||
            "Something went wrong while saving; try again later.",
        });
        return;
      }

      Swal.fire({
        icon: "error",
        title: "Failed to save product",
        text:
          summary ||
          err?.message ||
          `Request failed (HTTP ${status}).`,
      });
    },
  },
};
</script>

<style scoped>
.card-header {
  background-color: #f3f3f3;
}
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

@media (max-width: 768px) {
  .container-fluid {
    padding-left: 0.5rem;
    padding-right: 0.5rem;
  }

  .card {
    margin-left: 0.25rem !important;
    margin-right: 0.25rem !important;
  }

  .card-header {
    padding: 0.75rem;
  }

  .card-body {
    padding: 1rem;
  }
}

@media (max-width: 992px) and (min-width: 769px) {
  .card {
    margin-left: 1rem !important;
    margin-right: 1rem !important;
  }
}
</style>
