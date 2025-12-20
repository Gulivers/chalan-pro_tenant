<template>
  <div class="modal fade" ref="modalElement" id="houseModelModal" tabindex="-1" aria-labelledby="houseModelModalLabel"
       aria-hidden="true">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="houseModelModalLabel">
            {{ action === 'edit' ? 'Edit House Model ' + houseModelId : 'Add House Model' }}
          </h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        <div class="modal-body text-start">
          <form @submit.prevent="handleSubmit">
            <!-- Campo para nombre del modelo -->
            <div class="mb-3">
              <label for="houseModelName" class="form-label">House Model Name</label>
              <input type="text" class="form-control" id="houseModelName" v-model="houseModel.name"
                     :class="{ 'is-invalid': error.houseModelName }" @input="clearError('houseModelName')"/>
              <div v-if="error.houseModelName" class="text-danger mt-1">
                Please provide a house model name.
              </div>
<!--
              <div v-if="resp_error?.name" class="text-danger mt-1 text-start">
                {{ resp_error.name.join(', ') }}
              </div>
-->
            </div>

            <!-- Campo para comunidades (Jobs) -->
            <div class="mb-3">
              <div class="row">
                <!-- Buttons -->
                <div class="col-md-6">
                  <label for="jobs" class="form-label">Select Communities (Jobs)</label>
                  <div class="row mb-3 text-start">
                    <div class="col-lg-6 ms-3">
                      <div class="btn-group" role="group">
                        <button type="button" class="btn btn-sm btn-outline-primary" @click="selectAll">Select All
                        </button>
                        <button type="button" class="btn btn-sm btn-outline-secondary" @click="clearAll">Deselect All
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Search Filter Input -->
                <div class="mb-3 col-md-6">
                  <label>Filter:</label>
                  <div class="position-relative">
                    <input type="text" class="form-control" v-model="searchQuery"
                           placeholder="Search by builder or community name...">
                    <span v-if="searchQuery" @click="clearSearch" class="position-absolute"
                          style="top: 50%; right: 10px; transform: translateY(-50%); cursor: pointer; font-size: 1.5rem">
                      &times;
                  </span>
                  </div>
                </div>

              </div>
              <!-- Work Price Checkboxes -->
              <div class="row px-3 text-start">
                <div v-for="(opt, gIdx) in filteredGroupedJobs" :key="'grp-' + gIdx" class="mb-2">
                  <label class="form-label text-black">{{opt.label}}</label>
                  <div class="form-check form-switch col-xl-3 col-md-4 col-sm-6" v-for="item in opt.options" :key="item.id">
                    <input class="form-check-input" type="checkbox" role="switch" :value="item.id" v-model="houseModel.jobs"/>
                    <label class="form-check-label">{{ item.name }}</label>
                  </div>
                </div>
<!--
                <div class="form-check form-switch col-xl-3 col-md-4 col-sm-6" v-for="item in jobs" :key="item.id">
                  <input class="form-check-input" type="checkbox" role="switch" :value="item.id"
                         v-model="houseModel.jobs"/>
                  <label class="form-check-label">{{ item.name }}</label>
                </div>
-->
<!--
                <multiselect v-model="houseModel.jobs" :options="groupedJobs" :group-values="'options'"
                                :group-label="'label'" :track-by="'id'" :multiple="true" label="name"
                                placeholder="Select Communities" @input="clearError('jobs')"
                                :class="{ 'is-invalid': error.jobs }" />
