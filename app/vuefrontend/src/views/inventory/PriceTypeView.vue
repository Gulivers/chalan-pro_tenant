<template>
  <div class="card shadow mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h6 class="text-primary mb-0">Price Types</h6>
      <button class="btn btn-success" @click="goToCreateForm">
        <strong>+</strong>
        New Price Type
      </button>
    </div>

    <div class="card-body">
      <div v-if="loading" class="text-center py-3">
        Loading Price Types...
        <div class="spinner-border" role="status"></div>
      </div>

      <div v-else-if="items.length" class="table-responsive">
        <table class="table table-striped table-hover table-bordered" id="priceTypeTable" ref="priceTypeTable">
          <thead>
            <tr>
              <th>ID</th>
              <th v-for="field in headers" :key="field" :class="getHeaderClass(field)">
                {{ schema[field]?.label || field }}
              </th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td>{{ item.id }}</td>

              <td v-for="field in headers" :key="field" :class="getCellClass(field)">
                <template v-if="typeof item[field] === 'boolean'">
                  <span class="badge" :class="item[field] ? 'bg-success' : 'bg-secondary'">
                    {{ item[field] ? 'Active' : 'Inactive' }}
                  </span>
                </template>

                <template v-else>
                  {{ item[field] || '—' }}
                </template>
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

      <div v-else class="text-muted text-center">No price types available.</div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import Swal from 'sweetalert2';

  export default {
    name: 'PriceTypeView',
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
          .get('/api/schema/pricetype/')
          .then(res => {
            this.schema = res.data || {};
            this.headers = Object.keys(this.schema);
          })
          .catch(err => {
            console.error('Error fetching schema:', err);
            this.notifyError('Failed to fetch schema.');
          });
      },
      fetchItems() {
        this.loading = true;
        axios
          .get('/api/pricetypes/')
          .then(res => {
            this.items = res.data;
            this.loading = false;
            setTimeout(() => {
              if (this.items.length && this.$refs.priceTypeTable) {
                this.initDataTable();
              }
            }, 100);
          })
          .catch(() => {
            this.loading = false;
            this.notifyError('Failed to load price types.');
          });
      },
      destroyDataTable() {
        if (this.dataTable && $.fn.dataTable && $.fn.dataTable.isDataTable(this.$refs.priceTypeTable)) {
          try {
            this.dataTable.destroy();
            this.dataTable = null;
          } catch (error) {
            console.warn('Error destroying DataTable:', error);
          }
        }
      },
      initDataTable() {
        const table = this.$refs.priceTypeTable;
        if (!table || !$.fn.dataTable) {
          return;
        }

        try {
          this.destroyDataTable();

          this.dataTable = $(table).DataTable({
            destroy: true,
            responsive: true,
            pageLength: 50,
            order: [[0, 'desc']],
            language: {
              search: 'Search:',
            },
          });
        } catch (error) {
          console.error('Error initializing DataTable:', error);
        }
      },
      goToCreateForm() {
        this.$router.push({ name: 'price-type-form' });
      },
      viewItem(id) {
        this.$router.push({ name: 'price-type-view', params: { id } });
      },
      editItem(id) {
        this.$router.push({ name: 'price-type-edit', params: { id } });
      },

      async confirmDelete(id) {
        const result = await Swal.fire({
          title: 'Delete?',
          text: 'This will delete the price type. This action cannot be undone.',
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
          await axios.delete(`/api/pricetypes/${id}/`);
          // refrescar tabla
          this.destroyDataTable();
          this.items = this.items.filter(p => p.id !== id);
          setTimeout(() => {
            if (this.items.length && this.$refs.priceTypeTable) {
              this.initDataTable();
            }
          }, 50);

          // toast de éxito (patrón)
          if (this.notifyToastSuccess) {
            this.notifyToastSuccess('The price type has been deleted.');
          }
        } catch (error) {
          console.error('Error deleting price type:', error);
          const { status } = error?.response || {};
          // Tu interceptor ya maneja 409 (in_use) con Swal. Dejamos este genérico adicional por ahora.
          if (status === 403) {
            await Swal.fire('Forbidden', 'You do not have permission for this action.', 'error');
          } else {
            await Swal.fire('Oops!', 'Error deleting the price type.', 'error');
          }
        } finally {
          this.deletingId = null;
        }
      },

      notifyError(message = 'Something went wrong!') {
        Swal.fire({
          icon: 'error',
          title: 'Error',
          text: message,
          confirmButtonText: 'OK',
        });
      },

      getHeaderClass(field) {
        // Alinear a la izquierda los campos específicos
        if (field === 'description' || field === 'is_active') {
          return 'text-start';
        }
        return '';
      },

      getCellClass(field) {
        // Alinear a la izquierda el contenido de los campos específicos
        if (field === 'description' || field === 'is_active') {
          return 'text-start';
        }
        return '';
      },
    },
  };
</script>
