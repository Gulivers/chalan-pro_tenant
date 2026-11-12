<template>
  <JRPage class="jr-user-admin">
    <JRPageHeader :title="pageTitle" :description="pageDescription">
      <template #actions>
        <JRButton
          v-if="isReadOnly && userId && canEditTarget"
          type="button"
          variant="primary"
          size="sm"
          @click="goEdit">
          Edit user
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
        {{ $t('permissions.loadingUser') }}
      </p>

      <template v-else>
        <JRSection :title="$t('permissions.sectionAccount')">
          <div class="jr-form-grid jr-form-grid--identity">
            <JRField
              v-slot="{ describedby, invalid }"
              class="jr-user-admin-form__identity-field"
              :label="$t('permissions.username')"
              required
              inputId="user-username"
              :hint="$t('permissions.usernameHint')"
              :error="fieldErrors.username">
              <JRInput
                inputId="user-username"
                v-model="form.username"
                maxlength="150"
                autocomplete="username"
                :disabled="isReadOnly"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('username')" />
            </JRField>
          </div>

          <div
            v-if="!isReadOnly"
            class="jr-form-stack jr-form-stack--credentials">
            <JRField
              v-slot="{ describedby, invalid }"
              class="jr-user-admin-form__password-field"
              :label="userId ? $t('permissions.newPassword') : $t('permissions.password')"
              :required="!userId"
              inputId="user-password"
              :hint="passwordHint"
              :error="fieldErrors.password">
              <JRInput
                inputId="user-password"
                v-model="form.password"
                type="password"
                autocomplete="new-password"
                :invalid="invalid"
                :required="!userId"
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('password')" />
            </JRField>

            <JRField
              v-slot="{ describedby, invalid }"
              class="jr-user-admin-form__password-confirm"
              :label="$t('permissions.passwordConfirmation')"
              :required="!userId || !!form.password"
              inputId="user-password-confirm"
              :hint="
                userId
                  ? $t('permissions.passwordConfirmHintExisting')
                  : $t('permissions.passwordConfirmHintNew')
              "
              :error="fieldErrors.password_confirm">
              <JRInput
                inputId="user-password-confirm"
                v-model="form.password_confirm"
                type="password"
                autocomplete="new-password"
                :invalid="invalid"
                :required="!userId || !!form.password"
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('password_confirm')" />
            </JRField>
          </div>
        </JRSection>

        <JRSection :title="$t('permissions.sectionPersonal')">
          <div class="jr-form-grid jr-form-grid--personal">
            <JRField
              v-slot="{ describedby, invalid }"
              :label="$t('permissions.firstName')"
              required
              inputId="user-first-name"
              :error="fieldErrors.first_name">
              <JRInput
                inputId="user-first-name"
                v-model="form.first_name"
                maxlength="150"
                autocomplete="given-name"
                :disabled="isReadOnly"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('first_name')" />
            </JRField>
            <JRField
              v-slot="{ describedby, invalid }"
              :label="$t('permissions.lastName')"
              required
              inputId="user-last-name"
              :error="fieldErrors.last_name">
              <JRInput
                inputId="user-last-name"
                v-model="form.last_name"
                maxlength="150"
                autocomplete="family-name"
                :disabled="isReadOnly"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('last_name')" />
            </JRField>
            <JRField
              v-slot="{ describedby, invalid }"
              class="jr-user-admin-form__email-field"
              :label="$t('permissions.emailAddress')"
              required
              inputId="user-email"
              :hint="$t('permissions.emailAddressHint')"
              :error="fieldErrors.email">
              <JRInput
                inputId="user-email"
                v-model="form.email"
                type="email"
                maxlength="254"
                autocomplete="email"
                :disabled="isReadOnly"
                :invalid="invalid"
                required
                :ariaDescribedby="describedby"
                @update:modelValue="clearFieldError('email')" />
            </JRField>
          </div>
        </JRSection>

        <JRSection :title="$t('permissions.sectionPermissions')">
          <div class="jr-user-admin-form__access">
            <div class="jr-form-checks">
              <JRField
                :label="$t('permissions.active')"
                inputId="user-is-active"
                :hint="$t('permissions.activeHint')">
                <JRCheckbox
                  inputId="user-is-active"
                  v-model="form.is_active"
                  :ariaLabel="$t('permissions.active')"
                  :disabled="isReadOnly" />
              </JRField>
              <JRField
                :label="$t('permissions.staffStatus')"
                inputId="user-is-staff"
                :hint="$t('permissions.staffStatusHint')">
                <JRCheckbox
                  inputId="user-is-staff"
                  v-model="form.is_staff"
                  :ariaLabel="$t('permissions.staffStatus')"
                  :disabled="isReadOnly" />
              </JRField>
            </div>
            <p v-if="form.is_superuser" class="jr-user-admin-form__note">
              This account is a superuser. Superuser status can only be managed in Django Admin.
            </p>
          </div>

          <div class="jr-user-admin-form__assignments">
            <div class="jr-user-admin-form__pick">
              <h3 class="jr-user-admin-form__pick-title">{{ $t('permissions.groups') }}</h3>
              <DualListPick
                v-model="groupLists"
                label-key="name"
                filter-by="name"
                :source-header="$t('permissions.availableGroups')"
                :target-header="$t('permissions.chosenGroups')"
                :disabled="isReadOnly"
                :hint="$t('permissions.groupsHint')" />
            </div>

            <div class="jr-user-admin-form__pick">
              <h3 class="jr-user-admin-form__pick-title">{{ $t('permissions.userPermissions') }}</h3>
              <DualListPick
                v-model="permissionLists"
                :source-header="$t('permissions.availablePermissions')"
                :target-header="$t('permissions.chosenPermissions')"
                :disabled="isReadOnly"
                :hint="$t('permissions.userPermissionsHint')" />
            </div>
          </div>
        </JRSection>

        <JRSection v-if="userId" :title="$t('permissions.sectionDates')">
          <div class="jr-form-grid jr-form-grid--dates">
            <JRField :label="$t('permissions.lastLogin')" inputId="user-last-login">
              <JRInput
                inputId="user-last-login"
                :modelValue="formatWhen(form.last_login)"
                disabled />
            </JRField>
            <JRField :label="$t('permissions.dateJoined')" inputId="user-date-joined">
              <JRInput
                inputId="user-date-joined"
                :modelValue="formatWhen(form.date_joined)"
                disabled />
            </JRField>
          </div>
        </JRSection>

        <div class="jr-user-admin-form__actions">
          <JRButton
            type="submit"
            variant="primary"
            :disabled="isReadOnly || submitting || !canEditTarget">
            {{ submitting ? $t('common.saving') : userId ? $t('common.update') : $t('common.save') }}
          </JRButton>
          <JRButton type="button" variant="secondary" @click="goBack">
            {{ isReadOnly ? $t('common.backToList') : $t('common.cancel') }}
          </JRButton>
          <JRButton
            v-if="userId && !isReadOnly && canEditTarget && !isSelf"
            type="button"
            variant="danger"
            :disabled="submitting"
            @click="confirmRemove">
            {{ $t('common.delete') }}
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
  JRCheckbox,
} from '@/ui';
import DualListPick from './DualListPick.vue';

