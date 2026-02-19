<template>
  <div class="container mt-3">
    <div class="text-center">
      <h3 class="text-warning">Truck</h3>
    </div>
    <div class="card shadow-sm mx-auto" style="max-width: 720px">
      <div class="card-header d-flex justify-content-center align-items-center">
        <h6 class="mb-0 w-100 text-center text-primary">{{ formTitle }}</h6>
      </div>
      <div class="card-body text-start">
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="mb-3">
            <label class="form-label mb-2">Plate Number <span class="text-danger">*</span></label>
            <input type="text" class="form-control" v-model.trim="form.plate_number" maxlength="20" :disabled="isViewMode || submitting" required />
          </div>
          <div class="mb-3">
            <label class="form-label mb-2">Model <span class="text-danger">*</span></label>
            <input type="text" class="form-control" v-model.trim="form.model" maxlength="255" :disabled="isViewMode || submitting" required />
          </div>
          <div class="mb-3">
            <label class="form-label mb-2">Year <span class="text-danger">*</span></label>
            <input type="number" class="form-control" v-model.number="form.year" min="1900" max="2100" :disabled="isViewMode || submitting" required />
          </div>
          <div class="form-check form-switch mb-3">
            <input class="form-check-input" type="checkbox" id="statusSwitch" v-model="form.status" :disabled="isViewMode || submitting" />
            <label class="form-check-label" for="statusSwitch">Active</label>
          </div>
          <div class="d-flex justify-content-center gap-2">
            <button type="button" class="btn btn-secondary" :disabled="submitting" @click="goList">Cancel</button>
            <button v-if="!isViewMode" type="submit" class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
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
import { onMounted, ref, computed, getCurrentInstance } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === 'crew-truck-view');
const isEditMode = computed(() => !!id && !isViewMode.value);

const submitting = ref(false);
const form = ref({
  plate_number: '',
  model: '',
  year: new Date().getFullYear(),
  status: true,
});

const formTitle = computed(() => {
  if (isViewMode.value) return 'View Truck';
  if (isEditMode.value) return 'Edit Truck';
  return 'Add Truck';
});

async function loadData() {
  if (!id) return;
  try {
    const { data } = await axios.get(`/api/trucks/${id}/`);
    form.value = {
      plate_number: data.plate_number || '',
      model: data.model || '',
      year: data.year || new Date().getFullYear(),
      status: !!data.status,
    };
  } catch (err) {
    console.error('Load error:', err);
    await Swal.fire('Oops!', 'Error loading the truck.', 'error');
  }
}

function validate() {
  if (!(form.value.plate_number || '').trim()) {
    Swal.fire('Validation', 'Plate number is required.', 'warning');
    return false;
  }
  if (!(form.value.model || '').trim()) {
    Swal.fire('Validation', 'Model is required.', 'warning');
    return false;
  }
  const y = form.value.year;
  if (!y || y < 1900 || y > 2100) {
    Swal.fire('Validation', 'Year must be between 1900 and 2100.', 'warning');
    return false;
  }
  return true;
}

async function handleSubmit() {
  if (!validate()) return;
  submitting.value = true;
  try {
    const payload = { plate_number: form.value.plate_number.trim(), model: form.value.model.trim(), year: form.value.year, status: form.value.status };
    if (id) {
      await axios.patch(`/api/trucks/${id}/`, payload);
      proxy?.notifyToastSuccess?.('Truck updated.');
      router.push({ name: 'crew-trucks' });
    } else {
      const { data } = await axios.post('/api/trucks/', payload);
      proxy?.notifyToastSuccess?.('Truck created.');

      const result = await Swal.fire({
        title: 'Create mobile warehouse for this truck?',
        text: 'Do you want to create a mobile warehouse to track equipment assets and serial numbers for this truck?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Yes',
        cancelButtonText: 'No',
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#6c757d',
      });

      if (result.isConfirmed) {
        try {
          const res = await axios.post(`/api/trucks/${data.id}/create-mobile-warehouse/`);
          const msg = res.data?.message || (res.status === 201 ? 'Mobile warehouse created.' : 'Mobile warehouse already exists.');
          proxy?.notifyToastSuccess?.(msg);
        } catch (whErr) {
          console.error('Create mobile warehouse error:', whErr);
          const detail = whErr.response?.data?.detail;
          const msg = (typeof detail === 'string' ? detail : Object.values(detail || {}).flat().join(' ') || 'Error creating mobile warehouse.');
          Swal.fire('Error', msg, 'error');
        }
      }
      router.push({ name: 'crew-trucks' });
    }
  } catch (err) {
    console.error('Save error:', err);
    const msg = err.response?.data ? (Object.values(err.response.data).flat().join(' ') || 'Error saving truck.') : 'Error saving truck.';
    Swal.fire('Error', msg, 'error');
  } finally {
    submitting.value = false;
  }
}

function goList() {
  router.push({ name: 'crew-trucks' });
}

onMounted(loadData);
</script>
