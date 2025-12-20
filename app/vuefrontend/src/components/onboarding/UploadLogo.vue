<template>
  <div class="logo-upload-container mb-4">
    <label class="form-label fw-semibold mb-3 d-block">
      Company Logo
      <span class="text-muted small ms-1">(Optional)</span>
    </label>
    
    <div class="logo-upload-area" :class="{ 'has-preview': preview }">
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        class="d-none"
        @change="handleFileChange"
        aria-label="Upload company logo"
      />
      
      <div v-if="!preview" class="upload-placeholder" @click="triggerFileInput">
        <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
        <p class="mb-0 text-muted">Click to upload logo</p>
        <small class="text-muted">PNG, JPG, GIF (max. 5MB)</small>
      </div>
      
      <div v-else class="preview-container">
        <img :src="preview" alt="Logo preview" class="preview-image" />
        <button
          type="button"
          class="btn btn-sm btn-danger remove-btn"
          @click="removeLogo"
          aria-label="Remove logo"
        >
          <i class="fas fa-times"></i>
        </button>
        <button
          type="button"
          class="btn btn-sm btn-outline-primary change-btn"
          @click="triggerFileInput"
          aria-label="Change logo"
        >
          <i class="fas fa-edit me-1"></i>
          Change
        </button>
      </div>
    </div>
    
    <div v-if="error" class="text-danger small mt-2">
      <i class="fas fa-exclamation-circle me-1"></i>
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: File,
    default: null
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const fileInput = ref(null)
const preview = ref(null)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  
  if (!file) {
    return
  }
  
  // Validate file size (5MB max)
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    emit('update:modelValue', null)
    preview.value = null
    return
  }
  
  // Validate file type
  const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif']
  if (!allowedTypes.includes(file.type)) {
    emit('update:modelValue', null)
    preview.value = null
    return
  }
  
  // Create preview
  const reader = new FileReader()
  reader.onload = (e) => {
    preview.value = e.target.result
  }
  reader.readAsDataURL(file)
  
  emit('update:modelValue', file)
}

const removeLogo = () => {
  emit('update:modelValue', null)
  preview.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  if (!newValue && preview.value) {
    preview.value = null
  }
})
</script>

<style scoped>
.logo-upload-container {
  width: 100%;
}

.logo-upload-area {
  border: 2px dashed var(--bs-border-color);
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  background-color: var(--bs-light);
  transition: all 0.3s ease;
  cursor: pointer;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-upload-area:hover {
  border-color: var(--bs-primary);
  background-color: rgba(var(--bs-primary-rgb), 0.05);
}

.logo-upload-area.has-preview {
  border-style: solid;
  border-color: var(--bs-primary);
  background-color: white;
  padding: 1rem;
}

.upload-placeholder {
  width: 100%;
}

.preview-container {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.preview-image {
  max-width: 200px;
  max-height: 200px;
  object-fit: contain;
  border-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.remove-btn,
.change-btn {
  position: relative;
  z-index: 1;
}

.remove-btn {
  position: absolute;
  top: 0;
  right: 0;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

