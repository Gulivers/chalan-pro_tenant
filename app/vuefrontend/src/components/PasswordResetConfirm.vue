<template>
  <div class="col-12 col-lg-4 mx-auto card my-5">
    <div class="card-title pt-3">
      <h2>Change your password</h2>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="confirmResetPassword">
        <label for="new-password" class="form-label text-start w-100 text-black">New password:</label>
        <input type="password" class="form-control" v-model="newPassword" required placeholder="secure password">
        <label for="confirm-password" class="form-label text-start w-100 text-black mt-3">Confirm new password:</label>
        <input type="password" class="form-control" v-model="confirmPassword" required placeholder="secure password">
        <div class="d-grid mt-3">
          <button class="btn btn-outline-primary btn-block my-3" type="submit">Change my password</button>
        </div>
      </form>
      <div class="alert alert-success" role="alert" v-if="message">
        {{ message }}
      </div>
      <div class="alert alert-danger" role="alert" v-if="error">
        {{ error }}
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
      newPassword: '',
      confirmPassword: '',
      message: '',
      error: ''
    };
  },
  methods: {
    async confirmResetPassword() {
      this.isLoading = true;
      this.error = '';
      this.message = '';
      const urlParams = new URLSearchParams(window.location.search);
      const uidb64 = urlParams.get('uid');
      const token = urlParams.get('token');

      if (this.newPassword !== this.confirmPassword) {
        this.error = 'Passwords do not match.';
        return;
      }

      try {
        const response = await axios.post(
            `/api/password-reset-confirm/${uidb64}/${token}/`,
            JSON.stringify({new_password: this.newPassword}),
            {
              headers: {
                'Content-Type': 'application/json',
              }
            });
        if (response && response.status == 200 && response.data) {
          this.message = 'Your password has been updated successfully.';
          setTimeout(()=>{
            this.$router.push('/login');
          }, 2000);
        } else {
          this.error = data.error || 'Failed to reset password.';
        }
        this.isLoading = false;
      } catch (err) {
        this.error = 'Error in request.'
        this.isLoading = false;
      }
    }
  }
};
</script>
  