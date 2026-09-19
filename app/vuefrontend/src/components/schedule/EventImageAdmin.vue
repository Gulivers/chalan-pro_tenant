<template>
  <div class="jr-pilot jr-event-folder">
    <div
      v-if="hasPermission('appschedule.add_eventimage')"
      class="jr-event-folder__upload-card"
      :class="{ 'jr-event-folder__upload-card--dragging': isDragging }"
      @click="triggerFileInput"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop">
      <input
        id="imageUpload"
        ref="fileInput"
        type="file"
        class="jr-sr-only"
        multiple
        @change="handleImageUpload" />
      <div class="jr-event-folder__upload-content">
        <span class="jr-event-folder__upload-icon-wrap" aria-hidden="true">
          <UploadIcon />
        </span>
        <div class="jr-event-folder__upload-text">
          <span class="jr-event-folder__upload-title">
            <span class="jr-event-folder__upload-link">Choose files</span> or drag & drop here
          </span>
          <span class="jr-event-folder__upload-hint">
            Allowed: images (JPG, PNG, WebP), PDF, AutoCAD (DWG, DXF, DWF)
          </span>
        </div>
      </div>
    </div>

    <JREmptyState
      v-if="!images.length && !selectedImageUrl"
      title="No project files yet"
      description="Upload drawings, photos or PDFs for this schedule event." />

    <JRScrollArea
      v-show="!selectedImageUrl && images.length"
      class="jr-event-folder__scroll"
      height="var(--jr-wov-body-height, 22rem)">
      <div ref="galleryWrapper" class="jr-event-folder__gallery">
        <div class="jr-event-folder__grid">
          <div
            v-for="img in images"
            :key="img.id"
            class="jr-event-folder__box">
            <div class="jr-event-folder__tile">
              <template v-if="isAutoCAD(img.image_url)">
                <button
                  type="button"
                  class="jr-event-folder__thumb jr-event-folder__thumb--file"
                  :title="getFileName(img.image_url)"
                  @click="openAutoCADViewer(img.image_url)">
                  <img
                    :src="getFileIcon(img.image_url)"
                    alt=""
                    class="jr-event-folder__icon" />
                  <span class="jr-event-folder__name">
                    {{ getFileName(img.image_url) }}
                  </span>
                  <JRBadge
                    :value="getFileExt(img.image_url)"
                    severity="info"
                    class="jr-event-folder__badge" />
                </button>
                <button
                  type="button"
                  class="jr-event-folder__delete"
                  aria-label="Delete file"
                  title="Delete file"
                  @click.stop="deleteImage(img.id)">
                  <TrashIcon aria-hidden="true" />
                </button>
              </template>

              <template v-else-if="isDocument(img.image_url)">
                <button
                  type="button"
                  class="jr-event-folder__thumb jr-event-folder__thumb--file"
                  :title="`Click to open/download ${getFileName(img.image_url)}`"
                  @click.prevent="downloadDocument(img.image_url)">
                  <img
                    :src="getFileIcon(img.image_url)"
                    alt=""
                    class="jr-event-folder__icon" />
                  <span class="jr-event-folder__name">
                    {{ getFileName(img.image_url) }}
                  </span>
                  <JRBadge
                    value="PDF"
                    severity="secondary"
                    class="jr-event-folder__badge" />
                </button>
                <button
                  type="button"
                  class="jr-event-folder__delete"
                  aria-label="Delete file"
                  title="Delete file"
                  @click.stop="deleteImage(img.id)">
                  <TrashIcon aria-hidden="true" />
                </button>
              </template>

              <template
                v-else-if="
                  !img.image_url.match(/\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i)
                ">
                <div class="jr-event-folder__thumb jr-event-folder__thumb--file">
                  <img
                    :src="getFileIcon(img.image_url)"
                    alt=""
                    class="jr-event-folder__icon" />
                  <span class="jr-event-folder__name">
                    {{ getFileName(img.image_url) }}
                  </span>
                  <JRBadge
                    :value="getFileExt(img.image_url)"
                    severity="secondary"
                    class="jr-event-folder__badge" />
                </div>
                <button
                  type="button"
                  class="jr-event-folder__delete"
                  aria-label="Delete file"
                  title="Delete file"
                  @click.stop="deleteImage(img.id)">
                  <TrashIcon aria-hidden="true" />
                </button>
              </template>

              <template v-else>
                <button
                  type="button"
                  class="jr-event-folder__thumb jr-event-folder__thumb--image"
                  :aria-label="`View ${getFileName(img.image_url)}`"
                  @click="openImageViewer(img.image_url)">
                  <img :src="img.image_url" alt="" class="jr-event-folder__img" />
                </button>
                <button
                  type="button"
                  class="jr-event-folder__delete"
                  aria-label="Delete image"
                  title="Delete image"
                  @click.stop="deleteImage(img.id)">
                  <TrashIcon aria-hidden="true" />
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </JRScrollArea>

    <div
      v-if="selectedImageUrl"
      class="jr-event-folder__fullscreen"
      role="dialog"
      aria-modal="true"
      aria-label="Image preview"
      @click="closeImageViewer">
      <button
        type="button"
        class="jr-event-folder__close"
        aria-label="Close preview"
        @click.stop="closeImageViewer">
        ✕
      </button>
      <img :src="selectedImageUrl" alt="Selected" @click.stop />
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Swal from "sweetalert2";
import UploadIcon from "@primevue/icons/upload";
import TrashIcon from "@primevue/icons/trash";
import { JRBadge, JREmptyState, JRScrollArea } from "@ui";

