<template>
  <AuthShell
    title="Sign in"
    lead="Enter your username and password for this JobRhythm workspace.">
    <form class="jr-auth-form" @submit.prevent="login">
      <Message
        v-if="error"
        severity="error"
        :closable="false"
        role="alert">
        {{ error }}
      </Message>

      <JRField
        label="Username"
        required
        inputId="login-username">
        <template #default="{ describedby }">
          <JRInput
            inputId="login-username"
            v-model="username"
            autocomplete="username"
            :disabled="isLoading"
            :ariaDescribedby="describedby"
            required />
        </template>
      </JRField>

      <JRField
        label="Password"
        required
        inputId="login-password">
        <template #default="{ describedby }">
          <div class="jr-auth-pw">
            <JRInput
              inputId="login-password"
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              autocomplete="current-password"
              :disabled="isLoading"
              :ariaDescribedby="describedby"
              required />
            <button
              type="button"
              class="jr-auth-pw__toggle"
              :aria-label="showPassword ? 'Hide password' : 'Show password'"
              :disabled="isLoading"
              @click="showPassword = !showPassword">
              <EyeSlash v-if="showPassword" class="jr-auth-pw__icon" />
              <Eye v-else class="jr-auth-pw__icon" />
            </button>
          </div>
        </template>
      </JRField>

      <JRButton
        type="submit"
        fluid
        :disabled="isLoading"
        :loading="isLoading">
        {{ isLoading ? 'Signing in…' : 'Sign in' }}
      </JRButton>

      <p class="jr-auth-form__footer">
        <router-link to="/reset_password" class="jr-auth-form__link">
          Forgot password?
        </router-link>
      </p>
    </form>
  </AuthShell>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import Message from 'primevue/message';
import Eye from '@primeicons/vue/eye';
import EyeSlash from '@primeicons/vue/eye-slash';
import { JRField, JRInput, JRButton } from '@/ui';
import AuthShell from './AuthShell.vue';
import authService from '@/auth/authService';

const username = ref('');
const password = ref('');
const error = ref('');
const isLoading = ref(false);
const showPassword = ref(false);
const router = useRouter();
const route = useRoute();

onMounted(() => {
  document.getElementById('login-username')?.focus();
});

function safeRedirectTarget() {
  const raw = route.query.redirect;
  if (typeof raw !== 'string' || !raw.startsWith('/') || raw.startsWith('//')) {
    return '/';
  }
  return raw;
}

async function login() {
  isLoading.value = true;
  error.value = '';
  try {
    const data = await authService.login(username.value, password.value);
    if (!data?.access) {
      throw new Error('Access token not received in the response');
    }
    router.push(safeRedirectTarget());
  } catch (err) {
    console.error('Login error:', err);
    if (err.response) {
      const data = err.response.data || {};
      const code = data.code;
      switch (err.response.status) {
        case 401:
          error.value =
            data.detail || 'Incorrect credentials. Please try again.';
          break;
        case 403:
          if (code === 'tenant_inactive') {
            error.value =
              data.detail ||
              'This workspace has been deactivated. Contact support.';
          } else {
            error.value = data.detail || 'Access denied.';
          }
          break;
        case 429:
          error.value =
            (typeof data.detail === 'string'
              ? data.detail
              : data.detail?.detail) ||
            'Too many login attempts. Please try again later.';
          break;
        case 500:
          error.value = 'Internal server error. Please try again later.';
          break;
        default:
          error.value = `Unknown error: ${err.response.status}. Please try again later.`;
      }
    } else if (err.request) {
      error.value =
        'Could not connect to the server. Please check your internet connection.';
    } else {
      error.value = `An unexpected error occurred: ${err.message}. Please try again later.`;
    }
  } finally {
    isLoading.value = false;
  }
}
</script>
