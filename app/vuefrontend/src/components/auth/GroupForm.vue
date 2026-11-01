<template>
  <JRPage class="jr-user-admin">
    <JRPageHeader :title="pageTitle" :description="pageDescription">
      <template #actions>
        <JRButton
          v-if="isReadOnly && groupId"
          type="button"
          variant="primary"
          size="sm"
          @click="goEdit">
          Edit role
        </JRButton>
      </template>
    </JRPageHeader>

    <form class="jr-user-admin-form" @submit.prevent="handleSubmit" novalidate>
      <div
        v-if="attentionCount || formBannerMessage"
        ref="formBanner"
        class="jr-form-banner"
        role="alert"
        tabindex="-1">
        {{
          formBannerMessage ||
          `${attentionCount} ${attentionCount === 1 ? 'field needs' : 'fields need'} attention`
        }}
      </div>

      <p v-if="loading" class="jr-user-admin-form__status" role="status">
        Loading role…
      </p>

      <template v-else>
        <JRSection title="Role">
          <div class="jr-form-grid jr-form-grid--identity">
            <JRField
              v-slot="{ describedby, invalid }"
              class="jr-user-admin-form__identity-field"
              label="Name"
              required
              inputId="group-name"
              hint="Name of this role (Django Group)."
              :error="fieldErrors.name">
              <JRInput
                inputId="group-name"
                v-model="form.name"
                maxlength="150"
                :disabled="isReadOnly"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('name')" />
            </JRField>
          </div>
        </JRSection>

        <JRSection title="Permissions">
          <div class="jr-user-admin-form__assignments">
            <p class="jr-user-admin-form__note">
              Members of this role receive every permission listed on the right.
            </p>
            <div class="jr-user-admin-form__pick">
              <DualListPick
                v-model="permissionLists"
                source-header="Available permissions"
                target-header="Chosen permissions"
                filter-placeholder="Filter"
                :disabled="isReadOnly"
                hint="Hold Ctrl (Windows) or ⌘ (Mac) to select more than one, then move with the arrows." />
            </div>
          </div>
        </JRSection>

        <div class="jr-user-admin-form__actions">
          <JRButton
            type="submit"
            variant="primary"
            :disabled="isReadOnly || submitting">
            {{ submitting ? 'Saving…' : groupId ? 'Update' : 'Save' }}
          </JRButton>
          <JRButton type="button" variant="secondary" @click="goBack">
            {{ isReadOnly ? 'Back to list' : 'Cancel' }}
          </JRButton>
          <JRButton
            v-if="groupId && !isReadOnly"
            type="button"
            variant="danger"
            :disabled="submitting"
            @click="confirmRemove">
            Delete
          </JRButton>
        </div>
      </template>
    </form>
  </JRPage>
</template>

<script>
import axios from 'axios';
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRButton,
  JRInput,
} from '@/ui';
import DualListPick from './DualListPick.vue';

