<template>
  <footer class="text-bg-light py-3">
    <div class="container text-center">
      <div class="row">
        <!-- Left: Company Info -->
        <div class="col-md-4 mb-2">
          <p>© {{ currentYear }} Chalan-Pro. All rights reserved.</p>
          <p>Version: {{ appVersion }}</p>
        </div>

        <!-- Center: Quick Navigation -->
        <div class="col-md-4 mb-2" v-if="!$route.meta.hideNavbar">
          <router-link class="footer-link" to="/">Dashboard</router-link> |
          <router-link class="footer-link" to="/contracts">Contracts</router-link> |
          <router-link class="footer-link" to="/work-prices">Work Prices</router-link> |
          <router-link class="footer-link" to="/about">About</router-link>
        </div>
        <div class="col-md-4 mb-2" v-if="$route.meta.hideNavbar">
          <span style="font-family: Avenir, Helvetica, Arial, sans-serif; color: #4e73df; font-size: 22px; text-transform: uppercase; letter-spacing: 2px;">
            <strong>CHALAN-PRO</strong>
          </span>
        </div>


        <!-- Right: Support -->
        <div class="col-md-4 mb-2">
          <p>Support: <a href="mailto:oliveralverto@gmail.com" class="footer-link">oliveralverto@gmail.com</a></p>
          <p>📞 Contact: +1 (239) 240-0016</p>
        </div>
      </div>

      <!-- System Status -->
      <div class="mt-2">
        <small>🔔 Last Update: Schedule Module and Weekly Supervisor Stats Report.</small>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  data() {
    return {
      currentYear: new Date().getFullYear(),
      appVersion: "1.2.1",
    };
  },
};
</script>

<style scoped>
.footer-link {
  color: orange;
  text-decoration: none;
  margin: 0 5px;
}

.footer-link:hover {
  text-decoration: underline;
}
</style>
