<template>
  <div class="container">
    <h3 class="text-warning pt-3">
      <p>{{ cleanFormTitle }}</p>
    </h3>

    <div class="card shadow mb-4">
      <div class="card-header">
        <h6 class="ms-1 font-weight-bold text-primary">{{ formTitle }}</h6>
      </div>

      <div class="card-body">
        <form @submit.prevent="handleSubmit" v-if="Object.keys(internalSchema).length">
          <div class="row g-3">
            <div class="col-md-6" v-for="(config, key) in internalSchema" :key="key">
              <!-- Layout horizontal para campos normales -->
              <div v-if="config.type !== 'boolean'" class="row align-items-center g-2">
                
                <label class="col-12 col-sm-3 col-form-label text-start text-sm-end">
                  {{ config.label }}
                  <span v-if="config.required" class="text-danger">*</span>
                </label>
                <div class="col-sm-9">
                  <!-- Text / String -->
                  <input
                    v-if="config.type === 'string' || config.type === 'text'"
                    v-model.trim="form[key]"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': validationErrors[key] }"
                    :placeholder="`Enter ${config.label}...`"
                    :disabled="isDisabled" />
                  <!-- Error message for string fields -->
                  <div
                    v-if="validationErrors[key] && (config.type === 'string' || config.type === 'text')"
                    class="invalid-feedback d-block">
                    {{ validationErrors[key] }}
                  </div>

                  <!-- Textarea -->
                  <textarea
                    v-else-if="config.type === 'textarea' || config.widget === 'textarea'"
                    v-model.trim="form[key]"
                    class="form-control"
                    :placeholder="`Enter ${config.label}...`"
                    :disabled="isDisabled" />

                  <!-- Select con v-select -->
                  <v-select
                    v-else-if="config.type === 'select'"
                    v-model="form[key]"
                    :options="optionsMap[key] || []"
                    :label="'label'"
                    :reduce="opt => opt.value"
                    :disabled="isDisabled"
                    :multiple="config.multiple || false"
                    :placeholder="`Select ${config.label}...`"
                    :clearable="true"
                    :close-on-select="!config.multiple"
                    :class="{ 'is-invalid': validationErrors[key] }" />
                  <!-- Error message for select fields -->
                  <div v-if="validationErrors[key] && config.type === 'select'" class="invalid-feedback d-block">
                    {{ validationErrors[key] }}
                  </div>
                </div>
              </div>

              <!-- Boolean con layout especial -->
              <div v-else-if="config.type === 'boolean'" class="row align-items-center g-2">
                <div class="col-sm-3"></div>
                <div class="col-sm-9">
                  <div class="form-check form-switch d-flex align-items-center">
                    <input
                      v-model="form[key]"
                      class="form-check-input"
                      type="checkbox"
                      role="switch"
                      :id="key"
                      :disabled="isDisabled" />
                    <label class="form-check-label ms-2 text-primary" :for="key">
                      {{ config.label }}
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Botones -->
          <div class="mt-4" v-if="!isViewMode">
            <button type="submit" class="btn btn-primary" :disabled="isDisabled">
              <span
                v-if="submitting"
                class="spinner-border spinner-border-sm me-1"
                role="status"
                aria-hidden="true"></span>
              <i v-else class="fas fa-save me-1"></i>
              {{ submitting ? 'Saving...' : 'Save' }}
            </button>

            <button type="button" class="btn btn-secondary ms-2" @click="cancelForm" :disabled="submitting">
              Cancel
            </button>
          </div>

          <div v-else>
            <button type="button" class="btn btn-secondary mt-3" @click="cancelForm" :disabled="submitting">
              Back
            </button>
          </div>
        </form>

        <div v-else>
          <p class="text-muted">Loading Schema and checking for fields...</p>
          <div class="spinner-border"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import Swal from 'sweetalert2';
  import vSelect from 'vue-select';
  import selectMixin from '@/helpers/useSelectOptions'; // debe exportar default { ... } (mixin)

  export default {
    name: 'DynamicForm',
    components: {
      vSelect,
    },
    mixins: [selectMixin], // sin appMixin
    props: {
      schema: Object,
      schemaEndpoint: String,
      apiEndpoint: { type: String, required: true }, // e.g. '/api/builder/'
      objectId: { type: [String, Number], default: null },
      formTitle: { type: String, default: 'Form' },
      readOnly: { type: Boolean, default: false }, // fuerza modo view
      redirectAfterSave: { type: String, default: null }, // ruta (path) o nombre de ruta
      isModal: { type: Boolean, default: false },
    },
    data() {
      return {
        internalSchema: {},
        form: {},
        fields: [],
        submitting: false,
        validationErrors: {},
      };
    },
    computed: {
      isViewMode() {
        // soporta prop readOnly o query ?mode=view
        return this.readOnly || this.$route?.query?.mode === 'view';
      },
      isEditMode() {
        return !!this.objectId && !this.isViewMode;
      },
      isDisabled() {
        return this.isViewMode || this.submitting;
      },
      cleanFormTitle() {
        return this.formTitle
          .replace(/^Create\s+/i, '')
          .replace(/^Edit\s+/i, '')
          .replace(/^View\s+/i, '')
          .trim();
      },
    },
    watch: {
      objectId: {
        immediate: true,
        async handler() {
          if (this.internalSchema && Object.keys(this.internalSchema).length) {
            await this.loadRecord();
          }
        },
      },
    },
    async created() {
      try {
        // 1) Cargar esquema
        if (this.schema && Object.keys(this.schema).length) {
          this.internalSchema = this.schema;
        } else if (this.schemaEndpoint) {
          const response = await axios.get(this.schemaEndpoint);
          this.internalSchema = response.data || {};
        }

        this.fields = Object.keys(this.internalSchema);

        // 2) Cargar opciones de selects (mixin)
        await this.loadOptionsForSchema(this.internalSchema);

        // 3) Cargar registro (si objectId)
        await this.loadRecord();
      } catch (err) {
        console.error('❌ Error initializing schema:', err);
        await Swal.fire('Oops!', 'Error initializing the form schema.', 'error');
      }
    },
    methods: {
      async loadRecord() {
        if (!this.internalSchema || !Object.keys(this.internalSchema).length) return;
        try {
          if (this.objectId) {
            const res = await axios.get(`${this.apiEndpoint}${this.objectId}/`);
            this.form = res.data;
          } else {
            // inicializa valores (boolean -> false, otros -> '')
            this.form = Object.fromEntries(
              this.fields.map(f => {
                const type = this.internalSchema[f]?.type;
                const def = this.internalSchema[f]?.default;
                if (def !== undefined) return [f, def];
                return [f, type === 'boolean' ? false : ''];
              })
            );
          }
        } catch (err) {
          console.error('❌ Error loading record:', err);
          await Swal.fire('Oops!', 'Error loading the record.', 'error');
        }
      },

      _buildCleanPayload() {
        const cleaned = { ...this.form };

        for (const key of this.fields) {
          const cfg = this.internalSchema[key] || {};

          // Trimming para strings/textarea
          if (['string', 'text'].includes(cfg.type) || cfg.type === 'textarea' || cfg.widget === 'textarea') {
            cleaned[key] = (cleaned[key] ?? '').toString().trim();
          }

          // Selects con optionsEndpoint: si viene objeto, extrae id/value
          if (cfg.type === 'select' && cfg.optionsEndpoint) {
            const v = cleaned[key];
            cleaned[key] = v && typeof v === 'object' ? v.id ?? v.value ?? '' : v;
          }
        }
        return cleaned;
      },

      // Validaciones del frontend
      validateForm() {
        this.validationErrors = {};
        let hasErrors = false;

        for (const [key, config] of Object.entries(this.internalSchema)) {
          const value = this.form[key];
          const label = config.label || key;

          // Validación de campos requeridos
          if (config.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
            this.validationErrors[key] = `${label} is required.`;
            hasErrors = true;
            continue;
          }

          // Validaciones específicas por campo
          if (value && typeof value === 'string') {
            const trimmedValue = value.trim();

            // Validación de Name (mínimo 2 caracteres)
            if (key === 'name' && trimmedValue.length > 0 && trimmedValue.length < 2) {
              this.validationErrors[key] = 'Must be at least 2 characters.';
              hasErrors = true;
            }

            // Validación de Email
            if (key === 'email' && trimmedValue.length > 0) {
              const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
              if (!emailRegex.test(trimmedValue)) {
                this.validationErrors[key] = 'Enter a valid email address.';
                hasErrors = true;
              }
            }

            // Validación de RFC (máximo 50 caracteres)
            if (key === 'rfc' && trimmedValue.length > 50) {
              this.validationErrors[key] = 'Must be 50 characters or fewer.';
              hasErrors = true;
            }
          }
        }

        return !hasErrors;
      },

      // Validación de duplicados (Name y RFC)
      async validateUniqueness() {
        const name = this.form.name?.trim();
        const rfc = this.form.rfc?.trim();

        if (!name && !rfc) return true;

        try {
          // Verificar si ya existe un Builder con el mismo nombre o RFC
          const params = new URLSearchParams();
          if (name) params.append('name', name);
          if (rfc) params.append('rfc', rfc);
          if (this.objectId) params.append('exclude_id', this.objectId);

          const response = await axios.get(`${this.apiEndpoint}?${params.toString()}`);
          const existingBuilders = Array.isArray(response.data) ? response.data : response.data.results || [];

          if (existingBuilders.length > 0) {
            const duplicateBuilder = existingBuilders[0];
            const errors = [];

            if (name && duplicateBuilder.name?.toLowerCase() === name.toLowerCase()) {
              errors.push(`Name "${name}" already exists.`);
            }

            if (rfc && duplicateBuilder.rfc === rfc) {
              errors.push(`RFC "${rfc}" already exists.`);
            }

            if (errors.length > 0) {
              const errorList = errors.map(error => `<li><strong>${error}</strong></li>`).join('');
              const html = `<div class="text-start"><ul class="mb-0">${errorList}</ul></div>`;
              await Swal.fire({
                title: 'Duplicate Data',
                html: html,
                icon: 'error',
                confirmButtonText: 'OK',
              });
              return false;
            }
          }

          return true;
        } catch (error) {
          console.error('Error validating uniqueness:', error);
          // Si hay error en la validación, permitir continuar
          return true;
        }
      },

      async handleSubmit() {
        if (this.isViewMode) return;

        // Validaciones del frontend
        if (!this.validateForm()) {
          return;
        }

        // Validación de duplicados
        if (!(await this.validateUniqueness())) {
          return;
        }

        this.submitting = true;

        const payload = this._buildCleanPayload();
        const url = this.objectId ? `${this.apiEndpoint}${this.objectId}/` : this.apiEndpoint;
        const method = this.objectId ? 'put' : 'post';

        try {
          const response = await axios[method](url, payload);

          // Éxito silencioso + redirección
          if (this.redirectAfterSave) {
            if (this.redirectAfterSave.startsWith('/')) {
              this.$router.push(this.redirectAfterSave);
            } else {
              this.$router.push({ name: this.redirectAfterSave });
            }
          } else {
            // En modo modal, emitir el objeto guardado
            this.$emit('saved', response.data);
          }
        } catch (error) {
          console.error('❌ Save error:', error);
          const { status, data } = error?.response || {};
          
          if (status === 400 && data) {
            // Manejar errores de validación del backend
            const errorList = Object.entries(data)
              .map(([field, msgs]) => {
                const label = this.internalSchema[field]?.label || field;
                const message = Array.isArray(msgs) ? msgs.join(', ') : msgs;
                return `<li><strong>${label}:</strong> ${message}</li>`;
              })
              .join('');

            const html = `<div class="text-start"><ul class="mb-0">${errorList}</ul></div>`;
            await Swal.fire({
              title: 'Validation Errors',
              html: html,
              icon: 'error',
              confirmButtonText: 'OK',
            });
          } else if (status === 403) {
            await Swal.fire('Forbidden', 'You do not have permission for this action.', 'error');
          } else {
            // Error genérico
            const errorMessage = data?.detail || data?.message || 'Error saving the record.';
            await Swal.fire('Oops!', errorMessage, 'error');
          }
        } finally {
          this.submitting = false;
        }
      },

      cancelForm() {
        if (this.isModal) {
          this.$emit('cancel');
        } else {
          if (this.$router && this.$route.name) {
            this.$router.back();
          } else {
            this.$emit('cancel');
          }
        }
      },
    },
  };
