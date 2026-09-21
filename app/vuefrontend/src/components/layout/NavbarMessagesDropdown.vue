<template>
  <!-- Sidebar variant -->
  <SidebarMenuItem v-if="shouldShow && variant === 'sidebar'">
    <SidebarMenuButton
      :is-active="isMessagesActive || isDropdownOpen"
      aria-label="Notifications"
      :aria-expanded="isDropdownOpen"
      @click="toggleDropdown">
      <Comments />
      <span>Messages</span>
    </SidebarMenuButton>
    <SidebarMenuBadge v-if="chatStore.unreadTotal > 0">
      {{ chatStore.unreadTotal }}
      <span class="jr-shell-sidebar__sr-only">unread messages</span>
    </SidebarMenuBadge>
  </SidebarMenuItem>

  <!-- Topbar variant -->
  <div
    v-else-if="shouldShow && variant === 'topbar'"
    class="jr-shell-topbar-messages-wrap">
    <button
      type="button"
      class="jr-shell-topbar__nav-link jr-shell-topbar__nav-link--messages"
      :class="{
        'jr-shell-topbar__nav-link--active': isMessagesActive || isDropdownOpen,
      }"
      aria-label="Notifications"
      :aria-expanded="isDropdownOpen"
      @click="toggleDropdown">
      <Comments class="jr-shell-topbar__nav-icon" aria-hidden="true" />
      <span>Messages</span>
      <span
        v-if="chatStore.unreadTotal > 0"
        class="jr-shell-topbar__nav-badge jr-shell-topbar__nav-badge--unread">
        {{ chatStore.unreadTotal }}
        <span class="jr-shell-sidebar__sr-only">unread messages</span>
      </span>
    </button>
  </div>

  <!-- Mobile / Rail variant -->
  <div
    v-else-if="shouldShow"
    class="jr-shell-mobile-messages-wrap"
    :class="variantClass">
    <button
      type="button"
      class="jr-shell-messages"
      :class="variantClass"
      aria-label="Notifications"
      :aria-expanded="isDropdownOpen"
      @click="toggleDropdown">
      <Comments />
      <span
        v-if="chatStore.unreadTotal > 0"
        class="jr-shell-sidebar__badge"
        :class="{ 'jr-shell-sidebar__badge--rail': variant === 'rail' }">
        {{ chatStore.unreadTotal }}
        <span class="jr-shell-sidebar__sr-only">unread messages</span>
      </span>
    </button>
  </div>

  <!-- Notifications Popover Dropdown -->
  <Popover
    v-if="shouldShow"
    ref="popoverRef"
    :base-z-index="1060"
    :pt="popoverPt"
    @show="isDropdownOpen = true"
    @hide="isDropdownOpen = false">
    <div class="jr-notif-dropdown">
      <!-- Header -->
      <div class="jr-notif-dropdown__header">
        <div class="jr-notif-dropdown__title-wrap">
          <span class="jr-notif-dropdown__title">Notifications</span>
          <span
            v-if="chatStore.unreadTotal > 0"
            class="jr-notif-dropdown__total-badge">
            {{ chatStore.unreadTotal }}
          </span>
        </div>
        <button
          v-if="chatStore.unreadTotal > 0"
          type="button"
          class="jr-notif-dropdown__mark-all"
          @click="handleMarkAllAsRead">
          Mark all read
        </button>
      </div>

      <!-- Category Filter Tabs (Trim, Rough, etc.) -->
      <div v-if="categoryList.length > 1" class="jr-notif-dropdown__tabs">
        <button
          type="button"
          class="jr-notif-dropdown__tab"
          :class="{
            'jr-notif-dropdown__tab--active': selectedCategory === 'ALL',
          }"
          @click="selectedCategory = 'ALL'">
          All ({{ chatStore.unreadTotal }})
        </button>
        <button
          v-for="cat in categoryList"
          :key="cat.name"
          type="button"
          class="jr-notif-dropdown__tab"
          :class="{
            'jr-notif-dropdown__tab--active':
              selectedCategory.toLowerCase() === cat.name.toLowerCase(),
          }"
          @click="selectedCategory = cat.name">
          {{ cat.label }} ({{ cat.count }})
        </button>
      </div>

      <!-- Notifications List Area -->
      <div class="jr-notif-dropdown__body">
        <!-- Loading State -->
        <div
          v-if="chatStore.loadingDetails && !filteredNotifications.length"
          class="jr-notif-dropdown__loading">
          <span class="jr-notif-dropdown__spinner"></span>
          <span>Loading notifications...</span>
        </div>

        <!-- Empty State -->
        <div
          v-else-if="filteredNotifications.length === 0"
          class="jr-notif-dropdown__empty">
          <Comments class="jr-notif-dropdown__empty-icon" aria-hidden="true" />
          <span class="jr-notif-dropdown__empty-title">
            No unread notifications
          </span>
          <span class="jr-notif-dropdown__empty-sub">
            You're all caught up!
          </span>
        </div>

        <!-- Notifications Content -->
        <div v-else class="jr-notif-dropdown__list">
          <!-- When ALL is selected and multiple categories exist: group by category -->
          <template
            v-if="selectedCategory === 'ALL' && groupedNotifications.length > 1">
            <div
              v-for="group in groupedNotifications"
              :key="group.categoryName"
              class="jr-notif-group">
              <div class="jr-notif-group__header">
                <span class="jr-notif-group__title">
                  {{ group.categoryLabel }}
                </span>
                <span class="jr-notif-group__count">
                  {{ group.items.length }}
                </span>
              </div>
              <div class="jr-notif-group__items">
                <div
                  v-for="item in group.items"
                  :key="item.id"
                  class="jr-notif-card"
                  role="button"
                  tabindex="0"
                  @click="handleNotificationClick(item)"
                  @keydown.enter="handleNotificationClick(item)">
                  <div class="jr-notif-card__header-line">
                    <span class="jr-notif-card__title" :title="item.title">
                      {{ item.title }}
                    </span>
                    <div class="jr-notif-card__badges-group">
                      <span
                        class="jr-notif-card__category"
                        :class="getCategoryClass(item.crew_category)">
                        {{ formatCategory(item.crew_category) }}
                      </span>
                      <span class="jr-notif-card__unread-badge">
                        <Comments
                          class="jr-notif-card__unread-icon"
                          aria-hidden="true" />
                        {{ item.unread_messages }}
                      </span>
                    </div>
                  </div>
                  <div class="jr-notif-card__sub-line">
                    <div class="jr-notif-card__crew-and-date">
                      <span v-if="item.crew_title" class="jr-notif-card__crew">
                        {{ item.crew_title }}
                      </span>
                      <span v-if="item.date" class="jr-notif-card__date">
                        {{ item.date }}
                      </span>
                      <span
                        v-if="item.extended_service"
                        class="jr-notif-card__ext-badge">
                        Ext. Service
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- Flat list when filtered by specific category or only 1 category -->
          <template v-else>
            <div
              v-for="item in filteredNotifications"
              :key="item.id"
              class="jr-notif-card"
              role="button"
              tabindex="0"
              @click="handleNotificationClick(item)"
              @keydown.enter="handleNotificationClick(item)">
              <div class="jr-notif-card__header-line">
                <span class="jr-notif-card__title" :title="item.title">
                  {{ item.title }}
                </span>
                <div class="jr-notif-card__badges-group">
                  <span
                    class="jr-notif-card__category"
                    :class="getCategoryClass(item.crew_category)">
                    {{ formatCategory(item.crew_category) }}
                  </span>
                  <span class="jr-notif-card__unread-badge">
                    <Comments
                      class="jr-notif-card__unread-icon"
                      aria-hidden="true" />
                    {{ item.unread_messages }}
                  </span>
                </div>
              </div>
              <div class="jr-notif-card__sub-line">
                <div class="jr-notif-card__crew-and-date">
                  <span v-if="item.crew_title" class="jr-notif-card__crew">
                    {{ item.crew_title }}
                  </span>
                  <span v-if="item.date" class="jr-notif-card__date">
                    {{ item.date }}
                  </span>
                  <span
                    v-if="item.extended_service"
                    class="jr-notif-card__ext-badge">
                    Ext. Service
                  </span>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Footer -->
      <div class="jr-notif-dropdown__footer">
        <router-link
          to="/work-accounts"
          class="jr-notif-dropdown__footer-link"
          @click="closePopover">
          <span>View all in Work Accounts</span>
          <ArrowRight
            class="jr-notif-dropdown__footer-arrow"
            aria-hidden="true" />
        </router-link>
      </div>
    </div>
  </Popover>
