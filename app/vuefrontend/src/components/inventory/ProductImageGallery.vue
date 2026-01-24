<template>
  <div
    class="modal fade"
    id="productImageGalleryModal"
    tabindex="-1"
    aria-labelledby="productImageGalleryModalLabel"
    aria-hidden="true"
    ref="modal">
    <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="productImageGalleryModalLabel">
            <span v-if="productInfo">
              📷 Images of: {{ productInfo.name }}
              <small class="text-muted">({{ productInfo.sku }})</small>
            </span>
            <span v-else>Loading...</span>
          </h5>
          <button 
            type="button" 
            class="btn-close" 
            @click="closeModal"
            v-tt
            data-title="Close gallery"></button>
        </div>

        <div class="modal-body p-0">
          <div v-if="isLoading" class="text-center p-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted">Loading product images...</p>
          </div>

          <div v-else-if="error" class="alert alert-danger m-3" role="alert">
            <strong>Error:</strong> {{ error }}
          </div>

          <div v-else-if="brands.length === 0" class="text-center p-5">
            <p class="text-muted">No images found. This product has no associated brands.</p>
          </div>

          <div v-else class="card border-0">
            <!-- Tabs por marca -->
            <BNav tabs class="card-header-tabs">
              <BNavItem
                v-for="brand in brands"
                :key="brand.id"
                :active="activeBrandId === brand.id"
                @click="activeBrandId = brand.id">
                {{ brand.name }}
                <span v-if="getImagesCount(brand.id) > 0" class="badge bg-secondary ms-2">
                  {{ getImagesCount(brand.id) }}
                </span>
              </BNavItem>
            </BNav>

            <!-- Contenido de cada tab -->
            <div class="card-body">
              <div v-for="brand in brands" :key="brand.id" v-show="activeBrandId === brand.id" class="tab-content-item">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h6 class="mb-0">
                    Images for brand: <strong>{{ brand.name }}</strong>
                  </h6>
                  <div>
                    <label 
                      class="btn btn-primary btn-sm"
                      v-tt
                      data-title="Select and upload new images for this brand">
                      <input
                        type="file"
                        @change="handleFileSelect(brand, $event)"
                        accept="image/*"
                        multiple
                        style="display: none" />
                      📤 Upload Images
                    </label>
                  </div>
                </div>

                <!-- Galería de imágenes -->
                <div v-if="getImagesForBrand(brand.id).length === 0" class="text-center p-5 border rounded bg-light">
                  <p class="text-muted mb-3">No images found for this brand.</p>
                  <label 
                    class="btn btn-outline-primary"
                    v-tt
                    data-title="Click to select the first image for this brand">
                    <input
                      type="file"
                      @change="handleFileSelect(brand, $event)"
                      accept="image/*"
                      multiple
                      style="display: none" />
                    📤 Upload First Image
                  </label>
                </div>

                <div v-else class="gallery-grid">
                  <div
                    v-for="image in getImagesForBrand(brand.id)"
                    :key="image.id"
                    class="image-box">
                    <div class="position-relative">
                      <img
                        :src="image.image_url"
                        :alt="image.description || `Image ${image.id}`"
                        class="img-thumbnail"
                        @click="openImageModal(image)"
                        v-tt
                        data-title="Click to enlarge image" />
                      
                      <span
                        v-if="image.is_primary"
                        class="badge bg-success position-absolute top-0 start-0 m-2"
                        style="z-index: 4;">
                        Primary
                      </span>

                      <button
                        type="button"
                        class="btn delete-btn"
                        @click.stop="deleteImage(image.id)"
                        :disabled="isDeleting === image.id"
                        v-tt
                        data-title="Delete this image">
                        <span v-if="isDeleting === image.id" class="spinner-border spinner-border-sm text-white"></span>
                      </button>

                      <div class="image-actions p-2">
                        <div class="d-flex justify-content-between align-items-center">
                          <small class="text-white-50 shadow-text">
                            {{ formatDate(image.uploaded_at) }}
                          </small>
                          <button
                            v-if="!image.is_primary"
                            class="btn btn-xs btn-primary py-0 px-1"
                            @click="setAsPrimary(image.id)"
                            v-tt
                            data-title="Set as primary image for this brand"
                            style="font-size: 0.65rem;">
                            Set Primary
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Indicador de carga al subir -->
                <div v-if="isUploading === brand.id" class="text-center mt-3">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Uploading...</span>
                  </div>
                  <p class="mt-2 text-muted">Uploading images...</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button 
            type="button" 
            class="btn btn-secondary" 
            @click="closeModal"
            v-tt
            data-title="Close this window">Close</button>
        </div>
      </div>
    </div>

    <!-- Modal para vista ampliada de imagen -->
    <div
      class="modal fade"
      id="imageViewerModal"
      tabindex="-1"
      aria-hidden="true"
      ref="imageViewerModal">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content border-0 bg-transparent">
          <div class="modal-header border-0 p-0 position-absolute top-0 end-0" style="z-index: 1051;">
            <button type="button" class="btn-close btn-close-white m-3" @click="closeImageModal" aria-label="Close"></button>
          </div>
          <div class="modal-body text-center p-0">
            <img
              v-if="selectedImage"
              :src="selectedImage.image_url"
              :alt="selectedImage.description || 'Image'"
              class="img-fluid rounded shadow-lg"
              style="max-height: 85vh; cursor: zoom-out;"
              @click="closeImageModal" />
            <div v-if="selectedImage?.description" class="p-3 text-white">
              {{ selectedImage.description }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as bootstrap from 'bootstrap';
import { BNav, BNavItem } from 'bootstrap-vue-next';
import axios from 'axios';

export default {
  name: 'ProductImageGallery',
  components: {
    BNav,
    BNavItem,
  },
  props: {
    productId: {
      type: [Number, String],
      required: true,
    },
  },
  data() {
    return {
      isLoading: false,
      error: null,
      productInfo: null,
      brands: [],
      imagesByBrand: {},
      activeBrandId: null,
      isUploading: null,
      isDeleting: null,
      selectedImage: null,
      imageViewerModalInstance: null,
    };
  },
  watch: {
    productId: {
      immediate: true,
      handler(newId) {
        console.log('👀 ProductImageGallery - productId changed to:', newId);
        if (newId) {
          console.log('📥 Loading images for product ID:', newId);
          this.loadImages();
        } else {
          console.warn('⚠️ ProductImageGallery - productId is null or undefined');
        }
      },
    },
  },
  methods: {
    async loadImages() {
      if (!this.productId) {
        console.warn('⚠️ loadImages called without productId');
        return;
      }

      console.log('🔄 loadImages started for product ID:', this.productId);
      console.log('🌐 API URL:', `/api/products/${this.productId}/images/`);
      
      this.isLoading = true;
      this.error = null;

      try {
        const response = await axios.get(`/api/products/${this.productId}/images/`);
        console.log('✅ API response received:', response.data);
        
        const data = response.data;

        this.productInfo = {
          id: data.product_id,
          name: data.product_name,
          sku: data.product_sku,
        };
        console.log('📦 ProductInfo updated:', this.productInfo);

        this.brands = data.brands || [];
        this.imagesByBrand = data.images_by_brand || {};
        console.log('🏷️ Brands found:', this.brands.length);
        console.log('🖼️ Images by brand:', Object.keys(this.imagesByBrand).length, 'brands with images');

        // Set the first brand (or default) as active
        if (this.brands.length > 0) {
          const defaultBrand = this.brands.find(b => b.is_default) || this.brands[0];
          this.activeBrandId = defaultBrand.id;
          console.log('✅ Active brand set:', defaultBrand.name, '(ID:', defaultBrand.id, ')');
        } else {
          console.warn('⚠️ No brands found for product');
        }
      } catch (error) {
        console.error('❌ Error loading images:', error);
        this.error = error.response?.data?.error || 'Error loading product images.';
      } finally {
        this.isLoading = false;
        console.log('🏁 loadImages finished');
      }
    },

    getImagesForBrand(brandId) {
      return this.imagesByBrand[brandId] || [];
    },

    getImagesCount(brandId) {
      return this.getImagesForBrand(brandId).length;
    },

    async handleFileSelect(brand, event) {
      const brandId = brand.id;
      const assignmentId = brand.assignment_id;
      
      const input = event?.target || (Array.isArray(this.$refs.fileInput) ? this.$refs.fileInput[0] : this.$refs.fileInput);
      if (!input || !input.files || input.files.length === 0) {
        console.warn('⚠️ No files selected');
        return;
      }
      
      console.log('📤 handleFileSelect called for brandId:', brandId, 'assignmentId:', assignmentId);
      console.log('📁 Files selected:', input.files.length);

      this.isUploading = brandId;

      try {
        const uploadPromises = Array.from(input.files).map(file => {
          const singleFormData = new FormData();
          singleFormData.append('image', file);
          singleFormData.append('product', this.productId);
          singleFormData.append('assignment', assignmentId);

          return axios.post('/api/productimages/', singleFormData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
        });

        await Promise.all(uploadPromises);
        await this.loadImages();

        if (this.$parent?.notifyToastSuccess) {
          this.$parent.notifyToastSuccess('Images uploaded successfully.');
        }
      } catch (error) {
        console.error('Error uploading images:', error);
        const errorMsg = error.response?.data?.error || error.response?.data?.brand?.[0] || 'Error uploading images.';
        if (this.$parent?.notifyError) {
          this.$parent.notifyError(errorMsg);
        }
      } finally {
        this.isUploading = null;
        if (input) input.value = '';
      }
    },

    async deleteImage(imageId) {
      this.confirmDelete(
        'Are you sure?',
        'Are you sure you want to delete this image?',
        async () => {
          this.isDeleting = imageId;
          try {
            await axios.delete(`/api/productimages/${imageId}/`);
            await this.loadImages();

            if (this.notifyToastSuccess) {
              this.notifyToastSuccess('Image deleted successfully.');
            }
          } catch (error) {
            console.error('Error deleting image:', error);
            const errorMsg = error.response?.data?.error || 'Error deleting image.';
            if (this.notifyError) {
              this.notifyError(errorMsg);
            }
          } finally {
            this.isDeleting = null;
          }
        }
      );
    },

    async setAsPrimary(imageId) {
      try {
        await axios.patch(`/api/productimages/${imageId}/`, {
          is_primary: true,
        });

        await this.loadImages();

        if (this.$parent?.notifyToastSuccess) {
          this.$parent.notifyToastSuccess('Image set as primary.');
        }
      } catch (error) {
        console.error('Error setting primary image:', error);
        const errorMsg = error.response?.data?.error || 'Error setting image as primary.';
        if (this.$parent?.notifyError) {
          this.$parent.notifyError(errorMsg);
        }
      }
    },

    findImageById(imageId) {
      for (const brandId in this.imagesByBrand) {
        const image = this.imagesByBrand[brandId].find(img => img.id === imageId);
        if (image) return image;
      }
      return null;
    },

    openImageModal(image) {
      this.selectedImage = image;
      this.$nextTick(() => {
        if (!this.imageViewerModalInstance) {
          const modalEl = this.$refs.imageViewerModal;
          if (modalEl) {
            this.imageViewerModalInstance = new bootstrap.Modal(modalEl);
          }
        }
        this.imageViewerModalInstance?.show();
      });
    },

    closeImageModal() {
      if (this.imageViewerModalInstance) {
        this.imageViewerModalInstance.hide();
      }
      this.selectedImage = null;
    },

    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    },

    openModal() {
      const modalEl = this.$refs.modal;
      if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
        this.loadImages();
      }
    },

    closeModal() {
      const modalEl = this.$refs.modal;
      if (modalEl) {
        const modal = bootstrap.Modal.getInstance(modalEl);
        modal?.hide();
      }
      this.closeImageModal();
    },
  },
};
</script>

