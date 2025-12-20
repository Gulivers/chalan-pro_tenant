<template>
  <!--
    BaseInventoryView.vue
    --------------------------------------------------------------
    ¿Qué es?
      - Componente base reutilizable para listar catálogos del módulo Inventory
        usando una tabla con DataTables (a través del mixin dataTableMixin).

    ¿Qué hace?
      - Carga un esquema (schemaEndpoint) para construir dinámicamente las columnas.
      - Obtiene los datos (apiEndpoint) y renderiza la tabla.
      - Inicializa/gestiona DataTables de forma segura con el mixin.
      - Expone acciones comunes (View/Edit) mediante rutas pasadas por props.

    ¿Quién lo usa?
      - Vistas de inventario tipo catálogo, por ejemplo:
          * WarehouseListView (almacenes)
          * ProductCategoryView (categorías de producto)
          * ProductBrandView (marcas)
          * UnitOfMeasureView (unidades de medida)
          * UnitCategoryView (categorías de unidades)
      - Cualquier otra vista de tipo listado que provea schemaEndpoint y apiEndpoint.

    Props clave:
      - schemaEndpoint:   URL para obtener metadatos de columnas (labels, etc.)
      - apiEndpoint:      URL para obtener los registros a listar
      - createRouteName / viewRouteName / editRouteName: nombres de rutas para acciones
      - tableId / tableRef: identificadores para inicializar DataTables de forma segura
  -->
  <div class="card shadow mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h6 class="text-primary mb-0">{{ title }}</h6>
      <button class="btn btn-success" @click="goToCreateForm">
        <strong>+</strong> {{ createButtonText }}
      </button>
    </div>

    <div class="card-body">
      <div v-if="loading" class="text-center py-3">
        Loading {{ loadingText }}...
        <div class="spinner-border" role="status"></div>
      </div>

      <div v-else-if="items.length" class="table-responsive">
        <table
          class="table table-striped table-hover table-bordered"
          :id="tableId"
          :ref="tableRef">
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
                  <span
                    :class="[
                      'badge',
                      item[field] ? 'bg-success' : 'bg-secondary',
                    ]">
                    {{ item[field] ? "Active" : "Inactive" }}
                  </span>
                </template>
                <template v-else>
                  {{ item[field] || "—" }}
                </template>
              </td>
              <td class="text-center">
                <div class="btn-group btn-group-sm">
                  <button
                    class="btn btn-outline-success"
                    @click="viewItem(item.id)">
                    View
                  </button>
                  <button
                    class="btn btn-outline-primary"
                    @click="editItem(item.id)">
                    Edit
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="text-muted text-center">{{ emptyMessage }}</div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { dataTableMixin } from '@/mixins/dataTableMixin';

export default {
  name: "BaseInventoryView",
  mixins: [dataTableMixin],
  props: {
    title: {
      type: String,
      required: true,
    },
    createButtonText: {
      type: String,
      required: true,
    },
    loadingText: {
      type: String,
      required: true,
    },
    emptyMessage: {
      type: String,
      required: true,
    },
    tableId: {
      type: String,
      required: true,
    },
    tableRef: {
      type: String,
      required: true,
    },
    schemaEndpoint: {
      type: String,
      required: true,
    },
    apiEndpoint: {
      type: String,
      required: true,
    },
    createRouteName: {
      type: String,
      required: true,
    },
    viewRouteName: {
      type: String,
      required: true,
    },
    editRouteName: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      schema: {},
      items: [],
      headers: [],
      loading: false,
    };
  },
  mounted() {
    this.fetchSchema();
    this.fetchItems();
  },
  methods: {
    fetchSchema() {
      axios
        .get(this.schemaEndpoint)
        .then(res => {
          this.schema = res.data || {};
          this.headers = Object.keys(this.schema);
        })
        .catch(err => {
          console.error("Error fetching schema:", err);
          this.schema = {};
          this.headers = [];
        });
    },
    fetchItems() {
      this.loading = true;
      axios
        .get(this.apiEndpoint)
        .then(res => {
          this.items = res.data;
          this.loading = false;
          this.safeInitDataTable();
        })
        .catch(() => {
          this.loading = false;
        });
    },
    goToCreateForm() {
      this.$router.push({ name: this.createRouteName });
    },
    viewItem(id) {
      this.$router.push({ name: this.viewRouteName, params: { id } });
    },
    editItem(id) {
      this.$router.push({ name: this.editRouteName, params: { id } });
    },
  },
};
</script> 