</template>

<script>
import { getAccessToken } from '@/auth/tokenHelpers';
import Comments from "@primeicons/vue/comments";
import ArrowRight from "@primeicons/vue/arrow-right";
import Popover from "primevue/popover";
import SidebarMenuBadge from "primevue/sidebarmenubadge";
import SidebarMenuButton from "primevue/sidebarmenubutton";
import SidebarMenuItem from "primevue/sidebarmenuitem";
import { ref, onMounted, onBeforeUnmount, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useChatStore } from "@/stores/chatStore";
import axios from "axios";
import messageSound from "@/assets/sounds/mixkit-sci-fi-confirmation-914.wav";

const ensureTrailingSlash = (url = "") => (url.endsWith("/") ? url : `${url}/`);
const stripTrailingSlash = (url = "") => url.replace(/\/+$/, "");
const stripLeadingSlash = (path = "") => path.replace(/^\/+/, "");

const getWsBaseUrl = () => {
  const explicit = window.__WS_BASE_URL || "";
  if (explicit) return ensureTrailingSlash(explicit);
  const api = window.__API_BASE_URL || "";
  if (api.startsWith("https://")) return ensureTrailingSlash(`wss://${api.slice(8)}`);
  if (api.startsWith("http://")) return ensureTrailingSlash(`ws://${api.slice(7)}`);
  return ensureTrailingSlash(api);
};

