<template>
  <JRPage class="jr-user-admin jr-user-admin-hub">
    <JRPageHeader
      title="User permissions"
      :description="isMobile ? '' : pageDescription">
      <template #actions>
        <JRButton
          v-if="activeTab === 'users'"
          type="button"
          @click="goCreateUser">
          + New user
        </JRButton>
        <JRButton
          v-else
          type="button"
          @click="goCreateGroup">
          + New role
        </JRButton>
      </template>
    </JRPageHeader>

    <Tabs v-model:value="activeTab" class="jr-user-admin-hub__tabs">
      <TabList>
        <Tab value="users">Users</Tab>
        <Tab value="groups">Roles (Groups)</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="users">
          <JRToolbar>
            <template #start>
              <div class="jr-user-admin-hub__search">
                <label class="jr-sr-only" for="user-admin-user-filter">
                  Search users
                </label>
                <span class="jr-user-admin-hub__search-icon" aria-hidden="true">
                  <SearchIcon />
                </span>
                <JRInput
                  inputId="user-admin-user-filter"
                  v-model="userFilter"
                  type="search"
                  placeholder="Search users…"
                  autocomplete="off"
                  :spellcheck="false"
                  autocapitalize="none"
                  autocorrect="off"
                  enterkeyhint="search" />
              </div>
            </template>
            <template v-if="!isMobile" #stats>
              <div class="jr-user-admin-hub__summary" aria-live="polite">
                <JRBadge :value="`${userStats.total} Total`" severity="secondary" />
                <JRBadge
                  :value="`${userStats.active} Active`"
                  :severity="userStats.active > 0 ? 'success' : 'secondary'" />
                <JRBadge
                  :value="`${userStats.staff} Staff`"
                  :severity="userStats.staff > 0 ? 'info' : 'secondary'" />
              </div>
            </template>
            <template #actions>
              <template v-if="!isMobile">
                <JRButton
                  type="button"
                  variant="ghost"
                  size="sm"
                  class="jr-user-admin-hub__refresh"
                  @click="loadUsers">
                  <RefreshIcon />
                  Refresh
                </JRButton>
              </template>
              <template v-else>
                <button
                  id="user-admin-users-tools-trigger"
                  type="button"
                  class="jr-icon-btn"
                  aria-label="List tools"
                  aria-haspopup="menu"
                  :aria-expanded="usersToolsOpen ? 'true' : 'false'"
                  aria-controls="user-admin-users-tools-menu"
                  @click="toggleUsersTools">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    aria-hidden="true"
                    fill="currentColor">
                    <circle cx="8" cy="3" r="1.4" />
                    <circle cx="8" cy="8" r="1.4" />
                    <circle cx="8" cy="13" r="1.4" />
                  </svg>
                </button>
                <Menu
                  id="user-admin-users-tools-menu"
                  ref="usersToolsMenu"
                  class="jr-overlay jr-row-menu"
                  :model="usersToolsModel"
                  :popup="true"
                  ariaLabel="List tools"
                  @show="usersToolsOpen = true"
                  @hide="usersToolsOpen = false" />
              </template>
            </template>
          </JRToolbar>

          <!-- Phone: scan list (pilot Product List) -->
          <div v-if="isMobile" class="jr-user-admin-hub__mobile">
            <JREmptyState
              v-if="!filteredUsers.length && !usersLoading"
              :title="usersEmptyTitle"
              :description="usersEmptyDescription">
              <JRButton
                v-if="userFilter.trim()"
                type="button"
                variant="ghost"
                size="sm"
                @click="userFilter = ''">
                Clear search
              </JRButton>
              <JRButton
                v-else
                type="button"
                variant="ghost"
                size="sm"
                @click="loadUsers">
                Refresh
              </JRButton>
            </JREmptyState>
            <p
              v-if="usersLoading && !filteredUsers.length"
              class="jr-user-admin-hub__loading">
              Loading users…
            </p>
            <p
              v-else-if="usersLoading && filteredUsers.length"
              class="jr-user-admin-hub__loading"
              aria-live="polite">
              Updating…
            </p>
            <ul
              v-if="filteredUsers.length"
              class="jr-user-admin-hub__rows"
              :aria-busy="usersLoading ? 'true' : 'false'">
              <li
                v-for="item in filteredUsers"
                :key="item.id"
                class="jr-user-admin-row">
                <div class="jr-user-admin-row__main">
                  <div class="jr-user-admin-cell">
                    <span class="jr-user-admin-cell__text">
                      <router-link
                        class="jr-user-admin-cell__name jr-user-admin-cell__name--link"
                        :to="userViewTo(item.id)"
                        :aria-label="`View ${item.username}`">
                        {{ item.username }}
                      </router-link>
                    </span>
                    <span
                      class="jr-user-admin-cell__avatar"
                      aria-hidden="true">
                      {{ userInitials(item) }}
                    </span>
                  </div>
                  <p class="jr-user-admin-row__meta">
                    <span>{{ item.email || 'No email' }}</span>
                    <span aria-hidden="true"> · </span>
                    <span>
                      {{ item.group_count || 0 }}
                      {{ Number(item.group_count) === 1 ? 'role' : 'roles' }}
                    </span>
                    <JRBadge
                      v-if="item.is_staff"
                      value="Staff"
                      severity="info" />
                  </p>
                </div>
                <div class="jr-user-admin-row__aside">
                  <JRBadge
                    :value="item.is_active ? 'Active' : 'Inactive'"
                    :severity="item.is_active ? 'success' : 'secondary'" />
                  <JRRowActions
                    :actions="userRowActions(item)"
                    :compact="true"
                    :entity-label="item.username" />
                </div>
              </li>
            </ul>
          </div>

          <!-- Tablet / desktop: data table -->
          <div v-else class="jr-user-admin-hub__table">
            <JRDataTable
              :value="filteredUsers"
              :loading="usersLoading"
              dataKey="id"
              paginator
              :rows="25"
              stripedRows
              scrollable
              :tableStyle="usersTableStyle"
              emptyTitle="No users found"
              emptyDescription="Create a user or adjust your search.">
              <Column field="username" header="Username" sortable>
                <template #body="{ data }">
                  <router-link
                    class="jr-master-row__name jr-master-row__name--link"
                    :to="userViewTo(data.id)">
                    {{ data.username }}
                  </router-link>
                </template>
              </Column>
              <Column
                v-if="!isTablet"
                field="email"
                header="Email"
                sortable>
                <template #body="{ data }">
                  {{ data.email || '—' }}
                </template>
              </Column>
              <Column field="group_count" header="Roles" sortable />
              <Column
                v-if="!isTablet"
                field="is_staff"
                header="Staff"
                sortable>
                <template #body="{ data }">
                  <JRBadge
                    :value="data.is_staff ? 'Yes' : 'No'"
                    :severity="data.is_staff ? 'info' : 'secondary'" />
                </template>
              </Column>
              <Column field="is_active" header="Status" sortable>
                <template #body="{ data }">
                  <JRBadge
                    :value="data.is_active ? 'Active' : 'Inactive'"
                    :severity="data.is_active ? 'success' : 'secondary'" />
                </template>
              </Column>
              <Column
                header="Actions"
                :sortable="false"
                :headerClass="actionsHeaderClass"
                :bodyClass="actionsBodyClass">
                <template #body="{ data }">
                  <JRRowActions
                    :actions="userRowActions(data)"
                    :compact="isTablet"
                    :entity-label="data.username" />
                </template>
              </Column>
            </JRDataTable>
          </div>
        </TabPanel>

        <TabPanel value="groups">
          <JRToolbar>
            <template #start>
              <div class="jr-user-admin-hub__search">
                <label class="jr-sr-only" for="user-admin-group-filter">
                  Search roles
                </label>
                <span class="jr-user-admin-hub__search-icon" aria-hidden="true">
                  <SearchIcon />
                </span>
                <JRInput
                  inputId="user-admin-group-filter"
                  v-model="groupFilter"
                  type="search"
                  placeholder="Search roles…"
                  autocomplete="off"
                  :spellcheck="false"
                  autocapitalize="none"
                  autocorrect="off"
                  enterkeyhint="search" />
              </div>
            </template>
            <template v-if="!isMobile" #stats>
              <div class="jr-user-admin-hub__summary" aria-live="polite">
                <JRBadge :value="`${groupStats.total} Total`" severity="secondary" />
              </div>
            </template>
            <template #actions>
              <template v-if="!isMobile">
                <JRButton
                  type="button"
                  variant="ghost"
                  size="sm"
                  class="jr-user-admin-hub__refresh"
                  @click="loadGroups">
                  <RefreshIcon />
                  Refresh
                </JRButton>
              </template>
              <template v-else>
                <button
                  id="user-admin-groups-tools-trigger"
                  type="button"
                  class="jr-icon-btn"
                  aria-label="List tools"
                  aria-haspopup="menu"
                  :aria-expanded="groupsToolsOpen ? 'true' : 'false'"
                  aria-controls="user-admin-groups-tools-menu"
                  @click="toggleGroupsTools">
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    aria-hidden="true"
                    fill="currentColor">
                    <circle cx="8" cy="3" r="1.4" />
                    <circle cx="8" cy="8" r="1.4" />
                    <circle cx="8" cy="13" r="1.4" />
                  </svg>
                </button>
                <Menu
                  id="user-admin-groups-tools-menu"
                  ref="groupsToolsMenu"
                  class="jr-overlay jr-row-menu"
                  :model="groupsToolsModel"
                  :popup="true"
                  ariaLabel="List tools"
                  @show="groupsToolsOpen = true"
                  @hide="groupsToolsOpen = false" />
              </template>
            </template>
          </JRToolbar>

          <div v-if="isMobile" class="jr-user-admin-hub__mobile">
            <JREmptyState
              v-if="!filteredGroups.length && !groupsLoading"
              :title="groupsEmptyTitle"
              :description="groupsEmptyDescription">
              <JRButton
                v-if="groupFilter.trim()"
                type="button"
                variant="ghost"
                size="sm"
                @click="groupFilter = ''">
                Clear search
              </JRButton>
              <JRButton
                v-else
                type="button"
                variant="ghost"
                size="sm"
                @click="loadGroups">
                Refresh
              </JRButton>
            </JREmptyState>
            <p
              v-if="groupsLoading && !filteredGroups.length"
              class="jr-user-admin-hub__loading">
              Loading roles…
            </p>
            <p
              v-else-if="groupsLoading && filteredGroups.length"
              class="jr-user-admin-hub__loading"
              aria-live="polite">
              Updating…
            </p>
            <ul
              v-if="filteredGroups.length"
              class="jr-user-admin-hub__rows"
              :aria-busy="groupsLoading ? 'true' : 'false'">
              <li
                v-for="item in filteredGroups"
                :key="item.id"
                class="jr-user-admin-row">
                <div class="jr-user-admin-row__main">
                  <div class="jr-user-admin-cell">
                    <span class="jr-user-admin-cell__text">
                      <router-link
                        class="jr-user-admin-cell__name jr-user-admin-cell__name--link"
                        :to="groupViewTo(item.id)"
                        :aria-label="`View ${item.name}`">
                        {{ item.name }}
                      </router-link>
                    </span>
                    <span
                      class="jr-user-admin-cell__avatar"
                      aria-hidden="true">
                      {{ roleInitials(item) }}
                    </span>
                  </div>
                  <p class="jr-user-admin-row__meta">
                    <span>
                      {{ item.permission_count || 0 }}
                      {{
                        Number(item.permission_count) === 1
                          ? 'permission'
                          : 'permissions'
                      }}
                    </span>
                    <span aria-hidden="true"> · </span>
                    <span>
                      {{ item.user_count || 0 }}
                      {{ Number(item.user_count) === 1 ? 'user' : 'users' }}
                    </span>
                  </p>
                </div>
                <div class="jr-user-admin-row__aside">
                  <span
                    class="jr-user-admin-row__stat"
                    :aria-label="`${item.permission_count || 0} permissions`">
                    {{ item.permission_count || 0 }}
                  </span>
                  <JRRowActions
                    :actions="groupRowActions(item)"
                    :compact="true"
                    :entity-label="item.name" />
                </div>
              </li>
            </ul>
          </div>

          <div v-else class="jr-user-admin-hub__table">
            <JRDataTable
              :value="filteredGroups"
              :loading="groupsLoading"
              dataKey="id"
              paginator
              :rows="25"
              stripedRows
              scrollable
              :tableStyle="groupsTableStyle"
              emptyTitle="No roles found"
              emptyDescription="Create a role to bundle permissions for your team.">
              <Column field="name" header="Role" sortable>
                <template #body="{ data }">
                  <router-link
                    class="jr-master-row__name jr-master-row__name--link"
                    :to="groupViewTo(data.id)">
                    {{ data.name }}
                  </router-link>
                </template>
              </Column>
              <Column field="permission_count" header="Permissions" sortable />
              <Column field="user_count" header="Users" sortable />
              <Column
                header="Actions"
                :sortable="false"
                :headerClass="actionsHeaderClass"
                :bodyClass="actionsBodyClass">
                <template #body="{ data }">
                  <JRRowActions
                    :actions="groupRowActions(data)"
                    :compact="isTablet"
                    :entity-label="data.name" />
                </template>
              </Column>
            </JRDataTable>
          </div>
        </TabPanel>
      </TabPanels>
    </Tabs>
  </JRPage>
