<template>
  <div class="col-12 col-lg-4 mx-auto card my-5">
    <div class="card-title pt-3">
      <h2>Change your password</h2>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="confirmResetPassword">
        <div
          v-if="nonFieldErrors.length"
          class="alert alert-danger"
          role="alert">
          <ul class="mb-0 ps-3">
            <li v-for="(msg, i) in nonFieldErrors" :key="'nf-' + i">{{ msg }}</li>
          </ul>
        </div>

        <label for="new-password" class="form-label text-start w-100 text-black">
          New password
        </label>
        <input
          id="new-password"
          type="password"
          class="form-control"
          :class="{ 'is-invalid': errors.new_password.length }"
          v-model="newPassword"
          required
          autocomplete="new-password"
          placeholder="Enter a secure password"
          :disabled="isLoading" />
        <ul
          v-if="errors.new_password.length"
          class="small text-danger mb-0 mt-1 ps-3">
          <li v-for="(msg, i) in errors.new_password" :key="'np-' + i">{{ msg }}</li>
        </ul>

        <label
          for="confirm-password"
          class="form-label text-start w-100 text-black mt-3">
          Confirm new password
        </label>
        <input
          id="confirm-password"
          type="password"
          class="form-control"
          :class="{ 'is-invalid': errors.confirm_password.length }"
          v-model="confirmPassword"
          required
          autocomplete="new-password"
          placeholder="Re-enter your password"
          :disabled="isLoading" />
        <ul
          v-if="errors.confirm_password.length"
          class="small text-danger mb-0 mt-1 ps-3">
          <li v-for="(msg, i) in errors.confirm_password" :key="'cp-' + i">
            {{ msg }}
          </li>
        </ul>

        <div class="d-grid mt-3">
          <button
            class="btn btn-outline-primary btn-block my-3"
            type="submit"
            :disabled="isLoading || !uidb64 || !token">
            <span
              v-if="isLoading"
              class="spinner-border spinner-border-sm me-2"
              role="status"
              aria-hidden="true"></span>
            {{ isLoading ? "Updating..." : "Change my password" }}
          </button>
        </div>
      </form>
      <div class="alert alert-success" role="alert" v-if="message">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

function emptyFieldErrors() {
  return { new_password: [], confirm_password: [] };
}

export default {
  data() {
    return {
      isLoading: false,
      newPassword: "",
      confirmPassword: "",
      message: "",
      nonFieldErrors: [],
      errors: emptyFieldErrors(),
      uidb64: "",
      token: "",
    };
  },
  mounted() {
    const urlParams = new URLSearchParams(window.location.search);
    this.uidb64 = urlParams.get("uid") || "";
    this.token = urlParams.get("token") || "";
    if (!this.uidb64 || !this.token) {
      this.nonFieldErrors = [
        "Invalid or expired reset link. Please request a new one from the login page.",
      ];
    }
  },
  methods: {
    clearErrors() {
      this.errors = emptyFieldErrors();
      this.nonFieldErrors = [];
      this.message = "";
    },

    applyApiErrors(data) {
      this.clearErrors();
      if (!data || typeof data !== "object" || Array.isArray(data)) {
        this.nonFieldErrors = [
          "Could not update your password. Please try again.",
        ];
        return;
      }

      for (const key of ["new_password", "confirm_password"]) {
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
          "Could not update your password. Please review the form and try again.",
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
        this.errors.confirm_password = ["Password confirmation does not match."];
        this.isLoading = false;
        return;
      }

      try {
        const response = await axios.post(
          `/api/password-reset-confirm/${this.uidb64}/${this.token}/`,
          {
            new_password: this.newPassword,
            confirm_password: this.confirmPassword,
          },
          { headers: { "Content-Type": "application/json" } }
        );

        if (response?.status === 200) {
          this.message = "Your password has been updated successfully.";
          setTimeout(() => {
            this.$router.push("/login");
          }, 2000);
        }
      } catch (err) {
        const status = err?.response?.status;
        const data = err?.response?.data;

        if (status === 400 && data && typeof data === "object") {
          this.applyApiErrors(data);
        } else {
          this.nonFieldErrors = [
            "Could not update your password. Please try again.",
          ];
        }
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>