const buildWsUrl = (path = "") => {
  const base = stripTrailingSlash(getWsBaseUrl());
  const cleanPath = stripLeadingSlash(path);
  return `${base}/${cleanPath}`;
};

export default {
  name: "NavbarMessagesDropdown",
  components: {
    ArrowRight,
    Comments,
    Popover,
    SidebarMenuBadge,
    SidebarMenuButton,
    SidebarMenuItem,
  },
  props: {
    variant: {
      type: String,
      default: "sidebar",
    },
  },
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    const chatStore = useChatStore();
    const popoverRef = ref(null);
    const isDropdownOpen = ref(false);
    const selectedCategory = ref("ALL");
    const ws = ref(null);
    const userId = ref(null);
    const lastUnreadTotal = ref(0);
    const audio = new Audio(messageSound);

    const popoverPt = {
      root: { class: "jr-overlay jr-shell-notifications-popover" },
      content: { class: "jr-shell-notifications-content" },
    };

    const variantClass = computed(() =>
      props.variant === "rail"
        ? "jr-shell-messages--rail"
        : "jr-shell-messages--full"
    );

    const shouldShow = computed(() => {
      if (route.meta?.hideNavbar) {
        return false;
      }

      const token = getAccessToken();
      if (!token) {
        return false;
      }

      const currentPath = window.location.pathname || route.path || "";
      const publicPaths = [
        "/onboarding",
        "/login",
        "/reset_password",
        "/reset-password-confirm",
      ];
      const isPublicRoute = publicPaths.some((path) =>
        currentPath.startsWith(path)
      );

      return !isPublicRoute;
    });

    const isMessagesActive = computed(() => {
      const path = route.path || "";
      return (
        path === "/work-accounts" ||
        path.startsWith("/work-accounts/") ||
        path === "/chat-general"
      );
    });

    const formatCategory = (cat) => {
      if (!cat) return "General";
      const cleaned = String(cat).replace(/^[\p{Emoji}\s\d]+/u, "").trim();
      if (!cleaned) return String(cat);
      return cleaned.charAt(0).toUpperCase() + cleaned.slice(1).toLowerCase();
    };

    const getCategoryClass = (cat) => {
      if (!cat) return "jr-notif-card__category--default";
      const lower = String(cat).toLowerCase();
      if (lower.includes("trim")) return "jr-notif-card__category--trim";
      if (lower.includes("rough") || lower.includes("routh")) {
        return "jr-notif-card__category--rough";
      }
      return "jr-notif-card__category--default";
    };

    const categoryList = computed(() => {
      const counts = {};
      chatStore.unreadNotifications.forEach((n) => {
        const rawCat = (n.crew_category || "General").trim();
        counts[rawCat] = (counts[rawCat] || 0) + (n.unread_messages || 0);
      });
      return Object.entries(counts).map(([name, count]) => ({
        name,
        label: formatCategory(name),
        count,
      }));
    });

    const filteredNotifications = computed(() => {
      if (selectedCategory.value === "ALL") {
        return chatStore.unreadNotifications;
      }
      return chatStore.unreadNotifications.filter((n) => {
        const cat = (n.crew_category || "General").trim();
        return cat.toLowerCase() === selectedCategory.value.toLowerCase();
      });
    });

    const groupedNotifications = computed(() => {
      const groupsMap = {};
      chatStore.unreadNotifications.forEach((item) => {
        const catKey = (item.crew_category || "General").trim();
        if (!groupsMap[catKey]) {
          groupsMap[catKey] = {
            categoryName: catKey,
            categoryLabel: formatCategory(catKey),
            items: [],
          };
        }
        groupsMap[catKey].items.push(item);
      });
      return Object.values(groupsMap);
    });

    const toggleDropdown = (event) => {
      if (popoverRef.value) {
        popoverRef.value.toggle(event);
      }
    };

    const closePopover = () => {
      if (popoverRef.value) {
        popoverRef.value.hide();
      }
    };

    const handleMarkAllAsRead = async () => {
      await chatStore.markAllAsRead();
    };

    const handleNotificationClick = async (item) => {
      if (!item) return;

      try {
        axios.post(`/api/mark-chat-read/${item.id}/`).catch(() => {});
        chatStore.markEventAsRead(item.id);
      } catch (err) {
        console.warn("Failed to mark chat as read:", err);
      }

      closePopover();

      let workAccountId = item.work_account;
      if (!workAccountId && item.title) {
        try {
          const res = await axios.get(
            `/api/work-accounts/?search=${encodeURIComponent(item.title)}`
          );
          const list = Array.isArray(res.data?.results)
            ? res.data.results
            : Array.isArray(res.data)
            ? res.data
            : [];
          if (list.length > 0) {
            workAccountId = list[0].id;
          }
        } catch (e) {
          console.warn("Could not find work account by title:", e);
        }
      }

      if (workAccountId) {
        router.push({
          path: `/work-accounts/${workAccountId}/view`,
          query: { tab: "chat", event: item.id },
        });
      } else {
        router.push({
          path: "/work-accounts/viewer",
          query: { tab: "chat", event: item.id },
        });
      }
    };

    const connectWebSocket = async () => {
      if (!shouldShow.value) return;

      const token = getAccessToken();
      if (!token) return;

      const currentPath = window.location.pathname || route.path || "";
      const publicPaths = [
        "/onboarding",
        "/login",
        "/reset_password",
        "/reset-password-confirm",
        "/about",
      ];
      if (publicPaths.some((path) => currentPath.startsWith(path))) {
        return;
      }

      try {
        const res = await axios.get("/api/auth/me/");
        userId.value = res.data.id;
        if (!userId.value) throw new Error("User ID not found.");

        ws.value = new WebSocket(
          buildWsUrl(`ws/schedule/unread/user/${userId.value}/`)
        );

        ws.value.onmessage = async (event) => {
          const data = JSON.parse(event.data);
          if (data.type === "unread.updated") {
            const { user_id: sender } = data;
            if (sender !== userId.value) {
              await chatStore.fetchUnreadEvents();
              if (chatStore.unreadTotal > lastUnreadTotal.value) {
                audio.play().catch(() => {});
              }
              lastUnreadTotal.value = chatStore.unreadTotal;
            }
          }
        };
      } catch (err) {
        if (err.response?.status !== 401) {
          console.error("Failed to connect WebSocket:", err);
        }
      }
    };

    onMounted(async () => {
      if (!shouldShow.value) return;

      const currentPath = window.location.pathname || route.path || "";
      const publicPaths = [
        "/onboarding",
        "/login",
        "/reset_password",
        "/reset-password-confirm",
        "/about",
      ];
      if (publicPaths.some((path) => currentPath.startsWith(path))) {
        return;
      }

      const token = getAccessToken();
      if (!token) return;

      try {
        await chatStore.fetchUnreadEvents();
        lastUnreadTotal.value = chatStore.unreadTotal;
        connectWebSocket();
      } catch (err) {
        if (err.response?.status !== 401) {
          console.warn("[NavbarMessagesDropdown] Error fetching unread events:", err);
        }
      }
    });

    onBeforeUnmount(() => {
      if (ws.value) ws.value.close();
    });

    return {
      chatStore,
      shouldShow,
      variantClass,
      isMessagesActive,
      popoverRef,
      isDropdownOpen,
      popoverPt,
      selectedCategory,
      categoryList,
      filteredNotifications,
      groupedNotifications,
      formatCategory,
      getCategoryClass,
      toggleDropdown,
      closePopover,
      handleMarkAllAsRead,
      handleNotificationClick,
    };
  },
};
</script>

<style scoped>
.jr-shell-topbar-messages-wrap {
  display: inline-flex;
  align-items: center;
  position: relative;
}

.jr-shell-mobile-messages-wrap {
  display: inline-flex;
  align-items: center;
  position: relative;
}

.jr-shell-messages {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface);
  color: var(--color-jr-text);
  text-decoration: none;
  cursor: pointer;
}

.jr-shell-messages svg {
  width: 1.125rem;
  height: 1.125rem;
}

.jr-shell-sidebar__badge--rail {
  position: absolute;
  top: 0.1rem;
  right: 0.1rem;
  min-width: 1rem;
  padding: 0.05rem 0.25rem;
  font-size: 0.75rem;
  margin-left: 0;
}

.jr-shell-sidebar__sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