</template>

<script>
import axios from 'axios';
import Column from 'primevue/column';
import Menu from 'primevue/menu';
import Tab from 'primevue/tab';
import TabList from 'primevue/tablist';
import TabPanel from 'primevue/tabpanel';
import TabPanels from 'primevue/tabpanels';
import Tabs from 'primevue/tabs';
import EyeIcon from '@primevue/icons/eye';
import PencilIcon from '@primevue/icons/pencil';
import RefreshIcon from '@primevue/icons/refresh';
import SearchIcon from '@primevue/icons/search';
import TrashIcon from '@primevue/icons/trash';
import {
  JRPage,
  JRPageHeader,
  JRToolbar,
  JRButton,
  JRInput,
  JRBadge,
  JRDataTable,
  JREmptyState,
  JRRowActions,
} from '@/ui';

const PHONE_MQ = '(max-width: 767.98px)';
const TABLET_MQ = '(min-width: 768px) and (max-width: 1023.98px)';

export default {
  name: 'UserPermissionsHub',
  components: {
    Column,
    Menu,
    Tab,
    TabList,
    TabPanel,
    TabPanels,
    Tabs,
    RefreshIcon,
    SearchIcon,
    JRPage,
    JRPageHeader,
    JRToolbar,
    JRButton,
    JRInput,
    JRBadge,
    JRDataTable,
    JREmptyState,
    JRRowActions,
  },
  data() {
    return {
      activeTab: this.$route.query.tab === 'groups' ? 'groups' : 'users',
      users: [],
      groups: [],
      usersLoading: false,
      groupsLoading: false,
      userFilter: '',
      groupFilter: '',
      currentUserId: null,
      currentUserIsSuperuser: false,
      isMobile: false,
      isTablet: false,
      usersToolsOpen: false,
      groupsToolsOpen: false,
      pageDescription:
        'Manage users, roles (groups), and permissions for this company.',
    };
  },
  computed: {
    actionsHeaderClass() {
      return this.isTablet
        ? 'jr-col-actions jr-col-actions--compact'
        : 'jr-col-actions';
    },
    actionsBodyClass() {
      return this.actionsHeaderClass;
    },
    usersTableStyle() {
      return this.isTablet ? 'min-width: 36rem' : 'min-width: 48rem';
    },
    groupsTableStyle() {
      return this.isTablet ? 'min-width: 32rem' : 'min-width: 40rem';
    },
    filteredUsers() {
      const q = this.userFilter.trim().toLowerCase();
      if (!q) return this.users;
      return this.users.filter((row) => {
        const hay = [row.username, row.email, row.first_name, row.last_name]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        return hay.includes(q);
      });
    },
    filteredGroups() {
      const q = this.groupFilter.trim().toLowerCase();
      if (!q) return this.groups;
      return this.groups.filter((row) =>
        String(row.name || '')
          .toLowerCase()
          .includes(q),
      );
    },
    userStats() {
      const total = this.users.length;
      const active = this.users.filter((u) => u.is_active).length;
      const staff = this.users.filter((u) => u.is_staff).length;
      return { total, active, staff };
    },
    groupStats() {
      return { total: this.groups.length };
    },
    usersEmptyTitle() {
      return this.userFilter.trim() ? 'No users found' : 'No users yet';
    },
    usersEmptyDescription() {
      if (this.userFilter.trim()) {
        return `No users match “${this.userFilter.trim()}”.`;
      }
      return 'Create a user to grant access for this company.';
    },
    groupsEmptyTitle() {
      return this.groupFilter.trim() ? 'No roles found' : 'No roles yet';
    },
    groupsEmptyDescription() {
      if (this.groupFilter.trim()) {
        return `No roles match “${this.groupFilter.trim()}”.`;
      }
      return 'Create a role to bundle permissions for your team.';
    },
    usersToolsModel() {
      return [{ label: 'Refresh', command: () => this.loadUsers() }];
    },
    groupsToolsModel() {
      return [{ label: 'Refresh', command: () => this.loadGroups() }];
    },
  },
  watch: {
    activeTab: {
      immediate: true,
      handler(value) {
        if (this.$route.query.tab !== value) {
          this.$router.replace({
            name: 'user-permissions',
            query: { ...this.$route.query, tab: value },
          });
        }
        if (value === 'users') this.loadUsers();
        else this.loadGroups();
      },
    },
  },
  mounted() {
    this.bindViewport();
    this.getAuthenticatedUser().then((me) => {
      this.currentUserId = me?.id ?? null;
      this.currentUserIsSuperuser = !!me?.is_superuser;
    });
  },
  beforeUnmount() {
    this.unbindViewport();
  },
  methods: {
    bindViewport() {
      if (typeof window === 'undefined' || !window.matchMedia) return;
      this.phoneQuery = window.matchMedia(PHONE_MQ);
      this.tabletQuery = window.matchMedia(TABLET_MQ);
      this.isMobile = this.phoneQuery.matches;
      this.isTablet = this.tabletQuery.matches;
      this.onPhoneChange = (event) => {
        this.isMobile = event.matches;
      };
      this.onTabletChange = (event) => {
        this.isTablet = event.matches;
      };
      if (this.phoneQuery.addEventListener) {
        this.phoneQuery.addEventListener('change', this.onPhoneChange);
        this.tabletQuery.addEventListener('change', this.onTabletChange);
      } else {
        this.phoneQuery.addListener(this.onPhoneChange);
        this.tabletQuery.addListener(this.onTabletChange);
      }
    },
    unbindViewport() {
      if (this.phoneQuery && this.onPhoneChange) {
        if (this.phoneQuery.removeEventListener) {
          this.phoneQuery.removeEventListener('change', this.onPhoneChange);
        } else {
          this.phoneQuery.removeListener(this.onPhoneChange);
        }
      }
      if (this.tabletQuery && this.onTabletChange) {
        if (this.tabletQuery.removeEventListener) {
          this.tabletQuery.removeEventListener('change', this.onTabletChange);
        } else {
          this.tabletQuery.removeListener(this.onTabletChange);
        }
      }
    },
    toggleUsersTools(event) {
      this.$refs.usersToolsMenu?.toggle(event);
    },
    toggleGroupsTools(event) {
      this.$refs.groupsToolsMenu?.toggle(event);
    },
    userInitials(row) {
      const first = String(row.first_name || '').trim();
      const last = String(row.last_name || '').trim();
      if (first || last) {
        return `${first.charAt(0)}${last.charAt(0)}`.toUpperCase() || '?';
      }
      const name = String(row.username || '?');
      return name.slice(0, 2).toUpperCase();
    },
    roleInitials(row) {
      const name = String(row.name || '?').trim();
      const parts = name.split(/\s+/).filter(Boolean);
      if (parts.length >= 2) {
        return `${parts[0].charAt(0)}${parts[1].charAt(0)}`.toUpperCase();
      }
      return name.slice(0, 2).toUpperCase();
    },
    userViewTo(id) {
      return { name: 'user-permissions-user-detail', params: { id } };
    },
    groupViewTo(id) {
      return { name: 'user-permissions-group-detail', params: { id } };
    },
    goCreateUser() {
      this.$router.push({ name: 'user-permissions-user-new' });
    },
    goCreateGroup() {
      this.$router.push({ name: 'user-permissions-group-new' });
    },
    userRowActions(row) {
      const isSelf = Number(row.id) === Number(this.currentUserId);
      const lockedSuper =
        !!row.is_superuser && !this.currentUserIsSuperuser;
      const actions = [
        {
          key: 'view',
          label: 'View',
          severity: 'success',
          icon: EyeIcon,
          command: () =>
            this.$router.push({
              name: 'user-permissions-user-detail',
              params: { id: row.id },
            }),
        },
      ];
      if (!lockedSuper) {
        actions.push({
          key: 'edit',
          label: 'Edit',
          severity: 'primary',
          icon: PencilIcon,
          command: () =>
            this.$router.push({
              name: 'user-permissions-user-edit',
              params: { id: row.id },
              query: { mode: 'edit' },
            }),
        });
      } else if (!this.isMobile) {
        actions.push({
          key: 'edit-placeholder',
          label: 'Edit',
          severity: 'primary',
          icon: PencilIcon,
          buttonClass: 'jr-row-actions__btn--placeholder',
          disabled: true,
          command: () => {},
        });
      }
      if (!isSelf && !lockedSuper) {
        actions.push({
          key: 'delete',
          label: 'Delete',
          severity: 'danger',
          icon: TrashIcon,
          command: () =>
            this.confirmDelete(
              'Delete this user?',
              `${row.username} will be permanently removed.`,
              () => this.deleteUser(row.id),
            ),
        });
      } else if (!this.isMobile) {
        actions.push({
          key: 'delete-placeholder',
          label: 'Delete',
          severity: 'danger',
          icon: TrashIcon,
          buttonClass: 'jr-row-actions__btn--placeholder',
          disabled: true,
          command: () => {},
        });
      }
      return actions;
    },
    groupRowActions(row) {
      return [
        {
          key: 'view',
          label: 'View',
          severity: 'success',
          icon: EyeIcon,
          command: () =>
            this.$router.push({
              name: 'user-permissions-group-detail',
              params: { id: row.id },
            }),
        },
        {
          key: 'edit',
          label: 'Edit',
          severity: 'primary',
          icon: PencilIcon,
          command: () =>
            this.$router.push({
              name: 'user-permissions-group-edit',
              params: { id: row.id },
              query: { mode: 'edit' },
            }),
        },
        {
          key: 'delete',
          label: 'Delete',
          severity: 'danger',
          icon: TrashIcon,
          command: () =>
            this.confirmDelete(
              'Delete this role?',
              `Users in “${row.name}” will lose its permissions.`,
              () => this.deleteGroup(row.id),
            ),
        },
      ];
    },
    async loadUsers() {
      this.usersLoading = true;
      try {
        const { data } = await axios.get('/api/auth/admin/users/');
        this.users = Array.isArray(data) ? data : [];
      } catch (err) {
        this.users = [];
        this.notifyToastError(
          err?.response?.data?.detail || 'Could not load users.',
        );
      } finally {
        this.usersLoading = false;
      }
    },
    async loadGroups() {
      this.groupsLoading = true;
      try {
        const { data } = await axios.get('/api/auth/admin/groups/');
        this.groups = Array.isArray(data) ? data : [];
      } catch (err) {
        this.groups = [];
        this.notifyToastError(
          err?.response?.data?.detail || 'Could not load roles.',
        );
      } finally {
        this.groupsLoading = false;
      }
    },
    async deleteUser(id) {
      try {
        await axios.delete(`/api/auth/admin/users/${id}/`);
        this.notifyToastSuccess('User deleted.');
        await this.loadUsers();
      } catch (err) {
        this.notifyToastError(
          err?.response?.data?.detail || 'Could not delete the user.',
        );
      }
    },
    async deleteGroup(id) {
      try {
        await axios.delete(`/api/auth/admin/groups/${id}/`);
        this.notifyToastSuccess('Role deleted.');
        await this.loadGroups();
      } catch (err) {
        this.notifyToastError(
          err?.response?.data?.detail || 'Could not delete the role.',
        );
      }
    },
  },
};
</script>