export default {
  name: 'UserForm',
  components: {
    JRPage,
    JRPageHeader,
    JRSection,
    JRField,
    JRButton,
    JRInput,
    JRCheckbox,
    DualListPick,
  },
  data() {
    return {
      loading: false,
      submitting: false,
      form: {
        username: '',
        password: '',
        password_confirm: '',
        first_name: '',
        last_name: '',
        email: '',
        is_active: true,
        is_staff: false,
        is_superuser: false,
        last_login: null,
        date_joined: null,
      },
      passwordRulesHint: [
        'Your password can’t be too similar to your other personal information.',
        'Your password must contain at least 8 characters.',
        'Your password can’t be a commonly used password.',
        'Your password can’t be entirely numeric.',
      ].join('\n'),
      groupLists: [[], []],
      permissionLists: [[], []],
      allGroups: [],
      allPermissions: [],
      fieldErrors: {},
      formBannerMessage: '',
      currentUserId: null,
      currentUserIsSuperuser: false,
    };
  },
  computed: {
    userId() {
      return this.$route.params.id || null;
    },
    isReadOnly() {
      if (!this.userId) return false;
      if (this.$route.query.mode === 'edit') return false;
      if (String(this.$route.name || '').endsWith('-edit')) return false;
      return true;
    },
    isSelf() {
      return (
        this.userId &&
        this.currentUserId &&
        Number(this.userId) === Number(this.currentUserId)
      );
    },
    canEditTarget() {
      if (!this.form.is_superuser) return true;
      return !!this.currentUserIsSuperuser;
    },
    pageTitle() {
      if (!this.userId) return 'New user';
      const name = this.form.username || 'user';
      return this.isReadOnly ? `View user · ${name}` : `Edit user · ${name}`;
    },
    pageDescription() {
      return 'Manage account access, roles (groups), and individual permissions. Superuser status is not editable here.';
    },
    attentionCount() {
      return Object.keys(this.fieldErrors).length;
    },
    passwordHint() {
      if (this.userId) {
        return `Leave blank to keep the current password.\n${this.passwordRulesHint}`;
      }
      return this.passwordRulesHint;
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
    formatWhen(value) {
      if (!value) return '—';
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return String(value);
      return date.toLocaleString();
    },
    splitLists(allItems, chosenIds) {
      const chosenSet = new Set((chosenIds || []).map(Number));
      const chosen = [];
      const available = [];
      for (const item of allItems) {
        if (chosenSet.has(Number(item.id))) chosen.push(item);
        else available.push(item);
      }
      return [available, chosen];
    },
    async bootstrap() {
      this.loading = true;
      this.fieldErrors = {};
      this.formBannerMessage = '';
      this.form.password = '';
      this.form.password_confirm = '';
      try {
        const me = await this.getAuthenticatedUser();
        this.currentUserId = me?.id ?? null;
        this.currentUserIsSuperuser = !!me?.is_superuser;

        const [groupsRes, permsRes] = await Promise.all([
          axios.get('/api/auth/admin/groups/'),
          axios.get('/api/auth/admin/permissions/'),
        ]);
        this.allGroups = Array.isArray(groupsRes.data) ? groupsRes.data : [];
        this.allPermissions = Array.isArray(permsRes.data) ? permsRes.data : [];

        if (this.userId) {
          const { data } = await axios.get(`/api/auth/admin/users/${this.userId}/`);
          this.form = {
            username: data.username || '',
            password: '',
            password_confirm: '',
            first_name: data.first_name || '',
            last_name: data.last_name || '',
            email: data.email || '',
            is_active: !!data.is_active,
            is_staff: !!data.is_staff,
            is_superuser: !!data.is_superuser,
            last_login: data.last_login,
            date_joined: data.date_joined,
          };
          this.groupLists = this.splitLists(this.allGroups, data.groups);
          this.permissionLists = this.splitLists(
            this.allPermissions,
            data.user_permissions,
          );
          if (!this.canEditTarget && this.$route.query.mode === 'edit') {
            this.formBannerMessage =
              'Only a superuser can edit another superuser account.';
          }
        } else {
          this.form = {
            username: '',
            password: '',
            password_confirm: '',
            first_name: '',
            last_name: '',
            email: '',
            is_active: true,
            is_staff: false,
            is_superuser: false,
            last_login: null,
            date_joined: null,
          };
          this.groupLists = [[...this.allGroups], []];
          this.permissionLists = [[...this.allPermissions], []];
        }
      } catch (err) {
        this.formBannerMessage =
          err?.response?.data?.detail || 'Could not load user data.';
        this.notifyToastError(this.formBannerMessage);
      } finally {
        this.loading = false;
      }
    },
    isValidEmailFormat(email) {
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    },
    validateLocalFields() {
      const errors = {};
      const username = (this.form.username || '').trim();
      const firstName = (this.form.first_name || '').trim();
      const lastName = (this.form.last_name || '').trim();
      const email = (this.form.email || '').trim();

      if (!username) {
        errors.username = 'Username is required.';
      }
      if (!firstName) {
        errors.first_name = 'First name is required.';
      }
      if (!lastName) {
        errors.last_name = 'Last name is required.';
      }
      if (!email) {
        errors.email = 'Email address is required.';
      } else if (!this.isValidEmailFormat(email)) {
        errors.email = 'Enter a valid email address.';
      }

      const password = this.form.password || '';
      const confirm = this.form.password_confirm || '';
      const changingPassword = !!password || !!confirm;

      if (!this.userId && !password) {
        errors.password = 'Password is required for new users.';
      }
      if (!this.userId && !confirm) {
        errors.password_confirm = 'This field is required.';
      }
      if (this.userId && changingPassword) {
        if (!password) {
          errors.password =
            'Enter a new password, or leave both password fields blank.';
        }
        if (!confirm) {
          errors.password_confirm = 'This field is required.';
        }
      }
      if (password && confirm && password !== confirm) {
        errors.password_confirm = 'The two password fields didn’t match.';
      }
      if (password) {
        if (password.length < 8) {
          errors.password =
            errors.password ||
            'Your password must contain at least 8 characters.';
        } else if (/^\d+$/.test(password)) {
          errors.password =
            errors.password ||
            'Your password can’t be entirely numeric.';
        }
      }
      return errors;
    },
    setAttentionBanner(errorCount) {
      if (!errorCount) {
        this.formBannerMessage = '';
        return;
      }
      this.formBannerMessage = `${errorCount} ${
        errorCount === 1 ? 'field needs' : 'fields need'
      } attention`;
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
      if (this.isReadOnly || this.submitting || !this.canEditTarget) return;
      this.submitting = true;
      this.fieldErrors = {};
      this.formBannerMessage = '';

      const localErrors = this.validateLocalFields();
      if (Object.keys(localErrors).length) {
        this.fieldErrors = localErrors;
        this.setAttentionBanner(Object.keys(localErrors).length);
        this.notifyToastError('Validation error.');
        this.focusFirstError();
        this.submitting = false;
        return;
      }

      const payload = {
        username: (this.form.username || '').trim(),
        first_name: (this.form.first_name || '').trim(),
        last_name: (this.form.last_name || '').trim(),
        email: (this.form.email || '').trim().toLowerCase(),
        is_active: !!this.form.is_active,
        is_staff: !!this.form.is_staff,
        groups: (this.groupLists[1] || []).map((item) => item.id),
        user_permissions: (this.permissionLists[1] || []).map((item) => item.id),
      };
      if (this.form.password) {
        payload.password = this.form.password;
        payload.password_confirm = this.form.password_confirm || '';
      }
      try {
        if (this.userId) {
          await axios.patch(`/api/auth/admin/users/${this.userId}/`, payload);
          this.notifyToastSuccess('User updated.');
        } else {
          const { data } = await axios.post('/api/auth/admin/users/', payload);
          this.notifyToastSuccess('User created.');
          this.$router.replace({
            name: 'user-permissions-user-edit',
            params: { id: data.id },
            query: { mode: 'edit' },
          });
          return;
        }
        this.$router.push({ name: 'user-permissions', query: { tab: 'users' } });
      } catch (err) {
        const status = err?.response?.status;
        const data = err?.response?.data || {};
        this.fieldErrors = {};
        this.formBannerMessage = '';

        if (status === 403) {
          this.formBannerMessage =
            data.detail ||
            'You do not have permission to save this user.';
        } else if (status === 404) {
          this.formBannerMessage = 'This user no longer exists.';
        } else if (status >= 500) {
          this.formBannerMessage =
            'Could not save the user. Please try again.';
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
          this.formBannerMessage = 'Could not save the user.';
        } else if (!this.formBannerMessage && Object.keys(this.fieldErrors).length) {
          this.setAttentionBanner(Object.keys(this.fieldErrors).length);
        }
        this.notifyToastError(this.formBannerMessage || 'Validation error.');
        this.focusFirstError();
      } finally {
        this.submitting = false;
      }
    },
    confirmRemove() {
      this.confirmDelete(
        'Delete this user?',
        `${this.form.username} will be permanently removed.`,
        () => this.removeUser(),
      );
    },
    async removeUser() {
      try {
        await axios.delete(`/api/auth/admin/users/${this.userId}/`);
        this.notifyToastSuccess('User deleted.');
        this.$router.push({ name: 'user-permissions', query: { tab: 'users' } });
      } catch (err) {
        this.notifyToastError(
          err?.response?.data?.detail || 'Could not delete the user.',
        );
      }
    },
    goEdit() {
      this.$router.push({
        name: 'user-permissions-user-edit',
        params: { id: this.userId },
        query: { mode: 'edit' },
      });
    },
    goBack() {
      this.$router.push({ name: 'user-permissions', query: { tab: 'users' } });
    },
  },
};
</script>

<style scoped>
/* Layout/type for this form lives under .jr-user-admin in jr-design-system.css */
.jr-user-admin-form__password-field :deep(.jr-field__hint) {
  white-space: pre-line;
  line-height: 1.55;
}
</style>
