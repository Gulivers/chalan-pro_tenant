<template>
  <JRPage>
    <JRPageHeader :title="pageTitle" :description="pageDescription">
      <template #actions>
        <JRButton
          v-if="
            isReadOnly &&
            currentProductId &&
            hasPermission('appinventory.change_product')
          "
          variant="primary"
          size="sm"
          @click="goToEdit">
          Edit product
        </JRButton>
      </template>
    </JRPageHeader>

    <form class="jr-product-form" @submit.prevent="handleSubmit" novalidate>
      <div
        v-if="attentionCount || formBannerMessage"
        ref="formBanner"
        class="jr-form-banner"
        role="alert"
        tabindex="-1">
        {{
          formBannerMessage ||
          `${attentionCount} ${
            attentionCount === 1 ? "field needs" : "fields need"
          } attention`
        }}
      </div>

      <p v-if="productLoading" class="jr-product-form__loading" role="status">
        Loading product…
      </p>

      <JRSection v-if="!productLoading" title="Identity">
        <div class="jr-form-grid jr-form-grid--identity">
          <JRField
            v-slot="{ describedby, invalid }"
            label="Name"
            required
            inputId="product-name"
            :error="fieldErrors.name">
            <JRInput
              inputId="product-name"
              v-model="product.name"
              :disabled="isReadOnly"
              :invalid="invalid"
              :required="true"
              :ariaDescribedby="describedby" />
          </JRField>
          <JRField
            v-slot="{ describedby, invalid }"
            label="SKU"
            required
            inputId="product-sku"
            hint="Must be unique. Used in warehouse and purchasing."
            :error="fieldErrors.sku">
            <JRInput
              inputId="product-sku"
              v-model="product.sku"
              :disabled="isReadOnly"
              :invalid="invalid"
              :required="true"
              :ariaDescribedby="describedby" />
          </JRField>
          <JRField
            v-slot="{ describedby, invalid }"
            label="Model #"
            inputId="product-model-number"
            :error="fieldErrors.model_number">
            <JRInput
              inputId="product-model-number"
              v-model="product.model_number"
              :disabled="isReadOnly"
              :invalid="invalid"
              :ariaDescribedby="describedby" />
          </JRField>
        </div>
      </JRSection>

      <JRSection v-if="!productLoading" title="Classification">
        <div class="jr-form-grid jr-form-grid--classification">
          <JRField
            v-slot="{ describedby, invalid }"
            label="Category"
            required
            inputId="product-category"
            :error="fieldErrors.category">
            <JRSelectAddon
              inputId="product-category"
              v-model="product.category"
              :options="categories"
              optionLabel="name"
              optionValue="id"
              placeholder="Select Category"
              :disabled="isReadOnly"
              :invalid="invalid"
              :required="true"
              :ariaDescribedby="describedby"
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
              @show="loadCategories"
              @add="openCatalog('category')"
              @edit="openCatalog('category', product.category)" />
          </JRField>

          <JRField
            v-slot="{ describedby, invalid }"
            label="Brands"
            required
            inputId="product-brands"
            hint="The first selected brand is the default for purchasing."
            :error="fieldErrors.brands">
            <JRSelectAddon
              inputId="product-brands"
              v-model="product.brands"
              :options="brands"
              optionLabel="name"
              optionValue="id"
              placeholder="Select Brands"
              multiple
              :disabled="isReadOnly"
              :invalid="invalid"
              :required="true"
              :ariaDescribedby="describedby"
              :showAdd="true"
              :addDisabled="
                isReadOnly || !hasPermission('appinventory.add_productbrand')
              "
              addLabel="Add a new brand to the system"
              filter
              @show="loadBrands"
              @add="openCatalog('brand')" />
            <JRField
              v-if="selectedBrandOptions.length"
              class="jr-product-form__default-brand"
              label="Default for purchasing"
              inputId="product-default-brand">
              <JRSelect
                v-if="selectedBrandOptions.length > 1"
                inputId="product-default-brand"
                :modelValue="defaultBrandId"
                :options="selectedBrandOptions"
                optionLabel="name"
                optionValue="id"
                :disabled="isReadOnly"
                placeholder="Select default brand"
                @update:modelValue="setDefaultBrand" />
              <p v-else class="jr-product-form__brand-name">
                {{ getDefaultBrandName() }}
              </p>
            </JRField>
          </JRField>

          <JRField
            v-slot="{ describedby, invalid }"
            label="Default Unit"
            required
            inputId="product-unit-default"
            :error="fieldErrors.unit_default">
            <JRSelectAddon
              inputId="product-unit-default"
              v-model="product.unit_default"
              :options="units"
              optionLabel="name"
              optionValue="id"
              placeholder="Select Unit"
              :disabled="isReadOnly"
              :invalid="invalid"
              :required="true"
              :ariaDescribedby="describedby"
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
              @show="loadUnits"
              @add="openCatalog('unit')"
              @edit="openCatalog('unit', product.unit_default)" />
          </JRField>
        </div>
      </JRSection>

      <JRSection v-if="!productLoading" title="Inventory">
        <div class="jr-form-grid jr-form-grid--inventory">
          <JRField
            v-slot="{ describedby }"
            label="Tracking Mode"
            inputId="product-tracking-mode"
            hint="Quantity counts stock. Serialized tracks each unit (tools and equipment).">
            <JRSelect
              inputId="product-tracking-mode"
              v-model="product.tracking_mode"
              :options="trackingModeOptions"
              optionLabel="label"
              optionValue="value"
              :disabled="isReadOnly"
              :ariaDescribedby="describedby"
              placeholder="Select tracking mode..." />
            <Message
              v-if="product.tracking_mode === 'SERIALIZED'"
              class="jr-product-form__info"
              severity="info"
              :closable="false">
              Serialized products create one tracked unit per quantity on
              purchase.
            </Message>
          </JRField>

          <JRField
            v-slot="{ describedby }"
            label="Reorder Level"
            inputId="product-reorder-level"
            hint="In the default warehouse unit.">
            <JRInput
              inputId="product-reorder-level"
              type="number"
              :min="0"
              :modelValue="product.reorder_level"
              :disabled="isReadOnly"
              :ariaDescribedby="describedby"
              @update:modelValue="
                product.reorder_level = $event == null ? 0 : $event
              " />
          </JRField>

          <JRField label="Active" inputId="isActive">
            <JRCheckbox
              v-model="product.is_active"
              inputId="isActive"
              ariaLabel="Active"
              :disabled="isReadOnly" />
          </JRField>
        </div>
      </JRSection>

      <JRSection v-if="!productLoading" title="Price and Unit Settings">
        <template #actions>
          <JRButton
            v-if="!isReadOnly && productPriceUnits.length"
            variant="secondary"
            size="sm"
            @click="addPriceRow">
            + Add Row
          </JRButton>
        </template>
        <p class="jr-product-form__note">
          Price rows can use a unit other than the warehouse default. Only a
          sale price can be the default.
        </p>
        <ProductPriceUnitTable
          ref="productPriceUnitTable"
          v-model="productPriceUnits"
          :priceTypes="priceTypes"
          :units="units"
          :readonly="isReadOnly"
          :hideToolbar="true"
          :rowErrors="priceRowErrors"
          @open-modal="handleOpenModal"
          @edit-modal="handleEditModal"
          @refresh-priceTypes="loadPriceTypes"
          @refresh-units="loadUnits" />
      </JRSection>

      <div v-if="!productLoading" class="jr-product-form__actions">
        <span v-if="formIsDirty" class="jr-unsaved">Unsaved</span>
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
          {{ isReadOnly ? "Back to list" : "Cancel" }}
        </JRButton>
      </div>
    </form>

    <JRDrawer
      class="jr-catalog-drawer"
      :visible="catalogDrawerVisible"
      :header="catalogDrawerTitle"
      position="right"
      @update:visible="onCatalogVisible">
      <ProductCatalogForm
        v-if="catalogDrawerVisible && catalogSpec"
        :key="catalogFormKey"
        :schemaEndpoint="catalogSpec.schemaEndpoint"
        :apiEndpoint="catalogSpec.apiEndpoint"
        :objectId="catalogObjectId"
        :backLabel="catalogBackLabel"
        @saved="onCatalogSaved"
        @cancel="closeCatalogDrawer" />
    </JRDrawer>

    <JRDialog
      :visible="leaveDialogVisible"
      header="Leave without saving?"
      message="Unsaved changes will be lost."
      confirmLabel="Leave"
      confirmVariant="danger"
      @update:visible="onLeaveVisible"
      @confirm="confirmLeave" />
  </JRPage>
