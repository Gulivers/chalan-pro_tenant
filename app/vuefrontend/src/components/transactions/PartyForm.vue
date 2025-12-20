<template>
  <div class="container position-relative my-2">
    <!-- Encabezado principal (naranja, centrado) -->
    <h3 class="text-center text-warning mb-2">Party</h3>

    <div class="card shadow mb-2">
      <div class="card-header d-flex align-items-center justify-content-between position-relative">
        <!-- Subtítulo según modo (primary, centrado) -->
        <h6 class="mb-0 w-100 text-center text-primary">{{ title }}</h6>
      </div>

      <div class="card-body">
        <div v-if="loading" class="text-muted">Loading...</div>

        <form v-else @submit.prevent="handleSubmit" novalidate>
          <!-- non_field_errors -->
          <div v-if="serverErrors.non_field_errors" class="alert alert-warning py-2">
            <ul class="mb-0">
              <li v-for="(msg, i) in serverErrors.non_field_errors" :key="'warn-' + i">{{ msg }}</li>
            </ul>
          </div>

          <!-- === Formulario horizontal (labels a la izquierda) === -->
          <div class="row g-3">
            <!-- Name / RFC -->
            <div class="col-md-6">
              <div class="row align-items-center g-2">
                <label class="col-sm-3 form-label" for="f-name">
                  Name
                  <span class="text-danger">*</span>
                </label>
                <div class="col-sm-9">
                  <input
                    id="f-name"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.name }"
                    v-model="form.name"
                    :disabled="isViewMode"
                    maxlength="255"
                    autocomplete="off"
                    required
                    v-tt="'Enter the legal or trade name of the party'"/>
                  <div v-if="serverErrors.name" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.name" :key="'name-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-3 text-primary"
                  for="f-rfc">
                  RFC
                </label>
                <div class="col-sm-9">
                  <input
                    id="f-rfc"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.rfc }"
                    v-model="form.rfc"
                    :disabled="isViewMode"
                    maxlength="50"
                    autocomplete="off"
                    v-tt="'Enter the tax identification number (RFC) if available'" />
                  <div v-if="serverErrors.rfc" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.rfc" :key="'rfc-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Street / Floor -->
            <div class="col-md-6">
              <div class="row align-items-center g-2">
                <label class="col-sm-3 text-primary" for="f-street">Street</label>
                <div class="col-sm-9">
                  <input
                    id="f-street"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.street }"
                    v-model="form.street"
                    :disabled="isViewMode"
                    maxlength="100"
                    autocomplete="off"
                    v-tt="'Enter the street address and number'" />
                  <div v-if="serverErrors.street" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.street" :key="'street-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-3 text-primary"
                  for="f-floor">
                  Floor/Office
                </label>
                <div class="col-sm-9">
                  <input
                    id="f-floor"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.floor_office }"
                    v-model="form.floor_office"
                    :disabled="isViewMode"
                    maxlength="100"
                    autocomplete="off"
                    v-tt="'Enter suite, floor or office number if applicable'" />
                  <div v-if="serverErrors.floor_office" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.floor_office" :key="'fo-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- City / State / Zip -->
            <div class="col-md-6">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-3 text-primary"
                  for="f-city">
                  City
                </label>
                <div class="col-sm-9">
                  <input
                    id="f-city"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.city }"
                    v-model="form.city"
                    :disabled="isViewMode"
                    maxlength="100"
                    autocomplete="off"
                    v-tt="'Enter the city name'" />
                  <div v-if="serverErrors.city" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.city" :key="'city-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-6 text-primary"
                  for="f-state">
                  State
                </label>
                <div class="col-sm-6">
                  <input
                    id="f-state"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.state }"
                    v-model="form.state"
                    :disabled="isViewMode"
                    maxlength="100"
                    autocomplete="off"
                    v-tt="'Enter the state or province'" />
                  <div v-if="serverErrors.state" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.state" :key="'state-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-6 text-primary"
                  for="f-zip">
                  Zip Code
                </label>
                <div class="col-sm-4">
                  <input
                    id="f-zip"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.zipcode }"
                    v-model="form.zipcode"
                    :disabled="isViewMode"
                    maxlength="7"
                    autocomplete="off"
                    v-tt="'Enter the postal or zip code'" />
                  <div v-if="serverErrors.zipcode" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.zipcode" :key="'zip-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Country / Phone -->
            <div class="col-md-6">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-3 text-primary"
                  for="f-country">
                  Country
                </label>
                <div class="col-sm-9">
                  <input
                    id="f-country"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.country }"
                    v-model="form.country"
                    :disabled="isViewMode"
                    maxlength="100"
                    autocomplete="off"
                    v-tt="'Enter the country name'" />
                  <div v-if="serverErrors.country" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.country" :key="'country-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-3 text-primary"
                  for="f-phone">
                  Phone
                </label>
                <div class="col-sm-9">
                  <input
                    id="f-phone"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.phone }"
                    v-model="form.phone"
                    :disabled="isViewMode"
                    maxlength="20"
                    autocomplete="off"
                    v-tt="'Enter the main contact phone number'" />
                  <div v-if="serverErrors.phone" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.phone" :key="'phone-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Email / Types -->
            <div class="col-md-6">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-3 text-primary"
                  for="f-email">
                  Email
                </label>
                <div class="col-sm-9">
                  <input
                    id="f-email"
                    type="email"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.email }"
                    v-model="form.email"
                    :disabled="isViewMode"
                    maxlength="255"
                    autocomplete="off"
                    v-tt="'Enter the primary contact email address'" />
                  <div v-if="serverErrors.email" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.email" :key="'email-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-3 text-primary">
                  Types
                </label>
                <div class="col-sm-9">
                  <v-select
                    :options="options.types"
                    label="name"
                    :reduce="o => o.id"
                    v-model="form.types"
                    :disabled="isViewMode"
                    multiple
                    :class="{ 'is-invalid': serverErrors.types }"
                    placeholder="Select one or more types"
                    :close-on-select="false"
                    :clearable="true"
                    v-tt="'Select the roles or types that apply to this party'" />
                  <div v-if="serverErrors.types" class="invalid-feedback d-block">
                    <div v-for="(msg, idx) in serverErrors.types" :key="'types-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Category / Default Price Type -->
            <div class="col-md-6">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-3 text-primary">
                  Category
                </label>
                <div class="col-sm-9">
                  <v-select
                    :options="options.categories"
                    label="name"
                    :reduce="o => o.id"
                    v-model="form.category"
                    :disabled="isViewMode"
                    :class="{ 'is-invalid': serverErrors.category }"
                    placeholder="Select a category"
                    :clearable="true"
                    v-tt="'Select a category to segment or group this party'" />
                  <div v-if="serverErrors.category" class="invalid-feedback d-block">
                    <div v-for="(msg, idx) in serverErrors.category" :key="'cat-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-3 text-primary">
                  Default Price Type
                </label>
                <div class="col-sm-9">
                  <v-select
                    :options="options.priceTypes"
                    label="name"
                    :reduce="o => o.id"
                    v-model="form.default_price_type"
                    :disabled="isViewMode"
                    :class="{ 'is-invalid': serverErrors.default_price_type }"
                    placeholder="Select a price type"
                    :clearable="true"
                    v-tt="'Select the default price type to use for sales transactions'" />
                  <div v-if="serverErrors.default_price_type" class="invalid-feedback d-block">
                    <div v-for="(msg, idx) in serverErrors.default_price_type" :key="'pt-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Ranks / Active -->
            <div class="col-md-3">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-6 text-primary"
                  for="f-crank">
                  Customer Rank
                </label>
                <div class="col-sm-6">
                  <input
                    id="f-crank"
                    type="number"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.customer_rank }"
                    v-model.number="form.customer_rank"
                    :disabled="isViewMode"
                    min="0"
                    v-tt="'Set customer priority rank (higher number = higher priority)'" />
                  <div v-if="serverErrors.customer_rank" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.customer_rank" :key="'cr-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="row align-items-center g-2">
                <label
                  class="col-sm-6 text-primary"
                  for="f-srank">
                  Supplier Rank
                </label>
                <div class="col-sm-6">
                  <input
                    id="f-srank"
                    type="number"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.supplier_rank }"
                    v-model.number="form.supplier_rank"
                    :disabled="isViewMode"
                    min="0"
                    v-tt="'Set supplier priority rank (higher number = higher priority)'" />
                  <div v-if="serverErrors.supplier_rank" class="invalid-feedback">
                    <div v-for="(msg, idx) in serverErrors.supplier_rank" :key="'sr-' + idx">{{ msg }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-3 d-flex align-items-center">
              <div class="form-check form-switch" title="Enable/disable this party">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="isActiveSwitch"
                  v-model="form.is_active"
                  :disabled="isViewMode"
                  v-tt="'Enable or disable this party for transactions'" />
                <label class="form-check-label ms-2" for="isActiveSwitch">Active</label>
              </div>
            </div>
          </div>

          <div class="mt-4 d-flex justify-content-center gap-2 py-2">
            <button v-if="!isViewMode" type="submit" class="btn btn-primary" :disabled="submitting">
              <i class="fas fa-save me-1" v-if="!submitting" ></i>
              {{ submitting ? 'Saving...' : 'Save' }}
            </button>

            <button type="button" class="btn btn-secondary" @click="handleCancel">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, reactive, computed, onMounted, onActivated, onBeforeUnmount, nextTick } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import axios from 'axios';
  import Swal from 'sweetalert2';
  import '@assets/css/base.css';

  // Ajusta al nombre/path real de tu ruta de lista
  const LIST_ROUTE_NAME = 'parties';
  const LIST_ROUTE_PATH = '/parties';

  const route = useRoute();
  const router = useRouter();
  
  const props = defineProps({
    id: {
      type: [String, Number],
      default: null
    },
    isModal: {
      type: Boolean,
      default: false
    }
  });

  const emit = defineEmits(['saved', 'cancel']);

  const id = computed(() => props.id || route.query.id || null);
  const isViewMode = route.query.mode === 'view';
  const isEditMode = computed(() => !!id.value && !isViewMode);
  const isCreateMode = computed(() => !id.value);

  const title = computed(() => (isCreateMode.value ? 'Create Party' : isViewMode ? 'View Party' : 'Edit Party'));

  const loading = ref(false);
  const submitting = ref(false);
  const serverErrors = reactive({});

  // Errores de SweetAlert (requeridos)
  const validationErrors = reactive({});
  const REQUIRED_LABELS = {
    name: 'Name',
    rfc: 'RFC',
    street: 'Street',
    city: 'City',
    state: 'State',
    country: 'Country',
    phone: 'Phone',
    email: 'Email',
    types: 'Types',
    category: 'Category',
    default_price_type: 'Default Price Type',
  };

  // Form alineado con tu serializer
  const form = reactive({
    name: '',
    rfc: '',
    street: '',
    floor_office: '',
    city: '',
    state: '',
    zipcode: '',
    country: '',
    phone: '',
    email: '',
    types: [],
    category: null,
    default_price_type: null,
    customer_rank: 0,
    supplier_rank: 0,
    is_active: true,
  });

  // Catálogos para vue-select
  const options = reactive({ types: [], categories: [], priceTypes: [] });

  function normalizePaginator(data) {
    return Array.isArray(data) ? data : Array.isArray(data?.results) ? data.results : [];
  }

  function trimForm() {
    for (const k of Object.keys(form)) {
      if (typeof form[k] === 'string') form[k] = form[k].trim();
    }
    if (form.email) form.email = form.email.toLowerCase();
  }

  function resetServerErrors() {
    for (const k of Object.keys(serverErrors)) delete serverErrors[k];
  }

  function redirectToList() {
    if (LIST_ROUTE_NAME) {
      try {
        router.push({ name: LIST_ROUTE_NAME });
      } catch {
        router.push(LIST_ROUTE_PATH);
      }
    } else {
      router.push(LIST_ROUTE_PATH);
    }
  }

  function handleCancel() {
    if (props.isModal) {
      // En modal, emitir evento para cerrar
      emit('cancel');
    } else {
      // En página normal, redirigir a lista
      redirectToList();
    }
  }

  // Validación de requeridos (SweetAlert)
  function resetValidationErrors() {
    for (const k of Object.keys(validationErrors)) delete validationErrors[k];
  }
  function validateRequiredFields() {
    resetValidationErrors();
    const isEmpty = val => {
      if (val == null) return true;
      if (typeof val === 'string') return val.trim().length === 0;
      if (Array.isArray(val)) return val.length === 0;
      return false;
    };
    Object.keys(REQUIRED_LABELS).forEach(key => {
      if (isEmpty(form[key])) validationErrors[key] = `${REQUIRED_LABELS[key]} is required.`;
    });
    return Object.keys(validationErrors).length === 0;
  }
  function showRequiredAlert() {
    const html = `<ul>${Object.values(validationErrors)
      .map(msg => `<li>${msg}</li>`)
      .join('')}</ul>`;
    return Swal.fire({ title: 'Missing Required Fields', html, icon: 'error', confirmButtonText: 'OK' });
  }

  /** -------- Validación cliente (mínima) -------- */
  function validateClient() {
    const errs = {};
    if (!form.name) errs.name = ['This field is required.'];
    else if (form.name.length < 2) errs.name = ['Must be at least 2 characters.'];
    else if (form.name.length > 255) errs.name = ['Must be 255 characters or fewer.'];
    if (form.rfc && form.rfc.length > 50) errs.rfc = ['Must be 50 characters or fewer.'];
    [
      ['street', 100],
      ['floor_office', 100],
      ['city', 100],
      ['state', 100],
      ['country', 100],
    ].forEach(([k, max]) => {
      if (form[k] && form[k].length > max) errs[k] = [`Must be ${max} characters or fewer.`];
    });
    [
      ['zipcode', 20],
      ['phone', 20],
    ].forEach(([k, max]) => {
      if (form[k] && form[k].length > max) errs[k] = [`Must be ${max} characters or fewer.`];
    });
    if (form.email) {
      const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRe.test(form.email)) errs.email = ['Enter a valid email address.'];
    }
    ['customer_rank', 'supplier_rank'].forEach(k => {
      if (!Number.isInteger(form[k]) || form[k] < 0) errs[k] = ['Must be a non-negative integer.'];
    });
    resetServerErrors();
    Object.assign(serverErrors, errs);
    return Object.keys(errs).length === 0;
  }

  /** -------- Carga de catálogos y detalle -------- */
  async function fetchCatalogs() {
    const [t, c, p] = await Promise.all([
      axios.get('/api/party-types/?is_active=true&ordering=name'),
      axios.get('/api/party-categories/?is_active=true&ordering=name'),
      axios.get('/api/pricetypes/?is_active=true&ordering=name'), // módulo appinventory
    ]);
    options.types = normalizePaginator(t.data);
    options.categories = normalizePaginator(c.data);
    options.priceTypes = normalizePaginator(p.data);
  }

  // --- Refresh helpers ---
  let lastFetchTs = 0;
  const REFRESH_MIN_MS = 1000;
  async function refreshCatalogs(force = false) {
    const now = Date.now();
    if (!force && now - lastFetchTs < REFRESH_MIN_MS) return;
    try {
      await fetchCatalogs();
      lastFetchTs = now;
    } catch (e) {
      serverErrors.non_field_errors = ['Failed to refresh catalogs.'];
      console.error('refreshCatalogs error:', e);
    }
  }
  function handleWindowFocus() {
    refreshCatalogs(true);
  }

  async function fetchPartyIfNeeded() {
    if (!id.value) return;
    const { data } = await axios.get(`/api/parties/${id.value}/`);
    Object.assign(form, data);
  }

  onMounted(async () => {
    loading.value = true;
    try {
      await refreshCatalogs(true);
      await fetchPartyIfNeeded();
    } catch (e) {
      serverErrors.non_field_errors = ['Failed to load catalogs. Check your session or network and try again.'];
      console.error('PartyForm init error:', e);
    } finally {
      loading.value = false;
    }

    window.addEventListener('focus', handleWindowFocus);
  });

  onActivated(() => refreshCatalogs(true));
  onBeforeUnmount(() => {
    window.removeEventListener('focus', handleWindowFocus);
  });

  /** -------- Guardar (create/edit) -------- */
  async function handleSubmit() {
    if (isViewMode) return;
    trimForm();
    const hasAllRequired = validateRequiredFields();
    if (!hasAllRequired) {
      await showRequiredAlert();
      return;
    }
    if (!validateClient()) return;
    submitting.value = true;
    try {
      let savedData;
      if (isEditMode) {
        const response = await axios.put(`/api/parties/${id.value}/`, form);
        savedData = response.data;
      } else {
        const response = await axios.post('/api/parties/', form);
        savedData = response.data;
      }
      
      // Emit saved event for modal usage
      emit('saved', savedData);
      
      // Solo redirigir si NO estamos en modal
      if (!props.isModal) {
        redirectToList();
      }
    } catch (error) {
      const data = error?.response?.data;
      resetServerErrors();
      if (data && typeof data === 'object') Object.assign(serverErrors, data);
      else serverErrors.non_field_errors = ['Unexpected error. Please try again.'];
    } finally {
      submitting.value = false;
    }
  }
</script>

<style scoped>
  /* Ajustes horizontales */
  .v-select,
  .v-select .vs__dropdown-toggle {
    width: 100%;
  }
  .badge {
    font-weight: 500;
  }
  /* Labels alineadas a la izquierda en móviles */
  @media (max-width: 576px) {
    .text-primary {
      text-align: left !important;
    }
  }

</style>
