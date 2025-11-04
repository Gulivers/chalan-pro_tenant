<template>
  <div class="calendar-container">
    <div class="d-flex flex-column flex-md-row align-items-stretch align-items-md-center justify-content-md-end gap-2 py-2">
      <div v-if="categoryTotals.length">
        <div class="text-center me-5">
          <strong>Weekly Totals:</strong>
          <span v-for="(item, index) in categoryTotals" :key="index" class="badge bg-secondary mx-1">
            {{ removeEmojis(item.crew__category__name) }}: {{ item.total }}
          </span>
        </div>
      </div>
      <div class="me-2" v-if="hasPermission('appschedule.view_event')">
        <button class="btn btn-outline-success me-2 btn-sm" @click="downloadScheduleExcel">
          <img src="@/assets/img/microsoft-excel-icon.svg" alt="Excel" width="25" class="me-1" />
          Excel Schedule
        </button>
        <button class="btn btn-outline-dark btn-sm" @click="generateSchedulePDF">
          📄 Print Schedule PDF
        </button>
      </div>
      <div v-if="hasPermission('appschedule.add_event')">
        <button
          class="btn btn-warning me-3 btn-sm"
          :disabled="publishing || !showBntPublishAll"
          :aria-busy="publishing"
          :title="publishing ? 'Publishing drafts…' : (showBntPublishAll ? 'Publish all drafts in view' : 'No drafts to publish')"
          @click="publishAllDrafts">
          <span v-if="publishing" class="spinner-border spinner-border-sm me-2" role="status"></span>
          {{ publishing ? 'Publishing...' : '📢 Publish All Drafts' }}
        </button>
      </div>

      <div class="input-group input-group-sm me-2" style="max-width: 280px;">
        <span class="input-group-text">Search: </span>
        <input type="text" class="form-control form-control-sm" placeholder="Search here 🔍" v-model="search">
        <!--<button class="btn btn-outline-primary btn-sm" type="button">
          <img src="@assets/img/search.svg" alt="Search" width="20" height="20" />
        </button>-->
      </div>
    </div>
    <FullCalendar ref="calendarRef" :options="calendarOptions" v-if="showFullCalendar"/>
    <EventModal ref="eventModal" :formData="formData" @save-event="handleSaveEvent"/>
  </div>
</template>

<script>
import FullCalendar from '@fullcalendar/vue3'
import interactionPlugin from '@fullcalendar/interaction'
import resourceTimelinePlugin from '@fullcalendar/resource-timeline'
import '@assets/css/schedule.css';
import '@assets/css/base.css';
import EventModal from './ScheduleEventModal.vue';
import axios from 'axios';
import dayjs from 'dayjs'
import localizedFormat from 'dayjs/plugin/localizedFormat'
import Swal from "sweetalert2";
dayjs.extend(localizedFormat)
import {useAuthStore} from '@stores/auth'
import { openPdf } from '@helpers';
import SearchIcon from "@components/icons/searchIcon.vue";

// npm install @fullcalendar/vue3 @fullcalendar/interaction @fullcalendar/resource-timeline