export default {
  name: "EventImageAdmin",
  components: {
    JRBadge,
    JREmptyState,
    JRScrollArea,
    TrashIcon,
    UploadIcon,
  },
  props: {
    eventId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      images: [],
      selectedImageUrl: null,
      isDragging: false,
    };
  },
  watch: {
    eventId: {
      immediate: true,
      handler(newVal) {
        if (newVal) this.fetchImages();
      },
    },
  },
  methods: {
    async fetchImages() {
      try {
        const response = await axios.get(
          `/api/event-images/?event=${this.eventId}`
        );
        this.images = response.data;
      } catch (error) {
        console.error("[❌] Error fetching event images:", error);
      }
    },
    triggerFileInput() {
      this.$refs.fileInput?.click();
    },
    onDrop(event) {
      this.isDragging = false;
      const files = event.dataTransfer?.files;
      if (files?.length) {
        this.processFiles(files);
      }
    },
    getFileExt(fileUrl) {
      if (!fileUrl || typeof fileUrl !== "string") return "";
      return fileUrl.split(".").pop().toUpperCase();
    },
    async handleImageUpload(event) {
      const files = event.target.files;
      await this.processFiles(files);
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = "";
      }
    },
    async processFiles(files) {
      if (!files || !files.length) return;
      const allowedExt = [
        "dwg",
        "dxf",
        "dwf",
        "dwt",
        "pdf",
        "jpg",
        "jpeg",
        "png",
        "webp",
        "bmp",
      ];
      const invalidFiles = [];
      const validFiles = [];

      for (let file of files) {
        const ext = file.name.split(".").pop().toLowerCase();
        if (allowedExt.includes(ext)) {
          validFiles.push(file);
        } else {
          invalidFiles.push(file.name);
        }
      }

      if (invalidFiles.length) {
        console.warn("[🔒 BLOCKED FILES]", invalidFiles);
        this.notifyWarning?.(
          `File type not allowed: ${invalidFiles.join(", ")}`
        );
        return;
      }
      if (!validFiles.length) return;

      const formData = new FormData();
      formData.append("event_id", this.eventId);
      for (let i = 0; i < validFiles.length; i++) {
        formData.append("images", validFiles[i]);
      }

      try {
        const response = await axios.post(
          `/api/event-images/upload/`,
          formData,
          {
            headers: { "Content-Type": "multipart/form-data" },
          }
        );
        this.images = response.data || [];
        await this.fetchImages();
        this.$nextTick(() => {
          const gallery = this.$refs.galleryWrapper;
          if (gallery) {
            gallery.scrollTop = 0;
          }
        });
        Swal.fire({
          icon: "success",
          toast: true,
          title: "Images uploaded",
          showConfirmButton: false,
          timer: 1500,
        });
      } catch (error) {
        console.error("[❌] Error uploading images:", error);
        Swal.fire("Oops!", "Error uploading image(s).", "error");
      }
    },
    async deleteImage(imageId) {
      const confirm = await Swal.fire({
        title: "Are you sure?",
        text: "This image will be deleted permanently.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes, delete it!",
        cancelButtonText: "Cancel",
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
      });

      if (confirm.isConfirmed) {
        try {
          await axios.delete(`/api/event-images/${imageId}/`);
          this.images = this.images.filter((img) => img.id !== imageId);
          this.notifyToastSuccess("Message has been deleted successfully");
        } catch (err) {
          Swal.fire(
            "Oops!",
            "There was a problem deleting the image.",
            "error"
          );
        }
      }
    },
    openImageViewer(url) {
      this.selectedImageUrl = url;
    },
    closeImageViewer() {
      this.selectedImageUrl = null;
    },
    isAutoCAD(fileUrl) {
      const ext = fileUrl.split(".").pop().toLowerCase();
      return ["dwg", "dxf", "dwf", "dwt"].includes(ext);
    },
    isDocument(fileUrl) {
      if (!fileUrl || typeof fileUrl !== "string") return false;
      const ext = fileUrl.split(".").pop().toLowerCase();
      return ["pdf"].includes(ext);
    },
    getFileIcon(fileUrl) {
      if (!fileUrl || typeof fileUrl !== "string")
        return require("@/assets/img/file-generic.svg");
      const ext = fileUrl.split(".").pop().toLowerCase();
      switch (ext) {
        case "pdf":
          return require("@/assets/img/document-pdf.svg");
        case "dwg":
        case "dxf":
        case "dwf":
        case "dwt":
          return require("@/assets/img/file-autocad.svg");
        default:
          return require("@/assets/img/file-generic.svg");
      }
    },
    getFileName(fileUrl) {
      return fileUrl.split("/").pop();
    },
    openAutoCADViewer(fileUrl) {
      const encodedUrl = encodeURIComponent(fileUrl);
      const viewerUrl = `https://viewer.autodesk.com/?url=${encodedUrl}`;
      window.open(viewerUrl, "_blank");
    },
    async downloadDocument(fileUrl) {
      window.open(fileUrl, "_blank");
    },
    showDeleteBtn(fileUrl) {
      const ext = fileUrl.split(".").pop().toLowerCase();
      return (
        ["pdf", "dwg", "dxf", "dwf", "dwt"].includes(ext) ||
        this.isImageFile(fileUrl)
      );
    },
  },
};
</script>

