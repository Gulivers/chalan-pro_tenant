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
          <div class="row px-2 text-start">
            <div
              class="col-md-6 col-lg-6 mb-3"
              v-for="(config, key) in internalSchema"
              :key="key"
            >
              <!-- Evita duplicar label en booleanos -->
              <label v-if="config.type !== 'boolean'" class="form-label">
                {{ config.label }}
              </label>

              <!-- Text / String -->
              <input
                v-if="config.type === 'string' || config.type === 'text'"
                v-model.trim="form[key]"
                type="text"
                class="form-control"
                :placeholder="`Enter ${config.label}...`"
                :disabled="isDisabled"
              />

              <!-- Textarea -->
              <textarea
                v-else-if="config.type === 'textarea' || config.widget === 'textarea'"
                v-model.trim="form[key]"
                class="form-control"
                :placeholder="`Enter ${config.label}...`"
                :disabled="isDisabled"
              />

              <!-- Select -->
              <select
                v-else-if="config.type === 'select'"
                v-model="form[key]"
                class="form-select"
                :disabled="isDisabled"
              >
                <option value="" disabled selected hidden class="text-muted">
                  Select {{ config.label }}...
                </option>
                <option
                  v-for="opt in optionsMap[key] || []"
                  :key="opt.value"
                  :value="opt.value"
                >
                  {{ opt.label }}
                </option>
              </select>

              <!-- Boolean -->
              <div
                v-else-if="config.type === 'boolean'"
                class="form-check form-switch d-flex align-items-center mt-4"
              >
                <input
                  v-model="form[key]"
                  class="form-check-input"
                  type="checkbox"
                  role="switch"
                  :id="key"
                  :disabled="isDisabled"
                />
                <label class="form-check-label ms-2" :for="key">
                  {{ config.label }}
                </label>
              </div>
            </div>
          </div>

          <!-- Botones -->
          <div class="mt-4" v-if="!isViewMode">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isDisabled"
            >
              <span
                v-if="submitting"
                class="spinner-border spinner-border-sm me-1"
                role="status"
                aria-hidden="true"
              ></span>
              <i v-else class="fas fa-save me-1"></i>
              {{ submitting ? 'Saving...' : 'Save' }}
            </button>

            <button
              type="button"
              class="btn btn-secondary ms-2"
              @click="cancelForm"
              :disabled="submitting"
            >
              Cancel
            </button>
          </div>

          <div v-else>
            <button
              type="button"
              class="btn btn-secondary mt-3"
              @click="cancelForm"
              :disabled="submitting"
            >
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
import axios from 'axios'
import Swal from 'sweetalert2'
import selectMixin from '@/helpers/useSelectOptions' // debe exportar default { ... } (mixin)

