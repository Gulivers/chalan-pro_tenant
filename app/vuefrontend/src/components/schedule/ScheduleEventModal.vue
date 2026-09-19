<template>
  <JRDialog
    :visible="visible"
    :header="dialogHeader"
    size="xl"
    :show-footer="false"
    @update:visible="onVisibleChange">
    <div class="jr-schedule-event">
      <header class="jr-schedule-event__header">
        <div class="jr-schedule-event__header-main">
          <div class="jr-schedule-event__header-text">
            <span class="jr-schedule-event__label">
              {{ is_draft ? "Draft Work Order" : "Work Account" }}
            </span>
            <h2 class="jr-schedule-event__title">{{ displayHeaderTitle }}</h2>
          </div>
          <JRBadge
            :value="is_draft ? 'Draft' : 'Posted'"
            :severity="is_draft ? 'secondary' : 'success'" />
        </div>

        <dl v-if="headerMetaItems.length" class="jr-schedule-event__meta">
          <div
            v-for="item in headerMetaItems"
            :key="item.label"
            class="jr-schedule-event__meta-item">
            <dt class="jr-schedule-event__meta-label">{{ item.label }}</dt>
            <dd class="jr-schedule-event__meta-value" :title="item.value">
              {{ item.value }}
            </dd>
          </div>
        </dl>
      </header>

      <div class="jr-schedule-event__layout">
        <form
          class="jr-schedule-event__form"
          @submit.prevent="submitEvent(false)">
          <JRField
            v-if="isEditing && hasPermission('appschedule.add_absencereason')"
            label="Absence"
            inputId="jr-schedule-absence-switch"
            hint="Marks this slot as an absence instead of a work account.">
            <JRCheckbox
              inputId="jr-schedule-absence-switch"
              v-model="isAbsence"
              label="Mark as absence"
              :disabled="!isEditing" />
          </JRField>

          <JRField label="Date" inputId="jr-schedule-event-date" required>
            <JRDatePicker
              inputId="jr-schedule-event-date"
              :model-value="isoToDate(localFormData.date)"
              :disabled="!isEditing"
              placeholder="Select a date"
              :show-button-bar="true"
              @update:model-value="onDateChange" />
          </JRField>

          <JRField
            v-if="isAbsence"
            label="Absence reason"
            inputId="jr-schedule-absence-reason"
            required>
            <JRSelect
              inputId="jr-schedule-absence-reason"
              v-model="localFormData.absence_reason"
              :options="absenceReasons"
              option-label="name"
              option-value="id"
              :disabled="!isEditing"
              placeholder="Select absence reason"
              filter
              show-clear />
          </JRField>

          <div v-if="!isAbsence" class="jr-schedule-event__wa">
            <WorkAccountSelector
              v-model="localFormData.work_account"
              :disabled="!isEditing"
              :required="!isAbsence" />
          </div>

          <JRField label="Title" inputId="jr-schedule-event-title" required>
            <JRInput
              inputId="jr-schedule-event-title"
              v-model="localFormData.title"
              class="jr-schedule-event__title-input"
              :disabled="!isEditing"
              placeholder="Enter event title"
              @update:model-value="titleManuallyEdited = true" />
          </JRField>

          <JRField label="Description" inputId="jr-schedule-event-description">
            <JRTextarea
              inputId="jr-schedule-event-description"
              v-model="localFormData.description"
              :rows="3"
              :disabled="!isEditing"
              placeholder="Optional notes for this work order" />
          </JRField>

          <JRField
            v-if="isEditing && hasPermission('appschedule.add_event')"
            label="Extended service"
            inputId="jr-schedule-extended-service">
            <JRCheckbox
              inputId="jr-schedule-extended-service"
              v-model="localFormData.extended_service"
              label="Extended service"
              :disabled="!isEditing" />
          </JRField>

          <div
            v-if="
              hasPermission('appschedule.add_eventdraft') &&
              canAccessEventActions
            "
            class="jr-schedule-event__actions">
            <template v-if="isEditing">
              <JRButton
                v-if="hasPermission('appschedule.add_event')"
                type="button"
                variant="primary"
                :disabled="loading || offLine"
                @click="submitEvent(true)">
                {{ loading || offLine ? "Saving…" : "Save and Post" }}
              </JRButton>
              <JRButton
                v-if="
                  !localFormData.event &&
                  hasPermission('appschedule.add_eventdraft')
                "
                type="submit"
                variant="secondary"
                :disabled="loading || offLine">
                {{ loading || offLine ? "Saving…" : "Save" }}
              </JRButton>
              <JRButton
                v-if="
                  !is_draft &&
                  localFormData.event &&
                  hasPermission('appschedule.add_event')
                "
                type="button"
                variant="danger"
                :disabled="loading || offLine"
                @click="deleteEvent">
                Delete
              </JRButton>
              <JRButton
                v-if="
                  localFormData.id &&
                  hasPermission('appschedule.delete_eventdraft')
                "
                type="button"
                variant="danger"
                :disabled="loading || offLine"
                @click="deleteEvent">
                Discard draft
              </JRButton>
            </template>
            <JRButton
              v-else
              type="button"
              variant="secondary"
              @click="toggleEdit">
              Edit
            </JRButton>
          </div>

          <p
            v-if="isEditing && offLine"
            class="jr-schedule-event__offline"
            role="alert">
            No internet connection. Reconnect to save changes.
          </p>
        </form>

        <div class="jr-schedule-event__discussion">
          <WorkOrderViewerTabs
            v-if="discussionEventId"
            :key="discussionEventId"
            :event-id="discussionEventId"
            :work-account-id="discussionWorkAccountId"
            :sync-route="false"
            initial-tab="chat" />
          <JREmptyState
            v-else
            class="jr-schedule-event__discussion-empty"
            title="Discussion unavailable"
            description="Save and post this work order to open chat, notes, folder, contracts, and transactions for this event." />
        </div>
      </div>
    </div>
  </JRDialog>