<style scoped>
.jr-event-folder {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 0;
  height: 100%;
}

.jr-event-folder :deep(.jr-empty-state) {
  min-height: var(--jr-wov-body-height, 22rem);
  display: flex;
  align-items: center;
  justify-content: center;
}

.jr-event-folder__upload-card {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem 1.25rem;
  border: 1px dashed var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-control, 0);
  background: var(--color-jr-surface-muted, #f9fafb);
  cursor: pointer;
  transition: border-color 0.15s ease, background-color 0.15s ease;
}

.jr-event-folder__upload-card:hover,
.jr-event-folder__upload-card--dragging {
  border-color: var(--color-jr-primary, #2563eb);
  background: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 4%,
    var(--color-jr-surface-muted, #f9fafb)
  );
}

.jr-event-folder__upload-content {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  text-align: left;
}

.jr-event-folder__upload-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: var(--radius-jr-control, 0);
  background: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 12%,
    var(--color-jr-surface, #fff)
  );
  color: var(--color-jr-primary, #2563eb);
  flex-shrink: 0;
}

.jr-event-folder__upload-text {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.jr-event-folder__upload-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-jr-text, #111827);
}

.jr-event-folder__upload-link {
  color: var(--color-jr-primary, #2563eb);
  font-weight: 600;
  text-decoration: underline;
}

.jr-event-folder__upload-hint {
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-event-folder__gallery {
  max-height: none;
  overflow: visible;
  display: flex;
  flex-direction: column-reverse;
  padding: 0.25rem;
  border: none;
  background: transparent;
}

.jr-event-folder__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
  padding: 0.75rem;
}

.jr-event-folder__tile {
  position: relative;
}

.jr-event-folder__thumb {
  display: flex;
  width: 100%;
  margin: 0;
  padding: 0;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-control, 0);
  background: var(--color-jr-surface-muted, #f9fafb);
  cursor: pointer;
  text-align: center;
  overflow: hidden;
  transition: border-color 0.15s ease, background-color 0.15s ease;
}

.jr-event-folder__thumb:hover {
  border-color: var(--color-jr-hover-border, #d1d5db);
  background: var(--color-jr-surface, #fff);
}

.jr-event-folder__thumb:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 1px;
}

.jr-event-folder__thumb--file {
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 8.5rem;
  padding: 0.875rem 0.5rem 0.625rem;
  gap: 0.5rem;
}

.jr-event-folder__thumb--image {
  aspect-ratio: 4 / 3;
}

.jr-event-folder__img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
}

.jr-event-folder__icon {
  width: 2.75rem;
  height: 2.75rem;
}

.jr-event-folder__name {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-jr-text, #111827);
  word-break: break-all;
  max-width: 90%;
  line-height: 1.3;
}

.jr-event-folder__badge {
  pointer-events: none;
}

.jr-event-folder__delete {
  position: absolute;
  top: 0.35rem;
  right: 0.35rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  padding: 0;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-control, 0);
  background: var(--color-jr-surface, #fff);
  color: var(--color-jr-danger-text, #991b1b);
  opacity: 0;
  transition: opacity 0.15s ease, background-color 0.15s ease, border-color 0.15s ease;
  z-index: 2;
  cursor: pointer;
}

.jr-event-folder__delete:hover {
  background: var(--color-jr-danger-subtle, #fee2e2);
  border-color: var(--color-jr-danger, #dc2626);
}

.jr-event-folder__tile:hover .jr-event-folder__delete,
.jr-event-folder__tile:focus-within .jr-event-folder__delete {
  opacity: 1;
}

.jr-event-folder__fullscreen {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  background: color-mix(
    in srgb,
    var(--color-jr-text, #111827) 90%,
    transparent
  );
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  cursor: zoom-out;
}

.jr-event-folder__close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  background: color-mix(
    in srgb,
    var(--color-jr-surface, #fff) 20%,
    transparent
  );
  color: var(--color-jr-surface, #fff);
  border: 1px solid color-mix(
    in srgb,
    var(--color-jr-surface, #fff) 30%,
    transparent
  );
  border-radius: var(--radius-jr-control, 0);
  font-size: 0.9375rem;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.jr-event-folder__close:hover {
  background: color-mix(
    in srgb,
    var(--color-jr-surface, #fff) 35%,
    transparent
  );
}

.jr-event-folder__fullscreen img {
  max-width: 90%;
  max-height: 90%;
  border-radius: var(--radius-jr-control, 0);
}

@media (min-width: 768px) {
  .jr-event-folder__grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
