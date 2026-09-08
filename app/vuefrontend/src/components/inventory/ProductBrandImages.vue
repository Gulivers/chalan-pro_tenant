<template>
  <div class="jr-brand-images">
    <p
      v-if="!productId && !displayBrands.length"
      class="jr-brand-images__hint">
      Select at least one brand above, then add photos here. They are uploaded
      when you save the product.
    </p>

    <p v-else-if="productId && isLoading" class="jr-brand-images__status" role="status">
      Loading images…
    </p>

    <p v-else-if="error" class="jr-brand-images__error" role="alert">
      {{ error }}
    </p>

    <p
      v-else-if="isFlushing"
      class="jr-brand-images__status"
      role="status">
      Uploading photos…
    </p>

    <JREmptyState
      v-else-if="productId && !displayBrands.length"
      title="No brands on this product"
      description="Assign at least one brand and save to keep photos per brand." />

    <Tabs
      v-else-if="displayBrands.length"
      class="jr-brand-images__tabs"
      :value="activeBrandKey"
      scrollable
      @update:value="activeBrandKey = $event">
      <TabList>
        <Tab
          v-for="brand in displayBrands"
          :key="brand.id"
          :value="brandKey(brand.id)">
          {{ brand.name }}
          <JRBadge
            v-if="brand.is_default"
            class="jr-brand-images__default"
            value="Default"
            severity="info" />
          <span class="jr-brand-images__count">{{
            getImagesCount(brand.id)
          }}</span>
        </Tab>
      </TabList>
      <TabPanels>
        <TabPanel
          v-for="brand in displayBrands"
          :key="brand.id"
          :value="brandKey(brand.id)">
          <div
            v-if="canAdd && getImagesForBrand(brand.id).length"
            class="jr-brand-images__toolbar">
            <FileUpload
              :key="'upload-' + brand.id + '-' + uploadNonce"
              mode="basic"
              accept="image/*"
              :multiple="true"
              :auto="true"
              :customUpload="true"
              :disabled="isUploading === brand.id || busy || isFlushing"
              chooseLabel="Upload"
              :chooseButtonProps="uploadButtonProps"
              @uploader="onUpload($event, brand)" />
          </div>

          <p
            v-if="isUploading === brand.id"
            class="jr-brand-images__status"
            role="status">
            Uploading…
          </p>

          <JREmptyState
            v-if="!getImagesForBrand(brand.id).length && isUploading !== brand.id"
            title="No photos for this brand"
            :description="emptyBrandDescription">
            <FileUpload
              v-if="canAdd"
              :key="'upload-first-' + brand.id + '-' + uploadNonce"
              mode="basic"
              accept="image/*"
              :multiple="true"
              :auto="true"
              :customUpload="true"
              :disabled="isUploading === brand.id || busy || isFlushing"
              chooseLabel="Upload first image"
              :chooseButtonProps="uploadButtonProps"
              @uploader="onUpload($event, brand)" />
          </JREmptyState>

          <Gallery
            v-else
            class="jr-brand-gallery"
            :activeIndex="previewIndex"
            :fullscreen="isPreviewing(brand)"
            @update:activeIndex="previewIndex = $event"
            @update:fullscreen="onPreviewFullscreen($event, brand)">
            <ul class="jr-brand-images__grid">
              <li
                v-for="(image, index) in getImagesForBrand(brand.id)"
                :key="image.id"
                class="jr-brand-images__item">
                <div class="jr-brand-images__frame">
                  <button
                    type="button"
                    class="jr-brand-images__thumb"
                    :aria-label="`View ${image.description || brand.name + ' photo'}`"
                    @click="openPreview(brand, index)">
                    <img
                      :src="image.image_url"
                      :alt="image.description || `${brand.name} photo`"
                      class="jr-brand-images__img" />
                  </button>
                  <JRBadge
                    v-if="image.is_primary"
                    class="jr-brand-images__primary"
                    value="Primary"
                    severity="success" />
                </div>
                <div class="jr-brand-images__meta">
                  <span>{{
                    image.pending ? image.name : formatDate(image.uploaded_at)
                  }}</span>
                  <div class="jr-brand-images__actions">
                    <JRButton
                      v-if="image.pending"
                      variant="secondary"
                      size="sm"
                      @click="removePending(brand.id, image.pendingKey)">
                      Remove
                    </JRButton>
                    <JRButton
                      v-if="canChange && !image.pending && !image.is_primary"
                      variant="secondary"
                      size="sm"
                      @click="setAsPrimary(image)">
                      Set primary
                    </JRButton>
                    <JRButton
                      v-if="canDelete && !image.pending"
                      variant="danger"
                      size="sm"
                      :disabled="isDeleting === image.id"
                      @click="askDelete(image)">
                      Delete
                    </JRButton>
                  </div>
                </div>
              </li>
            </ul>
            <GalleryBackdrop />
            <GalleryHeader>
              <GalleryFullScreen aria-label="Close preview" />
            </GalleryHeader>
            <GalleryContent>
              <GalleryItem
                v-for="image in getImagesForBrand(brand.id)"
                :key="'preview-' + image.id">
                <img
                  :src="image.image_url"
                  :alt="image.description || `${brand.name} photo`" />
              </GalleryItem>
            </GalleryContent>
            <GalleryPrev
              v-if="getImagesCount(brand.id) > 1"
              aria-label="Previous photo" />
            <GalleryNext
              v-if="getImagesCount(brand.id) > 1"
              aria-label="Next photo" />
          </Gallery>
        </TabPanel>
      </TabPanels>
    </Tabs>

    <JRDialog
      :visible="deleteVisible"
      header="Delete image"
      message="Delete this image? This cannot be undone."
      confirmLabel="Delete"
      confirmVariant="danger"
      @update:visible="deleteVisible = $event"
      @confirm="confirmDelete" />
  </div>
