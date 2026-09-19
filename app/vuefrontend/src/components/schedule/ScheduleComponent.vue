<template>
  <JRPage>
    <JRPageHeader
      title="Schedule"
      description="Plan crew work by day or week. Search, jump to a date, or publish drafts in view." />

    <JRToolbar>
      <template #start>
        <div class="jr-schedule__search">
          <label class="jr-sr-only" for="schedule-search">Search schedule</label>
          <span class="jr-schedule__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="schedule-search"
            v-model="search"
            type="search"
            placeholder="Search crew, address, title…"
            autocomplete="off"
            :spellcheck="false"
            enterkeyhint="search" />
        </div>
      </template>

      <template v-if="categoryTotals.length" #stats>
        <div class="jr-schedule__totals" aria-live="polite">
          <span class="jr-schedule__totals-label">Weekly Totals</span>
          <JRBadge
            v-for="(item, index) in categoryTotals"
            :key="index"
            :value="`${removeEmojis(item.crew__category__name)}: ${item.total}`"
            severity="secondary" />
        </div>
      </template>

      <template #actions>
        <div class="jr-schedule__jump">
          <label class="jr-sr-only" for="schedule-jump-date">Go to date</label>
          <JRDatePicker
            inputId="schedule-jump-date"
            :model-value="jumpDate"
            placeholder="Go to date"
            :show-button-bar="true"
            @update:model-value="onJumpDate" />
        </div>

        <JRButton
          v-if="hasPermission('appschedule.view_event')"
          type="button"
          variant="ghost"
          size="sm"
          @click="downloadScheduleExcel">
          <FileExcel
            class="jr-schedule__excel-icon"
            aria-hidden="true" />
          Excel
        </JRButton>

        <JRButton
          v-if="hasPermission('appschedule.view_event')"
          type="button"
          variant="ghost"
          size="sm"
          @click="generateSchedulePDF">
          <FilePdf
            class="jr-schedule__pdf-icon"
            aria-hidden="true" />
          Print PDF
        </JRButton>

        <JRButton
          v-if="hasPermission('appschedule.add_event')"
          type="button"
          :variant="showBntPublishAll ? 'primary' : 'secondary'"
          size="sm"
          :disabled="publishing || !showBntPublishAll"
          :aria-busy="publishing ? 'true' : 'false'"
          :title="
            publishing
              ? 'Publishing drafts…'
              : showBntPublishAll
                ? 'Publish all drafts in view'
                : 'No drafts to publish'
          "
          @click="publishAllDrafts">
          {{ publishing ? "Publishing…" : "Publish All Drafts" }}
        </JRButton>
      </template>
    </JRToolbar>

    <div class="jr-schedule">
      <p
        v-if="!showFullCalendar"
        class="jr-schedule__loading"
        role="status"
        aria-live="polite">
        Loading schedule…
      </p>
      <JREmptyState
        v-else-if="!allResources.length"
        title="No crews to schedule"
        description="Active crews with a category appear here as rows. Add or activate a crew, then refresh." />
      <div v-else class="jr-schedule__pane">
        <FullCalendar
          ref="calendarRef"
          class="jr-schedule__calendar"
          :options="calendarOptions" />
      </div>
    </div>

    <EventModal
      ref="eventModal"
      :formData="formData"
      @save-event="handleSaveEvent" />
  </JRPage>
</template>

<script>
import FullCalendar from "@fullcalendar/vue3";
import interactionPlugin from "@fullcalendar/interaction";
import resourceTimelinePlugin from "@fullcalendar/resource-timeline";
import "@assets/css/schedule.css";
import EventModal from "./ScheduleEventModal.vue";
import axios from "axios";
import dayjs from "dayjs";
import localizedFormat from "dayjs/plugin/localizedFormat";
import Swal from "sweetalert2";
dayjs.extend(localizedFormat);
import { useAuthStore } from "@stores/auth";
import { openPdf } from "@helpers";
import SearchIcon from "@components/icons/searchIcon.vue";
import { appMixin } from "@mixins/appMixin";
import FileExcel from "@primeicons/vue/file-excel";
import FilePdf from "@primeicons/vue/file-pdf";
import {
  JRPage,
  JRPageHeader,
  JRToolbar,
  JRInput,
  JRButton,
  JRBadge,
  JRDatePicker,
  JREmptyState,
} from "@ui";

function escapeScheduleHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export default {
  components: {
    SearchIcon,
    FileExcel,
    FilePdf,
    FullCalendar,
    EventModal,
    JRPage,
    JRPageHeader,
    JRToolbar,
    JRInput,
    JRButton,
    JRBadge,
    JRDatePicker,
    JREmptyState,
  },
  mixins: [appMixin],
  data() {
    return {
      search: "",
      jumpDate: null,
      calendar_start: null,
      calendar_end: null,
      resizeObserver: null,
      allResources: [],
      events: [],
      showModal: false,
      showFullCalendar: false,
      formData: {
        date: "",
        job: "",
        lot: "",
        title: "",
        description: "",
        extendedService: false,
      },
      userId: null,
      publishing: false,
      categoryTotals: [],
      /** Ancho columna crew: 25% móvil/tablet pequeña, 15% desktop / tablet grande (≥992px) */
      resourceAreaWidthCurrent: "25%",
      websocket: null,
      wsUrl: null,
      initialCalendarOptions: {
        plugins: [interactionPlugin, resourceTimelinePlugin],
        schedulerLicenseKey: "GPL-My-Project-Is-Open-Source",
        initialView: "resourceTimelineWeek",
        firstDay: 1,
        headerToolbar: {
          left: "prev,next today",
          center: "title",
          right: "resourceTimelineDay,resourceTimelineWeek",
        },
        buttonText: {
          today: "Today",
          resourceTimelineDay: "Day",
          resourceTimelineWeek: "Week",
        },
        editable: false,
        eventResizableFromStart: false,
        droppable: false,
        resourceAreaHeaderContent: "Crew",
        eventMinHeight: 90,
        height: "100%",
        stickyHeaderDates: true,
        slotLabelInterval: { days: 1 },
        slotDuration: { days: 1 },
        slotLabelFormat: { weekday: "long", month: "short", day: "numeric" },
        resourceGroupField: "category",
        resourceOrder: "category",
        resources: [],
        eventDrop: () => {
          return false;
        },
        eventResize: () => {
          return false;
        },
        dateClick: () => {
          return false;
        },
        eventClick: this.handleEventClick,
        datesSet: this.handleDatesSet,
        eventContent: function (arg) {
          const event_date = dayjs(arg.event.extendedProps.updated_at);
          const isAbsence = arg.event.extendedProps?.is_absence;
          let cardClass = "jr-schedule-event-card";
          if (arg.event.extendedProps?.deleted !== undefined) {
            cardClass += arg.event.extendedProps?.deleted
              ? " jr-schedule-event-card--deleted"
              : " jr-schedule-event-card--posted";
          } else {
            cardClass += " jr-schedule-event-card--draft";
          }
          if (isAbsence) {
            cardClass =
              "jr-schedule-event-card jr-schedule-event-card--absence";
          }
          const title = escapeScheduleHtml(arg.event.title || "");
          const description = escapeScheduleHtml(
            arg.event.extendedProps.description || ""
          );
          const extService = arg.event.extendedProps?.extended_service
            ? `<div class="jr-schedule-event-card__flags"><span class="jr-schedule-event-card__badge">Ext. Service</span></div>`
            : "";
          const absencePrefix = isAbsence
            ? `<span class="jr-schedule-event-card__absence-mark" aria-hidden="true"></span>`
            : "";
          return {
            html: `<div class="${cardClass}">
                     <span class="jr-schedule-event-card__title">${absencePrefix}${title}</span>
                     <div class="jr-schedule-event-card__desc">${description}</div>
                     ${extService}
                     <div class="jr-schedule-event-card__meta">${escapeScheduleHtml(
                       event_date.format("lll")
                     )}</div>
                   </div>`,
          };
        },
      },
    };
  },
  computed: {
    /**
     * Crews inactivos no aparecen salvo que tengan eventos (borrador o publicado) en el rango cargado.
     */
    resources() {
      const idsWithEvents = new Set(
        (this.events || []).map((e) => Number(e.resourceId))
      );
      return this.allResources.filter((r) => {
        const active = r.crewActive !== false;
        if (active) return true;
        return idsWithEvents.has(Number(r.id));
      });
    },
    filteredEvents() {
      const searchTerm = this.search.toLowerCase();
      if (searchTerm.trim().length > 0) {
        return this.events.filter((event) => {
          return (
            event.extendedProps.crew_title
              ?.toLowerCase()
              .includes(searchTerm) ||
            event.extendedProps.address?.toLowerCase().includes(searchTerm) ||
            event.extendedProps.description
              ?.toLowerCase()
              .includes(searchTerm) ||
            event.extendedProps.title?.toLowerCase().includes(searchTerm)
          );
        });
      } else {
        return this.events;
      }
    },
    showBntPublishAll() {
      return this.events.some((e) => e?.extendedProps?.event !== undefined);
    },
    calendarOptions() {
      return {
        ...this.initialCalendarOptions,
        resourceAreaWidth: this.resourceAreaWidthCurrent,
        resources: this.resources,
        events: this.filteredEvents,
      };
    },
  },
  async mounted() {
    const data = await this.getAuthenticatedUser();
    const authStore = useAuthStore();
    authStore.setUser(data);
    this.userId = data.id;
    this.updateResourceAreaWidth();
    window.addEventListener("resize", this.updateResourceAreaWidth);
    this.getCrews();
    this.wsUrl = this.buildWsUrl("ws/calendar-updates/");
    this.connectWebSocket();
    this.updateCalendarPermissions();
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.updateResourceAreaWidth);
    this.disconnectWebSocket();
    this.disconnectResizeObserver();
  },

  methods: {
    toCalendarDate(value) {
      if (!value) return null;
      if (value instanceof Date && !Number.isNaN(value.getTime())) return value;
      const d = dayjs(value);
      return d.isValid() ? d.toDate() : null;
    },
    onJumpDate(value) {
      this.jumpDate = value;
      const date = this.toCalendarDate(value);
      if (!date) return;
      const api = this.$refs.calendarRef?.getApi?.();
      if (!api) return;
      api.gotoDate(date);
    },
    /** Alineado con breakpoint Bootstrap lg (992px): ancho útil para iPad Pro y desktop. */
    updateResourceAreaWidth() {
      if (typeof window === "undefined") return;
      const wide = window.matchMedia("(min-width: 992px)").matches;
      this.resourceAreaWidthCurrent = wide ? "15%" : "25%";
      this.$nextTick(() => {
        const api = this.$refs.calendarRef?.getApi?.();
        if (api) {
          try {
            api.updateSize();
          } catch (e) {
            // Calendar not ready
          }
        }
      });
    },
    reSizeCalendar() {
      const resourceRows = document.querySelectorAll(".fc-resource-cell");
      const eventRows = document.querySelectorAll(".fc-datagrid-cell");

      this.resizeObserver = new ResizeObserver((entries) => {
        entries.forEach((entry, index) => {
          if (resourceRows[index]) {
            resourceRows[index].style.height = `${entry.contentRect.height}px`;
          }
        });
      });

      eventRows.forEach((row) => {
        this.resizeObserver.observe(row);
      });
    },

    async updateCalendarPermissions() {
      try {
        const { data } = await axios.get("/api/crew/supervisor/");
        const crewId = data.crew?.id;

        this.userCrewCategoryName = data.crew?.category?.name || null;
        this.can_create_event = data.can_create_event;
        this.is_coordinator = data.is_coordinator;
        this.crewId = crewId;
        this.crewName = data.crew?.name;

        if (
          this.hasPermission("appschedule.add_eventdraft") ||
          (data.can_create_event && !data.is_coordinator)
        ) {
          this.initialCalendarOptions.editable = true;
          this.initialCalendarOptions.eventResizableFromStart = true;
          this.initialCalendarOptions.droppable = true;
          this.initialCalendarOptions.eventDrop = this.handleEventDrop;
          this.initialCalendarOptions.eventResize = this.handleEventDrop;
          this.initialCalendarOptions.dateClick = this.handleDateClick;
        }
      } catch (error) {
        console.error("🚫 Error al cargar permisos de supervisor:", error);
      }
    },

    handleDatesSet(info) {
      const startDate = dayjs(info.view.currentStart).format("YYYY-MM-DD");
      const endDate = dayjs(info.view.currentEnd).format("YYYY-MM-DD");

      this.jumpDate = dayjs(info.view.currentStart).toDate();

      if (startDate !== this.calendar_start && endDate !== this.calendar_end) {
        this.calendar_start = startDate;
        this.calendar_end = endDate;
        this.getEvents();
      }
    },

    async getCrews() {
      this.showFullCalendar = false;
      try {
        const response = await axios.get("/api/crews/");

        if (response.status === 200) {
          const data = response.data.results || response.data;
          const crews = Array.isArray(data) ? data : [];

          const crewsWithCategory = crews.filter(
            (item) => item && item.category_name
          );

          this.allResources = crewsWithCategory.map((item) => ({
            id: item.id,
            title: item.name.toUpperCase(),
            category: item.category_name.toUpperCase(),
            crewActive: item.status !== false,
          }));

          if (this.allResources.length === 0) {
            console.warn(
              "⚠️ No crews found with category_name. Calendar will be empty."
            );
          }
        }
        this.showFullCalendar = true;
        await this.$nextTick();
        if (this.$refs.calendarRef && this.$refs.calendarRef.getApi) {
          try {
            this.$refs.calendarRef.getApi().refetchResources();
          } catch (e) {
            // Calendar API not ready yet
          }
        }
      } catch (error) {
        console.error("❌ Error fetching crews data:", error);
        this.showFullCalendar = true;
        Swal.fire({
          icon: "error",
          title: "Error loading crews",
          text:
            error.response?.data?.detail ||
            error.message ||
            "Could not load crews data. Please refresh the page.",
          confirmButtonText: "OK",
        });
      }
    },

    async getEvents() {
      try {
        const url_get = `/api/schedule-list/?start_at=${this.calendar_start}&end_at=${this.calendar_end}`;
        const response = await axios.get(url_get);
        if (response.status === 200) {
          this.events = [];
          this.categoryTotals = response.data.category_totals || [];
          response.data?.events?.forEach((item) => {
            this.events.push({
              id: "event_id_" + String(item.id),
              resourceId: item.crew,
              start: item.date,
              end: item.end_dt,
              title: item.title,
              extendedProps: item,
            });
          });
          response.data?.drafts?.forEach((item) => {
            this.events.push({
              id: "draft_id_" + String(item.id),
              resourceId: item.crew,
              start: item.date,
              end: item.end_dt,
              title: item.title,
              extendedProps: item,
            });
          });
          this.$nextTick(() => {
            this.reSizeCalendar();
          });
        }
      } catch (error) {
        console.error("Error fetching chart data:", error);
      }
    },
    async updateEvent(url, payload, method = "patch") {
      const axios_method = method === "patch" ? axios.patch : axios.post;
      await axios_method(url, payload);
    },

    handleDateClick(info) {
      try {
        const isCoordinator = this.is_coordinator;
        const canCreateEvent = this.can_create_event;
        const crewCategoryName = this.userCrewCategoryName?.toLowerCase();
        const clickedCrewId = parseInt(info.resource.id);
        const crewId = this.crewId;
        const crewName = this.crewName;
        this.clickedCrewId = clickedCrewId;

        if (!canCreateEvent && !isCoordinator) {
          Swal.fire(
            "Permission Denied",
            "You do not have permission to create events.",
            "error"
          );
          return;
        }

        if (!isCoordinator && crewId !== clickedCrewId) {
          Swal.fire(
            "Permission Denied",
            `You can only create events for your category (${
              crewCategoryName?.toUpperCase() || "UNKNOWN"
            }) with your assigned crew (${crewName || "No Crew"}).`,
            "warning"
          );
          return;
        }

        this.$refs.eventModal.open(
          {
            date: info.dateStr,
            title: "",
            description: "",
            work_account: null,
            crew: parseInt(info.resource.id),
            crewTitle: info.resource.title,
            crewCategory: info.resource.category ?? "",
            extended_service: false,
            canCreateEvent: this.can_create_event,
            clickedCrewId: this.clickedCrewId,
            crewId: this.crewId,
            isCoordinator: this.is_coordinator,
          },
          true
        );
      } catch (error) {
        console.error("💥 Error inesperado en handleDateClick:", error);
        Swal.fire(
          "Oops!",
          "Something went wrong while trying to open the event modal.",
          "error"
        );
      }
    },

    handleEventClick(info) {
      const clickedCrewId = parseInt(info.event.getResources()[0].id);
      this.clickedCrewId = clickedCrewId;
      const resource = info.event.getResources()[0];
      this.$refs.eventModal.open(
        {
          id: parseInt(info.event.extendedProps?.id),
          title: info.event.title,
          date: info.event.startStr,
          description: info.event.extendedProps?.description,
          work_account: info.event.extendedProps?.work_account || null,
          crew: resource?.id,
          crewTitle: resource?.title ?? "",
          crewCategory:
            resource?.category ?? info.event.extendedProps?.crew_category ?? "",
          extended_service: info.event.extendedProps?.extended_service,
          isAbsence: info.event.extendedProps?.is_absence || false,
          absence_reason: info.event.extendedProps?.absence_reason || null,
          extendedProps: info.event.extendedProps,
          canCreateEvent: this.can_create_event,
          clickedCrewId: this.clickedCrewId,
          crewId: this.crewId,
          isCoordinator: this.is_coordinator,
        },
        false
      );
    },

    async handleEventDrop(info) {
      const isCoordinator = this.is_coordinator;
      const crewId = this.crewId;
      const clickedCrewId = parseInt(info.event.getResources()[0].id);
      const crewName = this.crewName;

      if (!isCoordinator && crewId !== clickedCrewId) {
        Swal.fire(
          "Permission Denied",
          `You can only move events of your assigned crew (${
            crewName || "Unknown Crew"
          }).`,
          "warning"
        );
        info.revert();
        return;
      }
      const is_draft = info.event.extendedProps?.event !== undefined;
      try {
        if (is_draft) {
          const payload = {
            title: info.event.title,
            description: info.event.extendedProps?.description,
            date: info.event.startStr,
            end_dt: info.event.endStr,
            work_account: info.event.extendedProps?.work_account || null,
            crew: info.event.getResources()[0].id,
            extended_service: info.event.extendedProps?.extended_service,
            is_absence: info.event.extendedProps?.is_absence || false,
          };
          await this.updateEvent(
            `/api/schedule/${info.event.extendedProps?.id}/`,
            payload
          );
        } else {
          const payload = { ...info.event.extendedProps };
          payload.id = null;
          payload.event = info.event.extendedProps?.id;
          payload.date = info.event.startStr;
          payload.end_dt = info.event.endStr;
          payload.crew = info.event.getResources()[0].id;
          payload._post = true;
          payload._deleted = info.event.extendedProps?.deleted;
          await this.updateEvent(`/api/schedule/`, payload, "post");
        }
      } catch (e) {
        if (e.response.status === 400) {
          const err = e.response.data;
          if (err.hasOwnProperty("non_field_errors")) {
            if (
              Array.isArray(err.non_field_errors) &&
              err.non_field_errors.includes("Duplicate Event Detected")
            ) {
              Swal.fire(
                "Duplicate Event Detected",
                "An event with the same title (Lot, Community, or Address) already exists in this Crew Category.",
                "error"
              );
              return;
            }
          }
          Swal.fire(e.response.statusText, e.message, "error");
        }
        if (e.response.status === 403) {
          Swal.fire(
            "Action not allowed",
            "You do not have permission to publish events",
            "error"
          );
          return;
        }
      }
    },

    handleSaveEvent() {
      this.getEvents();
    },

    connectWebSocket() {
      this.websocket = new WebSocket(this.wsUrl);

      this.websocket.onopen = () => {
        console.log("Conexión WebSocket establecida.");
      };

      this.websocket.onmessage = () => {
        this.getEvents();
      };

      this.websocket.onclose = () => {
        console.log("Conexión WebSocket cerrada.");
      };

      this.websocket.onerror = (error) => {
        console.error("Error de WebSocket:", error);
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
      if (!this.showBntPublishAll || this.publishing) return;
      this.publishing = true;

      const watchdog = setTimeout(() => {
        if (this.publishing) {
          this.publishing = false;
          if (typeof this.notifyToastError === "function") {
            this.notifyToastError(
              "Publish timed out after 30s. Please try again."
            );
          }
        }
      }, 30000);

      try {
        await axios.post(
          "/api/schedule/publish_drafts/",
          {
            start_date: this.calendar_start,
            end_date: this.calendar_end,
          },
          { timeout: 30000 }
        );

        if (typeof this.getEvents === "function") {
          await this.getEvents();
        }

        if (typeof this.notifyToastSuccess === "function") {
          this.notifyToastSuccess("Drafts published successfully.");
        }
      } catch (e) {
        console.error(e);
        const msg =
          e?.response?.data?.error ||
          e?.message ||
          "Error while publishing drafts.";
        if (typeof this.notifyToastError === "function") {
          this.notifyToastError(msg);
        }
      } finally {
        clearTimeout(watchdog);
        this.publishing = false;
      }
    },

    async generateSchedulePDF() {
      try {
        const url = `/api/schedule-report/?start_at=${this.calendar_start}&end_at=${this.calendar_end}`;
        const response = await axios.get(url);

        if (response.status === 200) {
          openPdf(response.data);
        }
      } catch (error) {
        console.error("❌ Error downloading schedule PDF:", error);
        Swal.fire("Error", "Could not generate the PDF.", "error");
      }
    },
    async downloadScheduleExcel() {
      const url = `/api/schedule-excel/?start_at=${this.calendar_start}&end_at=${this.calendar_end}`;
      try {
        const response = await axios.get(url, { responseType: "blob" });
        const blob = new Blob([response.data], {
          type: response.headers["content-type"],
        });
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);

        const endDate = new Date(this.calendar_end);
        endDate.setDate(endDate.getDate() - 1);
        const formattedEnd = endDate.toISOString().split("T")[0];

        link.download = `schedule-${this.calendar_start}_to_${formattedEnd}.xlsx`;
        link.click();
      } catch (err) {
        Swal.fire("Error", "Could not download the Excel file.", "error");
        console.error("Excel Download Error:", err);
      }
    },
    removeEmojis(text) {
      text = text.replace(/\d\uFE0F\u20E3/g, "");
      return text
        .replace(
          /([\u2700-\u27BF]|[\uE000-\uF8FF]|[\uD83C-\uDBFF\uDC00-\uDFFF]+|[\uFE00-\uFE0F]|\u200D)/g,
          ""
        )
        .trim();
    },
  },
};
</script>