</template>

<script>
import axios from "axios";
import Message from "primevue/message";
import ProductPriceUnitTable from "@/components/inventory/ProductPriceUnitTable.vue";
import ProductCatalogForm from "@/components/inventory/ProductCatalogForm.vue";
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
  JRDrawer,
  JRDialog,
} from "@ui";

const CATALOG_SPECS = {
  category: {
    schemaEndpoint: "/api/schema/product-category/",
    apiEndpoint: "/api/productcategory/",
    addTitle: "Add Category",
    editTitle: "Edit Category",
    refresh: "loadCategories",
  },
  brand: {
    schemaEndpoint: "/api/schema/productbrand/",
    apiEndpoint: "/api/productbrand/",
    addTitle: "Add Brand",
    editTitle: "Edit Brand",
    refresh: "loadBrands",
  },
  unit: {
    schemaEndpoint: "/api/schema/unitofmeasure/",
    apiEndpoint: "/api/unitsofmeasure/",
    addTitle: "Add Unit of Measure",
    editTitle: "Edit Unit of Measure",
    refresh: "loadUnits",
  },
  priceType: {
    schemaEndpoint: "/api/schema/pricetype/",
    apiEndpoint: "/api/pricetypes/",
    addTitle: "Add Price Type",
    editTitle: "Edit Price Type",
    refresh: "loadPriceTypes",
  },
};