export default {
  name: 'DynamicForm',
  mixins: [selectMixin], // sin appMixin
  props: {
    schema: Object,
    schemaEndpoint: String,
    apiEndpoint: { type: String, required: true },   // e.g. '/api/product-categories/'
    objectId: { type: [String, Number], default: null },
    formTitle: { type: String, default: 'Form' },
    readOnly: { type: Boolean, default: false },     // fuerza modo view
    redirectAfterSave: { type: String, default: null }, // ruta (path) o nombre de ruta
    isModal: { type: Boolean, default: false }
  },
  data () {
    return {
      internalSchema: {},
      form: {},
      fields: [],
      submitting: false
    }
  },
  computed: {
    isViewMode () {
      // soporta prop readOnly o query ?mode=view
      return this.readOnly || (this.$route?.query?.mode === 'view')
    },
    isEditMode () {
      return !!this.objectId && !this.isViewMode
    },
    isDisabled () {
      return this.isViewMode || this.submitting
    },
    cleanFormTitle () {
      return this.formTitle
        .replace(/^Create\s+/i, '')
        .replace(/^Edit\s+/i, '')
        .replace(/^View\s+/i, '')
        .trim()
    }
  },
  watch: {
    objectId: {
      immediate: true,
      async handler () {
        if (this.internalSchema && Object.keys(this.internalSchema).length) {
          await this.loadRecord()
        }
      }
    }
  },
  async created () {
    try {
      // 1) Cargar esquema
      if (this.schema && Object.keys(this.schema).length) {
        this.internalSchema = this.schema
      } else if (this.schemaEndpoint) {
        const response = await axios.get(this.schemaEndpoint)
        this.internalSchema = response.data || {}
      }

      this.fields = Object.keys(this.internalSchema)

      // 2) Cargar opciones de selects (mixin)
      await this.loadOptionsForSchema(this.internalSchema)

      // 3) Cargar registro (si objectId)
      await this.loadRecord()
    } catch (err) {
      console.error('❌ Error initializing schema:', err)
      await Swal.fire('Oops!', 'Error initializing the form schema.', 'error')
    }
  },
  methods: {
    async loadRecord () {
      if (!this.internalSchema || !Object.keys(this.internalSchema).length) return
      try {
        if (this.objectId) {
          const res = await axios.get(`${this.apiEndpoint}${this.objectId}/`)
          this.form = res.data
        } else {
          // inicializa valores (boolean -> false, otros -> '')
          this.form = Object.fromEntries(
            this.fields.map(f => {
              const type = this.internalSchema[f]?.type
              const def = this.internalSchema[f]?.default
              if (def !== undefined) return [f, def]
              return [f, type === 'boolean' ? false : '']
            })
          )
        }
      } catch (err) {
        console.error('❌ Error loading record:', err)
        await Swal.fire('Oops!', 'Error loading the record.', 'error')
      }
    },

    _buildCleanPayload () {
      const cleaned = { ...this.form }

      for (const key of this.fields) {
        const cfg = this.internalSchema[key] || {}

        // Trimming para strings/textarea
        if (
          ['string', 'text'].includes(cfg.type) ||
          cfg.type === 'textarea' ||
          cfg.widget === 'textarea'
        ) {
          cleaned[key] = (cleaned[key] ?? '').toString().trim()
        }

        // Selects con optionsEndpoint: si viene objeto, extrae id/value
        if (cfg.type === 'select' && cfg.optionsEndpoint) {
          const v = cleaned[key]
          cleaned[key] =
            v && typeof v === 'object'
              ? (v.id ?? v.value ?? '')
              : v
        }
      }
      return cleaned
    },

    async handleSubmit () {
      if (this.isViewMode) return
      this.submitting = true

      const payload = this._buildCleanPayload()
      const url = this.objectId ? `${this.apiEndpoint}${this.objectId}/` : this.apiEndpoint
      const method = this.objectId ? 'put' : 'post'

      try {
        await axios[method](url, payload)

        // Éxito silencioso + redirección
        if (this.redirectAfterSave) {
          if (this.redirectAfterSave.startsWith('/')) {
            this.$router.push(this.redirectAfterSave)
          } else {
            this.$router.push({ name: this.redirectAfterSave })
          }
        } else {
          this.$emit('saved')
        }
      } catch (error) {
        console.error('❌ Save error:', error)
        const { status, data } = error?.response || {}
        if (status === 400 && data) {
          const messages = Object.entries(data)
            .map(([field, msgs]) => {
              const label = this.internalSchema[field]?.label || field
              return `${label}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`
            })
            .join('\n')
          await Swal.fire('Oops!', messages || 'There were validation errors.', 'error')
        } else if (status === 403) {
          await Swal.fire('Forbidden', 'You do not have permission for this action.', 'error')
        } else {
          await Swal.fire('Oops!', 'Error saving the record.', 'error')
        }
      } finally {
        this.submitting = false
      }
    },

    cancelForm () {
      if (this.isModal) {
        this.$emit('cancel')
      } else {
        if (this.$router && this.$route.name) {
          this.$router.back()
        } else {
          this.$emit('cancel')
        }
      }
    }
  }
}
</script>

<style scoped>
.form-check-label {
  margin-left: 0.5rem;
}
</style>
