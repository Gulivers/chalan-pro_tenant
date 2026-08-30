<template>
  <JRPage>
    <JRPageHeader :title="pageTitle">
      <template #actions>
        <JRButton
          v-if="
            isReadOnly &&
            currentProductId &&
            hasPermission('appinventory.change_product')
          "
          variant="primary"
          size="sm"
          v-tt
          data-title="Switch to edit mode for this product"
          @click="goToEdit">
          Edit product
        </JRButton>
        <JRButton variant="secondary" size="sm" @click="cancelForm">
          Back
        </JRButton>
      </template>
    </JRPageHeader>

    <form class="jr-product-form" @submit.prevent="handleSubmit" novalidate>
      <JRSection title="Identity">
        <div class="jr-form-grid jr-form-grid--measure">
          <JRField label="Name" required inputId="product-name" :error="fieldErrors.name">
            <JRInput
              inputId="product-name"
              v-model="product.name"
              :disabled="isReadOnly"
              :invalid="!!fieldErrors.name"
              v-tt
              data-title="Product name for identification and display purposes" />
          </JRField>
          <JRField
            label="SKU"
            required
            inputId="product-sku"
            :error="fieldErrors.sku"
            hint="Required (min 3). Unique identifier for warehouse/purchasing.">
            <JRInput
              inputId="product-sku"
              v-model="product.sku"
              :disabled="isReadOnly"
              :invalid="!!fieldErrors.sku"
              v-tt
              data-title="Unique identifier for warehouse and purchasing operations" />
          </JRField>
          <JRField
            label="Model #"
            inputId="product-model-number"
            :error="fieldErrors.model_number"
            hint="Optional. Manufacturer or catalog model (e.g. 14A19060W6CCT02-02).">
            <JRInput
              inputId="product-model-number"
              v-model="product.model_number"
              :disabled="isReadOnly"
              :invalid="!!fieldErrors.model_number"
              v-tt
              data-title="Manufacturer or catalog model reference" />
          </JRField>
        </div>
      </JRSection>

      <JRSection title="Classification">
        <div class="jr-form-grid jr-form-grid--measure">
          <JRField
            label="Category"
            required
            inputId="product-category"
            :error="fieldErrors.category"
            hint="Required. Group products for filtering and analytics.">
            <JRSelectAddon
              inputId="product-category"
              v-model="product.category"
              :options="categories"
              optionLabel="name"
              optionValue="id"
              placeholder="Select Category"
              :disabled="
                isReadOnly ||
                !hasPermission('appinventory.add_productcategory')
              "
              :invalid="!!fieldErrors.category"
              :showAdd="true"
              :showEdit="!!product.category"
              :addDisabled="
                isReadOnly ||
                !hasPermission('appinventory.add_productcategory')
              "
              :editDisabled="
                isReadOnly ||
                !hasPermission('appinventory.change_productcategory')
              "
              addLabel="Add a new category to the system"
              editLabel="Edit the currently selected category"
              filter
              v-tt
              data-title="Required field for product categorization"
              @show="loadCategories"
              @add="openCategoryModal('add')"
              @edit="openCategoryModal('edit', product.category)" />
          </JRField>

          <JRField
            label="Brands"
            required
            inputId="product-brands"
            :error="fieldErrors.brands"
            hint="Required for product traceability and brand management.">
            <JRSelectAddon
              inputId="product-brands"
              v-model="product.brands"
              :options="brands"
              optionLabel="name"
              optionValue="id"
              placeholder="Select Brands"
              multiple
              showClear
              :disabled="
                isReadOnly ||
                !hasPermission('appinventory.add_productcategory')
              "
              :invalid="!!fieldErrors.brands"
              :showAdd="true"
              :addDisabled="
                isReadOnly || !hasPermission('appinventory.add_productbrand')
              "
              addLabel="Add a new brand to the system"
              filter
              v-tt
              data-title="Required field - select one or more brands"
              @show="loadBrands"
              @add="openBrandModal('add')" />
            <p
              v-if="product.brands && product.brands.length > 0"
              class="jr-product-form__helper">
              <strong>Default Brand:</strong>
              {{ getDefaultBrandName() || "Will be auto-assigned" }}
            </p>
          </JRField>

          <JRField
            label="Default Unit"
            required
            inputId="product-unit-default"
            :error="fieldErrors.unit_default"
            hint="Required. Primary unit used for stock and valuations (e.g., EA, FT).">
            <JRSelectAddon
              inputId="product-unit-default"
              v-model="product.unit_default"
              :options="units"
              optionLabel="name"
              optionValue="id"
              placeholder="Select Unit"
              :disabled="
                isReadOnly ||
                !hasPermission('appinventory.add_productcategory')
              "
              :invalid="!!fieldErrors.unit_default"
              :showAdd="true"
              :showEdit="!!product.unit_default"
              :addDisabled="
                isReadOnly ||
                !hasPermission('appinventory.add_unitofmeasure')
              "
              :editDisabled="
                isReadOnly ||
                !hasPermission('appinventory.change_unitofmeasure')
              "
              addLabel="Add a new unit of measure to the system"
              editLabel="Edit the currently selected unit"
              filter
              v-tt
              data-title="Required field for unit selection"
              @show="loadUnits"
              @add="openUnitModal('add')"
              @edit="openUnitModal('edit', product.unit_default)" />
          </JRField>
        </div>
      </JRSection>

      <JRSection title="Inventory">
        <div class="jr-form-grid jr-form-grid--measure">
          <JRField
            label="Reorder Level"
            inputId="product-reorder-level"
            hint="Alert threshold to trigger restock notifications">
            <JRInput
              inputId="product-reorder-level"
              type="number"
              :min="0"
              :modelValue="product.reorder_level"
              :disabled="isReadOnly"
              v-tt
              data-title="Optional. Used for low-stock alerts and inventory management"
              @update:modelValue="
                product.reorder_level = $event == null ? 0 : $event
              " />
          </JRField>

          <JRField
            label="Tracking Mode"
            inputId="product-tracking-mode"
            hint="QUANTITY = stock by quantity; SERIALIZED = track by individual units (equipment/tools).">
            <JRSelect
              inputId="product-tracking-mode"
              v-model="product.tracking_mode"
              :options="trackingModeOptions"
              optionLabel="label"
              optionValue="value"
              :disabled="isReadOnly"
              placeholder="Select tracking mode..." />
            <p
              v-if="product.tracking_mode === 'SERIALIZED'"
              class="jr-product-form__info">
              Serialized products create one unit (SerializedItem) per
              quantity on purchase.
            </p>
          </JRField>

          <JRField>
            <JRCheckbox
              v-model="product.is_active"
              inputId="isActive"
              label="Active"
              :disabled="isReadOnly"
              v-tt
              data-title="Toggle product availability in the system" />
          </JRField>
        </div>
      </JRSection>

      <JRSection title="Price and Unit Settings">
        <ProductPriceUnitTable
          ref="productPriceUnitTable"
          v-model="productPriceUnits"
          :priceTypes="priceTypes"
          :units="units"
          :readonly="isReadOnly"
          @open-modal="handleOpenModal"
          @edit-modal="handleEditModal"
          @refresh-priceTypes="loadPriceTypes"
          @refresh-units="loadUnits" />
      </JRSection>

      <div class="jr-product-form__actions">
        <JRButton
          type="submit"
          variant="primary"
          :disabled="isReadOnly || submitting">
          {{
            submitting
              ? "Saving..."
              : $route?.query?.id || $route?.params?.id || objectId
              ? "Update"
              : "Save"
          }}
        </JRButton>
        <JRButton type="button" variant="secondary" @click="cancelForm">
          Cancel
        </JRButton>
      </div>
    </form>

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
  </JRPage>
