<template>
    <div class="card shadow mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="text-primary mb-0">Product Units</h6>
        <button class="btn btn-success" @click="goToCreateForm">
          <strong>+</strong> New Product Unit
        </button>
      </div>
  
      <div class="card-body">
        <div v-if="loading" class="text-center py-3">
          Loading Product Units...
          <div class="spinner-border" role="status"></div>
        </div>
  
        <div v-else-if="items.length" class="table-responsive">
          <table class="table table-striped table-hover table-bordered" id="productUnitTable" ref="productUnitTable">
            <thead>
              <tr>
                <th>ID</th>
                <th>Product</th>
                <th>Unit</th>
                <th class="text-center">Is Purchase</th>
                <th class="text-center">Is Sale</th>
                <th class="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in items" :key="item.id">
                <td>{{ item.id }}</td>
                <td class="text-start">{{ item.product_name || 'N/A' }}</td>
                <td class="text-start">{{ item.unit_name || 'N/A' }}</td>
                <td class="text-center">{{ item.is_purchase ? '✔' : '✖' }}</td>
                <td class="text-center">{{ item.is_sale ? '✔' : '✖' }}</td>
                <td class="text-center">
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-success" @click="viewItem(item.id)">View</button>
                    <button class="btn btn-outline-primary" @click="editItem(item.id)">Edit</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
  
        <div v-else class="text-muted text-center">No product units available.</div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  
  export default {
    name: 'ProductUnitView',
    data() {
      return {
        schema: {},
        items: [],
        headers: [],
        loading: false,
        dataTable: null,
      }
    },
    mounted() {
      this.fetchSchema()
      this.fetchItems()
    },
    beforeUnmount() {
      // Limpiar DataTable antes de desmontar el componente
      this.destroyDataTable()
    },
    methods: {
      fetchSchema() {
        axios.get('/api/schema/productunit/')
          .then(res => {
            this.schema = res.data || {}
            this.headers = Object.keys(this.schema)
          })
          .catch(err => {
            console.error('Error fetching schema:', err)
          })
      },
      fetchItems() {
        this.loading = true
        axios.get('/api/productunit/')
          .then(res => {
            this.items = res.data
            this.loading = false
            // Usar setTimeout para asegurar que el DOM esté completamente renderizado
            setTimeout(() => {
              if (this.items.length && this.$refs.productUnitTable) {
                this.initDataTable()
              }
            }, 100)
          })
          .catch(err => {
            this.loading = false
            console.error('Error fetching product units:', err)
          })
      },
      destroyDataTable() {
        if (this.dataTable && $.fn.dataTable && $.fn.dataTable.isDataTable(this.$refs.productUnitTable)) {
          try {
            this.dataTable.destroy()
            this.dataTable = null
          } catch (error) {
            console.warn('Error destroying DataTable:', error)
          }
        }
      },
      initDataTable() {
        const table = this.$refs.productUnitTable
        if (!table || !$.fn.dataTable) {
          return
        }

        try {
          // Destruir DataTable existente si existe
          this.destroyDataTable()

          // Inicializar nuevo DataTable
          this.dataTable = $(table).DataTable({
            destroy: true,
            responsive: true,
            pageLength: 50,
            order: [[0, 'desc']],
            language: {
              search: "Search:",
            },
          })
        } catch (error) {
          console.error('Error initializing DataTable:', error)
        }
      },
      goToCreateForm() {
        this.$router.push({ name: 'product-unit-form' })
      },
      viewItem(id) {
        this.$router.push({ name: 'product-unit-view', params: { id } })
      },
      editItem(id) {
        this.$router.push({ name: 'product-unit-edit', params: { id } })
      }
    }
  }
  </script>
  