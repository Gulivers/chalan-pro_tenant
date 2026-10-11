<template>
  <AuthShell
    title="Choose a new password"
    lead="Enter and confirm a new password for your JobRhythm account.">
    <form class="jr-auth-form" @submit.prevent="confirmResetPassword">
      <Message
        v-if="nonFieldErrors.length"
        severity="error"
        :closable="false"
        role="alert">
        <ul class="jr-auth-form__list">
          <li v-for="(msg, i) in nonFieldErrors" :key="'nf-' + i">{{ msg }}</li>
        </ul>
      </Message>

      <Message
        v-if="message"
        severity="success"
        :closable="false"
        role="status">
        {{ message }}
      </Message>

      <JRField
        label="New password"
        required
        inputId="new-password"
        :error="errors.new_password[0] || ''">
        <template #default="{ invalid, describedby }">
          <div class="jr-auth-pw">
            <JRInput
              inputId="new-password"
              :type="showPassword ? 'text' : 'password'"
              v-model="newPassword"
              autocomplete="new-password"
              placeholder="Enter a secure password"
              :invalid="invalid"
              :disabled="isLoading || !canSubmit"
              :ariaDescribedby="describedby"
              required />
            <button
              type="button"
              class="jr-auth-pw__toggle"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
              :disabled="isLoading || !canSubmit"
              @click="showPassword = !showPassword">
              <EyeSlash v-if="showPassword" class="jr-auth-pw__icon" />
              <Eye v-else class="jr-auth-pw__icon" />
            </button>
          </div>
        </template>
      </JRField>

      <JRField
        label="Confirm new password"
        required
        inputId="confirm-password"
        :error="errors.confirm_password[0] || ''">
        <template #default="{ invalid, describedby }">
          <div class="jr-auth-pw">
            <JRInput
              inputId="confirm-password"
              :type="showConfirm ? 'text' : 'password'"
              v-model="confirmPassword"
              autocomplete="new-password"
              placeholder="Re-enter your password"
              :invalid="invalid"
              :disabled="isLoading || !canSubmit"
              :ariaDescribedby="describedby"
              required />
            <button
              type="button"
              class="jr-auth-pw__toggle"
              :aria-label="
                showConfirm ? 'Hide confirmation' : 'Show confirmation'
              "
              :disabled="isLoading || !canSubmit"
              @click="showConfirm = !showConfirm">
              <EyeSlash v-if="showConfirm" class="jr-auth-pw__icon" />
              <Eye v-else class="jr-auth-pw__icon" />
            </button>
          </div>
        </template>
      </JRField>

      <JRButton
        type="submit"
        fluid
        :disabled="isLoading || !canSubmit"
        :loading="isLoading">
        {{ isLoading ? 'Updating…' : 'Change my password' }}
      </JRButton>

      <p class="jr-auth-form__footer">
        <router-link to="/login" class="jr-auth-form__link">
          Back to sign in
        </router-link>
      </p>
    </form>
  </AuthShell>
</template>

<script>
import axios from 'axios';
import Message from 'primevue/message';
import Eye from '@primeicons/vue/eye';
import EyeSlash from '@primeicons/vue/eye-slash';
import { JRField, JRInput, JRButton } from '@/ui';
import AuthShell from './AuthShell.vue';

function emptyFieldErrors() {
  return { new_password: [], confirm_password: [] };
}

export default {
  components: {
    AuthShell,
    JRField,
    JRInput,
    JRButton,
    Message,
    Eye,
    EyeSlash,
  },
  data() {
    return {
      isLoading: false,
      newPassword: '',
      confirmPassword: '',
      message: '',
      nonFieldErrors: [],
      errors: emptyFieldErrors(),
      uidb64: '',
      token: '',
      showPassword: false,
      showConfirm: false,
    };
  },
  computed: {
    canSubmit() {
      return Boolean(this.uidb64 && this.token);
    },
  },
  mounted() {
    const urlParams = new URLSearchParams(window.location.search);
    this.uidb64 = urlParams.get('uid') || '';
    this.token = urlParams.get('token') || '';
    if (!this.uidb64 || !this.token) {
      this.nonFieldErrors = [
        'Invalid or expired reset link. Please request a new one from the login page.',
      ];
    } else {
      this.$nextTick(() => {
        document.getElementById('new-password')?.focus();
      });
    }
  },
  methods: {
    clearErrors() {
      this.errors = emptyFieldErrors();
      this.nonFieldErrors = [];
      this.message = '';
    },

    applyApiErrors(data) {
      this.clearErrors();
      if (!data || typeof data !== 'object' || Array.isArray(data)) {
        this.nonFieldErrors = [
          'Could not update your password. Please try again.',
        ];
        return;
      }

      for (const key of ['new_password', 'confirm_password']) {
        const raw = data[key];
        if (raw == null) continue;
        this.errors[key] = Array.isArray(raw) ? raw.map(String) : [String(raw)];
      }

      const nf = data.non_field_errors ?? data.detail ?? data.error;
      if (nf != null) {
        const list = Array.isArray(nf) ? nf : [nf];
        this.nonFieldErrors.push(...list.map(String));
      }

      if (
        !this.nonFieldErrors.length &&
        !this.errors.new_password.length &&
        !this.errors.confirm_password.length
      ) {
        this.nonFieldErrors = [
          'Could not update your password. Please review the form and try again.',
        ];
      }
    },

    async confirmResetPassword() {
      if (!this.uidb64 || !this.token) {
        return;
      }

      this.isLoading = true;
      this.clearErrors();

      if (this.newPassword !== this.confirmPassword) {
        this.errors.confirm_password = [
          'Password confirmation does not match.',
        ];
        this.isLoading = false;
        return;
      }

      try {
        const response = await axios.post(
          `/api/auth/password/reset/`,
          {
            uid: this.uidb64,
            token: this.token,
            new_password: this.newPassword,
            confirm_password: this.confirmPassword,
          },
          { headers: { 'Content-Type': 'application/json' } }
        );

        if (response?.status === 200) {
          this.message =
            response.data?.detail ||
            'Your password has been updated successfully.';
          setTimeout(() => {
            this.$router.push('/login');
          }, 2000);
        }
      } catch (err) {
        const status = err?.response?.status;
        const data = err?.response?.data;

        if (status === 400 && data && typeof data === 'object') {
          this.applyApiErrors(data);
        } else {
          this.nonFieldErrors = [
            'Could not update your password. Please try again.',
          ];
        }
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>