</template>

<script>
// Options API to keep consistency with current codebase
import axios from "axios";
import Swal from "sweetalert2";
import ProductPriceUnitTable from "@/components/inventory/ProductPriceUnitTable.vue";
import CategoryModal from "@/components/inventory/CategoryModal.vue";
import BrandModal from "@/components/inventory/BrandModal.vue";
import UnitModal from "@/components/inventory/UnitModal.vue";
import PriceTypeModal from "@/components/inventory/PriceTypeModal.vue";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRButton,
  JRInput,
  JRSelect,
  JRSelectAddon,
  JRCheckbox,
} from "@ui";

const LIST_ROUTE_NAME = "product-list"; // ProductListView (/products)

export default {
  name: "ProductForm",
  components: {
    ProductPriceUnitTable,
    CategoryModal,
    BrandModal,
    UnitModal,
    PriceTypeModal,
    JRPage,
    JRPageHeader,
    JRSection,
    JRField,
    JRButton,
    JRInput,
    JRSelect,
    JRSelectAddon,
    JRCheckbox,
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
      axios
        .get("/api/productcategory/")
        .then((res) => {
          this.categories = res.data;
        })
        .catch(() => this.notifyToastError?.("Failed to load categories"));
    },
    loadBrands() {
      axios
        .get("/api/productbrand/")
        .then((res) => {
          this.brands = res.data;
        })
        .catch(() => this.notifyToastError?.("Failed to load brands"));
    },
    loadUnits() {
      axios
        .get("/api/unitsofmeasure/")
        .then((res) => {
          this.units = res.data;
        })
        .catch(() => this.notifyToastError?.("Failed to load units"));
    },
    loadPriceTypes() {
      axios
        .get("/api/pricetypes/")
        .then((res) => {
          this.priceTypes = res.data;
        })
        .catch(() => this.notifyToastError?.("Failed to load price types"));
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
.jr-form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1rem;
}

@media (min-width: 768px) {
  .jr-form-grid--measure {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    max-width: 48rem;
  }
}

.jr-product-form__helper {
  margin: 0.35rem 0 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-product-form__info {
  margin: 0.5rem 0 0;
  padding: 0.5rem 0.65rem;
  font-size: 0.75rem;
  line-height: 1.4;
  color: var(--color-jr-text, #111827);
  background: var(--color-jr-surface-muted, #f9fafb);
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-control, 0.5rem);
}

.jr-product-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.25rem;
  margin-top: 0.5rem;
  background: var(--color-jr-page, #f3f4f6);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}
</style>
