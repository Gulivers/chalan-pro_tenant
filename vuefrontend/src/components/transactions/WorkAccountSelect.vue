<template>
  <div class="container position-relative my-2">

    <h3 class="text-center text-warning mb-2">Work Account</h3>

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

          <!-- === Formulario en dos columnas === -->
          <div class="row g-3">
            <!-- Columna izquierda - Campos principales -->
            <div class="col-md-6">
              <!-- Builder, Job, House Model -->
              <div class="mb-3">
                <BuilderJobHouseSelect
                  v-model="builderJobHouseData"
                  :is-editing="isEditing"
                  :is-absence="isDisabled"
                  @update:builder="onBuilderChanged($event)"
                  @update:job="onJobChanged($event)"
                  @update:houseModel="onHouseModelChanged($event)" />
              </div>

              <!-- Lot -->
              <div class="row mb-3">
                <div class="col-12 d-flex flex-column flex-sm-row justify-content-center align-items-center gap-2">
                  <label class="col-12 col-sm-2 col-form-label" for="f-lot">Lot</label>
                  <input
                    id="f-lot"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': (lotTouched && !canEditLotAddr) || serverErrors.lot }"
                    v-model.trim="local.lot"
                    :placeholder="canEditLotAddr ? 'Enter lot...' : 'Select Builder and Job first'"
                    :disabled="!canEditLotAddr || isDisabled"
                    @input="onUserTypedTitle()"
                    @blur="
                      lotTouched = true;
                      autoFillTitle();
                    "
                    maxlength="100"
                    autocomplete="off"
                    v-tt="'Lot number or identifier. Enabled when Builder and Job are selected.'" />
                </div>
                <div v-if="lotTouched && !canEditLotAddr" class="invalid-feedback d-block">
                  You must select both a
                  <strong>Builder</strong>
                  and a
                  <strong>Job</strong>
                  before entering Lot.
                </div>
                <div v-if="serverErrors.lot" class="invalid-feedback">
                  <div v-for="(msg, idx) in serverErrors.lot" :key="'lot-' + idx">{{ msg }}</div>
                </div>
              </div>

              <!-- Address -->
              <div class="row mb-3">
                <div class="col-12 d-flex flex-column flex-sm-row justify-content-center align-items-center gap-2">
                  <label class="col-12 col-sm-2 col-form-label" for="f-address">Address</label>
                  <input
                    id="f-address"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': (addrTouched && !canEditLotAddr) || serverErrors.address }"
                    v-model.trim="local.address"
                    :placeholder="canEditLotAddr ? 'Street, City ST ZIP' : 'Select Builder and Job first'"
                    :disabled="!canEditLotAddr || isDisabled"
                    @input="onUserTypedTitle()"
                    @blur="
                      addrTouched = true;
                      autoFillTitle();
                    "
                    maxlength="255"
                    autocomplete="off"
                    v-tt="'Street address. Auto-contributes to TITLE when Job is selected.'" />
                </div>
                <div v-if="addrTouched && !canEditLotAddr" class="invalid-feedback d-block">
                  You must select both a
                  <strong>Builder</strong>
                  and a
                  <strong>Job</strong>
                  before entering Address.
                </div>
                <div v-if="serverErrors.address" class="invalid-feedback">
                  <div v-for="(msg, idx) in serverErrors.address" :key="'addr-' + idx">{{ msg }}</div>
                </div>
              </div>

              <!-- TITLE (auto, uppercase) -->
              <div class="row mb-3">
                <div class="col-12 d-flex flex-column flex-sm-row justify-content-center align-items-center gap-2">
                  <label class="col-12 col-sm-2 col-form-label" for="f-title">
                    TITLE
                    <span class="text-danger">*</span>
                  </label>
                  <input
                    id="f-title"
                    type="text"
                    class="form-control text-uppercase"
                    :class="{ 'is-invalid': serverErrors.title }"
                    v-model="local.title"
                    @input="onTitleTyped"
                    placeholder="Will auto-fill from Lot/Address + Job"
                    maxlength="200"
                    autocomplete="off"
                    :disabled="isDisabled"
                    required
                    v-tt="
                      'Friendly identifier (UPPERCASE). Autocompletes from Lot/Address + Job; you can override it.'
                    " />
                </div>
                <div class="form-text text-center">TITLE. Always stored in UPPERCASE.</div>
                <div v-if="serverErrors.title" class="invalid-feedback">
                  <div v-for="(msg, idx) in serverErrors.title" :key="'title-' + idx">{{ msg }}</div>
                </div>
              </div>
              <!-- Active switch -->
              <div class="row mb-3">
                <div class="col-12 d-flex flex-column flex-sm-row align-items-center gap-2">
                  <label class="col-12 col-sm-2 col-form-label" for="wa-active">Active</label>
                  <div class="form-check form-switch" title="Enable/disable this work account">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      id="wa-active"
                      v-model="local.is_active"
                      :disabled="isDisabled"
                      v-tt="'When inactive, this Work Account is hidden for selection and uniqueness rules relax.'" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Columna derecha - Campos secundarios -->
            <div class="col-md-6">
              <!-- Default Price Type -->
              <div class="row mb-3">
                <div class="col-12 d-flex flex-column flex-sm-row justify-content-center align-items-center gap-2">
                  <label class="col-12 col-sm-2 col-form-label">Default Price Type</label>
                  <v-select
                    :options="priceTypeOptions"
                    :reduce="p => p.id"
                    label="name"
                    v-model="local.default_price_type"
                    :loading="loadingPriceTypes.priceTypes"
                    @search="onSearchPriceTypes"
                    :clearable="true"
                    :disabled="isDisabled"
                    :class="{ 'is-invalid': serverErrors.default_price_type }"
                    placeholder="Select a price type"
                    v-tt="'Optional default Price Type used in transactions for this work account.'" />
                </div>
                <div v-if="serverErrors.default_price_type" class="invalid-feedback d-block">
                  <div v-for="(msg, idx) in serverErrors.default_price_type" :key="'pt-' + idx">{{ msg }}</div>
                </div>
              </div>

              <!-- City -->
              <div class="row mb-3">
                <div class="col-12 d-flex flex-column flex-sm-row justify-content-center align-items-center gap-2">
                  <label class="col-12 col-sm-2 col-form-label" for="f-city">City</label>
                  <input
                    id="f-city"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.city }"
                    v-model.trim="local.city"
                    maxlength="100"
                    autocomplete="off"
                    :disabled="isDisabled"
                    v-tt="'Optional city for the work account.'" />
                </div>
                <div v-if="serverErrors.city" class="invalid-feedback">
                  <div v-for="(msg, idx) in serverErrors.city" :key="'city-' + idx">{{ msg }}</div>
                </div>
              </div>

              <!-- State -->
              <div class="row mb-3">
                <div class="col-12 d-flex flex-column flex-sm-row justify-content-center align-items-center gap-2">
                  <label class="col-12 col-sm-2 col-form-label" for="f-state">State</label>
                  <input
                    id="f-state"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.state }"
                    v-model.trim="local.state"
                    maxlength="50"
                    autocomplete="off"
                    :disabled="isDisabled"
                    v-tt="'Optional state (e.g., FL).'" />
                </div>
                <div v-if="serverErrors.state" class="invalid-feedback">
                  <div v-for="(msg, idx) in serverErrors.state" :key="'state-' + idx">{{ msg }}</div>
                </div>
              </div>

              <!-- ZIP Code -->
              <div class="row mb-3">
                <div class="col-12 d-flex flex-column flex-sm-row justify-content-center align-items-center gap-2">
                  <label class="col-12 col-sm-2 col-form-label" for="f-zip">ZIP Code</label>
                  <input
                    id="f-zip"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.zipcode }"
                    v-model.trim="local.zipcode"
                    maxlength="20"
                    autocomplete="off"
                    :disabled="isDisabled"
                    v-tt="'Optional ZIP/Postal code.'" />
                </div>
                <div v-if="serverErrors.zipcode" class="invalid-feedback">
                  <div v-for="(msg, idx) in serverErrors.zipcode" :key="'zip-' + idx">{{ msg }}</div>
                </div>
              </div>

              <!-- Notes -->
              <div class="row mb-3">
                <div class="col-12 d-flex flex-column flex-sm-row justify-content-center align-items-center gap-2">
                  <label class="col-12 col-sm-2 col-form-label" for="f-notes">Notes</label>
                  <textarea
                    id="f-notes"
                    class="form-control"
                    :class="{ 'is-invalid': serverErrors.notes }"
                    rows="4"
                    v-model.trim="local.notes"
                    maxlength="500"
                    :disabled="isDisabled"
                    v-tt="'Free text notes about this Work Account.'"></textarea>
                </div>
                <div v-if="serverErrors.notes" class="invalid-feedback">
                  <div v-for="(msg, idx) in serverErrors.notes" :key="'notes-' + idx">{{ msg }}</div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="!isDisabled" class="mt-4 d-flex justify-content-center gap-2 py-2">
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status"></span>
              <i v-else class="fas fa-save me-1"></i>
              {{ submitting ? 'Saving...' : 'Save' }}
            </button>

            <button type="button" class="btn btn-secondary" :disabled="submitting" @click="onCancel">
              <i class="fas fa-arrow-left me-1"></i>
              Cancel
            </button>
          </div>

          <!-- Botón para modo de vista -->
          <div v-if="isViewMode" class="mt-4 d-flex justify-content-center gap-2 py-2">
            <button type="button" class="btn btn-secondary" @click="goList">
              <i class="fas fa-arrow-left me-1"></i>
              Back
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, reactive, watch, computed, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import axios from 'axios';
  import VSelect from 'vue-select';
  import 'vue-select/dist/vue-select.css';
  import '@assets/css/base.css';
  import BuilderJobHouseSelect from '@/components/houses/BuilderJobHouseSelect.vue';
  import Swal from 'sweetalert2';

  const route = useRoute();
  const router = useRouter();

  const props = defineProps({
    id: {
      type: [String, Number],
      default: null,
    },
    modelValue: {
      type: Object,
      default: () => ({
        builder: null,
        job: null,
        house_model: null,
        lot: '',
        address: '',
        city: '',
        state: '',
        zipcode: '',
        default_price_type: null,
        title: '',
        notes: '',
        is_active: true,
      }),
    },
    isEditing: { type: Boolean, default: true },
    isAbsence: { type: Boolean, default: false },
    workAccountId: { type: [Number, String], default: null },
    endpoints: {
      type: Object,
      default: () => ({
        jobs: '/api/jobs/',
        priceTypes: '/api/pricetypes/',
        workAccounts: '/api/work-accounts/',
      }),
    },
    /** Route name to redirect after silent success (CRUD Pattern) */
    listRouteName: { type: String, default: 'work-accounts' },
    /** When used inside a modal, disable router redirection on save/cancel */
    redirectOnSuccess: { type: Boolean, default: true },
  });

  // Detectar modo por query parameters o prop (similar a PartyForm.vue)
  // Si se proporciona un prop.id, usarlo; de lo contrario, usar route.query.id
  // Pero solo si estamos en una ruta directa, no en un modal
  const id = props.id ?? (route.name === 'work-accounts-form' ? route.query.id : null) ?? null;
  console.log('🔍 DEBUG WorkAccountSelect: props.id:', props.id, 'route.query.id:', route.query.id, 'route.name:', route.name, 'final id:', id);
  const isViewMode = route.query.mode === 'view';
  const isEditMode = !!id && id !== null && id !== 'null' && !isViewMode;
  const isCreateMode = !id || id === null || id === 'null';

  const emit = defineEmits(['update:modelValue', 'change', 'warning', 'success', 'error', 'cancel', 'saved']);

  const local = reactive({ ...props.modelValue });
  const lotTouched = ref(false);
  const addrTouched = ref(false);
  const titleManuallyEdited = ref(false);
  const submitting = ref(false);
  const loading = ref(false);
  const serverErrors = reactive({});

  const builderJobHouseData = reactive({
    builder: local.builder,
    job: local.job,
    house_model: local.house_model,
  });

  const jobName = ref('');
  const canEditLotAddr = computed(() => !!(local.builder && local.job));

  const loadingPriceTypes = reactive({ priceTypes: false });
  const priceTypeOptions = ref([]);

  const title = computed(() => {
    if (isCreateMode) return 'Create Work Account';
    if (isViewMode) return 'View Work Account';
    return 'Edit Work Account';
  });

  // Computed para determinar si los campos deben estar deshabilitados
  const isDisabled = computed(() => props.isAbsence || isViewMode);

  watch(
    () => props.modelValue,
    val => {
      Object.assign(local, val || {});
    }
  );
  watch(local, () => emitChange(), { deep: true });

  // Watch for id prop changes to reload data
  watch(() => props.id, async (newId) => {
    console.log('🔍 DEBUG WorkAccountSelect: props.id changed to:', newId, 'Type:', typeof newId);
    if (newId && newId !== null && newId !== 'null') {
      await loadWorkAccount();
    }
  });

  function emitChange() {
    emit('update:modelValue', { ...local, title: (local.title || '').toUpperCase() });
    emit('change', { ...local });
  }

  function onTitleTyped() {
    titleManuallyEdited.value = true;
    local.title = (local.title || '').toUpperCase();
    emitChange();
  }

  function onUserTypedTitle() {
    if (!titleManuallyEdited.value) autoFillTitle();
  }

  async function resolveJobName(jobId) {
    if (!jobId) {
      jobName.value = '';
      return;
    }
    try {
      const { data } = await axios.get(props.endpoints.jobs, { params: { id: jobId } });
      const obj = Array.isArray(data?.results)
        ? data.results.find(j => j.id === jobId)
        : Array.isArray(data)
        ? data.find(j => j.id === jobId)
        : data;
      jobName.value = (obj?.name || '').trim().toUpperCase();
    } catch (_) {
      jobName.value = '';
    }
  }

  function onBuilderChanged(v) {
    builderJobHouseData.builder = v;
    local.builder = v;
    builderJobHouseData.job = null;
    builderJobHouseData.house_model = null;
    local.job = null;
    local.house_model = null;
    lotTouched.value = false;
    addrTouched.value = false;
    autoFillTitle();
    emitChange();
  }

  function onJobChanged(v) {
    builderJobHouseData.job = v;
    local.job = v;
    builderJobHouseData.house_model = null;
    local.house_model = null;
    lotTouched.value = false;
    addrTouched.value = false;
    resolveJobName(v);
    autoFillTitle();
    emitChange();
  }

  function onHouseModelChanged(v) {
    builderJobHouseData.house_model = v;
    local.house_model = v;
    autoFillTitle();
    emitChange();
  }

  function autoFillTitle() {
    if (titleManuallyEdited.value) return;
    const builder = local.builder;
    const job = local.job;
    const lot = (local.lot || '').trim().toUpperCase();
    const address = (local.address || '').trim().toUpperCase();

    if ((lot || address) && (!builder || !job)) {
      if (props.isEditing) emit('warning', 'You must select both a Builder and a Job before entering Lot or Address.');
      local.title = '';
      return;
    }

    const jobLabel = (jobName.value || '').toUpperCase();
    if (lot) {
      local.title = jobLabel ? `${lot} ${jobLabel}` : `${lot}`;
    } else if (address) {
      local.title = jobLabel ? `${address} ${jobLabel}` : `${address}`;
    } else {
      local.title = jobLabel || (local.title || '').toUpperCase();
    }
  }

  // Recalcular el TITLE cuando se resuelva asincrónicamente el nombre del Job
  watch(jobName, () => {
    if (!titleManuallyEdited.value) autoFillTitle();
  });

  watch(
    () => [local.lot, local.address, local.job, local.builder],
    () => {
      if (!titleManuallyEdited.value) autoFillTitle();
    }
  );
  if (local.job) resolveJobName(local.job);

  // === Price Types ===
  async function onSearchPriceTypes(search) {
    loadingPriceTypes.priceTypes = true;
    try {
      const { data } = await axios.get(props.endpoints.priceTypes, { params: { search } });
      priceTypeOptions.value = data?.results || data || [];
    } finally {
      loadingPriceTypes.priceTypes = false;
    }
  }
  (async () => {
    await onSearchPriceTypes('');
  })();

  // === Cargar datos para modo edit/view ===
  const loadWorkAccount = async () => {
    if (!id || id === null || id === 'null') return;

    loading.value = true;
    try {
      const response = await axios.get(`/api/work-accounts/${id}/`);
      const data = response.data;

      // Mapear datos del servidor al formato del formulario
      Object.assign(local, {
        builder: data.builder,
        job: data.job,
        house_model: data.house_model,
        lot: data.lot || '',
        address: data.address || '',
        city: data.city || '',
        state: data.state || '',
        zipcode: data.zipcode || '',
        default_price_type: data.default_price_type,
        title: data.title || '',
        notes: data.notes || '',
        is_active: data.is_active !== false,
      });

      // Actualizar builderJobHouseData
      builderJobHouseData.builder = data.builder;
      builderJobHouseData.job = data.job;
      builderJobHouseData.house_model = data.house_model;

      // Resolver nombre del job si existe
      if (data.job) {
        await resolveJobName(data.job);
        if (!titleManuallyEdited.value) autoFillTitle();
      }
    } catch (error) {
      console.error('Error loading work account:', error);
      
      // Si es un error 404 (work account no encontrado), no mostrar modal
      if (error.response?.status === 404) {
        console.warn(`Work account ${id} not found, skipping load`);
        loading.value = false;
        return;
      }
      
      // Para otros errores, mostrar el modal
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error loading work account data.',
        confirmButtonText: 'OK',
      }).then(() => {
        router.push({ name: 'work-accounts' });
      });
    } finally {
      loading.value = false;
    }
  };

  // === CRUD: Save / Cancel ===
  async function handleSubmit() {
    if (isViewMode) return;

    try {
      submitting.value = true;

      // 1) Trim + validación mínima
      const trimmedData = {
        builder: local.builder,
        job: local.job,
        house_model: local.house_model,
        lot: (local.lot ?? '').trim(),
        address: (local.address ?? '').trim(),
        city: (local.city ?? '').trim(),
        state: (local.state ?? '').trim(),
        zipcode: (local.zipcode ?? '').trim(),
        default_price_type: local.default_price_type,
        title: (local.title ?? '').trim().toUpperCase(),
        notes: (local.notes ?? '').trim(),
        is_active: local.is_active,
      };

      // Validaciones requeridas
      if (!trimmedData.builder) {
        await Swal.fire('Validation', 'Builder is required.', 'warning');
        return;
      }
      if (!trimmedData.job) {
        await Swal.fire('Validation', 'Job is required.', 'warning');
        return;
      }
      if (!trimmedData.lot && !trimmedData.address) {
        await Swal.fire('Validation', 'Either Lot or Address is required.', 'warning');
        return;
      }
      if (!trimmedData.title) {
        await Swal.fire('Validation', 'Title is required.', 'warning');
        return;
      }

      // Validaciones de longitud
      if (trimmedData.lot.length > 100) {
        await Swal.fire('Validation', 'Lot cannot exceed 100 characters.', 'warning');
        return;
      }
      if (trimmedData.address.length > 255) {
        await Swal.fire('Validation', 'Address cannot exceed 255 characters.', 'warning');
        return;
      }
      if (trimmedData.title.length > 200) {
        await Swal.fire('Validation', 'Title cannot exceed 200 characters.', 'warning');
        return;
      }
      if (trimmedData.city.length > 100) {
        await Swal.fire('Validation', 'City cannot exceed 100 characters.', 'warning');
        return;
      }
      if (trimmedData.state.length > 50) {
        await Swal.fire('Validation', 'State cannot exceed 50 characters.', 'warning');
        return;
      }
      if (trimmedData.zipcode.length > 20) {
        await Swal.fire('Validation', 'ZIP Code cannot exceed 20 characters.', 'warning');
        return;
      }
      if (trimmedData.notes.length > 500) {
        await Swal.fire('Validation', 'Notes cannot exceed 500 characters.', 'warning');
        return;
      }

      // 2) Guardar
      let savedData;
      if (isEditMode) {
        const response = await axios.put(`/api/work-accounts/${id}/`, trimmedData);
        savedData = response.data;
      } else {
        const response = await axios.post('/api/work-accounts/', trimmedData);
        savedData = response.data;
      }

      // Emit saved event for modal usage
      emit('saved', savedData);

      // Solo preguntar por sincronizar títulos al EDITAR (no al crear)
      if (isEditMode) {
        const { isConfirmed } = await Swal.fire({
          title: 'Update schedule titles?',
          text: 'Do you want to propagate this title change to all related schedule events? This will overwrite customized titles.',
          icon: 'question',
          showCancelButton: true,
          confirmButtonText: 'Yes, update',
          cancelButtonText: 'No, keep as is'
        });

        if (isConfirmed) {
          try {
            const waId = id;
            if (waId) {
              const syncResp = await axios.post(`/api/work-accounts/${waId}/sync-schedule-titles/`);
              await Swal.fire({
                icon: 'success',
                title: 'Schedule Updated',
                text: `Updated ${syncResp.data?.updated_events || 0} events and ${syncResp.data?.updated_drafts || 0} drafts.`,
                timer: 2500,
                showConfirmButton: false
              });
            }
          } catch (e) {
            await Swal.fire({
              icon: 'error',
              title: 'Sync Failed',
              text: 'Could not synchronize schedule titles. You can try again later from Work Accounts.',
            });
          }
        }
      }

      // Redirección solo si está habilitada (p. ej., no en modal)
      if (props.redirectOnSuccess) {
        goList();
      }
    } catch (error) {
      console.error('Error saving work account:', error);
      const { status, data } = error?.response || {};

      if (status === 400 && data) {
        const messages = Object.entries(data)
          .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
          .join('\n');
        await Swal.fire('Oops!', messages || 'There were validation errors.', 'error');
      } else if (status === 403) {
        await Swal.fire('Forbidden', 'You do not have permission for this action.', 'error');
      } else if (status === 409) {
        await Swal.fire('Protected', 'This work account is in use and cannot be modified.', 'error');
      } else {
        await Swal.fire('Oops!', 'Error saving the work account.', 'error');
      }
    } finally {
      submitting.value = false;
    }
  }

  function goList() {
    // Redirección por NOMBRE 'work-accounts' (con fallback al path)
    router.push({ name: 'work-accounts' }).catch(() => {
      router.push('/work-accounts');
    });
  }

  function onCancel() {
    if (props.redirectOnSuccess) {
      goList();
    } else {
      emit('cancel');
    }
  }

  // === Lifecycle ===
  onMounted(async () => {
    if (id && id !== null && id !== 'null') {
      await loadWorkAccount();
    }
  });
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
  :deep(.vs__spinner) {
    border-color: #007bff transparent #007bff transparent;
  }
</style>
