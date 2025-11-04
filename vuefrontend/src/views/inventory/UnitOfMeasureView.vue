<template>
  <div class="card shadow mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h6 class="text-primary mb-0">Unit of Measure</h6>
      <button class="btn btn-success" @click="goToCreateForm">
        <strong>+</strong>
        New Unit
      </button>
    </div>

    <div class="card-body">
      <div v-if="loading" class="text-center py-3">
        Loading Units...
        <div class="spinner-border" role="status"></div>
      </div>

      <div v-else-if="items.length" class="table-responsive">
        <table class="table table-striped table-hover table-bordered" id="unitTable" ref="unitTable">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Code</th>
              <th>Category</th>
              <th class="text-center">Ref. Unit</th>
              <th class="text-center">Sign</th>
              <th>Factor</th>
              <th class="text-center">Active</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td>{{ item.id }}</td>
              <td class="text-start">{{ item.name }}</td>
              <td class="text-start">{{ item.code }}</td>
              <td class="text-start">{{ item.category_name || 'N/A' }}</td>
              <td class="text-center">{{ item.reference_unit ? '✔' : '✖' }}</td>
              <td class="text-center">{{ item.conversion_sign }}</td>
              <td>{{ item.conversion_factor }}</td>
              <td class="text-center">
                <span class="badge" :class="item.is_active ? 'bg-success' : 'bg-secondary'">
                  {{ item.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="text-center">
                <div class="btn-group btn-group-sm">
                  <button class="btn btn-outline-success me-1" @click="viewItem(item.id)">View</button>
                  <button class="btn btn-outline-primary me-1" @click="editItem(item.id)">Edit</button>
                  <button
                    class="btn btn-outline-danger"
                    @click="confirmDelete(item.id)"
                    :disabled="deletingId === item.id">
                    <span
                      v-if="deletingId === item.id"
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

      <div v-else class="text-muted text-center">No units available.</div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import Swal from 'sweetalert2';

  export default {
    name: 'UnitOfMeasureView',
    data() {
      return {
        schema: {},
        items: [],
        headers: [],
        loading: false,
        dataTable: null,
        deletingId: null,
      };
    },
    mounted() {
      this.fetchSchema();
      this.fetchItems();
    },
    beforeUnmount() {
      this.destroyDataTable();
    },
    methods: {
      fetchSchema() {
        axios
          .get('/api/schema/unitofmeasure/')
          .then(res => {
            this.schema = res.data || {};
            this.headers = Object.keys(this.schema);
          })
          .catch(err => {
            console.error('Error fetching schema:', err);
          });
      },
      fetchItems() {
        this.loading = true;
        axios
          .get('/api/unitsofmeasure/')
          .then(res => {
            this.items = res.data;
            this.loading = false;
            setTimeout(() => {
              if (this.items.length && this.$refs.unitTable) {
                this.initDataTable();
              }
            }, 100);
          })
          .catch(err => {
            this.loading = false;
            console.error('Error fetching items:', err);
          });
      },
      destroyDataTable() {
        if (this.dataTable && $.fn.dataTable && $.fn.dataTable.isDataTable(this.$refs.unitTable)) {
          try {
            this.dataTable.destroy();
            this.dataTable = null;
          } catch (error) {
            console.warn('Error destroying DataTable:', error);
          }
        }
      },
      initDataTable() {
        const table = this.$refs.unitTable;
        if (!table || !$.fn.dataTable) return;

        try {
          this.destroyDataTable();
          this.dataTable = $(table).DataTable({
            destroy: true,
            responsive: true,
            pageLength: 50,
            order: [[0, 'desc']],
            language: { search: 'Search:' },
          });
        } catch (error) {
          console.error('Error initializing DataTable:', error);
        }
      },
      goToCreateForm() {
        this.$router.push({ name: 'unit-measure-form' });
      },
      viewItem(id) {
        this.$router.push({ name: 'unit-measure-view', params: { id } });
      },
      editItem(id) {
        this.$router.push({ name: 'unit-measure-edit', params: { id } });
      },

      async confirmDelete(id) {
        const result = await Swal.fire({
          title: 'Delete?',
          text: 'This will delete the unit. This action cannot be undone.',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Yes, delete',
          cancelButtonText: 'Cancel',
        });
        if (!result.isConfirmed) return;
        await this.deleteItem(id);
      },

      async deleteItem(id) {
        this.deletingId = id;
        try {
          await axios.delete(`/api/unitsofmeasure/${id}/`);
          // refrescar tabla
          this.destroyDataTable();
          this.items = this.items.filter(u => u.id !== id);
          setTimeout(() => {
            if (this.items.length && this.$refs.unitTable) {
              this.initDataTable();
            }
          }, 50);
          if (this.notifyToastSuccess) {
            this.notifyToastSuccess('The unit has been deleted.');
          }
        } catch (error) {
          console.error('Error deleting unit:', error);
          const { status } = error?.response || {};
          if (status === 403) {
            await Swal.fire('Forbidden', 'You do not have permission for this action.', 'error');
          } else {
            await Swal.fire('Oops!', 'Error deleting the unit.', 'error');
          }
        } finally {
          this.deletingId = null;
        }
      },
    },
  };
</script>
