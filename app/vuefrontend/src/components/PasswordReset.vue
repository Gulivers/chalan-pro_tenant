<template>
  <div class="col-12 col-lg-4 mx-auto card my-5">
    <div class="card-title pt-3">
      <h2>Forgot Your Password?</h2>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="resetPassword">
        <label for="email" class="form-label text-start w-100 text-black">Email</label>
        <input
          id="email"
          type="email"
          class="form-control"
          :class="{ 'is-invalid': errors.email.length }"
          v-model="email"
          required
          autocomplete="email"
          placeholder="email@example.com"
          :disabled="isLoading" />
        <ul
          v-if="errors.email.length"
          class="small text-danger mb-0 mt-1 ps-3">
          <li v-for="(msg, i) in errors.email" :key="'em-' + i">{{ msg }}</li>
        </ul>

        <div
          v-if="nonFieldErrors.length"
          class="alert alert-danger mt-3 mb-0"
          role="alert">
          <ul class="mb-0 ps-3">
            <li v-for="(msg, i) in nonFieldErrors" :key="'nf-' + i">{{ msg }}</li>
          </ul>
        </div>

        <div class="d-grid mt-3">
          <button
            type="submit"
            class="btn btn-outline-primary btn-block my-3"
            :disabled="isLoading">
            <span
              v-if="isLoading"
              class="spinner-grow spinner-grow-sm"
              aria-hidden="true"></span>
            <span v-if="isLoading">Please wait...</span>
            <span v-else>Send instructions</span>
          </button>
        </div>
      </form>
      <div class="alert alert-success mt-3" role="alert" v-if="message">
        {{ message }}
      </div>
    </div>

  </div>
</template>

<script>
import axios from "axios";
export default {
  data() {
    return {
      isLoading: false,
      email: "",
      message: "",
      nonFieldErrors: [],
      errors: { email: [] },
    };
  },
  methods: {
    clearErrors() {
      this.errors = { email: [] };
      this.nonFieldErrors = [];
      this.message = "";
    },

    applyApiErrors(data) {
      this.clearErrors();
      if (!data || typeof data !== "object" || Array.isArray(data)) {
        this.nonFieldErrors = ["Could not send reset instructions. Please try again."];
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
        this.nonFieldErrors = ["Could not send reset instructions. Please try again."];
      }
    },

    async resetPassword() {
      this.isLoading = true;
      this.clearErrors();
      try {
        const response = await axios.post(
          "/api/request-password-reset/",
          { email: this.email.trim() },
          { headers: { "Content-Type": "application/json" } }
        );
        if (response?.status === 200) {
          this.message =
            "If an account exists for this email, you will receive password reset instructions shortly.";
          this.email = "";
        }
      } catch (err) {
        const status = err?.response?.status;
        const data = err?.response?.data;
        if (status === 400 && data && typeof data === "object") {
          this.applyApiErrors(data);
        } else if (status === 404 && data && typeof data === "object") {
          this.applyApiErrors(data);
        } else {
          this.nonFieldErrors = ["Could not send reset instructions. Please try again."];
        }
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>
  