</template>

<script>
import axios from "axios";
import Swal from "sweetalert2";
import dayjs from "dayjs";
import WorkAccountSelector from "@components/transactions/WorkAccountSelector.vue";
import WorkOrderViewerTabs from "@components/work-accounts/WorkOrderViewerTabs.vue";
import {
  JRDialog,
  JRField,
  JRInput,
  JRTextarea,
  JRSelect,
  JRDatePicker,
  JRCheckbox,
  JRButton,
  JRBadge,
  JREmptyState,
} from "@ui";

export default {
  name: "ScheduleEventModal",
  props: ["formData"],
  emits: ["save-event", "delete-event"],
  components: {
    WorkAccountSelector,
    WorkOrderViewerTabs,
    JRDialog,
    JRField,
    JRInput,
    JRTextarea,
    JRSelect,
    JRDatePicker,
    JRCheckbox,
    JRButton,
    JRBadge,
    JREmptyState,
  },
  data() {
    return {
      visible: false,
      localFormData: {
        id: null,
        crew: null,
        work_account: null,
        title: "",
        description: "",
        date: "",
        extended_service: false,
        absence_reason: "",
      },
      crewTitle: "",
      crewCategory: "",
      eventMeta: null,
      workAccountDetails: null,
      isEditing: false,
      titleManuallyEdited: false,
      is_draft: true,
      event_data: null,
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
    workOrderDisplayId() {
      const id = this.event_data?.id ?? this.localFormData?.id ?? null;
      return id != null && id !== "" ? id : null;
    },
    dialogHeader() {
      if (this.workOrderDisplayId) {
        return `Work Order # ${this.workOrderDisplayId}`;
      }
      return this.is_draft ? "New draft work order" : "Work Order";
    },
    displayHeaderTitle() {
      const title = (this.localFormData?.title || this.event_data?.title || "")
        .toString()
        .trim();
      return title || this.dialogHeader;
    },
    headerMetaItems() {
      const ev = this.eventMeta || {};
      const wa = this.workAccountDetails || {};
      const title = this.displayHeaderTitle?.trim() || "";
      const addr = (wa.address || ev.address || "").toString().trim();
      const isAddrRedundant =
        addr && title && addr.toLowerCase() === title.toLowerCase();
      const lotValue = wa.lot ?? ev.lot;

      const items = [
        {
          label: "Area Supervisor",
          value: wa.supervisor || ev.supervisor || null,
        },
        {
          label: "Builder",
          value: wa.builder_name || ev.builder_name || null,
        },
        {
          label: "Community",
          value: wa.job_name || ev.job_name || null,
        },
        {
          label: "Lot",
          value: lotValue ? `Lot ${lotValue}` : null,
        },
        {
          label: "House Model",
          value: wa.house_model_name || ev.house_model_name || null,
        },
        {
          label: "Address",
          value: isAddrRedundant ? null : addr || null,
        },
        {
          label: "Default Price Type",
          value:
            wa.default_price_type_name || ev.default_price_type_name || null,
        },
      ];
      return items.filter((item) => item.value);
    },
    isAbsence: {
      get() {
        return this.localFormData.is_absence === true;
      },
      set(value) {
        this.localFormData.is_absence = value;
      },
    },
    canAccessEventActions() {
      if (!this.canCreateEvent && !this.isCoordinator) {
        return false;
      }
      if (!this.isCoordinator && this.crewId !== this.clickedCrewId) {
        return false;
      }
      return true;
    },
    discussionEventId() {
      const id = this.event_data?.id;
      const parsed = Number(id);
      return Number.isFinite(parsed) ? parsed : null;
    },
    discussionWorkAccountId() {
      const raw =
        this.localFormData?.work_account ??
        this.event_data?.work_account ??
        null;
      const parsed = Number(raw);
      return Number.isFinite(parsed) ? parsed : null;
    },
  },
  watch: {
    isAbsence(newVal) {
      if (newVal) {
        this.localFormData.work_account = null;
        this.localFormData.title = "";
      } else {
        this.localFormData.absence_reason = "";
        this.localFormData.title = "";
      }
    },
    "localFormData.absence_reason"(newVal) {
      if (this.isAbsence && newVal && !this.titleManuallyEdited) {
        this.autoFillTitle();
      }
    },
    "localFormData.work_account"() {
      this.autoFillTitle();
    },
  },
  methods: {
    isoToDate(value) {
      if (!value) return null;
      if (value instanceof Date) return value;
      const d = dayjs(value);
      return d.isValid() ? d.toDate() : null;
    },
    dateToIso(value) {
      if (!value) return "";
      const d = dayjs(value);
      return d.isValid() ? d.format("YYYY-MM-DD") : "";
    },
    onDateChange(value) {
      this.localFormData.date = this.dateToIso(value);
    },
    onVisibleChange(next) {
      this.visible = next;
      if (!next) {
        this.event_data = null;
        this.eventMeta = null;
        this.workAccountDetails = null;
      }
    },
    async loadWorkAccountDetails(waId = this.localFormData.work_account) {
      if (!waId) {
        this.workAccountDetails = null;
        return null;
      }
      try {
        const response = await axios.get(`/api/work-accounts/${waId}/`);
        if (response.status === 200) {
          this.workAccountDetails = response.data || null;
          return this.workAccountDetails;
        }
      } catch (error) {
        console.error("Error loading work account details:", error);
        this.workAccountDetails = null;
      }
      return null;
    },
    async autoFillTitle() {
      if (this.titleManuallyEdited) return;

      if (this.isAbsence) {
        const reason = this.absenceReasons.find(
          (r) => r.id === this.localFormData.absence_reason
        );
        this.localFormData.title = reason ? reason.name : "Absence";
        return;
      }

      if (this.localFormData.work_account) {
        const data = await this.loadWorkAccountDetails(
          this.localFormData.work_account
        );
        if (data?.title) {
          this.localFormData.title = data.title.toUpperCase();
        } else if (!this.titleManuallyEdited) {
          this.localFormData.title = "";
        }
      } else {
        this.localFormData.title = "";
        this.workAccountDetails = null;
      }
    },

    open(eventData, isEditMode = false) {
      this.old_event = null;
      if (eventData?.extendedProps?.end_dt) {
        this.old_event = eventData?.extendedProps;
      }
      this.titleManuallyEdited = Boolean(eventData?.title);
      this.localFormData = {
        id: null,
        crew: eventData?.crew,
        date: eventData?.date,
        end_dt: eventData?.extendedProps?.end_dt || null,
        work_account:
          eventData?.work_account ||
          eventData?.extendedProps?.work_account ||
          null,
        title: eventData?.title || "",
        description: eventData?.description || "",
        extended_service: eventData?.extended_service || false,
        is_absence:
          eventData?.isAbsence ?? eventData?.extendedProps?.is_absence ?? false,
        absence_reason:
          eventData?.absence_reason ??
          eventData?.extendedProps?.absence_reason ??
          null,
        _post: false,
      };

      this.crewTitle = eventData?.crewTitle ?? "";
      this.crewCategory =
        eventData?.crewCategory ??
        eventData?.extendedProps?.crew_category ??
        "";
      this.eventMeta = {
        ...(eventData?.extendedProps || {}),
        date: eventData?.date || eventData?.extendedProps?.date || null,
        crew_title:
          eventData?.crewTitle || eventData?.extendedProps?.crew_title || null,
        crew_category:
          eventData?.crewCategory ||
          eventData?.extendedProps?.crew_category ||
          null,
      };
      this.workAccountDetails = null;
      this.event_data = null;

      if (eventData?.extendedProps?.event === undefined) {
        this.is_draft = false;
        this.localFormData.event = eventData?.extendedProps?.id || null;
        this.event_data = {
          id: eventData?.extendedProps?.id,
          title: eventData?.extendedProps?.title,
          work_account:
            eventData?.work_account ||
            eventData?.extendedProps?.work_account ||
            null,
        };
      } else {
        if (eventData?.extendedProps?.event) {
          this.event_data = {
            id: eventData?.extendedProps?.event,
            title: eventData?.extendedProps?.title,
            work_account:
              eventData?.work_account ||
              eventData?.extendedProps?.work_account ||
              null,
          };
        }
        this.is_draft = true;
        this.localFormData.id = eventData?.extendedProps?.id;
        this.localFormData.event = eventData?.extendedProps?.event;
      }

      this.titleManuallyEdited = false;
      this.canCreateEvent = eventData?.canCreateEvent || false;
      this.isCoordinator = eventData?.isCoordinator || false;
      this.crewId = eventData?.crewId || null;
      this.clickedCrewId = eventData?.clickedCrewId || eventData?.crew || null;

      this.isEditing = isEditMode;
      this.visible = true;
      this.loadWorkAccountDetails(this.localFormData.work_account);
    },

    hideModal() {
      if (document.activeElement) {
        document.activeElement.blur();
      }
      this.visible = false;
      this.event_data = null;
    },

    toggleEdit() {
      this.isEditing = !this.isEditing;
    },

    async submitEvent(post = false) {
      this.loading = true;
      if (!this.localFormData.end_dt && this.localFormData.date) {
        const start = new Date(this.localFormData.date);
        const end = new Date(start);
        end.setDate(start.getDate() + 1);
        this.localFormData.end_dt = end.toISOString().split("T")[0];
      }
      this.localFormData._post = post === true;
      const id_exist = this.localFormData?.id >= 1;
      const url = id_exist
        ? `/api/schedule/${this.localFormData?.id}/`
        : "/api/schedule/";
      const axios_method = id_exist ? axios.put : axios.post;

      if (this.old_event) {
        const old_start = dayjs(this.old_event.date);
        const new_start = dayjs(this.localFormData.date);
        if (!old_start.isSame(new_start)) {
          const old_end = dayjs(this.old_event.end_dt);
          const duration = old_end.diff(old_start, "days");
          const new_end = new_start.add(duration, "days");
          this.localFormData.end_dt = new_end.format("YYYY-MM-DD");
        }
      }

      if (!this.isAbsence) {
        if (!this.localFormData.work_account) {
          Swal.fire(
            "Missing Fields",
            "Please select a Work Account before saving.",
            "warning"
          );
          this.loading = false;
          return;
        }
      }

      try {
        const resp = await axios_method(url, this.localFormData);
        this.loading = false;
        if ([200, 201].includes(resp.status)) {
          this.$emit("save-event", true);
          this.hideModal();
        }
      } catch (e) {
        this.loading = false;
        if (e.response?.status === 400) {
          const err = e.response.data;
          if (err.hasOwnProperty("non_field_errors")) {
            if (
              Array.isArray(err.non_field_errors) &&
              err.non_field_errors.includes("Duplicate Event Detected")
            ) {
              if (this.isAbsence) {
                console.warn(
                  "Skipping duplicate validation for absence event."
                );
              } else {
                Swal.fire(
                  "Duplicate Event Detected",
                  "An event with the same Lot and Community or Address already exists in this Crew Category.",
                  "error"
                );
                return;
              }
            } else {
              Swal.fire(
                "Error Detected",
                err.non_field_errors.join(", "),
                "error"
              );
              return;
            }
          }

          const msg = [];
          for (const item in err) {
            msg.push(`${item}: ${err[item].join(", ")}`);
          }
          Swal.fire("Validation Error", msg.join(", "), "error");
          return;
        }

        Swal.fire(
          "Error Detected",
          "An error occurred while saving the data.",
          "error"
        );
      }
    },

    async deleteApi() {
      this.loading = true;
      try {
        const url = !this.is_draft
          ? `/api/schedule/${this.localFormData.event}/?deleted=true`
          : `/api/schedule/${this.localFormData.id}/`;
        await axios.delete(url);
        this.$emit("delete-event", this.localFormData.id);
        this.hideModal();
        this.notifyToastSuccess("Event deleted successfully.");
      } catch (e) {
        console.error(e);
      }
      this.loading = false;
    },

    async deleteEvent() {
      if (this.is_draft) {
        await this.deleteApi();
        return;
      }
      const title = `Are you sure you want to delete this event${
        this.is_draft ? " draft" : ""
      }?`;
      const text = this.is_draft
        ? "This action cannot be undone."
        : "This event will no longer be public";
      this.confirmDelete(title, text, this.deleteApi);
    },

    async loadAbsenceReasons() {
      try {
        const response = await axios.get("/api/absence-reasons/");
        this.absenceReasons = response.data;
      } catch (error) {
        console.error("Error loading absence reasons:", error);
        this.notifyError("Failed to load absence reasons");
      }
    },
    updateOnlineStatus() {
      this.offLine = !navigator.onLine;
    },
  },

  mounted() {
    this.offLine = !navigator.onLine;
    this.loadAbsenceReasons();
    window.addEventListener("online", this.updateOnlineStatus);
    window.addEventListener("offline", this.updateOnlineStatus);
  },
  beforeUnmount() {
    window.removeEventListener("online", this.updateOnlineStatus);
    window.removeEventListener("offline", this.updateOnlineStatus);
  },
};
</script>

<style scoped>
/* Mobile-first: stacked layout, natural height, modal scrolls */
.jr-schedule-event {
  --jr-wov-body-height: min(16rem, calc(100dvh - 20rem));
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  min-height: 0;
}

.jr-schedule-event__header {
  margin: 0;
  padding: 0.75rem 0.875rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #ffffff);
  flex: 0 0 auto;
}

.jr-schedule-event__header-main {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.625rem 0.875rem;
}

.jr-schedule-event__header-text {
  min-width: 0;
  flex: 1 1 10rem;
}

.jr-schedule-event__label {
  display: block;
  margin-bottom: 0.2rem;
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-muted, #4b5563);
}

.jr-schedule-event__title {
  margin: 0;
  font-size: 1.3125rem;
  font-weight: 600;
  line-height: 1.25;
  color: var(--color-jr-text, #111827);
  letter-spacing: -0.01em;
  word-break: break-word;
}

.jr-schedule-event__meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.625rem 1rem;
  margin: 0.75rem 0 0;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-schedule-event__meta-item {
  display: flex;
  flex-direction: column;
  min-width: 0;
  max-width: none;
}

.jr-schedule-event__meta-label {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-jr-muted, #4b5563);
}

.jr-schedule-event__meta-value {
  margin: 0.15rem 0 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-jr-text, #111827);
  line-height: 1.35;
  word-break: break-word;
}

.jr-schedule-event__layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.875rem;
  align-items: start;
  height: auto;
  max-height: none;
  min-height: 0;
}

.jr-schedule-event__form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 0;
  min-height: 0;
  max-height: none;
  overflow: visible;
  padding: 0.75rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #ffffff);
}