<style scoped>
.jr-schedule__search {
  position: relative;
  width: 100%;
  max-width: 22rem;
}

.jr-schedule__search-icon {
  position: absolute;
  left: 0.65rem;
  top: 50%;
  transform: translateY(-50%);
  display: inline-flex;
  color: var(--color-jr-muted, #4b5563);
  pointer-events: none;
  z-index: 1;
}

.jr-schedule__search :deep(.jr-control),
.jr-schedule__search :deep(input) {
  padding-left: 2.15rem;
}

.jr-schedule__totals {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem 0.5rem;
  pointer-events: none;
}

.jr-schedule__totals-label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-jr-muted, #4b5563);
  margin-right: 0.15rem;
}

.jr-schedule__jump {
  min-width: 10.5rem;
  max-width: 12.5rem;
  flex: 1 1 10.5rem;
}

.jr-schedule__excel-icon,
.jr-schedule__pdf-icon {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  margin-right: 0.35rem;
  vertical-align: -0.15em;
}

.jr-schedule__excel-icon {
  color: var(--color-jr-success, #16a34a);
}

.jr-schedule__pdf-icon {
  color: var(--color-jr-danger, #dc2626);
}

.jr-schedule {
  margin-top: 0.75rem;
}

.jr-schedule__loading {
  margin: 0;
  padding: 2.5rem 1rem;
  text-align: center;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-jr-muted, #4b5563);
}

.jr-schedule__pane {
  display: flex;
  flex-direction: column;
  background: var(--color-jr-surface, #ffffff);
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  height: calc(100vh - var(--jr-shell-topbar, 3.5rem) - 10.5rem);
  max-height: calc(100vh - var(--jr-shell-topbar, 3.5rem) - 10.5rem);
  min-height: 22rem;
  overflow: hidden;
}

.jr-schedule__calendar {
  flex: 1 1 auto;
  min-height: 0;
  height: 100%;
}

.jr-schedule__pane :deep(.fc),
.jr-schedule__pane :deep(.fc-view-harness) {
  height: 100% !important;
}

.jr-schedule__pane ::selection {
  background: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 22%,
    var(--color-jr-surface, #ffffff)
  );
  color: var(--color-jr-text, #111827);
}

@media (max-width: 1023.98px) {
  .jr-schedule__search {
    max-width: none;
  }

  .jr-schedule__jump {
    max-width: none;
    flex: 1 1 100%;
  }

  .jr-schedule__pane {
    height: calc(100dvh - var(--jr-shell-mobile-bar, 3rem) - 13.5rem);
    max-height: calc(100dvh - var(--jr-shell-mobile-bar, 3rem) - 13.5rem);
    min-height: 18rem;
  }
}
</style>