const LIST_ROUTE_NAME = "product-list";
const PRODUCT_FIELD_KEYS = [
  "name",
  "sku",
  "model_number",
  "category",
  "brands",
  "brands_data",
  "unit_default",
  "tracking_mode",
];

export default {
  name: "ProductForm",
  components: {
    ProductPriceUnitTable,
    ProductCatalogForm,
    Message,
    JRPage,
    JRPageHeader,
    JRSection,
    JRField,
    JRButton,
    JRInput,
    JRSelect,
    JRSelectAddon,
    JRCheckbox,
    JRDrawer,
    JRDialog,
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
        { value: "QUANTITY", label: "Quantity — stock by count" },
        { value: "SERIALIZED", label: "Serialized — track each unit" },
      ],
      productPriceUnits: [],
      categories: [],
      brands: [],
      units: [],
      priceTypes: [],
      catalogType: null,
      catalogObjectId: null,
      catalogDrawerVisible: false,
      catalogFromSheet: false,
      catalogSheetIndex: null,
      submitting: false,
      submitAttempted: false,
      isReadOnly: false,
      fieldErrors: {},
      priceRowErrors: [],
      formBannerMessage: "",
      dirtySnapshot: "",
      leaveDialogVisible: false,
      leaveAction: null,
      pendingRouteNext: null,
      leaveResolved: false,
      productLoading: false,
    };
  },
  computed: {
    formIsDirty() {
      return this.isDirty();
    },
    defaultBrandId() {
      return this.product.brands && this.product.brands.length
        ? this.product.brands[0]
        : null;
    },
    selectedBrandOptions() {
      const ids = (this.product.brands || []).map((id) => String(id));
      return (this.brands || []).filter((brand) => ids.includes(String(brand.id)));
    },
    pageTitle() {
      if (this.isReadOnly) return "View Product";
      const id =
        this.objectId || this.$route?.params?.id || this.$route?.query?.id;
      return id ? "Edit Product" : "Create Product";
    },
    pageDescription() {
      if (this.isReadOnly) {
        return "Read-only. Use Edit product to change this SKU.";
      }
      if (this.currentProductId) {
        return "Update identity, stock settings, and prices.";
      }
      return "Create a SKU the crew can buy and sell.";
    },
    attentionCount() {
      const fields = Object.values(this.fieldErrors).filter(Boolean).length;
      const rows = this.priceRowErrors.filter(Boolean).length;
      return fields + rows;
    },
    catalogSpec() {
      return CATALOG_SPECS[this.catalogType] || null;
    },
    catalogDrawerTitle() {
      if (!this.catalogSpec) return "";
      return this.catalogObjectId
        ? this.catalogSpec.editTitle
        : this.catalogSpec.addTitle;
    },
    catalogBackLabel() {
      return this.catalogFromSheet ? "Back to price row" : "Cancel";
    },
    catalogFormKey() {
      return `${this.catalogType || "none"}-${this.catalogObjectId || "new"}`;
    },
    currentProductId() {
      const raw =
        this.objectId ?? this.$route?.params?.id ?? this.$route?.query?.id;
      if (raw === undefined || raw === null || raw === "") return null;
      return String(raw);
    },
  },
  created() {
    this.isReadOnly = this.$route?.query?.mode === "view" || this.isReadOnly;
    this.loadInitialData();
    const id =
      this.objectId || this.$route?.params?.id || this.$route?.query?.id;
    if (id) this.loadProduct();
    else {
      this.seedInitialPriceRow();
      this.captureDirtySnapshot();
    }
  },
  watch: {
    "$route.query.mode"(val) {
      this.isReadOnly = val === "view";
    },
    "$route.query.id"(val, oldVal) {
      if (val && val !== oldVal) this.loadProduct();
    },
    "product.name"() {
      this.revalidateKnownField("name");
    },
    "product.sku"() {
      this.revalidateKnownField("sku");
    },
    "product.model_number"() {
      this.revalidateKnownField("model_number");
    },
    "product.category"() {
      this.revalidateKnownField("category");
    },
    "product.brands"() {
      this.revalidateKnownField("brands");
    },
    "product.unit_default"() {
      this.revalidateKnownField("unit_default");
    },
    productPriceUnits: {
      deep: true,
      handler() {
        if (this.submitAttempted || this.priceRowErrors.some(Boolean)) {
          this.validatePriceMatrix();
        }
      },
    },
  },
  beforeRouteLeave(to, from, next) {
    if (this.isReadOnly || !this.isDirty()) {
      next();
      return;
    }
    this.askLeave("guard", next);
  },
  methods: {
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
      const id =
        this.objectId || this.$route?.params?.id || this.$route?.query?.id;
      if (!id) return;
      this.productLoading = true;
      try {
        const res = await axios.get(`/api/products/${id}/`);
        this.product = res.data;
        if (this.product.model_number == null) this.product.model_number = "";
        if (res.data.brands && Array.isArray(res.data.brands)) {
          this.product.brands = res.data.brands.map((brand) =>
            typeof brand === "object" ? brand.id : brand
          );
        } else {
          this.product.brands = [];
        }
        const defaultBrandId = this.normalizeId(res.data.default_brand);
        if (defaultBrandId) this.setDefaultBrand(defaultBrandId);

        const prices = Array.isArray(res.data.prices) ? res.data.prices : [];
        const unitsFlags = Array.isArray(res.data.price_units)
          ? res.data.price_units
          : [];
        const flagsByUnit = new Map();
        unitsFlags.forEach((u) => {
          const uid = this.normalizeId(u.unit);
          if (uid) {
            flagsByUnit.set(uid, {
              is_purchase: !!u.is_purchase,
              is_sale: !!u.is_sale,
            });
          }
        });

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

        this.productPriceUnits = rows;
        this.captureDirtySnapshot();
      } catch (err) {
        console.error("Error loading product:", err);
        this.notifyToastError?.("Failed to load product");
      } finally {
        this.productLoading = false;
      }
    },
    normalizeId(value) {
      return typeof value === "object" ? value?.id : value;
    },
    seedInitialPriceRow() {
      if (this.currentProductId || this.productPriceUnits.length) return;
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
    },
    captureDirtySnapshot() {
      this.dirtySnapshot = this.serializeFormState();
    },
    serializeFormState() {
      return JSON.stringify({
        product: {
          name: this.product.name,
          sku: this.product.sku,
          model_number: this.product.model_number,
          category: this.product.category,
          brands: this.product.brands,
          unit_default: this.product.unit_default,
          reorder_level: this.product.reorder_level,
          tracking_mode: this.product.tracking_mode,
          is_active: this.product.is_active,
        },
        prices: this.productPriceUnits.filter(
          (row) => !this.isTentativePriceRow(row)
        ),
      });
    },
    isDirty() {
      if (this.isReadOnly || !this.dirtySnapshot) return false;
      return this.serializeFormState() !== this.dirtySnapshot;
    },
    setDefaultBrand(id) {
      if (id == null || id === "") return;
      const current = this.product.brands || [];
      const rest = current.filter((item) => String(item) !== String(id));
      this.product.brands = [id, ...rest];
    },
    askLeave(action, routerNext = null) {
      this.leaveAction = action;
      this.pendingRouteNext = routerNext;
      this.leaveResolved = false;
      this.leaveDialogVisible = true;
    },
    confirmLeave() {
      const action = this.leaveAction;
      const next = this.pendingRouteNext;
      this.leaveResolved = true;
      this.leaveAction = null;
      this.pendingRouteNext = null;
      this.leaveDialogVisible = false;
      if (action === "guard" && typeof next === "function") next();
      else if (action === "cancel") {
        this.$router.push({ name: LIST_ROUTE_NAME }).catch(() => {});
      }
    },
    onLeaveVisible(visible) {
      this.leaveDialogVisible = visible;
      if (visible) return;
      if (this.leaveResolved) {
        this.leaveResolved = false;
        return;
      }
      if (this.leaveAction === "guard" && typeof this.pendingRouteNext === "function") {
        this.pendingRouteNext(false);
      }
      this.leaveAction = null;
      this.pendingRouteNext = null;
    },
    pushFieldError(field, msg) {
      this.fieldErrors = { ...this.fieldErrors, [field]: msg };
    },
    clearOneFieldError(field) {
      if (!this.fieldErrors[field]) return;
      const next = { ...this.fieldErrors };
      delete next[field];
      this.fieldErrors = next;
    },
    clearFieldErrors() {
      this.fieldErrors = {};
      this.priceRowErrors = [];
      this.formBannerMessage = "";
    },
    fieldMessage(field) {
      if (field === "name") {
        const name = (this.product.name || "").trim();
        if (!name) return "Name is required.";
        if (name.length < 3) return "Min length is 3.";
        if (name.length > 255) return "Max length is 255.";
        return "";
      }
      if (field === "sku") {
        const sku = (this.product.sku || "").trim();
        if (!sku) return "SKU is required.";
        if (sku.length < 3) return "Min length is 3.";
        if (sku.length > 100) return "Max length is 100.";
        return "";
      }
      if (field === "model_number") {
        const model = (this.product.model_number || "").trim();
        if (model && model.length > 128) return "Max length is 128.";
        return "";
      }
      if (field === "category") {
        return this.normalizeId(this.product.category)
          ? ""
          : "Category is required.";
      }
      if (field === "brands") {
        if (
          !this.product.brands ||
          !Array.isArray(this.product.brands) ||
          this.product.brands.length === 0
        ) {
          return "At least one brand is required.";
        }
        return "";
      }
      if (field === "unit_default") {
        return this.normalizeId(this.product.unit_default)
          ? ""
          : "Default Unit is required.";
      }
      return "";
    },
    revalidateKnownField(field) {
      if (!this.submitAttempted && !this.fieldErrors[field]) return;
      const msg = this.fieldMessage(field);
      if (msg) this.pushFieldError(field, msg);
      else this.clearOneFieldError(field);
    },
    focusFirstError() {
      this.$nextTick(() => {
        const banner = this.$refs.formBanner;
        if (banner && typeof banner.focus === "function") banner.focus();
        const fieldError = this.$el?.querySelector?.(".jr-field__error");
        if (fieldError) {
          const wrap = fieldError.closest(".jr-field");
          wrap?.scrollIntoView?.({ behavior: "smooth", block: "center" });
          const control = wrap?.querySelector(
            'input:not([type="hidden"]), textarea, select, [role="combobox"]'
          );
          if (control && typeof control.focus === "function") {
            control.focus();
            return;
          }
        }
        const rowError = this.$el?.querySelector?.(".jr-price-row-error");
        if (rowError) {
          rowError.scrollIntoView({ behavior: "smooth", block: "center" });
          const prev = rowError.closest("tr")?.previousElementSibling;
          const control = (
            prev || rowError.closest(".jr-price-row-item")
          )?.querySelector('input:not([type="hidden"]), [role="combobox"]');
          control?.focus?.();
        }
      });
    },
    validateMinimal() {
      this.product.name = (this.product.name || "").trim();
      this.product.sku = (this.product.sku || "").trim();
      this.product.model_number = (this.product.model_number || "").trim();
      ["name", "sku", "model_number", "category", "brands", "unit_default"].forEach(
        (field) => {
          const msg = this.fieldMessage(field);
          if (msg) this.pushFieldError(field, msg);
          else this.clearOneFieldError(field);
        }
      );
    },
    isSentPriceRow(pu) {
      if (!pu || this.isTentativePriceRow(pu)) return false;
      const unitId = this.normalizeId(pu.unit);
      const priceTypeId = this.normalizeId(pu.price_type);
      const priceValue =
        pu.price === "" || pu.price === null || pu.price === undefined
          ? null
          : Number(pu.price);
      return !!(
        unitId &&
        priceTypeId &&
        priceValue !== null &&
        !Number.isNaN(priceValue)
      );
    },
    isTentativePriceRow(pu) {
      if (!pu || pu.id) return false;
      const emptyType = !this.normalizeId(pu.price_type);
      const emptyUnit = !this.normalizeId(pu.unit);
      const emptyPrice =
        pu.price === null || pu.price === undefined || pu.price === "";
      const defaultFlags = !pu.is_purchase && !pu.is_sale && !pu.is_default;
      const emptyDates = !pu.valid_from && !pu.valid_until;
      const defaultActive = pu.is_active !== false;
      return (
        emptyType &&
        emptyUnit &&
        emptyPrice &&
        defaultFlags &&
        emptyDates &&
        defaultActive
      );
    },
    incompleteRowMessage(pu) {
      const missing = [];
      if (!this.normalizeId(pu.price_type)) missing.push("Price Type");
      if (!this.normalizeId(pu.unit)) missing.push("Unit");
      const priceEmpty =
        pu.price === null || pu.price === undefined || pu.price === "";
      if (priceEmpty) missing.push("Price");
      if (!missing.length) return "";
      const needed =
        missing.length === 1
          ? missing[0]
          : `${missing.slice(0, -1).join(", ")} and ${missing[missing.length - 1]}`;
      return `Complete or delete this row to save the product. Still needed: ${needed}.`;
    },
    validatePriceMatrix() {
      const comboSet = new Set();
      const byRow = this.productPriceUnits.map(() => []);
      this.productPriceUnits.forEach((pu, idx) => {
        if (this.isTentativePriceRow(pu)) return;
        const unitId = this.normalizeId(pu.unit);
        const priceTypeId = this.normalizeId(pu.price_type);
        const purchaseOk = pu.is_purchase === true || pu.is_purchase === false;
        const saleOk = pu.is_sale === true || pu.is_sale === false;
        const priceEmpty =
          pu.price === null || pu.price === undefined || pu.price === "";
        const complete = !!(
          unitId &&
          priceTypeId &&
          !priceEmpty &&
          !Number.isNaN(Number(pu.price))
        );
        if (!complete) byRow[idx].push(this.incompleteRowMessage(pu));
        if (!purchaseOk || !saleOk) {
          byRow[idx].push("Purchase and Sale must each be on or off.");
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
          if (comboSet.has(key)) {
            byRow[idx].push(
              "Duplicate combination (Unit, Price Type, Flags, Dates)."
            );
          }
          comboSet.add(key);
        }
        if (!priceEmpty) {
          const num = Number(pu.price);
          if (Number.isNaN(num) || num < 0) {
            byRow[idx].push("Price must be a non-negative number.");
          }
        }
        if (pu.valid_from && pu.valid_until && pu.valid_from > pu.valid_until) {
          byRow[idx].push("Valid From must be on or before Valid Until.");
        }
      });
      this.priceRowErrors = byRow.map((msgs) => msgs.filter(Boolean).join(" "));
      return !this.priceRowErrors.some(Boolean);
    },
    async handleSubmit() {
      if (this.isReadOnly) return;
      this.submitting = true;
      this.submitAttempted = true;
      this.clearFieldErrors();
      try {
        this.validateMinimal();
        const priceOk = this.validatePriceMatrix();
        if (Object.keys(this.fieldErrors).length || !priceOk) {
          this.submitting = false;
          this.focusFirstError();
          return;
        }
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
        const id =
          this.objectId || this.$route?.params?.id || this.$route?.query?.id;
        const url = id ? `/api/products/${id}/` : "/api/products/";
        const method = id ? "put" : "post";
        const res = await axios({ method, url, data: payload });
        const savedId =
          id || (res?.data?.id != null ? String(res.data.id) : null);
        this.notifyToastSuccess?.(id ? "Product updated" : "Product created");
        this.captureDirtySnapshot();
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
        this.applySaveFailure(err);
      } finally {
        this.submitting = false;
      }
    },
    applySaveFailure(err) {
      const status = err?.response?.status;
      const data = err?.response?.data;
      if (this.responseLooksLikeHtmlPayload(err)) {
        this.formBannerMessage =
          "The server returned an unexpected error page. Try again.";
        this.notifyToastError?.(this.formBannerMessage);
        this.focusFirstError();
        return;
      }
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
          if (key === "prices" || key === "price_units") {
            this.mapPriceApiErrors(key, value);
            continue;
          }
          const msg = this.humanizeErrorValue(value);
          if (PRODUCT_FIELD_KEYS.includes(key)) {
            const fieldKey = key === "brands_data" ? "brands" : key;
            this.pushFieldError(fieldKey, msg);
          }
        }
        const leftover = [];
        const nonFieldCombined = this.combineNonFieldApiMessages(data);
        if (nonFieldCombined) leftover.push(nonFieldCombined);
        const mappedKeys = new Set([
          ...skipFieldMapKeys,
          ...PRODUCT_FIELD_KEYS,
          "prices",
          "price_units",
        ]);
        Object.entries(data).forEach(([key, value]) => {
          if (mappedKeys.has(key) || value == null) return;
          leftover.push(
            `${this.humanizeKey(key)}: ${this.humanizeErrorValue(value)}`
          );
        });
        if (leftover.length) {
          this.formBannerMessage = leftover.join(" ");
          this.notifyToastError?.(this.formBannerMessage);
        }
        if (this.attentionCount || this.formBannerMessage) this.focusFirstError();
        return;
      }
      this.formBannerMessage = this.humanSaveFailure(err);
      this.notifyToastError?.(this.formBannerMessage);
      this.focusFirstError();
    },
    mapPriceApiErrors(key, value) {
      if (Array.isArray(value)) {
        const next = [...this.priceRowErrors];
        const sentIndexes = this.productPriceUnits
          .map((row, i) => (this.isSentPriceRow(row) ? i : null))
          .filter((i) => i != null);
        value.forEach((item, sentIdx) => {
          if (item == null) return;
          const msg = this.humanizeErrorValue(item);
          if (!msg) return;
          const uiIdx = sentIndexes[sentIdx];
          if (uiIdx == null) {
            this.formBannerMessage = [this.formBannerMessage, msg]
              .filter(Boolean)
              .join(" ");
            return;
          }
          next[uiIdx] = [next[uiIdx], msg].filter(Boolean).join(" ");
        });
        this.priceRowErrors = next;
        return;
      }
      const msg = this.humanizeErrorValue(value);
      if (msg) {
        this.formBannerMessage = [this.formBannerMessage, msg]
          .filter(Boolean)
          .join(" ");
      }
    },
    humanizeKey(key) {
      return String(key).replace(/_/g, " ");
    },
    humanizeErrorValue(value) {
      if (value == null) return "";
      if (typeof value === "string") return value;
      if (Array.isArray(value)) {
        return value
          .map((v) => this.humanizeErrorValue(v))
          .filter(Boolean)
          .join(" ");
      }
      if (typeof value === "object") {
        return Object.entries(value)
          .map(([k, v]) => `${this.humanizeKey(k)}: ${this.humanizeErrorValue(v)}`)
          .filter(Boolean)
          .join(" ");
      }
      return String(value);
    },
    cancelForm() {
      if (!this.isReadOnly && this.isDirty()) {
        this.askLeave("cancel");
        return;
      }
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
    addPriceRow() {
      this.$refs.productPriceUnitTable?.addRowFromToolbar?.();
    },
    openCatalog(type, id = null, fromSheet = false, sheetIndex = null) {
      if (this.isReadOnly) return;
      this.$refs.productPriceUnitTable?.closeSheet?.();
      this.catalogType = type;
      this.catalogObjectId = id == null ? null : this.normalizeId(id);
      this.catalogFromSheet = !!fromSheet;
      this.catalogSheetIndex = fromSheet ? sheetIndex : null;
      this.catalogDrawerVisible = true;
    },
    closeCatalogDrawer() {
      const reopenIndex = this.catalogFromSheet ? this.catalogSheetIndex : null;
      this.catalogDrawerVisible = false;
      this.catalogType = null;
      this.catalogObjectId = null;
      this.catalogFromSheet = false;
      this.catalogSheetIndex = null;
      if (reopenIndex != null) {
        this.$nextTick(() => {
          this.$refs.productPriceUnitTable?.openSheet?.(reopenIndex);
        });
      }
    },
    onCatalogVisible(visible) {
      if (!visible) this.closeCatalogDrawer();
      else this.catalogDrawerVisible = true;
    },
    onCatalogSaved() {
      const refreshName = this.catalogSpec?.refresh;
      if (refreshName && typeof this[refreshName] === "function") {
        this[refreshName]();
      }
      this.closeCatalogDrawer();
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
    handleOpenModal(payload) {
      const type = typeof payload === "string" ? payload : payload?.type;
      const fromSheet = typeof payload === "object" && !!payload?.fromSheet;
      const sheetIndex =
        typeof payload === "object" ? payload?.sheetIndex ?? null : null;
      if (type === "priceType" || type === "unit") {
        this.openCatalog(type, null, fromSheet, sheetIndex);
      }
    },
    handleEditModal(payload) {
      const type = payload?.type;
      const id = payload?.id;
      const fromSheet = !!payload?.fromSheet;
      const sheetIndex = payload?.sheetIndex ?? null;
      if (type === "priceType" || type === "unit") {
        this.openCatalog(type, id, fromSheet, sheetIndex);
      }
    },
    getDefaultBrandName() {
      if (!this.product.brands || this.product.brands.length === 0) return null;
      const firstBrandId = this.product.brands[0];
      const brandObj = this.brands.find(
        (b) => String(b.id) === String(firstBrandId)
      );
      return brandObj ? brandObj.name : null;
    },
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
    humanSaveFailure(err) {
      const res = err?.response;
      const status = res?.status;
      if (!res) {
        return (
          err?.message ||
          "Could not reach the server. Check your connection and try again."
        );
      }
      if (status === 401) return "Sign-in required. Your session may have expired.";
      if (status === 403) return "You cannot save this product with your current user.";
      if (status === 404) return "Product not found. Open it again from the list.";
      if (status === 409) return "Conflict with existing data. Check the SKU and try again.";
      if (status >= 500) return "Something went wrong while saving. Try again later.";
      return err?.message || `Request failed (HTTP ${status}).`;
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
  .jr-form-grid--identity,
  .jr-form-grid--classification,
  .jr-form-grid--inventory {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .jr-form-grid--identity,
  .jr-form-grid--classification,
  .jr-form-grid--inventory {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.jr-form-banner {
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
  background: var(--color-jr-danger-subtle);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
}

.jr-form-banner:focus {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-product-form__note {
  margin: 0 0 0.75rem;
  font-size: 0.75rem;
  line-height: 1.4;
  color: var(--color-jr-muted, #4b5563);
}

.jr-product-form__default-brand {
  margin-top: 0.65rem;
}

.jr-unsaved {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-warning-text);
  align-self: center;
}

.jr-product-form__loading {
  margin: 0 0 1rem;
  font-size: 0.9375rem;
  line-height: 1.45;
  color: var(--color-jr-text, #111827);
}

.jr-product-form__brand-name,
.jr-product-form__status {
  margin: 0.5rem 0 0;
  font-size: 0.9375rem;
  line-height: 1.4;
  color: var(--color-jr-text, #111827);
}

.jr-product-form__info {
  margin: 0.5rem 0 0;
  --p-message-info-background: var(--color-jr-info-subtle);
  --p-message-info-border-color: var(--color-jr-border);
  --p-message-info-color: var(--color-jr-info-text);
  --p-message-border-radius: var(--radius-jr-control, 0.5rem);
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

<style>
.p-drawer.jr-catalog-drawer {
  width: min(28rem, 100vw);
}

@media (max-width: 767.98px) {
  .p-drawer.jr-catalog-drawer {
    width: 100vw;
    max-width: 100vw;
  }
}
</style>
