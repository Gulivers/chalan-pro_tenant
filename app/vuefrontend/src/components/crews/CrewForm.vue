<template>
  <div class="container mt-3">
    <div class="text-center">
      <h3 class="text-warning">Crew</h3>
    </div>
    <div class="card shadow-sm mx-auto" style="max-width: 720px">
      <div class="card-header d-flex justify-content-center align-items-center">
        <h6 class="mb-0 w-100 text-center text-primary">{{ formTitle }}</h6>
      </div>
      <div class="card-body text-start">
        <form @submit.prevent="handleSubmit" novalidate>
          <div class="mb-3">
            <label class="form-label d-flex align-items-center gap-2">Crew Name <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.name"
              type="text"
              class="form-control"
              maxlength="255"
              :disabled="isViewMode || submitting"
              required
              v-tt
              data-title="Crew name for identification and display purposes" />
          </div>
          <div class="mb-3">
            <label class="form-label d-flex align-items-center gap-2">
              Category
              <i
                v-tt
                class="fas fa-info-circle text-muted"
                data-title="Group crews by type or department"></i>
            </label>
            <v-select
              :options="categories"
              label="name"
              :reduce="c => c.id"
              v-model="form.category"
              placeholder="Select Category"
              :disabled="isViewMode || submitting"
              :clearable="true"
              v-tt
              data-title="Optional. Assigns the crew to a category for organization" />
          </div>
          <div class="mb-3">
            <label class="form-label d-flex align-items-center gap-2">
              Crew Members
              <i
                v-tt
                class="fas fa-info-circle text-muted"
                data-title="Users who belong to this crew"></i>
            </label>
            <v-select
              :options="users"
              label="username"
              :reduce="u => u.id"
              v-model="form.members"
              placeholder="Select Crew Members"
              :disabled="isViewMode || submitting"
              multiple
              :close-on-select="false"
              :clearable="true"
              v-tt
              data-title="Select one or more users to assign to this crew" />
          </div>
          <div class="mb-3">
            <label class="form-label d-flex align-items-center gap-2">
              Assigned Jobs
              <i
                v-tt
                class="fas fa-info-circle text-muted"
                data-title="Jobs this crew can work on"></i>
            </label>
            <v-select
              :options="jobs"
              label="name"
              :reduce="j => j.id"
              v-model="form.jobs"
              placeholder="Select Assigned Jobs"
              :disabled="isViewMode || submitting"
              multiple
              :close-on-select="false"
              :clearable="true"
              v-tt
              data-title="Select jobs that this crew is assigned to" />
          </div>
          <div class="form-check form-switch mb-3">
            <input class="form-check-input" type="checkbox" id="statusSwitch" v-model="form.status" :disabled="isViewMode || submitting" v-tt data-title="When active, the crew is available for assignments" />
            <label class="form-check-label" for="statusSwitch">Active</label>
          </div>
          <div class="form-check form-switch mb-3">
            <input class="form-check-input" type="checkbox" id="permissionSwitch" v-model="form.permission_create_event" :disabled="isViewMode || submitting" v-tt data-title="Allows this crew to create and update schedule events" />
            <label class="form-check-label" for="permissionSwitch">Can Create/Update Schedule?</label>
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
import vSelect from 'vue-select';
import axios from 'axios';
import Swal from 'sweetalert2';
import { onMounted, ref, computed, getCurrentInstance } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import 'vue-select/dist/vue-select.css';

const { proxy } = getCurrentInstance();
const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isViewMode = computed(() => route.name === 'crew-view');
const isEditMode = computed(() => !!id && !isViewMode.value);

const submitting = ref(false);
const categories = ref([]);
const users = ref([]);
const jobs = ref([]);
const form = ref({
  name: '',
  category: null,
  members: [],
  jobs: [],
  status: true,
  permission_create_event: false,
});

const formTitle = computed(() => {
  if (isViewMode.value) return 'View Crew';
  if (isEditMode.value) return 'Edit Crew';
  return 'Add Crew';
});

async function loadOptions() {
  try {
    const [catRes, usersRes, jobsRes] = await Promise.all([
      axios.get('/api/categories/'),
      axios.get('/api/crew-users/'),
      axios.get('/api/jobs/'),
    ]);
    categories.value = catRes.data.results ?? catRes.data;
    users.value = usersRes.data;
    jobs.value = jobsRes.data.results ?? jobsRes.data;
  } catch (err) {
    console.error('Load options error:', err);
  }
}

async function loadData() {
  if (!id) return;
  try {
    const { data } = await axios.get(`/api/crews/${id}/`);
    form.value = {
      name: data.name || '',
      category: data.category ?? null,
      members: Array.isArray(data.members) ? data.members : [],
      jobs: Array.isArray(data.jobs) ? data.jobs : [],
      status: !!data.status,
      permission_create_event: !!data.permission_create_event,
    };
  } catch (err) {
    console.error('Load error:', err);
    await Swal.fire('Oops!', 'Error loading the crew.', 'error');
  }
}

function validate() {
  if (!(form.value.name || '').trim()) {
    Swal.fire('Validation', 'Crew name is required.', 'warning');
    return false;
  }
  return true;
}

async function handleSubmit() {
  if (!validate()) return;
  submitting.value = true;
  try {
    const payload = {
      name: form.value.name.trim(),
      category: form.value.category,
      members: form.value.members || [],
      jobs: form.value.jobs || [],
      status: form.value.status,
      permission_create_event: form.value.permission_create_event,
    };
    if (id) {
      await axios.patch(`/api/crews/${id}/`, payload);
      proxy?.notifyToastSuccess?.('Crew updated.');
    } else {
      await axios.post('/api/crews/', payload);
      proxy?.notifyToastSuccess?.('Crew created.');
    }
    router.push({ name: 'crew-list' });
  } catch (err) {
    console.error('Save error:', err);
    const data = err.response?.data;
    let msg = 'Error saving crew.';
    if (data) {
      if (typeof data === 'string') msg = data;
      else if (data.detail) msg = Array.isArray(data.detail) ? data.detail.join(' ') : data.detail;
      else if (data.non_field_errors) msg = data.non_field_errors.join(' ');
      else msg = Object.values(data).flat().join(' ') || msg;
    }
    await Swal.fire('Validation Error', msg, 'error');
  } finally {
    submitting.value = false;
  }
}

function goList() {
  router.push({ name: 'crew-list' });
}

onMounted(async () => {
  await loadOptions();
  await loadData();
});
</script>

<style scoped>
.v-select { --vs-border-color: #ced4da; }
</style>
