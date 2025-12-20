<template>
  <div class="container mt-4">
    <div class="text-center">
      <h3 class="text-warning">Party Types</h3>
    </div>

    <div class="card shadow-sm mx-auto" style="max-width: 720px">
      <div class="card-header d-flex justify-content-center align-items-center">
        <h6 class="mb-0 w-100 text-center text-primary">
          {{ isViewMode ? 'View Party Type' : isEditMode ? 'Edit Party Type' : 'New Party Type' }}
        </h6>
      </div>

      <div class="card-body p-4  text-start">
        <form @submit.prevent="handleSubmit" novalidate>
          <!-- Name -->
          <div class="mb-3">
            <label for="name" class="form-label">
              Name
              <span class="text-danger">*</span>
            </label>
            <input
              id="name"
              type="text"
              class="form-control"
              v-model="form.name"
              maxlength="150"
              required
              :disabled="submitting || isViewMode" />
          </div>

          <!-- Description -->
          <div class="mb-3">
            <label for="description" class="form-label">Description</label>
            <textarea
              id="description"
              class="form-control"
              rows="3"
              v-model="form.description"
              placeholder="Optional description..."
              :disabled="submitting || isViewMode"></textarea>
          </div>

          <!-- Active -->
          <div class="mb-4 form-check form-switch">
            <input
              id="is_active"
              class="form-check-input"
              type="checkbox"
              v-model="form.is_active"
              :disabled="submitting || isViewMode" />
            <label class="form-check-label" for="is_active">Active</label>
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
  import { ref, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import axios from 'axios';
  import Swal from 'sweetalert2';
  import '@assets/css/base.css';

  const route = useRoute();
  const router = useRouter();

  // Modo view si viene ?mode=view; edit si hay ?id (y no es view); create si no hay id.
  const isViewMode = ref(route.query.mode === 'view');
  const isEditMode = ref(!!route.query.id && !isViewMode.value);
  const submitting = ref(false);
  const id = route.query.id || null;

  const form = ref({
    name: '',
    description: '',
    is_active: true,
  });

  onMounted(async () => {
    // Si pidieron view pero no pasaron id, no hay nada que ver.
    if (isViewMode.value && !id) {
      await Swal.fire('Info', 'No record to view.', 'info');
      goList();
      return;
    }

    if (id) {
      try {
        const { data } = await axios.get(`/api/party-types/${id}/`);
        form.value = data;
      } catch (error) {
        console.error('Error loading party type:', error);
        await Swal.fire('Oops!', 'Error loading the party type.', 'error');
        goList();
      }
    }
  });

  const handleSubmit = async () => {
    if (isViewMode.value) return;

    try {
      submitting.value = true;

      // 1) Trim + validación mínima
      form.value.name = (form.value.name ?? '').trim();
      form.value.description = (form.value.description ?? '').trim();

      if (!form.value.name) {
        await Swal.fire('Validation', 'Name is required.', 'warning');
        return;
      }
      if (form.value.name.length > 150) {
        await Swal.fire('Validation', 'Name cannot exceed 150 characters.', 'warning');
        return;
      }

      // 2) Guardar
      if (isEditMode.value) {
        await axios.put(`/api/party-types/${id}/`, form.value);
      } else {
        await axios.post('/api/party-types/', form.value);
      }

      // Éxito silencioso → 2) Redirect por nombre (con fallback al path)
      goList();
    } catch (error) {
      console.error('Error saving party type:', error);
      const { status, data } = error?.response || {};

      if (status === 400 && data) {
        const messages = Object.entries(data)
          .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
          .join('\n');
        await Swal.fire('Oops!', messages || 'There were validation errors.', 'error');
      } else if (status === 403) {
        await Swal.fire('Forbidden', 'You do not have permission for this action.', 'error');
      } else {
        await Swal.fire('Oops!', 'Error saving the party type.', 'error');
      }
    } finally {
      submitting.value = false;
    }
  };

  const goList = () => {
    // 2) Redirección por NOMBRE 'party-types' (ajusta si tu router usa otro)
    router.push({ name: 'party-types' }).catch(() => {
      router.push('/party-types'); // fallback al path
    });
  };
</script>

<style scoped></style>
