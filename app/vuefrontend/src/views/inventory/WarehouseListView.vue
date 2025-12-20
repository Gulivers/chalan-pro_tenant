<template>
  <div class="card shadow mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h6 class="text-primary mb-0">Warehouse List</h6>
      <button class="btn btn-success ml-auto" @click="createWarehouse">
        <strong>+</strong>
        New Warehouse
      </button>
    </div>

    <div class="card-body">
      <div v-if="loading" class="spinner-container text-center">
        <p>Loading Warehouses...</p>
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <div class="table-responsive">
        <table class="table table-striped table-hover table-bordered" ref="warehouseTable">
          <thead>
            <tr>
              <th>ID</th>
              <th scope="col">Name</th>
              <th scope="col">Location</th>
              <th scope="col">Status</th>
              <th scope="col">Default</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody v-show="!loading">
            <tr v-for="warehouse in warehouses" :key="warehouse.id">
              <td>{{ warehouse.id }}</td>
              <td class="text-start">{{ warehouse.name }}</td>
              <td class="text-start">{{ warehouse.location }}</td>
              <td>
                <span class="badge bg-success" v-if="warehouse.is_active">Active</span>
                <span class="badge bg-secondary" v-else>Inactive</span>
              </td>
              <td>
                <span class="badge bg-warning text-dark" v-if="warehouse.is_default">
                  <i class="fas fa-star me-1"></i>Default
                </span>
                <span class="text-muted" v-else>-</span>
              </td>
              <td class="text-center">
                <div class="btn-group btn-group-sm">
                  <button class="btn btn-outline-success me-1" @click="viewWarehouse(warehouse.id)">View</button>
                  <button class="btn btn-outline-primary me-1" @click="editWarehouse(warehouse.id)">Edit</button>
                  <button
                    class="btn btn-outline-danger"
                    @click="confirmDelete(warehouse.id)"
                    :disabled="deletingId === warehouse.id">
                    <span
                      v-if="deletingId === warehouse.id"
                      class="spinner-border spinner-border-sm me-1"
                      role="status"
                      aria-hidden="true"></span>
                    Delete
                  </button>
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
  import Swal from 'sweetalert2';

  export default {
    name: 'WarehouseListView',
    data() {
      return {
        loading: false,
        warehouses: [],
        dataTable: null,
        deletingId: null,
      };
    },
    mounted() {
      this.fetchWarehouses();
    },
    beforeUnmount() {
      this.destroyDataTable();
    },
    methods: {
      fetchWarehouses() {
        this.loading = true;
        axios
          .get('/api/warehouses/')
          .then(res => {
            this.warehouses = res.data;
            this.$nextTick(this.initDataTable);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      destroyDataTable() {
        if (this.dataTable && $.fn.DataTable && $.fn.DataTable.isDataTable(this.$refs.warehouseTable)) {
          try {
            this.dataTable.destroy();
            this.dataTable = null;
          } catch (error) {
            console.warn('Error destroying DataTable:', error);
          }
        }
      },
      initDataTable() {
        if (this.$refs.warehouseTable && $.fn.DataTable) {
          if ($.fn.DataTable.isDataTable(this.$refs.warehouseTable)) {
            $(this.$refs.warehouseTable).DataTable().destroy();
          }

          this.dataTable = $(this.$refs.warehouseTable).DataTable({
            destroy: true,
            responsive: true,
            pageLength: 50,
            order: [[0, 'desc']],
            language: { search: 'Search:' },
          });
        }
      },
      createWarehouse() {
        this.$router.push({ name: 'warehouse-form' });
      },
      editWarehouse(id) {
        this.$router.push({ name: 'warehouse-edit', params: { id } });
      },
      viewWarehouse(id) {
        this.$router.push({ name: 'warehouse-view', params: { id } });
      },

      async confirmDelete(id) {
        const result = await Swal.fire({
          title: 'Delete?',
          text: 'This will delete the warehouse. This action cannot be undone.',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Yes, delete',
          cancelButtonText: 'Cancel',
        });
        if (!result.isConfirmed) return;
        await this.deleteWarehouse(id);
      },

      async deleteWarehouse(id) {
        this.deletingId = id;
        try {
          await axios.delete(`/api/warehouses/${id}/`);
          // refrescar tabla
          this.destroyDataTable();
          this.warehouses = this.warehouses.filter(w => w.id !== id);
          this.$nextTick(() => {
            if (this.warehouses.length && this.$refs.warehouseTable) this.initDataTable();
          });

          // toast éxito (patrón)
          if (this.notifyToastSuccess) {
            this.notifyToastSuccess('The warehouse has been deleted.');
          }
        } catch (error) {
          console.error('Error deleting warehouse:', error);
          const { status } = error?.response || {};
          // Tu interceptor ya maneja 409 (in_use) con Swal. Dejamos este genérico adicional por ahora.
          if (status === 403) {
            await Swal.fire('Forbidden', 'You do not have permission for this action.', 'error');
          } else {
            await Swal.fire('Oops!', 'Error deleting the warehouse.', 'error');
          }
        } finally {
          this.deletingId = null;
        }
      },
    },
  };
</script>

<style scoped>
  .spinner-container {
    padding: 2rem;
  }
</style>
