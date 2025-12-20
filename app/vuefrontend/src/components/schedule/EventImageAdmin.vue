<template>
  <div class="event-image-gallery py-2">
    <div class="mb-3" v-if="hasPermission('appschedule.add_eventimage')">
      <label for="imageUpload" class="form-label fw-bold">Upload Project Files</label>
      <input type="file" class="form-control" id="imageUpload" multiple @change="handleImageUpload" ref="fileInput" />
    </div>

    <!-- Galería de miniaturas -->
    <div class="gallery-wrapper" v-show="!selectedImageUrl" ref="galleryWrapper">
      <div class="gallery-grid">
        <div class="image-box" v-for="img in images" :key="img.id">
          <div class="position-relative">
            <!-- AutoCAD Files -->
            <template v-if="isAutoCAD(img.image_url)">
              <div class="non-image-thumbnail" @click="openAutoCADViewer(img.image_url)">
                <img :src="getFileIcon(img.image_url)" alt="AutoCAD File" class="file-icon" />
                <small class="filename">{{ getFileName(img.image_url) }}</small>
              </div>
              <button
                type="button"
                class="btn delete-btn"
                @click.stop="deleteImage(img.id)"
                title="Delete file"></button>
            </template>

            <!-- Known Document Files -->
            <template v-else-if="isDocument(img.image_url)">
              <div
                class="non-image-thumbnail"
                @click.prevent="downloadDocument(img.image_url)"
                title="Click to open/download">
                <img :src="getFileIcon(img.image_url)" alt="File icon" class="file-icon" />
                <small class="filename">{{ getFileName(img.image_url) }}</small>
              </div>
              <button
                type="button"
                class="btn delete-btn"
                @click.stop="deleteImage(img.id)"
                title="Delete file"></button>
            </template>

            <!-- Unknown File Types -->
            <template v-else-if="!img.image_url.match(/\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i)">
              <div class="non-image-thumbnail">
                <img :src="getFileIcon(img.image_url)" alt="Other File" class="file-icon" />
                <small class="filename">{{ getFileName(img.image_url) }}</small>
              </div>
              <button
                type="button"
                class="btn delete-btn"
                @click.stop="deleteImage(img.id)"
                title="Delete file"></button>
            </template>

            <!-- Images -->
            <template v-else>
              <img :src="img.image_url" class="img-thumbnail" alt="Image" @click="openImageViewer(img.image_url)" />
              <button
                type="button"
                class="btn delete-btn"
                @click.stop="deleteImage(img.id)"
                title="Delete image"></button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Imagen en pantalla completa -->
    <div v-if="selectedImageUrl" class="fullscreen-image-viewer" @click="closeImageViewer">
      <img :src="selectedImageUrl" alt="Selected" />
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import Swal from 'sweetalert2';

  export default {
    name: 'EventImageAdmin',
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
          const response = await axios.get(`/api/event-images/?event=${this.eventId}`);
          this.images = response.data;
        } catch (error) {
          console.error('[❌] Error fetching event images:', error);
        }
      },
      async handleImageUpload(event) {
        const allowedExt = [
          'dwg',
          'dxf',
          'dwf',
          'dwt',
          'pdf',
          'jpg',
          'jpeg',
          'png',
          'webp',
          'bmp',
        ];
        const files = event.target.files;
        const invalidFiles = [];
        const validFiles = [];

        for (let file of files) {
          const ext = file.name.split('.').pop().toLowerCase();
          if (allowedExt.includes(ext)) {
            validFiles.push(file);
          } else {
            invalidFiles.push(file.name);
          }
        }

        if (invalidFiles.length) {
          console.warn('[🔒 BLOCKED FILES]', invalidFiles);
          this.notifyWarning(`File type not allowed: ${invalidFiles.join(', ')}`);
          event.target.value = ''; // limpiar input
          return;
        }
        if (!files.length) return;

        const formData = new FormData();
        formData.append('event_id', this.eventId);
        for (let i = 0; i < files.length; i++) {
          formData.append('images', files[i]);
        }

        try {
          const response = await axios.post(`/api/event-images/upload/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });
          this.images = response.data || [];
          await this.fetchImages();
          this.$nextTick(() => {
            const gallery = this.$refs.galleryWrapper;
            if (gallery) {
              gallery.scrollTop = 0; // Hace scroll hacia arriba para mostrar la nueva imagen
            }
            if (this.$refs.fileInput) {
              this.$refs.fileInput.value = ''; // Limpia el input para permitir re-carga
            }
          });
          Swal.fire({ icon: 'success', toast: true, title: 'Images uploaded', showConfirmButton: false, timer: 1500 });
        } catch (error) {
          console.error('[❌] Error uploading images:', error);
          Swal.fire('Oops!', 'Error uploading image(s).', 'error');
        }
      },
      async deleteImage(imageId) {
        const confirm = await Swal.fire({
          title: 'Are you sure?',
          text: 'This image will be deleted permanently.',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Yes, delete it!',
          cancelButtonText: 'Cancel',
          confirmButtonColor: '#d33',
          cancelButtonColor: '#3085d6',
        });

        if (confirm.isConfirmed) {
          try {
            await axios.delete(`/api/event-images/${imageId}/`);
            this.images = this.images.filter(img => img.id !== imageId);
            this.notifyToastSuccess('Message has been deleted successfully');
          } catch (err) {
            Swal.fire('Oops!', 'There was a problem deleting the image.', 'error');
          }
        }
      },
      openImageViewer(url) {
        this.selectedImageUrl = url;
      },
      closeImageViewer() {
        this.selectedImageUrl = null;
      },
      // Función para identificar archivos AutoCAD
      isAutoCAD(fileUrl) {
        const ext = fileUrl.split('.').pop().toLowerCase();
        return ['dwg', 'dxf', 'dwf', 'dwt'].includes(ext);
      },
      isDocument(fileUrl) {
        if (!fileUrl || typeof fileUrl !== 'string') return false;
        const ext = fileUrl.split('.').pop().toLowerCase();
        return ['pdf'].includes(ext);
      },
      getFileIcon(fileUrl) {
        if (!fileUrl || typeof fileUrl !== 'string') return require('@/assets/img/file-generic.svg');
        const ext = fileUrl.split('.').pop().toLowerCase();
        switch (ext) {
          case 'pdf':
            return require('@/assets/img/document-pdf.svg');
          case 'dwg':
          case 'dxf':
          case 'dwf':
          case 'dwt':
            return require('@/assets/img/file-autocad.svg');
          default:
            return require('@/assets/img/file-generic.svg');
        }
      },
      getFileName(fileUrl) {
        return fileUrl.split('/').pop();
      },
      // Función para abrir archivos AutoCAD en Autodesk Viewer
      openAutoCADViewer(fileUrl) {
        const encodedUrl = encodeURIComponent(fileUrl);
        const viewerUrl = `https://viewer.autodesk.com/?url=${encodedUrl}`;
        window.open(viewerUrl, '_blank');
      },
      async downloadDocument(fileUrl) {
        const ext = fileUrl.split('.').pop().toLowerCase();
        if (ext === 'pdf') {
          window.open(fileUrl, '_blank');
        } else {
          window.open(fileUrl, '_blank'); // fallback por si se coló algo
        }
      },
      // Mostrar botón eliminar también para archivos no imagen
      showDeleteBtn(fileUrl) {
        const ext = fileUrl.split('.').pop().toLowerCase();
        return (
          ['pdf', 'dwg', 'dxf', 'dwf', 'dwt'].includes(ext) ||
          this.isImageFile(fileUrl)
        );
      },
    },
  };
