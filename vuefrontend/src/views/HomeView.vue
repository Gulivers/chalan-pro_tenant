<template>
  <div class="container-fluid">
    <!-- Page Heading -->
    <div class="d-sm-flex align-items-center justify-content-between my-2">
      <h1 class="h3 mb-0 text-gray-800">Dashboard</h1>
    </div>

    <!-- Sales vs Purchases Comparison (Top) -->
    <div class="row mb-3">
      <div class="col-xl-12 col-lg-12">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Sales vs Purchases (Last 12 Months)</h6>
          </div>
          <div class="card-body">
            <CustomersSuppliersComparison
              :comparison-data="comparisonData"
              :loading="loadingComparison"
              @refresh="loadComparison"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Content Row -->
    <div class="row">
      <!-- Area Chart -->
      <div class="col-xl-12 col-lg-12">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Weekly Contract Totals</h6>
          </div>
          <div class="card-body">
            <div class="chart-area">
              <AreaChart />
            </div>
          </div>
        </div>
      </div>
      <!-- Bar Chart -->
      <div class="col-xl-12 col-lg-12">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Monthly Contract Totals</h6>
          </div>
          <div class="card-body">
            <div class="chart-bar">
              <BarChart />
            </div>
          </div>
        </div>
      </div>
      <!-- Bar Supervisor Chart -->
      <div v-if="this.hasPermission('ctrctsapp.add_contract')" class="col-xl-12 col-lg-12">
        <div class="card shadow mb-4">
          <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">Weekly Supervisor Stats</h6>
          </div>
          <div class="card-body">
            <div class="chart-bar">
              <WeeklySupervisorChart />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { defineComponent } from 'vue';
  import AreaChart from '@components/contracts/AreaChart.vue';
  import BarChart from '@components/contracts/BarChart.vue';
  import WeeklySupervisorChart from '@components/schedule/WeeklySupervisorChart.vue';
  import CustomersSuppliersComparison from '@components/inventory/dashboard/components/CustomersSuppliersComparison.vue';

  import axios from 'axios';

  export default defineComponent({
    name: 'HomeView',
    components: {
      AreaChart,
      BarChart,
      WeeklySupervisorChart,
      CustomersSuppliersComparison,
    },

    mounted() {
      // Llamada a logUserAction solo una vez después de que el usuario haya iniciado sesión y esté en el Home
      this.checkUserIdentity().then(userId => {
        if (userId) {
          this.logUserAction('login', 'User', userId, 'User logged in successfully');
        }
      });
      this.loadComparison();
    },
    methods: {
      // Llamada para obtener la identidad del usuario autenticado
      async checkUserIdentity() {
        const user = await this.getAuthenticatedUser();
        return user ? user.id : null; // Retorna el ID del usuario o null
      },

      // Método para registrar la acción del usuario
      logUserAction(action, model_name, object_id, details) {
        const token = localStorage.getItem('authToken');
        if (token) {
          axios
            .post(
              '/api/log-action/',
              {
                action,
                model_name,
                object_id,
                details,
              },
              {
                headers: {
                  Authorization: `Token ${token}`,
                  'Content-Type': 'application/json',
                },
              }
            )
            .then(response => {
              console.log('Acción registrada:', response.data);
            })
            .catch(error => {
              console.error('Error registrando la acción:', error);
            });
        } else {
          console.error('Token no encontrado. El usuario no está autenticado.');
        }
      },

      async loadComparison() {
        try {
          this.loadingComparison = true;
          const response = await axios.get('/api/dashboard/customers-suppliers-comparison/');
          this.comparisonData = Array.isArray(response.data) ? response.data : [];
        } catch (error) {
          console.error('Error loading comparison data:', error);
          this.comparisonData = [];
        } finally {
          this.loadingComparison = false;
        }
      },
    },
    data() {
      return {
        comparisonData: [],
        loadingComparison: false,
      };
    },
  });
</script>

<style scoped>

.chart-area {
  height: 380px;
}

@media (max-width: 768px) {
  .chart-area{
    height: 300px;
  }
}

.chart-container {
  position: relative;
  width: 100%;
  height: 400px;
  overflow: hidden;
}

canvas {
  width: 100% !important;
  height: 100% !important;
  max-height: 360px;
}

/* Móvil: Ajustar mejor en pantallas pequeñas */
@media (max-width: 768px) {
  .chart-container {
    height: 300px; /* Más compacto */
  }

  canvas {
    max-height: 280px;
  }
}
</style>