export default {
  name: 'GroupForm',
  components: {
    JRPage,
    JRPageHeader,
    JRSection,
    JRField,
    JRButton,
    JRInput,
    DualListPick,
  },
  data() {
    return {
      loading: false,
      submitting: false,
      form: { name: '' },
      permissionLists: [[], []],
      allPermissions: [],
      fieldErrors: {},
      formBannerMessage: '',
    };
  },
  computed: {
    groupId() {
      return this.$route.params.id || null;
    },
    isReadOnly() {
      if (!this.groupId) return false;
      if (this.$route.query.mode === 'edit') return false;
      if (String(this.$route.name || '').endsWith('-edit')) return false;
      return true;
    },
    pageTitle() {
      if (!this.groupId) return 'New role';
      return this.isReadOnly ? 'View role' : 'Edit role';
    },
    pageDescription() {
      return 'Roles are Django groups. Assign the permissions this role should grant.';
    },
    attentionCount() {
      return Object.keys(this.fieldErrors).length;
    },
  },
  watch: {
    '$route.params.id': {
      immediate: true,
      handler() {
        this.bootstrap();
      },
    },
  },
  methods: {
    clearFieldError(field) {
      if (!this.fieldErrors[field]) return;
      const next = { ...this.fieldErrors };
      delete next[field];
      this.fieldErrors = next;
    },
    async bootstrap() {
      this.loading = true;
      this.fieldErrors = {};
      this.formBannerMessage = '';
      try {
        const { data: permissions } = await axios.get('/api/auth/admin/permissions/');
        this.allPermissions = Array.isArray(permissions) ? permissions : [];
        if (this.groupId) {
          const { data } = await axios.get(`/api/auth/admin/groups/${this.groupId}/`);
          this.form.name = data.name || '';
          const chosenIds = new Set((data.permissions || []).map(Number));
          const chosen = [];
          const available = [];
          for (const perm of this.allPermissions) {
            if (chosenIds.has(Number(perm.id))) chosen.push(perm);
            else available.push(perm);
          }
          this.permissionLists = [available, chosen];
        } else {
          this.form.name = '';
          this.permissionLists = [[...this.allPermissions], []];
        }
      } catch (err) {
        this.formBannerMessage =
          err?.response?.data?.detail || 'Could not load role data.';
        this.notifyToastError(this.formBannerMessage);
      } finally {
        this.loading = false;
      }
    },
    focusFirstError() {
      this.$nextTick(() => {
        const banner = this.$refs.formBanner;
        if (banner && typeof banner.focus === 'function') banner.focus();
        const fieldError = this.$el?.querySelector?.('.jr-field__error');
        if (!fieldError) return;
        const wrap = fieldError.closest('.jr-field');
        wrap?.scrollIntoView?.({ behavior: 'smooth', block: 'center' });
        const control = wrap?.querySelector(
          'input:not([type="hidden"]), textarea, select, [role="combobox"]',
        );
        if (control && typeof control.focus === 'function') control.focus();
      });
    },
    async handleSubmit() {
      if (this.isReadOnly || this.submitting) return;
      this.submitting = true;
      this.fieldErrors = {};
      this.formBannerMessage = '';

      const name = (this.form.name || '').trim();
      if (!name) {
        this.fieldErrors = { name: 'Name is required.' };
        this.formBannerMessage = '1 field needs attention';
        this.notifyToastError('Validation error.');
        this.focusFirstError();
        this.submitting = false;
        return;
      }

      const payload = {
        name,
        permissions: (this.permissionLists[1] || []).map((item) => item.id),
      };
      try {
        if (this.groupId) {
          await axios.patch(`/api/auth/admin/groups/${this.groupId}/`, payload);
          this.notifyToastSuccess('Role updated.');
        } else {
          const { data } = await axios.post('/api/auth/admin/groups/', payload);
          this.notifyToastSuccess('Role created.');
          this.$router.replace({
            name: 'user-permissions-group-edit',
            params: { id: data.id },
            query: { mode: 'edit' },
          });
          return;
        }
        this.$router.push({ name: 'user-permissions', query: { tab: 'groups' } });
      } catch (err) {
        const status = err?.response?.status;
        const data = err?.response?.data || {};
        this.fieldErrors = {};
        this.formBannerMessage = '';

        if (status === 403) {
          this.formBannerMessage =
            data.detail || 'You do not have permission to save this role.';
        } else if (status === 404) {
          this.formBannerMessage = 'This role no longer exists.';
        } else if (status >= 500) {
          this.formBannerMessage =
            'Could not save the role. Please try again.';
        } else if (!err?.response) {
          this.formBannerMessage =
            'Network error. Check your connection and try again.';
        } else {
          Object.entries(data).forEach(([key, value]) => {
            if (key === 'detail' || key === 'non_field_errors') {
              this.formBannerMessage = Array.isArray(value)
                ? value.join(' ')
                : String(value);
              return;
            }
            this.fieldErrors[key] = Array.isArray(value)
              ? value.join(' ')
              : String(value);
          });
        }

        if (!this.formBannerMessage && !Object.keys(this.fieldErrors).length) {
          this.formBannerMessage = 'Could not save the role.';
        } else if (
          !this.formBannerMessage &&
          Object.keys(this.fieldErrors).length
        ) {
          const n = Object.keys(this.fieldErrors).length;
          this.formBannerMessage = `${n} ${
            n === 1 ? 'field needs' : 'fields need'
          } attention`;
        }
        this.notifyToastError(this.formBannerMessage || 'Validation error.');
        this.focusFirstError();
      } finally {
        this.submitting = false;
      }
    },
    confirmRemove() {
      this.confirmDelete(
        'Delete this role?',
        'Users in this role will lose its permissions.',
        () => this.removeGroup(),
      );
    },
    async removeGroup() {
      try {
        await axios.delete(`/api/auth/admin/groups/${this.groupId}/`);
        this.notifyToastSuccess('Role deleted.');
        this.$router.push({ name: 'user-permissions', query: { tab: 'groups' } });
      } catch (err) {
        this.notifyToastError(
          err?.response?.data?.detail || 'Could not delete the role.',
        );
      }
    },
    goEdit() {
      this.$router.push({
        name: 'user-permissions-group-edit',
        params: { id: this.groupId },
        query: { mode: 'edit' },
      });
    },
    goBack() {
      this.$router.push({ name: 'user-permissions', query: { tab: 'groups' } });
    },
  },
};
</script>
