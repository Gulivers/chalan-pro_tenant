<template>
  <div
    class="modal fade"
    ref="modalElement"
    :id="id"
    tabindex="-1"
    role="dialog"
    aria-labelledby="jobModalLabel"
    aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="jobModalLabel">
            {{ action === 'edit' ? 'Edit Community (Job)' : 'Add Community (Job)' }}
          </h5>
          <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="saveJob">
            <!-- Name Field -->
            <div class="mb-3">
              <label for="jobName" class="form-label">Name</label>
              <input
                id="jobName"
                type="text"
                v-model="modalJob.name"
                class="form-control"
                :class="{ 'is-invalid': error.name }"
                placeholder="Enter community name"
                @input="clearError('name')"
                required />
              <div v-if="error.name" class="text-danger mt-1">Please provide a community name.</div>
            </div>

            <!-- [M2M] Assigned Crews -->
            <div class="mb-3">
              <label for="assignedCrews" class="form-label">Assigned Crews</label>
              <v-select
                id="assignedCrews"
                :options="crews"
                v-model="modalJob.crews"
                :multiple="false"
                :reduce="c => c.id"
                label="name"
                :close-on-select="true"
                placeholder="Select one or more crews" />
              <!-- Si lo quieres obligatorio, habilita validación -->
              <!-- <div v-if="error.crews" class="text-danger mt-1">Please select at least one crew.</div> -->
            </div>

            <!-- Builder Field -->
            <div class="mb-3">
              <label for="builder" class="form-label">Builder</label>
              <v-select
                id="builder"
                :options="builders"
                v-model="modalJob.builder"
                :reduce="builder => builder.id"
                label="name"
                placeholder="Select Builder"
                :class="{ 'is-invalid': error.builder }"
                @input="clearError('builder')"
                required />
              <div v-if="error.builder" class="text-danger mt-1">Please select a builder.</div>
            </div>

            <!-- Address Field -->
            <div class="mb-3">
              <label for="address" class="form-label">Address</label>
              <input
                id="address"
                type="text"
                v-model="modalJob.address"
                class="form-control"
                placeholder="Enter address"
                @input="fetchCoordinates" />
            </div>

            <!-- Latitude Field -->
            <div class="mb-3">
              <label for="latitude" class="form-label">Latitude</label>
              <input
                id="latitude"
                type="number"
                step="0.000001"
                v-model="modalJob.latitude"
                class="form-control"
                placeholder="Latitude (Optional)" />
            </div>

            <!-- Longitude Field -->
            <div class="mb-3">
              <label for="longitude" class="form-label">Longitude</label>
              <input
                id="longitude"
                type="number"
                step="0.000001"
                v-model="modalJob.longitude"
                class="form-control"
                placeholder="Longitude (Optional)" />
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button type="button" class="btn btn-primary" @click="saveJob">
            {{ action === 'edit' ? 'Update' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import { Modal } from 'bootstrap';
  import vSelect from 'vue-select';
  import 'vue-select/dist/vue-select.css';

  export default {
    name: 'JobModalComponent',
    components: { vSelect },
    props: {
      id: String,
      action: String,
      job: {
        type: Object,
        default: () => ({
          name: '',
          builder: null,
          address: '',
          latitude: null,
          longitude: null,
          crews: [], // [M2M] puede venir vacío
        }),
      },
      builders: { type: Array, default: () => [] },
    },
    data() {
      return {
        modalJob: {
          id: null, // necesario para PUT
          name: '',
          builder: null,
          address: '',
          latitude: null,
          longitude: null,
          crews: [], // [M2M] array de IDs
        },
        crews: [], // catálogo para el select
        modalInstance: null,
        error: { name: false, builder: false /*, crews: false*/ },
      };
    },
    watch: {
      job: {
        async handler(newJob) {
          if (!newJob) return
          this.modalJob.id = newJob.id || null
          this.modalJob.name = newJob.name || ''
          this.modalJob.builder = newJob.builder || null
          this.modalJob.address = newJob.address || ''
          this.modalJob.latitude = newJob.latitude !== null ? newJob.latitude : null
          this.modalJob.longitude = newJob.longitude !== null ? newJob.longitude : null

          // Normalizar crews SIEMPRE a array de IDs
          const raw = Array.isArray(newJob.crews) && newJob.crews.length
             ? newJob.crews
             : (Array.isArray(newJob.crews_detail) ? newJob.crews_detail : [])

           if (raw.length) {
             const ids = raw.map(c => (typeof c === 'object' ? c.id : c)).filter(Boolean)
             this.modalJob.crews = ids
           } else {
             // Si no vino nada en el prop, traemos el detalle del job para obtener crews
             await this.fetchJobDetailCrews(this.modalJob.id)
           }
        },
        immediate: true,
        deep: true,
      },
    },
    mounted() {
      if (this.$refs.modalElement) {
        this.modalInstance = Modal.getOrCreateInstance(this.$refs.modalElement);
        
        // Agregar event listener para manejar el foco cuando se oculta el modal
        this.$refs.modalElement.addEventListener('hidden.bs.modal', () => {
          // Asegurar que no hay elementos con foco dentro del modal oculto
          const focusedElement = this.$refs.modalElement.querySelector(':focus')
          if (focusedElement) {
            focusedElement.blur()
          }
        })
      } else {
        console.error('Modal element not found in JobModalComponent');
      }
      this.fetchCrews();
    },
    methods: {
      async fetchCrews() {
        try {
          // Segun tu router: /api/crews/
          const { data } = await axios.get('/api/crews/');
          this.crews = (Array.isArray(data) ? data : []).map(c => ({
            id: c.id,
            name: c.name || c.title || `Crew #${c.id}`,
          }));
        } catch (e) {
          console.error('Error fetching crews:', e);
        }
      },

      validateFields() {
        let ok = true;
        if (!this.modalJob.name || this.modalJob.name.trim() === '') {
          this.error.name = true;
          ok = false;
        } else this.error.name = false;
        if (!this.modalJob.builder) {
          this.error.builder = true;
          ok = false;
        } else this.error.builder = false;
        // Si quieres crews obligatorio:
        // if (!this.modalJob.crews?.length) { this.error.crews = true; ok = false } else this.error.crews = false
        return ok;
      },

      clearError(field) {
        this.error[field] = false;
      },

      async saveJob() {

        if (!this.validateFields()) return
        try {
          const crewsNorm = Array.isArray(this.modalJob.crews)
            ? this.modalJob.crews
            : (this.modalJob.crews == null ? [] : [this.modalJob.crews])  // coacción a array
            console.log('[DBG] type of crews:', typeof this.modalJob.crews, this.modalJob.crews)
          const payload = {
            name: this.modalJob.name,
            builder: this.modalJob.builder,
            address: this.modalJob.address,
            latitude: this.modalJob.latitude || null,
            longitude: this.modalJob.longitude || null,
            crews: crewsNorm.map(n => Number(n)).filter(n => !Number.isNaN(n)), // números limpios
          }

          if (this.action === 'edit') {
            if (!this.modalJob.id) { console.error('[JOB] Missing modalJob.id in edit mode'); return }
            await axios.put(`/api/job/${this.modalJob.id}/`, payload)
          } else {
            await axios.post('/api/job/', payload)
          }

          this.$emit('refresh')
          this.$emit('saved', payload)
          if (this.action !== 'edit') this.$emit('clearJobSelect')
          this.closeModal()
        } catch (error) {
          console.error('Error saving job:', error?.response?.data || error?.message)
        }
      },

      async fetchCoordinates() {
        if (!this.modalJob.address || this.modalJob.address.length < 5) return;
        try {
          const response = await axios.get('https://nominatim.openstreetmap.org/search', {
            params: { q: this.modalJob.address, format: 'json', addressdetails: 1 },
            headers: { 'User-Agent': 'chalan-pro-app' },
          });
          if (response.data.length > 0) {
            const loc = response.data[0];
            this.modalJob.latitude = parseFloat(loc.lat) || null;
            this.modalJob.longitude = parseFloat(loc.lon) || null;
          }
        } catch (error) {
          console.error('Error fetching coordinates:', error);
        }
      },

      showModal() {
        if (this.modalInstance) {
          this.modalInstance.show();
          // Enfocar el primer campo después de que el modal se muestre
          this.$nextTick(() => {
            const firstInput = this.$refs.modalElement?.querySelector('input[type="text"]')
            if (firstInput) {
              firstInput.focus()
            }
          })
        }
      },
      hideModal() {
        // Quitar el foco antes de ocultar el modal
        if (document.activeElement) {
          document.activeElement.blur()
        }
        if (this.modalInstance) this.modalInstance.hide();
      },
      closeModal() {
        // Quitar el foco antes de cerrar
        if (document.activeElement) {
          document.activeElement.blur()
        }
        this.hideModal();
        this.$emit('close');
      },
      async fetchJobDetailCrews(jobId) {
        if (!jobId) return
        try {
          const { data } = await axios.get(`/api/job/${jobId}/`)
          // Si tu serializer expone 'crews' (ids) o 'crews_detail' (objetos), soportamos ambos:
          const raw = Array.isArray(data.crews) && data.crews.length
            ? data.crews
            : (Array.isArray(data.crews_detail) ? data.crews_detail : [])

          const ids = raw.map(c => (typeof c === 'object' ? c.id : c)).filter(Boolean)
          this.modalJob.crews = ids
        } catch (e) {
          console.error('[JobModal] fetchJobDetailCrews error:', e?.response?.data || e)
        }
      },
    },
  };
</script>

<style scoped>
  .text-danger {
    color: red;
    font-size: 0.875rem;
  }
  .is-invalid {
    border-color: red !important;
    box-shadow: 0 0 5px red !important;
  }
</style>
