<template>
  <div class="container-fluid">
    <div class="row">
      <!-- Sidebar de eventos -->
      <div class="col-md-5 col-lg-4 col-xl-3 border-end p-3 bg-light">
        <div class="row pb-2" ref="leftHeader">
          <div class="col-3 text-start"><h3 class="mb-0">Jobs</h3></div>
          <div class="col-9 text-end">
            <div class="input-group mb-3">
              <input
                type="text"
                class="form-control"
                placeholder="Search event"
                v-model="search"
                @keydown.enter="getEvents" />
              <button class="btn btn-outline-secondary" type="button" @click="clearSearch">
                <i class="bi bi-x-lg" style="font-size: 0.785rem"></i>
              </button>
              <button class="btn btn-primary" type="button" @click="getEvents">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
        </div>
        <ul class="list-group events-list" ref="events" :style="eventsMaxHeightStyle">
          <li
            v-for="event in events"
            :key="event.id"
            @click="selectEvent(event)"
            class="list-group-item list-group-item-action"
            :class="{ active: selectedEvent && selectedEvent.id === event.id }">
            <!-- Título alineado a la izquierda -->
            <div class="w-100 d-flex justify-content-between align-items-center">
              <span class="fw-semibold text-truncate" style="font-size: 0.87rem">
                {{ event.title }}
              </span>
              <span class="badge bg-secondary text-capitalize ms-2" style="font-size: 0.65rem">
                {{ event.crew_category }}
              </span>
            </div>
            <!-- Detalles secundarios con espacio horizontal -->
            <small class="text-muted d-flex align-items-center justify-content-between overflow-hidden"
              style="font-size: 0.75rem; gap: 0.75rem">
              <span class="text-truncate" style="max-width: 25%">
                {{ event.crew_title }}
              </span>
              <span v-if="event.extended_service" class="badge text-bg-danger text-truncate" style="max-width: 19%">
                Ext. Service
              </span>
              <span class="text-truncate" style="max-width: 25%">
                {{ event.date }}
              </span>
              <span
                v-if="unreadMessages[event.id]"
                class="d-flex align-items-center text-truncate"
                style="max-width: 25%">
                <img :src="envelopeIcon" alt="Messages" width="16" height="16" class="me-1 flex-shrink-0" />
                <span class="badge rounded-pill bg-warning">
                  {{ unreadMessages[event.id] }}
                </span>
              </span>
            </small>
          </li>
        </ul>
        <div class="row">
          <div class="col-12 mt-2">
            <button
              type="button"
              class="btn btn-primary btn-sm me-2"
              :disabled="!previous || loading"
              @click="handlePrevious">
              Previous
            </button>
            <button type="button" class="btn btn-primary btn-sm" :disabled="!next || loading" @click="handleNext">
              Next
            </button>
          </div>
        </div>
      </div>

      <!-- Chat window -->
      <div class="col-md-7 col-lg-8 col-xl-9 d-flex flex-column p-2" :style="contentMaxHeightStyle">
        <div v-if="selectedEvent" class="chat-window border rounded p-2 d-flex flex-column flex-grow-1">
          <ScheduleHouseDiscussion v-if="selectedEvent" :event="selectedEvent" />
        </div>
        <div class="d-flex align-items-center h-100" v-if="loading">
          <h2 class="text-center w-100">Preparing event...</h2>
        </div>
        <div class="d-flex align-items-center h-100" v-if="!loading && !selectedEvent">
          <h2 class="text-center w-100">Please select an event first.</h2>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import '@assets/css/base.css';
  import axios from 'axios';
  import dayjs from 'dayjs';
  import ScheduleHouseDiscussion from '@schedule/ScheduleHouseDiscussion.vue';
  import { useAuthStore } from '@stores/auth';
  import { useChatStore } from '@/stores/chatStore';
  import SearchIcon from '@components/icons/searchIcon.vue';
  import envelopeIcon from '@/assets/img/envelope-arrow-up.svg';

  export default {
    components: { SearchIcon, ScheduleHouseDiscussion },
    data() {
      return {
        envelopeIcon,
        chatStore: useChatStore(),
        events: [],
        next: null,
        previous: null,
        page: 1,
        selectedEvent: null,
        search: '',
        duration: null,
        loading: false,
        leftHeaderHeight: 0,
        mainNavHeight: 0,
        mainFooterHeight: 0,
        unreadMessages: {},
        wsNotify: null,
        userId: null,
      };
    },
    computed: {
      eventsMaxHeightStyle() {
        const calculatedHeight = `calc(100vh - ${this.leftHeaderHeight}px - ${this.mainNavHeight}px - ${this.mainFooterHeight}px)`;
        return {
          height: calculatedHeight,
          minHeight: '400px',
          overflowY: 'auto',
        };
      },
      contentMaxHeightStyle() {
        const calculatedHeight = `calc(100vh - ${this.mainNavHeight}px - ${this.mainFooterHeight}px)`;
        return {
          minHeight: calculatedHeight,
          overflowY: 'auto',
        };
      },
    },
    async mounted() {
      const data = await this.getAuthenticatedUser();
      const authStore = useAuthStore();
      authStore.setUser(data);
      this.userId = data.id;
      this.connectUnreadWebSocket();

      this.updateHeights();
      this.getEvents();
    },
    beforeUnmount() {
      this.disconnectUnreadWebSocket();
    },
    methods: {
      async getEvents(event, page = 1) {
        this.page = page;
        const currentSelectedId = this.selectedEvent ? this.selectedEvent.id : null;

        try {
          const url_get = `/api/my-events/?page=${this.page}${this.search.trim() ? '&search=' + this.search : ''}`;
          const response = await axios.get(url_get);

          if (response.status === 200) {
            this.events = response.data.results;
            this.next = response.data.next;
            this.previous = response.data.previous;
            console.log('this.events: ', this.events);

            // Carga los mensajes no leídos
            const unreadRes = await axios.get('/api/unread-chat-counts/');
            this.unreadMessages = unreadRes.data;

            // Restaurar el evento seleccionado si sigue visible
            if (currentSelectedId) {
              const stillVisible = this.events.find(e => e.id === currentSelectedId);
              if (stillVisible) {
                this.selectedEvent = stillVisible;
              }
            }
          }
        } catch (error) {
          console.error('Error fetching event data:', error);
        }
      },
      async fetchOnlyEvents(page = 1) {
        try {
          const url_get = `/api/my-events/?page=${page}${this.search.trim() ? '&search=' + this.search : ''}`;
          const response = await axios.get(url_get);

          if (response.status === 200) {
            this.events = response.data.results;
            this.next = response.data.next;
            this.previous = response.data.previous;

            const unreadRes = await axios.get('/api/unread-chat-counts/');
            this.unreadMessages = unreadRes.data;
          }
        } catch (error) {
          console.error('Error refreshing event list silently:', error);
        }
      },
      async mark_as_read(event_id){
        try {
          await axios.post(`/api/mark-chat-read/${event_id}/`);
          this.unreadMessages[event_id] = 0;
          await this.chatStore.fetchUnreadEvents();
        } catch (error) {
          console.warn('Failed to mark chat as read:', error);
        }
      },
      async selectEvent(event) {
        this.selectedEvent = null;
        this.loading = true;

        // Marcar como leído
        this.mark_as_read(event.id)

        setTimeout(() => {
          this.loading = false;
          this.selectedEvent = event;
        }, 500);
      },
      updateHeights() {
        if (this.$refs.leftHeader) {
          this.leftHeaderHeight = this.$refs.leftHeader.offsetHeight;
        }
        const nav = document.querySelector('nav');
        if (nav) {
          this.mainNavHeight = nav.offsetHeight;
        }
        const footer = document.querySelector('footer');
        if (footer) {
          this.mainFooterHeight = footer.offsetHeight;
        }
      },
      handleNext() {
        this.getEvents(null, this.page + 1);
      },
      handlePrevious() {
        this.getEvents(null, this.page - 1);
      },
      connectUnreadWebSocket() {
        if (!this.userId) return;

        this.wsNotify = new WebSocket(`${process.env.VUE_APP_WS_BASE_URL}ws/schedule/unread/user/${this.userId}/`);

        this.wsNotify.onopen = () => {
          console.log('[WS] Connected to unread counter for user', this.userId);
        };

        this.wsNotify.onmessage = event => {
          const data = JSON.parse(event.data);

          if (data.type === 'unread.updated') {
            const { event_id, count, user_id } = data;

            // If open chat not add message to counter
            if (this.selectedEvent === null || this.selectedEvent.id !== event_id){
              this.unreadMessages[event_id] = count
            } else {
              this.mark_as_read(event_id)
            }

            //  OAHP. Nuevo mensaje, Recargar la primera página desde el backend
            // ya que el backend ordena por `unread_count` primero
            this.fetchOnlyEvents(1); // NO resetea selectedEvent

            // Actualizar contador global
            this.chatStore.fetchUnreadEvents();
          }
        };

        this.wsNotify.onclose = () => {
          console.warn('[WS] Unread socket closed');
        };
      },
      disconnectUnreadWebSocket() {
        if (this.wsNotify) {
          this.wsNotify.close();
          this.wsNotify = null;
        }
      },
      async getAuthenticatedUser() {
        try {
          const response = await axios.get('/api/user_detail/');
          return response.data;
        } catch (error) {
          console.error('Error fetching authenticated user:', error);
          return {};
        }
      },
      clearSearch() {
        this.search = '';
        this.getEvents(); // para recargar la lista sin filtro
      },
    },
  };
</script>
