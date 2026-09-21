<template>
  <AuthShell
    title="Forgot password?"
    lead="Enter the email on your account. If it matches a user in this workspace, we will send reset instructions.">
    <form class="jr-auth-form" @submit.prevent="resetPassword">
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
        label="Email"
        required
        inputId="reset-email"
        :error="errors.email[0] || ''">
        <template #default="{ invalid, describedby }">
          <JRInput
            inputId="reset-email"
            type="email"
            v-model="email"
            autocomplete="email"
            placeholder="email@example.com"
            :invalid="invalid"
            :disabled="isLoading"
            :ariaDescribedby="describedby"
            required />
        </template>
      </JRField>

      <JRButton type="submit" fluid :disabled="isLoading" :loading="isLoading">
        {{ isLoading ? 'Sending…' : 'Send instructions' }}
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
import { JRField, JRInput, JRButton } from '@/ui';
import AuthShell from './AuthShell.vue';

export default {
  components: { AuthShell, JRField, JRInput, JRButton, Message },
  data() {
    return {
      isLoading: false,
      email: '',
      message: '',
      nonFieldErrors: [],
      errors: { email: [] },
    };
  },
  mounted() {
    this.$nextTick(() => {
      document.getElementById('reset-email')?.focus();
    });
  },
  methods: {
    clearErrors() {
      this.errors = { email: [] };
      this.nonFieldErrors = [];
      this.message = '';
    },

    applyApiErrors(data) {
      this.clearErrors();
      if (!data || typeof data !== 'object' || Array.isArray(data)) {
        this.nonFieldErrors = [
          'Could not send reset instructions. Please try again.',
        ];
        return;
      }

      if (data.email != null) {
        const raw = data.email;
        this.errors.email = Array.isArray(raw) ? raw.map(String) : [String(raw)];
      }

      const nf = data.non_field_errors ?? data.detail ?? data.error;
      if (nf != null) {
        const list = Array.isArray(nf) ? nf : [nf];
        this.nonFieldErrors.push(...list.map(String));
      }

      if (!this.nonFieldErrors.length && !this.errors.email.length) {
        this.nonFieldErrors = [
          'Could not send reset instructions. Please try again.',
        ];
      }
    },

    async resetPassword() {
      this.isLoading = true;
      this.clearErrors();
      try {
        const response = await axios.post(
          '/api/auth/password/forgot/',
          { email: this.email.trim() },
          { headers: { 'Content-Type': 'application/json' } }
        );
        if (response?.status === 200) {
          this.message =
            response.data?.detail ||
            'If an account exists for this email, you will receive password reset instructions shortly.';
          this.email = '';
        }
      } catch (err) {
        const status = err?.response?.status;
        const data = err?.response?.data;
        if (status === 400 && data && typeof data === 'object') {
          this.applyApiErrors(data);
        } else if (status === 429) {
          const detail =
            (data && data.detail && data.detail.detail) ||
            data?.detail ||
            'Too many requests. Please try again later.';
          this.nonFieldErrors = [String(detail)];
        } else {
          this.nonFieldErrors = [
            'Could not send reset instructions. Please try again.',
          ];
        }
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>