<style scoped>
.card {
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.card-header-tabs {
  border-bottom: 2px solid #dee2e6;
  background-color: #f8f9fa;
  padding: 0;
}

.card-body {
  min-height: 400px;
  padding: 1.5rem;
  background-color: #fff;
}

/* Estilos de galería inspirados en EventImageAdmin */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.image-box {
  width: 100%;
}

img.img-thumbnail {
  border-radius: 8px;
  object-fit: cover;
  width: 100%;
  height: auto;
  aspect-ratio: 4 / 3;
  object-position: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease-in-out;
  cursor: pointer;
}

img.img-thumbnail:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  transform: translateY(-2px);
}

.delete-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 26px;
  height: 26px;
  background-image: url('@/assets/img/inline-delete.svg');
  background-size: cover;
  background-color: rgba(228, 14, 14, 0.85);
  border: none;
  opacity: 0;
  transition: opacity 0.2s ease-in-out;
  z-index: 5;
  border-radius: 4px;
}

.position-relative:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  transform: scale(1.1);
  background-color: #f00;
}

.image-actions {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.position-relative:hover .image-actions {
  opacity: 1;
}

.shadow-text {
  text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
}

.tab-content-item {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Estilos para BNav tabs */
:deep(.nav-tabs) {
  border-bottom: 2px solid #dee2e6;
  margin-bottom: 0;
}

:deep(.nav-item .nav-link) {
  color: #495057;
  border: none;
  border-bottom: 3px solid transparent;
  padding: 0.50rem 1rem;
  transition: all 0.2s ease;
  background-color: transparent;
  cursor: pointer;
}

:deep(.nav-item .nav-link.active) {
  color: #0d6efd;
  background-color: transparent;
  border-bottom-color: #0d6efd;
  font-weight: 600;
}

.modal-xl {
  max-width: 1200px;
}
</style>