.jr-schedule-event__wa :deep(.jr-field),
.jr-schedule-event__wa :deep(label) {
  font-size: 0.8125rem;
}

.jr-schedule-event__title-input :deep(input) {
  text-transform: uppercase;
}

.jr-schedule-event__actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.25rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
  position: static;
  background: var(--color-jr-surface, #ffffff);
}

.jr-schedule-event__actions :deep(.jr-button),
.jr-schedule-event__actions :deep(.p-button) {
  width: 100%;
  min-height: 2.75rem;
  justify-content: center;
}

.jr-schedule-event__offline {
  margin: 0;
  padding: 0.5rem 0.65rem;
  border: 1px solid var(--color-jr-danger, #dc2626);
  background: color-mix(
    in srgb,
    var(--color-jr-danger, #dc2626) 12%,
    var(--color-jr-surface, #ffffff)
  );
  color: var(--color-jr-danger-text, #991b1b);
  font-size: 0.8125rem;
  font-weight: 600;
}

.jr-schedule-event__discussion {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: calc(var(--jr-wov-body-height, 16rem) + 7rem);
  height: auto;
  max-height: none;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #ffffff);
  overflow: hidden;
}

.jr-schedule-event__discussion :deep(.jr-wov-tabs) {
  border: none;
  flex: 1 1 auto;
  min-height: 0;
  height: 100%;
}

.jr-schedule-event__discussion :deep(.jr-scroll-area),
.jr-schedule-event__discussion :deep(.p-scrollarea.jr-scroll-area) {
  height: var(--jr-wov-body-height, 16rem) !important;
  min-height: 12rem;
}

.jr-schedule-event__discussion-empty {
  padding: 1.25rem 1rem;
}

@media (min-width: 992px) {
  .jr-schedule-event {
    --jr-wov-body-height: min(26rem, calc(100dvh - 18rem));
    gap: 1rem;
  }

  .jr-schedule-event__header {
    padding: 0.85rem 1rem;
  }

  .jr-schedule-event__label {
    font-size: 0.8125rem;
  }

  .jr-schedule-event__meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem 1.75rem;
  }

  .jr-schedule-event__meta-item {
    min-width: 7.5rem;
    max-width: 14rem;
  }

  .jr-schedule-event__layout {
    grid-template-columns: minmax(16rem, 20rem) minmax(0, 1fr);
    gap: 1.25rem;
    align-items: stretch;
    height: min(36rem, calc(100dvh - 12rem));
    max-height: min(36rem, calc(100dvh - 12rem));
  }

  .jr-schedule-event__form {
    gap: 0.85rem;
    padding: 0.85rem;
    max-height: 100%;
    overflow-y: auto;
    overscroll-behavior: contain;
  }

  .jr-schedule-event__actions {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: flex-end;
    margin-top: auto;
    position: sticky;
    bottom: 0;
    z-index: 2;
  }

  .jr-schedule-event__actions :deep(.jr-button),
  .jr-schedule-event__actions :deep(.p-button) {
    width: auto;
    min-height: 0;
  }

  .jr-schedule-event__discussion {
    height: 100%;
    max-height: 100%;
    min-height: 0;
  }

  .jr-schedule-event__discussion :deep(.jr-scroll-area),
  .jr-schedule-event__discussion :deep(.p-scrollarea.jr-scroll-area) {
    height: 100% !important;
    min-height: 14rem;
  }
}
</style>
