<template>
  <AuthShell
    title="Workspace deactivated"
    lead="This JobRhythm workspace is no longer active. Contact your platform administrator or JobRhythm support if you need it restored.">
    <div class="jr-auth-suspended">
      <JRButton type="button" variant="secondary" fluid @click="logout">
        Sign out
      </JRButton>
      <JRButton type="button" fluid @click="goLogin">
        Back to sign in
      </JRButton>
    </div>
  </AuthShell>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { JRButton } from '@/ui';
import AuthShell from './AuthShell.vue';
import authService from '@/auth/authService';

const router = useRouter();

async function logout() {
  await authService.handleLogout();
}

function goLogin() {
  router.push('/login');
}
</script>

<style scoped>
.jr-auth-suspended {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
</style>
