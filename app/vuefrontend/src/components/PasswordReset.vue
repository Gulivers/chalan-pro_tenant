<template>
  <div class="col-12 col-lg-4 mx-auto card my-5">
    <div class="card-title pt-3">
      <h2>Forgot Your Password?</h2>
    </div>
    <div class="card-body p-4">
      <form @submit.prevent="resetPassword">
        <label for="email" class="form-label text-start w-100 text-black" >Email:</label>
        <input type="email" class="form-control" v-model="email" required placeholder="email@example.com">

        <div class="d-grid mt-3">
          <button type="submit" class="btn btn-outline-primary btn-block my-3" :disabled="isLoading">
                      <span v-if="isLoading" class="spinner-grow spinner-grow-sm" aria-hidden="true"></span>
                      <span v-if="isLoading">Please wait ...</span>
                      <span v-else>Send instructions</span>
                    </button>
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
      email: '',
      message: '',
      error: ''
    };
  },
  methods: {
    async resetPassword() {
      this.isLoading = true;
      this.error = '';
      this.message = '';
      try {
        const response = await axios.post('/api/request-password-reset/', JSON.stringify({email: this.email}), {
          headers: {
            'Content-Type': 'application/json',
          }
        });
        if (response && response.status == 200 && response.data) {
          this.message = 'An email has been sent with instructions on how to recover your password.'
          this.email = ''

        } else {
          this.error = data.error || 'Failed to send instructions email.';
        }
        this.isLoading = false;
      } catch (err) {
        this.error = 'Error in request.';
        this.isLoading = false;
      }
    }
  }
};
</script>
  