</template>

<script>
import axios from "axios";
import FileUpload from "primevue/fileupload";
import Gallery from "primevue/gallery";
import GalleryBackdrop from "primevue/gallerybackdrop";
import GalleryContent from "primevue/gallerycontent";
import GalleryFullScreen from "primevue/galleryfullscreen";
import GalleryHeader from "primevue/galleryheader";
import GalleryItem from "primevue/galleryitem";
import GalleryNext from "primevue/gallerynext";
import GalleryPrev from "primevue/galleryprev";
import Tab from "primevue/tab";
import TabList from "primevue/tablist";
import TabPanel from "primevue/tabpanel";
import TabPanels from "primevue/tabpanels";
import Tabs from "primevue/tabs";
import { JRBadge, JRButton, JRDialog, JREmptyState } from "@ui";

export default {
  name: "ProductBrandImages",
  components: {
    FileUpload,
    Gallery,
    GalleryBackdrop,
    GalleryContent,
    GalleryFullScreen,
    GalleryHeader,
    GalleryItem,
    GalleryNext,
    GalleryPrev,
    Tab,
    TabList,
    TabPanel,
    TabPanels,
    Tabs,
    JRBadge,
    JRButton,
    JRDialog,
    JREmptyState,
  },
  props: {
    productId: {
      type: [Number, String],
      default: null,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
    revision: {
      type: Number,
      default: 0,
    },
    pendingBrands: {
      type: Array,
      default: () => [],
    },
    busy: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["changed"],
  data() {
    return {
      isLoading: false,
      isFlushing: false,
      error: "",
      brands: [],
      imagesByBrand: {},
      pendingByBrand: {},
      pendingSeq: 0,
      activeBrandKey: "",
      isUploading: null,
      isDeleting: null,
      deleteVisible: false,
      pendingDelete: null,
      uploadLock: false,
      uploadNonce: 0,
      previewBrandKey: "",
      previewIndex: 0,
      previewOpen: false,
    };
  },
  computed: {
    canEditProduct() {
      return !!this.hasPermission?.("appinventory.change_product");
    },
    canMutateProduct() {
      return (
        this.canEditProduct ||
        !!this.hasPermission?.("appinventory.add_product")
      );
    },
    canAdd() {
      return (
        !this.readonly &&
        this.canMutateProduct &&
        !!this.hasPermission?.("appinventory.add_productimage")
      );
    },
    canChange() {
      return (
        !this.readonly &&
        this.canMutateProduct &&
        !!this.hasPermission?.("appinventory.change_productimage")
      );
    },
    canDelete() {
      return (
        !this.readonly &&
        this.canEditProduct &&
        !!this.hasPermission?.("appinventory.change_product") &&
        !!this.hasPermission?.("appinventory.delete_productimage")
      );
    },
    createBrands() {
      return (this.pendingBrands || []).map((brand, index) => ({
        id: brand.id,
        name: brand.name,
        is_default: index === 0,
      }));
    },
    displayBrands() {
      return this.productId ? this.brands : this.createBrands;
    },
    emptyBrandDescription() {
      if (this.canAdd && !this.productId) {
        return "Choose photos now. They are uploaded when you save the product.";
      }
      if (this.canAdd) {
        return "Upload one or more images. Mark one as primary for the product list.";
      }
      return "No photos for this brand yet.";
    },
    uploadButtonProps() {
      return {
        size: "small",
        type: "button",
        class: "p-button p-component jr-button",
      };
    },
  },
  watch: {
    productId: {
      immediate: true,
      handler(id) {
        if (id) this.loadImages();
        else this.resetLoadedState();
      },
    },
    revision() {
      if (this.productId) this.loadImages();
    },
    pendingBrands: {
      immediate: true,
      handler() {
        this.syncPendingBrands();
      },
    },
  },
  beforeUnmount() {
    this.previewOpen = false;
    this.clearPending(true);
  },
  methods: {
    brandKey(id) {
      return String(id);
    },
    isPreviewing(brand) {
      return this.previewOpen && this.previewBrandKey === this.brandKey(brand.id);
    },
    openPreview(brand, index) {
      this.previewBrandKey = this.brandKey(brand.id);
      this.previewIndex = index;
      this.previewOpen = true;
    },
    onPreviewFullscreen(value, brand) {
      if (value) {
        this.previewBrandKey = this.brandKey(brand.id);
        this.previewOpen = true;
        return;
      }
      this.previewOpen = false;
    },
    resetLoadedState() {
      this.isLoading = false;
      this.error = "";
      this.brands = [];
      this.imagesByBrand = {};
    },
    syncPendingBrands() {
      if (this.productId) return;
      const allowed = new Set(
        (this.pendingBrands || []).map((brand) => this.brandKey(brand.id))
      );
      const next = { ...this.pendingByBrand };
      let changed = false;
      Object.keys(next).forEach((key) => {
        if (!allowed.has(key)) {
          this.revokeBrandUrls(next[key]);
          delete next[key];
          changed = true;
        }
      });
      if (changed) this.pendingByBrand = next;
      const brands = this.createBrands;
      if (
        brands.length &&
        !brands.some((brand) => this.brandKey(brand.id) === this.activeBrandKey)
      ) {
        this.activeBrandKey = this.brandKey(brands[0].id);
      }
    },
    getPendingForBrand(brandId) {
      return this.pendingByBrand[this.brandKey(brandId)] || [];
    },
    getImagesForBrand(brandId) {
      if (!this.productId) {
        return this.getPendingForBrand(brandId).map((item, index) => ({
          id: item.key,
          pendingKey: item.key,
          pending: true,
          image_url: item.url,
          name: item.file?.name || "Photo",
          is_primary: index === 0,
          uploaded_at: null,
        }));
      }
      const key = this.brandKey(brandId);
      return this.imagesByBrand[key] || this.imagesByBrand[brandId] || [];
    },
    getImagesCount(brandId) {
      return this.getImagesForBrand(brandId).length;
    },
    hasPending() {
      return Object.values(this.pendingByBrand).some(
        (list) => Array.isArray(list) && list.length > 0
      );
    },
    revokeBrandUrls(list) {
      (list || []).forEach((item) => {
        if (item?.url) URL.revokeObjectURL(item.url);
      });
    },
    clearPending(revoke = true) {
      if (revoke) {
        Object.values(this.pendingByBrand).forEach((list) =>
          this.revokeBrandUrls(list)
        );
      }
      this.pendingByBrand = {};
    },
    stageFiles(brand, files) {
      if (!brand?.id || !files.length) return;
      const key = this.brandKey(brand.id);
      const extra = files.map((file) => ({
        key: `pending-${++this.pendingSeq}`,
        file,
        url: URL.createObjectURL(file),
      }));
      this.pendingByBrand = {
        ...this.pendingByBrand,
        [key]: [...this.getPendingForBrand(brand.id), ...extra],
      };
      this.uploadNonce += 1;
    },
    removePending(brandId, pendingKey) {
      const key = this.brandKey(brandId);
      const next = this.getPendingForBrand(brandId).filter((item) => {
        if (item.key !== pendingKey) return true;
        if (item.url) URL.revokeObjectURL(item.url);
        return false;
      });
      this.pendingByBrand = { ...this.pendingByBrand, [key]: next };
    },
    async loadImages() {
      if (!this.productId) return;
      this.isLoading = true;
      this.error = "";
      try {
        const { data } = await axios.get(
          `/api/products/${this.productId}/images/`
        );
        this.brands = data.brands || [];
        this.imagesByBrand = data.images_by_brand || {};
        const current = this.brands.find(
          (brand) => this.brandKey(brand.id) === this.activeBrandKey
        );
        const fallback =
          this.brands.find((brand) => brand.is_default) || this.brands[0];
        this.activeBrandKey = this.brandKey((current || fallback || {}).id || "");
      } catch (err) {
        this.error =
          err.response?.data?.error || "Could not load product images.";
      } finally {
        this.isLoading = false;
      }
    },
    filesFromEvent(event) {
      if (!event) return [];
      if (Array.isArray(event.files)) return event.files;
      if (event.files && typeof event.files.length === "number") {
        return Array.from(event.files);
      }
      return [];
    },
    async onUpload(event, brand) {
      const files = this.filesFromEvent(event);
      if (!files.length || this.uploadLock) return;
      if (!this.productId) {
        this.stageFiles(brand, files);
        return;
      }
      if (!brand?.assignment_id) return;
      this.uploadLock = true;
      this.isUploading = brand.id;
      try {
        await Promise.all(
          files.map((file) => {
            const body = new FormData();
            body.append("image", file);
            body.append("product", this.productId);
            body.append("assignment", brand.assignment_id);
            return axios.post("/api/productimages/", body);
          })
        );
        await this.loadImages();
        this.$emit("changed");
        this.notifyToastSuccess?.("Images uploaded.");
      } catch (err) {
        const msg =
          err.response?.data?.error ||
          err.response?.data?.brand?.[0] ||
          "Could not upload images.";
        this.notifyToastError?.(msg);
      } finally {
        this.isUploading = null;
        this.uploadLock = false;
        this.uploadNonce += 1;
      }
    },
    async flushPending(productId) {
      if (!productId || !this.hasPending()) {
        return { uploaded: 0, failed: 0 };
      }
      this.isFlushing = true;
      this.uploadLock = true;
      let uploaded = 0;
      let failed = 0;
      try {
        const { data } = await axios.get(`/api/products/${productId}/images/`);
        const savedBrands = data.brands || [];
        const jobs = [];
        savedBrands.forEach((brand) => {
          const staged = this.getPendingForBrand(brand.id);
          staged.forEach((item, index) => {
            if (!item?.file || !brand.assignment_id) {
              failed += 1;
              return;
            }
            const body = new FormData();
            body.append("image", item.file);
            body.append("product", productId);
            body.append("assignment", brand.assignment_id);
            if (index === 0) body.append("is_primary", "true");
            jobs.push(
              axios
                .post("/api/productimages/", body)
                .then(() => {
                  uploaded += 1;
                })
                .catch(() => {
                  failed += 1;
                })
            );
          });
        });
        await Promise.all(jobs);
        return { uploaded, failed };
      } finally {
        this.clearPending(true);
        this.isFlushing = false;
        this.uploadLock = false;
      }
    },
    async setAsPrimary(image) {
      try {
        await axios.patch(`/api/productimages/${image.id}/`, {
          is_primary: true,
        });
        await this.loadImages();
        this.$emit("changed");
        this.notifyToastSuccess?.("Primary image updated.");
      } catch (err) {
        this.notifyToastError?.(
          err.response?.data?.error || "Could not set primary image."
        );
      }
    },
    askDelete(image) {
      if (!this.canDelete) return;
      this.pendingDelete = image;
      this.deleteVisible = true;
    },
    async confirmDelete() {
      const image = this.pendingDelete;
      this.deleteVisible = false;
      this.pendingDelete = null;
      if (!image || !this.canDelete) return;
      this.isDeleting = image.id;
      try {
        await axios.delete(`/api/productimages/${image.id}/`);
        await this.loadImages();
        this.$emit("changed");
        this.notifyToastSuccess?.("Image deleted.");
      } catch (err) {
        this.notifyToastError?.(
          err.response?.data?.error || "Could not delete image."
        );
      } finally {
        this.isDeleting = null;
      }
    },
    formatDate(value) {
      if (!value) return "";
      return new Date(value).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    },
  },
};
</script>

<style scoped>
.jr-brand-images__hint,
.jr-brand-images__status {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-brand-images__error {
  margin: 0;
  padding: 0.35rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-danger-text);
  background: var(--color-jr-danger-subtle);
}

.jr-brand-images__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem 1rem;
  margin-bottom: 0.75rem;
}

.jr-brand-images__default {
  margin-left: 0.35rem;
}

.jr-brand-images__count {
  margin-left: 0.35rem;
  color: var(--color-jr-muted, #4b5563);
  font-weight: 600;
}

.jr-brand-images__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(10.5rem, 1fr));
  gap: 0.75rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.jr-brand-images__item {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  min-width: 0;
}

.jr-brand-images__frame {
  position: relative;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface-muted, #f9fafb);
}

.jr-brand-images__frame :deep(.p-image) {
  width: 100%;
  height: 100%;
  display: block;
}

.jr-brand-images__frame :deep(.jr-brand-images__img),
.jr-brand-images__thumb .jr-brand-images__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 0;
}