export default {
  components: {SearchIcon, FullCalendar, EventModal},
  data() {
    return {
      search: '',
      calendar_start: null,
      calendar_end: null,
      calendarRef: null,
      resizeObserver: null,
      resources: [],
      events: [],
      showModal: false,
      showFullCalendar: false,
      formData: {
        date: '',
        job: '',
        lot: '',
        title: '',
        description: '',
        extendedService: false
      },
      userId: null, // _OAHP
      publishing: false,   // OAHO400
      categoryTotals: [],
      // filteredEvents: [],
      websocket: null,
      wsUrl: `${process.env.VUE_APP_WS_BASE_URL}ws/calendar-updates/`,
      // categoryOrder: ['Rough', 'Roug-hWaitList', 'Trim', 'TrimWaitList', 'Others', 'Hourly'],
      initialCalendarOptions: {
        plugins: [interactionPlugin, resourceTimelinePlugin],
        initialView: 'resourceTimelineWeek',
        firstDay: 1, // Lunes como primer día de la semana
        headerToolbar: {
          left: 'prev,next today',
          center: 'title',
          right: 'resourceTimelineDay,resourceTimelineWeek'
        },
        editable: false,
        eventResizableFromStart: false,
        droppable: false,
        resourceAreaHeaderContent: 'Crew',
        resourceAreaWidth: '15%',
        eventMinHeight: 90,  // Altura mínima para asegurar visibilidad
        // slotHeight: null,
        height: 'auto', // Establece la altura como auto
        slotLabelInterval: {days: 1},
        slotDuration: {days: 1},
        slotLabelFormat: {weekday: 'long', month: 'short', day: 'numeric'},
        resourceGroupField: 'category',
        // resourceOrder: 'title',
        resourceOrder: 'category',
        resources: [],
        // events: [],
        eventDrop:()=>{return false},
        eventResize: ()=>{return false}, // Manejo para cuando se cambia el tamaño de un evento
        dateClick: ()=>{return false},
        eventClick: this.handleEventClick,
        datesSet: this.handleDatesSet,
        eventContent: function (arg) {
          const event_date = dayjs(arg.event.extendedProps.updated_at)
          const isAbsence = arg.event.extendedProps?.is_absence;
          let event_class = 'p-1 bg-light'
          if (arg.event.extendedProps?.deleted !== undefined) { // is_event
            event_class = `p-1 ${!arg.event.extendedProps?.deleted ? 'bg-success': 'bg-danger'} bg-opacity-25`
          }
          if (isAbsence) {
            event_class = 'p-1 bg-success-subtle opacity-75" border border-success-subtle '; // Azulito pa’ las ausencias
          }
          return {
            html: `<div class="${event_class}">
                     <span class="text-capitalize" style="font-size: 0.9rem"> ${isAbsence ? '🛑 ' : ''}${arg.event.title}</span>
                     <div class="mb-1 text-muted text-break" style="font-size: 0.75rem">${arg.event.extendedProps.description || ''}</div>
                     ${arg.event.extendedProps?.extended_service ? '<div class="text-end pb-1"><span class="badge text-bg-danger bg-danger">Ext. Service</span></div>': ''}
                     <div class="hstack">
                         <small class="text-black-50 " style="font-size: 0.7rem">${event_date.format('lll')}</small>
                     </div>
                   </div>`
          };
        }
      }
    }
  },
  computed: {
    filteredEvents() {
      const searchTerm = this.search.toLowerCase();
      if (searchTerm.trim().length > 0) {
        return this.events.filter(event => {
          return (
              event.extendedProps.crew_title?.toLowerCase().includes(searchTerm) ||
              event.extendedProps.address?.toLowerCase().includes(searchTerm) ||
              event.extendedProps.description?.toLowerCase().includes(searchTerm) ||
              event.extendedProps.title?.toLowerCase().includes(searchTerm)
          );
        });
      } else {
        return this.events
      }
    },
    showBntPublishAll() {
      return this.events.some(e => e?.extendedProps?.event !== undefined)
    },
    calendarOptions(){
      return {
        ...this.initialCalendarOptions,
        events: this.filteredEvents
      }
    }
  },
  async mounted() {
      const data = await this.getAuthenticatedUser();
      const authStore = useAuthStore();
      authStore.setUser(data);
      this.userId = data.id;
      this.getCrews();
      this.connectWebSocket();
      this.updateCalendarPermissions();
  },
  beforeUnmount() {
    this.disconnectWebSocket();
    this.disconnectResizeObserver();
  },

  methods: {
    reSizeCalendar() {
      const resourceRows = document.querySelectorAll('.fc-resource-cell');
      const eventRows = document.querySelectorAll('.fc-datagrid-cell');

      // Observador para ajustar la altura
      this.resizeObserver = new ResizeObserver(entries => {
        entries.forEach((entry, index) => {
          if (resourceRows[index]) {
            resourceRows[index].style.height = `${entry.contentRect.height}px`;
          }
        });
      });

      // Aplicar observador a cada fila de evento
      eventRows.forEach(row => {
        this.resizeObserver.observe(row);
      });
    },

    async updateCalendarPermissions() {
        try {
          const { data } = await axios.get('/api/crew/supervisor/');
          const crewId = data.crew?.id;
          console.log('✔ Permisos cargados desde API directo:', data);

          this.userCrewCategoryName = data.crew?.category?.name || null;
          this.can_create_event = data.can_create_event;
          this.is_coordinator = data.is_coordinator;
          this.crewId = crewId;
          this.crewName = data.crew?.name;

          if (this.hasPermission('appschedule.add_eventdraft') || (data.can_create_event && !data.is_coordinator)) {
            this.initialCalendarOptions.editable = true;
            this.initialCalendarOptions.eventResizableFromStart = true;
            this.initialCalendarOptions.droppable = true;
            this.initialCalendarOptions.eventDrop = this.handleEventDrop;
            this.initialCalendarOptions.eventResize = this.handleEventDrop; // Manejo para cuando se cambia el tamaño de un evento
            this.initialCalendarOptions.dateClick = this.handleDateClick;
          }
        } catch (error) {
          console.error('🚫 Error al cargar permisos de supervisor:', error);
        }
    },

    handleDatesSet(info) {
      // Esta función se ejecuta cuando cambia la vista (mes, semana, día, etc.)
      const startDate = dayjs(info.view.currentStart).format('YYYY-MM-DD');
      const endDate = dayjs(info.view.currentEnd).format('YYYY-MM-DD');
      // console.log('Rango de fechas actual (Options API), aqui debemos cargar los eventos que están en ese rango de fechas:', startDate, ' - ', endDate);

      if (startDate !== this.calendar_start && endDate !== this.calendar_end){
        this.calendar_start = startDate
        this.calendar_end = endDate
        this.getEvents();
      }

      // Aquí podrías llamar a tu función para cargar los eventos
      // this.fetchEvents(startDate, endDate);
    },

    async getCrews() {
      this.showFullCalendar = false
      try {
        const response = await axios.get('/crews/');
        if (response.status === 200) {
          this.resources = response.data.filter(item => item.category_name).map((item) => ({
            id: item.id,
            title: item.name.toUpperCase(),
            category: item.category_name.toUpperCase(),
          }))
          this.initialCalendarOptions.resources = this.resources
        }
        this.showFullCalendar = true
      } catch (error) {
        console.error('Error fetching crews data:', error);
      }
    },

    async getEvents() {
      try {
        const url_get = `/api/schedule-list/?start_at=${this.calendar_start}&end_at=${this.calendar_end}`
        const response = await axios.get(url_get);
        if (response.status === 200) {
          this.events = []
          this.categoryTotals = response.data.category_totals || []
          response.data?.events?.forEach((item) => {this.events.push({
            id: 'event_id_' + String(item.id),
            resourceId: item.crew,
            start: item.date,
            end: item.end_dt,
            title: item.title,
            extendedProps: item
          })})
          response.data?.drafts?.forEach((item) => {this.events.push({
            id: 'draft_id_' + String(item.id),
            resourceId: item.crew,
            start: item.date,
            end: item.end_dt,
            title: item.title,
            extendedProps: item
          })})
          this.$nextTick(()=>{
            this.reSizeCalendar()
          })
        }
      } catch (error) {
        console.error('Error fetching chart data:', error);
      }
    },
    async updateEvent(url, payload, method='patch') {
      const axios_method = method==='patch' ? axios.patch: axios.post
      const resp = await axios_method(url, payload)
    },

    handleDateClick(info) {
        try {
          const isCoordinator = this.is_coordinator;
          const canCreateEvent = this.can_create_event;
          const crewCategoryName = this.userCrewCategoryName?.toLowerCase(); // ej. "slabs"
          const clickedCategoryName = this.resources.find(r => r.id == info.resource.id)?.category?.toLowerCase();
          const clickedCrewId = parseInt(info.resource.id);
          const crewId = this.crewId;
          const crewName = this.crewName;
          this.clickedCrewId = clickedCrewId;

          //  No tiene permiso para crear
          if (!canCreateEvent && !isCoordinator) {
            Swal.fire('Permission Denied', 'You do not have permission to create events.', 'error');
            return;
          }

          // Si NO es coordinador, validar categoría
          if (!isCoordinator && crewId !== clickedCrewId) {
            Swal.fire(
              'Permission Denied',
              // `You can only create events for your category (${crewCategoryName?.toUpperCase() || 'UNKNOWN'}).`,
              `You can only create events for your category (${
                crewCategoryName?.toUpperCase() || 'UNKNOWN'
              }) with your assigned crew (${crewName || 'No Crew'}).`,
              'warning'
            );
            return;
          }

          // Abre el modal si todo es válido
          this.$refs.eventModal.open(
            {
              date: info.dateStr,
              title: '',
              description: '',
              work_account: null,
              crew: parseInt(info.resource.id),
              crewTitle: info.resource.title,
              extended_service: false,
              canCreateEvent: this.can_create_event,
              clickedCrewId: this.clickedCrewId,
              crewId: this.crewId,
              isCoordinator: this.is_coordinator,
            },
            true
          );
        } catch (error) {
          console.error('💥 Error inesperado en handleDateClick:', error);
          Swal.fire('Oops!', 'Something went wrong while trying to open the event modal.', 'error');
        }
    },

    handleEventClick(info) {
      // console.log("Clicked event data:", info.event);
      // console.log("Clicked event data:", info.event.getResources()[0].id);
      const clickedCrewId = parseInt(info.event.getResources()[0].id)
      this.clickedCrewId = clickedCrewId
      this.$refs.eventModal.open({
        id: parseInt(info.event.extendedProps?.id),
        title: info.event.title,
        date: info.event.startStr,
        description: info.event.extendedProps?.description,
        work_account: info.event.extendedProps?.work_account || null,
        crew: info.event.getResources()[0].id,
        crewTitle: info.event.getResources()[0].title,
        extended_service: info.event.extendedProps?.extended_service,
        isAbsence: info.event.extendedProps?.is_absence || false,
        absence_reason: info.event.extendedProps?.absence_reason || null,
        extendedProps: info.event.extendedProps,
        canCreateEvent: this.can_create_event,
        clickedCrewId: this.clickedCrewId,
        crewId: this.crewId,
        isCoordinator: this.is_coordinator,
      }, false);
    },

    async handleEventDrop(info) {
      const isCoordinator = this.is_coordinator;
      const crewId = this.crewId;
      const clickedCrewId = parseInt(info.event.getResources()[0].id);
      const crewName = this.crewName;

      console.log('🎯 Drag Event Info:', {
        isCoordinator,
        crewId,
        clickedCrewId,
        eventTitle: info.event.title,
      });

      // Bloquea si NO es coordinador y está intentando mover otra cuadrilla
      if (!isCoordinator && crewId !== clickedCrewId) {
        Swal.fire(
          'Permission Denied',
          `You can only move events of your assigned crew (${crewName || 'Unknown Crew'}).`,
          'warning'
        );
        info.revert(); // Devuelve el evento a su posición original
        return;
      }
      // console.log(info.event.extendedProps)
      // console.log(`Moved ${info.event.title} to ${info.event.startStr} under ${info.event.getResources()[0].title}`);
      const is_draft = info.event.extendedProps?.event !== undefined
      try {
        if (is_draft) {
         //const payload = {
         //  date: info.event.startStr,
         //  end_dt: info.event.endStr,
         //  crew: info.event.getResources()[0].id
          //}
          const payload = {
            title: info.event.title,
            description: info.event.extendedProps?.description,
            date: info.event.startStr,
            end_dt: info.event.endStr,
            work_account: info.event.extendedProps?.work_account || null,
            crew: info.event.getResources()[0].id,
            extended_service: info.event.extendedProps?.extended_service,
            is_absence: info.event.extendedProps?.is_absence || false
          };
          // console.log('📍 PATCH Draft Payload:', payload)
          await this.updateEvent(`/api/schedule/${info.event.extendedProps?.id}/`, payload)
        } else {
          const payload = {...info.event.extendedProps}
          payload.id = null
          payload.event = info.event.extendedProps?.id
          payload.date = info.event.startStr
          payload.end_dt = info.event.endStr
          payload.crew = info.event.getResources()[0].id
          payload._post = true
          payload._deleted = info.event.extendedProps?.deleted
          await this.updateEvent(`/api/schedule/`, payload, 'post')
        }
      } catch (e) {
        if (e.response.status === 400){
          const err = e.response.data
          if (err.hasOwnProperty('non_field_errors')) {
            if (Array.isArray(err.non_field_errors) && err.non_field_errors.includes('Duplicate Event Detected')) {
              Swal.fire('Duplicate Event Detected', 'An event with the same title (Lot, Community, or Address) already exists in this Crew Category.', 'error')
              return
            }
          }
          Swal.fire(e.response.statusText, e.message,  'error')
        }
        if (e.response.status === 403){
          const err = e.response.data
          Swal.fire('Action not allowed', 'You do not have permission to publish events', 'error')
          return
        }
      }
    },

    handleSaveEvent(eventData) {
      // console.log('Event saved:', eventData);
      this.getEvents()
    },

    connectWebSocket() {
      // console.log('connectWebSocket:: ', this.wsUrl)
      this.websocket = new WebSocket(this.wsUrl);

      this.websocket.onopen = () => {
        console.log('Conexión WebSocket establecida.');
      };

      this.websocket.onmessage = (event) => {
        console.log('websocket.onmessage:: ', event);
        this.getEvents()
        // const data = JSON.parse(event.data);
        // this.messages.push(data.message);
      };

      this.websocket.onclose = () => {
        console.log('Conexión WebSocket cerrada.');
        // Opcional: Intenta reconectar después de un tiempo
        // setTimeout(this.connectWebSocket, 3000);
      };

      this.websocket.onerror = (error) => {
        console.error('Error de WebSocket:', error);
      };
    },

    disconnectWebSocket() {
      if (this.websocket) {
        this.websocket.close();
        this.websocket = null;
      }
    },

    disconnectResizeObserver() {
      if (this.resizeObserver) {
        this.resizeObserver.disconnect();
        this.resizeObserver = null;
      }
    },

    async publishAllDrafts() {
      if (!this.showBntPublishAll || this.publishing) return
      this.publishing = true

      // Watchdog por si la request queda colgada
      const watchdog = setTimeout(() => {
        if (this.publishing) {
          this.publishing = false
          if (typeof this.notifyToastError === 'function') {
            this.notifyToastError('Publish timed out after 30s. Please try again.')
          }
        }
      }, 30000)

      try {
        await axios.post(
          '/api/schedule/publish_drafts/',
          {
            start_date: this.calendar_start,
            end_date: this.calendar_end,
          },
          { timeout: 30000 } // ✅ NEW: timeout duro en axios
        )

        if (typeof this.getEvents === 'function') {
          await this.getEvents()
        }

        if (typeof this.notifyToastSuccess === 'function') {
          this.notifyToastSuccess('Drafts published successfully.')
        }
      } catch (e) {
        console.error(e)
        const msg = e?.response?.data?.error || e?.message || 'Error while publishing drafts.'
        if (typeof this.notifyToastError === 'function') {
          this.notifyToastError(msg)
        }
      } finally {
        clearTimeout(watchdog)
        this.publishing = false
      }
    },
    
    async generateSchedulePDF() {
      try {
        const url = `/api/schedule-report/?start_at=${this.calendar_start}&end_at=${this.calendar_end}`;
        // console.log('📡 Sending PDF request to:', url);

        const response = await axios.get(url);

        if (response.status === 200) {
          console.log('✅ PDF response received:', response.data);
          openPdf(response.data);
        }
      } catch (error) {
        console.error('❌ Error downloading schedule PDF:', error);
        Swal.fire("Error", "Could not generate the PDF.", "error");
      }
    },
    async downloadScheduleExcel() {
      const url = `/api/schedule-excel/?start_at=${this.calendar_start}&end_at=${this.calendar_end}`;
      // console.log('✌ Sending PDF request to:', url);
      try {
        const response = await axios.get(url, { responseType: 'blob' });
        const blob = new Blob([response.data], { type: response.headers['content-type'] });
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);

        // Resto 1 día visualmente para el nombre del archivo
        const endDate = new Date(this.calendar_end);
        endDate.setDate(endDate.getDate() - 1);
        const formattedEnd = endDate.toISOString().split('T')[0];

        link.download = `schedule-${this.calendar_start}_to_${formattedEnd}.xlsx`;
        link.click();
      } catch (err) {
        Swal.fire("Error", "Could not download the Excel file.", "error");
        console.error("Excel Download Error:", err);
      }
    },
    removeEmojis(text) {
      // Elimina numeritos emoji (1️⃣, 2️⃣, etc.)
      text = text.replace(/\d\uFE0F\u20E3/g, '');
      // Elimina otros emojis y símbolos combinados
      return text.replace(
        /([\u2700-\u27BF]|[\uE000-\uF8FF]|[\uD83C-\uDBFF\uDC00-\uDFFF]+|[\uFE00-\uFE0F]|\u200D)/g,
        ''
      ).trim();
    }
  },
}
</script>

<style scoped>
/* 
 ::v-deep .fc-datagrid-cell-main {
    font-weight: bold;
  } 
  */
</style>
