<template>

  <!-- El resto del código permanece igual -->
  <div class="card shadow mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h6 class="text-primary">Piece Work List</h6>
      <button v-if="this.hasPermission('ctrctsapp.add_workprice')" class="btn btn-success ml-auto" @click="createPrice()"> <strong>+</strong> New Price Work</button>
    </div>

    <div class="card-body">
      <div v-if="loading" class="spinner-container">
        Loading Pieces ...&nbsp;
        <div class="spinner-border" style="width: 4rem; height: 4rem;" role="status"></div>
        <div class="spinner-grow" style="width: 3rem; height: 3rem;" role="status"></div>
        <div class="spinner-grow" style="width: 2rem; height: 2rem;" role="status"></div>
        <div class="spinner-grow" style="width: 1rem; height: 1rem;" role="status"></div>
      </div>

      <div class="table-responsive">
        <table class="table table-striped table-hover table-bordered" id="workPricesTable" ref="workPricesTable">
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col" class="text-start">Description</th>
              <th scope="col">USD$ Trim</th>
              <th scope="col">USD$ Rough</th>
              <th scope="col">Unit Price Type</th>
              <th scope="col">Accions</th>
            </tr>
          </thead>
          <tbody v-show="!loading">
            <tr v-for="price in prices" :key="price.id">
              <td>{{ price.id }}</td>
              <td class="text-start">{{ price.name }}</td>
              <td>$ {{ price.trim }}</td>
              <td>$ {{ price.rough }}</td>
              <td>{{ price.unit_price }}</td>
              <td>
                <div class="btn-group btn-group-sm" role="group" aria-label="Small button group">
                  <button v-if="this.hasPermission('ctrctsapp.view_workprice')" type="button" class="btn btn-outline-success" @click="viewPrice(price.id)">View</button> &nbsp;
                  <button v-if="this.hasPermission('ctrctsapp.change_workprice')" type="button" class="btn btn-outline-primary" @click="editPrice(price.id)">Edit</button>
                  &nbsp;
                  <!--<button v-if="this.hasPermission('ctrctsapp.delete_workprice')" type="button" class="btn btn-outline-danger" @click="deletePrice(price.id)">Delete</button>-->
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios';

  export default {
    name: 'WorkPricesView',
    data() {
      return {
        loading: false,
        prices: [],
        newPrice: {
          name: '',
          trim: '',
          rough: '',
          unit_price: ''
        }
      };
    },
    mounted() {
      this.fetchPrices();
    },
    methods: {
      fetchPrices() {
        this.loading = true;
        axios.get('/api/workprice/') // El signo "-" indica orden descendente
          .then(response => {
            this.prices = response.data;
            this.$nextTick(() => {
              this.initDataTable();
            });
            this.loading = false;
          })
          .catch(error => {
            this.loading = false;
            console.error('Error fetching work prices:', error);
          });
      },
      initDataTable() {
        if (this.$refs.workPricesTable) {
          // Destruir la tabla existente si ya está inicializada
          if ($.fn.dataTable.isDataTable(this.$refs.workPricesTable)) {
            $(this.$refs.workPricesTable).DataTable().destroy();
          }

          // Inicializar DataTables
          $(this.$refs.workPricesTable).DataTable({
            pageLength: 50,
            order: [[0, 'desc']],
            responsive: true,
          });
        }
      },
      createPrice() {
        this.$router.push({ name: 'work-prices-form' });
      },
      editPrice(id) {
        // console.log('Edit price with ID:', id);
        this.$router.push({ name: 'work-prices-edit', params: { id: id } });
      },
      viewPrice(id) {
        // console.log('Edit price with ID:', id);
        this.$router.push({ name: 'work-prices-view', params: { id: id } });
      },
/*      deletePrice(id) {
        if (confirm("Are you sure you want to delete this price?")) {
          axios.delete(`/api/workprice/${id}/`)
            .then(() => {
              console.log('Price deleted successfully');
              this.fetchPrices(); // Recarga la lista de precios después de eliminar
            })
            .catch(error => {
              console.error('Error deleting price:', error);
            });
        } else {
          console.log('Contract deletion cancelled');
        }
      },*/
    }
  };
</script>

<style scoped>
  /* Estilos adicionales */
</style>