.jr-brand-images__thumb {
  display: block;
  width: 100%;
  height: 100%;
  padding: 0;
  border: 0;
  background: none;
  cursor: pointer;
}

.jr-brand-images__thumb:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 2px;
}

.jr-brand-gallery.p-gallery {
  height: auto;
  overflow: visible;
  display: block;
}

.jr-brand-gallery.p-gallery:not([data-fullscreen]) :deep(.p-gallery-content),
.jr-brand-gallery.p-gallery:not([data-fullscreen]) :deep(.p-gallery-header),
.jr-brand-gallery.p-gallery:not([data-fullscreen]) :deep(.p-gallery-backdrop),
.jr-brand-gallery.p-gallery:not([data-fullscreen]) :deep(.p-gallery-next),
.jr-brand-gallery.p-gallery:not([data-fullscreen]) :deep(.p-gallery-prev) {
  display: none;
}

.jr-brand-gallery.p-gallery[data-fullscreen] {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.jr-brand-gallery.p-gallery[data-fullscreen] .jr-brand-images__grid {
  display: none;
}

.jr-brand-gallery :deep(.p-gallery-item img) {
  max-width: min(90vw, 56rem);
  max-height: 80vh;
  object-fit: contain;
}

.jr-brand-images__primary {
  position: absolute;
  top: 0.4rem;
  left: 0.4rem;
  z-index: 1;
}

.jr-brand-images__meta {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-brand-images__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.jr-brand-images :deep(.p-tablist-tab-list) {
  gap: 0.15rem;
}

.jr-brand-images :deep(.p-tab) {
  display: inline-flex;
  align-items: center;
  border-radius: 0;
}

.jr-brand-images :deep(.p-tabpanels) {
  padding: 0.85rem 0 0;
  background: transparent;
}

.jr-brand-images :deep(.p-fileupload-basic .p-button) {
  min-height: 2.25rem;
  border-radius: var(--radius-jr-control, 0);
}
</style>
