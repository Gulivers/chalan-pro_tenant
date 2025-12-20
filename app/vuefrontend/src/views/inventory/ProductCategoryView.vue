<template>
  <div class="card shadow mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h6 class="text-primary mb-0">Product Categories</h6>
      <button class="btn btn-success" @click="goToCreateForm">
        <strong>+</strong> New Category
      </button>
    </div>

    <div class="card-body">
      <div v-if="loading" class="text-center py-3">
        Loading Categories...
        <div class="spinner-border" role="status"></div>
      </div>

      <div v-else-if="items.length" class="table-responsive">
        <table
          class="table table-striped table-hover table-bordered"
          id="categoryTable"
          ref="categoryTable"
        >
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
              <td v-for="field in headers" :key="field" class="text-start">
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
                    :disabled="deletingId === item.id"
                  >
                    <span
                      v-if="deletingId === item.id"
                      class="spinner-border spinner-border-sm me-1"
                      role="status"
                      aria-hidden="true"
                    ></span>
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
import axios from 'axios'
import Swal from 'sweetalert2'

export default {
  name: 'ProductCategoryView',
  data() {
    return {
      schema: {},
      items: [],
      headers: [],
      loading: false,
      dataTable: null,
      deletingId: null,
    }
  },
  mounted() {
    this.fetchSchema()
    this.fetchItems()
  },
  beforeUnmount() {
    this.destroyDataTable()
  },
  methods: {
    fetchSchema() {
      axios
        .get('/api/schema/product-category/')
        .then(res => {
          this.schema = res.data || {}
          this.headers = Object.keys(this.schema)
        })
        .catch(err => {
          console.error('Error fetching schema:', err)
          this.schema = {}
          this.headers = []
        })
    },
    fetchItems() {
      this.loading = true
      axios
        .get('/api/productcategory/')
        .then(res => {
          this.items = res.data
          this.loading = false
          setTimeout(() => {
            if (this.items.length && this.$refs.categoryTable) {
              this.initDataTable()
            }
          }, 100)
        })
        .catch(() => {
          this.loading = false
        })
    },
    destroyDataTable() {
      if (this.dataTable && $.fn.dataTable && $.fn.dataTable.isDataTable(this.$refs.categoryTable)) {
        try {
          this.dataTable.destroy()
          this.dataTable = null
        } catch (error) {
          console.warn('Error destroying DataTable:', error)
        }
      }
    },
    initDataTable() {
      const table = this.$refs.categoryTable
      if (!table || !$.fn.dataTable) return
      try {
        this.destroyDataTable()
        this.dataTable = $(table).DataTable({
          destroy: true,
          responsive: true,
          pageLength: 50,
          order: [[0, 'desc']],
          language: { search: 'Search:' },
        })
      } catch (error) {
        console.error('Error initializing DataTable:', error)
      }
    },
    goToCreateForm() {
      this.$router.push({ name: 'product-category-form' })
    },
    viewItem(id) {
      this.$router.push({ name: 'product-category-view', params: { id } })
    },
    editItem(id) {
      this.$router.push({ name: 'product-category-edit', params: { id } })
    },

    async confirmDelete(id) {
      const result = await Swal.fire({
        title: 'Delete?',
        text: 'This will delete the product category. This action cannot be undone.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete',
        cancelButtonText: 'Cancel',
      })
      if (!result.isConfirmed) return
      await this.deleteItem(id)
    },

    async deleteItem(id) {
      this.deletingId = id
      try {
        await axios.delete(`/api/productcategory/${id}/`)
        // refrescar tabla
        this.destroyDataTable()
        this.items = this.items.filter(c => c.id !== id)
        setTimeout(() => {
          if (this.items.length && this.$refs.categoryTable) {
            this.initDataTable()
          }
        }, 50)

        // toast de éxito (patrón)
        if (this.notifyToastSuccess) {
          this.notifyToastSuccess('The product category has been deleted.')
        }
      } catch (error) {
        console.error('Error deleting product category:', error)
        const { status } = error?.response || {}
        // Nota: tu interceptor ya muestra Swal para 409 (in_use).
        // Dejas este genérico adicional por ahora, tal como acordamos.
        if (status === 403) {
          await Swal.fire('Forbidden', 'You do not have permission for this action.', 'error')
        } else {
          await Swal.fire('Oops!', 'Error deleting the product category.', 'error')
        }
      } finally {
        this.deletingId = null
      }
    },
  },
}
</script>