</script>

<style scoped>
  .event-image-gallery {
    background-color: #f9f9f9;
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
  }

  .gallery-wrapper {
    max-height: 60vh;
    overflow-y: auto;
    display: flex;
    flex-direction: column-reverse;
    scrollbar-width: thin;
    scrollbar-color: #999 #eee;
  }

  .gallery-wrapper::-webkit-scrollbar {
    width: 16px;
  }
  .gallery-wrapper::-webkit-scrollbar-thumb {
    background-color: #888;
    border-radius: 6px;
  }
  .gallery-wrapper::-webkit-scrollbar-track {
    background-color: #eee;
  }

  .gallery-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .gallery-grid .image-box {
    width: 100%;
  }

  .gallery-grid img.img-thumbnail {
    border-radius: 8px;
    object-fit: cover;
    width: 100%;
    height: auto;
    aspect-ratio: 4 / 3;
    object-position: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    transition: box-shadow 0.3s ease-in-out;
  }

  .gallery-grid img.img-thumbnail:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  }

  .delete-btn {
    position: absolute;
    top: 6px;
    right: 6px;
    width: 26px;
    height: 26px;
    background-image: url('@/assets/img/inline-delete.svg');
    background-size: cover;
    background-color: rgba(228, 14, 14, 0.753);
    border: none;
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
    z-index: 5;
  }
  .position-relative:hover .delete-btn {
    opacity: 1;
    cursor: pointer;
  }
  .delete-btn:hover {
    transform: scale(1.1);
  }

  .fullscreen-image-viewer {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.95);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2000;
  }

  .fullscreen-image-viewer img {
    max-width: 90%;
    max-height: 90%;
    border-radius: 12px;
    cursor: zoom-out;
    box-shadow: 0 4px 12px rgba(255, 255, 255, 0.5);
  }
  .non-image-thumbnail {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    background-color: #f0f0f0;
    border-radius: 8px;
    cursor: pointer;
    padding: 1rem;
    border: 1px solid #ddd;
    text-align: center;
  }

  .non-image-thumbnail:hover {
    background-color: #e6e6e6;
  }

  .file-icon {
    width: 48px;
    height: 48px;
    margin-bottom: 0.5rem;
  }

  .filename {
    font-size: 0.75rem;
    word-break: break-all;
    color: #555;
  }
  .non-image-thumbnail {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background-color: #f4f4f4;
    border-radius: 8px;
    border: 1px solid #ccc;
    height: 100%;
    text-align: center;
    cursor: pointer;
  }

  .non-image-thumbnail:hover {
    background-color: #eaeaea;
  }

  .file-icon {
    width: 48px;
    height: 48px;
    margin-bottom: 0.5rem;
  }

  .filename {
    font-size: 0.75rem;
    color: #555;
    word-break: break-all;
  }
</style>