-->
                <div v-if="error.jobs" class="text-danger mt-1">
                  Please select at least one community.
                </div>
              </div>
            </div>

            <!-- Botones de acción -->
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
              <button type="button" class="btn btn-primary" @click="handleSubmit">
                {{ action === 'edit' ? 'Update' : 'Save' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Multiselect from 'vue-multiselect';
import 'vue-multiselect/dist/vue-multiselect.min.css';

export default {
  components: {Multiselect},
  props: {
    action: String,
    houseModelId: {
      type: Number,
      default: null,
    },
    builderId: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      modalInstance: null,
      houseModel: {
        name: '',
        jobs: [],
      },
      builders: [],
      jobs: [],
      groupedJobs: [],
      searchQuery: '', // New property for the search filter
      error: {
        jobs: false,
        houseModelName: false,
      },
      resp_error: null
    };
  },
  computed: {
    /**
     * Filters the grouped jobs based on the searchQuery.
     * It searches in the group label (builder name) and the option name (community name).
     */
    filteredGroupedJobs() {
      if (!this.searchQuery.trim()) {
        return this.groupedJobs;
      }
      const query = this.searchQuery.toLowerCase();

      const result = [];
      for (const group of this.groupedJobs) {
        // If the builder/group name matches, add the whole group
        if (group.label.toLowerCase().includes(query)) {
          result.push(group);
        } else {
          // Otherwise, check if any of the jobs/options match
          const matchingOptions = group.options.filter(option =>
            option.name.toLowerCase().includes(query)
          );
          // If there are matching jobs, add a new group with only those jobs
          if (matchingOptions.length > 0) {
            result.push({ ...group, options: matchingOptions });
          }
        }
      }
      return result;
    }
  },
  watch: {
    // houseModelId: {
    //   handler(newVal) {
    //     this.searchQuery = '';
    //     if (this.action === 'edit' && newVal) {
    //       this.fetchHouseModelJobs();
    //     } else {
    //       this.houseModel = {
    //         name: '',
    //         jobs: [],
    //       };
    //     }
    //   },
    //   immediate: true,
    // },
    // builderId: {
    //   handler(newVal) {
    //     this.searchQuery = '';
    //     if (newVal){
    //       const builder_data = this.builders.find(item => item.id === this.builderId);
    //       this.searchQuery = builder_data ? builder_data.name : '';
    //     }
    //   },
    //   immediate: true,
    // },
  },
  methods: {
    clearSearch() {
      this.searchQuery = '';
    },
    validateFields() {
      let isValid = true;

      // Validar que al menos un Job esté seleccionado
      if (!this.houseModel.jobs || this.houseModel.jobs.length === 0) {
        this.error.jobs = true;
        isValid = false;
      } else {
        this.error.jobs = false;
      }

      // Validar que el nombre del modelo no esté vacío
      if (!this.houseModel.name || this.houseModel.name.trim() === '') {
        this.error.houseModelName = true;
        isValid = false;
      } else {
        this.error.houseModelName = false;
      }

      return isValid;
    },
    clearError(field) {
      this.error[field] = false; // Elimina el error correspondiente
    },
    async handleSubmit() {
      if (!this.validateFields()) {
        return;
      }

      try {
        this.resp_error = null;
        const houseModelToSend = {
          name: this.houseModel.name,
          // jobs: this.houseModel.jobs.map(job => job.id), // Transformar los Jobs a IDs
          jobs: this.houseModel.jobs,
          builder_id: this.builderId, // Include builder_id for validation
        };

        let saved;
        if (this.action === 'edit') {
          const { data } = await axios.put(`/api/house_model/${this.houseModelId}/`, houseModelToSend);
          saved = data;
        } else {
          const { data } = await axios.post('/api/house_model/', houseModelToSend);
          saved = data;
        }

        // Notificar al padre con el objeto guardado (incluye id)
        this.$emit('saved', saved);
        this.$emit('refresh');
        this.closeModal();
      } catch (error) {
        console.error('Error saving House Model:', error);
        if (error.response) {
          if (error.response.status === 400) {
            this.resp_error = error.response.data;
            if (error.response?.data?.name){
              this.notifyError(error.response.data.name.join(', '))
            }
          }
        }
      }
    },

    async showModal() {
      // Asegurar catálogos cargados antes de filtrar
      if (!Array.isArray(this.builders) || this.builders.length === 0 || !Array.isArray(this.jobs) || this.jobs.length === 0) {
        await this.fetchBuildersAndJobs();
      }

      // Si estamos editando, precargar relaciones
      if (this.action === 'edit' && this.$props.houseModelId) {
        await this.fetchHouseModelJobs();
      }

      // Normalizar builderId a número y aplicar filtro por nombre del builder
      const builderIdNum = this.builderId != null ? Number(this.builderId) : null;
      if (builderIdNum) {
        const builderData = (this.builders || []).find(item => Number(item.id) === builderIdNum);
        this.searchQuery = builderData ? (builderData.name || '') : '';
      } else {
        this.searchQuery = '';
      }

      if (this.modalInstance) {
        this.modalInstance.show();
      }
    },
    hideModal() {
      // Solo cierra el modal sin emitir eventos (llamado desde el padre)
      this.houseModel = {
        name: '',
        jobs: [],
      };
      if (this.modalInstance) {
        this.modalInstance.hide();
      }
    },
    closeModal() {
      // Cierra el modal Y emite el evento (llamado desde los botones internos)
      this.houseModel = {
        name: '',
        jobs: [],
      };
      if (this.modalInstance) {
        this.modalInstance.hide();
      }
      this.$emit('close');
    },
    async fetchBuildersAndJobs() {
      try {
        const builderResponse = await axios.get('/api/builder/');
        const jobResponse = await axios.get('/api/job/');
        this.builders = builderResponse.data || [];
        this.jobs = jobResponse.data || [];
        this.groupedJobs = this.builders.map(builder => ({
          label: 'Builder: ' + builder.name || 'Unnamed Builder',
          options: this.jobs.filter(job => job && job.builder === builder.id && job.name),
        })).filter(group => group.options.length > 0);
      } catch (error) {
        console.error('Error fetching Builders or Jobs:', error);
      }
    },
    async fetchHouseModelJobs() {
      try {
        if (this.houseModelId) {
          const response = await axios.get(`/api/house_models/${this.houseModelId}/jobs/`);
          const {houseModel, jobs} = response.data;
          this.houseModel.name = houseModel.name;
          this.houseModel.jobs = jobs.map(job => job.id)
        }
      } catch (error) {
        console.error('Error fetching House Model Jobs:', error);
      }
    },
    selectAll() {
      // this.houseModel.jobs = this.jobs.map(item => item.id);
      let listHouse = []
      this.filteredGroupedJobs.forEach(item => {
        item.options.forEach(opt => {
          listHouse.push(opt.id)
        })
      });
      // console.log('listHouse::', listHouse)
      this.houseModel.jobs = listHouse
    },
    clearAll() {
      this.houseModel.jobs = [];
    }
  },
  mounted() {
    this.fetchBuildersAndJobs();
    if (this.houseModelId) {
      this.fetchHouseModelJobs();
    }
    // Vue-style Bootstrap modal instance
    if (this.$refs.modalElement) {
      const {Modal} = require('bootstrap');
      this.modalInstance = Modal.getOrCreateInstance(this.$refs.modalElement);
    }
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
