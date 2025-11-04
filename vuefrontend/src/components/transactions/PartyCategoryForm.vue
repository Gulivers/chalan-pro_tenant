<template>
  <div class="container mt-3">
        <!-- Main Title -->
        <div class="text-center">
      <h3 class="text-warning">Party Category</h3>
    </div>
    <div class="card shadow-sm mx-auto" style="max-width: 720px">
      <div class="card-header d-flex justify-content-center align-items-center">
        <h6 class="mb-0 w-100 text-center text-primary">
          {{ isViewMode ? 'View Party Category' : isEditMode ? 'Edit Party Category' : 'New Party Category' }}
        </h6>
      </div>

      <div class="card-body text-start">
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="mb-3">
            <label class="form-label mb-2">
              Name
              <span class="text-danger">*</span>
            </label>
            <input
              type="text"
              class="form-control"
              v-model.trim="form.name"
              :maxlength="150"
              :disabled="isViewMode || submitting"
              required />
          </div>

          <div class="mb-3">
            <label class="form-label">Description</label>
            <textarea
              class="form-control"
              rows="3"
              v-model.trim="form.description"
              :disabled="isViewMode || submitting" />
          </div>

          <div class="form-check form-switch mb-3">
            <input
              class="form-check-input"
              type="checkbox"
              id="isActiveSwitch"
              v-model="form.is_active"
              :disabled="isViewMode || submitting" />
            <label class="form-check-label" for="isActiveSwitch">Active</label>
          </div>

          <!-- Actions -->
          <div class="d-flex justify-content-center gap-2">
            <button type="button" class="btn btn-secondary" :disabled="submitting" @click="goList">
              <i class="fas fa-arrow-left me-1"></i>
              Cancel
            </button>

            <button v-if="!isViewMode" type="submit" class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
              <i v-else class="fas fa-save me-1"></i>
              {{ submitting ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
  import axios from 'axios';
  import Swal from 'sweetalert2';
  import { onMounted, ref, computed } from 'vue';
  import { useRoute, useRouter } from 'vue-router';

  const route = useRoute();
  const router = useRouter();

  const id = route.query.id;
  const isViewMode = computed(() => route.query.mode === 'view');
  const isEditMode = computed(() => !!id && !isViewMode.value);

  const submitting = ref(false);
  const form = ref({
    name: '',
    description: '',
    is_active: true,
  });

  async function loadData() {
    if (!id) return;
    try {
      const { data } = await axios.get(`/api/party-categories/${id}/`);
      form.value = {
        name: data.name || '',
        description: data.description || '',
        is_active: !!data.is_active,
      };
    } catch (error) {
      console.error('Load error:', error);
      await Swal.fire('Oops!', 'Error loading the category.', 'error');
    }
  }

  function validateLocal() {
    const name = (form.value.name || '').trim();
    if (!name) {
      Swal.fire('Validation', 'Name is required.', 'warning');
      return false;
    }
    if (name.length > 150) {
      Swal.fire('Validation', 'Name must be at most 150 characters.', 'warning');
      return false;
    }
    return true;
  }

  async function handleSubmit() {
    if (!validateLocal()) return;

    submitting.value = true;
    try {
      if (isEditMode.value) {
        await axios.put(`/api/party-categories/${id}/`, form.value);
      } else {
        await axios.post('/api/party-categories/', form.value);
      }
      // Éxito silencioso + redirección inmediata
      goList();
    } catch (error) {
      console.error('Error saving party category:', error);
      const { status, data } = error?.response || {};

      if (status === 400 && data) {
        const messages = Object.entries(data)
          .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
          .join('\n');
        await Swal.fire('Oops!', messages || 'There were validation errors.', 'error');
      } else if (status === 403) {
        await Swal.fire('Forbidden', 'You do not have permission for this action.', 'error');
      } else {
        await Swal.fire('Oops!', 'Error saving the party category.', 'error');
      }
    } finally {
      submitting.value = false;
    }
  }

  function goList() {
    router.push({ name: 'party-categories' });
  }

  onMounted(loadData);
</script>
