<template>
  <div>
    <!-- Main Modal -->
    <div class="modal fade" ref="eventModal" tabindex="-1" aria-labelledby="eventModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-xl">
        <div class="modal-content text-start">
          <div class="modal-header">
            <h5 class="modal-title" id="eventModalLabel">
              <span class="badge text-bg-secondary me-2 text-uppercase" v-if="is_draft">Draft</span>
              <span class="badge text-bg-success text-white me-2 text-uppercase" v-else>Event</span>
              {{ isEditing ?
                event_data?.id ? `Edit Event: ${event_data?.title}` : 'New Event' :
                event_data?.id ? `View Event: ${event_data?.title}`:'View Event'
              }} | Crew: {{crewTitle}}  </h5>
            <button type="button" class="btn-close" @click="hideModal"></button>
          </div>
          <div class="modal-body">
<!--            <div class="container-fluid">-->
              <div class="row">
                <!-- Form section -->
                <div class="col-lg-4 col-md-12 mb-3">
                  <form @submit.prevent="submitEvent">

                    <!-- Checkbox Absences Switch -->
                    <!-- Switch solo si no está en modo edición -->
                    <div  v-if="isEditing && this.hasPermission('appschedule.add_absencereason')" class="form-check form-switch mb-3">
                      <label class="form-check-label" for="absencesScheduled">Absences Scheduled</label>
                      <input
                        class="form-check-input"
                        type="checkbox"
                        id="absencesScheduled"
                        v-model="isAbsence"
                      />
                    </div>

                    <div class="mb-3">
                      <label for="eventDate" class="form-label">Date</label>
                      <input type="date" class="form-control" id="eventDate"
                            v-model="localFormData.date" :readonly="!isEditing"
                            placeholder="Select a date"/>
                    </div>

                    <!-- Select Absence Reason -->
                    <div  v-if="isAbsence" class="mb-3">
                      <label class="form-label">Absence Reason</label>
                      <v-select :disabled="!isEditing" class="bg-primary-subtle text-primary-emphasis"
                        :options="absenceReasons"
                        v-model="localFormData.absence_reason"
                        :reduce="reason => reason.id"
                        label="name"
                        placeholder="Select Absence Reason"
                      />
                    </div>

                    <!-- Work Account Selector -->
                    <div v-if="!isAbsence" class="mb-3">
                      <WorkAccountSelector
                        v-model="localFormData.work_account"
                        :disabled="!isEditing"
                        :required="!isAbsence"
                      />
                    </div>

                    <div class="mb-3">
                      <label class="form-label">Title</label>
                      <input type="text" class="form-control text-uppercase" v-model="localFormData.title"
                             @input="titleManuallyEdited = true" :readonly="!isEditing"
                             placeholder="Enter event title"/>
                    </div>
                    <div class="mb-3">
                      <label class="form-label">Description</label>
                      <input type="text" class="form-control" v-model="localFormData.description"
                             :readonly="!isEditing" placeholder="Enter event description"/>
                    </div>

                    <!-- Extended Service -->
                    <div  v-if="isEditing && this.hasPermission('appschedule.add_event')" class="form-check form-switch mb-3">
                      <input class="form-check-input" type="checkbox" id="eventExtendedService"
                             v-model="localFormData.extended_service" :disabled="!isEditing"/>
                      <label class="form-check-label" for="eventExtendedService">Extended
                        Service</label>
                    </div>

                    <div class="d-flex justify-content-end" v-if="this.hasPermission('appschedule.add_eventdraft') && canAccessEventActions">
                      <template v-if="isEditing">
                        <button type="button" class="btn btn-success text-white me-2" @click="submitEvent(true)"
                            v-if="this.hasPermission('appschedule.add_event')" :disabled="loading || offLine">
                            <span v-if="loading || offLine" class="spinner-border spinner-border-sm me-2" role="status"></span>
                            Save and Post
                        </button>
                        <button type="submit" class="btn btn-primary me-2"
                            v-if="!localFormData.event && this.hasPermission('appschedule.add_eventdraft')" :disabled="loading || offLine">
                            <span v-if="loading || offLine" class="spinner-border spinner-border-sm me-2" role="status"></span>
                            Save
                        </button>
                        <button type="button" class="btn btn-danger me-2" @click="deleteEvent"
                            v-if="!is_draft && localFormData.event && this.hasPermission('appschedule.add_event')" :disabled="loading || offLine">
                            <span v-if="loading || offLine" class="spinner-border spinner-border-sm me-2" role="status"></span>
                            Delete
                        </button>
                        <button type="button" class="btn btn-danger"
                            v-if="localFormData.id && this.hasPermission('appschedule.delete_eventdraft')"
                            @click="deleteEvent">Discard draft
                        </button>
                      </template>
                      <button v-if="!isEditing" type="button" class="btn btn-outline-secondary"
                              @click="toggleEdit">
                        <img src="@assets/img/icon-changelink.svg" alt="Edit" width="35"
                             height="20"/>
                      </button>
                    </div>
                    <div v-if="isEditing && offLine" class="col-12 mt-2 alert alert-danger" role="alert">
                      No internet connection!
                    </div>
                  </form>
                </div>

                <!-- Comments/Discussion -->
                <div class="col-lg-8 col-md-12">
                  <p v-if="!event_data" class="text-danger">No event selected</p>
                  <ScheduleHouseDiscussion v-if="event_data " :event="event_data"/>
                </div>
              </div>
