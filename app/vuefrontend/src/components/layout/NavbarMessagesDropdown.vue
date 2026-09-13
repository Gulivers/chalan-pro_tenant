<template>
  <SidebarMenuItem v-if="shouldShow && variant === 'sidebar'">
    <SidebarMenuButton :is-active="isMessagesActive" @click="goToMessages">
      <Comments />
      <span>Messages</span>
    </SidebarMenuButton>
    <SidebarMenuBadge v-if="chatStore.unreadTotal > 0">
      {{ chatStore.unreadTotal }}
      <span class="jr-shell-sidebar__sr-only">unread messages</span>
    </SidebarMenuBadge>
  </SidebarMenuItem>

  <router-link
    v-else-if="shouldShow && variant === 'topbar'"
    to="/chat-general"
    class="jr-shell-topbar__nav-link jr-shell-topbar__nav-link--messages"
    :class="{ 'jr-shell-topbar__nav-link--active': isMessagesActive }"
    aria-label="Messages">
    <Comments class="jr-shell-topbar__nav-icon" aria-hidden="true" />
    <span>Messages</span>
    <span
      v-if="chatStore.unreadTotal > 0"
      class="jr-shell-topbar__nav-badge">
      {{ chatStore.unreadTotal }}
      <span class="jr-shell-sidebar__sr-only">unread messages</span>
    </span>
  </router-link>

  <router-link
    v-else-if="shouldShow"
    to="/chat-general"
    class="jr-shell-messages"
    :class="variantClass"
    aria-label="Messages"
    @click="closeMobileNav">
    <Comments />
    <span
      v-if="chatStore.unreadTotal > 0"
      class="jr-shell-sidebar__badge"
      :class="{ 'jr-shell-sidebar__badge--rail': variant === 'rail' }">
      {{ chatStore.unreadTotal }}
      <span class="jr-shell-sidebar__sr-only">unread messages</span>
    </span>
  </router-link>
</template>

<script>
import Comments from "@primeicons/vue/comments";
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
  components: {
    Comments,
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
    const ws = ref(null);
    const userId = ref(null);
    const lastUnreadTotal = ref(0);
    const audio = new Audio(messageSound);

    const variantClass = computed(() =>
      props.variant === "rail" ? "jr-shell-messages--rail" : "jr-shell-messages--full"
    );

    const shouldShow = computed(() => {
      if (route.meta.hideNavbar) {
        return false;
      }

      const token = localStorage.getItem("authToken");
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
      return path === "/chat-general" || path.startsWith("/chat-general/");
    });

    const connectWebSocket = async () => {
      if (!shouldShow.value) {
        return;
      }

      const token = localStorage.getItem("authToken");
      if (!token) {
        return;
      }

      const currentPath = window.location.pathname || route.path || "";
      const publicPaths = [
        "/onboarding",
        "/login",
        "/reset_password",
        "/reset-password-confirm",
        "/about",
      ];
      const isPublicRoute = publicPaths.some((path) =>
        currentPath.startsWith(path)
      );

      if (isPublicRoute) {
        return;
      }

      try {
        const res = await axios.get("/api/user_detail/");
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

    const goToMessages = () => {
      router.push("/chat-general");
    };

    const closeMobileNav = () => {
      document.body.style.overflow = "";
    };

    onMounted(async () => {
      if (!shouldShow.value) {
        return;
      }

      const currentPath = window.location.pathname || route.path || "";
      const publicPaths = [
        "/onboarding",
        "/login",
        "/reset_password",
        "/reset-password-confirm",
        "/about",
      ];
      const isPublicRoute = publicPaths.some((path) =>
        currentPath.startsWith(path)
      );

      if (isPublicRoute) {
        return;
      }

      const token = localStorage.getItem("authToken");
      if (!token) {
        return;
      }

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
      goToMessages,
      closeMobileNav,
    };
  },
};
</script>

<style scoped>
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
