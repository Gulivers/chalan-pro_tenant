<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow-sm border-0">
          <div class="card-body p-4 p-md-5 text-center">
            <h1 class="h4 fw-bold mb-3">Workspace deactivated</h1>
            <p class="text-muted mb-4">
              This JobRhythm workspace is no longer active. Contact your platform
              administrator or JobRhythm support if you need it restored.
            </p>
            <button type="button" class="btn btn-outline-secondary me-2" @click="logout">
              Sign out
            </button>
            <router-link class="btn btn-primary" to="/login">
              Back to sign in
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

async function logout() {
  try {
    await axios.post('/api/logout/')
  } catch {
    /* ignore */
  }
  localStorage.removeItem('authToken')
  localStorage.removeItem('userPermissions')
  router.push({ name: 'login' })
}
</script>