</script>

<style scoped>
  .form-check-label {
    margin-left: 0.5rem;
  }

  /* Estilos para v-select */
  .v-select,
  .v-select .vs__dropdown-toggle {
    width: 100%;
  }

  /* Labels alineadas a la derecha en móviles también */
  @media (max-width: 576px) {
    .text-primary.text-end {
      text-align: right !important;
    }

    .row.align-items-center .col-sm-3 {
      margin-bottom: 0.5rem;
    }
  }

  /* Ajustes para formulario horizontal */
  .row.align-items-center {
    margin-bottom: 0.5rem;
  }

  .form-label {
    font-weight: 500;
    margin-bottom: 0;
  }

  /* Estilos para campos booleanos */
  .form-check-input {
    margin-top: 0;
  }

  /* Ajustes para v-select en formulario horizontal */
  .v-select .vs__selected-options {
    padding: 0.375rem 0.75rem;
  }

  .v-select .vs__dropdown-toggle {
    border: 1px solid #ced4da;
    border-radius: 0.375rem;
    min-height: 38px;
  }

  .v-select .vs__dropdown-toggle:focus {
    border-color: #86b7fe;
    box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
  }

  .v-select.is-invalid .vs__dropdown-toggle {
    border-color: #dc3545;
  }

  .v-select.is-invalid .vs__dropdown-toggle:focus {
    border-color: #dc3545;
    box-shadow: 0 0 0 0.25rem rgba(220, 53, 69, 0.25);
  }
</style>
