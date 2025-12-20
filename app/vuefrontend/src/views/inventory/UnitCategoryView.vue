<template>
  <div class="card shadow mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h6 class="text-primary mb-0">Unit Categories</h6>
      <button class="btn btn-success" @click="goToCreateForm">
        <strong>+</strong>
        New Category
      </button>
    </div>

    <div class="card-body">
      <div v-if="loading" class="text-center py-3">
        Loading Unit Categories...
        <div class="spinner-border" role="status"></div>
      </div>

      <div v-else-if="items.length" class="table-responsive">
        <table class="table table-striped table-hover table-bordered" id="unitCategoryTable" ref="unitCategoryTable">
          <thead>
            <tr>
              <th>ID</th>
              <th v-for="field in headers" :key="field">
                {{ schema[field]?.label || field }}
              </th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td>{{ item.id }}</td>
              <td v-for="field in headers" :key="field">
                <template v-if="typeof item[field] === 'boolean'">
                  <span :class="['badge', item[field] ? 'bg-success' : 'bg-secondary']">
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

      <div v-else class="text-muted text-center">No categories available.</div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import Swal from 'sweetalert2';

  export default {
    name: 'UnitCategoryView',
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
          .get('/api/schema/unitcategory/')
          .then(res => {
            this.schema = res.data || {};
            this.headers = Object.keys(this.schema);
          })
          .catch(err => {
            console.error('❌ Error fetching schema:', err);
          });
      },
      fetchItems() {
        this.loading = true;
        axios
          .get('/api/unitcategory/')
          .then(res => {
            this.items = res.data;
            this.loading = false;
            setTimeout(() => {
              if (this.items.length && this.$refs.unitCategoryTable) {
                this.initDataTable();
              }
            }, 100);
          })
          .catch(() => {
            this.loading = false;
            console.error('❌ Error fetching categories');
          });
      },
      destroyDataTable() {
        if (this.dataTable && $.fn.dataTable && $.fn.dataTable.isDataTable(this.$refs.unitCategoryTable)) {
          try {
            this.dataTable.destroy();
            this.dataTable = null;
          } catch (error) {
            console.warn('Error destroying DataTable:', error);
          }
        }
      },
      initDataTable() {
        const table = this.$refs.unitCategoryTable;
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
        this.$router.push({ name: 'unit-category-form' });
      },
      viewItem(id) {
        this.$router.push({ name: 'unit-category-view', params: { id } });
      },
      editItem(id) {
        this.$router.push({ name: 'unit-category-edit', params: { id } });
      },

      async confirmDelete(id) {
        const result = await Swal.fire({
          title: 'Delete?',
          text: 'This will delete the unit category. This action cannot be undone.',
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
          await axios.delete(`/api/unitcategory/${id}/`);
          // refrescar tabla
          this.destroyDataTable();
          this.items = this.items.filter(c => c.id !== id);
          setTimeout(() => {
            if (this.items.length && this.$refs.unitCategoryTable) {
              this.initDataTable();
            }
          }, 50);

          // Toast de éxito (según patrón)
          if (this.notifyToastSuccess) {
            this.notifyToastSuccess('The unit category has been deleted.');
          }
        } catch (error) {
          console.error('Error deleting unit category:', error);
          const { status } = error?.response || {};

          // Nota: si tu interceptor ya muestra Swal para 409 (in_use), aquí seguirá mostrando el genérico también
          // (lo aceptaste por ahora). Si luego quieres evitar el doble Swal, te digo cómo.
          if (status === 403) {
            await Swal.fire('Forbidden', 'You do not have permission for this action.', 'error');
          } else {
            await Swal.fire('Oops!', 'Error deleting the unit category.', 'error');
          }
        } finally {
          this.deletingId = null;
        }
      },
    },
  };
</script>