<!--            </div>-->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {Modal} from 'bootstrap';
import VSelect from 'vue-select';
import axios from "axios";
import Swal from 'sweetalert2';
import dayjs from 'dayjs'
import ScheduleHouseDiscussion from './ScheduleHouseDiscussion.vue';
import WorkAccountSelector from '@components/transactions/WorkAccountSelector.vue';



export default {
  props: ['formData'],
  components: {
    VSelect,
    ScheduleHouseDiscussion,
    WorkAccountSelector
  },
  data() {
    return {
      localFormData: {
        id: null,
        crew: null,
        work_account: null,
        title: '',
        description: '',
        date: '',
        extended_service: false,
        absence_reason: '',
      },
      crewTitle: '',
      isEditing: false,
      modalInstance: null,
      titleManuallyEdited: false,
      is_draft: true,
      event_data: null,
      websocket: null,
      wsUrl: null,
      old_event: null,
      absenceReasons: [],
      canCreateEvent: false,
      isCoordinator: false,
      crewId: null,
      clickedCrewId: null,
      loading: false,
      offLine: false,
    };
  },
  computed: {
    isAbsence: {
      get() {
        return this.localFormData.is_absence === true;
      },
      set(value) {
        this.localFormData.is_absence = value;
      }
    },
    canAccessEventActions() {
      // Si NO tiene permiso, fuera.
      if (!this.canCreateEvent && !this.isCoordinator) {
        return false;
      }

      // Si NO es coordinador y su categoría no coincide, fuera.
      if (!this.isCoordinator && this.crewId !== this.clickedCrewId) {
        return false;
      }

      // Tiene acceso.
      return true;
    }

  },
  watch: {
    isAbsence(newVal) {
      if (newVal) {
        // Cuando se activó el modo ausencia
        this.localFormData.work_account = null;
        this.localFormData.title = '';
      } else {
        // Cuando se desactivó el modo ausencia
        this.localFormData.absence_reason = '';
        this.localFormData.title = '';
      }
    },
    'localFormData.absence_reason'(newVal) {
      if (this.isAbsence && newVal && !this.titleManuallyEdited) {
        this.autoFillTitle();
      }
    },
    'localFormData.work_account': 'autoFillTitle',

    canAccessEventActions(val) {
    console.debug('[CAA]', val, {
      canCreateEvent: this.canCreateEvent,
      isCoordinator: this.isCoordinator,
      crewId: this.crewId,
      clickedCrewId: this.clickedCrewId
    });
  }
  },
  methods: {
    selectText(event) {
      const input = event.target;
      input.select();
    },
    focusNext(event, nextField) {
      event.preventDefault();
      if (this.$refs[nextField]) {
        if (this.$refs[nextField].$el) {
          this.$refs[nextField].$el.querySelector('input, select').focus();
        } else {
          this.$refs[nextField].focus();
        }
      }
    },

    async autoFillTitle() {
      if (this.titleManuallyEdited) return;

      if (this.isAbsence) {
        const reason = this.absenceReasons.find(r => r.id === this.localFormData.absence_reason);
        this.localFormData.title = reason ? reason.name : 'Absence';
        return;
      }

      // Si hay work_account, obtener su título
      if (this.localFormData.work_account) {
        try {
          const response = await axios.get(`/api/work-accounts/${this.localFormData.work_account}/`);
          if (response.status === 200 && response.data.title) {
            this.localFormData.title = response.data.title.toUpperCase();
          }
        } catch (error) {
          console.error('Error loading work account title:', error);
          this.localFormData.title = '';
        }
      } else {
        this.localFormData.title = '';
      }
    },

    open(eventData, isEditMode = false) {
      this.old_event = null;
      if (eventData?.extendedProps?.end_dt){
        this.old_event = eventData?.extendedProps
      }
      // console.log("✔ ", eventData)
      this.titleManuallyEdited = eventData?.title
      this.localFormData = {
        id: null,
        crew: eventData?.crew,
        date: eventData?.date,
        end_dt: eventData?.extendedProps?.end_dt || null,
        work_account: eventData?.work_account || eventData?.extendedProps?.work_account || null,
        title: eventData?.title || '',
        description: eventData?.description || '',
        extended_service: eventData?.extended_service || false,
        is_absence: eventData?.isAbsence ?? eventData?.extendedProps?.is_absence ?? false,
        absence_reason: eventData?.absence_reason ?? eventData?.extendedProps?.absence_reason ?? null,
        _post: false,
      };

      this.crewTitle = eventData?.crewTitle;
      this.event_data = null

      if(eventData?.extendedProps?.event === undefined){
        this.is_draft = false
        this.localFormData.event = eventData?.extendedProps?.id || null;
        this.event_data = {
          id: eventData?.extendedProps?.id,
          title: eventData?.extendedProps?.title
        }
      } else {
        if (eventData?.extendedProps?.event) {
          this.event_data = {
            id: eventData?.extendedProps?.event,
            title: eventData?.extendedProps?.title
          }
        }
        this.is_draft = true
        this.localFormData.id = eventData?.extendedProps?.id;
        this.localFormData.event = eventData?.extendedProps?.event;
      }

      this.titleManuallyEdited = false;
      this.canCreateEvent = eventData?.canCreateEvent || false;
      this.isCoordinator = eventData?.isCoordinator || false;
      this.crewId = eventData?.crewId || null;
      // Fallback: si no viene clickedCrewId, usar el crew del evento
      this.clickedCrewId = eventData?.clickedCrewId || eventData?.crew || null;

      this.isEditing = isEditMode;
      this.showModal();
    },

    showModal() {
      const modalEl = this.$refs.eventModal;
      if (!this.modalInstance) {
        this.modalInstance = Modal.getOrCreateInstance(modalEl);
        modalEl.addEventListener('hidden.bs.modal', event => {
          this.event_data = null;
          // Asegurar que no hay elementos con foco dentro del modal oculto
          const focusedElement = modalEl.querySelector(':focus')
          if (focusedElement) {
            focusedElement.blur()
          }
        })
      }
      this.modalInstance.show();
      
      // Enfocar el primer campo después de que el modal se muestre
      this.$nextTick(() => {
        const firstInput = modalEl?.querySelector('input[type="date"], input[type="text"]')
        if (firstInput) {
          firstInput.focus()
        }
      })
    },

    hideModal() {
      console.log('hideModal')
      // Quitar el foco antes de ocultar el modal
      if (document.activeElement) {
        document.activeElement.blur()
      }
      if (this.modalInstance) {
        this.modalInstance.hide();
      }
    },

    toggleEdit() {
      this.isEditing = !this.isEditing;
    },

    async submitEvent(post = false, e) {
      this.loading = true;
      // Agrega este cálculo automático de end_dt
      if (!this.localFormData.end_dt && this.localFormData.date) {
        const start = new Date(this.localFormData.date);
        const end = new Date(start);
        end.setDate(start.getDate() + 1);
        this.localFormData.end_dt = end.toISOString().split('T')[0];
      }
      this.localFormData._post = post === true;
      // console.log('this.localFormData:::', this.localFormData)
      const id_exist = this.localFormData?.id >= 1;
      const url = id_exist ? `/api/schedule/${this.localFormData?.id}/` : '/api/schedule/';
      const axios_method = id_exist ? axios.put : axios.post;

      // Ajustar end_dt si la fecha fue modificada
      if (this.old_event) {
        const old_start = dayjs(this.old_event.date);
        const new_start = dayjs(this.localFormData.date);
        if (!old_start.isSame(new_start)) {
          const old_end = dayjs(this.old_event.end_dt);
          const duration = old_end.diff(old_start, 'days');
          const new_end = new_start.add(duration, 'days');
          this.localFormData.end_dt = new_end.format('YYYY-MM-DD');
        }
      }

      // Validación preventiva (solo si no es una ausencia)
      if (!this.isAbsence) {
        if (!this.localFormData.work_account) {
          Swal.fire('Missing Fields', 'Please select a Work Account before saving.', 'warning');
          this.loading = false;
          return;
        }
      }

      try {
        const resp = await axios_method(url, this.localFormData);
        this.loading = false;
        if ([200, 201].includes(resp.status)) {
          this.$emit('save-event', true);
          this.hideModal();
        }
      } catch (e) {
        if (e.response.status === 400) {
          const err = e.response.data;
          let msg = [];
          if (err.hasOwnProperty('non_field_errors')) {
            if (Array.isArray(err.non_field_errors) && err.non_field_errors.includes('Duplicate Event Detected')) {
              if (this.isAbsence) {
                console.warn('🔁 Skipping duplicate validation for absence event.');
              } else {
                Swal.fire(
                  'Duplicate Event Detected',
                  'An event with the same Lot and Community or Address already exists in this Crew Category.',
                  'error'
                );
                this.loading = false;
                return;
              }
            } else {
              Swal.fire('Error Detected', err.non_field_errors.join(', '), 'error');
              return;
            }
          }

          for (const item in err) {
            msg.push(`${item}: ${err[item].join(', ')}`);
          }

          Swal.fire('Validation Error', msg.join(', '), 'error');
          return;
        }

        Swal.fire('Error Detected', 'An error occurred while saving the data.', 'error');
        this.loading = false;
      }
    },

    async deleteApi() {
      this.loading = true;
      try {
        const url = !this.is_draft ? `/api/schedule/${this.localFormData.event}/?deleted=true` : `/api/schedule/${this.localFormData.id}/`
        await axios.delete(url)
        this.$emit('delete-event', this.localFormData.id);
        this.hideModal();
        this.notifyToastSuccess('Event deleted successfully.');
      } catch (e) {
        console.error(e)
      }
      this.loading = false;
    },

    async deleteEvent() {
      if (this.is_draft){
        await this.deleteApi()
        return
      }
      const title = `Are you sure you want to delete this event${this.is_draft ? ' draft': ''}?`
      const text = this.is_draft ? 'This action cannot be undone.' : 'This event will no longer be public'
      this.confirmDelete(
          title,
          text,
          this.deleteApi
      );
    },


    async loadAbsenceReasons() {
      try {
        const response = await axios.get('/api/absence-reasons/');
        this.absenceReasons = response.data;
      } catch (error) {
        console.error('Error loading absence reasons:', error);
        this.notifyError('Failed to load absence reasons');
      }
    },
    updateOnlineStatus() {
      // 'navigator.onLine' es una propiedad booleana que indica el estado de la conexión
      this.offLine = !navigator.onLine;
    }
  },

  mounted() {
    this.offLine = !navigator.onLine;
    this.loadAbsenceReasons()

    window.addEventListener('online', this.updateOnlineStatus);
    window.addEventListener('offline', this.updateOnlineStatus);
  },
  beforeUnmount() {
    window.removeEventListener('online', this.updateOnlineStatus);
    window.removeEventListener('offline', this.updateOnlineStatus);
  },

};
</script>