<style scoped>
.jr-user-admin-hub__tabs {
  margin-top: 0.25rem;
}
:deep(.p-tablist) {
  margin-bottom: 0.75rem;
}

.jr-user-admin-hub__search {
  position: relative;
  min-width: 0;
  width: 100%;
}

.jr-user-admin-hub__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-user-admin-hub__search-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.jr-user-admin-hub__search :deep(.p-inputtext) {
  padding-left: 2.25rem;
}

.jr-user-admin-hub__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  pointer-events: none;
}

.jr-user-admin-hub__loading {
  margin: 0;
  padding: 1rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-user-admin-hub__rows {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: 1px solid var(--color-jr-border);
}

.jr-user-admin-hub__rows[aria-busy='true'] {
  opacity: 0.55;
}

.jr-user-admin-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-user-admin-row__main {
  min-width: 0;
  flex: 1 1 auto;
  text-align: left;
}

.jr-user-admin-cell {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  max-width: 100%;
  min-width: 0;
}

.jr-user-admin-cell__avatar {
  order: -1;
  flex-shrink: 0;
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  border: 1px dashed var(--color-jr-border);
  border-radius: var(--radius-jr-control);
  background: var(--color-jr-surface-muted);
  color: var(--color-jr-muted);
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1;
}

.jr-user-admin-cell__text {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.1rem;
}

.jr-user-admin-cell__name {
  color: var(--color-jr-text);
  font-weight: 600;
  font-size: 0.875rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

a.jr-user-admin-cell__name--link {
  color: var(--color-jr-primary);
  text-decoration: none;
}

a.jr-user-admin-cell__name--link:hover {
  color: var(--color-jr-primary-hover);
  text-decoration: underline;
}

a.jr-user-admin-cell__name--link:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-user-admin-row__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0.2rem 0 0 calc(2.75rem + 0.75rem);
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-user-admin-row__aside {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.35rem;
  flex-shrink: 0;
}

.jr-user-admin-row__stat {
  font-size: 0.875rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--color-jr-text);
}

@media (max-width: 767.98px) {
  :deep(.jr-page-header) {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  :deep(.jr-page-header__actions) {
    flex-shrink: 0;
  }

  :deep(.jr-toolbar) {
    flex-direction: row;
    flex-wrap: nowrap;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0 0.5rem;
    margin-bottom: 0.5rem;
  }

  :deep(.jr-toolbar__start) {
    flex: 1 1 auto;
    min-width: 0;
  }

  :deep(.jr-toolbar__actions) {
    flex: 0 0 auto;
  }
}

.jr-user-admin-hub__table :deep(.p-datatable) {
  --p-datatable-row-striped-background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
}

.jr-user-admin-hub__table :deep(.p-datatable-table-container) {
  overflow-x: auto;
}

.jr-user-admin-hub__table :deep(.p-datatable-thead > tr > th) {
  background: var(--color-jr-surface-muted);
  color: var(--color-jr-text);
  font-size: 0.875rem;
  font-weight: 600;
}

.jr-user-admin-hub__table :deep(.p-datatable-tbody > tr > td) {
  font-size: 0.875rem;
  vertical-align: middle;
  padding-top: 0.3rem;
  padding-bottom: 0.3rem;
}

.jr-user-admin-hub__table :deep(th.jr-col-actions),
.jr-user-admin-hub__table :deep(td.jr-col-actions) {
  width: 16.5rem;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
}

.jr-user-admin-hub__table :deep(th.jr-col-actions.jr-col-actions--compact),
.jr-user-admin-hub__table :deep(td.jr-col-actions.jr-col-actions--compact) {
  width: 3.25rem;
  min-width: 3.25rem;
}

.jr-user-admin-hub__table
  :deep(th.jr-col-actions .p-datatable-column-header-content),
.jr-user-admin-hub__table :deep(td.jr-col-actions .jr-row-actions) {
  display: flex;
  justify-content: center;
  width: 100%;
}

.jr-user-admin-hub__table :deep(td.jr-col-actions .jr-row-actions) {
  flex-wrap: nowrap;
  align-items: center;
  gap: 0.15rem;
}

.jr-user-admin-hub__table
  :deep(td.jr-col-actions .jr-row-actions__btn--placeholder.p-button) {
  visibility: hidden;
  pointer-events: none;
}

a.jr-master-row__name--link {
  color: var(--color-jr-primary);
  font-weight: 600;
  text-decoration: none;
}

a.jr-master-row__name--link:hover {
  color: var(--color-jr-primary-hover);
  text-decoration: underline;
}
</style>
